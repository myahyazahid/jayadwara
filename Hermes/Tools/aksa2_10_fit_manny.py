"""Aksa2 H1 — Fit mesh ke pose rest Manny asli tanpa mengubah skeleton.
Input : Hermes/Art/aksa2/Blender/aksa2_v01_intake.blend
Output: Hermes/Art/aksa2/Blender/aksa2_v02_fit.blend
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v01_intake.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v02_fit.blend"
MANNY_FBX = ROOT / "Art" / "Reference" / "manny" / "SKM_Manny_Simple.fbx"
MANNY_JSON = ROOT / "Art" / "Reference" / "manny" / "manny_rest.json"

assert BLEND_IN.exists(), f"File intake tidak ditemukan: {BLEND_IN}"
assert MANNY_FBX.exists(), f"FBX Manny tidak ditemukan: {MANNY_FBX}"
assert MANNY_JSON.exists(), f"JSON Manny tidak ditemukan: {MANNY_JSON}"

with open(MANNY_JSON, encoding="utf-8") as f:
    manny_data = json.load(f)
manny = manny_data["joints_m"]

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
mesh_obj = bpy.data.objects.get("AK2_Source")
assert mesh_obj is not None, "AK2_Source tidak ditemukan"

# ------------------------------------------------------------------ 1) Impor Manny FBX sebagai AK2_Armature
before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(MANNY_FBX))
new_obs = [o for o in bpy.data.objects if o not in before]
arm = next(o for o in new_obs if o.type == "ARMATURE")

# Unparent dari empty 0.01x dan bake matrix_world
mw = arm.matrix_world.copy()
arm.parent = None
arm.matrix_world = mw

# Hapus empty dan mesh bawaan FBX
for o in new_obs:
    if o != arm:
        bpy.data.objects.remove(o, do_unlink=True)

bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Tambah tulang root sebagai induk akar Manny
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.data.edit_bones
roots = [b for b in eb if b.parent is None and b.name != "root"]
rb = eb.get("root") or eb.new("root")
rb.head, rb.tail = (0.0, 0.0, 0.0), (0.0, 0.1, 0.0)
for b in roots:
    b.parent = rb
    b.use_connect = False
bpy.ops.object.mode_set(mode="OBJECT")
arm.name = arm.data.name = "AK2_Armature"

# Masukkan ke collection AK2_Aksa
ak_coll = bpy.data.collections.get("AK2_Aksa")
if ak_coll:
    rig_coll = bpy.data.collections.get("08_Rig") or bpy.data.collections.new("08_Rig")
    if rig_coll.name not in ak_coll.children:
        ak_coll.children.link(rig_coll)
    for c in list(arm.users_collection):
        c.objects.unlink(arm)
    rig_coll.objects.link(arm)

print(f"AK2_Armature dibuat dengan {len(arm.data.bones)} tulang.")

# ------------------------------------------------------------------ 2) Fit Mesh via Temp Armature
temp_arm = arm.copy()
temp_arm.data = arm.data.copy()
temp_arm.name = temp_arm.data.name = "Temp_Armature"
bpy.context.scene.collection.objects.link(temp_arm)

DEFORM_BONES = {
    "pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "neck_02", "head",
    "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "thigh_l", "calf_l", "foot_l", "ball_l",
    "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r", "thigh_r", "calf_r", "foot_r", "ball_r",
}
for b in temp_arm.data.bones:
    b.use_deform = b.name in DEFORM_BONES

# Arah Tripo yang diukur
dir_up_l = Vector((0.311 - 0.1901, 0.135 - 0.0256, 1.20 - 1.4358)).normalized()
dir_lo_l = Vector((0.393 - 0.311, 0.149 - 0.135, 1.05 - 1.20)).normalized()
dir_up_r = Vector((-0.311 - (-0.1901), 0.135 - 0.0256, 1.20 - 1.4358)).normalized()
dir_lo_r = Vector((-0.393 - (-0.311), 0.149 - 0.135, 1.05 - 1.20)).normalized()

len_up = (Vector(manny["lowerarm_l"]) - Vector(manny["upperarm_l"])).length
len_lo = (Vector(manny["hand_l"]) - Vector(manny["lowerarm_l"])).length

dir_th_l = Vector((0.153 - 0.0997, 0.038 - (-0.0254), 0.5027 - 0.9354)).normalized()
dir_ca_l = Vector((0.182 - 0.153, 0.020 - 0.038, 0.0824 - 0.5027)).normalized()
dir_th_r = Vector((-0.153 - (-0.0997), 0.038 - (-0.0254), 0.5027 - 0.9354)).normalized()
dir_ca_r = Vector((-0.182 - (-0.153), 0.020 - 0.038, 0.0824 - 0.5027)).normalized()

len_th = (Vector(manny["calf_l"]) - Vector(manny["thigh_l"])).length
len_ca = (Vector(manny["foot_l"]) - Vector(manny["calf_l"])).length

bpy.context.view_layer.objects.active = temp_arm
bpy.ops.object.mode_set(mode="EDIT")
eb = temp_arm.data.edit_bones

# Lengan
sh_l = eb["upperarm_l"].head.copy()
el_l = sh_l + dir_up_l * len_up
wr_l = el_l + dir_lo_l * len_lo
eb["upperarm_l"].tail = eb["lowerarm_l"].head = el_l
eb["lowerarm_l"].tail = eb["hand_l"].head = wr_l

sh_r = eb["upperarm_r"].head.copy()
el_r = sh_r + dir_up_r * len_up
wr_r = el_r + dir_lo_r * len_lo
eb["upperarm_r"].tail = eb["lowerarm_r"].head = el_r
eb["lowerarm_r"].tail = eb["hand_r"].head = wr_r

# Kaki
hip_l = eb["thigh_l"].head.copy()
kn_l = hip_l + dir_th_l * len_th
an_l = kn_l + dir_ca_l * len_ca
eb["thigh_l"].tail = eb["calf_l"].head = kn_l
eb["calf_l"].tail = eb["foot_l"].head = an_l

hip_r = eb["thigh_r"].head.copy()
kn_r = hip_r + dir_th_r * len_th
an_r = kn_r + dir_ca_r * len_ca
eb["thigh_r"].tail = eb["calf_r"].head = kn_r
eb["calf_r"].tail = eb["foot_r"].head = an_r

bpy.ops.object.mode_set(mode="OBJECT")

# Bind AK2_Source ke Temp_Armature dengan auto weights
for o in bpy.context.view_layer.objects:
    o.select_set(False)
mesh_obj.select_set(True)
temp_arm.select_set(True)
bpy.context.view_layer.objects.active = temp_arm
bpy.ops.object.parent_set(type="ARMATURE_AUTO")

# Pose ke Manny
bpy.ops.object.mode_set(mode="POSE")

# Rotasi Lengan
for side, el, wr in [("_l", el_l, wr_l), ("_r", el_r, wr_r)]:
    pb_up = temp_arm.pose.bones["upperarm" + side]
    b_up = pb_up.bone
    v_tripo_up = el - b_up.head_local
    v_manny_up = Vector(manny["lowerarm" + side]) - Vector(manny["upperarm" + side])
    r_up_world = v_tripo_up.rotation_difference(v_manny_up)
    
    m_rest_up = b_up.matrix_local.to_3x3()
    r_up_loc = (m_rest_up.inverted() @ r_up_world.to_matrix() @ m_rest_up).to_quaternion()
    pb_up.rotation_mode = "QUATERNION"
    pb_up.rotation_quaternion = r_up_loc
    bpy.context.view_layer.update()
    
    pb_lo = temp_arm.pose.bones["lowerarm" + side]
    b_lo = pb_lo.bone
    v_tripo_lo = wr - el
    v_cur_lo = r_up_world @ v_tripo_lo
    v_manny_lo = Vector(manny["hand" + side]) - Vector(manny["lowerarm" + side])
    r_lo_world = v_cur_lo.rotation_difference(v_manny_lo)
    
    m_rest_lo = b_lo.matrix_local.to_3x3()
    r_lo_loc = (m_rest_lo.inverted() @ r_lo_world.to_matrix() @ m_rest_lo).to_quaternion()
    pb_lo.rotation_mode = "QUATERNION"
    pb_lo.rotation_quaternion = r_lo_loc
    bpy.context.view_layer.update()

# Rotasi Kaki
for side, kn, an in [("_l", kn_l, an_l), ("_r", kn_r, an_r)]:
    pb_th = temp_arm.pose.bones["thigh" + side]
    b_th = pb_th.bone
    v_tripo_th = kn - b_th.head_local
    v_manny_th = Vector(manny["calf" + side]) - Vector(manny["thigh" + side])
    r_th_world = v_tripo_th.rotation_difference(v_manny_th)
    
    m_rest_th = b_th.matrix_local.to_3x3()
    r_th_loc = (m_rest_th.inverted() @ r_th_world.to_matrix() @ m_rest_th).to_quaternion()
    pb_th.rotation_mode = "QUATERNION"
    pb_th.rotation_quaternion = r_th_loc
    bpy.context.view_layer.update()
    
    pb_ca = temp_arm.pose.bones["calf" + side]
    b_ca = pb_ca.bone
    v_tripo_ca = an - kn
    v_cur_ca = r_th_world @ v_tripo_ca
    v_manny_ca = Vector(manny["foot" + side]) - Vector(manny["calf" + side])
    r_ca_world = v_cur_ca.rotation_difference(v_manny_ca)
    
    m_rest_ca = b_ca.matrix_local.to_3x3()
    r_ca_loc = (m_rest_ca.inverted() @ r_ca_world.to_matrix() @ m_rest_ca).to_quaternion()
    pb_ca.rotation_mode = "QUATERNION"
    pb_ca.rotation_quaternion = r_ca_loc
    bpy.context.view_layer.update()

bpy.ops.object.mode_set(mode="OBJECT")

# Apply Armature modifier pada mesh_obj
bpy.context.view_layer.objects.active = mesh_obj
for mod in list(mesh_obj.modifiers):
    if mod.type == "ARMATURE":
        bpy.ops.object.modifier_apply(modifier=mod.name)

# Hapus temp_arm dan vertex groups sementara
bpy.data.objects.remove(temp_arm, do_unlink=True)
mesh_obj.vertex_groups.clear()

# ------------------------------------------------------------------ 3) Pengukuran Sendi
me = mesh_obj.data


def get_joint_center(jname, target, r=0.08):
    tv = Vector(target)
    pts = [v.co for v in me.vertices if (v.co - tv).length <= r]
    if pts:
        # Gunakan bounding center dari slice lokal jika cukup banyak vertex (mis. paha/kaki)
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        zs = [p.z for p in pts]
        return Vector(((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, sum(zs) / len(zs)))
    # fallback
    pts2 = [v.co for v in me.vertices if (v.co - tv).length <= r * 1.5]
    return sum(pts2, Vector()) / len(pts2) if pts2 else tv


JOINTS_TO_REPORT = [
    ("Bahu Kiri", "upperarm_l"),
    ("Siku Kiri", "lowerarm_l"),
    ("Pergelangan Kiri", "hand_l"),
    ("Bahu Kanan", "upperarm_r"),
    ("Siku Kanan", "lowerarm_r"),
    ("Pergelangan Kanan", "hand_r"),
    ("Pinggul Kiri", "thigh_l"),
    ("Lutut Kiri", "calf_l"),
    ("Pergelangan Kaki Kiri", "foot_l"),
    ("Pinggul Kanan", "thigh_r"),
    ("Lutut Kanan", "calf_r"),
    ("Pergelangan Kaki Kanan", "foot_r"),
    ("Leher", "neck_01"),
    ("Kepala", "head"),
]

print("=" * 80)
print(f"{'Sendi':<24} {'Manny Target (X, Y, Z)':<26} {'Mesh Fit (X, Y, Z)':<26} {'Jarak':<8}")
print("=" * 80)
results = []
for label, jname in JOINTS_TO_REPORT:
    target = manny[jname]
    mc = get_joint_center(jname, target, 0.08)
    dist_cm = (Vector(target) - mc).length * 100
    results.append((label, jname, target, mc, dist_cm))
    print(f"{label + ' (' + jname + ')':<24} {str([round(x, 3) for x in target]):<26} {str([round(x, 3) for x in mc]):<26} {dist_cm:.2f} cm")
print("=" * 80)

# Simpan blend baru
BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT), relative_remap=True)
print(f"Model berhasil difit dan disimpan ke: {BLEND_OUT}")
