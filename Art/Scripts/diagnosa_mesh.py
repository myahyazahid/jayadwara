"""Diagnosa masalah mesh ter-skin di satu wilayah tubuh ("lengan robek", "ketiak bolong", "paha keropos", "leher meleh").

Headless (tidak menyimpan .blend apa pun):
  blender --background --factory-startup --python Art/Scripts/diagnosa_mesh.py -- <file.fbx> --tulang upperarm_r,lowerarm_r
        --out <dir> [--pose semua|<nama>[,<nama>]] [--height 1.806] [--profil Art/Scripts/pose_profil/manny.json]
        [--radius 0.12] [--sebelum <dir diagnosa sebelumnya>] [--res 420]
        [--pembanding <fbx model sehat> [--height-pembanding M] | --pembanding-hasil <dir diagnosa model sehat>] [--tanpa-render]
Wilayah = vertex yang SECARA FISIK dekat ruas tulang --tulang (jarak <= --radius m pada tinggi 1,806, diskalakan --height),
apa pun bobotnya, supaya vertex yang salah dibobot tetap tertangkap. Untuk "lengan kanan robek": --tulang upperarm_r,lowerarm_r;
ketiak: --tulang upperarm_r,clavicle_r; leher: --tulang neck_01,neck_02,head; paha: --tulang thigh_l,calf_l.

Pemeriksaan (semua di wilayah):
  1 lubang          loop tepi terbuka; berapa melebar di pose (keliling pose / rest)
  2 jahitan_terbelah vertex kembar (posisi sama, tidak tersambung) yang bobotnya beda -> terpisah saat bergerak (GLB Tripo!)
  3 bobot_jauh      vertex yang tulang dominannya jauh dari vertex itu, padahal ada tulang lain jauh lebih dekat
  4 bobot_tajam     tepi dengan lompatan bobot > 0,6 untuk satu tulang -> lipatan/robek tajam
  5 bobot_rusak     tanpa bobot, > 4 influence, tidak ternormalisasi
  6 tembus          pasangan segitiga yang saling menembus di pose tetapi tidak di rest
  7 normal_terbalik muka anggota badan yang normalnya menghadap ke tulang (ke dalam)
  8 regangan        p99 & maks per pose, lokasi terburuk
Hasil di <out>: diagnosa.md (tempel ke laporan: dugaan penyebab berurutan + kode resep di Hermes/panduan_kerja_claude.md),
diagnosa.json, render rest & pose terburuk dari 4 sudut dengan vertex bermasalah DIWARNAI:
  merah = tepi lubang, magenta = bobot ke tulang jauh, kuning = jahitan terbelah, oranye = bobot tajam, biru = tembus.
--pembanding: jalankan diagnosa yang sama (wilayah & pose sama) di model SEHAT (mis. Art/Export/SK_Aksa.fbx) dan laporkan hanya
  yang lebih buruk dari model sehat. Tanpa pembanding, tepi baju/kantong & lipatan sendi wajar bisa ikut tercurigai. WAJIB dipakai.
--sebelum: tabel sebelum/sesudah dengan hasil diagnosa lama (wajib setelah perbaikan).
Exit code 0 = tidak ada temuan, 1 = ada temuan.
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_line
from mathutils.kdtree import KDTree

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not argv or "--tulang" not in argv:
    print(__doc__)
    sys.exit(2)


def opt(name, default, cast=str):
    return cast(argv[argv.index(name) + 1]) if name in argv else default


FBX = Path(argv[0]).resolve()
OUT = Path(opt("--out", str(FBX.parent / ("diagnosa_" + FBX.stem)))).resolve()
TULANG = [t.strip() for t in opt("--tulang", "").split(",") if t.strip()]
H = opt("--height", 1.806, float)
SC = H / 1.806
RADIUS = opt("--radius", 0.12, float) * SC
RES = opt("--res", 420, int)
POSE_ARG = opt("--pose", "semua")
PROFIL = json.loads(Path(opt("--profil", str(Path(__file__).resolve().parent / "pose_profil" / "manny.json"))).read_text(encoding="utf-8"))
SEBELUM = opt("--sebelum", "")
PEMBANDING_FBX = opt("--pembanding", "")
PEMBANDING_DIR = opt("--pembanding-hasil", "")
TANPA_RENDER = "--tanpa-render" in argv
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- impor
if FBX.is_file() and FBX.stat().st_size < 1024 and FBX.read_bytes().startswith(b"version https://git-lfs"):
    print(f"GAGAL: {FBX} masih pointer Git LFS (file asli belum diunduh). Jalankan: git lfs pull --include=\"{FBX.name}\"")
    sys.exit(2)
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=str(FBX))
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
meshes = [o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers)]
if arm is None or not meshes:
    print("GAGAL: FBX tidak berisi armature + mesh ter-skin")
    sys.exit(2)
zs = [(o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices]
if max(zs) - min(zs) > 20:                        # data cm -> meter
    for o in bpy.data.objects:
        if o.parent is None:
            o.scale = o.scale * 0.01
bpy.context.view_layer.update()
bones = arm.pose.bones
bad = [t for t in TULANG if t not in bones]
if bad:
    print(f"GAGAL: tulang tidak ada: {bad}. Tulang yang ada: {sorted(b.name for b in arm.data.bones)}")
    sys.exit(2)
scene = bpy.context.scene
MW = arm.matrix_world


def ujung(pb):
    """Ujung anatomis tulang (dunia): kepala anak utama (bukan twist/ik), kalau ada; selain itu ekor. Ekor tulang hasil impor
    FBX tidak sejajar anggota badan (mis. lowerarm Manny), jadi tidak dipakai untuk arah."""
    anak = [c for c in pb.children if "twist" not in c.name and not c.name.startswith("ik_")]
    if anak:
        c = max(anak, key=lambda c: (c.head - pb.head).length)
        if (c.head - pb.head).length > 1e-6:
            return MW @ c.head
    return MW @ pb.tail


def seg(name):                                    # ruas tulang di dunia (pose saat ini): kepala -> ujung anatomis
    pb = bones[name]
    return MW @ pb.head, ujung(pb)


def dist_seg(p, a, b):
    t = intersect_point_line(p, a, b)[1]
    t = min(max(t, 0.0), 1.0)
    return (p - (a + (b - a) * t)).length


# ---------------------------------------------------------------- pose (sama dengan audit_karakter.py)
AX = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}
POSES = {"rest": []}
POSES.update({k: v for k, v in PROFIL.get("pose", {}).items() if k != "rest"})
ARAH = PROFIL.get("arah", {})


def depth(name):
    n, b_ = 0, arm.data.bones[name]
    while b_.parent:
        n, b_ = n + 1, b_.parent
    return n


def reset_pose():
    if arm.animation_data:
        arm.animation_data.action = None
    arm.data.pose_position = "POSE"
    for pb in bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def set_world(pb, W):
    pb.matrix = MW.inverted() @ W
    bpy.context.view_layer.update()


def apply_pose(pname):
    reset_pose()
    if pname in POSES:
        for name, axis, val in sorted(POSES[pname], key=lambda o: depth(o[0])):
            if name not in bones:
                continue
            pb = bones[name]
            W = MW @ pb.matrix
            if axis == "down":
                set_world(pb, Matrix.Translation((0, 0, -val * SC)) @ W)
            else:
                h = W.translation.copy()
                set_world(pb, Matrix.Translation(h) @ Matrix.Rotation(math.radians(val), 4, AX[axis]) @ Matrix.Translation(-h) @ W)
    else:
        for name in sorted(ARAH[pname], key=depth):
            if name not in bones:
                continue
            pb = bones[name]
            W = MW @ pb.matrix
            h = MW @ pb.head
            cur = (ujung(pb) - h).normalized()
            R = cur.rotation_difference(Vector(ARAH[pname][name]).normalized()).to_matrix().to_4x4()
            set_world(pb, Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ W)


ALL_POSES = list(POSES) + [k for k in ARAH if k not in POSES]
POSE_LIST = [p for p in ALL_POSES if p != "rest"] if POSE_ARG == "semua" else [p.strip() for p in POSE_ARG.split(",")]
unknown = [p for p in POSE_LIST if p not in ALL_POSES]
if unknown:
    print(f"GAGAL: pose tidak ada di profil: {unknown}. Ada: {ALL_POSES}")
    sys.exit(2)


def posed_coords():
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    for o in meshes:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        out[o.name] = [o.matrix_world @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    return out


# ---------------------------------------------------------------- data rest
reset_pose()
REST = posed_coords()
deform = [b.name for b in arm.data.bones if b.use_deform]
rest_seg = {n: seg(n) for n in deform}
region_seg = [rest_seg[t] if t in rest_seg else seg(t) for t in TULANG]

info = {}           # per objek: data wilayah
for o in meshes:
    me = o.data
    names = {vg.index: vg.name for vg in o.vertex_groups}
    co = REST[o.name]
    W = [{names[g.group]: g.weight for g in v.groups if g.weight > 1e-4 and g.group in names} for v in me.vertices]
    near = [min(dist_seg(p, a, b) for a, b in region_seg) for p in co]
    reg = {i for i, d in enumerate(near) if d <= RADIUS}
    info[o.name] = {"co": co, "W": W, "reg": reg}
# tulang pembanding "terdekat" = hanya tulang yang benar-benar dipakai sebagai bobot dominan (rantai kosong, mis. sash_* tanpa
# mesh, tidak dihitung)
dipakai = {max(w, key=w.get) for d in info.values() for w in d["W"] if w}
near_seg = {n: s_ for n, s_ in rest_seg.items() if n in dipakai or n in TULANG}   # tulang wilayah selalu dihitung
n_reg = sum(len(d["reg"]) for d in info.values())
print(f"wilayah {TULANG} radius {RADIUS:.3f} m: {n_reg} vertex")
if n_reg == 0:
    print("GAGAL: tidak ada vertex di wilayah; periksa --tulang / --radius / --height")
    sys.exit(2)

hasil = {"fbx": str(FBX), "tulang": TULANG, "radius_m": RADIUS, "vertex_wilayah": n_reg}
mark = {o.name: {} for o in meshes}           # vertex -> warna


def tandai(oname, idx, warna):
    mark[oname].setdefault(idx, warna)


# 5 bobot rusak
tanpa = lebih4 = taknorm = 0
for oname, d in info.items():
    for i in d["reg"]:
        w = d["W"][i]
        if not w:
            tanpa += 1
            tandai(oname, i, "magenta")
        elif len(w) > 4:
            lebih4 += 1
        elif abs(sum(w.values()) - 1) > 0.01:
            taknorm += 1
hasil["bobot_rusak"] = {"tanpa_bobot": tanpa, "lebih_4_influence": lebih4, "tidak_normal": taknorm}

# 3 bobot jauh
jauh, jauh_tulang, jauh_set = 0, {}, set()
for oname, d in info.items():
    for i in d["reg"]:
        w = d["W"][i]
        if not w:
            continue
        dom = max(w, key=w.get)
        if dom not in rest_seg:
            continue
        p = d["co"][i]
        d_dom = dist_seg(p, *rest_seg[dom])
        nearest = min(near_seg, key=lambda n: dist_seg(p, *near_seg[n]))
        d_near = dist_seg(p, *near_seg[nearest])
        if d_dom > d_near + 0.25 * SC and d_dom > 3 * max(d_near, 0.01 * SC):   # model sehat (Aksa, bahu jaket -> clavicle): maks 0,20
            jauh += 1
            k = f"{dom} (terdekat {nearest})"
            jauh_tulang[k] = jauh_tulang.get(k, 0) + 1
            tandai(oname, i, "magenta")
            jauh_set.add((oname, i))
hasil["bobot_jauh"] = {"vertex": jauh, "per_tulang": sorted(jauh_tulang.items(), key=lambda kv: -kv[1])[:8]}

# 4 bobot tajam, 1 lubang (topologi)
tajam, tajam_tulang = 0, {}
loops = []
for o in meshes:
    d = info[o.name]
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table()
    for e in bm.edges:
        a, b = e.verts[0].index, e.verts[1].index
        if a not in d["reg"] and b not in d["reg"]:
            continue
        wa, wb = d["W"][a], d["W"][b]
        for bone in set(wa) | set(wb):
            if abs(wa.get(bone, 0) - wb.get(bone, 0)) > 0.6:
                tajam += 1
                tajam_tulang[bone] = tajam_tulang.get(bone, 0) + 1
                tandai(o.name, a, "oranye")
                tandai(o.name, b, "oranye")
                break
    # loop tepi terbuka yang menyentuh wilayah
    bnd = [e for e in bm.edges if e.is_boundary]
    adj = {}
    for e in bnd:
        a, b = e.verts[0].index, e.verts[1].index
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    seen = set()
    for s in adj:
        if s in seen:
            continue
        comp, stack = [], [s]
        seen.add(s)
        while stack:
            v = stack.pop()
            comp.append(v)
            for n in adj[v]:
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
        if any(v in d["reg"] for v in comp):
            loops.append((o.name, comp))
            for v in comp:
                tandai(o.name, v, "merah")
    bm.free()
hasil["bobot_tajam"] = {"tepi": tajam, "per_tulang": sorted(tajam_tulang.items(), key=lambda kv: -kv[1])[:8]}

# 2 jahitan terbelah: vertex kembar tak tersambung
kembar = []
for o in meshes:
    d = info[o.name]
    idx = sorted(d["reg"])
    kd = KDTree(len(idx))
    for j, i in enumerate(idx):
        kd.insert(d["co"][i], j)
    kd.balance()
    edges = {tuple(sorted(e.vertices)) for e in o.data.edges}
    for j, i in enumerate(idx):
        for _, j2, dist in kd.find_range(d["co"][i], 0.0002 * SC):
            i2 = idx[j2]
            if i2 <= i or tuple(sorted((i, i2))) in edges:
                continue
            wa, wb = d["W"][i], d["W"][i2]
            diff = sum(abs(wa.get(k, 0) - wb.get(k, 0)) for k in set(wa) | set(wb))
            kembar.append((o.name, i, i2, diff))
beda = [k for k in kembar if k[3] > 0.05]
for oname, i, i2, _ in beda:
    tandai(oname, i, "kuning")
    tandai(oname, i2, "kuning")
hasil["jahitan_terbelah"] = {"pasangan_kembar": len(kembar), "bobot_beda": len(beda)}

# 7 normal terbalik (anggota badan: arah normal vs arah dari tulang dominan)
balik = total_f = 0
for o in meshes:
    d = info[o.name]
    for f in o.data.polygons:
        if not all(v in d["reg"] for v in f.vertices):
            continue
        c = sum((d["co"][v] for v in f.vertices), Vector()) / len(f.vertices)
        w = d["W"][f.vertices[0]]
        if not w:
            continue
        dom = max(w, key=w.get)
        if dom not in rest_seg:
            continue
        a, b = rest_seg[dom]
        t = min(max(intersect_point_line(c, a, b)[1], 0.0), 1.0)
        out_dir = c - (a + (b - a) * t)
        if out_dir.length < 0.01 * SC:
            continue
        n = (o.matrix_world.to_3x3() @ f.normal).normalized()
        total_f += 1
        if n.dot(out_dir.normalized()) < -0.3:
            balik += 1
hasil["normal_terbalik"] = {"muka": balik, "dari": total_f, "persen": round(100 * balik / max(total_f, 1), 1)}


# ---------------------------------------------------------------- per pose: regangan, lubang melebar, jahitan terpisah, tembus
def tri_list(o, coords, verts_ok):
    tris, owners = [], []
    for f in o.data.polygons:
        if any(v in verts_ok for v in f.vertices):
            vs = list(f.vertices)
            for k in range(1, len(vs) - 1):
                tris.append((vs[0], vs[k], vs[k + 1]))
    return tris


def intersecting_pairs(o, coords, tris):
    if not tris:
        return set()
    bvh = BVHTree.FromPolygons(coords, tris, all_triangles=True, epsilon=0.0)
    pairs = set()
    for a, b in bvh.overlap(bvh):
        if a >= b or set(tris[a]) & set(tris[b]):
            continue
        pairs.add((a, b))
    return pairs


wide = {o.name: {i for i, p in enumerate(info[o.name]["co"]) if min(dist_seg(p, s0, s1) for s0, s1 in region_seg) <= RADIUS * 1.6}
        for o in meshes}
tris_by = {o.name: tri_list(o, REST[o.name], wide[o.name]) for o in meshes}
rest_pairs = {o.name: intersecting_pairs(o, REST[o.name], tris_by[o.name]) for o in meshes}
pose_res, biru = {}, {}
for pname in POSE_LIST:
    apply_pose(pname)
    P = posed_coords()
    strains, worst = [], (0.0, None)
    for o in meshes:
        d = info[o.name]
        r, c = REST[o.name], P[o.name]
        for e in o.data.edges:
            a, b = e.vertices
            if a not in d["reg"] and b not in d["reg"]:
                continue
            l0 = (r[a] - r[b]).length
            if l0 < 0.002 * SC:
                continue
            l1 = (c[a] - c[b]).length
            strains.append(abs(l1 - l0) / l0)
            if abs(l1 - l0) > worst[0]:
                w = d["W"][a]
                worst = (abs(l1 - l0), (tuple(round(x, 3) for x in r[a]), max(w, key=w.get) if w else "-"))
    strains.sort()
    lp = []
    for oname, comp in loops:
        r, c = REST[oname], P[oname]
        ext = lambda pts: max(max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3))
        lp.append(round(ext([c[v] for v in comp]) / max(ext([r[v] for v in comp]), 1e-6), 2))
    sep = max(((P[on][i] - P[on][i2]).length for on, i, i2, _ in beda), default=0.0)
    new_pen = 0
    for o in meshes:
        cur = intersecting_pairs(o, P[o.name], tris_by[o.name])
        nw = cur - rest_pairs[o.name]
        new_pen += len(nw)
        if True:
            for a, b in list(nw)[:4000]:
                for v in tris_by[o.name][a] + tris_by[o.name][b]:
                    if v in info[o.name]["reg"]:
                        biru.setdefault(o.name, set()).add(v)
    pose_res[pname] = {
        "regangan_p99_persen": round(100 * strains[int(0.99 * (len(strains) - 1))], 1) if strains else 0.0,
        "regangan_maks_cm": round(worst[0] * 100, 2), "lokasi_maks": worst[1],
        "lubang_melebar_x": max(lp, default=1.0), "jahitan_terpisah_cm": round(sep * 100, 2), "tembus_baru": new_pen,
    }
    print(f"  {pname:18s} p99 {pose_res[pname]['regangan_p99_persen']:5.1f}%  maks {pose_res[pname]['regangan_maks_cm']:6.2f} cm"
          f"  lubang x{pose_res[pname]['lubang_melebar_x']}  jahitan {pose_res[pname]['jahitan_terpisah_cm']} cm"
          f"  tembus {new_pen}")
reset_pose()
hasil["pose"] = pose_res
worst_pose = max(pose_res, key=lambda p: (pose_res[p]["regangan_p99_persen"] + 10 * (pose_res[p]["lubang_melebar_x"] - 1)
                                           + pose_res[p]["jahitan_terpisah_cm"] + pose_res[p]["tembus_baru"] / 50))
hasil["pose_terburuk"] = worst_pose
kembar_set = {(on, i) for on, i, i2, _ in beda} | {(on, i2) for on, i, i2, _ in beda}
akibat = [(on, c) for on, c in loops if sum((on, v) in jauh_set or (on, v) in kembar_set for v in c) > 0.3 * len(c)]   # akibat F2/F3
big_loops = [(on, len(c)) for on, c in loops if len(c) >= 6 and (on, c) not in akibat]
hasil["segitiga_wilayah"] = sum(len(t) for t in tris_by.values())
loop_daftar = []
for on, comp in sorted(loops, key=lambda lc: -len(lc[1])):
    pts = [REST[on][v] for v in comp]
    cen = sum(pts, Vector()) / len(pts)
    tb = {}
    for v in comp:
        w = info[on]["W"][v]
        if w:
            dmn = max(w, key=w.get)
            tb[dmn] = tb.get(dmn, 0) + 1
    loop_daftar.append({"tepi": len(comp), "pusat": [round(c, 3) for c in cen], "tulang": max(tb, key=tb.get) if tb else "-",
                        "ukuran_cm": round(max(max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)) * 100, 1),
                        "akibat": (on, comp) in akibat})
hasil["loop_daftar"] = loop_daftar
hasil["lubang"] = {"loop_akibat_bobot_atau_jahitan": len(akibat), "loop": len(loops), "loop_besar_>=6": len(big_loops), "vertex_tepi": sum(len(c) for _, c in loops),
                   "melebar_maks_x": max((p["lubang_melebar_x"] for p in pose_res.values()), default=1.0)}

# ---------------------------------------------------------------- pembanding (model sehat, wilayah & pose sama)
PB = None
if PEMBANDING_FBX and not PEMBANDING_DIR:
    import subprocess
    PEMBANDING_DIR = str(OUT / "pembanding")
    cmd = [bpy.app.binary_path, "--background", "--factory-startup", "--python", str(Path(__file__).resolve()), "--",
           PEMBANDING_FBX, "--tulang", ",".join(TULANG), "--out", PEMBANDING_DIR, "--pose", POSE_ARG, "--height",
           opt("--height-pembanding", str(H)), "--radius", str(RADIUS / SC), "--tanpa-render"]
    if "--profil" in argv:
        cmd += ["--profil", opt("--profil", "")]
    print("pembanding:", " ".join(cmd))
    subprocess.run(cmd, check=False)
if PEMBANDING_DIR:
    PB = json.loads((Path(PEMBANDING_DIR) / "diagnosa.json").read_text(encoding="utf-8"))
    hasil["pembanding"] = PB["fbx"]


def pb_pose(p, k, default=0.0):
    return PB["pose"].get(p, {}).get(k, default) if PB else default


# ---------------------------------------------------------------- dugaan penyebab (urut dari paling mungkin)
dugaan = []
L, J, B, T = hasil["lubang"], hasil["jahitan_terbelah"], hasil["bobot_jauh"], hasil["bobot_tajam"]
sep_max = max(p["jahitan_terpisah_cm"] for p in pose_res.values())


def pb_(*ks):                                      # nilai bersarang dari hasil pembanding, mis. pb_("lubang", "melebar_maks_x")
    if not PB:
        return 0
    d = PB
    for k in ks:
        d = d[k]
    return d


if B["vertex"] > (pb_("bobot_jauh", "vertex") + 10 if PB else 0):
    dugaan.append((95 if B["vertex"] >= 30 else 75, "BOBOT KE TULANG SALAH", f"{B['vertex']} vertex: {B['per_tulang'][:3]}"
                   + (f"; {len(akibat)} loop lubang di wilayah ini adalah akibatnya" if akibat else ""), "F3"))
if J["bobot_beda"] and sep_max > max(0.5 * SC, (max(p["jahitan_terpisah_cm"] for p in PB["pose"].values()) + 0.3) if PB else 0):
    dugaan.append((92, "JAHITAN TERBELAH", f"{J['bobot_beda']} pasangan vertex kembar berbobot beda, terpisah {sep_max} cm saat pose"
                   + (f"; {len(akibat)} loop lubang adalah akibatnya" if akibat else ""), "F2"))
lebar_ref = pb_("lubang", "melebar_maks_x") if PB else 1.15
if PB and L["loop_besar_>=6"] > pb_("lubang", "loop_besar_>=6"):
    dugaan.append((88, "LUBANG BARU", f"{L['loop_besar_>=6']} loop tepi terbuka di wilayah vs {pb_('lubang', 'loop_besar_>=6')} di model sehat "
                   f"(tepi {L['vertex_tepi']} vs {pb_('lubang', 'vertex_tepi')} vertex); lihat daftar loop & warna merah", "F1"))
elif L["loop_besar_>=6"] and L["melebar_maks_x"] > lebar_ref + (0.15 if PB else 0):
    dugaan.append((90 if PB else 60, "LUBANG" if PB else "LUBANG? (tepi baju juga melebar; ulangi dengan --pembanding)",
                   f"{L['loop_besar_>=6']} loop tepi terbuka (di luar akibat bobot/jahitan), melebar x{L['melebar_maks_x']}"
                   + (f" vs pembanding x{lebar_ref}" if PB else ""), "F1"))
elif L["loop_besar_>=6"] and not PB:
    dugaan.append((25, "LUBANG (diam)", f"{L['loop_besar_>=6']} loop tepi terbuka, tidak melebar; bisa tepi baju/kantong yang wajar — "
                   "cek gambar apakah terlihat tembus", "F1"))
if T["tepi"] > (pb_("bobot_tajam", "tepi") * 1.5 + 20 if PB else 20):
    dugaan.append((60, "BOBOT TAJAM", f"{T['tepi']} tepi lompatan bobot > 0,6: {T['per_tulang'][:3]}"
                   + (f" (pembanding {pb_('bobot_tajam', 'tepi')})" if PB else ""), "F4"))
if sum(hasil["bobot_rusak"].values()):
    dugaan.append((70, "BOBOT RUSAK", str(hasil["bobot_rusak"]), "F3"))
seg_w = max(hasil["segitiga_wilayah"], 1)
pen = {p: r["tembus_baru"] / seg_w for p, r in pose_res.items()}
pen_p = max(pen, key=pen.get)
if PB:
    ref = pb_pose(pen_p, "tembus_baru") / max(PB.get("segitiga_wilayah", 1), 1)
    if pen[pen_p] > ref * 1.5 + 0.01:
        dugaan.append((55, "TEMBUS", f"{pose_res[pen_p]['tembus_baru']} pasangan segitiga baru saling menembus di {pen_p} "
                       f"({pen[pen_p]:.3f}/segitiga vs pembanding {ref:.3f})", "F6"))
elif pose_res[pen_p]["tembus_baru"] > 30:
    dugaan.append((35, "TEMBUS? (ulangi dengan --pembanding)", f"{pose_res[pen_p]['tembus_baru']} pasangan segitiga baru menembus di "
                   f"{pen_p}; lipatan sendi pada pose dalam wajar menembus sedikit", "F6"))
nb, nb_ref = hasil["normal_terbalik"]["persen"], (pb_("normal_terbalik", "persen") if PB else 15)
if nb > nb_ref + (10 if PB else 0):
    dugaan.append((40 if PB else 30, "NORMAL TERBALIK" + ("" if PB else "? (ulangi dengan --pembanding)"),
                   f"{nb}% muka menghadap ke dalam" + (f" vs pembanding {nb_ref}%" if PB else ""), "F7"))
melar = [(p, r["regangan_p99_persen"], pb_pose(p, "regangan_p99_persen")) for p, r in pose_res.items()]
melar = [m for m in melar if (m[1] > m[2] + 8 if PB else m[1] > 35)]
if melar and not any(d[3] in ("F1", "F2", "F3") for d in dugaan):
    p_, v_, r_ = max(melar, key=lambda m: m[1] - m[2])
    dugaan.append((50, "MELAR", f"p99 {v_}% di {p_}" + (f" vs pembanding {r_}%" if PB else "") +
                   f", maks {pose_res[p_]['regangan_maks_cm']} cm di {pose_res[p_]['lokasi_maks']}", "F5"))
dugaan.sort(key=lambda d: -d[0])
hasil["dugaan"] = [{"skor": s, "masalah": m, "bukti": b, "resep": r} for s, m, b, r in dugaan]

# ---------------------------------------------------------------- render dengan penanda
if any(d["resep"] == "F6" for d in hasil["dugaan"]):           # biru hanya kalau tembus memang dicurigai (kalau tidak, menutupi warna lain)
    for on, vs in biru.items():
        for v in vs:
            mark[on].setdefault(v, "biru")
WARNA = {"merah": (1, 0.05, 0.05, 1), "magenta": (1, 0, 1, 1), "kuning": (1, 0.9, 0, 1), "oranye": (1, 0.45, 0, 1),
         "biru": (0.1, 0.4, 1, 1)}
for o in meshes:
    me = o.data
    attr = me.color_attributes.new("diagnosa", "FLOAT_COLOR", "POINT")
    for i in range(len(me.vertices)):
        attr.data[i].color = WARNA.get(mark[o.name].get(i), (0.72, 0.72, 0.72, 1))
    me.color_attributes.active_color = attr
try:
    scene.render.engine = "BLENDER_WORKBENCH"
except TypeError as e:
    print("engine:", e)
    raise
sh = scene.display.shading
sh.light = "STUDIO"
sh.color_type = "VERTEX"
sh.show_backface_culling = True
scene.view_settings.view_transform = "Standard"
if scene.world is None:
    scene.world = bpy.data.worlds.new("Diagnosa")
scene.world.color = (0.55, 0.6, 0.66)
arm.hide_render = True
cam = bpy.data.objects.new("DiagCam", bpy.data.cameras.new("DiagCam"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.lens = 35
cam.data.clip_start, cam.data.clip_end = 0.01 * SC, 200 * SC
gambar = []


def render_set(tag):
    P = posed_coords()
    pts = [P[o.name][i] for o in meshes for i in info[o.name]["reg"]]
    c = sum(pts, Vector()) / len(pts)
    size = max(max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3))
    dist = max(size * 1.6, 0.35 * SC)
    for nama, d in (("depan", (0, -1, 0.15)), ("belakang", (0, 1, 0.15)), ("luar", ((1 if c.x >= 0 else -1), -0.2, 0.1)),
                    ("bawah", ((0.4 if c.x >= 0 else -0.4), -0.3, -1))):
        cam.location = c + Vector(d).normalized() * dist
        cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.resolution_x = scene.render.resolution_y = RES
        f = OUT / f"{tag}_{nama}.png"
        scene.render.filepath = str(f)
        bpy.ops.render.render(write_still=True)
        gambar.append(f.name)


if not TANPA_RENDER:
    reset_pose()
    render_set("rest")
    apply_pose(worst_pose)
    render_set(f"pose_{worst_pose}")
    reset_pose()
hasil["gambar"] = gambar
try:
    if TANPA_RENDER:
        raise ImportError
    from PIL import Image, ImageDraw
    rows = []
    for tag in ("rest", f"pose_{worst_pose}"):
        ims = [Image.open(OUT / f"{tag}_{n}.png").convert("RGB") for n in ("depan", "belakang", "luar", "bawah")]
        r = Image.new("RGB", (RES * 4 + 12, RES + 20), (255, 255, 255))
        ImageDraw.Draw(r).text((4, 4), f"{tag}: depan | belakang | luar | bawah   (merah lubang, magenta bobot jauh, kuning jahitan, "
                                       f"oranye bobot tajam, biru tembus)", fill=(0, 0, 0))
        for k, im in enumerate(ims):
            r.paste(im, (k * (RES + 4), 20))
        rows.append(r)
    s = Image.new("RGB", (rows[0].width, sum(r.height for r in rows)), (255, 255, 255))
    for k, r in enumerate(rows):
        s.paste(r, (0, k * rows[0].height))
    s.save(OUT / "diagnosa_sheet.png")
    hasil["gambar"].append("diagnosa_sheet.png")
except ImportError:
    pass

# ---------------------------------------------------------------- laporan
(OUT / "diagnosa.json").write_text(json.dumps(hasil, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
md = [f"# Diagnosa {FBX.name} — wilayah {', '.join(TULANG)} (radius {RADIUS:.3f} m, {n_reg} vertex)", ""]
md += ["## Dugaan penyebab (urut)", ""]
if hasil["dugaan"]:
    md += [f"{k + 1}. **{d['masalah']}** (skor {d['skor']}) — {d['bukti']} → resep **{d['resep']}**" for k, d in enumerate(hasil["dugaan"])]
else:
    md += ["Tidak ada temuan terukur. Kalau keluhan tetap terlihat: cek pose/sudut yang sama dengan keluhan (--pose), "
           "radius wilayah, dan apakah masalahnya hanya di UE (resep F8)."]
md += ["", "## Angka", "", "| Ukuran | Nilai |", "|---|---|"]
for k in ("lubang", "jahitan_terbelah", "bobot_jauh", "bobot_tajam", "bobot_rusak", "normal_terbalik"):
    md.append(f"| {k} | {json.dumps(hasil[k], ensure_ascii=False, default=str)} |")
md += ["", "## Loop tepi terbuka di wilayah (terbesar dulu)", "",
       "Loop yang juga ada di model sehat = tepi baju/kerah/kantong yang disengaja: JANGAN ditutup. Kandidat F1 = 'tidak' di kolom terakhir "
       "DAN bertanda merah di tempat yang dikeluhkan.", "",
       "| # | vertex tepi | pusat (m) | tulang dominan | ukuran rest (cm) | akibat bobot/jahitan | ada di model sehat? |",
       "|---|---|---|---|---|---|---|"]
for k, L_ in enumerate(hasil["loop_daftar"][:12]):
    if PB and "loop_daftar" in PB:
        ada = any((Vector(L_["pusat"]) - Vector(q["pusat"])).length <= 0.03 * SC and abs(q["tepi"] - L_["tepi"]) <= max(6, 0.3 * L_["tepi"])
                  for q in PB["loop_daftar"])
        ada_s = "ya" if ada else "**tidak**"
    else:
        ada_s = "? (pakai --pembanding)"
    md.append(f"| {k + 1} | {L_['tepi']} | {tuple(L_['pusat'])} | {L_['tulang']} | {L_['ukuran_cm']} | {'ya' if L_['akibat'] else 'tidak'} | {ada_s} |")
md += ["", f"Pose terburuk: **{worst_pose}**", "", "| Pose | regangan p99 % | maks cm | lokasi maks | lubang melebar x | jahitan terpisah cm | tembus baru |",
       "|---|---|---|---|---|---|---|"]
for p, r in pose_res.items():
    md.append(f"| {p} | {r['regangan_p99_persen']} | {r['regangan_maks_cm']} | {r['lokasi_maks']} | {r['lubang_melebar_x']} | "
              f"{r['jahitan_terpisah_cm']} | {r['tembus_baru']} |")
if SEBELUM:
    old = json.loads((Path(SEBELUM) / "diagnosa.json").read_text(encoding="utf-8"))
    md += ["", "## Sebelum → sesudah", "", "| Ukuran | Sebelum | Sesudah | Status |", "|---|---|---|---|"]

    def cmp(nama, a, b, lebih_kecil_baik=True):
        st = "SAMA" if a == b else (("MEMBAIK" if b < a else "MEMBURUK") if lebih_kecil_baik else ("MEMBAIK" if b > a else "MEMBURUK"))
        md.append(f"| {nama} | {a} | {b} | {st} |")

    cmp("loop lubang besar", old["lubang"]["loop_besar_>=6"], hasil["lubang"]["loop_besar_>=6"])
    cmp("lubang melebar x", old["lubang"]["melebar_maks_x"], hasil["lubang"]["melebar_maks_x"])
    cmp("jahitan bobot beda", old["jahitan_terbelah"]["bobot_beda"], hasil["jahitan_terbelah"]["bobot_beda"])
    cmp("bobot jauh", old["bobot_jauh"]["vertex"], hasil["bobot_jauh"]["vertex"])
    cmp("bobot tajam", old["bobot_tajam"]["tepi"], hasil["bobot_tajam"]["tepi"])
    for p in pose_res:
        if p in old["pose"]:
            cmp(f"{p}: regangan p99 %", old["pose"][p]["regangan_p99_persen"], pose_res[p]["regangan_p99_persen"])
            cmp(f"{p}: tembus baru", old["pose"][p]["tembus_baru"], pose_res[p]["tembus_baru"])
md += ["", "Gambar: `diagnosa_sheet.png` (WAJIB dilihat: apakah warna penanda ada di tempat yang dikeluhkan?)."]
(OUT / "diagnosa.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
sys.exit(1 if hasil["dugaan"] else 0)
