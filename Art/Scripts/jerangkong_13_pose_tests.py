"""Jerangkong (jalur B) — uji pose potongan kaku (docs/20 Iterasi 1/3) + render lembar pose.

Headless: blender --background Art/Blender/jerangkong_v02_rig.blend --python Art/Scripts/jerangkong_13_pose_tests.py -- <outdir>
Membuat aksi JK_PoseTest (frame 1..N, satu pose per frame) di JK_Armature, merender tiap pose (Eevee, 3/4 depan)
ke <outdir>/jk_pose_<n>_<nama>.png. File .blend TIDAK disimpan.
Rotasi ditulis sebagai (sumbu dunia, derajat) dan diubah ke ruang lokal tiap tulang terhadap pose rest.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = r"C:\repository\unreal_engine\jayadwara"
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUTDIR = argv[0] if argv else os.path.join(ROOT, "Art", "Export", "_poses")
os.makedirs(OUTDIR, exist_ok=True)

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
POSES = [
    ("rest", {}),
    ("idle_bungkuk", {"spine_03": (X, 8), "spine_05": (X, 8), "neck_01": (X, 10), "upperarm_l": (Y, -6), "upperarm_r": (Y, 6)}),
    ("sapuan", {"spine_03": (Z, 25), "upperarm_r": (X, 75), "lowerarm_r": (X, 20), "clavicle_r": (X, 10),
                "upperarm_l": (X, -20)}),
    ("hantaman", {"upperarm_l": (X, 160), "upperarm_r": (X, 160), "lowerarm_l": (X, 30), "lowerarm_r": (X, 30),
                  "spine_03": (X, -10), "jaw": (X, -20)}),
    ("lempar", {"upperarm_r": (X, -60), "lowerarm_r": (X, 70), "spine_03": (Z, -25), "thigh_l": (X, 25), "calf_l": (X, -30)}),
    ("roboh", {"pelvis": (X, 35), "thigh_l": (X, 70), "thigh_r": (X, 60), "calf_l": (X, -110), "calf_r": (X, -100),
               "spine_03": (X, 20), "neck_01": (X, 20), "upperarm_l": (Y, -20), "upperarm_r": (Y, 20)}),
    ("raungan", {"jaw": (X, -28), "head": (X, -25), "neck_01": (X, -10), "upperarm_l": (Y, -35), "upperarm_r": (Y, 35),
                 "lowerarm_l": (X, 40), "lowerarm_r": (X, 40)}),
]

sc = bpy.context.scene
arm = bpy.data.objects["JK_Armature"]
arm.animation_data_create()
act = bpy.data.actions.get("JK_PoseTest") or bpy.data.actions.new("JK_PoseTest")
arm.animation_data.action = act
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"

for fi, (name, rots) in enumerate(POSES, start=1):
    for pb in arm.pose.bones:
        pb.rotation_quaternion = Quaternion()
        pb.location = Vector()
    for bn, (axis, deg) in rots.items():
        pb = arm.pose.bones[bn]
        rest = pb.bone.matrix_local.to_3x3()
        # sumbu dunia (karakter menghadap -Y): rotasi +X membungkuk ke depan untuk tulang yang mengarah ke atas
        ax_local = rest.inverted() @ Vector(axis)
        pb.rotation_quaternion = Quaternion(ax_local, math.radians(-deg if axis == X else deg))
    for pb in arm.pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=fi)
        pb.keyframe_insert("location", frame=fi)

# kamera & cahaya
cam = bpy.data.objects.get("JK_PoseCam") or bpy.data.objects.new("JK_PoseCam", bpy.data.cameras.new("JK_PoseCam"))
if cam.name not in sc.collection.objects:
    sc.collection.objects.link(cam)
cam.data.type = "ORTHO"
cam.data.ortho_scale = 3.0
tgt = Vector((0, 0, 1.15))
d = Vector((math.sin(math.radians(-35)), -math.cos(math.radians(-35)), 0.18)).normalized()
cam.location = tgt + d * 8
cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
sun = bpy.data.objects.get("JK_PoseSun") or bpy.data.objects.new("JK_PoseSun", bpy.data.lights.new("JK_PoseSun", "SUN"))
if sun.name not in sc.collection.objects:
    sc.collection.objects.link(sun)
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
for o in sc.objects:
    if o.type == "EMPTY" or o.name == "JK_Source":
        o.hide_render = True
world = sc.world or bpy.data.worlds.new("W")
sc.world = world
world.use_nodes = True
bgn = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bgn.inputs[0].default_value = (0.05, 0.05, 0.06, 1)
bgn.inputs[1].default_value = 0.6
try:
    sc.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 520, 640
sc.render.film_transparent = False
sc.view_settings.view_transform = "Standard"
paths = []
for fi, (name, _r) in enumerate(POSES, start=1):
    sc.frame_set(fi)
    sc.render.filepath = os.path.join(OUTDIR, f"jk_pose_{fi}_{name}.png")
    bpy.ops.render.render(write_still=True)
    paths.append(sc.render.filepath)
print("POSES", ";".join(paths))
