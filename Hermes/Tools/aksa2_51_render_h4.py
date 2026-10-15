"""Aksa2 H4 — Render PBR Studio untuk Verifikasi Palet Warna & Aksesoris.
Input : Hermes/Art/aksa2/Blender/aksa2_v06_F4.blend
Output:
  - Hermes/Art/aksa2/Render/h4/render_three_quarter_front.png
  - Hermes/Art/aksa2/Render/h4/render_three_quarter_back.png
  - Hermes/Art/aksa2/Render/h4/render_head_three_quarter.png
  - Hermes/Art/aksa2/Render/h4/render_necklace.png
  - Hermes/Art/aksa2/Render/h4/render_buckle.png
  - Hermes/Art/aksa2/Render/h4/render_back_emblem.png
"""
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v06_F4.blend"
TEX_DIR = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "Textures"
OUT_DIR = ROOT / "Hermes" / "Art" / "aksa2" / "Render" / "h4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
mesh = bpy.data.objects.get("AK2_Source")
assert mesh is not None, "AK2_Source tidak ditemukan"

# 1. Konfigurasi Material PBR dengan Tekstur Tertala
mat = mesh.material_slots[0].material if mesh.material_slots else None
assert mat is not None, "Material tidak ditemukan pada mesh"
mat.name = "M_Aksa2_Body"

# Muat tekstur dari file
img_d = bpy.data.images.load(str(TEX_DIR / "T_Aksa2_D.png"))
img_n = bpy.data.images.load(str(TEX_DIR / "T_Aksa2_N.png"))
img_orm = bpy.data.images.load(str(TEX_DIR / "T_Aksa2_ORM.png"))
img_n.colorspace_settings.name = "Non-Color"
img_orm.colorspace_settings.name = "Non-Color"

nodes = mat.node_tree.nodes
links = mat.node_tree.links
bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")

# Update node images
for node in nodes:
    if node.type == "TEX_IMAGE":
        lbl = node.label.lower() or node.name.lower()
        if "normal" in lbl:
            node.image = img_n
        elif "orm" in lbl:
            node.image = img_orm
        else:
            node.image = img_d

# 2. Setup Lighting Studio
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "Standard"

for ob in bpy.data.objects:
    if ob.type in {"EMPTY", "ARMATURE"}:
        ob.hide_render = True

# Environment neutral soft grey
world = bpy.data.worlds.new("_mw_h4")
sc.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.70, 0.72, 0.75, 1)
bg.inputs["Strength"].default_value = 0.85

# Studio 3-point lights
lights_data = [
    ("Key_Front", "SUN", 3.2, (50, 0, -40)),
    ("Fill_Side", "SUN", 1.4, (65, 0, 60)),
    ("Rim_Back", "SUN", 2.2, (45, 0, 160)),
]
for name, ltype, energy, rot in lights_data:
    ld = bpy.data.lights.new(name, ltype)
    ld.energy = energy
    lo = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(lo)
    lo.rotation_euler = tuple(math.radians(a) for a in rot)

# Setup Kamera
cam_data = bpy.data.cameras.new("H4Cam")
cam_data.lens = 70.0 # Lensa 70mm natural
cam_data.clip_start = 0.01
cam_data.clip_end = 20.0
cam_obj = bpy.data.objects.new("H4Cam", cam_data)
sc.collection.objects.link(cam_obj)
sc.camera = cam_obj

def point_cam(cam, eye, target):
    cam.location = eye
    forward = (target - eye).normalized()
    up = Vector((0, 0, 1))
    right = forward.cross(up).normalized()
    up = right.cross(forward).normalized()
    R = Matrix([right, up, -forward]).transposed()
    cam.matrix_world = Matrix.Translation(eye) @ R.to_4x4()

sc.render.resolution_x = 900
sc.render.resolution_y = 1200
sc.render.image_settings.file_format = "PNG"

SHOTS = [
    # (nama_file, eye_pos, target_pos, res_x, res_y)
    ("render_three_quarter_front", Vector((1.75, -2.40, 1.15)), Vector((0.0, 0.0, 0.95)), 900, 1200),
    ("render_three_quarter_back", Vector((-1.75, 2.40, 1.15)), Vector((0.0, 0.0, 0.95)), 900, 1200),
    ("render_head_three_quarter", Vector((0.48, -0.65, 1.68)), Vector((0.0, -0.04, 1.61)), 800, 800),
    ("render_necklace", Vector((0.15, -0.52, 1.34)), Vector((0.0, -0.08, 1.30)), 800, 800),
    ("render_buckle", Vector((0.12, -0.60, 0.98)), Vector((0.0, -0.05, 0.96)), 800, 800),
    ("render_back_emblem", Vector((0.0, 0.65, 1.40)), Vector((0.0, 0.06, 1.35)), 800, 800),
]

print("=== MEMULAI RENDER H4 ===")
for name, eye, target, rx, ry in SHOTS:
    sc.render.resolution_x = rx
    sc.render.resolution_y = ry
    point_cam(cam_obj, eye, target)
    out_file = OUT_DIR / f"{name}.png"
    sc.render.filepath = str(out_file)
    bpy.ops.render.render(write_still=True)
    print(f"Render {name} selesai -> {out_file.name}")

print(f"Seluruh render H4 selesai tersimpan di: {OUT_DIR}")
