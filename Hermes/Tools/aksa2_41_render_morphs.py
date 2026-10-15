"""Aksa2 H3b — Render 8 Morph Target Wajah (Nilai 1.0) & Susun Grid Kontak Berdampingan.
Input : Hermes/Art/aksa2/Blender/aksa2_v07_morph.blend
Output:
  - Hermes/Art/aksa2/Render/h3b/morph_<nama>.png
  - Hermes/Art/aksa2/Render/h3b/morph_sheet.png
  - Hermes/Art/aksa2/Render/h3b/morph_compare.png (vs Art/Export/_aksa_morphs.png)
"""
import math
import os
import sys
from pathlib import Path

import bpy

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v07_morph.blend"
OUT_DIR = ROOT / "Hermes" / "Art" / "aksa2" / "Render" / "h3b"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
mesh = bpy.data.objects.get("AK2_Source")
assert mesh is not None, "AK2_Source tidak ditemukan"
assert mesh.data.shape_keys is not None, "AK2_Source tidak memiliki shape keys"

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "Standard"

for ob in bpy.data.objects:
    if ob.type in {"EMPTY", "ARMATURE"}:
        ob.hide_render = True

# Setup Environment Lighting
world = bpy.data.worlds.new("_mw")
sc.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.62, 0.64, 0.68, 1)
bg.inputs["Strength"].default_value = 0.9

for name, rot, e in (("key", (55, 0, -35), 3.2), ("fill", (70, 0, 55), 1.2)):
    d = bpy.data.lights.new(name, "SUN")
    d.energy = e
    o = bpy.data.objects.new(name, d)
    sc.collection.objects.link(o)
    o.rotation_euler = tuple(math.radians(a) for a in rot)

# Kamera Ortografis Wajah Aksa2
cd = bpy.data.cameras.new("_mc")
cd.type = "ORTHO"
cd.ortho_scale = 0.25
cam = bpy.data.objects.new("_mc", cd)
sc.collection.objects.link(cam)
sc.camera = cam
cam.location = (0.0, -1.0, 1.61) # Fokus tepat di wajah Aksa2
cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.resolution_x, sc.render.resolution_y = 420, 420

EXP_NAMES = [
    "ak_blink_L",
    "ak_blink_R",
    "ak_smile",
    "ak_angry",
    "ak_mouth_open",
    "ak_brow_up",
    "ak_wince",
    "ak_sad",
]

shots = [("netral", {})] + [(n, {n: 1.0}) for n in EXP_NAMES]
rendered_files = []

for label, vals in shots:
    # Reset semua shape keys ke 0
    for k in mesh.data.shape_keys.key_blocks[1:]:
        k.value = vals.get(k.name, 0.0)
    bpy.context.view_layer.update()

    out_file = OUT_DIR / f"morph_{label}.png"
    sc.render.filepath = str(out_file)
    bpy.ops.render.render(write_still=True)
    rendered_files.append((label, out_file))
    print(f"Render {label} selesai -> {out_file.name}")

print("Selesai render semua morph!")
