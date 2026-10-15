"""Aksa Iterasi 4 — render semua morph target wajah (nilai 1.0) berdampingan dengan netral.

Headless: blender --background Art/Blender/aksa/aksa_v04_outfit.blend --python Art/Scripts/aksa_41_render_morphs.py -- <outdir>
Output: <outdir>/morph_<nama>.png; grid: python -I Art/Scripts/aksa_41_morph_sheet.py <outdir>.
Kamera ortografis depan memotong wajah (skala sama dengan aksa_21_render_head.py).
"""
import math
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else r"C:\repository\unreal_engine\jayadwara\Art\Export"
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "Standard"
for ob in bpy.data.objects:
    if ob.name.startswith(("AK_REF", "AK_LM")) or ob.type in {"EMPTY", "ARMATURE"}:
        ob.hide_render = True
world = bpy.data.worlds.new("_mw")
sc.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.62, 0.64, 0.68, 1)
bg.inputs["Strength"].default_value = 0.9
for name, rot, e in (("key", (55, 0, -35), 3.0), ("fill", (70, 0, 55), 1.1)):
    d = bpy.data.lights.new(name, "SUN")
    d.energy = e
    o = bpy.data.objects.new(name, d)
    sc.collection.objects.link(o)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
cd = bpy.data.cameras.new("_mc")
cd.type = "ORTHO"
cd.ortho_scale = 0.23
cam = bpy.data.objects.new("_mc", cd)
sc.collection.objects.link(cam)
sc.camera = cam
cam.location = (0.0, -1.0, 1.655)
cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.resolution_x, sc.render.resolution_y = 420, 420
head, brows = bpy.data.objects["AK_Head"], bpy.data.objects["AK_Brows"]
names = [k.name for k in head.data.shape_keys.key_blocks][1:]
shots = [("netral", {})] + [(n, {n: 1.0}) for n in names]
files = []
for label, vals in shots:
    for o in (head, brows):
        for k in o.data.shape_keys.key_blocks[1:]:
            k.value = vals.get(k.name, 0.0)
    sc.render.filepath = os.path.join(OUT, f"morph_{label}.png")
    bpy.ops.render.render(write_still=True)
    files.append((label, sc.render.filepath))
print("morph dirender:", [l for l, _ in files])
