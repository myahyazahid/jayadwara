"""Iterasi 2 (revisi mengikuti konsep) — KAKI. Mengganti JD_Leg_*.

Konsep: paha hitam berotot dengan pelat merah besar di depan-luar (bertepi emas); lutut = berlian emas BESAR
berinset merah; greave merah melebar di bawah lutut (±0,20 m) lalu meramping ke pergelangan (±0,09 m), sisi dalam
hitam terlihat, pita emas di atas dan berlian kecil di tulang kering; pita emas di pergelangan; sepatu merah runcing
dengan ujung emas dan sol hitam. Ukuran target diukur dari reference plane (lihat docs/13, revisi).
"""
import importlib
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jd_common as C
import jd_hero as Hh
import jd_skeleton as SK
importlib.reload(C)
importlib.reload(Hh)
importlib.reload(SK)

S = SK.SIDES
seg = SK.bone_segments()
rad = math.radians
UP, FR, SIDE = Vector((0, 0, 1)), Vector((0, -1, 0)), Vector((1, 0, 0))


def P(name, bm, zone, slot, **kw):
    return C.finish_part(name, bm, "07_Leg", zone, slot, smooth="angle", **kw)


def merge(dst, src):
    tmp = bpy.data.meshes.new("_mg")
    src.to_mesh(tmp)
    src.free()
    dst.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)


for ob in list(bpy.data.objects):
    if ob.type == "MESH" and ob.name.startswith("JD_Leg_"):
        bpy.data.objects.remove(ob, do_unlink=True)
made = []

for sd, s in S.items():
    L = sd.upper()
    hip, knee = seg[f"thigh_{sd}"]
    _, ankle = seg[f"calf_{sd}"]
    ball = seg[f"ball_{sd}"][0]
    TW = {f"thigh_{sd}": 0.7, f"thigh_twist_01_{sd}": 0.3}
    CW = {f"calf_{sd}": 0.7, f"calf_twist_01_{sd}": 0.3}

    # ---- pelat paha merah besar (depan-luar) + tepi emas pipih
    a0, a1 = hip + (knee - hip) * 0.20, hip + (knee - hip) * 0.84     # tepi atas turun: sabuk kini di pinggul
    cd = Vector((s * 0.45, -0.89, 0))
    rth = lambda t: 0.106 - 0.022 * t + 0.008 * math.sin(math.pi * t)       # paha: tebal di tengah, meramping ke lutut
    fn = Hh.axis_patch_fn(a0, a1, rth, None, cd, rad(165))
    bm = bmesh.new()
    Hh.grid_surface(bm, fn, 10, 7)
    bm = Hh.harden(bm, thick=0.014, bevel=0.004, segs=2)
    made.append(P(f"JD_Leg_ThighGuard_{L}", bm, "red", "Armor", weights=TW))
    fo = Hh.axis_patch_fn(a0, a1, rth, None, cd, rad(165), off=0.009)
    bm = bmesh.new()
    for uv in ([(0, 0), (0, 1)], [(1, 0), (1, 1)], [(0, 1), (0.5, 0.93), (1, 1)], [(0, 0), (0.5, 0.05), (1, 0)]):
        rb = bmesh.new()
        Hh.ribbon_on_surface(rb, fo, uv, 0.016, spp=8)
        merge(bm, Hh.harden(rb, thick=0.006, bevel=0.0015, segs=1))
    made.append(P(f"JD_Leg_ThighTrim_{L}", bm, "gold", "Armor", weights=TW))

    # ---- lutut: berlian emas BESAR + bingkai + inset merah
    kc = Vector((knee.x, -0.094, 0.585))
    bm = bmesh.new()
    Hh.hull(bm, [kc + UP * 0.112, kc - UP * 0.112, kc + SIDE * 0.072, kc - SIDE * 0.072, kc + FR * 0.046, kc - FR * 0.018])
    bm = Hh.harden(bm, thick=0.0, bevel=0.004, segs=2)
    outline = [kc + UP * 0.118 + FR * 0.006, kc + SIDE * 0.077 + FR * 0.006, kc - UP * 0.118 + FR * 0.006, kc - SIDE * 0.077 + FR * 0.006]
    Hh.closed_tube(bm, outline, 0.010, n=6)
    made.append(P(f"JD_Leg_KneeGuard_{L}", bm, "gold", "Armor", bone=f"calf_{sd}"))
    bm = bmesh.new()
    ki = kc + FR * 0.024
    Hh.hull(bm, [ki + UP * 0.070, ki - UP * 0.070, ki + SIDE * 0.044, ki - SIDE * 0.044, ki + FR * 0.026, ki - FR * 0.006])
    bm = Hh.harden(bm, thick=0.0, bevel=0.002, segs=1)
    made.append(P(f"JD_Leg_KneeInset_{L}", bm, "red", "Armor", bone=f"calf_{sd}"))

    # ---- greave: melebar di bawah lutut lalu meramping (profil r(t)), sisi dalam terbuka (hitam terlihat)
    g0, g1 = knee + (ankle - knee) * 0.10, ankle + Vector((0, 0, 0.045))
    cd2 = Vector((s * 0.30, -1, 0))
    rgv = lambda t: 0.050 + 0.042 * (1 - t) ** 1.4 + 0.006 * math.sin(math.pi * min(t * 1.6, 1.0))   # konsep: ±0,18 m di bawah lutut, ±0,10 m di pergelangan
    fn2 = Hh.axis_patch_fn(g0, g1, rgv, None, cd2, rad(330), squash=(1.15, 1.0))
    bm = bmesh.new()
    Hh.grid_surface(bm, fn2, 14, 9)
    bm = Hh.harden(bm, thick=0.014, bevel=0.004, segs=2)
    made.append(P(f"JD_Leg_Greave_{L}", bm, "red", "Armor", weights=CW))
    fo2 = Hh.axis_patch_fn(g0, g1, rgv, None, cd2, rad(330), squash=(1.15, 1.0), off=0.010)
    bm = bmesh.new()
    for uv, w in (([(0.0, 0.03), (0.25, 0.10), (0.5, 0.22), (0.75, 0.10), (1.0, 0.03)], 0.020),     # V emas di bawah lutut
                  ([(0.0, 0.0), (0.5, 0.0), (1.0, 0.0)], 0.014),
                  ([(0.22, 0.30), (0.22, 0.97)], 0.011), ([(0.78, 0.30), (0.78, 0.97)], 0.011)):
        rb = bmesh.new()
        Hh.ribbon_on_surface(rb, fo2, uv, w, spp=8)
        merge(bm, Hh.harden(rb, thick=0.006, bevel=0.0015, segs=1))
    sc = Vector(fo2(0.5, 0.55))                                                                  # berlian kecil di tulang kering
    sb = bmesh.new()
    Hh.hull(sb, [sc + UP * 0.055, sc - UP * 0.055, sc + SIDE * 0.030, sc - SIDE * 0.030, sc + FR * 0.016, sc - FR * 0.010])
    merge(bm, Hh.harden(sb, thick=0.0, bevel=0.0015, segs=1))
    made.append(P(f"JD_Leg_GreaveTrim_{L}", bm, "gold", "Armor", weights=CW))

    # ---- SEPATU (revisi atas feedback: "sepatu belum mirip, improve biar bagus")
    # Konsep: sepatu merah ramping berujung runcing yang sedikit naik, poros pergelangan menyatu ke greave,
    # manset emas berbentuk V dengan berlian di depan, toe cap emas, strip emas di sisi, sol hitam tebal.
    yaw = math.atan2(abs(ball.x) - abs(ankle.x), -(ball.y - ankle.y)) * s
    rz = Matrix.Rotation(yaw, 3, "Z")
    A = Vector((ankle.x, 0.0, 0.0))

    def W(p):
        return A + rz @ Vector(p)

    def loft(bm_, path, rx, rzs, n=14):
        """Loft penampang elips sepanjang path (rx = setengah lebar, rzs = setengah tinggi). rx≈0 -> ujung runcing."""
        P_ = [Vector(q) for q in path]
        rings = []
        for k_, q in enumerate(P_):
            T = (P_[min(k_ + 1, len(P_) - 1)] - P_[max(k_ - 1, 0)]).normalized()
            Lv = T.cross(Vector((0, 0, 1))).normalized()
            Vv = Lv.cross(T).normalized()
            if rx[k_] < 1e-3:
                rings.append([bm_.verts.new(q)])
                continue
            rings.append([bm_.verts.new(q + Lv * (rx[k_] * math.cos(2 * math.pi * m / n)) + Vv * (rzs[k_] * math.sin(2 * math.pi * m / n)))
                          for m in range(n)])
        for a_, b_ in zip(rings[:-1], rings[1:]):
            if len(b_) == 1:
                for m in range(n):
                    bm_.faces.new((a_[m], a_[(m + 1) % n], b_[0]))
            else:
                for m in range(n):
                    bm_.faces.new((a_[m], a_[(m + 1) % n], b_[(m + 1) % n], b_[m]))
        if len(rings[0]) > 2:
            bm_.faces.new(rings[0][::-1])
        bmesh.ops.recalc_face_normals(bm_, faces=list(bm_.faces))

    # jalur kaki: tumit -> lengkung -> bola kaki -> jari -> ujung runcing (sedikit naik); (x lokal, y, z)
    FP = [(0, 0.088, 0.087), (0, 0.040, 0.094), (0, -0.040, 0.094), (0, -0.130, 0.082), (0, -0.215, 0.068),
          (0, -0.285, 0.056), (0, -0.330, 0.056), (0, -0.356, 0.066)]
    RX = [0.054, 0.062, 0.066, 0.066, 0.056, 0.038, 0.016, 0.0]          # lebih ramping & runcing (konsep)
    RZ = [0.064, 0.072, 0.072, 0.060, 0.046, 0.032, 0.018, 0.0]          # punggung kaki lebih tinggi (bukan sandal pipih)
    bm = bmesh.new()
    loft(bm, [W(q) for q in FP], RX, RZ)
    Hh.tube(bm, [W((0, 0.020, 0.085)), W((0, 0.010, 0.150)), W((0, 0.004, 0.215))], [0.058, 0.060, 0.064], n=14,
            squash=(1.0, 1.12), caps=(False, True), up=(0, -1, 0))            # poros pergelangan menyatu ke greave
    bm = Hh.harden(bm, thick=0.0, bevel=0.0, segs=1)
    boot_bvh = BVHTree.FromBMesh(bm)                                   # untuk menempelkan ornamen ke permukaan sepatu
    made.append(P(f"JD_Leg_Boot_{L}", bm, "red", "Armor", bone=f"foot_{sd}"))

    bm = bmesh.new()                                                   # toe cap emas (ujung depan, sedikit lebih besar)
    loft(bm, [W(q) for q in FP[5:]], [r + 0.005 for r in RX[5:-1]] + [0.0], [r + 0.005 for r in RZ[5:-1]] + [0.0])   # hanya ujung (konsep)
    made.append(P(f"JD_Leg_BootToe_{L}", bm, "gold", "Armor", bone=f"foot_{sd}"))

    bm = bmesh.new()                                                   # manset emas: PITA lebar berbentuk V (bukan kawat) + strip sisi
    cuff, cn = [], []
    for k_ in range(33):
        a = 2 * math.pi * k_ / 32
        front = max(0.0, -math.sin(a)) ** 2                           # -Y = depan -> titik V terendah di depan
        q = W((0.066 * math.cos(a), 0.004 + 0.076 * math.sin(a), 0.200 - 0.052 * front))
        cuff.append(q)
        cn.append((rz @ Vector((math.cos(a), math.sin(a), 0.0))).normalized())
    Hh.ribbon(bm, cuff, cn, 0.026)
    bm = Hh.harden(bm, thick=0.008, bevel=0.0018, segs=1)
    for sx in (-1, 1):
        side = [W((sx * (RX[k_] + 0.004), FP[k_][1], FP[k_][2] - 0.006)) for k_ in range(1, 6)]
        Hh.tube(bm, Hh.catmull(side, 4), 0.0065, n=5)
    made.append(P(f"JD_Leg_Ankle_{L}", bm, "gold", "Armor", bone=f"foot_{sd}"))

    bm = bmesh.new()                                                   # pelat berlian merah berbingkai emas di punggung kaki (konsep)
    fwd = (rz @ Vector((0, -1, 0))).normalized()
    lat = (rz @ Vector((1, 0, 0))).normalized()
    c0 = W((0.0, -0.172, 0.20))

    def snap(q, lift):
        """Proyeksikan titik ke permukaan sepatu (dari atas) lalu angkat sepanjang normal permukaan."""
        hit, nrm, _i, _d = boot_bvh.ray_cast(q + Vector((0, 0, 0.2)), Vector((0, 0, -1)))
        if hit is None:
            hit, nrm, _i, _d = boot_bvh.find_nearest(q)
        return hit + nrm * lift, nrm

    corners = [c0 + fwd * 0.060, c0 + lat * 0.034, c0 - fwd * 0.046, c0 - lat * 0.034]
    ring = []
    for k_ in range(4):                                                # sisi berlian dipecah supaya mengikuti lengkung punggung kaki
        p0, p1 = corners[k_], corners[(k_ + 1) % 4]
        for m in range(4):
            ring.append(snap(p0.lerp(p1, m / 4), 0.004)[0])
    Hh.closed_tube(bm, ring, 0.0065, n=5)
    made.append(P(f"JD_Leg_FootFrame_{L}", bm, "gold", "Armor", bone=f"foot_{sd}"))
    bm = bmesh.new()
    inner = []
    for k_ in range(4):
        p0, p1 = c0.lerp(corners[k_], 0.80), c0.lerp(corners[(k_ + 1) % 4], 0.80)
        for m in range(3):
            inner.append(snap(p0.lerp(p1, m / 3), 0.003)[0])
    Hh.hull(bm, inner + [snap(c0, 0.014)[0]] + [snap(q, -0.004)[0] for q in inner[::3]])
    bm = Hh.harden(bm, thick=0.0, bevel=0.0015, segs=1)
    made.append(P(f"JD_Leg_FootGem_{L}", bm, "red", "Armor", bone=f"foot_{sd}"))

    d2 = bmesh.new()                                                   # berlian emas di titik V manset + berlian kecil di punggung kaki
    for c_, hh, ww in ((W((0, -0.086, 0.150)), 0.058, 0.040),):
        Hh.hull(d2, [c_ + UP * hh / 2, c_ - UP * hh / 2, c_ + SIDE * ww / 2, c_ - SIDE * ww / 2, c_ + FR * 0.018, c_ - FR * 0.008])
    d2 = Hh.harden(d2, thick=0.0, bevel=0.0018, segs=1)
    made.append(P(f"JD_Leg_AnkleGem_{L}", d2, "gold", "Armor", bone=f"foot_{sd}"))

    bm = bmesh.new()                                                   # sol hitam tebal mengikuti bentuk kaki
    outline = []
    for k_ in range(len(FP)):
        outline.append((RX[k_] + 0.002, FP[k_][1]))
    pts = [W((x, y, z)) for x, y in outline for z in (0.0, 0.034)] + [W((-x, y, z)) for x, y in outline for z in (0.0, 0.034)]   # sol tebal: dasar sepatu duduk di dalamnya
    pts += [W((0, FP[-1][1] + 0.004, 0.0)), W((0, FP[-1][1] + 0.004, 0.034))]
    Hh.hull(bm, pts)
    bm = Hh.harden(bm, thick=0.0, bevel=0.005, segs=2)
    made.append(P(f"JD_Leg_Sole_{L}", bm, "black", "Body", bone=f"foot_{sd}"))

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
tot = sum(C.tri_count(ob, dg) for ob in made)
print("KAKI tris:", tot, "| objek:", len(made))
