"""Iterasi 2 (revisi mengikuti konsep) — TORSO + BAHU. Mengganti JD_Torso_* dan JD_Shoulder_*.

Konsep: cuirass merah besar menutup dada sampai perut; ornamen emas DOMINAN di dada (pelat sayap emas di dada atas,
pita chevron V pipih, gulungan merah di atas emas); permata berlian dengan bingkai sinar surya (statis, K1/K6);
pelat perut merah bertingkat (chevron) dengan hitam di sela & sisi rusuk; punggung merah penuh dengan rusuk tengah;
pauldron emas berlapis bersudut dengan bilah runcing menyapu ke atas (bukan bulat).
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

S = {"l": +1, "r": -1}
CHEST_W = {"spine_04": 0.5, "spine_05": 0.5}
ABS_W = {"spine_02": 0.5, "spine_03": 0.5}


def P(name, bm, coll, zone, slot, **kw):
    return C.finish_part(name, bm, coll, zone, slot, smooth="angle", **kw)


for ob in list(bpy.data.objects):
    if ob.type == "MESH" and ob.name.startswith(("JD_Torso_", "JD_Shoulder_")):
        bpy.data.objects.remove(ob, do_unlink=True)
made = []

# ================================================================ CUIRASS (dada)
Z_TOP, DROP_SIDE, DROP_TIP, HALF_W = 1.565, 0.18, 0.10, 0.215


def chest(u, v):
    k = (u - 0.5) * 2
    ak = abs(k)
    z = Z_TOP + 0.012 * ak - v * (DROP_SIDE + DROP_TIP * (1 - ak) ** 1.2)
    W = HALF_W * (1 - 0.28 * v * v)
    pec = 0.018 * math.exp(-((ak - 0.45) / 0.28) ** 2) * (1 - v)          # tonjolan otot dada
    y = -(0.165 + pec) * (1 - ak ** 2.4) ** 0.75 * (1 - 0.22 * v) - 0.010 * (1 - ak) ** 2
    return Vector((k * W, y, z))


OUT = -1.0      # normal du×dv permukaan dada menghadap ke dalam -> offset ke luar = negatif
SKIN = 0.008    # setengah tebal cangkang (solidify 0,016 di tengah) -> ornamen diukur dari permukaan LUAR

bm = bmesh.new()
Hh.grid_surface(bm, chest, 18, 10)
bm = Hh.harden(bm, thick=0.016, bevel=0.004, segs=2)
made.append(P("JD_Torso_Chest", bm, "03_Torso", "red", "Armor", weights=CHEST_W))

# pelat sayap emas di dada atas (kiri/kanan) + pita chevron pipih + garis leher
bm = bmesh.new()
for sgn in (+1, -1):
    def wq(u, v, sgn=sgn):
        uu = u if sgn > 0 else 1 - u
        g = Hh.quad_region_fn(chest, (0.50 + sgn * 0.06, 0.06), (0.50 + sgn * 0.47, 0.03),
                              (0.50 + sgn * 0.40, 0.30), (0.50 + sgn * 0.08, 0.36))
        return g(uu, v)
    Hh.grid_surface(bm, Hh.offset_fn(wq, OUT * (SKIN + 0.007)), 7, 4)   # orientasi u sama dengan dada di kedua sisi (sudut sudah dicerminkan + u dibalik)
bm = Hh.harden(bm, thick=0.008, bevel=0.0025, segs=2)
for pts, w in (([(0.03, 0.05), (0.20, 0.33), (0.5, 0.62), (0.80, 0.33), (0.97, 0.05)], 0.034),
               ([(0.16, 0.42), (0.33, 0.62), (0.5, 0.80), (0.67, 0.62), (0.84, 0.42)], 0.020),
               ([(0.04, 0.012), (0.30, 0.010), (0.5, 0.045), (0.70, 0.010), (0.96, 0.012)], 0.020)):
    rb = bmesh.new()
    Hh.ribbon_on_surface(rb, chest, pts, w, offset=OUT * (SKIN + 0.004), spp=8)
    rb = Hh.harden(rb, thick=0.007, bevel=0.002, segs=1)
    tmp = bpy.data.meshes.new("_rb")
    rb.to_mesh(tmp)
    rb.free()
    bm.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)
made.append(P("JD_Torso_Chevron", bm, "03_Torso", "gold", "Armor", weights=CHEST_W))

# gulungan merah di atas pelat emas (ukiran "awan")
bm = bmesh.new()
for sgn in (+1, -1):
    for cu, cv, r0 in ((0.5 + sgn * 0.27, 0.15, 0.055), (0.5 + sgn * 0.17, 0.24, 0.035)):
        spiral = []
        for i in range(18):
            t = i / 17
            a = sgn * 2 * math.pi * 1.4 * t + (math.pi if sgn > 0 else 0)
            r = r0 * (1 - t) + 0.008
            spiral.append((cu + r * math.cos(a) / 0.43, cv + r * math.sin(a) / 0.28))
        Hh.tube(bm, Hh.curve_on_surface(chest, spiral, offset=OUT * (SKIN + 0.018), spp=2), lambda t: 0.0055 * (1 - 0.5 * t), n=5)
made.append(P("JD_Torso_Scroll", bm, "03_Torso", "red", "Armor", weights=CHEST_W))

# permata (statis) + bingkai berlian + sinar surya pipih
GZ = 1.480
gv = (Z_TOP - GZ) / (DROP_SIDE + DROP_TIP)
gem_c = Vector(chest(0.5, gv)) + Vector((0, -0.020, 0))
bm = bmesh.new()
Hh.diamond(bm, gem_c, 0.058, 0.108, 0.022, 0.010)
bm = Hh.harden(bm, thick=0.0, bevel=0.0015, segs=1)
made.append(P("JD_Torso_Gem", bm, "03_Torso", "gem", "Face", weights=CHEST_W))

bm = bmesh.new()
rim = [gem_c + Vector((0, -0.004, 0.064)), gem_c + Vector((0.036, -0.004, 0)), gem_c + Vector((0, -0.004, -0.064)),
       gem_c + Vector((-0.036, -0.004, 0))]
Hh.closed_tube(bm, rim, 0.0085, n=6)
for i in range(8):                                                     # sinar surya: segitiga pipih di sekeliling bingkai
    a = math.radians(i * 45 + 22.5)
    dr = Vector((math.cos(a) * 0.8, 0, math.sin(a)))
    sd_ = Vector((-math.sin(a), 0, math.cos(a)))
    base_c = gem_c + dr * 0.060
    tip = gem_c + dr * (0.098 if i % 2 == 0 else 0.084)
    pts = [base_c + sd_ * 0.013, base_c - sd_ * 0.013, tip]
    pts = [Vector((p.x, chest(min(max(0.5 + p.x / (2 * HALF_W), 0), 1), min(max((Z_TOP - p.z) / (DROP_SIDE + DROP_TIP), 0), 1)).y - 0.018, p.z))
           for p in pts]
    Hh.hull(bm, pts + [p + Vector((0, 0.006, 0)) for p in pts])
made.append(P("JD_Torso_GemFrame", bm, "03_Torso", "gold", "Armor", weights=CHEST_W))

# ================================================================ PELAT PERUT (revisi atas feedback: "perut masih kurang")
# Konsep: SATU pelat merah berbentuk V menyambung dari bawah ujung V dada sampai masuk ke sabuk, bertingkat
# (dua chevron emas tipis), sisi pinggang (oblique) hitam tetap terlihat.
AB_HW, AB_BOT = 0.150, 1.100        # revisi: sampai ke sabuk di pinggang


def abd(u, v):
    k = (u - 0.5) * 2
    ak = abs(k)
    z_top = 1.300 + 0.075 * ak ** 1.25                   # tepi atas V, masuk ±1,5 cm di bawah ujung V dada
    z = z_top + (AB_BOT - z_top) * v
    hw = AB_HW * (1 - 0.25 * v)                          # meramping ke pinggang
    x = k * hw
    y = (-(0.150 + 0.010 * (1 - k * k)) * (1 - ak ** 2.6) ** 0.55 - 0.004 * (1 - ak) ** 2) * (1 - 0.30 * v ** 1.5)   # masuk di balik sabuk
    return Vector((x, y, z))


bm = bmesh.new()
Hh.grid_surface(bm, abd, 14, 7)
bm = Hh.harden(bm, thick=0.016, bevel=0.004, segs=2)
made.append(P("JD_Torso_Abs", bm, "03_Torso", "red", "Armor", weights=ABS_W))
bm = bmesh.new()                                                       # chevron emas bertingkat + tepi samping emas
for uv, w in (([(0.06, 0.30), (0.30, 0.42), (0.5, 0.55), (0.70, 0.42), (0.94, 0.30)], 0.012),
              ([(0.12, 0.66), (0.32, 0.76), (0.5, 0.86), (0.68, 0.76), (0.88, 0.66)], 0.011)):   # tanpa pita tepi samping (terbaca seperti tali silang)
    rb = bmesh.new()
    Hh.ribbon_on_surface(rb, abd, uv, w, offset=OUT * (SKIN + 0.004), spp=8)
    rb = Hh.harden(rb, thick=0.006, bevel=0.0015, segs=1)
    tmp = bpy.data.meshes.new("_rb")
    rb.to_mesh(tmp)
    rb.free()
    bm.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)
made.append(P("JD_Torso_AbsTrim", bm, "03_Torso", "gold", "Armor", weights=ABS_W))

# ================================================================ PUNGGUNG merah penuh + rusuk tengah + pita emas
def back(u, v):
    k = (u - 0.5) * 2
    ak = abs(k)
    z = 1.565 - v * (0.32 + 0.04 * (1 - ak))
    W = 0.200 * (1 - 0.32 * v * v)
    ridge = 0.016 * (1 - ak) ** 3
    y = 0.060 + (0.098 + ridge) * (1 - ak ** 2.4) ** 0.8 * (1 - 0.18 * v)
    return Vector((k * W, y, z))


bm = bmesh.new()
Hh.grid_surface(bm, back, 16, 10)
bm = Hh.harden(bm, thick=0.016, bevel=0.004, segs=2)
made.append(P("JD_Torso_Back", bm, "03_Torso", "red", "Armor", weights=CHEST_W))
bm = bmesh.new()
for pts, w in (([(0.04, 0.10), (0.25, 0.06), (0.5, 0.20), (0.75, 0.06), (0.96, 0.10)], 0.022),
               ([(0.10, 0.30), (0.30, 0.42), (0.5, 0.62), (0.70, 0.42), (0.90, 0.30)], 0.018)):
    rb = bmesh.new()
    Hh.ribbon_on_surface(rb, back, pts, w, offset=0.012, spp=8)
    rb = Hh.harden(rb, thick=0.007, bevel=0.002, segs=1)
    tmp = bpy.data.meshes.new("_rb")
    rb.to_mesh(tmp)
    rb.free()
    bm.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)
made.append(P("JD_Torso_BackTrim", bm, "03_Torso", "gold", "Armor", weights=CHEST_W))

# ================================================================ KERAH HITAM (revisi: bukaan atas cuirass tampak berongga)
# Konsep: leher tinggi hitam naik dari bibir cuirass ke bawah helm. Corong dari dalam bibir (r ≈ 0,17–0,20) ke JD_Head_Collar.
COLLAR = [(1.540, 0.198, 0.162), (1.562, 0.168, 0.145), (1.582, 0.124, 0.114), (1.602, 0.090, 0.086), (1.622, 0.077, 0.076)]
bm = bmesh.new()
rings = []
for z, rx, ry in COLLAR:
    rings.append([bm.verts.new((rx * math.cos(2 * math.pi * m / 24), ry * math.sin(2 * math.pi * m / 24), z)) for m in range(24)])
for a_, b_ in zip(rings[:-1], rings[1:]):
    for m in range(24):
        bm.faces.new((a_[m], a_[(m + 1) % 24], b_[(m + 1) % 24], b_[m]))
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm = Hh.harden(bm, thick=0.004, bevel=0.0, segs=1)
made.append(P("JD_Torso_Collar", bm, "03_Torso", "black", "Body", weights={"spine_05": 0.6, "neck_01": 0.4}))

# ================================================================ PAULDRON (revisi atas feedback: "pauldron kurang mirip")
# Konsep: bukan tumpukan cakram datar, tapi LAME (pelat lengkung bertumpuk) yang menggantung menutupi bahu & lengan atas
# seperti sode: tutup emas di puncak bahu, dua lame emas melebar ke bawah, pita merah tipis di bawah tiap lame,
# ornamen gulungan merah, dua bilah tinggi menyapu ke atas + satu bilah kecil ke luar.
seg_ = SK.bone_segments()
for sd, s in S.items():
    L = sd.upper()
    capw = {f"clavicle_{sd}": 0.35, f"upperarm_{sd}": 0.65}             # revisi: lebih ikut lengan (deltoid berisi menempel di bawahnya)
    lamew = {f"upperarm_{sd}": 0.75, f"clavicle_{sd}": 0.25}
    sh, el = seg_[f"upperarm_{sd}"]
    d = (el - sh).normalized()
    outward = Vector((s * math.cos(SK.ARM_ANGLE), 0, math.sin(SK.ARM_ANGLE)))
    C0 = Vector((s * 0.236, 0.0, 1.598))                              # revisi: diturunkan (tadi menonjol seperti punuk)
    tilt = Matrix.Rotation(s * math.radians(36), 3, "Y")

    bm = bmesh.new()                                                   # tutup emas di puncak bahu
    Hh.ellipsoid_patch(bm, C0, (0.114, 0.106, 0.074), 0.06, 1.42, nu=16, nv=6, rot=tilt, wrap=True)   # tutup besar, lebih pipih
    bm = Hh.harden(bm, thick=0.012, bevel=0.003, segs=2)
    cap_obj = P(f"JD_Shoulder_Pauldron_{L}", bm, "04_Shoulder", "gold", "Armor", weights=capw)
    made.append(cap_obj)

    cdir = (outward + Vector((0, 0, 0.35)))
    cdir = (cdir - cdir.project(d)).normalized()
    bdir = d.cross(cdir).normalized()

    def lame(t0, t1, r0, flare, span, off=0.0, point=0.07):
        """Lame cembung yang melebar ke bawah; tepi bawah MERUNCING di tengah sisi luar (konsep)."""
        def fn(u, v):
            k = (u - 0.5) * 2
            t = t0 + (t1 - t0 + point * (1 - abs(k)) ** 1.5) * v
            r = r0 + flare * v ** 1.3 + 0.010 * math.sin(math.pi * v) + off
            ang = k * math.radians(span) / 2
            return sh + (el - sh) * t + cdir * (r * math.cos(ang)) + bdir * (r * math.sin(ang))
        return fn

    bm = bmesh.new()                                                   # dua lame emas bertumpuk menggantung ke bawah
    rb = bmesh.new()
    for t0, t1, r0 in ((0.035, 0.275, 0.100), (0.195, 0.355, 0.097)):   # digeser turun mengikuti cap yang lebih rendah      # lame bawah dipendekkan (tidak bentrok sirip siku saat siku ditekuk)
        g = bmesh.new()
        Hh.grid_surface(g, lame(t0, t1, r0, 0.034, 215), 14, 4)
        g = Hh.harden(g, thick=0.012, bevel=0.003, segs=2)
        tmp = bpy.data.meshes.new("_lm"); g.to_mesh(tmp); g.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
        r_ = bmesh.new()                                               # pita merah tipis terlihat di bawah tepi lame
        Hh.grid_surface(r_, lame(t1 - 0.04, t1 + 0.055, r0 + 0.008, 0.016, 205, point=0.10), 14, 2)   # di dalam lame (tanpa z-fighting), menyembul di bawahnya
        r_ = Hh.harden(r_, thick=0.008, bevel=0.002, segs=1)
        tmp = bpy.data.meshes.new("_lm"); r_.to_mesh(tmp); r_.free(); rb.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    made.append(P(f"JD_Shoulder_Lame_{L}", bm, "04_Shoulder", "gold", "Armor", weights=lamew))
    made.append(P(f"JD_Shoulder_Under_{L}", rb, "04_Shoulder", "red", "Armor", weights=lamew))

    bm = bmesh.new()                                                   # emblem berlian merah di sisi luar CAP (konsep: ornamen di tutup bahu)
    cap_tree = BVHTree.FromPolygons([v.co.copy() for v in cap_obj.data.vertices], [tuple(p_.vertices) for p_ in cap_obj.data.polygons])
    ray_d = Vector((s * 0.80, -0.25, 0.22)).normalized()                # sisi luar-atas cap (arah bawah mengenai bukaan cap)
    hit, nrm, _i, _dd = cap_tree.ray_cast(C0 + ray_d * 0.5, -ray_d, 1.0)
    nrm = nrm if nrm.dot(ray_d) > 0 else -nrm
    t1_ = nrm.cross(Vector((0, 1, 0))).normalized()
    t2_ = nrm.cross(t1_).normalized()
    c_ = hit - nrm * 0.010                                             # sedikit masuk; plate3d+harden menonjol ±6 mm di luar cap
    up_, sd_ = (t1_, t2_) if abs(t1_.z) > abs(t2_.z) else (t2_, t1_)   # berlian vertikal (bukan lingkaran+titik: terbaca seperti mata)
    up_ = up_ if up_.z > 0 else -up_
    dia = [up_ * 0.040, sd_ * 0.022, -up_ * 0.034, -sd_ * 0.022]
    ring = []
    for k_ in range(4):
        p0, p1 = dia[k_], dia[(k_ + 1) % 4]
        for m in range(3):
            ring.append(c_ + nrm * 0.014 + p0.lerp(p1, m / 3))
    Hh.plate3d(bm, ring)
    bm = Hh.harden(bm, thick=0.006, bevel=0.0015, segs=1)
    made.append(P(f"JD_Shoulder_Scroll_{L}", bm, "04_Shoulder", "red", "Armor", weights=capw))
    bm = bmesh.new()                                                   # bingkai & titik emas emblem
    Hh.closed_tube(bm, [q + nrm * 0.002 for q in ring], 0.0045, n=5)
    made.append(P(f"JD_Shoulder_Emblem_{L}", bm, "04_Shoulder", "gold", "Armor", weights=capw))

    bm = bmesh.new()                                                   # bilah runcing: dua tinggi ke atas + satu kecil ke luar
    top = C0 + tilt @ Vector((0, 0, 0.064))
    for pts, r0 in (([top + Vector((-s * 0.012, -0.045, -0.008)), top + Vector((s * 0.000, -0.052, 0.040)),
                      top + Vector((s * 0.018, -0.050, 0.088)), top + Vector((s * 0.040, -0.042, 0.122))], 0.046),
                    ([top + Vector((-s * 0.010, 0.045, -0.010)), top + Vector((s * 0.004, 0.054, 0.032)),
                      top + Vector((s * 0.022, 0.060, 0.072)), top + Vector((s * 0.042, 0.060, 0.098))], 0.038),
                    ([C0 + Vector((s * 0.105, 0.0, -0.040)), C0 + Vector((s * 0.140, 0.0, -0.030)), C0 + Vector((s * 0.172, 0.0, -0.016))], 0.024)):
        Hh.tube(bm, Hh.catmull(pts, 4), lambda t, r0=r0: r0 * (1 - t) ** 0.9 + 0.0006, n=6, squash=(1.0, 0.38), up=(0, 1, 0))
    made.append(P(f"JD_Shoulder_Spike_{L}", bm, "04_Shoulder", "gold", "Armor", weights=capw))

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
tot = 0
for ob in made:
    t = C.tri_count(ob, dg)
    tot += t
    print(f"{ob.name:28s} {t:6d}")
print("TORSO+BAHU tris:", tot)
