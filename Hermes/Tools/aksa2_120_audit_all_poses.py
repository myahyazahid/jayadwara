"""
Hermes/Tools/aksa2_120_audit_all_poses.py
Merender seluruh pose pengujian (Rest, Lompat, Jalan, Lari, Serang/Tangkis, Tangan Terangkat, Jongkok)
dari sudut depan, samping, dan tampak belakang (khusus ketiak dan lengan).
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v19_clean_arm_armpit.blend"
OUT_DIR = ROOT / "Hermes" / "Art" / "aksa2" / "Render" / "Poses"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# Setup render engine & camera
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderEngineEEVEENext') else 'BLENDER_EEVEE'
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.film_transparent = True

# Hapus kamera lama jika ada
for c in [o for o in scene.objects if o.type == 'CAMERA']:
    bpy.data.objects.remove(c, do_unlink=True)

# Tambah kamera baru
cam_data = bpy.data.cameras.new(name="AuditCam")
cam_data.lens = 50
cam_data.sensor_width = 36
cam_obj = bpy.data.objects.new("AuditCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Tambah 3-point lighting yang terang dan jelas
for l in [o for o in scene.objects if o.type == 'LIGHT']:
    bpy.data.objects.remove(l, do_unlink=True)

def add_sun(name, loc, rot, energy):
    ld = bpy.data.lights.new(name, 'SUN')
    ld.energy = energy
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    lo.rotation_euler = rot
    scene.collection.objects.link(lo)

add_sun("KeySun", (2, -3, 3), (math.radians(45), math.radians(15), math.radians(-30)), 3.0)
add_sun("FillSun", (-3, -2, 2), (math.radians(30), math.radians(-20), math.radians(45)), 1.5)
add_sun("RimSun", (0, 3, 2), (math.radians(-45), 0, math.radians(180)), 2.5)

# Reset pose
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
def reset_pose():
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()

# Helper rotasi joint
AX = {'x': Vector((1, 0, 0)), 'y': Vector((0, 1, 0)), 'z': Vector((0, 0, 1))}
def rotate_joint(pb_name, deg, axis):
    pb = arm.pose.bones.get(pb_name)
    if not pb: return
    R = Matrix.Rotation(math.radians(deg), 4, AX[axis])
    jpos = pb.matrix.translation.copy()
    pb.matrix = Matrix.Translation(jpos) @ R @ Matrix.Translation(-jpos) @ pb.matrix

def set_camera(angle_name):
    if angle_name == 'front':
        cam_obj.location = (0, -2.8, 1.1)
        cam_obj.rotation_euler = (math.radians(90), 0, 0)
    elif angle_name == 'side':
        cam_obj.location = (-2.8, 0, 1.1)
        cam_obj.rotation_euler = (math.radians(90), 0, math.radians(-90))
    elif angle_name == 'rear':
        cam_obj.location = (0, 2.8, 1.2)
        cam_obj.rotation_euler = (math.radians(90), 0, math.radians(180))
    elif angle_name == 'rear_elevated': # Sudut persis laporan user!
        cam_obj.location = (0, 2.3, 1.7)
        cam_obj.rotation_euler = (math.radians(72), 0, math.radians(180))
    elif angle_name == 'front_armpit': # Close up ketiak
        cam_obj.location = (0, -1.5, 1.35)
        cam_obj.rotation_euler = (math.radians(90), 0, 0)

# Daftar definisi pose
poses = {
    '01_rest_a_pose': [],
    '02_jump_arms_up': [
        ('pelvis', 0.05, 'down'),
        ('thigh_l', -45, 'x'), ('calf_l', 65, 'x'),
        ('thigh_r', -35, 'x'), ('calf_r', 55, 'x'),
        ('upperarm_l', -100, 'y'),
        ('upperarm_r', 100, 'y'),
        ('lowerarm_l', -40, 'x'),
        ('lowerarm_r', -40, 'x')
    ],
    '03_attack_punch': [
        ('spine_01', 15, 'z'), ('spine_02', 15, 'z'),
        ('upperarm_r', -75, 'x'), ('lowerarm_r', -80, 'x'),
        ('upperarm_l', 30, 'y'), ('lowerarm_l', -90, 'x')
    ],
    '04_arms_overhead': [
        ('upperarm_l', -120, 'y'),
        ('upperarm_r', 120, 'y'),
        ('clavicle_l', -20, 'y'),
        ('clavicle_r', 20, 'y')
    ],
    '05_crouch': [
        ('pelvis', 0.35, 'down'),
        ('thigh_l', -80, 'x'), ('calf_l', 110, 'x'),
        ('thigh_r', -80, 'x'), ('calf_r', 110, 'x'),
        ('spine_01', -20, 'x'), ('spine_02', -15, 'x'),
        ('upperarm_l', -30, 'x'), ('upperarm_r', -30, 'x')
    ]
}

rendered_files = []

for pose_name, ops in poses.items():
    reset_pose()
    for item in ops:
        bname, val, axis = item
        if axis == 'down':
            pb = arm.pose.bones.get(bname)
            if pb: pb.location.z -= val
        else:
            rotate_joint(bname, val, axis)
    bpy.context.view_layer.update()

    # Render Front
    set_camera('front')
    out_front = OUT_DIR / f"{pose_name}_front.png"
    scene.render.filepath = str(out_front)
    bpy.ops.render.render(write_still=True)
    rendered_files.append(out_front)

    # Khusus Jump dan Arms Up: render juga sudut rear_elevated dan front_armpit
    if 'jump' in pose_name or 'overhead' in pose_name:
        set_camera('rear_elevated')
        out_rear = OUT_DIR / f"{pose_name}_rear_elevated.png"
        scene.render.filepath = str(out_rear)
        bpy.ops.render.render(write_still=True)
        rendered_files.append(out_rear)

        set_camera('front_armpit')
        out_close = OUT_DIR / f"{pose_name}_close_armpit.png"
        scene.render.filepath = str(out_close)
        bpy.ops.render.render(write_still=True)
        rendered_files.append(out_close)

    print(f"Selesai render pose: {pose_name}")

print(f"Total file render berhasil dibuat: {len(rendered_files)}")
bpy.ops.wm.quit_blender()
