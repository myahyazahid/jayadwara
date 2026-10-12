"""Aksa — render badan penuh Eevee (3/4 depan, 3/4 belakang, close-up tangan & boots) untuk review pakaian.

Headless: blender --background Art/Blender/aksa_v04_outfit.blend --python Art/Scripts/aksa_31_render_body.py -- <outdir>
Output: body_q34.png, body_back.png, detail_hand.png, detail_boot.png, lalu body_sheet.png (gabungan).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else r"C:\repository\unreal_engine\jayadwara\Art\Export"
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "Standard"
sc.render.film_transparent = False
for ob in bpy.data.objects:
    if ob.name.startswith(("AK_REF", "AK_LM")) or ob.type in {"EMPTY", "ARMATURE"}:
        ob.hide_render = True
world = bpy.data.worlds.new("_body_world")
sc.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.62, 0.64, 0.68, 1)
bg.inputs["Strength"].default_value = 0.9
for name, rot, e in (("key", (55, 0, -35), 3.0), ("fill", (70, 0, 55), 1.1), ("rim", (120, 0, 160), 1.5)):
    d = bpy.data.lights.new(name, "SUN")
    d.energy = e
    d.angle = math.radians(25)
    o = bpy.data.objects.new(name, d)
    sc.collection.objects.link(o)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
cd = bpy.data.cameras.new("_bodycam")
cam = bpy.data.objects.new("_bodycam", cd)
sc.collection.objects.link(cam)
sc.camera = cam


def shot(name, loc, tgt, lens, w, h):
    cd.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


shot("body_q34", (1.9, -3.1, 1.25), (0.0, 0.0, 0.90), 50, 800, 1200)
shot("body_back", (-1.9, 3.1, 1.25), (0.0, 0.0, 0.90), 50, 800, 1200)
shot("detail_hand", (0.95, -0.55, 1.12), (0.48, -0.17, 1.00), 70, 800, 800)
shot("detail_boot", (0.75, -0.95, 0.40), (0.14, -0.03, 0.14), 60, 800, 800)
try:
    from PIL import Image  # noqa: F401
except Exception:  # noqa: BLE001
    pass
print("render badan selesai ->", OUT)
