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

from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C
import ak_hair as HA
import ak_hair2 as HA2
import ak_hair3 as HA3
import ak_hair4 as HA4
import ak_hair5 as HA5
import ak_head as HD
import jd_hero as HR

for m in (C, HD, HA, HA2, HA3, HA4, HA5, HR):
    importlib.reload(m)
from bl_ext.user_default.mpfb.services.humanservice import HumanService  # noqa: E402
from bl_ext.user_default.mpfb.services.locationservice import LocationService  # noqa: E402
from bl_ext.user_default.mpfb.services.targetservice import TargetService  # noqa: E402

assert any(k in bpy.data.filepath for k in ("aksa_v02", "aksa_v03", "aksa_v04", "aksa_v05")), "buka aksa_v03..v05"
OUT = Path(bpy.data.filepath) if any(k in bpy.data.filepath for k in ("aksa_v04", "aksa_v05")) else C.ART / "Blender" / "aksa_v03_mpfb.blend"

MACRO = {"gender": 1.0, "age": 0.5, "muscle": 0.78, "weight": 0.46, "proportions": 0.80, "height": 0.6,
         "cupsize": 0.5, "firmness": 0.5, "race": {"asian": 0.45, "caucasian": 0.30, "african": 0.25}}
TARGETS = {
    # Revisi 5 (12 Okt 2026, developer: "wajah sangat tidak mirip" -> bandingkan dengan konsep ak_head_front/side.png):
    # wajah oval-V (rahang meruncing ke dagu sempit tapi tegas), tulang pipi tinggi + pipi tirus, dagu lebih panjang & maju
    "head-oval": 0.40, "head-invertedtriangular": 0.12, "head-square": 0.10, "head-fat-decr": 0.15,
    "chin-height-incr": 0.80, "chin-width-decr": 0.15, "chin-prominent-incr": 0.70, "chin-prognathism-incr": 0.60, "chin-bones-incr": 0.25,
    "l-cheek-bones-incr": 0.55, "r-cheek-bones-incr": 0.55, "l-cheek-volume-decr": 0.40, "r-cheek-volume-decr": 0.40,
    "l-cheek-inner-decr": 0.35, "r-cheek-inner-decr": 0.35,
    # alis rendah, tulang alis tegas, dahi sedikit miring ke belakang (profil konsep)
    "eyebrows-trans-down": 0.35, "eyebrows-trans-forward": 0.60, "forehead-trans-backward": 0.45, "forehead-temple-decr": 0.15,
    # mata almond besar berjarak lebar, sudut luar sedikit naik
    "l-eye-trans-out": 1.0, "r-eye-trans-out": 1.0, "l-eye-scale-incr": 0.80, "r-eye-scale-incr": 0.80,
    "l-eye-height2-decr": 0.20, "r-eye-height2-decr": 0.20, "l-eye-corner2-up": 0.35, "r-eye-corner2-up": 0.35,
    "l-eye-epicanthus-out": 0.15, "r-eye-epicanthus-out": 0.15, "l-eye-bag-decr": 0.40, "r-eye-bag-decr": 0.40,
    # hidung lurus, ramping, menonjol (bukan lebar/bulat)
    "nose-width1-decr": 0.30, "nose-width2-decr": 0.45, "nose-width3-decr": 0.35, "nose-nostrils-width-decr": 0.35,
    "nose-point-width-decr": 0.45, "nose-volume-decr": 0.30, "nose-scale-depth-incr": 0.45, "nose-point-up": 0.25, "nose-trans-forward": 0.15, "nose-hump-decr": 0.30,
    "nose-flaring-decr": 0.30, "nose-trans-down": 0.10, "nose-scale-vert-incr": 0.15,
    # mulut lebih sempit, bibir atas tipis bersudut (cupid's bow), bibir bawah sedang, sedikit lebih jauh dari hidung
    "mouth-scale-horiz-decr": 0.30, "mouth-cupidsbow-incr": 0.25, "mouth-upperlip-volume-incr": 0.25, "mouth-lowerlip-volume-decr": 0.25, "mouth-upperlip-height-incr": 0.15,
    "mouth-trans-down": 0.60, "mouth-trans-backward": 0.30, "mouth-scale-depth-decr": 0.40, "mouth-philtrum-volume-incr": 0.20,
    # leher tetap seperti revisi 4 (kerah/kaos sudah dipas ke leher ini)
    "neck-scale-horiz-incr": 0.45, "neck-scale-depth-incr": 0.25, "neck-double-decr": 1.0,
}
EYE_Z, CHIN_TO_EYE, NOSE_Y = 1.668, 0.094, -0.111
EYE_TO_CROWN = 0.0817             # revisi 5: skala dari mata->ubun-ubun (tengkorak & rambut tetap), wajah bebas memanjang lewat target
SX_EXTRA = 1.10
LOWER_Z, LOWER_K = 1.614, 0.0           # revisi 5c: 0 (peregangan depan saja membuat garis rahang miring di tampak samping)
HEAD_K, HEAD_PIVOT_Z = 1.16, 1.535        # revisi 5b: kepala sedikit lebih besar terhadap badan (developer: wajah tidak proporsional)
NECK_KX, NECK_KY, NECK_CY = 0.90, 0.86, 0.010   # revisi 5: leher bawah dikecilkan ke ukuran revisi 4 (kaos/kerah dipas ke situ)
NECK_CUT = 1.430
NECK_FULL_Z = 1.585
EYE_SCALE = 1.20                    # mata stylized lebih besar (referensi developer): bukaan + bola mata + iris
IRIS_R = 0.0078                  # di bawah ini hanya silinder leher (bahu MPFB dibuang)
NECK_HALF_X = 0.072

arm = C.get_arm()
SEG = C.bone_segments(arm)

# ---------------------------------------------------------------- bersihkan
for ob in list(bpy.data.objects):
    if ob.name.startswith("Human") or (ob.type == "MESH" and ob.name.startswith(
            ("AK_Head", "AK_Ear", "AK_Eye", "AK_Brows", "AK_Hair", "AK_Neck", "AK_Cornea"))) and not ob.name.startswith("AK_Necklace"):
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
crown_z = max(p.z for p in P.values())
s = EYE_TO_CROWN / (crown_z - eye_c.z)
sx = s * SX_EXTRA
print(f"MPFB: mata z {eye_c.z:.4f}, dagu {chin_z:.4f}, hidung y {nose.y:.4f}, jarak mata {eye_l.x - eye_r.x:.4f} -> skala {s:.3f} (x {sx:.3f})")


def mp(p):
    z = (p.z - eye_c.z) * s + EYE_Z
    t = HD.smooth(1.545, 1.610, z)                                         # 0 = leher bawah, 1 = wajah/kepala
    sxe = s * (NECK_KX + (SX_EXTRA - NECK_KX) * t)                         # lebar ekstra hanya wajah; leher dipas ke kaos/kerah (revisi 4)
    y = (p.y - nose.y) * s + NOSE_Y
    y = NECK_CY + (y - NECK_CY) * (NECK_KY + (1.0 - NECK_KY) * t)
    dzm = LOWER_Z - z                                                      # revisi 5: wajah bawah (mulut->dagu) lebih panjang seperti konsep
    if dzm > 0:
        z -= LOWER_K * 0.045 * (1.0 - math.exp(-dzm / 0.045)) * HD.smooth(-0.010, -0.050, y)
    k = 1.0 + (HEAD_K - 1.0) * HD.smooth(HEAD_PIVOT_Z - 0.02, HEAD_PIVOT_Z + 0.025, z)   # perbesar kepala dari pangkal leher
    return Vector((p.x * sxe * k, NECK_CY + (y - NECK_CY) * k, HEAD_PIVOT_Z + (z - HEAD_PIVOT_Z) * k))


# ---------------------------------------------------------------- 2-3. ambil kepala + leher, petakan
def keep(q):
    """Leher utuh sampai NECK_CUT, bahu/trapezius MPFB (|x| besar) dibuang di bawah NECK_FULL_Z."""
    if q.z >= NECK_FULL_Z:
        return True
    return q.z >= NECK_CUT and abs(q.x) < NECK_HALF_X


sel = {i for i in body if keep(mp(P[i]))}

# ---- delta ekspresi (unit FACS MPFB, ras asian) -> morph target Aksa
UNIT_DIR = Path(LocationService.get_mpfb_data("targets")) / "expression" / "units" / "asian"
RECIPES = {
    "ak_blink_L": {"eye-left-closure": 1.0},
    "ak_blink_R": {"eye-right-closure": 1.0},
    "ak_smile": {"mouth-corner-puller": 1.0, "mouth-upward-retraction": 0.35, "eye-left-slit": 0.25, "eye-right-slit": 0.25},
    "ak_angry": {"eyebrows-left-down": 1.0, "eyebrows-right-down": 1.0, "nose-compression": 0.6, "mouth-compression": 0.5,
                 "eye-left-slit": 0.3, "eye-right-slit": 0.3},
    "ak_mouth_open": {"mouth-open": 1.0},
    "ak_brow_up": {"eyebrows-left-up": 1.0, "eyebrows-right-up": 1.0},
    "ak_wince": {"eye-left-slit": 0.9, "eye-right-slit": 0.9, "mouth-retraction": 0.7, "nose-compression": 0.6, "mouth-eversion": 0.3},
    "ak_sad": {"eyebrows-left-inner-up": 1.0, "eyebrows-right-inner-up": 1.0, "mouth-depression": 0.8,
               "eye-left-slit": 0.15, "eye-right-slit": 0.15},
}
unit_names = sorted({u for r in RECIPES.values() for u in r})
base_key = human.data.shape_keys.reference_key if human.data.shape_keys else None
unit_delta = {}
lin = mw.to_3x3()
for u in unit_names:
    kb = TargetService.load_target(human, str(UNIT_DIR / f"{u}.target.gz"), weight=0.0, name="ak_unit_" + u)
    ref = human.data.shape_keys.reference_key
    unit_delta[u] = {i: (lambda d: Vector((d.x * sx, d.y * s, d.z * s)))(lin @ (kb.data[i].co - ref.data[i].co)) for i in sel}
MORPH = {}
for name, rec in RECIPES.items():
    acc = {}
    for u, w in rec.items():
        for i, d in unit_delta[u].items():
            if d.length > 1e-6:
                acc[i] = acc.get(i, Vector()) + d * w
    MORPH[name] = acc
print("morph:", {k: len(v) for k, v in MORPH.items()})

bm = bmesh.new()
SRC = bm.verts.layers.int.new("ak_src")
vmap = {}
for i in sel:
    vmap[i] = bm.verts.new(mp(P[i]))
    vmap[i][SRC] = i
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
        if r < 0.040:
            w = (1.0 - HD.smooth(0.010, 0.040, r)) * (1.0 - HD.smooth(ec.y, ec.y + 0.020, v.co.y))   # tanpa patahan di y
            v.co = ec + d * (1.0 + (EYE_SCALE - 1.0) * w)
EYE_RAD *= EYE_SCALE
head = C.finish_part("AK_Head", bm, "02_Head", "skin", "Skin", kind="skin")
parts = [head]
src_idx = [d.value for d in head.data.attributes["ak_src"].data]
head.shape_key_add(name="Basis", from_mix=False)
for name, deltas in MORPH.items():
    sk = head.shape_key_add(name=name, from_mix=False)
    for vi, si in enumerate(src_idx):
        d = deltas.get(si)
        if d is not None:
            sk.data[vi].co = head.data.vertices[vi].co + d
head.data.attributes.remove(head.data.attributes["ak_src"])
print(f"kepala MPFB: {len(head.data.vertices)} vert, {C.tri_count(head)} tris; mata di x ±{eye_lm.x:.4f} z {eye_lm.z:.4f} y {eye_lm.y:.4f}, r {EYE_RAD:.4f}; mulut {tuple(round(c, 4) for c in mouth_m)}")

# warna bibir (elips di depan mulut)
ca = head.data.color_attributes["AK_Zone"]
skin, lip = C.zone_rgba("skin"), C.zone_rgba("lip")
for i, v in enumerate(head.data.vertices):
    if v.co.y < mouth_m.y - 0.004:
        e = (v.co.x / 0.0235) ** 2 + ((v.co.z - mouth_m.z) / 0.0110) ** 2
        t = 1.0 - HD.smooth(0.70, 1.05, e)
        if t > 0:
            ca.data[i].color = tuple(skin[j] * (1 - t) + lip[j] * t for j in range(4))
        dz = abs(v.co.z - mouth_m.z)
        if dz < 0.0016 and abs(v.co.x) < 0.0175:                           # garis mulut gelap tipis
            k = (1 - dz / 0.0016) * (1 - HD.smooth(0.011, 0.0175, abs(v.co.x)))
            c0 = tuple(ca.data[i].color)
            dark = C.zone_rgba("belt")
            ca.data[i].color = tuple(c0[j] * (1 - 0.55 * k) + dark[j] * 0.55 * k for j in range(4))

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
    for fx, dz in [(0.40, 0.0150), (0.70, 0.0185), (1.02, 0.0218), (1.34, 0.0238), (1.62, 0.0232), (1.84, 0.0205)]:
        pt, nrm = HD.surface_point(bvh, sgn_ * ex * fx, EYE_Z + dz + lift_b, off=0.0020)
        if pt is None:
            raise RuntimeError(f"alis: tidak ada permukaan di x={sgn_ * ex * fx:.3f}")
        path.append(pt)
    HR.tube(bm, path, [0.0034, 0.0044, 0.0044, 0.0040, 0.0030, 0.0012], n=6, squash=(0.50, 1.0), caps=(True, True), up=Vector((0, -1, 0)))
brows = C.finish_part("AK_Brows", bm, "02_Head", "hair", "Hair", kind="rigid", bone="head")
parts.append(brows)
from mathutils.kdtree import KDTree  # noqa: E402
kd = KDTree(len(head.data.vertices))
for vi, v in enumerate(head.data.vertices):
    kd.insert(v.co, vi)
kd.balance()
brows.shape_key_add(name="Basis", from_mix=False)
for sk_h in list(head.data.shape_keys.key_blocks)[1:]:
    sk = brows.shape_key_add(name=sk_h.name, from_mix=False)
    for vi, v in enumerate(brows.data.vertices):
        co, hi, dist = kd.find(v.co)
        if dist < 0.014:
            sk.data[vi].co = v.co + (sk_h.data[hi].co - head.data.vertices[hi].co) * 0.9

# rambut gaya 4 (ak_hair4.py). Konstanta rambut (garis rambut, ketebalan) dibuat untuk kepala skala 1 -> bangun di salinan kepala yang
# skalanya dibalik (HEAD_K), lalu hasilnya diskalakan maju lagi.
def _hk(co, inv):
    k = 1.0 / HEAD_K if inv else HEAD_K
    return Vector((co.x * k, NECK_CY + (co.y - NECK_CY) * k, HEAD_PIVOT_Z + (co.z - HEAD_PIVOT_Z) * k))


_tmp = head.data.copy()
for v in _tmp.vertices:
    v.co = _hk(v.co, True)
bm_shell, bm_locks, bm_hi, n_cl = HA5.build(_tmp)                 # gaya 5: low fade + atas bertekstur
bpy.data.meshes.remove(_tmp)
for _bm in (bm_shell, bm_locks, bm_hi):
    for v in _bm.verts:
        v.co = _hk(v.co, False)
print("fade: vertex kulit kepala diwarnai", HA5.paint_fade(head, lambda co: _hk(co, True)))
parts.append(C.finish_part("AK_HairShell", bm_shell, "03_Hair", "hair", "Hair", kind="rigid", bone="head"))
parts.append(C.finish_part("AK_Hair", bm_locks, "03_Hair", "hair", "Hair", kind="rigid", bone="head"))
parts.append(C.finish_part("AK_HairHi", bm_hi, "03_Hair", "hair_hi", "Hair", kind="rigid", bone="head"))
print("helai rambut:", n_cl)

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
