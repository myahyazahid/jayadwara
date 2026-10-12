"""Aksa Iterasi 5 (revisi wajah, 12 Okt 2026) — alis melengkung tipis, senyum tipis permanen, mata lebih terbuka (tidak "ngantuk").

Permintaan developer: alis mengikuti garis putih gambar (busur tipis, puncak di atas pertengahan mata, ujung dalam lebih rendah, ujung luar
lebih rendah dari puncak, lebih pendek ke luar); mulut agak tersenyum; mata terkesan mengantuk -> lebih terbuka.
Dijalankan di Blender pada file kerja (v05) TANPA mengulang kepala/pakaian/rig:
  1. Senyum: 50% delta `ak_smile` dipanggang ke Basis dan semua shape key lain (kecuali ak_smile sendiri) -> ak_smile=1,0 tetap senyum penuh.
  2. Mata: kelopak atas diangkat (maks ±3,2 mm di tengah, melebar halus ke lipatan) dan kelopak bawah turun 0,8 mm, dipanggang ke Basis
     dan semua key kecuali blink_L/R pada vertex yang digerakkan blink itu (kedipan tetap menutup penuh).
  3. Alis dibangun ulang (tabung tipis, ray cast ke permukaan kepala) + shape key transfer seperti aksa_22.
Idempoten lewat properti `ak_face_rev` pada AK_Head. Setelah ini ulangi: aksa_50_uv -> make_textures_aksa -> aksa_51_materials -> aksa_14_export.
"""
import importlib
import math
import sys

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C
import ak_head as HD
import jd_hero as HR

for m in (C, HD, HR):
    importlib.reload(m)

REV = 1
SMILE_BAKE = 0.08
EYE_UP, EYE_DOWN = 0.0018, 0.0005
EYE_SCALE, EYE_Z = 1.20, 1.668
# alis: (fx = kelipatan x pusat mata, dz di atas EYE_Z)  ujung dalam -> luar
BROW_PTS = [(0.42, 0.0052), (0.70, 0.0082), (1.00, 0.0104), (1.30, 0.0114), (1.58, 0.0108), (1.85, 0.0088)]   # revisi 5: rendah, ujung dalam turun (konsep)
BROW_R = [0.0038, 0.0042, 0.0040, 0.0035, 0.0025, 0.0009]

arm = C.get_arm()
head = bpy.data.objects["AK_Head"]
me = head.data
keys = me.shape_keys.key_blocks
n = len(me.vertices)


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


scl = bpy.data.objects["AK_EyeSclera"]
cx = [v.co.x for v in scl.data.vertices if v.co.x > 0]
ex = sum(cx) / len(cx)
ecs = {}
for sg in (1, -1):
    pts = [scl.matrix_world @ v.co for v in scl.data.vertices if v.co.x * sg > 0]
    ecs[sg] = sum(pts, Vector()) / len(pts)
EYE_Z = ecs[1].z                                   # pusat mata sebenarnya (kepala bisa diskalakan di aksa_22)

if head.get("ak_face_rev", 0) < REV:
    base_old = [keys[0].data[i].co.copy() for i in range(n)]
    old = {k.name: [k.data[i].co.copy() for i in range(n)] for k in keys}
    smile_d = [old["ak_smile"][i] - base_old[i] for i in range(n)]
    eye_off = [Vector() for _ in range(n)]
    for i, p in enumerate(base_old):
        sg = 1 if p.x > 0 else -1
        ec = ecs[sg]
        dx, dz = p.x - ec.x, p.z - ec.z
        if p.y < ec.y and abs(dx) < 0.034 and abs(dz) < 0.030:
            e = (dx / (0.0165 * EYE_SCALE)) ** 2 + (dz / (0.0076 * EYE_SCALE)) ** 2
            w = math.exp(-(e / 2.4) ** 2)
            s = smooth(-0.0015, 0.0025, dz)                       # 1 = kelopak atas, 0 = bawah
            outer = 1.0 + 0.25 * smooth(0.0, 0.016, dx * sg)      # sudut luar sedikit lebih terangkat
            eye_off[i] = Vector((0, 0, w * (EYE_UP * s * outer - EYE_DOWN * (1 - s))))
    for k in keys:
        for i in range(n):
            co = old[k.name][i].copy()
            if k.name != "ak_smile":
                co += smile_d[i] * SMILE_BAKE
            skip_eye = k.name.startswith("ak_blink") and (old[k.name][i] - base_old[i]).length > 1e-7
            if not skip_eye:
                co += eye_off[i]
            if k.name == "Basis":
                me.vertices[i].co = co
            k.data[i].co = co
    me.update()
    head["ak_face_rev"] = REV
    print("senyum + mata dipanggang; maks geser mata %.2f mm" % (max(v.length for v in eye_off) * 1000))
else:
    print("wajah sudah direvisi (ak_face_rev) — lewati senyum/mata")

# ---------------------------------------------------------------- alis
bvh = HD.make_bvh(me)
old_b = bpy.data.objects.get("AK_Brows")
if old_b is not None:
    bpy.data.objects.remove(old_b, do_unlink=True)
import bmesh  # noqa: E402

bm = bmesh.new()
lift_b = (EYE_SCALE - 1.0) * 0.012
for sg in (1, -1):
    path = []
    dense = []                                                  # 4 titik per segmen: alis mengikuti lengkung kepala (tidak mencuat lurus dari samping)
    for (f0, d0), (f1, d1) in zip(BROW_PTS[:-1], BROW_PTS[1:]):
        dense += [(f0 + (f1 - f0) * t / 4, d0 + (d1 - d0) * t / 4) for t in range(4)]
    dense.append(BROW_PTS[-1])
    for fx, dz in dense:
        pt, _nrm = HD.surface_point(bvh, sg * ex * fx, EYE_Z + dz + lift_b, off=0.0020)
        if pt is None:
            raise RuntimeError(f"alis: tidak ada permukaan di x={sg * ex * fx:.3f}")
        path.append(pt)
    HR.tube(bm, path, [BROW_R[min(int(i / 4), len(BROW_R) - 1)] + (BROW_R[min(int(i / 4) + 1, len(BROW_R) - 1)] - BROW_R[min(int(i / 4), len(BROW_R) - 1)]) * (i % 4) / 4 for i in range(len(path))], n=6, squash=(0.50, 1.0), caps=(True, True), up=Vector((0, -1, 0)))
brows = C.finish_part("AK_Brows", bm, "02_Head", "hair", "Hair", kind="rigid", bone="head")
kd = KDTree(n)
for vi, v in enumerate(me.vertices):
    kd.insert(v.co, vi)
kd.balance()
brows.shape_key_add(name="Basis", from_mix=False)
for sk_h in list(keys)[1:]:
    sk = brows.shape_key_add(name=sk_h.name, from_mix=False)
    for vi, v in enumerate(brows.data.vertices):
        _co, hi, dist = kd.find(v.co)
        if dist < 0.014:
            sk.data[vi].co = v.co + (sk_h.data[hi].co - me.vertices[hi].co) * 0.9
C.set_weights(brows, {"head": {i: 1.0 for i in range(len(brows.data.vertices))}})
C.clean_weights(brows)
mod = brows.modifiers.new("Armature", "ARMATURE")
mod.object = arm
mod.use_vertex_groups = True
brows.parent = arm
for kb in head.data.shape_keys.key_blocks[1:]:
    kb.value = 0.0
for kb in brows.data.shape_keys.key_blocks[1:]:
    kb.value = 0.0
print("alis dibangun ulang:", C.tri_count(brows), "tris")
bpy.ops.wm.save_mainfile()
