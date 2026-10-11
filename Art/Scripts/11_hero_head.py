"""Iterasi 2 (REVISI KEPALA, mengikuti head detail konsep) — mengganti semua JD_Head_*.

Konsep (concept-art/jayadwara_final.webp, panel HEAD DETAIL):
- Helm merah BERSUDUT/berfaset (bukan kubah bulat), puncak runcing, rusuk tengah.
- BINGKAI EMAS berbentuk V di atas mata (rendah di tengah, naik ke pelipis) yang menyatu dengan pangkal tanduk.
- PELINDUNG PIPI EMAS turun di sisi wajah; pelat pipi merah bersudut di belakangnya.
- ORNAMEN DAHI emas besar berukir (bentuk teratai/api) dengan latar merah, menjulang ke puncak helm.
- Mata LEBAR bersudut, sudut luar naik (emissive konstan). K6: rasio lebar:tinggi >= 3:1 (bukan lensa bulat).
- Faceplate putih lebar berbentuk V dengan rusuk tengah, dagu runcing merah.
- Tanduk emas sangat tebal di pangkal, tumbuh dari pelipis, melengkung ke atas, ujung sedikit ke dalam (K4).
- Pecahan sirip merah runcing di samping/belakang helm.
Nama objek dipertahankan untuk rig; bagian baru: CheekGuard, ForeheadInset, Shard.
"""
import importlib
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jd_common as C
import jd_hero as Hh
importlib.reload(C)
importlib.reload(Hh)

S = {"l": +1, "r": -1}
COLL = "02_Head"
HC = Vector((0, 0.02, 1.785))           # pusat kepala


# Proporsi diukur dari reference plane (lebar depan konsep: 0,154 m di z 1,70; 0,198 di 1,75; 0,245 di 1,80;
# kedalaman samping ±20% lebih kecil dari versi pertama). Semua bagian (kecuali tanduk & kerah) di-warp:
# x dikali faktor yang bergantung tinggi (meruncing ke rahang), bagian belakang (y>0) dipendekkan.
WARP_Z = [(1.60, 0.66), (1.68, 0.66), (1.75, 0.80), (1.82, 0.90), (1.88, 0.92), (2.10, 0.92)]
BACK_Y = 0.70


def fx(z):
    for (z0, f0), (z1, f1) in zip(WARP_Z[:-1], WARP_Z[1:]):
        if z <= z1:
            t = max(0.0, min(1.0, (z - z0) / (z1 - z0)))
            return f0 + (f1 - f0) * t
    return WARP_Z[-1][1]


def warp(bm):
    for v in bm.verts:
        x, y, z = v.co
        v.co = Vector((x * fx(z), y * BACK_Y if y > 0 else y, z))


def P(name, bm, zone, slot, **kw):
    if not any(k in name for k in ("Horn", "Collar")):
        warp(bm)
    return C.finish_part(name, bm, COLL, zone, slot, smooth="angle", bone=kw.pop("bone", "head"), **kw)


def merge(dst, src):
    tmp = bpy.data.meshes.new("_mg")
    src.to_mesh(tmp)
    src.free()
    dst.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)


def mirror_pts(pts):
    """Titik sisi kiri (x>=0) -> ditambah pasangan cermin (tanpa duplikat di x=0)."""
    out = []
    for x, y, z in pts:
        out.append((x, y, z))
        if abs(x) > 1e-6:
            out.append((-x, y, z))
    return out


def out_normal(p, fwd=0.6):
    """Normal kira-kira menghadap luar dari pusat kepala, condong ke depan."""
    n = (Vector(p) - HC)
    n.z *= 0.5
    n = n.normalized() + Vector((0, -fwd, 0))
    return n.normalized()


for ob in list(bpy.data.objects):
    if ob.type == "MESH" and ob.name.startswith("JD_Head_"):
        bpy.data.objects.remove(ob, do_unlink=True)
made = []

# ================================================================ HELM bersudut (hull berfaset)
helm_pts = mirror_pts([
    (0.0, -0.030, 1.938), (0.0, 0.070, 1.922), (0.0, 0.150, 1.862), (0.0, 0.172, 1.770),     # rusuk tengah: puncak -> belakang
    (0.062, -0.095, 1.872), (0.0, -0.108, 1.885),                                             # dahi
    (0.090, -0.040, 1.900), (0.098, 0.060, 1.895), (0.080, 0.130, 1.860),                      # sisi atas
    (0.120, -0.060, 1.815), (0.126, 0.040, 1.810), (0.112, 0.130, 1.770),                      # pelipis
    (0.072, 0.132, 1.700), (0.0, 0.150, 1.688),                                               # belakang bawah (meruncing ke leher)
    (0.110, -0.035, 1.700), (0.082, 0.060, 1.665),                                            # rahang samping
    (0.080, -0.088, 1.705),                                                                    # depan bawah (di balik faceplate)
])
bm = bmesh.new()
Hh.hull(bm, helm_pts)
bm = Hh.harden(bm, thick=0.0, bevel=0.0035, segs=1, angle=25)
made.append(P("JD_Head_Helm", bm, "red", "Armor"))

# pelat belakang berlapis (tampak belakang konsep): dua pelat V merah menumpuk di belakang helm
for z0, w, dy in ((1.840, 0.085, 0.0), (1.775, 0.075, 0.006)):
    bm = bmesh.new()
    path = [Vector((-w, 0.120 + dy, z0 + 0.022)), Vector((0, 0.162 + dy, z0 - 0.020)), Vector((w, 0.120 + dy, z0 + 0.022))]
    Hh.ribbon(bm, Hh.catmull(path, 4), [Vector((0, 1, 0.2))] * 9, 0.036)
    bm = Hh.harden(bm, thick=0.012, bevel=0.002, segs=1)
    made.append(P(f"JD_Head_BackPlate_{int(z0 * 1000)}", bm, "red", "Armor"))

# rusuk puncak merah (pisau tipis di atas helm, menonjol dari puncak ke belakang)
bm = bmesh.new()
path = Hh.catmull([(0, -0.040, 1.930), (0, 0.010, 1.950), (0, 0.080, 1.935), (0, 0.150, 1.880), (0, 0.190, 1.800)], 4)
Hh.tube(bm, path, lambda t: 0.030 * (1 - 0.70 * t), n=4, squash=(1.0, 0.32), up=(0, 0, 1))      # bilah rusuk, bukan kawat
made.append(P("JD_Head_Crest", bm, "red", "Armor"))

# ================================================================ WAJAH: faceplate putih + dagu MERAH di SATU permukaan
# (feedback: silver tidak boleh bercelah dengan merah; dagu diakhiri lapisan merah, bukan silver semua)
FP_TOP = 1.764
V_SPLIT = 0.62                         # di atas: faceplate putih; di bawah: dagu merah (z ±1,695 -> 1,652)


def face(u, v):
    k = (u - 0.5) * 2
    ak = abs(k)
    W = 0.096 * (1 - 0.92 * v ** 1.15)
    x = k * W
    z = FP_TOP + 0.026 * ak * (1 - v) - v * (FP_TOP - 1.652)        # tepi atas mengikuti sisi bawah mata
    y = -0.114 - 0.016 * (1 - k * k) * (1 - 0.3 * v) - 0.011 * (1 - ak) ** 2 - 0.026 * v * v + 0.020 * ak * ak
    return Vector((x, y, z))


def face_part(v0, v1):
    return lambda u, v: face(u, v0 + (v1 - v0) * v)


def cheek_fn(s):
    """Pelat pipi merah yang TUMBUH dari tepi faceplate (berbagi tepi -> tanpa celah), menyapu ke luar-belakang."""
    eu = 1.0 if s > 0 else 0.0

    def fn(t, v):
        return face(eu, v) + Vector((s * 0.042 * t * (1 - 0.35 * v), 0.052 * t, 0.006 * t))
    return fn


bm = bmesh.new()
Hh.grid_surface(bm, face_part(0.0, V_SPLIT), 12, 6)
bm = Hh.harden(bm, thick=0.010, bevel=0.0015, segs=1)
made.append(P("JD_Head_Faceplate", bm, "white", "Face"))
bm = bmesh.new()
Hh.grid_surface(bm, face_part(V_SPLIT, 1.0), 12, 4)
bm = Hh.harden(bm, thick=0.010, bevel=0.0015, segs=1)
made.append(P("JD_Head_Chin", bm, "red", "Armor"))

for sd, s in S.items():
    L = sd.upper()

    # ============================================================ BINGKAI EMAS V di atas mata -> pelipis (pangkal tanduk)
    brow = [(0.0, -0.126, 1.797), (s * 0.030, -0.122, 1.806), (s * 0.065, -0.110, 1.824), (s * 0.095, -0.090, 1.842),
            (s * 0.117, -0.068, 1.852)]
    pts = Hh.catmull(brow, 4)
    bm = bmesh.new()
    Hh.ribbon(bm, pts, [out_normal(p, 0.9) for p in pts], lambda t: 0.040 - 0.006 * t)      # bingkai tebal menyambung ke tanduk
    bm = Hh.harden(bm, thick=0.014, bevel=0.0025, segs=1)
    made.append(P(f"JD_Head_Brow_{L}", bm, "gold", "Armor"))

    # ============================================================ PELAT PIPI MERAH: tumbuh dari tepi faceplate (tanpa celah)
    cf = cheek_fn(s)
    bm = bmesh.new()
    Hh.grid_surface(bm, cf, 3, 8)
    bm = Hh.harden(bm, thick=0.012, bevel=0.002, segs=1)
    made.append(P(f"JD_Head_Cheek_{L}", bm, "red", "Armor"))

    # ============================================================ PELINDUNG PIPI EMAS: dari ujung bingkai alis menyusuri tepi luar pipi
    pts = [Vector((s * 0.117, -0.068, 1.852))] + [cf(1.0, v) for v in (0.0, 0.2, 0.4, 0.6, 0.8)]
    pts = Hh.catmull(pts, 4)
    nrm = [out_normal(p, 0.4) for p in pts]
    pts = [p + n * 0.007 for p, n in zip(pts, nrm)]
    bm = bmesh.new()
    Hh.ribbon(bm, pts, nrm, lambda t: 0.024 - 0.012 * t)
    bm = Hh.harden(bm, thick=0.012, bevel=0.0025, segs=1)
    made.append(P(f"JD_Head_CheekGuard_{L}", bm, "gold", "Armor"))

    # ============================================================ TANDUK emas: lengkung-S seperti konsep (keluar, lalu ujung menekuk ke dalam)
    bm = bmesh.new()
    path = Hh.catmull([(s * 0.100, -0.070, 1.848), (s * 0.114, -0.075, 1.878), (s * 0.117, -0.070, 1.912),
                       (s * 0.110, -0.060, 1.945), (s * 0.098, -0.050, 1.970), (s * 0.088, -0.044, 1.988)], 6)   # tinggi, ujung hanya sedikit menekuk ke dalam
    Hh.tube(bm, path, lambda t: 0.042 * (1 - t) ** 0.75 + 0.0006, n=8, squash=(1.0, 0.62), up=(0, -1, 0))
    # tanduk kecil kedua di belakang tanduk utama (konsep: dua lengkung emas per sisi)
    path = Hh.catmull([(s * 0.108, -0.030, 1.860), (s * 0.124, -0.026, 1.900), (s * 0.122, -0.018, 1.935), (s * 0.104, -0.010, 1.958)], 6)
    Hh.tube(bm, path, lambda t: 0.024 * (1 - t) ** 0.8 + 0.0006, n=6, squash=(1.0, 0.60), up=(0, -1, 0))
    made.append(P(f"JD_Head_Horn_{L}", bm, "gold", "Armor"))

    # ============================================================ PELAT EMAS SAMPING: bilah besar di sisi helm, menyapu ke belakang-atas
    #   (tampak samping konsep: sisi helm didominasi emas dari pangkal tanduk ke belakang)
    bm = bmesh.new()
    side = [(s * 0.124, -0.066, 1.815), (s * 0.130, -0.030, 1.880), (s * 0.128, 0.040, 1.915), (s * 0.122, 0.105, 1.905),
            (s * 0.130, 0.040, 1.850), (s * 0.130, -0.010, 1.810)]
    Hh.plate3d(bm, side)
    bm = Hh.harden(bm, thick=0.012, bevel=0.0025, segs=1)
    made.append(P(f"JD_Head_SidePlate_{L}", bm, "gold", "Armor"))

    # ============================================================ PECAHAN SIRIP MERAH runcing di samping (antara tanduk & helm)
    bm = bmesh.new()
    for pts, r0 in (([(s * 0.100, 0.000, 1.870), (s * 0.118, 0.030, 1.915), (s * 0.130, 0.070, 1.955)], 0.040),   # sirip = bilah lebar, bukan kumis
                    ([(s * 0.112, 0.060, 1.840), (s * 0.130, 0.105, 1.870), (s * 0.140, 0.155, 1.895)], 0.036),
                    ([(s * 0.100, 0.110, 1.780), (s * 0.118, 0.160, 1.780), (s * 0.128, 0.205, 1.770)], 0.030)):
        Hh.tube(bm, Hh.catmull(pts, 4), lambda t, r0=r0: r0 * (1 - t) ** 0.9 + 0.0006, n=4, squash=(1.0, 0.28), up=(0, 0, 1))   # bidang lebar menghadap samping
    made.append(P(f"JD_Head_Fin_{L}", bm, "red", "Armor"))

    # ============================================================ MATA lebar bersudut, sudut luar naik (emissive konstan)
    eye2d = [(0.016, 1.769), (0.050, 1.778), (0.090, 1.800), (0.100, 1.819), (0.062, 1.809), (0.020, 1.793)]   # sedikit lebih tinggi; rasio tetap >= 3:1 (K6)
    lenx = 0.100 - 0.016
    pts = [(s * x, -0.142 + (x - 0.016) / lenx * 0.034, z) for x, z in eye2d]      # di DEPAN faceplate & di bawah bingkai emas
    bm = bmesh.new()
    Hh.plate3d(bm, pts)
    bm = Hh.harden(bm, thick=0.008, bevel=0.0, segs=1)
    made.append(P(f"JD_Head_Eye_{L}", bm, "eye", "Face"))

# ================================================================ ORNAMEN DAHI emas besar (teratai/api) + latar merah + ukiran
ORN = [(0.0, -0.006), (0.030, 0.018), (0.054, 0.052), (0.060, 0.088), (0.048, 0.122), (0.024, 0.150), (0.0, 0.176)]   # plakat runcing (daun/api)
ORN = ORN + [(-x, z) for x, z in reversed(ORN[1:-1])]


def front_y(z, x=0.0):
    """Permukaan depan helm kira-kira (dahi miring ke belakang saat naik)."""
    return -0.126 + 0.55 * max(0.0, z - 1.80) + 0.10 * x * x / 0.01


def scaled(poly, k, cz=0.085):
    return [(x * k, cz + (z - cz) * k) for x, z in poly]


def petal(cx, z0, h, w, tilt):
    """Kelopak (tetesan) di bidang dahi: pangkal (cx, z0), tinggi h, lebar w, miring tilt (rad)."""
    pts = []
    for i in range(13):
        a = math.pi * i / 12
        pts.append((math.sin(a) * w * (1 - 0.15 * math.cos(a)), (1 - math.cos(a)) / 2 * h))
    pts = pts + [(-x, z) for x, z in reversed(pts[1:-1])]
    return [(cx + x * math.cos(tilt) + z * math.sin(tilt), z0 - x * math.sin(tilt) + z * math.cos(tilt)) for x, z in pts]


Z0 = 1.788
bm = bmesh.new()                                                       # plakat emas
Hh.plate3d(bm, [(x, front_y(Z0 + z, x) - 0.022, Z0 + z) for x, z in ORN])   # maju agar tidak tenggelam di helm
bm = Hh.harden(bm, thick=0.014, bevel=0.003, segs=2)
rim = [Vector((x, front_y(Z0 + z, x) - 0.032, Z0 + z)) for x, z in scaled(ORN, 0.84)]
Hh.closed_tube(bm, rim, 0.0036, n=5, up=(0, -1, 0))                     # bingkai timbul di dalam tepi
for (cx, z0, h, w, tilt) in ((0.0, 0.026, 0.100, 0.024, 0.0),          # teratai emas PADAT, besar (emas dominan seperti konsep)
                             (0.024, 0.030, 0.066, 0.016, -0.80),
                             (-0.024, 0.030, 0.066, 0.016, 0.80),
                             (0.0, 0.128, 0.028, 0.010, 0.0)):
    pb = bmesh.new()
    Hh.plate3d(pb, [(x, front_y(Z0 + z, x) - 0.036, Z0 + z) for x, z in petal(cx, z0, h, w, tilt)])
    merge(bm, Hh.harden(pb, thick=0.007, bevel=0.0015, segs=1))
made.append(P("JD_Head_Forehead", bm, "gold", "Armor"))

bm = bmesh.new()                                                       # latar merah di dalam bingkai (celah ukiran)
Hh.plate3d(bm, [(x, front_y(Z0 + z, x) - 0.0305, Z0 + z) for x, z in scaled(ORN, 0.62)])
bm = Hh.harden(bm, thick=0.003, bevel=0.0, segs=1)
made.append(P("JD_Head_ForeheadInset", bm, "red", "Armor"))

# ================================================================ PELINDUNG LEHER belakang + kerah hitam
bm = bmesh.new()
Hh.plate3d(bm, [(-0.090, 0.130, 1.725), (0.090, 0.130, 1.725), (0.070, 0.158, 1.630), (-0.070, 0.158, 1.630)])
bm = Hh.harden(bm, thick=0.012, bevel=0.003, segs=2)
made.append(P("JD_Head_NeckGuard", bm, "red", "Armor"))
bm = bmesh.new()
Hh.tube(bm, [(0, 0, 1.600), (0, 0, 1.625), (0, 0, 1.655)], [0.068, 0.070, 0.082], n=14, caps=(True, True))
made.append(P("JD_Head_Collar", bm, "black", "Body", bone="neck_02"))

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
print("KEPALA tris:", sum(C.tri_count(ob, dg) for ob in made), "| objek:", len(made))
