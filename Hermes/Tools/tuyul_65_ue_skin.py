"""Tuyul K6 rev3 — impor ulang tekstur KULIT (T_Tuyul_Color) ke sandbox setelah recolor warna kulit.
Hanya menyentuh /Game/Hermes/Tuyul/Textures/T_Tuyul_Color (sRGB, TC_DEFAULT), tidak mengubah aset lain.
Dijalankan: python Tools/ue_remote.py Hermes/Tools/tuyul_65_ue_skin.py
"""
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
TEX_DIR = os.path.join(REPO, "Hermes", "Art", "tuyul", "Textures")
DEST = "/Game/Hermes/Tuyul/Textures"
NAME = "T_Tuyul_Color"

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

task = unreal.AssetImportTask()
task.set_editor_property("filename", os.path.join(TEX_DIR, f"{NAME}.png"))
task.set_editor_property("destination_path", DEST)
task.set_editor_property("destination_name", NAME)
task.set_editor_property("automated", True)
task.set_editor_property("replace_existing", True)
task.set_editor_property("save", False)
asset_tools.import_asset_tasks([task])

t = EAL.load_asset(f"{DEST}/{NAME}")
assert t is not None, f"gagal impor {DEST}/{NAME}"
t.set_editor_property("srgb", True)
t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
EAL.save_loaded_asset(t)
print(f"reimport OK: {t.get_path_name()}  srgb={t.get_editor_property('srgb')}")
print("=== SKIN REIMPORT SELESAI ===")
