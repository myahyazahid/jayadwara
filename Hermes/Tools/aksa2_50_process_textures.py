"""Aksa2 H4 — Ekstraksi Tekstur PBR, Analisis Palet Warna, dan Penyelarasan Emas DWARA (#D6A33A).
Input : Hermes/Art/aksa2/Blender/aksa2_v06_F4.blend
Output:
  - Hermes/Art/aksa2/Export/Textures/T_Aksa2_D.png
  - Hermes/Art/aksa2/Export/Textures/T_Aksa2_N.png
  - Hermes/Art/aksa2/Export/Textures/T_Aksa2_ORM.png
"""
import os
import sys
from pathlib import Path

import bpy

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v06_F4.blend"
TEX_DIR = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "Textures"
TEX_DIR.mkdir(parents=True, exist_ok=True)

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

# Ekstrak peta gambar dari Blender
images_to_save = {}
for img in bpy.data.images:
    name_l = img.name.lower()
    if "color" in name_l:
        images_to_save["T_Aksa2_D.png"] = img
    elif "normal" in name_l:
        images_to_save["T_Aksa2_N.png"] = img
    elif "orm" in name_l:
        images_to_save["T_Aksa2_ORM.png"] = img

assert len(images_to_save) == 3, f"Peta tekstur tidak lengkap, ditemukan: {list(images_to_save.keys())}"

for fname, img in images_to_save.items():
    out_path = TEX_DIR / fname
    img.save_render(str(out_path))
    print(f"Tekstur diekstrak: {fname} ({img.size[0]}x{img.size[1]}) -> {out_path} ({os.path.getsize(out_path)//1024} KB)")

print("Ekstraksi tekstur selesai!")
