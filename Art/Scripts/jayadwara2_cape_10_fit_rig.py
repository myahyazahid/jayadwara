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
ap.add_argument("--skin", choices=("chains", "kinematic"), default="chains",
                help="chains (J1c): bawah jubah ikut rantai cape_* (simulasi UE); kinematic (J1): ikut pinggul/kaki")
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
CHAIN_Z0, CHAIN_Z1 = 1.28, 1.40  # J1c: bobot rantai penuh di bawah CHAIN_Z0, transisi ke bobot kaku s/d CHAIN_Z1
COLLAR_OPEN_Z, COLLAR_OPEN_DEG = 1.40, 55.0   # J1b: bukaan depan diteruskan ke pita kerah (sudut sama dengan intake)
SHOULDER_Z0, SHOULDER_Z1, SHOULDER_K = 1.25, 1.40, 0.12   # J1b: zona bahu/leher yang gulungannya dipadatkan
YOKE_C = (0.0, 0.0, 1.42)        # J1c: titik pusat raycast profil yoke (di sumbu tulang belakang)
YOKE_Z_TOP, YOKE_Z_BOT = 1.60, 1.24   # J1d: sampai kerah leher belakang (<= dagu 1,613, K9); turun melewati zona gulungan lama
HANG_THETA0, HANG_THETA1 = 40.0, 75.0   # J1f: gantung lurus/selubung penuh s/d 40 derajat, hilang di 75 (sisi menempel tubuh)
YOKE_HANG_Z = 1.50               # J1d: di bawah tinggi ini kain yoke menggantung lurus (jari-jari tidak mengecil ke bawah)
CONF_FADE_DEG, CONF_PLEAT_BAND = 8.0, 0.10   # J1e: lebar peralihan rentang di sisi (derajat); lipatan pudar dalam pita ini di bawah tepi atas (m, ruang lama)
EDGE_SMOOTH_Z, EDGE_SMOOTH_IT = 1.30, 12   # J1e: tepi terbuka di atas tinggi ini dihaluskan (iterasi)
HOLE_MAX_SIDES = 20             # J2: loop tepi <= ini sisi dianggap lubang & ditutup
COLLAR_MAX_Z = 1.600            # J2: batas K9 (dagu 1,613 m) — dicek lagi setelah penghalusan tepi
CONF_Z_SIDE, CONF_TOP_A0, CONF_TOP_A1 = 1.55, 100.0, 124.0   # J1e: tepi atas di sisi/lapel (bawah pauldron); peralihan 70-95 derajat
CONF_Z_A, CONF_Z_CUT = 0.65, 1.24   # J1d: kain di atas CONF_Z_A direntangkan; potongan CONF_Z_CUT tiba di kerah YOKE_Z_TOP
YOKE_THETA, YOKE_ROWS, YOKE_BLEND_ROWS = 122.0, 34, 0   # derajat dari punggung; baris; baris bawah yang menyatu ke jubah
YOKE_OVER, YOKE_ORN_MAX = 0.006, 0.04   # yoke 6 mm di luar jubah lama; ornamen > 4 cm di luar lambung diabaikan
YOKE_WHITE_HALF = 0.045         # setengah lebar strip putih = panel putih tengah jubah (diukur ±0,045 m)
YOKE_ENV = 8                     # kolom (x1,5 derajat) untuk selubung yang menjembatani cekungan punggung
PAUL_X, PAUL_Z = 0.21, 1.44     # J1d: tepi dalam pauldron (diukur |x| 0,20-0,22 di z 1,47-1,65); jubah tidak boleh di atasnya
BROOCH_X, BROOCH_Z, BROOCH_R = 0.155, 1.46, 0.042   # bros bahu (m), di sisi dalam pauldron seperti konsep
CHAIN_SAGS = (0.06, 0.13)       # juntai rantai antar-bros (m)
CHAIN_SIDE, CHAIN_PENDANT, CHAIN_BEAD = 0.20, 0.09, 0.0065   # rantai gantung bros, liontin tengah, ukuran butir (m)
PIN_Z = 1.535                   # hiasan emas di puncak strip putih
YOKE_UV = {"red": (0.4027, 0.1999), "white": (0.2039, 0.1783), "gold": (0.5519, 0.8552)}   # atlas cap02; merah = rata-rata jubah
ARM_MARGIN = 0.03                # 14 Okt: jarak bebas jubah dari kulit lengan (m)
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
    c = np.zeros(len(me.vertices) * 3)
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

# ------------------------------------------------------------------ 1c) yoke bahu/leher (J1c, feedback developer)
# Konsep: jubah naik rapi menutup punggung atas & puncak bahu (di bawah pauldron) sampai pangkal leher, panel putih tengah
# mulai tepat dari kerah. Gulungan kerah Tripo (walau dipadatkan) terbaca "terpotong". Di sini lembar yoke baru dibangun dari
# profil badan: tiap irisan vertikal (sudut θ dari punggung) di-raycast dari titik pusat YOKE_C ke luar pada elevasi φ,
# sehingga lereng trapezius tertangkap. Yoke diletakkan di luar lambung badan DAN di luar jubah lama (menutupinya), lalu muka
# jubah lama di bawah yoke dibuang. UV per zona (merah / putih tengah / list emas) dari titik atlas bersih -> batas tajam.
def build_yoke():
    """Yoke leher/bahu (J1c, revisi J1d). Lihat komentar blok di atas.

    J1d (feedback developer): (1) jubah TIDAK menutupi pauldron -> semua muka jubah/yoke di zona pauldron (|x| > PAUL_X,
    z > PAUL_Z) dibuang, yoke berhenti di tepi dalam pauldron; (2) tanpa "lipatan pembatas" -> yoke turun sampai
    YOKE_Z_BOT (di bawah zona gulungan lama) dan baris bawahnya menyatu ke permukaan jubah (tanpa bibir); (3) leher
    belakang selaras -> yoke naik sampai kerah YOKE_Z_TOP, merah = rata-rata jubah; (4) tanpa garis kuning melintang (hanya
    list tipis tegak di tepi strip putih, sama dengan panel putih jubah). Rantai Tripo yang terpotong diganti rantai skrip.
    """
    global P
    bvh_cape = BVHTree.FromPolygons([Vector(p) for p in P], [list(p.vertices) for p in me.polygons])
    C = Vector(YOKE_C)
    UP = Vector((0, 0, 1))

    def ray_dirs(t):
        u = Vector((math.sin(math.radians(t)), math.cos(math.radians(t)), 0.0))
        return [(u * math.cos(math.radians(f)) + UP * math.sin(math.radians(f))).normalized() for f in np.arange(-60.0, 89.0, 0.4)]

    def radii(d):
        hit, _, _, dist = bvh.ray_cast(C + d * 1.2, -d, 1.2)
        rb = (1.2 - dist) if hit is not None else None
        hc, _, _, dc = bvh_cape.ray_cast(C + d * 1.2, -d, 1.2)
        rc = (1.2 - dc) if hc is not None else None
        return rb, rc

    def profile(t):
        prof = []
        for d in ray_dirs(t):
            rb, rc = radii(d)
            if rb is None:
                continue
            r = max(rb + args.clear, (min(rc, rb + YOKE_ORN_MAX) + YOKE_OVER) if rc is not None else 0.0)
            q = C + d * r
            if YOKE_Z_BOT <= q.z <= YOKE_Z_TOP:
                prof.append(q)
        prof.sort(key=lambda q: -q.z)
        return prof

    step = 1.5
    t_max = 0.0
    while t_max + step <= YOKE_THETA and min(len(profile(t_max + step)), len(profile(-t_max - step))) >= 12:
        t_max += step
    thetas = np.arange(-t_max, t_max + 1e-6, step)
    grid = []
    for t in thetas:
        prof = profile(t)
        L = [0.0]
        for a_, b_ in zip(prof, prof[1:]):
            L.append(L[-1] + (b_ - a_).length)
        rows = []
        for k in range(YOKE_ROWS + 1):
            s = L[-1] * k / YOKE_ROWS
            j = max(0, min(len(L) - 2, int(np.searchsorted(L, s)) - 1))
            w = (s - L[j]) / max(L[j + 1] - L[j], 1e-6)
            rows.append(tuple(prof[j].lerp(prof[j + 1], w)))
        grid.append(rows)
    G = np.array(grid)
    Cn = np.array(C)
    Dv = G - Cn
    Dd = np.linalg.norm(Dv, axis=2)
    Dn = Dv / Dd[:, :, None]
    env = np.array([Dd[max(0, i - YOKE_ENV):i + YOKE_ENV + 1].max(axis=0) for i in range(len(Dd))])
    for _ in range(6):
        env[1:-1] = 0.25 * env[:-2] + 0.5 * env[1:-1] + 0.25 * env[2:]
    # J1f: selubung & gantung lurus hanya di punggung tengah; di sisi kain menempel tubuh (bahu) -> tanpa sudut "kotak"
    a_t = np.clip((np.abs(thetas) - HANG_THETA0) / (HANG_THETA1 - HANG_THETA0), 0.0, 1.0)
    keep = 1.0 - a_t * a_t * (3 - 2 * a_t)                  # 1 = punggung (gantung lurus), 0 = sisi (menempel tubuh)
    Dd_body = Dd.copy()
    Dd = Dd_body + (np.maximum(env, Dd) - Dd_body) * keep[:, None]
    # kain jatuh lurus (J1d): di bawah titik terlebar tiap irisan, jari-jari horizontal tidak boleh mengecil lagi
    # (kain menggantung, tidak mengikuti lekuk di bawah tulang belikat) -> tanpa "gembung"/lipatan melintang
    G0 = Cn + Dn * Dd[:, :, None]
    rh = np.hypot(G0[:, :, 0], G0[:, :, 1])
    for j in range(1, rh.shape[1]):
        below = G0[:, j, 2] < YOKE_HANG_Z
        rh[below, j] = np.maximum(rh[below, j], rh[below, j - 1])
    rh0 = np.hypot(G0[:, :, 0], G0[:, :, 1])
    rh = rh0 + (rh - rh0) * keep[:, None]
    k_h = rh / np.maximum(rh0, 1e-6)
    G0[:, :, 0] *= k_h
    G0[:, :, 1] *= k_h
    Dv = G0 - Cn
    Dd = np.linalg.norm(Dv, axis=2)
    Dn = Dv / Dd[:, :, None]
    # baris bawah menyatu ke permukaan jubah lama (+2 mm), transisi halus YOKE_BLEND_ROWS baris -> tanpa bibir/lipatan
    NT, NR = Dd.shape
    for i in range(NT if YOKE_BLEND_ROWS else 0):
        for j in range(NR - YOKE_BLEND_ROWS, NR):
            rb, rc = radii(Vector(Dn[i, j]))
            if rc is None or rb is None:
                continue
            target = max(min(rc, rb + 0.06) + 0.002, rb + args.clear)
            w = (j - (NR - YOKE_BLEND_ROWS - 1)) / YOKE_BLEND_ROWS
            w = w * w * (3 - 2 * w)
            Dd[i, j] = (1 - w) * Dd[i, j] + w * target
    G = Cn + Dn * Dd[:, :, None]
    for _ in range(4):
        G[1:-1] = 0.25 * G[:-2] + 0.5 * G[1:-1] + 0.25 * G[2:]

    def zone(i, j):
        t = 0.5 * (thetas[i] + thetas[i + 1])
        c = 0.25 * (G[i, j] + G[i + 1, j] + G[i, j + 1] + G[i + 1, j + 1])
        tw = math.degrees(YOKE_WHITE_HALF / max(math.hypot(c[0], c[1]), 0.05))
        if abs(t) < tw:
            return "white"
        if abs(t) < tw + 1.2:
            return "gold"                                       # list tipis tegak (sama dengan panel putih jubah)
        return "red"

    def in_pauldron(p):
        return p[2] > PAUL_Z and abs(p[0]) > PAUL_X

    bm = bmesh.new()
    bm.from_mesh(me)
    uvl = bm.loops.layers.uv.active
    # J1e: potong dengan bidang datar (bukan per pusat muka) -> tepi atas lurus, jadi garis kerah mulus setelah direntangkan
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), dist=1e-5,
                           plane_co=(0.0, 0.0, CONF_Z_CUT), plane_no=(0.0, 0.0, 1.0))
    # semua kain (punggung, sisi, lapel) dipotong di bidang yang sama lalu direntangkan ke tinggi target per sudut
    dead = [f for f in bm.faces if f.calc_center_median().z > CONF_Z_CUT]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    # J1d: TANPA lembar yoke terpisah (selalu menyisakan lipatan/sambungan). Kain jubah lama (lipatan tegak & panel putih
    # bertekstur Tripo) DITERUSKAN ke atas: z di atas CONF_Z_A direntangkan sehingga potongan CONF_Z_CUT tiba di kerah, lalu
    # jarak horizontalnya mengikuti permukaan profil G (menggantung lurus) + lipatan aslinya (selisih ke rata-rata lokal).
    z_top_col = G[:, 0, 2]
    F = (YOKE_Z_TOP - CONF_Z_A) / (CONF_Z_CUT - CONF_Z_A)
    cell_r = {}
    for v in bm.verts:
        if v.co.z > CONF_Z_A - 0.05:
            t = math.degrees(math.atan2(v.co.x, v.co.y))
            cell_r.setdefault((int(t // 4), int(v.co.z // 0.03)), []).append(v.co.xy.length)
    cell_m = {k: float(np.mean(r_)) for k, r_ in cell_r.items()}

    def surf_r(t, z):
        i = int(np.clip(np.searchsorted(thetas, t), 1, NT - 1))
        out = []
        for ii in (i - 1, i):
            zc = G[ii, :, 2][::-1]
            rc_ = np.hypot(G[ii, :, 0], G[ii, :, 1])[::-1]
            out.append(float(np.interp(z, zc, rc_)))
        w_ = (t - thetas[i - 1]) / max(thetas[i] - thetas[i - 1], 1e-6)
        return out[0] * (1 - w_) + out[1] * w_

    n_conf = 0
    for v in bm.verts:
        z = v.co.z
        if z <= CONF_Z_A or z > CONF_Z_CUT + 0.001:
            continue
        t = math.degrees(math.atan2(v.co.x, v.co.y))
        # tinggi tepi atas per sudut: kerah di punggung, turun mulus ke bawah pauldron di sisi & lapel (satu garis menerus)
        a_ = min(max((abs(t) - CONF_TOP_A0) / (CONF_TOP_A1 - CONF_TOP_A0), 0.0), 1.0)
        z_tt = YOKE_Z_TOP + (CONF_Z_SIDE - YOKE_Z_TOP) * a_ * a_ * (3 - 2 * a_)
        z_new = CONF_Z_A + (z - CONF_Z_A) * (z_tt - CONF_Z_A) / (CONF_Z_CUT - CONF_Z_A)
        z_new = min(z_new, COLLAR_MAX_Z)                     # K9: kerah <= dagu (1,613) dengan sedikit ruang
        s_t = float(np.clip((t_max - abs(t)) / CONF_FADE_DEG, 0.0, 1.0))
        s_t = s_t * s_t * (3 - 2 * s_t)                       # bentuk radial ikut profil hanya di rentang punggung
        r = v.co.xy.length
        if s_t <= 0 or r < 1e-4:
            v.co.z = z_new
            n_conf += 1
            continue
        w = min(max((z - CONF_Z_A) / 0.12, 0.0), 1.0)
        w = w * w * (3 - 2 * w) * s_t
        pleat = r - cell_m.get((int(t // 4), int(z // 0.03)), r)
        fz = min(max((z - (CONF_Z_CUT - CONF_PLEAT_BAND)) / CONF_PLEAT_BAND, 0.0), 1.0)   # jarak ke tepi atas (ruang lama)
        pleat_k = 1.0 - fz * fz * (3 - 2 * fz)                 # J1e: lipatan memudar menjelang kerah -> cincin kerah rapi
        R = surf_r(t, min(z_new, YOKE_Z_TOP))
        if z_new < YOKE_Z_BOT:
            R = max(float(np.interp(t, thetas, np.hypot(G[:, NR - 1, 0], G[:, NR - 1, 1]))), r - pleat)
        r_new = r + w * ((R + pleat * pleat_k) - r)
        k = r_new / r
        v.co.x *= k
        v.co.y *= k
        v.co.z = z_new
        n_conf += 1
    counts = {"diteruskan": n_conf}
    n_paul = 0
    n_join = 0
    # J1f: tanpa potongan zona pauldron — kain di sisi kini menempel bahu (di bawah pauldron), jadi tidak menutupinya dan
    # tidak ada tepi potongan tegak yang terlihat dari belakang.
    n_paul = 0
    # serpihan kecil (ujung ornamen Tripo yang terpotong) dibuang
    seen, small = set(), []
    for v in bm.verts:
        if v in seen:
            continue
        st, grp = [v], [v]
        seen.add(v)
        while st:
            cur = st.pop()
            for e in cur.link_edges:
                w_ = e.other_vert(cur)
                if w_ not in seen:
                    seen.add(w_)
                    st.append(w_)
                    grp.append(w_)
        if len(grp) < 40:
            small += grp
    bmesh.ops.delete(bm, geom=small, context="VERTS")
    # J1e: tepi terbuka di bagian atas (kerah, sisi, potongan pauldron) dihaluskan sepanjang garisnya -> tanpa gigi/serpihan
    bverts = {v for e in bm.edges if e.is_boundary and min(v_.co.z for v_ in e.verts) > EDGE_SMOOTH_Z for v in e.verts}
    nbr = {v: [e.other_vert(v) for e in v.link_edges if e.is_boundary and e.other_vert(v) in bverts] for v in bverts}
    for _ in range(EDGE_SMOOTH_IT):
        new_co = {}
        for v, ns in nbr.items():
            if len(ns) == 2:
                new_co[v] = v.co * 0.5 + (ns[0].co + ns[1].co) * 0.25
        for v, c_ in new_co.items():
            v.co = c_
    for v in bverts:
        v.co.z = min(v.co.z, COLLAR_MAX_Z)
    # J2: tutup lubang kecil (sisa bukaan ornamen Tripo di area yang direntangkan); tepi kain utama (loop besar) tidak disentuh
    filled = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=HOLE_MAX_SIDES)["faces"]
    u0, v0 = YOKE_UV["red"]
    for f in filled:
        f.smooth = True
        for k, l in enumerate(f.loops):
            l[uvl].uv = (u0 + 0.0015 * (k % 2), v0 + 0.0015 * ((k // 2) % 2))
    print(f"lubang kecil ditutup: {len(filled)} muka")
    # pita di bawah tepi ikut dihaluskan ringan supaya tepi tidak terlipat
    band = [v for v in bm.verts if v.co.z > EDGE_SMOOTH_Z and v not in bverts]
    for _ in range(3):
        upd = {v: v.co * 0.6 + sum((e.other_vert(v).co for e in v.link_edges), Vector()) * (0.4 / len(v.link_edges))
               for v in band if v.link_edges}
        for v, c_ in upd.items():
            v.co = c_

    # ---- ornamen mirip konsep: 2 bros, 2 juntai rantai antar-bros, liontin tengah, rantai gantung di bawah bros,
    # hiasan runcing di puncak strip putih. Ditempel ke permukaan yoke (raycast menuju C) + jarak kecil.
    bvh_y = BVHTree.FromBMesh(bm)

    def on_surface(x, z, lift):
        """titik yoke pada (x, z) tepat (sinar lurus dari belakang, -Y), normal keluar"""
        hit, nrm, _, _ = bvh_y.ray_cast(Vector((x, 1.5, z)), Vector((0, -1, 0)), 2.0)
        if hit is None:
            return None, None
        d = Vector((hit.x, hit.y, 0.0)).normalized()
        n = nrm if nrm.dot(d) > 0 else -nrm
        n = (n + d).normalized()
        return hit + n * lift, n

    def frame(pos, n, along=None):
        t = along.copy() if along is not None else Vector((0, 0, -1))
        t = (t - n * t.dot(n)).normalized()
        b_ = t.cross(n)
        return Matrix.Translation(pos) @ Matrix((b_, t, n)).transposed().to_4x4()

    def add_part(verts, zone_name):
        faces = {f for v in verts for f in v.link_faces}
        u0, v0 = YOKE_UV[zone_name]
        for f in faces:
            f.smooth = True
            for k, l in enumerate(f.loops):
                l[uvl].uv = (u0 + 0.0015 * (k in (1, 2)), v0 + 0.0015 * (k in (2, 3)))
        return len(faces)

    def diamond(pos, n, length, width, zone_name):
        M = frame(pos, n)
        a = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=width, radius2=0.0, depth=length * 0.7,
                                  matrix=M @ Matrix.Translation((0, length * 0.35, 0)) @ Matrix.Rotation(math.radians(-90), 4, "X") @
                                  Matrix.Diagonal((1, 0.5, 1, 1)))["verts"]
        b = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=width, radius2=0.0, depth=length * 0.3,
                                  matrix=M @ Matrix.Translation((0, -length * 0.15, 0)) @ Matrix.Rotation(math.radians(90), 4, "X") @
                                  Matrix.Diagonal((1, 0.5, 1, 1)))["verts"]
        return add_part(a + b, zone_name)

    def chain(points, lift=0.012):
        """butir emas sepanjang kurva (x, z) yang diproyeksikan ke permukaan yoke"""
        pts = []
        for x, z in points:
            p_, n_ = on_surface(x, z, lift)
            if p_ is not None:
                pts.append((p_, n_))
        cnt = 0
        acc = 0.0
        for (p0, n0), (p1, n1) in zip(pts, pts[1:]):
            seg = p1 - p0
            L = seg.length
            while acc <= L:
                q = p0 + seg * (acc / max(L, 1e-6))
                M = frame(q, n0, seg)
                bead = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0,
                                                  matrix=M @ Matrix.Diagonal((CHAIN_BEAD * 0.75, CHAIN_BEAD * 1.3, CHAIN_BEAD * 0.6, 1)))["verts"]
                cnt += add_part(bead, "gold")
                acc += CHAIN_BEAD * 2.1
            acc -= L
        return cnt, pts

    n_orn = 0
    bx, bz = BROOCH_X, BROOCH_Z
    for sx in (-1, 1):                                          # bros
        p_, n_ = on_surface(sx * bx, bz, 0.006)
        if p_ is None:
            continue
        M = frame(p_, n_)
        # J2: bros lebih ornate (konsep): pelat dasar emas, bingkai (bezel) tinggi, 4 ujung panjang + 4 ujung pendek
        # (bintang 8), permata merah berfaset.
        n_orn += add_part(bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=BROOCH_R, radius2=BROOCH_R * 0.86,
                                                depth=0.010, matrix=M)["verts"], "gold")
        n_orn += add_part(bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=BROOCH_R * 0.74, radius2=BROOCH_R * 0.66,
                                                depth=0.022, matrix=M @ Matrix.Translation((0, 0, 0.008)))["verts"], "gold")
        for a_ in range(8):
            ang = math.radians(45 * a_)
            r_ = Vector((math.cos(ang), math.sin(ang), 0.0))
            long_ = a_ % 2 == 0
            ln, wd = (0.040, 0.013) if long_ else (0.022, 0.009)
            n_orn += add_part(bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=wd, radius2=0.0, depth=ln,
                                                    matrix=M @ Matrix.Translation(r_ * (BROOCH_R + ln * 0.4)) @
                                                    Vector((0, 0, 1)).rotation_difference(r_).to_matrix().to_4x4() @
                                                    Matrix.Diagonal((1, 0.45, 1, 1)))["verts"], "gold")
        n_orn += add_part(bmesh.ops.create_icosphere(bm, subdivisions=1, radius=BROOCH_R * 0.58,
                                                     matrix=M @ Matrix.Translation((0, 0, 0.022)) @ Matrix.Diagonal((1, 1, 0.62, 1)))["verts"], "red")
        # rantai gantung di bawah bros + wajik (konsep: rantai turun di sisi panel putih)
        c_, pts = chain([(sx * bx, bz - BROOCH_R - 0.01 - k * 0.01) for k in range(int(CHAIN_SIDE / 0.01))])
        n_orn += c_
        if pts:
            n_orn += diamond(pts[-1][0] + Vector((0, 0, -0.03)), pts[-1][1], 0.06, 0.016, "gold")
    span = bx - BROOCH_R * 0.8
    for sag in CHAIN_SAGS:                                       # juntai antar-bros (parabola)
        xs = np.linspace(-span, span, 40)
        zs = bz - 0.01 - sag * (1 - (xs / span) ** 2)
        c_, _ = chain(list(zip(xs, zs)))
        n_orn += c_
    z_low = bz - 0.01 - max(CHAIN_SAGS)                         # liontin tengah dari juntai terbawah
    c_, pts = chain([(0.0, z_low - k * 0.01) for k in range(int(CHAIN_PENDANT / 0.01))])
    n_orn += c_
    if pts:
        n_orn += diamond(pts[-1][0] + Vector((0, 0, -0.035)), pts[-1][1], 0.07, 0.02, "gold")
    p_, n_ = on_surface(0.0, PIN_Z, 0.006)                       # hiasan runcing puncak strip putih
    if p_ is not None:
        n_orn += diamond(p_, n_, 0.11, 0.022, "gold")
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.update()
    P = coords()
    print(f"bahu/leher: θ ±{t_max:.1f}°, profil {NT}x{NR}; {counts['diteruskan']} vertex kain diteruskan ke kerah "
          f"(z {CONF_Z_A}-{CONF_Z_CUT} -> {CONF_Z_A}-{YOKE_Z_TOP} m); {n_paul} muka di zona pauldron & {len(dead)} muka gulungan dibuang; "
          f"ornamen {n_orn} muka")


build_yoke()
NV = len(me.vertices)
ev = np.zeros(len(me.edges) * 2, dtype=np.int64)
me.edges.foreach_get("vertices", ev)
ev = ev.reshape(-1, 2)
deg = np.bincount(ev.ravel(), minlength=NV).astype(np.float64)
deg[deg == 0] = 1


# ------------------------------------------------------------------ 1d) jubah mengalah ke belakang lengan (14 Okt)
# Developer: tangan/lengan menembus jubah di sisi (lapel & panel samping). Kapsul lengan (upperarm, lowerarm, hand per sisi;
# radius = p90 jarak kulit lengan ke tulang + ARM_MARGIN) dari pose rest; vertex jubah di dalam kapsul didorong ke BELAKANG
# (+Y) sampai keluar kapsul -> jubah di sisi lengan lebih ramping/berada di belakang lengan. Dorongan disamakan dalam radius
# SHARE_R (tebal lembar) lalu disebar halus ke tetangga (tanpa penyok).
def arm_clear():
    global P
    caps = []
    for sd in "lr":
        for seg, (b0, b1) in {"upper": ("upperarm", "lowerarm"), "lower": ("lowerarm", "hand"), "hand": ("hand", None)}.items():
            bone = arm.data.bones[f"{b0}_{sd}"]
            a = np.array(arm.matrix_world @ bone.head_local)
            b = np.array(arm.matrix_world @ (arm.data.bones[f"{b1}_{sd}"].head_local if b1 else bone.tail_local))
            if b1 is None:                                   # telapak + jari: perpanjang ke ujung jari
                b = a + (b - a) * 2.2
            pts = np.array([tuple(bverts[i]) for i, n in enumerate(dom) if n.startswith(f"{b0}") and n.endswith(f"_{sd}")])
            if len(pts) == 0:
                continue
            ab = b - a
            t = np.clip(((pts - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
            r = float(np.percentile(np.linalg.norm(pts - (a + t[:, None] * ab), axis=1), 90)) + ARM_MARGIN
            caps.append((a, b, r))
    need = np.zeros(NV)
    for a, b, r in caps:
        ab = b - a
        t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
        q = a + t[:, None] * ab
        dx, dz = P[:, 0] - q[:, 0], P[:, 2] - q[:, 2]
        h2 = r * r - dx * dx - dz * dz
        inside = (np.linalg.norm(P - q, axis=1) < r) & (h2 > 0)
        req = np.where(inside, q[:, 1] + np.sqrt(np.clip(h2, 0, None)) - P[:, 1], 0.0)
        need = np.maximum(need, req)
    m = share_max(need, P)
    D = m.copy()
    for _ in range(40):
        D = np.maximum(m, 0.5 * D + 0.5 * nb_mean(D) * 0.97)
    P = P.copy()
    P[:, 1] += D
    me.vertices.foreach_set("co", P.ravel())
    me.update()
    print(f"lengan: {len(caps)} kapsul (r {', '.join(f'{c[2] * 100:.0f}' for c in caps)} cm); {int((need > 0.001).sum())} vertex jubah "
          f"di dalam lengan, didorong ke belakang maks {D.max() * 100:.1f} cm ({int((D > 0.001).sum())} vertex ikut halus)")


arm_clear()
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

# J1c: bagian bawah jubah diikat ke rantai cape_* (disimulasikan node AnimNode_JDCapeChains di UE: gravitasi, hambatan
# udara -> terangkat saat jatuh/terbang, tabrakan kapsul kaki). Antar-rantai: sudut di sekeliling badan; sepanjang
# rantai: tinggi (setengah ruas ke tulang tetangga). Di atas CHAIN_Z1 tetap bobot kaku (yoke, ornamen, bahu).
if args.skin == "chains":
    order_c = sorted(CHAINS, key=lambda k: CHAINS[k])
    angs = [CHAINS[k] for k in order_c]
    bone_names = [f"cape_{k}_{i + 1:02d}" for k in order_c for i in range(N_SEG)]
    TARGETS += bone_names
    TI = {g: i for i, g in enumerate(TARGETS)}
    W = np.hstack([W, np.zeros((NV, len(bone_names)))])
    jz = {k: [p_.z for p_ in chain_pts[k]] for k in order_c}

    def along(k, z):
        """bobot ruas rantai k untuk tinggi z: {indeks tulang 0..N-1 (atau -1 = induk spine_05): bobot}."""
        zs = jz[k]
        if z >= zs[0]:
            return {-1: 1.0}
        if z <= zs[-1]:
            return {N_SEG - 1: 1.0}
        b = next(i for i in range(N_SEG) if zs[i] >= z >= zs[i + 1])
        t = (zs[b] - z) / max(zs[b] - zs[b + 1], 1e-6)
        if t < 0.5:
            return {b: 0.5 + t, b - 1: 0.5 - t}
        return {b: 1.5 - t, min(b + 1, N_SEG - 1): t - 0.5} if b + 1 < N_SEG else {b: 1.0}

    for i, p_ in enumerate(P):
        sblend = float(np.clip((CHAIN_Z1 - p_[2]) / (CHAIN_Z1 - CHAIN_Z0), 0, 1))
        sblend = sblend * sblend * (3 - 2 * sblend)
        if sblend <= 0:
            continue
        a = math.degrees(math.atan2(p_[0], p_[1]))
        if a <= angs[0]:
            cw = {order_c[0]: 1.0}
        elif a >= angs[-1]:
            cw = {order_c[-1]: 1.0}
        else:
            k = next(j for j in range(len(angs) - 1) if angs[j] <= a <= angs[j + 1])
            t = (a - angs[k]) / (angs[k + 1] - angs[k])
            t = t * t * (3 - 2 * t)
            cw = {order_c[k]: 1 - t, order_c[k + 1]: t}
        Wc = np.zeros(W.shape[1])
        for ck, cwt in cw.items():
            for bi, bw in along(ck, p_[2]).items():
                Wc[TI["spine_05"] if bi < 0 else TI[f"cape_{ck}_{bi + 1:02d}"]] += cwt * bw
        W[i] = (1 - sblend) * W[i] + sblend * Wc
    print(f"bobot rantai: {int((W[:, len(TARGETS) - len(bone_names):].sum(axis=1) > 0.01).sum())} vertex ikut cape_* "
          f"(penuh di bawah {CHAIN_Z0} m, transisi s/d {CHAIN_Z1} m)")
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
