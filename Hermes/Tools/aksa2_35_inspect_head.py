"""Aksa2 H3b — Inspeksi Geometri Kepala & Render Close-Up Wajah.
Input : Hermes/Art/aksa2/Blender/aksa2_v06_F4.blend
Output:
  - Data kuantitatif topologi mata, mulut, dan wajah
  - Hermes/Art/aksa2/Render/h3b/head_front.png
  - Hermes/Art/aksa2/Render/h3b/head_side.png
  - Hermes/Art/aksa2/Render/h3b/head_three_quarter.png
  - Hermes/Art/aksa2/Render/h3b/head_wire.png
"""
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v06_F4.blend"
OUT_DIR = ROOT / "Hermes" / "Art" / "aksa2" / "Render" / "h3b"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
mesh = bpy.data.objects.get("AK2_Source")
assert mesh is not None, "Objek AK2_Source tidak ditemukan"

# 1. Analisis Kuantitatif Topologi Kepala (z >= 1.45)
me = mesh.data
bm = bmesh.new()
bm.from_mesh(me)

head_verts = [v for v in bm.verts if v.co.z >= 1.45]
face_verts = [v for v in head_verts if v.co.y < 0.0] # Wajah depan (menghadap -Y)
eye_verts = [v for v in face_verts if 1.58 <= v.co.z <= 1.66 and abs(v.co.x) <= 0.08]
mouth_verts = [v for v in face_verts if 1.48 <= v.co.z <= 1.55 and abs(v.co.x) <= 0.06]

# Cek pulau mesh terpisah (connected components)
visited = set()
islands = []
for v in bm.verts:
    if v not in visited:
        island = []
        q = [v]
        visited.add(v)
        while q:
            cur = q.pop()
            island.append(cur)
            for e in cur.link_edges:
                other = e.other_vert(cur)
                if other not in visited:
                    visited.add(other)
                    q.append(other)
        islands.append(island)

print(f"=== ANALISIS TOPOLOGI KEPALA ===")
print(f"Total vertex mesh: {len(bm.verts)}")
print(f"Total vertex kepala (Z >= 1.45 m): {len(head_verts)}")
print(f"Total vertex wajah depan (Z >= 1.45 m, Y < 0): {len(face_verts)}")
print(f"Total vertex area mata (1.58 <= Z <= 1.66, |X| <= 0.08): {len(eye_verts)}")
print(f"Total vertex area mulut (1.48 <= Z <= 1.55, |X| <= 0.06): {len(mouth_verts)}")
print(f"Jumlah pulau mesh terpisah (islands): {len(islands)}")
for idx, isl in enumerate(islands):
    zs = [v.co.z for v in isl]
    print(f"  Pulau {idx+1}: {len(isl)} vertex, Z range [{min(zs):.3f}, {max(zs):.3f}] m")

# Cek apakah ada lubang / celah bibir / kelopak mata terbuka
boundary_edges = [e for e in bm.edges if e.is_boundary]
head_boundaries = [e for e in boundary_edges if (e.verts[0].co.z >= 1.45 or e.verts[1].co.z >= 1.45)]
print(f"Tepi terbuka (boundary edges) di kepala: {len(head_boundaries)}")

bm.free()

# 2. Setup Kamera Close-up Kepala
# Target fokus: wajah Aksa (0.0, -0.06, 1.61)
focus_pt = Vector((0.0, -0.06, 1.61))

cam_data = bpy.data.cameras.new("HeadCam")
cam_data.lens = 85.0 # Lensa portrait 85mm tanpa distorsi
cam_data.clip_start = 0.01
cam_data.clip_end = 10.0
cam_obj = bpy.data.objects.new("HeadCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

scene = bpy.context.scene
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"

# Pencahayaan Studio Wajah 3 Titik
light_data_key = bpy.data.lights.new("KeyLight", type="SUN")
light_data_key.energy = 3.5
light_key = bpy.data.objects.new("KeyLight", light_data_key)
light_key.location = Vector((0.8, -1.2, 2.2))
bpy.context.scene.collection.objects.link(light_key)

light_data_fill = bpy.data.lights.new("FillLight", type="SUN")
light_data_fill.energy = 1.5
light_fill = bpy.data.objects.new("FillLight", light_data_fill)
light_fill.location = Vector((-0.8, -1.0, 1.8))
bpy.context.scene.collection.objects.link(light_fill)

def point_camera(cam, target):
    loc = cam.location
    forward = (target - loc).normalized()
    up = Vector((0, 0, 1))
    right = forward.cross(up).normalized()
    up = right.cross(forward).normalized()
    R = Matrix([right, up, -forward]).transposed()
    cam.matrix_world = Matrix.Translation(loc) @ R.to_4x4()

# A. Render Close-up Depan
cam_obj.location = focus_pt + Vector((0.0, -0.75, 0.02))
point_camera(cam_obj, focus_pt)
scene.render.filepath = str(OUT_DIR / "head_front.png")
bpy.ops.render.render(write_still=True)
print("Render head_front selesai.")

# B. Render Close-up Samping (Profil Kiri)
cam_obj.location = focus_pt + Vector((0.75, 0.0, 0.02))
point_camera(cam_obj, focus_pt)
scene.render.filepath = str(OUT_DIR / "head_side.png")
bpy.ops.render.render(write_still=True)
print("Render head_side selesai.")

# C. Render Close-up 3/4
cam_obj.location = focus_pt + Vector((0.55, -0.55, 0.08))
point_camera(cam_obj, focus_pt)
scene.render.filepath = str(OUT_DIR / "head_three_quarter.png")
bpy.ops.render.render(write_still=True)
print("Render head_three_quarter selesai.")

# D. Render Wireframe / Shaded
mesh.show_wire = True
mesh.show_all_edges = True
bpy.context.view_layer.update()
scene.render.filepath = str(OUT_DIR / "head_wire.png")
bpy.ops.render.render(write_still=True)
print("Render head_wire selesai.")

print(f"Seluruh render inspeksi kepala tersimpan di: {OUT_DIR}")
