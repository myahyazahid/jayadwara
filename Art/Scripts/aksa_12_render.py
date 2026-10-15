"""Aksa Iterasi 1 — render ortografis depan/samping/belakang (warna + siluet) untuk dibandingkan dengan konsep.

Headless: blender --background Art/Blender/aksa/aksa_v01_proxy.blend --python Art/Scripts/aksa_12_render.py -- <outdir> [pose]
Kanvas 760x1200 dengan skala sama seperti Art/Reference/ak_ref_*.png (1000 px = tinggi badan, telapak di y=1100, tengah di x=380),
jadi konsep (1,75 m) dan proxy (1,806 m) bisa ditumpuk langsung. Output: <outdir>/<view>_color.png, <view>_mask.png.
`pose` (opsional): nama pose di action AK_PoseTest (aksa_13_pose_tests.py) yang dirender; default pose rest.
Lanjut: python -I Art/Scripts/aksa_12_compare_sheet.py <outdir>
"""
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUTDIR = argv[0] if argv else r"C:\repository\unreal_engine\jayadwara\Art\Export"
POSE = argv[1] if len(argv) > 1 else None
H = bpy.data.collections["AK_Aksa"]["ak_height_m"]
PX_PER_M = 1000.0 / H
W, HT = 760, 1200
CAM_Z = (1100 - HT / 2) / PX_PER_M

scene = bpy.context.scene
try:                                              # daftar enum under-report; ambil dari pesan TypeError
    scene.render.engine = "BLENDER_WORKBENCH"
except TypeError as e:
    print("engine:", e)
    raise
scene.render.resolution_x, scene.render.resolution_y = W, HT
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.display.shading.light = "FLAT"
scene.display.shading.show_object_outline = False
scene.display.shading.show_specular_highlight = False
scene.display.render_aa = "8"

arm = bpy.data.objects["AK_Armature"]
if POSE:
    act = bpy.data.actions.get("AK_PoseTest")
    arm.animation_data_create()
    arm.animation_data.action = act
    scene.frame_set(int(bpy.data.actions["AK_PoseTest"]["frames"][POSE]))
for ob in bpy.data.objects:
    if ob.name.startswith("AK_REF") or ob.name.startswith("AK_LM") or ob.type == "EMPTY":
        ob.hide_render = True
        ob.hide_viewport = True
for ob in bpy.data.objects:
    if ob.type == "ARMATURE":
        ob.hide_render = True

cam_data = bpy.data.cameras.new("AK_CmpCam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = HT / PX_PER_M
cam_data.clip_start, cam_data.clip_end = 0.1, 50
cam = bpy.data.objects.new("AK_CmpCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
VIEWS = {"front": ((0, -6, CAM_Z), (90, 0, 0)), "side": ((6, 0, CAM_Z), (90, 0, 90)), "back": ((0, 6, CAM_Z), (90, 0, 180))}
os.makedirs(OUTDIR, exist_ok=True)
sh = scene.display.shading
for name, (loc, rot) in VIEWS.items():
    cam.location = loc
    cam.rotation_euler = tuple(math.radians(a) for a in rot)
    scene.world.color = (0.82, 0.82, 0.82)
    sh.background_type = "WORLD"
    sh.color_type = "VERTEX" if hasattr(sh, "color_type") else "MATERIAL"
    scene.render.filepath = os.path.join(OUTDIR, f"{name}_color.png")
    bpy.ops.render.render(write_still=True)
    scene.world.color = (0.0, 0.0, 0.0)
    sh.color_type = "SINGLE"
    sh.single_color = (1.0, 1.0, 1.0)
    scene.render.filepath = os.path.join(OUTDIR, f"{name}_mask.png")
    bpy.ops.render.render(write_still=True)
print("render selesai ->", OUTDIR)
