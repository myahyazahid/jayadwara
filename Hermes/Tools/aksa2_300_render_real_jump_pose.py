"""
Hermes/Tools/aksa2_300_render_real_jump_pose.py
Merender pose lompat sesungguhnya (In-Air Jump / Fall Loop):
- Membersihkan animation_data lama agar pose manual tidak tertimpa.
- Mengganti tekstur lama ke tekstur bersih (T_Aksa2_BC.png hasil inpaint bebas noda putih).
- Menerapkan rotasi tulang: Siku terbuka ke samping setinggi bahu, lengan bawah dan tangan tertekuk ke dada, lutut ditekuk melayang di udara.
- Kamera high-angle rear 3/4 membingkai seluruh tubuh persis sudut pandang screenshot pengguna.
"""
import bpy
import math
from pathlib import Path
from mathutils import Vector, Euler

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v33_synchronized_cloth.blend"
CLEAN_BC = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "Textures" / "T_Aksa2_BC.png"
OUT_IMG = ROOT / "Hermes" / "Art" / "aksa2" / "Render" / "blender_real_jump_pose.png"

bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# 1. Bersihkan kamera dan lampu lama
for o in list(bpy.data.objects):
    if o.type in {"CAMERA", "LIGHT"}:
        bpy.data.objects.remove(o, do_unlink=True)

# 2. Pasang tekstur Base Color bersih (inpaint 39k px putih)
clean_img = bpy.data.images.load(str(CLEAN_BC))
for mat in bpy.data.materials:
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == "TEX_IMAGE" and ((n.image and "BC" in n.image.name) or "BC" in n.name):
                n.image = clean_img
                print(f"Mengganti node {n.name} di material {mat.name} ke {clean_img.name}")

# 3. Hapus animation_data lama agar pose tidak tertimpa
arm.animation_data_clear()

# 4. Terapkan Pose Lompat (In-Air / Fall Loop)
for o in bpy.context.view_layer.objects:
    o.select_set(False)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")

# Rotasi tulang membentuk pose persis screenshot pengguna
pose_ops = [
    # Pelvis & Tulang Belakang (condong sedikit ke depan khas lompatan)
    ("pelvis", (math.radians(-10), math.radians(0), math.radians(0))),
    ("spine_01", (math.radians(10), math.radians(0), math.radians(0))),
    ("spine_02", (math.radians(10), math.radians(0), math.radians(0))),
    ("spine_03", (math.radians(10), math.radians(0), math.radians(0))),
    # Kaki Ditekuk Melayang
    ("thigh_l", (math.radians(-50), math.radians(-20), math.radians(15))),
    ("calf_l", (math.radians(75), math.radians(0), math.radians(0))),
    ("foot_l", (math.radians(-25), math.radians(0), math.radians(0))),
    ("thigh_r", (math.radians(-35), math.radians(20), math.radians(-15))),
    ("calf_r", (math.radians(65), math.radians(0), math.radians(0))),
    ("foot_r", (math.radians(-15), math.radians(0), math.radians(0))),
    # Lengan: Siku terbuka ke samping setinggi bahu, lengan bawah dan tangan tertekuk ke dada
    ("clavicle_l", (math.radians(5), math.radians(-15), math.radians(15))),
    ("upperarm_l", (math.radians(30), math.radians(-75), math.radians(45))),
    ("lowerarm_l", (math.radians(95), math.radians(0), math.radians(50))),
    ("hand_l", (math.radians(30), math.radians(0), math.radians(-25))),
    ("clavicle_r", (math.radians(5), math.radians(15), math.radians(-15))),
    ("upperarm_r", (math.radians(30), math.radians(75), math.radians(-45))),
    ("lowerarm_r", (math.radians(95), math.radians(0), math.radians(-50))),
    ("hand_r", (math.radians(30), math.radians(0), math.radians(25))),
]

for bname, rot_euler in pose_ops:
    pb = arm.pose.bones.get(bname)
    if pb:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = rot_euler

bpy.context.view_layer.update()

# 5. Tata Cahaya 3-Point Studio Lembut
key_light = bpy.data.lights.new("KeyLight", type="SUN")
key_light.energy = 3.5
key_obj = bpy.data.objects.new("KeyLight", key_light)
key_obj.location = (2.0, -3.0, 4.0)
key_obj.rotation_euler = (math.radians(45), math.radians(0), math.radians(35))
bpy.context.scene.collection.objects.link(key_obj)

fill_light = bpy.data.lights.new("FillLight", type="SUN")
fill_light.energy = 2.5
fill_obj = bpy.data.objects.new("FillLight", fill_light)
fill_obj.location = (-2.0, 3.0, 3.5)
fill_obj.rotation_euler = (math.radians(-40), math.radians(0), math.radians(-135))
bpy.context.scene.collection.objects.link(fill_obj)

rim_light = bpy.data.lights.new("RimLight", type="SUN")
rim_light.energy = 2.0
rim_obj = bpy.data.objects.new("RimLight", rim_light)
rim_obj.location = (0.0, 0.0, 5.0)
rim_obj.rotation_euler = (math.radians(0), math.radians(0), math.radians(0))
bpy.context.scene.collection.objects.link(rim_obj)

world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.75, 0.8, 0.88, 1.0)
    bg_node.inputs[1].default_value = 1.0

# 6. Kamera High-Angle Rear 3/4
cam_data = bpy.data.cameras.new("UserViewCam")
cam_data.lens = 45.0
cam_obj = bpy.data.objects.new("UserViewCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Kamera di belakang-kiri atas membingkai seluruh tubuh
cam_obj.location = (-1.6, 2.6, 2.4)
target_co = Vector((0.0, 0.0, 1.05))
cam_dir = target_co - cam_obj.location
rot_quat = cam_dir.to_track_quat("-Z", "Y")
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 540
bpy.context.scene.render.filepath = str(OUT_IMG)

bpy.ops.render.render(write_still=True)
print(f"Render pose lompat nyata berhasil: {OUT_IMG}")
