"""Aksa Iterasi 2 putaran 2 — kepala dari MPFB (MakeHuman untuk Blender; aset inti CC0, kode GPLv3), disesuaikan ke konsep.

Jalankan di Blender yang ekstensi MPFB-nya aktif (MCP: exec(open(path).read())), dengan aksa_v02_head.blend atau aksa_v03_mpfb.blend
terbuka. Langkah:
  1. MPFB create_human dengan MACRO (laki-laki 25 th, atletis, campuran Asia/Afrika) + TARGETS wajah (dari ak_head_front/side.png).
  2. Target di-bake, kepala + leher (grup `body`, z terpetakan >= NECK_CUT) diambil; helper (mata, gigi, bulu mata) dibuang.
  3. Dipetakan ke ukuran konsep: skala dari jarak mata-dagu (0,094 m), x dikali SX_EXTRA, mata di z 1,668, ujung hidung di y -0,111.
  4. Bola mata (sclera/iris/pupil) di pusat helper mata MPFB, alis mesh menempel ke permukaan, rambut dibangun ulang di kepala baru.
  5. Bobot kepala/leher: kaku ke `head` di atas garis rahang, campuran neck_02/neck_01/spine_05 di bawahnya.
Hasil: AK_Head (termasuk telinga & leher), AK_EyeSclera/Iris/Pupil, AK_Brows, AK_Hair, AK_HairHi -> aksa_v03_mpfb.blend.
Ubah MACRO/TARGETS lalu jalankan ulang untuk iterasi feedback wajah.
"""
import importlib
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C
import ak_hair as HA
import ak_hair2 as HA2
import ak_hair3 as HA3
import ak_head as HD
import jd_hero as HR

for m in (C, HD, HA, HA2, HA3, HR):
    importlib.reload(m)
from bl_ext.user_default.mpfb.services.humanservice import HumanService  # noqa: E402
from bl_ext.user_default.mpfb.services.targetservice import TargetService  # noqa: E402

assert any(k in bpy.data.filepath for k in ("aksa_v02", "aksa_v03")), "buka aksa_v02_head.blend atau aksa_v03_mpfb.blend"
OUT = C.ART / "Blender" / "aksa_v03_mpfb.blend"

MACRO = {"gender": 1.0, "age": 0.5, "muscle": 0.70, "weight": 0.38, "proportions": 0.80, "height": 0.6,
         "cupsize": 0.5, "firmness": 0.5, "race": {"asian": 0.45, "caucasian": 0.30, "african": 0.25}}
TARGETS = {
    # kepala & rahang: tegas, bersudut, pipi tirus
    "head-square": 0.30, "head-invertedtriangular": 0.25, "head-scale-horiz-decr": 0.08, "chin-bones-incr": 0.60, "chin-width-decr": 0.10, "chin-prominent-incr": 0.20,
    "chin-height-decr": 0.10, "l-cheek-bones-incr": 0.45, "r-cheek-bones-incr": 0.45, "l-cheek-volume-decr": 0.45, "r-cheek-volume-decr": 0.45,
    "l-cheek-inner-decr": 0.30, "r-cheek-inner-decr": 0.30,
    # alis rendah, ujung dalam turun (serius); dahi tegas
    "eyebrows-trans-down": 0.35, "eyebrows-angle-down": 0.30, "eyebrows-trans-forward": 0.25, "forehead-temple-decr": 0.15,
    # mata: berjarak lebar (konsep), lebih besar, almond, kelopak terbuka
    "l-eye-trans-out": 1.00, "r-eye-trans-out": 1.00, "l-eye-scale-incr": 0.70, "r-eye-scale-incr": 0.70,
    "l-eye-height2-incr": 0.25, "r-eye-height2-incr": 0.25, "l-eye-corner1-up": 0.15, "r-eye-corner1-up": 0.15,
    "l-eye-epicanthus-out": 0.30, "r-eye-epicanthus-out": 0.30, "l-eye-eyefold-up": 0.20, "r-eye-eyefold-up": 0.20,
    # hidung lurus, lebih pendek, jembatan jelas
    "nose-hump-decr": 0.40, "nose-point-width-incr": 0.15, "nose-nostrils-width-incr": 0.10, "nose-scale-vert-decr": 0.20,
    "nose-greek-incr": 0.20,
    # mulut: bibir tidak maju, sedang
    "mouth-lowerlip-volume-decr": 0.40, "mouth-upperlip-volume-decr": 0.35, "mouth-scale-depth-decr": 0.55, "mouth-scale-horiz-decr": 0.15,
    "mouth-trans-backward": 0.45, "l-eye-height1-incr": 0.20, "r-eye-height1-incr": 0.20, "l-eye-height3-incr": 0.15, "r-eye-height3-incr": 0.15,
    # leher atletis
    "neck-scale-horiz-incr": 0.25, "neck-scale-depth-incr": 0.15,
}
EYE_Z, CHIN_TO_EYE, NOSE_Y = 1.668, 0.094, -0.111
SX_EXTRA = 1.04
NECK_CUT = 1.465
NECK_FULL_Z = 1.585
EYE_SCALE = 1.20                    # mata stylized lebih besar (referensi developer): bukaan + bola mata + iris
IRIS_R = 0.0074                  # di bawah ini hanya silinder leher (bahu MPFB dibuang)
NECK_HALF_X = 0.072

arm = C.get_arm()
SEG = C.bone_segments(arm)

# ---------------------------------------------------------------- bersihkan
for ob in list(bpy.data.objects):
    if ob.name.startswith("Human") or (ob.type == "MESH" and ob.name.startswith(
            ("AK_Head", "AK_Ear", "AK_Eye", "AK_Brows", "AK_Hair", "AK_Neck", "AK_Cornea"))):
        bpy.data.objects.remove(ob, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials):
    for d in list(coll):
        if d.users == 0:
            coll.remove(d)

# ---------------------------------------------------------------- 1. manusia MPFB + target
human = HumanService.create_human(macro_detail_dict=MACRO)
for mo in list(human.modifiers):
    human.modifiers.remove(mo)
missing = []
for name, val in TARGETS.items():
    path = TargetService.target_full_path(name)
    if not path:
        missing.append(name)
        continue
    TargetService.load_target(human, path, weight=val)
TargetService.bake_targets(human)
if missing:
    print("target tidak ditemukan:", missing)

mw = human.matrix_world
V = human.data.vertices
vg = {g.name: g.index for g in human.vertex_groups}


def members(name, wmin=0.5):
    gi = vg[name]
    return [v.index for v in V if any(g.group == gi and g.weight > wmin for g in v.groups)]


def centroid(name):
    idx = members(name)
    return sum((mw @ V[i].co for i in idx), Vector()) / len(idx)


eye_l, eye_r = centroid("joint-l-eye"), centroid("joint-r-eye")
eye_c = (eye_l + eye_r) / 2
body = set(members("body", 0.0))
P = {i: mw @ V[i].co for i in body}
face_front = [p for p in P.values() if abs(p.x) < 0.008 and p.y < eye_c.y + 0.01 and eye_c.z - 0.2 < p.z < eye_c.z]
chin_z = min(p.z for p in face_front)
nose = min((p for p in P.values() if abs(p.z - eye_c.z) < 0.08), key=lambda p: p.y)
s = CHIN_TO_EYE / (eye_c.z - chin_z)
sx = s * SX_EXTRA
print(f"MPFB: mata z {eye_c.z:.4f}, dagu {chin_z:.4f}, hidung y {nose.y:.4f}, jarak mata {eye_l.x - eye_r.x:.4f} -> skala {s:.3f} (x {sx:.3f})")


def mp(p):
    return Vector((p.x * sx, (p.y - nose.y) * s + NOSE_Y, (p.z - eye_c.z) * s + EYE_Z))


# ---------------------------------------------------------------- 2-3. ambil kepala + leher, petakan
def keep(q):
    """Leher utuh sampai NECK_CUT, bahu/trapezius MPFB (|x| besar) dibuang di bawah NECK_FULL_Z."""
    if q.z >= NECK_FULL_Z:
        return True
    return q.z >= NECK_CUT and abs(q.x) < NECK_HALF_X


sel = {i for i in body if keep(mp(P[i]))}
bm = bmesh.new()
vmap = {}
for i in sel:
    vmap[i] = bm.verts.new(mp(P[i]))
for poly in human.data.polygons:
    if all(v in sel for v in poly.vertices):
        try:
            bm.faces.new([vmap[v] for v in poly.vertices])
        except ValueError:
            pass
mouth_c = (centroid("helper-upper-teeth") + centroid("helper-lower-teeth")) / 2
mouth_m = mp(mouth_c)
eye_lm, eye_rm = mp(eye_l), mp(eye_r)
helper_pts = [mw @ V[i].co for i in members("helper-l-eye", 0.0)]
eye_r_orig = max((p - eye_l).length for p in helper_pts)
EYE_RAD = eye_r_orig * s * 0.985
loose = [v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context="VERTS")
_bnd = [v for v in bm.verts if v.is_boundary and v.co.z < NECK_FULL_Z + 0.01]
for _ in range(6):
    _new = {}
    for v in _bnd:
        nb = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
        if len(nb) == 2:
            _new[v] = v.co.lerp((nb[0].co + nb[1].co) / 2, 0.5)
    for v, co in _new.items():
        v.co = co
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bpy.data.objects.remove(human, do_unlink=True)

for v in bm.verts:                                                    # perbesar daerah mata (kelopak ikut)
    for ec in (eye_lm, eye_rm):
        d = v.co - ec
        r = d.length
        if r < 0.040 and v.co.y < ec.y + 0.010:
            w = 1.0 - HD.smooth(0.010, 0.040, r)
            v.co = ec + d * (1.0 + (EYE_SCALE - 1.0) * w)
EYE_RAD *= EYE_SCALE
head = C.finish_part("AK_Head", bm, "02_Head", "skin", "Skin", kind="skin")
parts = [head]
print(f"kepala MPFB: {len(head.data.vertices)} vert, {C.tri_count(head)} tris; mata di x ±{eye_lm.x:.4f} z {eye_lm.z:.4f} y {eye_lm.y:.4f}, r {EYE_RAD:.4f}; mulut {tuple(round(c, 4) for c in mouth_m)}")

# warna bibir (elips di depan mulut)
ca = head.data.color_attributes["AK_Zone"]
skin, lip = C.zone_rgba("skin"), C.zone_rgba("lip")
for i, v in enumerate(head.data.vertices):
    if v.co.y < mouth_m.y - 0.004:
        e = (v.co.x / 0.0215) ** 2 + ((v.co.z - mouth_m.z) / 0.0105) ** 2
        t = 1.0 - HD.smooth(0.55, 1.0, e)
        if t > 0:
            ca.data[i].color = tuple(skin[j] * (1 - t) + lip[j] * t for j in range(4))

lash = C.zone_rgba("hair")
for i, v in enumerate(head.data.vertices):
    for ec in (eye_lm, eye_rm):
        dx, dz = v.co.x - ec.x, v.co.z - ec.z
        if v.co.y < ec.y and abs(dx) < 0.032 and abs(dz) < 0.018:
            e = (dx / (0.0165 * EYE_SCALE)) ** 2 + (dz / (0.0076 * EYE_SCALE)) ** 2
            t = math.exp(-((e - 1.0) / 0.12) ** 2) * (1.0 if dz > -0.001 else 0.15)
            if t > 0.05:
                c0 = tuple(ca.data[i].color)
                ca.data[i].color = tuple(c0[j] * (1 - 0.85 * t) + lash[j] * 0.85 * t for j in range(4))

# ---------------------------------------------------------------- 4. mata, alis, rambut
bvh = HD.make_bvh(head.data)


def cap(bmx, center, radius, theta, seg=22, rings_n=3):
    rows = []
    for j in range(rings_n + 1):
        th = theta * j / rings_n
        if j == 0:
            rows.append([bmx.verts.new(center + Vector((0, -radius, 0)))])
            continue
        rows.append([bmx.verts.new(center + Vector((math.sin(th) * math.cos(2 * math.pi * k / seg), -math.cos(th),
                                                    math.sin(th) * math.sin(2 * math.pi * k / seg))) * radius) for k in range(seg)])
    for k in range(seg):
        bmx.faces.new((rows[0][0], rows[1][(k + 1) % seg], rows[1][k]))
    for a, b in zip(rows[1:-1], rows[2:]):
        for k in range(seg):
            bmx.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    bmesh.ops.recalc_face_normals(bmx, faces=list(bmx.faces))


bm_s, bm_i, bm_p = bmesh.new(), bmesh.new(), bmesh.new()
for ctr in (eye_lm, eye_rm):
    bmesh.ops.create_uvsphere(bm_s, u_segments=22, v_segments=14, radius=EYE_RAD, matrix=Matrix.Translation(ctr) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    cap(bm_i, ctr, EYE_RAD + 0.0003, math.asin(min(0.95, IRIS_R / EYE_RAD)))
    cap(bm_p, ctr, EYE_RAD + 0.0006, math.asin(0.0030 / EYE_RAD), rings_n=2)
parts.append(C.finish_part("AK_EyeSclera", bm_s, "02_Head", "sclera", "Eyes", kind="rigid", bone="head"))
parts.append(C.finish_part("AK_EyeIris", bm_i, "02_Head", "iris", "Eyes", kind="rigid", bone="head"))
parts.append(C.finish_part("AK_EyePupil", bm_p, "02_Head", "pupil", "Eyes", kind="rigid", bone="head"))

bm = bmesh.new()
ex = eye_lm.x
for sgn_ in (1, -1):
    path = []
    lift_b = (EYE_SCALE - 1.0) * 0.012
    for fx, dz in [(0.46, 0.0165), (0.74, 0.0210), (1.04, 0.0238), (1.34, 0.0250), (1.60, 0.0228), (1.82, 0.0185)]:
        pt, nrm = HD.surface_point(bvh, sgn_ * ex * fx, EYE_Z + dz + lift_b, off=0.0020)
        if pt is None:
            raise RuntimeError(f"alis: tidak ada permukaan di x={sgn_ * ex * fx:.3f}")
        path.append(pt)
    HR.tube(bm, path, [0.0044, 0.0052, 0.0050, 0.0044, 0.0032, 0.0012], n=6, squash=(0.45, 1.0), caps=(True, True), up=Vector((0, -1, 0)))
parts.append(C.finish_part("AK_Brows", bm, "02_Head", "hair", "Hair", kind="rigid", bone="head"))

bm_shell = bmesh.new()
bvh_shell = HA3.build_shell(bm_shell, head.data)
bm_locks, bm_hi = bmesh.new(), bmesh.new()
n_cl = HA3.make_locks(bm_locks, bm_hi, bm_shell, bvh_shell, bvh)
parts.append(C.finish_part("AK_HairShell", bm_shell, "03_Hair", "hair", "Hair", kind="rigid", bone="head"))
parts.append(C.finish_part("AK_Hair", bm_locks, "03_Hair", "hair", "Hair", kind="rigid", bone="head"))
parts.append(C.finish_part("AK_HairHi", bm_hi, "03_Hair", "hair_hi", "Hair", kind="rigid", bone="head"))
print("gumpalan rambut:", n_cl)

# ---------------------------------------------------------------- 5. bobot
n = len(head.data.vertices)
C.distance_weights(head, SEG, ["spine_05", "neck_01", "neck_02"], k=2, power=4.0)
hg = head.vertex_groups.get("head") or head.vertex_groups.new(name="head")
for v in head.data.vertices:
    t = HD.smooth(1.555, 1.600, v.co.z + max(0.0, -(v.co.y + 0.03)) * 0.8)
    for g in list(v.groups):
        head.vertex_groups[g.group].add([v.index], g.weight * (1 - t), "REPLACE")
    if t > 1e-4:
        hg.add([v.index], t, "REPLACE")
C.smooth_weights(head, iters=2, factor=0.4)
for obj in parts:
    if obj["ak_kind"] == "rigid":
        C.set_weights(obj, {obj["ak_bone"]: {i: 1.0 for i in range(len(obj.data.vertices))}})
    C.clean_weights(obj)
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    mod.use_vertex_groups = True
    obj.parent = arm
for p_ in head.data.polygons:
    p_.use_smooth = True

hz = [v.co.z for o in parts if o.name.startswith("AK_Hair") for v in o.data.vertices]
tot = sum(C.tri_count(o) for o in parts)
for o in parts:
    print(f"  {o.name:14s} tris {C.tri_count(o):6d}")
print(f"rambut z maks {max(hz):.3f}; total kepala {tot} tris; model {sum(C.tri_count(o) for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('AK_') and not o.name.startswith('AK_REF'))}")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
print("Disimpan:", bpy.data.filepath)
