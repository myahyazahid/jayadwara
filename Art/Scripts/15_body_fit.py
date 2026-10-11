"""Revisi — FIT undersuit ke zirah: badan di bawah zirah didorong keluar sampai berjarak GAP dari permukaan dalam zirah.

Masalah yang diselesaikan: undersuit (Skin modifier) terlalu ramping di bahu/lengan atas/dada sehingga cuirass & pauldron
tampak melayang dengan celah 4–8 cm. Jalankan SETELAH 10–14 (zirah sudah ada) dan SEBELUM 02_rig (bobot dihitung ulang).

Cara kerja per vertex undersuit:
  1) tembak sinar sepanjang normal ke zirah yang BOLEH mendorong vertex itu (dipilih dari tulang terdekat: badan -> zirah
     badan & bahu; lengan atas -> bahu & lengan; lengan bawah -> lengan). Lengan tidak didorong oleh zirah dada, dst.
  2) dorongan mentah = jarak hit - GAP (maks MAX_PUSH); disebarkan halus ke tetangga supaya tidak ada tangga di tepi zirah.
  3) batas keras: tidak boleh melewati (jarak hit - GAP) ke zirah mana pun di arah normal, lalu cek jarak terdekat.
  4) dicatat ke mesh: atribut JD_FitPush (m) & JD_FitSrc (indeks ke body["jd_fit_src"]) -> 02_rig mencampur bobot badan
     ke bobot zirah itu, supaya otot yang menempel bergerak BERSAMA zirahnya (tanpa ini cap pauldron tertelan deltoid
     saat lengan terangkat).
Hasil dicetak: celah median per zirah sebelum/sesudah.
"""
import importlib
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_line

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jd_skeleton as SK
importlib.reload(SK)

GAP = globals().get("FIT_GAP", 0.008)          # m; jarak sisa badan -> permukaan dalam zirah
MAX_PUSH = globals().get("FIT_MAX_PUSH", 0.075)
REACH = 0.14                                    # sinar lebih jauh dari ini = bukan zirah yang menutupi vertex
SHOULDER_MIN_LAT = 0.55                         # pauldron hanya mendorong permukaan yang menghadap ke samping (deltoid)
SPREAD_ITERS = 8                                # cincin tetangga untuk transisi halus di tepi zirah

GROUPS = {
    "torso": ("JD_Torso_Chest", "JD_Torso_Back", "JD_Torso_Abs"),
    "shoulder": ("JD_Shoulder_Pauldron_", "JD_Shoulder_Lame_", "JD_Shoulder_Under_"),
    "arm": ("JD_Arm_UpperPlate_", "JD_Arm_Bracer_"),
    "block": ("JD_Belt_Band", "JD_Belt_", "JD_Cloth_", "JD_Leg_", "JD_Head_", "JD_Torso_", "JD_Shoulder_", "JD_Arm_"),
}
ALLOWED = {"torso": ("torso", "shoulder"), "clavicle": ("torso", "shoulder"), "upperarm": ("shoulder", "arm"),
           "lowerarm": ("arm",), "other": ()}

scene = bpy.context.scene
scene.frame_set(scene.frame_start)
dg = bpy.context.evaluated_depsgraph_get()
body = bpy.data.objects["JD_Body_Undersuit"]


SRC_NAMES = []                                  # nama objek zirah sumber dorongan (indeks = JD_FitSrc)


def group_tree(prefixes):
    """BVH gabungan satu kelompok + peta indeks poligon -> indeks di SRC_NAMES."""
    verts, polys, owner = [], [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or o is body or not o.name.startswith(prefixes):
            continue
        if o.name not in SRC_NAMES:
            SRC_NAMES.append(o.name)
        si = SRC_NAMES.index(o.name)
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        off = len(verts)
        verts += [ev.matrix_world @ v.co for v in me.vertices]
        polys += [tuple(off + i for i in p.vertices) for p in me.polygons]
        owner += [si] * len(me.polygons)
        ev.to_mesh_clear()
    return (BVHTree.FromPolygons(verts, polys), owner) if polys else (None, owner)


trees, owners = {}, {}
for k, v in GROUPS.items():
    trees[k], owners[k] = group_tree(v)

seg = SK.bone_segments()
CLASS_OF = {}
for n in seg:
    if n.startswith(("pelvis", "spine_", "neck_", "head")):
        CLASS_OF[n] = "torso"
    elif n.startswith("clavicle_"):
        CLASS_OF[n] = "clavicle"
    elif n.startswith("upperarm_"):
        CLASS_OF[n] = "upperarm"
    elif n.startswith(("lowerarm_", "hand_")):
        CLASS_OF[n] = "lowerarm"
    elif n.startswith(("thigh_", "calf_", "foot_", "ball_")):
        CLASS_OF[n] = "other"
SEGS = [(n, h, t) for n, (h, t) in seg.items() if n in CLASS_OF and "twist" not in n]


def vclass(p):
    best, bd = "other", 1e9
    for n, h, t in SEGS:
        q, f = intersect_point_line(p, h, t)
        q = h if f < 0 else t if f > 1 else q
        d = (p - q).length
        if d < bd:
            best, bd = CLASS_OF[n], d
    return best


def gap_stats(tag):
    """Median jarak permukaan zirah ke badan (cm) per kelompok, untuk laporan sebelum/sesudah."""
    me = body.data
    mw = body.matrix_world
    bt = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    out = []
    for k in ("torso", "shoulder", "arm"):
        ds = []
        for o in bpy.data.objects:
            if o.type == "MESH" and o.name.startswith(GROUPS[k]):
                ev = o.evaluated_get(dg)
                m2 = ev.to_mesh()
                ds += [bt.find_nearest(ev.matrix_world @ v.co)[3] for v in m2.vertices]
                ev.to_mesh_clear()
        ds.sort()
        out.append(f"{k} {ds[len(ds) // 2] * 100:.1f}")
    print(f"celah median ({tag}), cm:", " | ".join(out))


gap_stats("sebelum")
bm = bmesh.new()
bm.from_mesh(body.data)
bm.verts.ensure_lookup_table()
bm.normal_update()
mw = body.matrix_world
mwi = mw.inverted()
nv = len(bm.verts)
pos = [mw @ v.co for v in bm.verts]
nrm = [(mw.to_3x3() @ v.normal).normalized() for v in bm.verts]
raw, cap, src = [0.0] * nv, [MAX_PUSH] * nv, [-1] * nv
for i in range(nv):
    o_ = pos[i] + nrm[i] * 0.001
    hb = trees["block"].ray_cast(o_, nrm[i], REACH)
    if hb[0] is not None:
        cap[i] = max(0.0, min(MAX_PUSH, hb[3] - GAP))
    best = None
    for g in ALLOWED[vclass(pos[i])]:
        if trees[g] is None:
            continue
        if g == "shoulder" and abs(nrm[i].x) < SHOULDER_MIN_LAT:
            continue                                  # trapezius (normal ke atas) tidak didorong pauldron -> tidak berpunuk
        h = trees[g].ray_cast(o_, nrm[i], REACH)
        if h[0] is not None and (best is None or h[3] < best):
            best = h[3]
            src[i] = owners[g][h[2]]
    if best is not None:
        raw[i] = max(0.0, min(MAX_PUSH, best - GAP))

nb = [[e.other_vert(v).index for e in v.link_edges] for v in bm.verts]
for i in range(nv):                                   # hit di luar jangkauan dorongan tidak dihitung sebagai sumber
    if raw[i] <= 0:
        src[i] = -1
d = raw[:]
for _ in range(SPREAD_ITERS):                         # sebar: di bawah zirah tetap penuh, di luar meluruh halus
    d = [min(cap[i], max(raw[i], 0.5 * d[i] + 0.5 * sum(d[j] for j in nb[i]) / max(1, len(nb[i])))) for i in range(nv)]
for _ in range(3):                                    # haluskan sedikit lagi (tanpa melewati batas)
    d = [min(cap[i], 0.5 * d[i] + 0.5 * sum(d[j] for j in nb[i]) / max(1, len(nb[i]))) if raw[i] == 0 else
         min(cap[i], max(0.85 * raw[i], 0.5 * d[i] + 0.5 * sum(d[j] for j in nb[i]) / max(1, len(nb[i])))) for i in range(nv)]

front = [i for i in range(nv) if src[i] >= 0]       # vertex hasil sebaran mewarisi sumber tetangga terdekat (BFS)
while front:
    nxt = []
    for i in front:
        for j in nb[i]:
            if src[j] < 0 and d[j] > 1e-4:
                src[j] = src[i]
                nxt.append(j)
    front = nxt

moved = 0
for i, v in enumerate(bm.verts):
    if d[i] <= 1e-4:
        continue
    k = d[i]
    for _ in range(5):                                # pengaman: jangan lebih dekat dari GAP/2 ke zirah mana pun
        p = pos[i] + nrm[i] * k
        hit = trees["block"].find_nearest(p)
        if hit[0] is None or hit[3] >= GAP * 0.5:
            break
        k *= 0.6
    v.co = mwi @ (pos[i] + nrm[i] * k)
    moved += 1
bm.to_mesh(body.data)
bm.free()
me = body.data
for an, at in (("JD_FitPush", "FLOAT"), ("JD_FitSrc", "INT")):
    if an in me.attributes:
        me.attributes.remove(me.attributes[an])
    me.attributes.new(an, at, "POINT")
me.attributes["JD_FitPush"].data.foreach_set("value", [x if x > 1e-4 else 0.0 for x in d])
me.attributes["JD_FitSrc"].data.foreach_set("value", [x if d[i] > 1e-4 else -1 for i, x in enumerate(src)])
body["jd_fit_src"] = __import__("json").dumps(SRC_NAMES)
me.update()
dg = bpy.context.evaluated_depsgraph_get()
gap_stats("sesudah")
print(f"FIT: {moved} dari {nv} vertex didorong | dorongan maks {max(d) * 100:.1f} cm")
