"""Aksa2 H0 — render ortografis depan/samping/belakang (warna + siluet) untuk dibandingkan dengan konsep.

Headless:
  "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background Hermes/Art/aksa2/Blender/aksa2_v01_intake.blend --python Hermes/Tools/aksa2_02_render.py -- Hermes/Art/aksa2/Render/h0
Kanvas 760x1200 dengan skala sama seperti Art/Reference/ak_ref_*.png (1000 px = tinggi badan, telapak di y=1100, tengah di x=380).
Output: <outdir>/<view>_color.png, <view>_mask.png.
"""
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if argv:
    OUTDIR = str((ROOT / argv[0]).resolve() if not Path(argv[0]).is_absolute() else Path(argv[0]).resolve())
else:
    OUTDIR = str((ROOT / "Hermes" / "Art" / "aksa2" / "Render" / "h0").resolve())
POSE = argv[1] if len(argv) > 1 else None

coll = bpy.data.collections.get("AK2_Aksa") or bpy.data.collections.get("AK_Aksa")
H = coll.get("ak_height_m", 1.806) if coll else 1.806
PX_PER_M = 1000.0 / H
W, HT = 760, 1200
CAM_Z = (1100 - HT / 2) / PX_PER_M

scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_WORKBENCH"
except TypeError as e:
    print("engine:", e)
    raise

scene.render.resolution_x, scene.render.resolution_y = W, HT
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.display.shading.light = "STUDIO"
scene.display.shading.show_object_outline = False
scene.display.shading.show_specular_highlight = False
scene.display.render_aa = "8"

arm = bpy.data.objects.get("AK2_Armature") or bpy.data.objects.get("AK_Armature")
if arm and POSE:
    act = bpy.data.actions.get("AK_PoseTest") or bpy.data.actions.get("AK2_PoseTest")
    if act:
        arm.animation_data_create()
        arm.animation_data.action = act
        scene.frame_set(int(act["frames"][POSE]))

for ob in bpy.data.objects:
    if ob.name.startswith("AK_REF") or ob.name.startswith("AK_LM") or ob.name.startswith("AK2_REF") or ob.type == "EMPTY":
        ob.hide_render = True
        ob.hide_viewport = True
    if ob.type == "ARMATURE":
        ob.hide_render = True

cam_data = bpy.data.cameras.new("AK2_CmpCam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = HT / PX_PER_M
cam_data.clip_start, cam_data.clip_end = 0.1, 50
cam = bpy.data.objects.new("AK2_CmpCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

VIEWS = {
    "front": ((0, -6, CAM_Z), (90, 0, 0)),
    "side": ((6, 0, CAM_Z), (90, 0, 90)),
    "back": ((0, 6, CAM_Z), (90, 0, 180)),
}
os.makedirs(OUTDIR, exist_ok=True)
sh = scene.display.shading

imgs = [i for i in bpy.data.images if i.type == "IMAGE" and i.users and i.name != "Render Result"]
color_mode = "TEXTURE" if imgs else "MATERIAL"

for name, (loc, rot) in VIEWS.items():
    cam.location = loc
    cam.rotation_euler = tuple(math.radians(a) for a in rot)
    
    # Render Color
    scene.world.color = (0.82, 0.82, 0.82)
    sh.background_type = "WORLD"
    sh.light = "STUDIO"
    sh.color_type = color_mode
    scene.render.filepath = os.path.join(OUTDIR, f"{name}_color.png")
    bpy.ops.render.render(write_still=True)
    
    # Render Mask
    scene.world.color = (0.0, 0.0, 0.0)
    sh.light = "FLAT"
    sh.color_type = "SINGLE"
    sh.single_color = (1.0, 1.0, 1.0)
    scene.render.filepath = os.path.join(OUTDIR, f"{name}_mask.png")
    bpy.ops.render.render(write_still=True)

print("render selesai ->", OUTDIR)
