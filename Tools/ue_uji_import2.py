import unreal

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

FBX = r"C:\repository\unreal_engine\jayadwara_hermes_combo\mixamo\result\finisher_02.fbx"
DEST = "/Game/Temp/UjiAnim2"
SKEL = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/Raw/SK_Mixamo_YBot_Skeleton")
print("[U2] skeleton: %s" % (SKEL.get_name() if SKEL else "TIDAK ADA"))

ui = unreal.FbxImportUI()
ui.set_editor_property("import_materials", False)
ui.set_editor_property("import_textures", False)
ui.set_editor_property("create_physics_asset", False)
ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
ui.set_editor_property("original_import_type", unreal.FBXImportType.FBXIT_ANIMATION)
ui.set_editor_property("import_mesh", False)
ui.set_editor_property("import_animations", True)
if SKEL:
    ui.set_editor_property("skeleton", SKEL)
a = ui.get_editor_property("anim_sequence_import_data")
a.set_editor_property("convert_scene", True)
a.set_editor_property("import_bone_tracks", True)
a.set_editor_property("remove_redundant_keys", False)

t = unreal.AssetImportTask()
t.set_editor_property("filename", FBX)
t.set_editor_property("destination_path", DEST)
t.set_editor_property("destination_name", "UJI2_finisher_02")
t.set_editor_property("automated", True)
t.set_editor_property("replace_existing", True)
t.set_editor_property("save", True)
t.set_editor_property("options", ui)

unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
try:
    asset_tools.import_asset_tasks([t])
finally:
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")

print("[U2] paths: %s" % list(t.get_editor_property("imported_object_paths")))
for p in EAL.list_assets(DEST, True, False):
    a2 = EAL.load_asset(p)
    cls = a2.get_class().get_name() if a2 else "?"
    extra = ""
    if isinstance(a2, unreal.AnimSequence):
        sk = a2.get_editor_property("skeleton")
        extra = " | panjang %.3f s | skeleton %s" % (a2.get_play_length(), sk.get_name() if sk else "-")
    print("[U2] %s (%s)%s" % (p, cls, extra))
