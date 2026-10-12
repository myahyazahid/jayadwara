"""Spike skeleton model Aksa (docs/19 Iterasi 0) — ekspor SKM_Manny_Simple ke FBX + cetak ukurannya (Unreal Editor Python).

STATUS: BELUM DIUJI (ditulis 12 Okt 2026 saat editor tertutup). Kalau API gagal, ekspor manual:
Content Browser -> klik kanan SKM_Manny_Simple -> Asset Actions -> Export -> simpan ke Art/Reference/manny/.

Pakai (editor terbuka): python Tools/ue_remote.py Tools/ue_export_manny.py
Hasil : Art/Reference/manny/SKM_Manny_Simple.fbx
Lanjut: blender --background --factory-startup --python Art/Scripts/aksa_spike_analyze_manny.py
"""
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT_DIR = os.path.join(REPO, "Art", "Reference", "manny")
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"

os.makedirs(OUT_DIR, exist_ok=True)
mesh = unreal.EditorAssetLibrary.load_asset(MANNY)
if mesh is None:
    raise RuntimeError(f"{MANNY} tidak ditemukan")

b = mesh.get_bounds()
unreal.log(f"[Aksa] {MANNY}: origin z={b.origin.z:.1f} cm, setengah-tinggi kotak={b.box_extent.z:.1f} cm "
           f"-> tinggi ~{2 * b.box_extent.z:.1f} cm (cek: kaki di z=0?)")
unreal.log(f"[Aksa] skeleton: {mesh.get_editor_property('skeleton').get_path_name()}")

task = unreal.AssetExportTask()
task.set_editor_property("object", mesh)
task.set_editor_property("filename", os.path.join(OUT_DIR, "SKM_Manny_Simple.fbx"))
task.set_editor_property("automated", True)
task.set_editor_property("prompt", False)
task.set_editor_property("replace_identical", True)
ok = unreal.Exporter.run_asset_export_task(task)
unreal.log(f"[Aksa] export FBX: {'OK' if ok else 'GAGAL'} -> {task.get_editor_property('filename')}")
