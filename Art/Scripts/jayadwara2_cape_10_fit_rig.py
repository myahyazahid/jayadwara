"""Jubah Jayadwara2 J1 — fit lokal (bebas dari badan), skeleton jubah, bobot kinematik (docs/26 J1).

  blender --background Art/Blender/jayadwara2_cape_v00_intake.blend --python Art/Scripts/jayadwara2_cape_10_fit_rig.py -- \
      [--out Art/Blender/jayadwara2_cape_v01_rig.blend] [--clear 0.025] [--collar-clear 0.012]
Hasil (collection `10_Cape`): `JD2_Cape` (mesh ter-fit + bobot), `JD2C_Armature` (salinan skeleton Jayadwara2, nama tulang SAMA
supaya Copy Pose From Mesh di UE cocok, + rantai `cape_{c,l,r,fl,fr}_01..06` berbobot 0 untuk J3). Tiap tulang JD2C yang
namanya ada di JD2_Armature diberi constraint Copy Transforms -> pose badan di Blender langsung menggerakkan jubah (meniru UE).

1) Fit lokal: badan dilihat sebagai "lambung radial" per ketinggian (raycast horizontal dari luar ke sumbu tubuh, lengan
   dikecualikan karena bergerak, pauldron dikecualikan supaya jubah lewat di bawahnya — kalau tidak, kerah jadi "rak" datar). Vertex jubah yang lebih dekat dari lambung + jarak bebas didorong keluar radial; dorongan
   disamakan dalam radius 3 cm (sisi dalam & luar lembar bergerak sama, tebal tidak terbalik) lalu disebar halus ke tetangga.
2) Bobot: diambil dari kulit badan terdekat (lengan -> clavicle, kaki bawah -> paha, leher/kepala -> spine_05: kerah tidak ikut
   kepala), dilemahkan menurut jarak ke "bobot jauh" per ketinggian (pelvis / spine_03 / spine_05); porsi paha <= LEG_MAX
   (pelajaran R3d: rok kinematik, tanpa simulasi). Dihaluskan lewat topologi + tetangga spasial (sisi dalam/luar sama).
"""
import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(ROOT / "Art" / "Blender" / "jayadwara2_cape_v01_rig.blend"))
ap.add_argument("--clear", type=float, default=0.025, help="m, jarak bebas jubah ke badan di bawah kerah")
ap.add_argument("--no-calf", action="store_true", help="betis dipetakan ke paha (bukan calf_*)")
ap.add_argument("--leg-max", type=float, default=0.6)
ap.add_argument("--near-d1", type=float, default=0.23, help="m, jarak tempat bobot kulit hilang")
ap.add_argument("--collar-clear", type=float, default=0.012, help="m, jarak bebas pita kerah ke leher")
args = ap.parse_args(argv)
OUT = Path(args.out)
assert "jayadwara2_v05_rig_r3" not in OUT.name and "intake" not in OUT.name

COLLAR_Z = 1.60 - 0.07          # pita kerah (puncak 1,60 dari J0)
SHARE_R = 0.03                  # m: dorongan & bobot disamakan dalam radius ini (tebal lembar jubah < 3 cm)
LEG_MAX = args.leg_max          # porsi maksimum kaki (paha+betis; sisanya pinggul) — pola sayap R3d (0,55)
CALF = not args.no_calf         # jubah di belakang betis ikut betis (tumit naik ke belakang saat langkah)
NEAR_D0, NEAR_D1 = 0.03, args.near_d1   # bobot kulit penuh s/d 3 cm, hilang di NEAR_D1 (bobot jauh)
CHAINS = {"c": 0.0, "l": 60.0, "r": -60.0, "fl": 112.0, "fr": -112.0}   # derajat dari punggung (+Y), positif ke +X (kiri karakter)
CHAIN_TOP = {"c": 1.45, "l": 1.47, "r": 1.47, "fl": 1.47, "fr": 1.47}
N_SEG = 6
COLLAR_OPEN_Z, COLLAR_OPEN_DEG = 1.40, 55.0   # J1b: bukaan depan diteruskan ke pita kerah (sudut sama dengan intake)
SHOULDER_Z0, SHOULDER_Z1, SHOULDER_K = 1.25, 1.40, 0.12   # J1b: zona bahu/leher yang gulungannya dipadatkan
JUNK_R, JUNK_Z = 0.13, 1.20     # muka jubah sedekat ini ke sumbu tubuh = sisa panel depan di dalam badan/antara kaki

body = bpy.data.objects["JD2_Body"]
arm = bpy.data.objects["JD2_Armature"]
src = bpy.data.objects["JD2_Cape_Source"]
coll = bpy.data.collections["10_Cape"]
for n in ("JD2_Cape", "JD2C_Armature"):
    o = bpy.data.objects.get(n)
    if o is not None:
        d = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        (bpy.data.meshes if isinstance(d, bpy.types.Mesh) else bpy.data.armatures).remove(d)

cape = src.copy()
cape.data = src.data.copy()
cape.name = cape.data.name = "JD2_Cape"
coll.objects.link(cape)
src.hide_render = src.hide_viewport = True
for e in (o for o in coll.objects if o.name.startswith("JD2C_ANCHOR_")):
    e.hide_render = True
me = cape.data

# sisa panel depan Tripo di sumbu tubuh (antara kaki / di dalam badan): kalau didorong radial dari sumbu, arahnya acak -> sirip.
bm = bmesh.new()
bm.from_mesh(me)
junk = [f for f in bm.faces if (lambda c: c.z < JUNK_Z and c.xy.length < JUNK_R)(f.calc_center_median())]
# J1b (feedback developer): depan pita kerah ikut dibuka — kalau tidak, pita menjuntai melintang di atas zirah dada
# ("bulatan merah" di depan). Konsep: depan bersih, jubah hanya dari bahu ke belakang.
front = [f for f in bm.faces if f not in junk and (lambda c: c.z >= COLLAR_OPEN_Z and
         math.degrees(math.atan2(abs(c.x), -c.y)) < COLLAR_OPEN_DEG)(f.calc_center_median())]
bmesh.ops.delete(bm, geom=junk + front, context="FACES")
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
# serpihan (rantai/ornamen yang terputus dari lembar utama)
seen, isl = set(), []
for v in bm.verts:
    if v in seen:
        continue
    st, grp = [v], [v]
    seen.add(v)
    while st:
        cur = st.pop()
        for e in cur.link_edges:
            w = e.other_vert(cur)
            if w not in seen:
                seen.add(w)
                st.append(w)
                grp.append(w)
    isl.append(grp)
big = max(len(g) for g in isl)
loose = [v for g in isl if len(g) < max(200, big * 0.02) for v in g]
bmesh.ops.delete(bm, geom=loose, context="VERTS")
bm.to_mesh(me)
bm.free()
me.update()
NV = len(me.vertices)
print(f"buang sisa di sumbu tubuh (r < {JUNK_R} m, z < {JUNK_Z} m): {len(junk)} muka; depan pita kerah: {len(front)} muka; "
      f"serpihan {len(loose)} vertex")

# ------------------------------------------------------------------ badan: BVH tanpa lengan
ARM_KEYS = ("upperarm", "lowerarm", "hand")
gname = {g.index: g.name for g in body.vertex_groups}
bme = body.data
bw = body.matrix_world
bverts = [bw @ v.co for v in bme.vertices]
dom = []
for v in bme.vertices:
    best = max(v.groups, key=lambda g: g.weight, default=None)
    dom.append(gname[best.group] if best is not None else "")
is_arm = [any(k in n for k in ARM_KEYS) for n in dom]
is_pauldron = [n.startswith("clavicle") for n in dom]     # pelat bahu: bobot kaku 50/50 clavicle-upperarm (R3)


def polys_without(*masks):
    return [list(p.vertices) for p in bme.polygons
            if not any(sum(m[i] for i in p.vertices) * 2 >= len(p.vertices) for m in masks)]


# lambung fit: tanpa lengan & pauldron (jubah lewat DI BAWAH pauldron); bobot: pauldron ikut (jubah di bawahnya ikut bahu)
bvh = BVHTree.FromPolygons(bverts, polys_without(is_arm, is_pauldron))
poly_verts = polys_without(is_arm)
bvh_w = BVHTree.FromPolygons(bverts, poly_verts)

# ------------------------------------------------------------------ topologi jubah (numpy)
ev = np.zeros(len(me.edges) * 2, dtype=np.int64)
me.edges.foreach_get("vertices", ev)
ev = ev.reshape(-1, 2)
deg = np.bincount(ev.ravel(), minlength=NV).astype(np.float64)
deg[deg == 0] = 1


def nb_mean(a):
    s = np.zeros_like(a)
    np.add.at(s, ev[:, 0], a[ev[:, 1]])
    np.add.at(s, ev[:, 1], a[ev[:, 0]])
    return s / (deg[:, None] if a.ndim == 2 else deg)


def coords():
    c = np.zeros(NV * 3)
    me.vertices.foreach_get("co", c)
    return c.reshape(-1, 3)


def share_max(vals, P):
    """Nilai per vertex = maksimum di dalam radius SHARE_R (sisi dalam & luar lembar diperlakukan sama)."""
    kd = KDTree(NV)
    for i, p in enumerate(P):
        kd.insert(p, i)
    kd.balance()
    out = vals.copy()
    for i in np.nonzero(vals > 0)[0]:
        for _, j, _ in kd.find_range(P[i], SHARE_R):
            out[j] = max(out[j], vals[i])
    return out


# ------------------------------------------------------------------ 1) fit lokal radial
def hull_need(P):
    need = np.zeros(NV)
    dirs = np.zeros((NV, 3))
    for i, p in enumerate(P):
        h = Vector((p[0], p[1], 0.0))
        r = h.length
        if r < 1e-4:
            continue
        d = h / r
        dirs[i] = d
        hit, _, _, dist = bvh.ray_cast(Vector((d.x * 2.0, d.y * 2.0, p[2])), -d, 2.0)
        if hit is None:
            continue
        clear = args.collar_clear if p[2] > COLLAR_Z else args.clear
        need[i] = max(0.0, (2.0 - dist) + clear - r)
    return need, dirs


P = coords()
P0 = P.copy()
need0, _ = hull_need(P)
print(f"fit: awal {int((need0 > 0.001).sum())} vertex di dalam lambung+jarak bebas (maks {need0.max() * 100:.1f} cm)")
for it in range(4):
    need, dirs = hull_need(P)
    if (need > 0.001).sum() == 0:
        break
    m = share_max(need, P)
    D = m.copy()
    for _ in range(60):                     # sebar halus ke tetangga, tidak pernah di bawah kebutuhan
        D = np.maximum(m, 0.5 * D + 0.5 * nb_mean(D) * 0.985)
    P = P + dirs * D[:, None]
    me.vertices.foreach_set("co", P.ravel())
    me.update()
    print(f"fit: putaran {it + 1}: dorong {int((D > 0.001).sum())} vertex, maks {D.max() * 100:.1f} cm")
# J1b: rapikan bahu/leher. Pita kerah Tripo = gulungan tebal (seperti tudung terlipat); setelah didorong keluar jadi "donat"
# menonjol di sekeliling leher (dilihat dari atas). Konsep: jubah jatuh rapi dari bahu. Di zona atas, jarak radial tiap vertex
# ke permukaan terdalam lembar di sel (sudut, tinggi) yang sama dikompres x SHOULDER_K, lalu lembar ditempel ke lambung badan.
def hull_radius(P):
    hr = np.zeros(NV)
    for i, p in enumerate(P):
        h = Vector((p[0], p[1], 0.0))
        if h.length < 1e-4:
            continue
        d = h / h.length
        hit, _, _, dist = bvh.ray_cast(Vector((d.x * 2.0, d.y * 2.0, p[2])), -d, 2.0)
        hr[i] = (2.0 - dist) if hit is not None else 0.0
    return hr


r = np.linalg.norm(P[:, :2], axis=1)
ang = np.degrees(np.arctan2(P[:, 0], P[:, 1]))
wz = np.clip((P[:, 2] - SHOULDER_Z0) / (SHOULDER_Z1 - SHOULDER_Z0), 0, 1)
wz = wz * wz * (3 - 2 * wz)
cell = (np.floor(ang / 4.0).astype(np.int64) * 1000 + np.floor(P[:, 2] / 0.025).astype(np.int64))
rmin = {}
for c_, r_ in zip(cell, r):
    rmin[c_] = min(rmin.get(c_, 9.0), r_)
rin = np.array([rmin[c_] for c_ in cell])
hr = hull_radius(P)
clear = np.where(P[:, 2] > COLLAR_Z, args.collar_clear, args.clear)
r_new = np.where(hr > 0, np.maximum(hr + clear, 0) + (r - rin) * SHOULDER_K, r)
r_fin = r + (r_new - r) * wz
r_fin = np.maximum(r_fin, np.where(hr > 0, hr + clear, 0))      # tidak boleh masuk lagi
k = np.divide(r_fin, r, out=np.ones_like(r), where=r > 1e-4)
P[:, 0] *= k
P[:, 1] *= k
me.vertices.foreach_set("co", P.ravel())
me.update()
print(f"bahu/leher: {int((wz > 0).sum())} vertex di zona {SHOULDER_Z0}-{SHOULDER_Z1} m, tebal gulungan x{SHOULDER_K}; "
      f"radial berubah rata-rata {np.abs(r_fin - r)[wz > 0].mean() * 100:.1f} cm, maks {np.abs(r_fin - r).max() * 100:.1f} cm")

need_end, _ = hull_need(P)
moved = np.linalg.norm(P - P0, axis=1)
print(f"fit: sisa {int((need_end > 0.001).sum())} vertex di dalam (maks {need_end.max() * 100:.2f} cm); "
      f"geser rata-rata {moved.mean() * 100:.1f} cm, maks {moved.max() * 100:.1f} cm")

# ------------------------------------------------------------------ 2) skeleton jubah
ca = arm.copy()
ca.data = arm.data.copy()
ca.name = ca.data.name = "JD2C_Armature"
ca.animation_data_clear()
coll.objects.link(ca)
ca.hide_render = True
ca.hide_viewport = False
for c in ca.users_collection:
    pass


def chain_points(key):
    a = math.radians(CHAINS[key])
    ang = np.degrees(np.arctan2(P[:, 0], P[:, 1]))          # 0 = punggung (+Y), + ke +X
    win = np.abs(((ang - CHAINS[key]) + 180) % 360 - 180) < 7
    z_end = P[win, 2].min() + 0.03
    pts = []
    for z in np.linspace(CHAIN_TOP[key], z_end, N_SEG + 1):
        sel = win & (np.abs(P[:, 2] - z) < 0.03)
        if sel.sum() == 0:
            r = pts[-1].xy.length if pts else 0.2
            pts.append(Vector((math.sin(a) * r, math.cos(a) * r, z)))
        else:
            q = P[sel].mean(axis=0)
            pts.append(Vector((q[0], q[1], z)))
    return pts


chain_pts = {k: chain_points(k) for k in CHAINS}
bpy.context.view_layer.objects.active = ca
for o in bpy.context.view_layer.objects:
    o.select_set(o == ca)
bpy.ops.object.mode_set(mode="EDIT")
eb = ca.data.edit_bones
inv = ca.matrix_world.inverted()
for k, pts in chain_pts.items():
    parent = eb["spine_05"]
    for i in range(N_SEG):
        b = eb.new(f"cape_{k}_{i + 1:02d}")
        b.head, b.tail = inv @ pts[i], inv @ pts[i + 1]
        b.roll = 0.0
        b.parent = parent
        b.use_connect = i > 0
        b.use_deform = True
        parent = b
bpy.ops.object.mode_set(mode="OBJECT")
n_bones = len(ca.data.bones)
print(f"skeleton jubah: {n_bones} tulang ({n_bones - len(arm.data.bones)} rantai cape_*)")

# constraint: tulang bernama sama mengikuti badan (meniru Copy Pose From Mesh)
for pb in ca.pose.bones:
    if pb.name in arm.pose.bones:
        c = pb.constraints.new("COPY_TRANSFORMS")
        c.target, c.subtarget = arm, pb.name

# ------------------------------------------------------------------ 3) bobot kinematik
def remap(g):
    side = g[-1] if g[-2:] in ("_l", "_r") else ""
    if any(k in g for k in ARM_KEYS):
        return f"clavicle_{side}"
    if g.startswith("thigh"):
        return f"thigh_{side}"
    if g.startswith(("calf", "foot", "ball")):
        return f"calf_{side}" if CALF else f"thigh_{side}"
    if g.startswith(("neck", "head")):
        return "spine_05"
    if g.startswith(("cloth_", "scarf_")):
        return "pelvis"
    return g


TARGETS = sorted({remap(g) for g in gname.values()} | {"pelvis", "spine_03", "spine_05"})
TI = {g: i for i, g in enumerate(TARGETS)}
G = len(TARGETS)
WB = np.zeros((len(bme.vertices), G))
for v in bme.vertices:
    for g in v.groups:
        WB[v.index, TI[remap(gname[g.group])]] += g.weight
s = WB.sum(axis=1, keepdims=True)
WB = np.divide(WB, s, out=np.zeros_like(WB), where=s > 0)


def far_w(z):
    w = np.zeros(G)
    knots = [(0.90, "pelvis"), (1.20, "spine_03"), (1.45, "spine_05")]
    if z <= knots[0][0]:
        w[TI["pelvis"]] = 1
    elif z >= knots[-1][0]:
        w[TI["spine_05"]] = 1
    else:
        for (z0, b0), (z1, b1) in zip(knots, knots[1:]):
            if z0 <= z <= z1:
                t = (z - z0) / (z1 - z0)
                w[TI[b0]] += 1 - t
                w[TI[b1]] += t
                break
    return w


W = np.zeros((NV, G))
dist = np.zeros(NV)
for i, p in enumerate(P):
    pv = Vector(p)
    hit, _, fi, d = bvh_w.find_nearest(pv)
    dist[i] = d
    vs = poly_verts[fi]
    iw = np.array([1.0 / max((bverts[j] - hit).length, 1e-4) for j in vs])
    near = (WB[vs] * iw[:, None]).sum(axis=0) / iw.sum()
    f = float(np.clip(1.0 - (d - NEAR_D0) / (NEAR_D1 - NEAR_D0), 0.0, 1.0))
    W[i] = f * near + (1 - f) * far_w(p[2])

LEGS = [TI[g] for g in ("thigh_l", "thigh_r", "calf_l", "calf_r") if g in TI]


def cap_legs(W):
    leg = W[:, LEGS].sum(axis=1)
    over = np.clip(leg - LEG_MAX, 0, None)
    k = np.divide(LEG_MAX, leg, out=np.ones_like(leg), where=leg > LEG_MAX)
    W[:, LEGS] *= k[:, None]
    W[:, TI["pelvis"]] += over
    return W


W = cap_legs(W)
for _ in range(8):
    W = 0.5 * W + 0.5 * nb_mean(W)
# sisi dalam & luar lembar: rata-rata tetangga spasial
kd = KDTree(NV)
for i, p in enumerate(P):
    kd.insert(p, i)
kd.balance()
W2 = np.zeros_like(W)
for i, p in enumerate(P):
    idx = [j for _, j, _ in kd.find_range(p, SHARE_R)]
    W2[i] = W[idx].mean(axis=0)
W = cap_legs(W2)
# maksimum 4 pengaruh, buang < 2 %
order = np.argsort(-W, axis=1)
W_final = np.zeros_like(W)
for i in range(NV):
    top = [j for j in order[i, :4] if W[i, j] >= 0.02]
    W_final[i, top] = W[i, top]
W_final /= W_final.sum(axis=1, keepdims=True)

cape.vertex_groups.clear()
for g in TARGETS:
    col = W_final[:, TI[g]]
    idx = np.nonzero(col > 0)[0]
    if len(idx) == 0:
        continue
    vg = cape.vertex_groups.new(name=g)
    for i in idx:
        vg.add([int(i)], float(col[i]), "REPLACE")
cape.modifiers.clear()
mod = cape.modifiers.new("Armature", "ARMATURE")
mod.object = ca
cape.parent = ca
cape.matrix_parent_inverse = ca.matrix_world.inverted()

used = {g: float(W_final[:, TI[g]].sum()) for g in TARGETS if W_final[:, TI[g]].sum() > 0}
print("bobot (jumlah per tulang, % vertex):", {g: round(100 * v / NV, 1) for g, v in sorted(used.items(), key=lambda kv: -kv[1])})
print(f"porsi paha maks {W_final[:, LEGS].sum(axis=1).max():.2f}; jarak ke badan median {np.median(dist) * 100:.1f} cm")

cape["jd2_cape"] = "J1 fit lokal + bobot kinematik (docs/26)"
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
print("disimpan ->", OUT)
