"""Import Aksa2 Spike (R1) ke Unreal Engine 5.6.
Destinasi: /Game/Jayadwara/Characters/Aksa2/
Skeleton: /Game/Characters/Mannequins/Meshes/SK_Mannequin (asli, tanpa penambahan tulang baru)
"""
import json
import os
import unreal

REPO = r"C:\repository\unreal_engine\jayadwara"
EXP = r"C:\repository\unreal_engine\explorasi\aksa2"
FBX_PATH = os.path.join(EXP, "export", "SK_Aksa2_Spike.fbx")
SOCKETS_PATH = os.path.join(EXP, "export", "SK_Aksa2_Spike_sockets.json")
TEX_DIR = os.path.join(EXP, "export", "Textures")

DEST_ROOT = "/Game/Jayadwara/Characters/Aksa2"
MESH_DEST = f"{DEST_ROOT}/Mesh"
TEX_DEST = f"{DEST_ROOT}/Textures"
MAT_DEST = f"{DEST_ROOT}/Materials"

SKELETON_PATH = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

def log(msg):
    unreal.log(f"[Aksa2_Spike] {msg}")

# 1. Pastikan skeleton ada
skeleton = unreal.load_object(None, f"{SKELETON_PATH}.SK_Mannequin") or EAL.load_asset(SKELETON_PATH)
if not skeleton:
    raise RuntimeError(f"Skeleton tidak ditemukan: {SKELETON_PATH}")

# 2. Import Tekstur
tex_assets = {}
for f in os.listdir(TEX_DIR):
    if f.endswith(".png"):
        name = os.path.splitext(f)[0]
        t_path = os.path.join(TEX_DIR, f)
        
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", t_path)
        task.set_editor_property("destination_path", TEX_DEST)
        task.set_editor_property("destination_name", name)
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", True)
        task.set_editor_property("save", True)
        
        asset_tools.import_asset_tasks([task])
        imported_tex = EAL.load_asset(f"{TEX_DEST}/{name}")
        if imported_tex:
            if "N" in name:
                imported_tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
                imported_tex.set_editor_property("srgb", False)
            elif "ORM" in name or "Mask" in name:
                imported_tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
                imported_tex.set_editor_property("srgb", False)
            else:
                imported_tex.set_editor_property("srgb", True)
            EAL.save_loaded_asset(imported_tex)
            tex_assets[name] = imported_tex
            log(f"Imported texture: {name}")

# 3. Buat Material Master & Material Instance
mat_name = "M_Aksa2_Master"
mat_path = f"{MAT_DEST}/{mat_name}"
mat = EAL.load_asset(mat_path)
if not mat:
    mat = asset_tools.create_asset(mat_name, MAT_DEST, unreal.Material, unreal.MaterialFactoryNew())
    
MEL = unreal.MaterialEditingLibrary
mat.set_editor_property("two_sided", True)

# Bersihkan node lama
MEL.delete_all_material_expressions(mat)

# Buat parameter BaseColor, Normal, ORM
tex_bc = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -400, -200)
tex_bc.set_editor_property("parameter_name", "BaseColor")
if "T_Aksa2_BC" in tex_assets:
    tex_bc.set_editor_property("texture", tex_assets["T_Aksa2_BC"])
MEL.connect_material_property(tex_bc, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

tex_n = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -400, 100)
tex_n.set_editor_property("parameter_name", "Normal")
tex_n.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
if "T_Aksa2_N" in tex_assets:
    tex_n.set_editor_property("texture", tex_assets["T_Aksa2_N"])
MEL.connect_material_property(tex_n, "RGB", unreal.MaterialProperty.MP_NORMAL)

tex_orm = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -400, 400)
tex_orm.set_editor_property("parameter_name", "ORM")
tex_orm.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
if "T_Aksa2_ORM" in tex_assets:
    tex_orm.set_editor_property("texture", tex_assets["T_Aksa2_ORM"])
MEL.connect_material_property(tex_orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
MEL.connect_material_property(tex_orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
MEL.connect_material_property(tex_orm, "B", unreal.MaterialProperty.MP_METALLIC)

MEL.recompile_material(mat)
EAL.save_loaded_asset(mat)
log(f"Material {mat_name} configured and saved")

# 4. Import Skeletal Mesh SK_Aksa2_Spike
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

task = unreal.AssetImportTask()
task.set_editor_property("filename", FBX_PATH)
task.set_editor_property("destination_path", MESH_DEST)
task.set_editor_property("destination_name", "SK_Aksa2_Spike")
task.set_editor_property("automated", True)
task.set_editor_property("replace_existing", True)
task.set_editor_property("save", True)
task.set_editor_property("options", ui)

unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
try:
    asset_tools.import_asset_tasks([task])
finally:
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")

mesh = EAL.load_asset(f"{MESH_DEST}/SK_Aksa2_Spike")
if not isinstance(mesh, unreal.SkeletalMesh):
    raise RuntimeError("Gagal import SK_Aksa2_Spike sebagai SkeletalMesh!")

# Assign material ke slot
mats = mesh.get_editor_property("materials")
for m in mats:
    m.set_editor_property("material_interface", mat)
mesh.set_editor_property("materials", mats)

# Bounds & verify
b = mesh.get_bounds()
height_cm = 2 * b.box_extent.z
log(f"SK_Aksa2_Spike terimpor! Tinggi = {height_cm:.2f} cm (Target Manny 180.6 cm)")
log(f"Skeleton yang dipakai: {mesh.get_editor_property('skeleton').get_path_name()}")

# 5. Pasang Sockets dari JSON
if os.path.exists(SOCKETS_PATH):
    with open(SOCKETS_PATH, "r", encoding="utf-8") as f:
        sock_data = json.load(f)
    for s in sock_data.get("sockets", []):
        name = s["name"]
        if mesh.find_socket(name) is not None:
            continue
        try:
            sock = unreal.new_object(unreal.SkeletalMeshSocket, outer=mesh)
            sock.set_socket_parent(mesh, s["bone"])
            loc = unreal.Vector(*s["ue_component_cm"])
            sock.set_editor_property("relative_location", loc)
            mesh.add_socket(sock, False)
            mesh.rename_socket(str(sock.get_editor_property("socket_name")), name)
            log(f"Socket {name} dipasang pada {s['bone']}")
        except Exception as e:
            log(f"Socket {name} dilewati: {e}")

EAL.save_loaded_asset(mesh)
log("SK_Aksa2_Spike berhasil disimpan dan siap diuji!")
