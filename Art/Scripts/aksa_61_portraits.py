"""Aksa Iterasi 6 — potret dialog (netral, senyum, marah) untuk UI vertical slice (docs/18 bagian F, dialog = teks + potret).

Headless (file tidak disimpan): blender --background Art/Blender/aksa/aksa_v05_tex.blend --python Art/Scripts/aksa_61_portraits.py
Keluaran: Art/Export/Portraits/T_Aksa_Portrait_{Neutral,Smile,Angry}.png (1024², latar transparan, kepala-bahu 3/4 kiri).
Ekspresi = morph target yang sama dengan di game (ak_smile, ak_angry), jadi potret konsisten dengan model.
"""
import math
import os

import bpy

OUT = r"C:\repository\unreal_engine\jayadwara\Art\Export\Portraits"
os.makedirs(OUT, exist_ok=True)
EXPR = {"Neutral": {}, "Smile": {"ak_smile": 0.85}, "Angry": {"ak_angry": 1.0, "ak_wince": 0.25}}

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "Standard"
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = 1024
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
for ob in bpy.data.objects:
    if ob.name.startswith(("AK_REF", "AK_LM")) or ob.type in {"EMPTY", "LIGHT"}:
        ob.hide_render = True
w = bpy.data.worlds.new("_pw")
sc.world = w
w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.55, 0.57, 0.62, 1)
bg.inputs["Strength"].default_value = 0.7
for name, rot, e, col in (("_key", (60, 0, -40), 3.2, (1.0, 0.95, 0.88)), ("_fill", (75, 0, 50), 1.0, (0.85, 0.9, 1.0)),
                          ("_rim", (110, 0, 160), 2.2, (1.0, 0.9, 0.75))):
    d = bpy.data.lights.new(name, "SUN")
    d.energy = e
    d.color = col
    o = bpy.data.objects.new(name, d)
    sc.collection.objects.link(o)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
cam = bpy.data.objects.new("_pcam", bpy.data.cameras.new("_pcam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 85
cam.location = (0.36, -0.98, 1.63)
cam.rotation_euler = (math.radians(91), 0, math.radians(18))
keyed = [o for o in bpy.data.objects if o.type == "MESH" and o.data.shape_keys and o.name.startswith(("AK_Head", "AK_Brows"))]
for name, vals in EXPR.items():
    for o in keyed:
        for kb in o.data.shape_keys.key_blocks[1:]:
            kb.value = vals.get(kb.name, 0.0)
    sc.render.filepath = os.path.join(OUT, f"T_Aksa_Portrait_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("potret:", sc.render.filepath)
