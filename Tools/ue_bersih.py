import unreal

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# 1) hapus folder uji
for f in ("/Game/Temp/UjiAnim", "/Game/Temp/UjiAnim2", "/Game/Temp"):
    if EAL.does_directory_exist(f):
        EAL.delete_directory(f)
        print("[C] hapus folder %s" % f)

if EAL.does_asset_exist("/Game/Hermes/ComboIter2/Montages/AM_UJI_montage"):
    EAL.delete_asset("/Game/Hermes/ComboIter2/Montages/AM_UJI_montage")
    print("[C] hapus AM_UJI_montage")

# 2) pulihkan AnimSequence proyek yang tertimpa (folder /Game/Jayadwara/.../Mixamo/Raw)
DEST = "/Game/Jayadwara/Characters/Aksa/Anims/Mixamo/Raw"
SKEL = EAL.load_asset(DEST + "/SK_Mixamo_YBot_Skeleton")
LAMA = r"C:\repository\unreal_engine\jayadwara_hermes_combo\Hermes\Art\combo-iter2\Mixamo\_lama"

for peran in ("finisher_02", "air_slam"):
    nama = "A_Aksa_Mx_%s" % peran
    for p in list(EAL.list_assets(DEST, True, False)):
        base = p.split("/")[-1].split(".")[0]
        if base == nama or base.startswith(nama + "_"):
            EAL.delete_asset(p)
    unreal.SystemLibrary.collect_garbage()

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
    t.set_editor_property("filename", LAMA + "\\" + peran + ".fbx")
    t.set_editor_property("destination_path", DEST)
    t.set_editor_property("destination_name", nama)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", True)
    t.set_editor_property("options", ui)
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    try:
        asset_tools.import_asset_tasks([t])
    finally:
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")

    obj = EAL.load_asset(DEST + "/" + nama)
    if isinstance(obj, unreal.AnimSequence):
        print("[C] %s dipulihkan: AnimSequence %.3f s" % (nama, obj.get_play_length()))
    else:
        print("[C] %s: hasil impor bukan AnimSequence (%s)" % (nama, obj.get_class().get_name() if obj else "kosong"))
