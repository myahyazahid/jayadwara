
import unreal
EAL = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary
SK = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/Raw/SK_Mixamo_YBot_Skeleton")
if not SK:
    SK = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/Raw/SK_Mixamo_YBot").get_editor_property("skeleton")
print("skeleton:", SK.get_name() if SK else None)
ui_proto = unreal.FbxImportUI
def imp(path, name):
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_materials", False)
    ui.set_editor_property("import_textures", False)
    ui.set_editor_property("create_physics_asset", False)
    ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    ui.set_editor_property("original_import_type", unreal.FBXImportType.FBXIT_ANIMATION)
    ui.set_editor_property("import_mesh", False)
    ui.set_editor_property("import_animations", True)
    ui.set_editor_property("skeleton", SK)
    a = ui.get_editor_property("anim_sequence_import_data")
    a.set_editor_property("convert_scene", True)
    a.set_editor_property("import_bone_tracks", True)
    a.set_editor_property("remove_redundant_keys", False)
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", path)
    t.set_editor_property("destination_path", "/Game/Hermes/ComboIter2/_uji")
    t.set_editor_property("destination_name", name)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", True)
    t.set_editor_property("options", ui)
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    try:
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    finally:
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")
    return EAL.load_asset("/Game/Hermes/ComboIter2/_uji/" + name)

BASE = "C:/repository/unreal_engine/jayadwara_hermes_combo/Hermes/Art/combo-iter2/Mixamo/_uji/"
for tag in ("a","b","c"):
    seq = imp(BASE + f"air_{tag}.fbx", f"A_uji_{tag}")
    if not seq:
        print(tag, "GAGAL IMPOR"); continue
    L = AL.get_sequence_length(seq); o = unreal.AnimPoseEvaluationOptions()
    ys = []; hz = []
    for i in range(0, 13):
        t = min(L*i/12.0, L)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        ys.append(unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).translation.y)
        hz.append(unreal.AnimPoseExtensions.get_bone_pose(p, "head", unreal.AnimPoseSpaces.WORLD).translation.z)
    print(f"[uji] {tag}: panjang {L:.2f} kepala Z {min(hz):.1f}..{max(hz):.1f} | pelvis Y {min(ys):.1f}..{max(ys):.1f}")
