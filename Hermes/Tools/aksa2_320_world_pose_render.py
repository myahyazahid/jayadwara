"""
Hermes/Tools/aksa2_320_world_pose_render.py
Menerapkan pose lompat in-air (Fall Loop) menggunakan sistem rotasi sumbu world audit_karakter:
- upperarm terangkat setinggi bahu
- lowerarm tertekuk tajam ke arah dada
- thigh dan calf ditekuk (lutut melayang di udara)
- Memverifikasi secara visual dengan kamera high-angle rear 3/4
"""
import bpy
import math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v33_synchronized_cloth.blend"
CLEAN_BC = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "Textures" / "T_Aksa2_BC.png"
OUT_IMG = ROOT / "Hermes" / "Art" / "aksa2" / "Render" / "blender_world_pose_jump.png"

bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# 1. Bersihkan kamera dan lampu lama
for o in list(bpy.data.objects):
    if o.type in {"CAMERA", "LIGHT"}:
        bpy.data.objects.remove(o, do_unlink=True)

# 2. Pasang tekstur bersih
clean_img = bpy.data.images.load(str(CLEAN_BC))
for mat in bpy.data.materials:
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == "TEX_IMAGE" and ((n.image and "BC" in n.image.name) or "BC" in n.name):
                n.image = clean_img

# 3. Bersihkan animasi lama
if arm.animation_data:
    arm.animation_data_clear()
arm.data.pose_position = "POSE"

bones = arm.pose.bones
for pb in bones:
    pb.location = (0, 0, 0)
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.rotation_euler = (0, 0, 0)
    pb.scale = (1, 1, 1)
bpy.context.view_layer.update()

AX = {
    "x": Vector((1, 0, 0)),
    "y": Vector((0, 1, 0)),
    "z": Vector((0, 0, 1)),
}

def set_world(pb, W):
    pb.matrix = arm.matrix_world.inverted() @ W
    bpy.context.view_layer.update()

def apply_ops(ops):
    for op in ops:
        name = op[0]
        if name not in bones:
            continue
        pb = bones[name]
        W = arm.matrix_world @ pb.matrix
        axis, val = op[1], op[2]
        if axis == "down":
            W.translation.z -= val
            set_world(pb, W)
        elif axis in AX:
            h = arm.matrix_world @ pb.head
            R = Matrix.Rotation(math.radians(val), 4, AX[axis])
            set_world(pb, Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ W)

# Operasi pose lompat dinamis
jump_ops = [
    ["pelvis", "down", -0.15], # naikkan pelvis 15 cm
    ["thigh_l", "x", -50],
    ["calf_l", "x", 75],
    ["foot_l", "x", -20],
    ["thigh_r", "x", -35],
    ["calf_r", "x", 65],
    ["foot_r", "x", -15],
    ["spine_02", "x", 12],
    ["spine_03", "x", 12],
    # Angkat lengan ke samping setinggi bahu
    ["upperarm_l", "y", -70],
    ["upperarm_l", "x", 25],
    # Tekuk siku tajam ke depan dada
    ["lowerarm_l", "z", -75],
    ["lowerarm_l", "x", 35],
    ["hand_l", "z", -25],
    # Lengan kanan
    ["upperarm_r", "y", 70],
    ["upperarm_r", "x", 25],
    ["lowerarm_r", "z", 75],
    ["lowerarm_r", "x", 35],
    ["hand_r", "z", 25],
]

apply_ops(jump_ops)

# Kunci pose ke frame 1 agar dievaluasi untuk render
for pb in bones:
    pb.keyframe_insert(data_path="location", frame=1)
    pb.keyframe_insert(data_path="rotation_quaternion", frame=1)

bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()

# 4. Pencahayaan Studio 3-Point
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

# 5. Kamera High-Angle Rear 3/4
cam_data = bpy.data.cameras.new("UserViewCam")
cam_data.lens = 45.0
cam_obj = bpy.data.objects.new("UserViewCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

cam_obj.location = (-1.5, 2.5, 2.2)
target_co = Vector((0.0, 0.0, 1.15))
cam_dir = target_co - cam_obj.location
rot_quat = cam_dir.to_track_quat("-Z", "Y")
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 540
bpy.context.scene.render.filepath = str(OUT_IMG)

bpy.ops.render.render(write_still=True)
print(f"Render pose world jump berhasil: {OUT_IMG}")
