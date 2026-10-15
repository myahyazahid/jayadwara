"""
Hermes/Tools/aksa2_180_reimport_perfect_mesh.py
Me-reimport SK_Aksa2.fbx versi sempurna (watertight, zero webbing, zero holes) ke Unreal Engine sandbox.
"""
import unreal
from pathlib import Path

DEST = "/Game/Hermes/Aksa2"
FBX_FILE = r"C:\repository\unreal_engine\jayadwara_hermes\Hermes\Art\aksa2\Export\SK_Aksa2.fbx"

eal = unreal.EditorAssetLibrary

mesh_path = f"{DEST}/Mesh/SK_Aksa2"
sk_mesh = eal.load_asset(mesh_path)
if not sk_mesh:
    print(f"Error: {mesh_path} tidak ditemukan!")
else:
    print(f"Me-reimport {sk_mesh.get_name()} dari {FBX_FILE}...")
    task = unreal.AssetImportTask()
    task.filename = FBX_FILE
    task.destination_path = f"{DEST}/Mesh"
    task.destination_name = "SK_Aksa2"
    task.replace_existing = True
    task.automated = True
    task.save = True

    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = True
    options.import_materials = False
    options.import_textures = False
    options.import_animations = False
    
    # Gunakan skeleton sandbox kita
    skel_asset = eal.load_asset(f"{DEST}/Rig/SKEL_Aksa2")
    options.skeleton = skel_asset
    task.options = options

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    print(f"Reimport selesai: {task.imported_object_paths}")

    # Pasang kembali material MI_Aksa2_Body
    sk_mesh = eal.load_asset(mesh_path)
    mat = eal.load_asset(f"{DEST}/Materials/MI_Aksa2_Body")
    if mat and sk_mesh:
        mats = sk_mesh.get_editor_property("materials")
        if mats:
            for m in mats:
                m.set_editor_property("material_interface", mat)
            sk_mesh.set_editor_property("materials", mats)
            print("Material MI_Aksa2_Body berhasil dipasang ke semua slot.")

    # Pasang Physics Asset PA_Aksa2
    pa = eal.load_asset(f"{DEST}/Rig/PA_Aksa2")
    if pa and sk_mesh:
        sk_mesh.set_editor_property("physics_asset", pa)
        print("Physics Asset PA_Aksa2 berhasil dipasang.")

    eal.save_loaded_asset(sk_mesh)
    print("Aset SK_Aksa2 berhasil disimpan permanen ke disk.")
