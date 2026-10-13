"""Jayadwara2 R1/R2 — render peta makro (hasil jayadwara2_10_rig_spike) berwarna: depan / samping / belakang.
  blender --background Art/Blender/jayadwara2_v02_rig_spike.blend --python Art/Scripts/jayadwara2_11_macro_render.py -- [out.png]
Hasil: <out>_front/_side/_back.png (gabungkan dengan PIL di luar Blender).
"""
import json, sys
from pathlib import Path
import bpy
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else Path(r"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2\_macro.png")
body = bpy.data.objects["JD2_Body"]
macro = json.loads(body["jd2_macro"])
COL = {"HEAD": (1, 1, 0), "TORSO": (0.2, 0.4, 1), "ARM_l": (1, 0.1, 0.1), "ARM_r": (1, 0.5, 0.1), "LEG_l": (0.1, 0.8, 0.2),
       "LEG_r": (0.1, 0.6, 0.6), "WING_l": (1, 0, 1), "WING_r": (0.6, 0, 0.8), "CLOTH": (1, 1, 1)}
me = body.data
ca = me.color_attributes.get("macro") or me.color_attributes.new("macro", "FLOAT_COLOR", "POINT")
for i, m in enumerate(macro):
    ca.data[i].color = (*COL[m], 1)
me.color_attributes.active_color = ca
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light, sh.color_type, sh.show_cavity = "FLAT", "VERTEX", False
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w"); sc.world.color = (0.3, 0.3, 0.3)
for o in bpy.data.objects:
    if o.type in {"ARMATURE", "EMPTY"}: o.hide_render = True
cam_d = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.type, cam_d.ortho_scale = "ORTHO", 2.28
sc.render.resolution_x, sc.render.resolution_y = 760, 1200
for name, loc in (("front", (0, -10, 1.055)), ("side", (10, 0, 1.055)), ("back", (0, 10, 1.055))):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector((0, 0, 1.055)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = str(OUT.with_name(f"{OUT.stem}_{name}.png")); bpy.ops.render.render(write_still=True)
print("ok", OUT.stem)
