"""Aksa Iterasi 2 — kepala, wajah, telinga, mata, alis, rambut, leher (menggantikan proxy kepala Iterasi 1).

Jalankan di Blender (MCP: exec(open(path).read())) dengan aksa_v01_proxy.blend atau aksa_v02_head.blend terbuka. Membangun:
  AK_Head (kulit, loft cincin + fitur wajah, 12k tris), AK_Ear_L/R, AK_EyeSclera/Iris/Pupil (slot Eyes), AK_Brows, AK_Hair (tudung +
  gumpalan) + AK_HairHi (highlight coklat), AK_Neck. Semua kaku ke `head` kecuali leher (bobot jarak). Lalu menyimpan aksa_v02_head.blend.
Parameter wajah: ak_head.py (KEYS, feature); rambut: ak_hair.py. Ubah lalu jalankan ulang untuk iterasi feedback.
Kornea terpisah (mata) ditunda ke Iterasi 5 (butuh material translucent); bola mata + iris + pupil sudah terpisah.
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
import ak_head as HD
import jd_common as JC
import jd_hero as HR

for m in (C, HD, HA, HR):
    importlib.reload(m)

assert "aksa_v01" in bpy.data.filepath or "aksa_v02" in bpy.data.filepath, "buka aksa_v01_proxy.blend atau aksa_v02_head.blend"
OUT = C.ART / "Blender" / "aksa" / "aksa_v02_head.blend"
arm = C.get_arm()
SEG = C.bone_segments(arm)

for ob in list(bpy.data.objects):
    if ob.type == "MESH" and ob.name.startswith(("AK_Head", "AK_Ear", "AK_Eye", "AK_Brows", "AK_Hair", "AK_Neck", "AK_Cornea")):
        bpy.data.objects.remove(ob, do_unlink=True)
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)
parts = []


def new_part(name, bm, coll, zone, slot, kind="rigid", bone="head"):
    o = C.finish_part("AK_" + name, bm, coll, zone, slot, kind=kind, bone=bone)
    parts.append(o)
    return o


# ================================================================== kepala
bm = bmesh.new()
rings = HD.build_head(bm)
ts = HD.ring_angles()
ring_pts = [[(v.co.copy(), v.normal.copy()) for v in ring] for ring in rings]
head = new_part("Head", bm, "02_Head", "skin", "Skin")
bvh = HD.make_bvh(head.data)
lip = C.zone_rgba("lip")
ca = head.data.color_attributes["AK_Zone"]
nlip = 0
for i, v in enumerate(head.data.vertices):
    w, yf, yb, p = HD.profile(v.co.z)
    if abs(v.co.x) < 0.0225 and 1.5985 < v.co.z < 1.6190 and v.co.y < (yf + yb) / 2:
        t = HD.smooth(0.0225, 0.014, abs(v.co.x)) * HD.smooth(1.5985, 1.6035, v.co.z) * (1 - HD.smooth(1.6140, 1.6190, v.co.z))
        if abs(v.co.z - 1.6098) < 0.0012 and abs(v.co.x) < 0.0195:
            t = 1.0
        base = C.zone_rgba("skin")
        ca.data[i].color = tuple(base[j] * (1 - t) + lip[j] * t for j in range(4))
        nlip += t > 0.3
print("vertex bibir:", nlip)


# ================================================================== telinga
def build_ear(s):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=14, radius=1.0, matrix=Matrix.Diagonal((0.0055, 0.0155, 0.029, 1.0)))
    bm.normal_update()
    for v in bm.verts:
        y, z = v.co.y, v.co.z
        rn = math.hypot(y / 0.0155, (z + 0.001) / 0.029)
        d = -0.0035 * math.exp(-(rn / 0.5) ** 2) + 0.0020 * math.exp(-((rn - 0.88) / 0.13) ** 2)
        if v.co.x > 0:                                          # sisi luar saja
            v.co += Vector((d, 0, 0))
    if s < 0:
        for v in bm.verts:
            v.co.x = -v.co.x
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    phi = math.radians(-18 * s)
    bmesh.ops.rotate(bm, verts=list(bm.verts), cent=(0, 0, 0), matrix=Matrix.Rotation(phi, 3, "Z"))
    bmesh.ops.translate(bm, verts=list(bm.verts), vec=(s * 0.0590, 0.0077, 1.653))
    return bm


for tag, s in (("L", 1), ("R", -1)):
    new_part(f"Ear_{tag}", build_ear(s), "02_Head", "skin", "Skin")

# ================================================================== mata (bola + iris + pupil)
R = HD.EYE_R


def cap(bm, center, radius, theta, seg=22, rings_n=3):
    """Tutup bola menghadap -Y: sudut polar 0..theta."""
    rows = []
    for j in range(rings_n + 1):
        th = theta * j / rings_n
        if j == 0:
            rows.append([bm.verts.new(center + Vector((0, -radius, 0)))])
            continue
        row = []
        for k in range(seg):
            ph = 2 * math.pi * k / seg
            row.append(bm.verts.new(center + Vector((math.sin(th) * math.cos(ph), -math.cos(th), math.sin(th) * math.sin(ph))) * radius))
        rows.append(row)
    for k in range(seg):
        bm.faces.new((rows[0][0], rows[1][(k + 1) % seg], rows[1][k]))
    for a, b in zip(rows[1:-1], rows[2:]):
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))


bm_s, bm_i, bm_p = bmesh.new(), bmesh.new(), bmesh.new()
for s in (1, -1):
    ctr = Vector((s * HD.EYE_X, HD.EYE_CENTER_Y, HD.EYE_Z))
    bmesh.ops.create_uvsphere(bm_s, u_segments=22, v_segments=14, radius=R, matrix=Matrix.Translation(ctr) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    cap(bm_i, ctr, R + 0.0003, math.asin(0.0060 / R))
    cap(bm_p, ctr, R + 0.0006, math.asin(0.0023 / R), rings_n=2)
new_part("EyeSclera", bm_s, "02_Head", "sclera", "Eyes")
new_part("EyeIris", bm_i, "02_Head", "iris", "Eyes")
new_part("EyePupil", bm_p, "02_Head", "pupil", "Eyes")

# ================================================================== alis (mengikuti permukaan)
bm = bmesh.new()
for s in (1, -1):
    path = []
    for ax, z in [(0.010, 1.6835), (0.021, 1.6885), (0.033, 1.6915), (0.044, 1.6895), (0.0525, 1.6835)]:
        pt, nrm = HD.surface_point(bvh, s * ax, z, off=0.0018)
        if pt is None:
            raise RuntimeError(f"alis: tidak ada permukaan di x={s * ax}, z={z}")
        path.append(pt)
    HR.tube(bm, path, [0.0030, 0.0046, 0.0050, 0.0044, 0.0020], n=4, squash=(0.8, 1.0), caps=(True, True), up=Vector((0, -1, 0)))
new_part("Brows", bm, "02_Head", "hair", "Hair")

# ================================================================== rambut
bm = bmesh.new()
HA.scalp_cap(bm, ring_pts, ts)
bm_hi = bmesh.new()
n_cl = HA.make_clumps(bm, bvh, bm_hi)
new_part("Hair", bm, "03_Hair", "hair", "Hair")
new_part("HairHi", bm_hi, "03_Hair", "hair_hi", "Hair")
print("gumpalan rambut:", n_cl)

# ================================================================== leher (lebih ramping di atas, di belakang rahang)
bm = bmesh.new()
HR.tube(bm, [Vector(p) for p in [(0, 0.016, 1.495), (0, 0.012, 1.550), (0, 0.010, 1.598)]], [0.058, 0.043, 0.031], n=12, squash=(1.0, 0.95),
        caps=(False, False))
neck = new_part("Neck", bm, "01_Body", "skin", "Skin", kind="skin", bone=None)
bvh = None

# ================================================================== bobot + modifier
for obj in parts:
    n = len(obj.data.vertices)
    if obj["ak_kind"] == "rigid":
        C.set_weights(obj, {obj["ak_bone"]: {i: 1.0 for i in range(n)}})
    else:
        C.distance_weights(obj, SEG, ["spine_05", "neck_01", "neck_02", "head"], k=3, power=4.0)
        C.smooth_weights(obj, iters=2, factor=0.5)
    C.clean_weights(obj)
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    mod.use_vertex_groups = True
    obj.parent = arm

for ob in bpy.data.objects:                                     # tampilkan lagi (pratinjau sebelumnya menyembunyikan)
    if ob.name.startswith("AK_") and ob.type == "MESH":
        ob.hide_viewport = False
tot = 0
for o in parts:
    t = C.tri_count(o)
    tot += t
    print(f"  {o.name:16s} tris {t:6d}")
hz = [v.co.z for o in parts if o.name.startswith("AK_Hair") for v in o.data.vertices]
hx = [abs(v.co.x) for o in parts if o.name.startswith("AK_Hair") for v in o.data.vertices]
print(f"rambut: z maks {max(hz):.3f} (target <= 1.806+2cm), lebar maks ±{max(hx):.3f} m")
print("TOTAL kepala+rambut+leher tris:", tot)
body = sum(C.tri_count(o) for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("AK_") and o not in parts and not o.name.startswith("AK_REF"))
print("TOTAL model (tris):", tot + body)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
print("Disimpan:", bpy.data.filepath)
