"""Tuyul K0 (docs/27, Hermes/tuyul_hermes.md) — setup scene Blender untuk model Tuyul (Tripo, jenis B).

Jalankan headless (scene kosong):
  blender --background --factory-startup --python Art/Scripts/tuyul_00_setup_scene.py
Membuat satuan metrik, collection `TY_Tuyul` (+ anak 00_REF, 01_Source, 09_Rig, 10_Sockets),
lalu menyimpan Art/Blender/tuyul/tuyul_v00_setup.blend.

Nilai dari kartu model Hermes/tuyul_hermes.md bagian 3: tinggi authoring 1,0 m, menghadap -Y.
Skrip ini hanya membuat basis scene; jangan dijalankan ulang di atas file yang sudah dimodel.
Salinan dari Art/Scripts/jerangkong_00_setup_scene.py; hanya path/collection/nama yang diubah.
"""
import bpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuyul_paths as P  # noqa: E402

ROOT = P.ROOT
OUT = P.BLENDER / "tuyul_v00_setup.blend"

H = 1.0                        # tinggi authoring (m) — kartu model

scene = bpy.context.scene

# 1) buang objek default
for ob in list(scene.objects):
    if ob.type == "MESH" and ob.name.startswith("Cube"):
        bpy.data.objects.remove(ob, do_unlink=True)

# 2) satuan metrik
us = scene.unit_settings
us.system = "METRIC"
us.scale_length = 1.0
us.length_unit = "METERS"


# 3) collection
def make_collection(name, parent):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in parent.children:
        parent.children.link(c)
    return c


root_coll = make_collection("TY_Tuyul", scene.collection)
root_coll["ty_height_m"] = H
root_coll["ty_unit"] = "1 unit Blender = 1 m"
root_coll["ty_source"] = "Art/Source/tuyul_tripo_v01.glb (Tripo AI, developer)"
root_coll["ty_guide"] = "Hermes/tuyul_hermes.md"

for n in ["00_REF", "01_Source", "09_Rig", "10_Sockets"]:
    make_collection(n, root_coll)

scene_coll = make_collection("_Scene", scene.collection)
for ob in scene.objects:                       # Camera & Light ke _Scene
    if ob.type in {"CAMERA", "LIGHT"}:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        scene_coll.objects.link(ob)

# 4) simpan
OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
print("Disimpan:", bpy.data.filepath)
print("Collections:", [c.name for c in root_coll.children])
