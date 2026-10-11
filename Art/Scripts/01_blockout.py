"""Iterasi 1 — blockout proxy Jayadwara (bagian per bagian, bentuk bersudut).

Jalankan di Blender 5.2 setelah 00_setup_scene.py. Aman dijalankan ulang: mesh JD_* lama dihapus dulu.
Target: < 12k tris total, 4 slot material, tiap bagian diberi metadata rig (jd_bone / jd_weights / jd_chain).
Dimensi: docs/14-model-sheet-jayadwara.md; posisi sendi: jd_skeleton.py.
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
import jd_skeleton as SK
importlib.reload(C)
importlib.reload(SK)

S = SK.SIDES
rad = math.radians


def resample(points, factor):
    out = []
    for a, b in zip(points[:-1], points[1:]):
        for k in range(factor):
            out.append(a.lerp(b, k / factor))
    out.append(points[-1])
    return out


def bm_new():
    return bmesh.new()


def part(name, bm, coll, zone, slot, **kw):
    return C.finish_part(name, bm, coll, zone, slot, **kw)


C.remove_existing("JD_")
parts = []

# ============================================================== BODY (undersuit, Skin modifier)
bm = bm_new()
skin = bm.verts.layers.skin.verify()


def sv(p, r, root=False):
    v = bm.verts.new(Vector(p))
    v[skin].radius = r
    v[skin].use_root = root
    return v


P = sv((0, 0, 0.95), (0.145, 0.105), root=True)
Wst = sv((0, 0, 1.09), (0.135, 0.095))
C1 = sv((0, 0, 1.29), (0.165, 0.125))
C2 = sv((0, 0, 1.47), (0.18, 0.13))
N0 = sv((0, 0, 1.56), (0.05, 0.05))
N1 = sv((0, 0, 1.66), (0.048, 0.048))
for a, b in ((P, Wst), (Wst, C1), (C1, C2), (C2, N0), (N0, N1)):
    bm.edges.new((a, b))
seg = SK.bone_segments()
for sd, s in S.items():
    sh = seg[f"upperarm_{sd}"][0]
    el = seg[f"lowerarm_{sd}"][0]
    wr = seg[f"hand_{sd}"][0]
    vs, ve, vw = sv(sh, (0.06, 0.06)), sv(el, (0.048, 0.048)), sv(wr, (0.04, 0.04))
    for a, b in ((C2, vs), (vs, ve), (ve, vw)):
        bm.edges.new((a, b))
    hip, knee, ankle = seg[f"thigh_{sd}"][0], seg[f"calf_{sd}"][0], seg[f"foot_{sd}"][0]
    vh, vk, va = sv(hip, (0.085, 0.085)), sv(knee, (0.072, 0.072)), sv(ankle, (0.052, 0.052))
    for a, b in ((P, vh), (vh, vk), (vk, va)):
        bm.edges.new((a, b))

tmp_mesh = bpy.data.meshes.new("_tmp_skin")
bm.to_mesh(tmp_mesh)
bm.free()
tmp = bpy.data.objects.new("_tmp_skin", tmp_mesh)
bpy.context.scene.collection.objects.link(tmp)
mod = tmp.modifiers.new("Skin", "SKIN")
mod.use_smooth_shade = True
mod.branch_smoothing = 0.6
sub = tmp.modifiers.new("Subsurf", "SUBSURF")
sub.levels = 1
sub.render_levels = 1
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev_mesh = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
bm = bmesh.new()
bm.from_mesh(ev_mesh)
bpy.data.objects.remove(tmp, do_unlink=True)
bpy.data.meshes.remove(tmp_mesh)
bpy.data.meshes.remove(ev_mesh)
parts.append(part("JD_Body_Undersuit", bm, "01_Body", "black", "Body", kind="skin", smooth=True))

# ============================================================== HEAD
bm = bm_new()
C.add_ico(bm, (0, 0.02, 1.785), (0.108, 0.14, 0.115), sub=2)
parts.append(part("JD_Head_Helm", bm, "02_Head", "red", "Armor", bone="head"))

bm = bm_new()
C.add_prism(bm, (0, 0.03, 1.885), (0, 0.075, 1.935), 0.028, 0.004, seg=4)       # rusuk tengah kubah
parts.append(part("JD_Head_Crest", bm, "02_Head", "red", "Armor", bone="head"))

for sd, s in S.items():
    L = sd.upper()
    bm = bm_new()
    C.add_prism(bm, (s * 0.10, 0.02, 1.785), (s * 0.115, 0.19, 1.70), 0.028, 0.003, seg=4)   # sirip pelipis
    parts.append(part(f"JD_Head_Fin_{L}", bm, "02_Head", "red", "Armor", bone="head"))

    bm = bm_new()
    C.add_prism(bm, (s * 0.002, -0.118, 1.79), (s * 0.10, -0.072, 1.832), 0.014, 0.012, seg=4)  # pelindung alis (V)
    parts.append(part(f"JD_Head_Brow_{L}", bm, "02_Head", "gold", "Armor", bone="head"))

    bm = bm_new()                                                                              # tanduk (K4)
    pts = [(s * 0.10, -0.072, 1.832), (s * 0.125, -0.066, 1.885), (s * 0.145, -0.056, 1.945), (s * 0.14, -0.046, 1.99)]
    radii = [0.024, 0.018, 0.010, 0.002]
    for i in range(3):
        C.add_prism(bm, pts[i], pts[i + 1], radii[i], radii[i + 1], seg=5, cap=(i == 2))
    parts.append(part(f"JD_Head_Horn_{L}", bm, "02_Head", "gold", "Armor", bone="head"))

    bm = bm_new()                                                                              # mata (celah miring, K6)
    front = [(s * 0.025, -0.121, 1.768), (s * 0.025, -0.121, 1.777),
             (s * 0.077, -0.097, 1.798), (s * 0.077, -0.097, 1.790)]
    C.add_hull(bm, front + [(x, y + 0.006, z) for x, y, z in front])
    parts.append(part(f"JD_Head_Eye_{L}", bm, "02_Head", "eye", "Face", bone="head"))

bm = bm_new()
C.add_ico(bm, (0, -0.116, 1.835), (0.028, 0.012, 0.045), sub=1)                                # ornamen dahi (K3)
parts.append(part("JD_Head_Forehead", bm, "02_Head", "gold", "Armor", bone="head"))

bm = bm_new()
C.add_hull(bm, [(-0.068, -0.108, 1.764), (0.068, -0.108, 1.764), (-0.05, -0.098, 1.72), (0.05, -0.098, 1.72),
                (0, -0.128, 1.672), (0, -0.108, 1.676), (-0.068, -0.082, 1.764), (0.068, -0.082, 1.764)])
parts.append(part("JD_Head_Faceplate", bm, "02_Head", "white", "Face", bone="head"))             # pelat putih V (K2)

bm = bm_new()
C.add_hull(bm, [(0, -0.138, 1.652), (0.026, -0.118, 1.695), (-0.026, -0.118, 1.695), (0, -0.098, 1.668)])
parts.append(part("JD_Head_Chin", bm, "02_Head", "red", "Armor", bone="head"))                  # dagu "paruh" merah

bm = bm_new()
C.add_cyl(bm, (0, 0, 1.625), (0.072, 0.072), 0.05, seg=8)
parts.append(part("JD_Head_Collar", bm, "02_Head", "black", "Body", bone="neck_02"))

# ============================================================== TORSO
chest_w = {"spine_04": 0.5, "spine_05": 0.5}
bm = bm_new()
C.add_hull(bm, [(-0.18, -0.09, 1.55), (0.18, -0.09, 1.55), (-0.18, 0.06, 1.55), (0.18, 0.06, 1.55),
                (-0.195, -0.125, 1.42), (0.195, -0.125, 1.42), (0, -0.16, 1.45),
                (-0.15, -0.105, 1.27), (0.15, -0.105, 1.27), (-0.15, 0.05, 1.27), (0.15, 0.05, 1.27), (0, -0.14, 1.29)])
parts.append(part("JD_Torso_Chest", bm, "03_Torso", "red", "Armor", weights=chest_w))

bm = bm_new()
for s in (+1, -1):                                                                              # chevron V emas
    C.add_prism(bm, (s * 0.168, -0.118, 1.54), (0, -0.163, 1.425), 0.017, 0.017, seg=4)
    C.add_prism(bm, (s * 0.105, -0.128, 1.325), (0, -0.151, 1.262), 0.013, 0.013, seg=4)
parts.append(part("JD_Torso_Chevron", bm, "03_Torso", "gold", "Armor", weights=chest_w))

bm = bm_new()
C.add_hull(bm, [(0, -0.162, 1.53), (0, -0.162, 1.43), (-0.026, -0.162, 1.48), (0.026, -0.162, 1.48),
                (0, -0.176, 1.48), (0, -0.150, 1.48)])
parts.append(part("JD_Torso_Gem", bm, "03_Torso", "gem", "Face", weights=chest_w))              # permata statis (K1, K6)

bm = bm_new()
C.add_hull(bm, [(-0.17, 0.06, 1.55), (0.17, 0.06, 1.55), (-0.17, 0.14, 1.52), (0.17, 0.14, 1.52),
                (-0.12, 0.06, 1.25), (0.12, 0.06, 1.25), (-0.12, 0.115, 1.28), (0.12, 0.115, 1.28), (0, 0.152, 1.42)])
parts.append(part("JD_Torso_Back", bm, "03_Torso", "red", "Armor", weights=chest_w))

# ============================================================== SHOULDER, ARM
for sd, s in S.items():
    L = sd.upper()
    sw = {f"clavicle_{sd}": 0.6, f"upperarm_{sd}": 0.4}
    bm = bm_new()
    C.add_ico(bm, (s * 0.255, 0, 1.605), (0.095, 0.085, 0.075), sub=2, rot=(0, s * rad(20), 0))
    parts.append(part(f"JD_Shoulder_Pauldron_{L}", bm, "04_Shoulder", "gold", "Armor", weights=sw))
    bm = bm_new()
    C.add_prism(bm, (s * 0.24, 0, 1.63), (s * 0.235, 0, 1.676), 0.034, 0.003, seg=4)
    parts.append(part(f"JD_Shoulder_Spike_{L}", bm, "04_Shoulder", "gold", "Armor", weights=sw))

    d = SK.arm_dir(s)
    el, wr = seg[f"lowerarm_{sd}"][0], seg[f"hand_{sd}"][0]
    bm = bm_new()
    C.add_prism(bm, el + d * 0.06, wr + d * 0.01, 0.054, 0.064, seg=6)
    parts.append(part(f"JD_Arm_Bracer_{L}", bm, "05_Arm", "gold", "Armor", bone=f"lowerarm_{sd}"))
    bm = bm_new()
    eul = d.to_track_quat("Z", "Y").to_euler()
    C.add_box(bm, wr + d * 0.065, (0.072, 0.056, 0.125), rot=tuple(eul))
    parts.append(part(f"JD_Arm_Glove_{L}", bm, "05_Arm", "black", "Body", bone=f"hand_{sd}"))

# ============================================================== BELT & CLOTH
bm = bm_new()
C.add_cyl(bm, (0, 0, 1.18), (0.168, 0.145), 0.07, seg=10)
parts.append(part("JD_Belt_Band", bm, "06_Belt_Cloth", "red", "Armor", bone="spine_02"))
bm = bm_new()
C.add_hull(bm, [(0, -0.153, 1.218), (0, -0.153, 1.142), (-0.034, -0.153, 1.18), (0.034, -0.153, 1.18),
                (0, -0.172, 1.18), (0, -0.142, 1.18)])
parts.append(part("JD_Belt_Buckle", bm, "06_Belt_Cloth", "gold", "Armor", bone="spine_02"))

# panel depan / belakang: strip dengan ujung runcing, rantai 3 tulang
for name, zs, y, dy, chain in (("Front", SK.CLOTH_FRONT_Z, SK.CLOTH_FRONT_Y, SK.CLOTH_FRONT_DY, "cloth_front"),
                               ("Back", SK.CLOTH_BACK_Z, SK.CLOTH_BACK_Y, SK.CLOTH_BACK_DY, "cloth_back")):
    line = resample(SK.cloth_points(zs, y, dy), 2)
    n = len(line)
    widths = [0.17 + 0.02 * math.sin(math.pi * i / (n - 1)) for i in range(n - 1)] + [0.0]
    bm = bm_new()
    C.add_strip(bm, line, widths, [Vector((1, 0, 0))] * n)
    parts.append(part(f"JD_Cloth_{name}", bm, "06_Belt_Cloth", "red", "Cloth", kind="strip", chain=chain))

for sd, s in S.items():                                                                          # selendang (K5)
    line = resample(SK.scarf_points(s), 2)
    n = len(line)
    sides, widths = [], []
    for i, p in enumerate(line):
        j = min(i, n - 2)
        dvec = (line[j + 1] - line[j]).normalized()
        sides.append(dvec.cross(Vector((0, 1, 0))).normalized())
        t = i / (n - 1)
        widths.append(0.19 * (1 - (abs(t - 0.3) / 0.7) ** 1.2) if i < n - 1 else 0.0)   # puncak lebar di t≈0,3, runcing di ujung
    bm = bm_new()
    C.add_strip(bm, line, widths, sides)
    parts.append(part(f"JD_Cloth_Scarf_{sd.upper()}", bm, "06_Belt_Cloth", "red", "Cloth", kind="strip", chain=f"scarf_{sd}"))

# ============================================================== LEG
for sd, s in S.items():
    L = sd.upper()
    hip, knee, ankle = seg[f"thigh_{sd}"][0], seg[f"calf_{sd}"][0], seg[f"foot_{sd}"][0]
    bm = bm_new()
    thigh_tilt = math.atan2(SK.KNEE_X - SK.HIP_X, hip.z - knee.z)           # paha melebar ke luar ke arah lutut
    C.add_box(bm, (s * (SK.HIP_X + SK.KNEE_X) / 2 + s * 0.012, -0.047, 0.76), (0.10, 0.065, 0.26),
              rot=(0, -s * thigh_tilt, 0))
    parts.append(part(f"JD_Leg_ThighGuard_{L}", bm, "07_Leg", "red", "Armor", bone=f"thigh_{sd}"))

    kx = knee.x
    bm = bm_new()
    C.add_hull(bm, [(kx, -0.07, 0.665), (kx, -0.07, 0.515), (kx - 0.05, -0.066, 0.59), (kx + 0.05, -0.066, 0.59),
                    (kx, -0.102, 0.59), (kx, -0.058, 0.59)])
    parts.append(part(f"JD_Leg_KneeGuard_{L}", bm, "07_Leg", "gold", "Armor", bone=f"calf_{sd}"))

    bm = bm_new()
    C.add_prism(bm, (kx, 0.0, 0.55), (ankle.x, 0.0, 0.16), 0.070, 0.054, seg=6, squash=(1.0, 1.55))   # kedalaman ±0,18 m (docs/14)
    parts.append(part(f"JD_Leg_Greave_{L}", bm, "07_Leg", "red", "Armor", bone=f"calf_{sd}"))

    fx = ankle.x
    ball = seg[f"ball_{sd}"][0]
    yaw = math.atan2(abs(ball.x) - abs(ankle.x), -(ball.y - ankle.y)) * s     # sepatu menghadap sedikit ke luar
    rz = Matrix.Rotation(yaw, 3, "Z")

    def foot_pts(pts):
        return [(Vector((fx, 0, 0)) + rz @ Vector((x, y, z))).to_tuple() for x, y, z in pts]

    boot = [(-0.06, 0.08, 0.02), (0.06, 0.08, 0.02), (-0.075, -0.18, 0.02), (0.075, -0.18, 0.02),
            (-0.065, -0.28, 0.02), (0.065, -0.28, 0.02), (-0.045, -0.28, 0.05), (0.045, -0.28, 0.05),
            (-0.06, 0.08, 0.17), (0.06, 0.08, 0.17), (-0.06, -0.02, 0.19), (0.06, -0.02, 0.19),
            (-0.065, -0.14, 0.10), (0.065, -0.14, 0.10)]
    bm = bm_new()
    C.add_hull(bm, foot_pts(boot))
    parts.append(part(f"JD_Leg_Boot_{L}", bm, "07_Leg", "red", "Armor", bone=f"foot_{sd}"))
    sole = [(-0.064, 0.085, 0.0), (0.064, 0.085, 0.0), (-0.08, -0.18, 0.0), (0.08, -0.18, 0.0),
            (-0.07, -0.29, 0.0), (0.07, -0.29, 0.0)]
    bm = bm_new()
    C.add_hull(bm, foot_pts(sole) + foot_pts([(x, y, 0.02) for x, y, _ in sole]))
    parts.append(part(f"JD_Leg_Sole_{L}", bm, "07_Leg", "black", "Body", bone=f"foot_{sd}"))

# ============================================================== laporan
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
total = 0
print(f"{'bagian':34s} {'tris':>6s}  zona   slot")
for ob in parts:
    t = C.tri_count(ob, dg)
    total += t
    print(f"{ob.name:34s} {t:6d}  {ob['jd_zone']:6s} {ob.data.materials[0].name.split('_')[-1]}")
print("TOTAL tris:", total, " | objek:", len(parts))
