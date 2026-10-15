"""
Hermes/Tools/aksa2_290_blender_render_user_jump.py
Merender pose lompat (Fall Loop) pada aksa2_v33_synchronized_cloth.blend di Blender:
- Pose: Siku terbuka ke samping setinggi bahu, lengan bawah dan tangan tertekuk ke dada, lutut ditekuk.
- Kamera: High-angle rear 3/4 menyerong dari belakang-kiri atas persis seperti screenshot pengguna.
- Tata cahaya: 3-point studio lighting (Key, Fill, Rim) agar tidak ada bayangan gelap yang membingungkan.
- Menguji integritas mesh (robekan, ketiak, bahu, siku, pergelangan tangan).
"""
import bpy
import math
from pathlib import Path
from mathutils import Vector, Euler

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v33_synchronized_cloth.blend"
OUT_IMG = ROOT / "Hermes" / "Art" / "aksa2" / "Render" / "blender_user_jump_verified.png"

bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# 1. Bersihkan kamera dan lampu lama
for o in list(bpy.data.objects):
    if o.type in {"CAMERA", "LIGHT"}:
        bpy.data.objects.remove(o, do_unlink=True)

# 2. Terapkan Pose Lompat (In-Air / Fall Loop)
for o in bpy.context.view_layer.objects:
    o.select_set(False)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")

# Rotasi tulang membentuk pose persis screenshot pengguna
pose_ops = [
    # Pelvis & Tulang Belakang
    ("pelvis", (math.radians(-5), math.radians(0), math.radians(0))),
    ("spine_01", (math.radians(5), math.radians(0), math.radians(0))),
    ("spine_02", (math.radians(5), math.radians(0), math.radians(0))),
    ("spine_03", (math.radians(5), math.radians(0), math.radians(0))),
    # Kaki Ditekuk Melayang
    ("thigh_l", (math.radians(-45), math.radians(-15), math.radians(10))),
    ("calf_l", (math.radians(65), math.radians(0), math.radians(0))),
    ("foot_l", (math.radians(-20), math.radians(0), math.radians(0))),
    ("thigh_r", (math.radians(-30), math.radians(15), math.radians(-10))),
    ("calf_r", (math.radians(55), math.radians(0), math.radians(0))),
    ("foot_r", (math.radians(-10), math.radians(0), math.radians(0))),
    # Lengan: Siku terbuka ke samping setinggi bahu, lengan bawah tertekuk ke dada
    ("clavicle_l", (math.radians(0), math.radians(-10), math.radians(10))),
    ("upperarm_l", (math.radians(25), math.radians(-75), math.radians(35))),
    ("lowerarm_l", (math.radians(85), math.radians(0), math.radians(40))),
    ("hand_l", (math.radians(25), math.radians(0), math.radians(-20))),
    ("clavicle_r", (math.radians(0), math.radians(10), math.radians(-10))),
    ("upperarm_r", (math.radians(25), math.radians(75), math.radians(-35))),
    ("lowerarm_r", (math.radians(85), math.radians(0), math.radians(-40))),
    ("hand_r", (math.radians(25), math.radians(0), math.radians(20))),
]

for bname, rot_euler in pose_ops:
    pb = arm.pose.bones.get(bname)
    if pb:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = rot_euler

bpy.context.view_layer.update()

# 3. Tata Cahaya 3-Point Studio
# Key Light (depan-kanan atas)
key_light = bpy.data.lights.new("KeyLight", type="SUN")
key_light.energy = 3.0
key_obj = bpy.data.objects.new("KeyLight", key_light)
key_obj.location = (2.0, -3.0, 4.0)
key_obj.rotation_euler = (math.radians(45), math.radians(0), math.radians(30))
bpy.context.scene.collection.objects.link(key_obj)

# Fill Light (belakang-kiri atas menerangi punggung dan bahu)
fill_light = bpy.data.lights.new("FillLight", type="SUN")
fill_light.energy = 2.0
fill_obj = bpy.data.objects.new("FillLight", fill_light)
fill_obj.location = (-2.0, 3.0, 3.5)
fill_obj.rotation_euler = (math.radians(-40), math.radians(0), math.radians(-140))
bpy.context.scene.collection.objects.link(fill_obj)

# Rim Light (atas lurus menerangi garis bahu dan rambut)
rim_light = bpy.data.lights.new("RimLight", type="SUN")
rim_light.energy = 2.5
rim_obj = bpy.data.objects.new("RimLight", rim_light)
rim_obj.location = (0.0, 0.0, 5.0)
rim_obj.rotation_euler = (math.radians(0), math.radians(0), math.radians(0))
bpy.context.scene.collection.objects.link(rim_obj)

# Atur World Background agar terang lembut (tidak gelap gulita)
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.8, 0.85, 0.9, 1.0)
    bg_node.inputs[1].default_value = 1.0

# 4. Kamera High-Angle Rear 3/4 persis sudut screenshot pengguna
cam_data = bpy.data.cameras.new("UserViewCam")
cam_data.lens = 50.0
cam_obj = bpy.data.objects.new("UserViewCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Karakter menghadap ke -Y, punggung di +Y
# Screenshot pengguna: kamera di belakang-kiri atas menghadap ke depan-kanan bawah
cam_obj.location = (-1.4, 2.4, 2.2)
target_co = Vector((0.0, 0.0, 1.1))
cam_dir = target_co - cam_obj.location
rot_quat = cam_dir.to_track_quat("-Z", "Y")
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 540
bpy.context.scene.render.filepath = str(OUT_IMG)

# Render menggunakan Eevee
bpy.ops.render.render(write_still=True)
print(f"Render verifikasi pose lompat berhasil: {OUT_IMG}")
