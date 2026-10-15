"""Iterasi 0 — setup scene Blender untuk model Jayadwara.

Jalankan di Blender 5.2 (mis. lewat MCP: exec(open(path).read())).
Membuat: satuan metrik, hierarki collection, reference plane (depan/samping/belakang),
penanda landmark proporsi, penggaris 1,9 m. Lalu menyimpan jayadwara_giant_v00_setup.blend.

Nilai proporsi dari docs/14-model-sheet-jayadwara.md (H = 1,90 m).
Script ini hanya membuat basis scene; jangan dijalankan ulang di atas file yang sudah dimodel.
"""
import math
from pathlib import Path

import bpy

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
REF = ROOT / "Art" / "Reference"
OUT = ROOT / "Art" / "Blender" / "jayadwara" / "jayadwara_giant_v00_setup.blend"

H = 1.90                       # tinggi badan (m), telapak kaki -> puncak helm tanpa tanduk
CANVAS_PX = (760, 1200)        # ukuran reference plane (px); 1000 px = 1,90 m
SOLE_PX_FROM_TOP = 1100
PLANE_SIZE = H * CANVAS_PX[1] / 1000.0      # sisi terpanjang gambar (m) = 2,28 m
PLANE_DIST = 0.6               # jarak plane dari titik tengah (m)

scene = bpy.context.scene

# --- 1. bersihkan objek default yang tidak dipakai (Cube) ---------------------------------
for ob in list(scene.objects):
    if ob.type == "MESH" and ob.name.startswith("Cube"):
        bpy.data.objects.remove(ob, do_unlink=True)

# --- 2. satuan ---------------------------------------------------------------------------
us = scene.unit_settings
us.system = "METRIC"
us.scale_length = 1.0
us.length_unit = "METERS"

# --- 3. collection -----------------------------------------------------------------------
def make_collection(name, parent):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in parent.children:
        parent.children.link(c)
    return c


root_coll = make_collection("JD_Giant", scene.collection)
root_coll["jd_height_m"] = H
root_coll["jd_unit"] = "1 unit Blender = 1 m"
root_coll["jd_source"] = "docs/concept-art/jayadwara_final.webp"
root_coll["jd_modelsheet"] = "docs/14-model-sheet-jayadwara.md"

COLL_NAMES = [
    "00_REF", "01_Body", "02_Head", "03_Torso", "04_Shoulder",
    "05_Arm", "06_Belt_Cloth", "07_Leg", "08_Rig", "09_Sockets",
]
coll = {n: make_collection(n, root_coll) for n in COLL_NAMES}
scene_coll = make_collection("_Scene", scene.collection)

for ob in scene.objects:                       # Camera & Light ke _Scene
    if ob.type in {"CAMERA", "LIGHT"}:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        scene_coll.objects.link(ob)


# --- 4. reference plane ------------------------------------------------------------------
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
ref_plane("JD_REF_front", "jd_ref_front.png", (0, +PLANE_DIST, 0), (90, 0, 0))
ref_plane("JD_REF_side", "jd_ref_side.png", (-PLANE_DIST, 0, 0), (90, 0, 90))
ref_plane("JD_REF_back", "jd_ref_back.png", (0, -PLANE_DIST, 0), (90, 0, 180))

# --- 5. penggaris & landmark -------------------------------------------------------------
ruler = bpy.data.objects.get("JD_REF_ruler_1.9m") or bpy.data.objects.new("JD_REF_ruler_1.9m", None)
ruler.empty_display_type = "SINGLE_ARROW"
ruler.empty_display_size = H
ruler.location = (0, 0, 0)
ruler.hide_select = True
if ruler.name not in coll["00_REF"].objects:
    coll["00_REF"].objects.link(ruler)

LANDMARKS = [  # nama, tinggi (m) — lihat docs/14 bagian 2
    ("sole", 0.0), ("ankle", 0.129), ("cloth_hem", 0.49), ("knee", 0.593),
    ("fist_target", 0.84), ("fist_concept", 0.91), ("hip_joint", 0.893),
    ("wrist", 1.049), ("belt", 1.180), ("elbow", 1.292), ("armpit", 1.376),
    ("gem_chest", 1.480), ("shoulder", 1.602), ("chin", 1.664),
    ("pauldron_tip", 1.674), ("crown", 1.900), ("horn_tip", 1.990),
]
for lm, z in LANDMARKS:
    n = f"JD_LM_{lm}"
    e = bpy.data.objects.get(n) or bpy.data.objects.new(n, None)
    e.empty_display_type = "PLAIN_AXES"
    e.empty_display_size = 0.06
    e.location = (0, 0, z)
    e.hide_select = True
    e.color = (0.0, 0.8, 1.0, 1.0)
    if e.name not in coll["00_REF"].objects:
        coll["00_REF"].objects.link(e)

# --- 6. simpan ---------------------------------------------------------------------------
OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_mainfile()
print("Disimpan:", bpy.data.filepath)
print("Collections:", [c.name for c in root_coll.children])
print("REF objects:", [o.name for o in coll["00_REF"].objects])
