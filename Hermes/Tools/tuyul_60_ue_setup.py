"""Tuyul K6 — setup aset di sandbox UE /Game/Hermes/Tuyul.
Dijalankan: python Tools/ue_remote.py Hermes/Tools/tuyul_60_ue_setup.py
Membuat: folder sandbox, SKEL_Tuyul (salinan SK_Mannequin + Compatible Skeleton), 4 tekstur,
M_Tuyul_Master (salinan M_Aksa2_Master + param Emissive/GlowIntensity), MI_Tuyul_Body,
dan duplikat level Test_Combat -> Test_Hermes_Tuyul.
"""
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
TEX_DIR = os.path.join(REPO, "Hermes", "Art", "tuyul", "Textures")

DEST = "/Game/Hermes/Tuyul"
MESH_DIR = f"{DEST}/Mesh"
TEX_DEST = f"{DEST}/Textures"
MAT_DIR = f"{DEST}/Materials"
MAP_DEST = f"{DEST}/Maps"
SKELETON = f"{MESH_DIR}/SKEL_Tuyul"

MANNY_SKEL = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
MASTER_SRC = "/Game/Jayadwara/Characters/Aksa2/Materials/M_Aksa2_Master"
MAP_SRC = "/Game/Jayadwara/Maps/Test_Combat"

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

print(f"=== TUYUL K6 SETUP: DEST = {DEST} ===")

# 1. Folder
for sub in ["", "/Mesh", "/Textures", "/Materials", "/Maps"]:
    p = f"{DEST}{sub}"
    if not EAL.does_directory_exist(p):
        EAL.make_directory(p)
        print("  mkdir", p)

# 2. Skeleton (salinan SK_Mannequin + compatible skeleton)
if not EAL.does_asset_exist(SKELETON):
    skel = EAL.duplicate_asset(MANNY_SKEL, SKELETON)
    print("  SKEL_Tuyul dibuat dari SK_Mannequin")
else:
    skel = EAL.load_asset(SKELETON)
    print("  SKEL_Tuyul sudah ada")
assert skel is not None, f"gagal membuat {SKELETON}"
man = EAL.load_asset(MANNY_SKEL)
if man not in list(skel.get_editor_property("compatible_skeletons")):
    skel.add_compatible_skeleton(man)
    print("  + Compatible Skeleton: SK_Mannequin")
else:
    print("  Compatible Skeleton SK_Mannequin sudah ada")
EAL.save_loaded_asset(skel)

# 3. Tekstur
TEX = {
    "T_Tuyul_Color": ("T_Tuyul_Color.png", True, unreal.TextureCompressionSettings.TC_DEFAULT),
    "T_Tuyul_N": ("T_Tuyul_N.png", False, unreal.TextureCompressionSettings.TC_NORMALMAP),
    "T_Tuyul_ORM": ("T_Tuyul_ORM.png", False, unreal.TextureCompressionSettings.TC_MASKS),
    "T_Tuyul_Emit": ("T_Tuyul_Emit.png", True, unreal.TextureCompressionSettings.TC_DEFAULT),
}
tex = {}
for name, (fn, srgb, comp) in TEX.items():
    path = f"{TEX_DEST}/{name}"
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", os.path.join(TEX_DIR, fn))
    task.set_editor_property("destination_path", TEX_DEST)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", False)
    asset_tools.import_asset_tasks([task])
    t = EAL.load_asset(path)
    if t:
        t.set_editor_property("srgb", srgb)
        t.set_editor_property("compression_settings", comp)
        EAL.save_loaded_asset(t)
        tex[name] = t
        print("  tekstur:", path)
    else:
        print("  PERINGATAN: gagal impor", path)

# 4. Master material (salinan M_Aksa2_Master) + param Emissive x GlowIntensity
master_path = f"{MAT_DIR}/M_Tuyul_Master"
if not EAL.does_asset_exist(master_path):
    master = EAL.duplicate_asset(MASTER_SRC, master_path)
    print("  M_Tuyul_Master disalin dari M_Aksa2_Master")
else:
    master = EAL.load_asset(master_path)
    print("  M_Tuyul_Master sudah ada")
assert master is not None

try:
    if tex.get("T_Tuyul_Emit"):
        tn = MEL.create_material_expression(master, unreal.MaterialExpressionTextureSampleParameter2D, -700, 300)
        tn.set_editor_property("parameter_name", "Emissive")
        tn.set_editor_property("texture", tex["T_Tuyul_Emit"])
        sn = MEL.create_material_expression(master, unreal.MaterialExpressionScalarParameter, -700, 560)
        sn.set_editor_property("parameter_name", "GlowIntensity")
        sn.set_editor_property("default_value", 1.0)
        mul = MEL.create_material_expression(master, unreal.MaterialExpressionMultiply, -380, 400)
        MEL.connect_material_expressions(tn, "RGB", mul, "A")
        MEL.connect_material_expressions(sn, "", mul, "B")
        MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        MEL.recompile_material(master)
        EAL.save_loaded_asset(master)
        print("  + param Emissive x GlowIntensity -> EmissiveColor")
except Exception as e:  # noqa: BLE001
    print("  PERINGATAN emissive:", e)

# 5. Material Instance
mi_path = f"{MAT_DIR}/MI_Tuyul_Body"
mi = EAL.load_asset(mi_path)
if mi is None:
    mi = asset_tools.create_asset("MI_Tuyul_Body", MAT_DIR, unreal.MaterialInstanceConstant,
                                  unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, master)
for pname, key in [("BaseColor", "T_Tuyul_Color"), ("Normal", "T_Tuyul_N"),
                   ("ORM", "T_Tuyul_ORM"), ("Emissive", "T_Tuyul_Emit")]:
    if tex.get(key):
        try:
            MEL.set_material_instance_texture_parameter_value(mi, pname, tex[key])
            print(f"  MI param {pname} <- {key}")
        except Exception as e:  # noqa: BLE001
            print(f"  PERINGATAN param {pname}:", e)
try:
    MEL.set_material_instance_scalar_parameter_value(mi, "GlowIntensity", 1.0)
except Exception as e:  # noqa: BLE001
    print("  PERINGATAN GlowIntensity:", e)
MEL.update_material_instance(mi)
EAL.save_loaded_asset(mi)
print("  MI_Tuyul_Body siap")

# 6. Level sandbox
map_dst = f"{MAP_DEST}/Test_Hermes_Tuyul"
if not EAL.does_asset_exist(map_dst):
    m = EAL.duplicate_asset(MAP_SRC, map_dst)
    print("  level Test_Hermes_Tuyul dibuat dari Test_Combat")
else:
    m = EAL.load_asset(map_dst)
    print("  level Test_Hermes_Tuyul sudah ada")
EAL.save_loaded_asset(m)

print("=== SETUP K6 SELESAI ===")
