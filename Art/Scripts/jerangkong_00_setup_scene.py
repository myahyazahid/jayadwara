"""Iterasi 0 (docs/20, docs/23) — setup scene Blender untuk model Jerangkong (boss Ep 1 + minion kerangka).

Jalankan di Blender 5.2 (headless: blender --background --factory-startup --python Art/Scripts/jerangkong_00_setup_scene.py,
atau lewat MCP: exec(open(path).read())). Membuat: satuan metrik, hierarki collection per kelompok potongan,
reference plane (depan/samping/belakang), landmark proporsi `JK_LM_*`, penanda target bungkuk sedang `JK_TGT_*`,
penggaris 2,2 m. Lalu menyimpan jerangkong_v00_setup.blend.

Nilai dari docs/23-model-sheet-jerangkong.md (H = 2,2 m = telapak -> puncak tengkorak di tampak depan konsep).
Karakter menghadap -Y (depan = -Y), sama dengan kontrak Jayadwara/Aksa.
Script ini hanya membuat basis scene; jangan dijalankan ulang di atas file yang sudah dimodel.
"""
import math
from pathlib import Path

import bpy

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
REF = ROOT / "Art" / "Reference"
OUT = ROOT / "Art" / "Blender" / "jerangkong_v00_setup.blend"

H = 2.2                        # tinggi konsep (m), telapak -> puncak tengkorak (tampak depan)
CANVAS_PX = (900, 1200)        # ukuran reference plane (px); 1000 px = 2,2 m
SOLE_PX_FROM_TOP = 1100
PLANE_SIZE = H * CANVAS_PX[1] / 1000.0      # sisi terpanjang gambar (m) = 2,64 m
PLANE_DIST = 0.9               # jarak plane dari titik tengah (m); figur lebar ±0,6 m

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


root_coll = make_collection("JK_Jerangkong", scene.collection)
root_coll["jk_height_m"] = H
root_coll["jk_unit"] = "1 unit Blender = 1 m"
root_coll["jk_source"] = "docs/concept-art/jerangkong_v01.webp"
root_coll["jk_modelsheet"] = "docs/23-model-sheet-jerangkong.md"

# satu collection per kelompok potongan (docs/20 bagian 4)
COLL_NAMES = [
    "00_REF", "01_Skull", "02_SpineRibs", "03_PelvisCloth", "04_Arms", "05_Hands",
    "06_LegsFeet", "07_Ornament", "08_KalaCore", "09_Rig", "10_Sockets",
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
ref_plane("JK_REF_front", "jk_ref_front.png", (0, +PLANE_DIST, 0), (90, 0, 0))
ref_plane("JK_REF_side", "jk_ref_side.png", (-PLANE_DIST, 0, 0), (90, 0, 90))
ref_plane("JK_REF_back", "jk_ref_back.png", (0, -PLANE_DIST, 0), (90, 0, 180))

# --- 5. penggaris, landmark, target bungkuk ----------------------------------------------
ruler = bpy.data.objects.get("JK_REF_ruler_2.2m") or bpy.data.objects.new("JK_REF_ruler_2.2m", None)
ruler.empty_display_type = "SINGLE_ARROW"
ruler.empty_display_size = H
ruler.location = (0, 0, 0)
ruler.hide_select = True
if ruler.name not in coll["00_REF"].objects:
    coll["00_REF"].objects.link(ruler)


def marker(name, loc, color, size=0.05, kind="PLAIN_AXES"):
    e = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    e.empty_display_type = kind
    e.empty_display_size = size
    e.location = loc
    e.hide_select = True
    e.color = color
    if e.name not in coll["00_REF"].objects:
        coll["00_REF"].objects.link(e)
    return e


LANDMARKS = [  # nama, tinggi (m) — docs/23 bagian 2 (tampak depan konsep, akurasi ±2 cm)
    ("sole", 0.0), ("ankle", 0.20), ("fingertip", 0.36), ("cloth_hem", 0.57), ("wrist", 0.75),
    ("knee", 0.765), ("bracelet_wrist", 0.83), ("hip_joint", 1.27), ("elbow", 1.33), ("pelvis_top", 1.39),
    ("rib_bottom", 1.51), ("bracelet_upper", 1.62), ("chin", 1.84), ("shoulder_joint", 1.85),
    ("eye", 1.99), ("skull_top", 2.19),
]
for lm, z in LANDMARKS:
    marker(f"JK_LM_{lm}", (0, 0, z), (1.0, 0.55, 0.0, 1.0))

# Target postur "bungkuk sedang" (docs/23 S2): posisi (y, z) di tampak samping; depan = -Y.
# Konsep: pusat tengkorak 0,43 m di depan pergelangan kaki. Model: 0,22 m (setengahnya).
TARGETS = [
    ("skull_center_konsep", (0, -0.43, 2.02), (0.5, 0.5, 0.5, 1.0)),
    ("skull_center", (0, -0.22, 2.00), (1.0, 0.1, 0.1, 1.0)),
    ("neck_base", (0, -0.06, 1.86), (1.0, 0.1, 0.1, 1.0)),
    ("shoulder_joint", (0, -0.08, 1.83), (1.0, 0.1, 0.1, 1.0)),
    ("thorax_center", (0, -0.02, 1.68), (1.0, 0.1, 0.1, 1.0)),
    ("pelvis_center", (0, 0.0, 1.30), (1.0, 0.1, 0.1, 1.0)),
]
for n, loc, col in TARGETS:
    marker(f"JK_TGT_{n}", loc, col, size=0.08, kind="SPHERE")

# --- 6. simpan ----------------------------------------------------------------------------
OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_mainfile()
print("Disimpan:", bpy.data.filepath)
print("Collections:", [c.name for c in root_coll.children])
print("REF objects:", len(coll["00_REF"].objects))
