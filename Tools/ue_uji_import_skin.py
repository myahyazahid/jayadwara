import unreal

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

FBX = r"C:\repository\unreal_engine\jayadwara_hermes_combo\mixamo\result\finisher_02.fbx"
DEST = "/Game/Temp/UjiAnim"
SKEL = "/Game/Jayadwara/Anims/Mixamo/Raw/SK_Mixamo_YBot"

skel = EAL.load_asset(SKEL + "_Skeleton")
if not skel:
    # cari skeleton dari mesh
    mesh = EAL.load_asset(SKEL)
    print("[U] mesh %s" % ("ada" if mesh else "TIDAK ADA"))
    if mesh:
        skel = mesh.get_editor_property("skeleton")
print("[U] skeleton: %s" % (skel.get_name() if skel else "None"))

ui = unreal.FbxImportUI()
ui.set_editor_property("import_materials", False)
ui.set_editor_property("import_textures", False)
ui.set_editor_property("create_physics_asset", False)
ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
ui.set_editor_property("original_import_type", unreal.FBXImportType.FBXIT_ANIMATION)
ui.set_editor_property("import_mesh", False)
ui.set_editor_property("import_animations", True)
if skel:
    ui.set_editor_property("skeleton", skel)
a = ui.get_editor_property("anim_sequence_import_data")
a.set_editor_property("convert_scene", True)
a.set_editor_property("import_bone_tracks", True)
a.set_editor_property("remove_redundant_keys", False)

t = unreal.AssetImportTask()
t.set_editor_property("filename", FBX)
t.set_editor_property("destination_path", DEST)
t.set_editor_property("destination_name", "UJI_finisher_02")
t.set_editor_property("automated", True)
t.set_editor_property("replace_existing", True)
t.set_editor_property("save", True)
t.set_editor_property("options", ui)

unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
try:
    asset_tools.import_asset_tasks([t])
finally:
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")

print("[U] imported_object_paths: %s" % list(t.get_editor_property("imported_object_paths")))
print("[U] isi folder: %s" % EAL.list_assets(DEST, True, False))
