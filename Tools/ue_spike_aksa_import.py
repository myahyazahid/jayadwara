"""Spike skeleton model Aksa, langkah S4 (docs/19 Iterasi 0) — impor FBX uji ke skeleton Mannequin asli (Unreal Editor Python).

Mengimpor Art/Export/_spike/SK_Aksa_Spike.fbx (dari Art/Scripts/aksa_spike_roundtrip.py) ke /Game/_Spike/ dengan
skeleton = SK_Mannequin (milik Manny/Quinn), lalu mengekspornya lagi ke Art/Export/_spike/SK_Aksa_Spike_UE.fbx supaya
Art/Scripts/aksa_spike_compare.py bisa membandingkan pose referensi mesh dengan Manny asli.
Folder /Game/_Spike dihapus dulu (uji bersih). Hapus manual setelah spike selesai.

Pakai: python Tools/ue_remote.py Tools/ue_spike_aksa_import.py
"""
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FBX = os.path.join(REPO, "Art", "Export", "_spike", "SK_Aksa_Spike.fbx")
FBX_BACK = os.path.join(REPO, "Art", "Export", "_spike", "SK_Aksa_Spike_UE.fbx")
DEST = "/Game/_Spike"
SKELETON = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()


def log(msg):
    unreal.log(f"[AksaSpike] {msg}")


if EAL.does_directory_exist(DEST):
    EAL.delete_directory(DEST)
skeleton = EAL.load_asset(SKELETON)
if skeleton is None:
    raise RuntimeError(f"{SKELETON} tidak ditemukan")

ui = unreal.FbxImportUI()
ui.set_editor_property("import_mesh", True)
ui.set_editor_property("import_as_skeletal", True)
ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
ui.set_editor_property("skeleton", skeleton)
ui.set_editor_property("import_materials", False)
ui.set_editor_property("import_textures", False)
ui.set_editor_property("import_animations", False)
ui.set_editor_property("create_physics_asset", False)
d = ui.get_editor_property("skeletal_mesh_import_data")
d.set_editor_property("import_uniform_scale", 1.0)
d.set_editor_property("convert_scene", True)
d.set_editor_property("use_t0_as_ref_pose", False)

t = unreal.AssetImportTask()
t.set_editor_property("filename", FBX)
t.set_editor_property("destination_path", DEST)
t.set_editor_property("destination_name", "SK_Aksa_Spike")
t.set_editor_property("automated", True)
t.set_editor_property("replace_existing", True)
t.set_editor_property("save", False)
t.set_editor_property("options", ui)
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")     # importer lama (seperti Jayadwara)
try:
    asset_tools.import_asset_tasks([t])
finally:
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")

mesh = EAL.load_asset(f"{DEST}/SK_Aksa_Spike")
if not isinstance(mesh, unreal.SkeletalMesh):
    raise RuntimeError("SK_Aksa_Spike tidak terimpor sebagai SkeletalMesh")
used = mesh.get_editor_property("skeleton")
log(f"skeleton mesh: {used.get_path_name()} | sama dengan {SKELETON}: {used.get_path_name().split('.')[0] == SKELETON}")
b = mesh.get_bounds()
log(f"tinggi kotak: {2 * b.box_extent.z:.1f} cm (Manny 180.6), origin z={b.origin.z:.1f}")
for a in EAL.list_assets(DEST, recursive=True, include_folder=False):
    log(f"aset baru: {a}")

task = unreal.AssetExportTask()
task.set_editor_property("object", mesh)
task.set_editor_property("filename", FBX_BACK)
task.set_editor_property("automated", True)
task.set_editor_property("prompt", False)
task.set_editor_property("replace_identical", True)
log(f"ekspor balik: {'OK' if unreal.Exporter.run_asset_export_task(task) else 'GAGAL'} -> {FBX_BACK}")
