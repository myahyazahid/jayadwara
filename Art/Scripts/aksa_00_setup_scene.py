"""Iterasi 0 (docs/19, docs/21) — setup scene Blender untuk model Aksa.

Jalankan di Blender 5.2 (headless: blender --background --factory-startup --python Art/Scripts/aksa_00_setup_scene.py,
atau lewat MCP: exec(open(path).read())). Membuat: satuan metrik, hierarki collection, reference plane
(depan/samping/belakang), penanda landmark proporsi, penggaris 1,75 m. Lalu menyimpan aksa_v00_setup.blend.

Nilai proporsi dari docs/21-model-sheet-aksa.md (H = 1,75 m, telapak sepatu -> ujung rambut).
Script ini hanya membuat basis scene; jangan dijalankan ulang di atas file yang sudah dimodel.
"""
import math
from pathlib import Path

import bpy

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
REF = ROOT / "Art" / "Reference"
OUT = ROOT / "Art" / "Blender" / "aksa_v00_setup.blend"

H = 1.75                       # tinggi badan (m), telapak sepatu -> ujung rambut tertinggi
CANVAS_PX = (760, 1200)        # ukuran reference plane (px); 1000 px = 1,75 m
SOLE_PX_FROM_TOP = 1100
PLANE_SIZE = H * CANVAS_PX[1] / 1000.0      # sisi terpanjang gambar (m) = 2,10 m
PLANE_DIST = 0.6               # jarak plane dari titik tengah (m)

scene = bpy.context.scene

# --- 1. bersihkan objek default (Cube) ----------------------------------------------------
for ob in list(scene.objects):
    if ob.type == "MESH" and ob.name.startswith("Cube"):
        bpy.data.objects.remove(ob, do_unlink=True)

# --- 2. satuan ----------------------------------------------------------------------------
us = scene.unit_settings
us.system = "METRIC"
us.scale_length = 1.0
us.length_unit = "METERS"


# --- 3. collection ------------------------------------------------------------------------
def make_collection(name, parent):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in parent.children:
        parent.children.link(c)
    return c


root_coll = make_collection("AK_Aksa", scene.collection)
root_coll["ak_height_m"] = H
root_coll["ak_unit"] = "1 unit Blender = 1 m"
root_coll["ak_source"] = "docs/concept-art/aksa_turnaround_v01.webp"
root_coll["ak_modelsheet"] = "docs/21-model-sheet-aksa.md"

COLL_NAMES = [
    "00_REF", "01_Body", "02_Head", "03_Hair", "04_Top", "05_Bottom",
    "06_Accessory", "07_Shoes", "08_Rig", "09_Sockets",
]
coll = {n: make_collection(n, root_coll) for n in COLL_NAMES}
scene_coll = make_collection("_Scene", scene.collection)

for ob in scene.objects:                       # Camera & Light ke _Scene
    if ob.type in {"CAMERA", "LIGHT"}:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        scene_coll.objects.link(ob)


# --- 4. reference plane -------------------------------------------------------------------
def set_enum(obj, prop, wanted):
    """Set enum hanya jika identifier valid (jangan hardcode buta)."""
    valid = [i.identifier for i in obj.bl_rna.properties[prop].enum_items]
    if wanted in valid:
        setattr(obj, prop, wanted)
    else:
        print(f"  ! {prop}: '{wanted}' tidak valid, pilihan: {valid}")


def ref_plane(name, filename, location, rotation_deg):
    img = bpy.data.images.load(str(REF / filename), check_existing=True)
    e = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    e.empty_display_type = "IMAGE"
    e.data = img
    e.empty_display_size = PLANE_SIZE
    e.empty_image_offset = (-0.5, -(CANVAS_PX[1] - SOLE_PX_FROM_TOP) / CANVAS_PX[1])
    e.use_empty_image_alpha = True
    e.color = (1.0, 1.0, 1.0, 0.55)
    e.show_empty_image_perspective = False
    e.show_empty_image_orthographic = True
    set_enum(e, "empty_image_side", "FRONT")
    e.location = location
    e.rotation_euler = tuple(math.radians(a) for a in rotation_deg)
    e.hide_select = True
    for c in list(e.users_collection):
        c.objects.unlink(e)
    coll["00_REF"].objects.link(e)
    return e


# Blender: depan dilihat dari -Y (karakter menghadap -Y), samping dari +X (menghadap kiri), belakang dari +Y
ref_plane("AK_REF_front", "ak_ref_front.png", (0, +PLANE_DIST, 0), (90, 0, 0))
ref_plane("AK_REF_side", "ak_ref_side.png", (-PLANE_DIST, 0, 0), (90, 0, 90))
ref_plane("AK_REF_back", "ak_ref_back.png", (0, -PLANE_DIST, 0), (90, 0, 180))

# --- 5. penggaris & landmark --------------------------------------------------------------
ruler = bpy.data.objects.get("AK_REF_ruler_1.75m") or bpy.data.objects.new("AK_REF_ruler_1.75m", None)
ruler.empty_display_type = "SINGLE_ARROW"
ruler.empty_display_size = H
ruler.location = (0, 0, 0)
ruler.hide_select = True
if ruler.name not in coll["00_REF"].objects:
    coll["00_REF"].objects.link(ruler)

LANDMARKS = [  # nama, tinggi (m) — docs/21 bagian 2 (diukur dari turnaround, akurasi ±2 cm)
    ("sole", 0.0), ("ankle", 0.11), ("boot_top", 0.26), ("sash_hem", 0.54), ("knee", 0.52),
    ("fingertip", 0.745), ("crotch", 0.85), ("hip_joint", 0.90), ("wrist", 0.95), ("jacket_hem", 1.01),
    ("belt", 1.055), ("elbow", 1.11), ("armpit", 1.24), ("pendant", 1.30), ("shoulder", 1.41),
    ("chin", 1.525), ("eye", 1.616), ("crown", 1.73), ("hair_top", 1.75),
]
for lm, z in LANDMARKS:
    n = f"AK_LM_{lm}"
    e = bpy.data.objects.get(n) or bpy.data.objects.new(n, None)
    e.empty_display_type = "PLAIN_AXES"
    e.empty_display_size = 0.05
    e.location = (0, 0, z)
    e.hide_select = True
    e.color = (1.0, 0.55, 0.0, 1.0)
    if e.name not in coll["00_REF"].objects:
        coll["00_REF"].objects.link(e)

# --- 6. simpan ----------------------------------------------------------------------------
OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_mainfile()
print("Disimpan:", bpy.data.filepath)
print("Collections:", [c.name for c in root_coll.children])
print("REF objects:", [o.name for o in coll["00_REF"].objects])
