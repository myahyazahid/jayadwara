"""Setup Aksa2 di Unreal Sandbox (/Game/Hermes/Aksa2).
Dijalankan melalui: python Tools/ue_remote.py Hermes/Tools/aksa2_70_ue_setup.py
"""
import json
import os
from pathlib import Path
import unreal

DEST = "/Game/Hermes/Aksa2"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

FBX_LOD0 = os.path.join(REPO, "Hermes", "Art", "aksa2", "Export", "SK_Aksa2.fbx")
SOCKETS_JSON = os.path.join(REPO, "Hermes", "Art", "aksa2", "Export", "SK_Aksa2_sockets.json")
TEX_DIR = os.path.join(REPO, "Hermes", "Art", "aksa2", "Export", "Textures")

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

print(f"=== AKS2 SANDBOX SETUP: DEST = {DEST} ===")

# 1. Pastikan folder tujuan ada
for sub in ["", "/Textures", "/Materials", "/Maps"]:
    p = f"{DEST}{sub}"
    if not EAL.does_directory_exist(p):
        EAL.make_directory(p)

# 2. Skeleton: Duplikasi SK_Mannequin ke sandbox jika belum ada
skel_dst = f"{DEST}/SKEL_Aksa2"
skel_src = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
if not EAL.does_asset_exist(skel_dst):
    print(f"Menduplikasi {skel_src} -> {skel_dst}...")
    skel_obj = EAL.duplicate_asset(skel_src, skel_dst)
else:
    print(f"Skeleton sandbox sudah ada: {skel_dst}")
    skel_obj = EAL.load_asset(skel_dst)

assert skel_obj is not None, f"Gagal memuat skeleton sandbox: {skel_dst}"
EAL.save_loaded_asset(skel_obj)

# 3. Import Tekstur PBR
tex_files = {
    "T_Aksa2_D": (os.path.join(TEX_DIR, "T_Aksa2_D.png"), True, unreal.TextureCompressionSettings.TC_DEFAULT),
    "T_Aksa2_N": (os.path.join(TEX_DIR, "T_Aksa2_N.png"), False, unreal.TextureCompressionSettings.TC_NORMALMAP),
    "T_Aksa2_ORM": (os.path.join(TEX_DIR, "T_Aksa2_ORM.png"), False, unreal.TextureCompressionSettings.TC_MASKS),
}

imported_tex = {}
for name, (fpath, srgb, comp) in tex_files.items():
    tex_path = f"{DEST}/Textures/{name}"
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", fpath)
    task.set_editor_property("destination_path", f"{DEST}/Textures")
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", False)
    asset_tools.import_asset_tasks([task])
    
    tex = EAL.load_asset(tex_path)
    if tex:
        tex.set_editor_property("srgb", srgb)
        tex.set_editor_property("compression_settings", comp)
        EAL.save_loaded_asset(tex)
        imported_tex[name] = tex
        print(f"Tekstur diimpor: {tex_path}")
    else:
        print(f"PERINGATAN: Gagal memuat tekstur {tex_path}")

# 4. Material Instance MI_Aksa2_Body
mat_path = f"{DEST}/Materials/MI_Aksa2_Body"
master_src = "/Game/Jayadwara/Characters/Aksa2/Materials/M_Aksa2_Master"
master_mat = EAL.load_asset(master_src)
assert master_mat is not None, f"Master material {master_src} tidak ditemukan"

mi_factory = unreal.MaterialInstanceConstantFactoryNew()
mi_obj = asset_tools.create_asset("MI_Aksa2_Body", f"{DEST}/Materials", unreal.MaterialInstanceConstant, mi_factory)
if mi_obj:
    MEL.set_material_instance_parent(mi_obj, master_mat)
    if "T_Aksa2_D" in imported_tex:
        MEL.set_material_instance_texture_parameter_value(mi_obj, "BaseColor", imported_tex["T_Aksa2_D"])
    if "T_Aksa2_N" in imported_tex:
        MEL.set_material_instance_texture_parameter_value(mi_obj, "Normal", imported_tex["T_Aksa2_N"])
    if "T_Aksa2_ORM" in imported_tex:
        MEL.set_material_instance_texture_parameter_value(mi_obj, "ORM", imported_tex["T_Aksa2_ORM"])
    MEL.update_material_instance(mi_obj)
    EAL.save_loaded_asset(mi_obj)
    print(f"Material Instance dibuat & disimpan: {mat_path}")

# 5. Import Skeletal Mesh LOD0
mesh_dst = f"{DEST}/SK_Aksa2"
print(f"Mengimpor mesh FBX: {FBX_LOD0} -> {mesh_dst}...")

task = unreal.AssetImportTask()
task.set_editor_property("filename", FBX_LOD0)
task.set_editor_property("destination_path", DEST)
task.set_editor_property("destination_name", "SK_Aksa2")
task.set_editor_property("automated", True)
task.set_editor_property("replace_existing", True)
task.set_editor_property("save", False)

ui = unreal.FbxImportUI()
ui.set_editor_property("import_mesh", True)
ui.set_editor_property("import_as_skeletal", True)
ui.set_editor_property("skeleton", skel_obj)
ui.set_editor_property("import_animations", False)
ui.set_editor_property("import_materials", False)
ui.set_editor_property("import_textures", False)

smd = ui.skeletal_mesh_import_data
smd.set_editor_property("import_morph_targets", False)
smd.set_editor_property("use_t0_as_ref_pose", False)
smd.set_editor_property("preserve_smoothing_groups", True)
smd.set_editor_property("import_mesh_lods", False)
smd.set_editor_property("convert_scene", True)
smd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)

task.set_editor_property("options", ui)
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
try:
    asset_tools.import_asset_tasks([task])
finally:
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")

sk_obj = EAL.load_asset(mesh_dst)
assert sk_obj is not None, f"Gagal memuat skeletal mesh: {mesh_dst}"

# Pasang material ke slot materials
if mi_obj:
    mats = []
    for m in sk_obj.get_editor_property("materials"):
        m.set_editor_property("material_interface", mi_obj)
        mats.append(m)
    sk_obj.set_editor_property("materials", mats)
    print("Material MI_Aksa2_Body terpasang ke mesh.")

# Pasang physics asset Mannequin
pa_manny = EAL.load_asset("/Game/Characters/Mannequins/Rigs/PA_Mannequin")
if pa_manny:
    sk_obj.set_editor_property("physics_asset", pa_manny)

# 6. Sockets
if os.path.exists(SOCKETS_JSON):
    sock_data = json.load(open(SOCKETS_JSON))
    print(f"Memeriksa {len(sock_data.get('sockets', []))} sockets dari json...")
    for s in sock_data.get("sockets", []):
        name = s["name"]
        bone = s["bone"]
        if sk_obj.find_socket(name) is not None:
            print(f"  Socket sudah ada: {name}")
            continue
        try:
            sock = unreal.new_object(unreal.SkeletalMeshSocket, outer=sk_obj)
            sock.set_socket_parent(sk_obj, bone)
            loc = unreal.Vector(*s.get("rel_loc", [0, 0, 0]))
            sock.set_editor_property("relative_location", loc)
            sk_obj.add_socket(sock, False)
            sk_obj.rename_socket(str(sock.get_editor_property("socket_name")), name)
            print(f"  + Socket dibuat: {name} @ {bone}")
        except Exception as e:
            print(f"  Peringatan pembuatan socket {name}: {e}")

EAL.save_loaded_asset(sk_obj)
EAL.save_loaded_asset(skel_obj)
print(f"Skeletal Mesh LOD0 disimpan: {mesh_dst}")

# 7. Duplikasi Level Sandbox
map_src = "/Game/Jayadwara/Maps/Test_Combat"
map_dst = f"{DEST}/Maps/Test_Hermes_Aksa2"
if not EAL.does_asset_exist(map_dst):
    print(f"Menduplikasi level: {map_src} -> {map_dst}...")
    map_obj = EAL.duplicate_asset(map_src, map_dst)
else:
    print(f"Level sandbox sudah ada: {map_dst}")
    map_obj = EAL.load_asset(map_dst)

EAL.save_loaded_asset(map_obj)
print("=== SETUP SELESAI DENGAN SUKSES ===")
