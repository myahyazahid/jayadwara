"""Jubah Jayadwara2 (docs/26 J1) — ABP pengikut + komponen jubah di BP_Jayadwara2 (Unreal Editor Python).

Butuh: ue_import_jayadwara2_cape.py; modul editor dengan JDEditorToolsLibrary.setup_copy_pose_anim_blueprint.
Membuat/mengubah:
  /Game/Jayadwara/Characters/Jayadwara2/Cape/ABP_Jayadwara2_Cape   Copy Pose From Mesh (induk attach) -> Output Pose
  BP_Jayadwara2: komponen SkeletalMesh "Cape" di-attach ke Mesh (SK_Jayadwara2_Cape + ABP di atas, tanpa tabrakan)
Pakai: python Tools/ue_remote.py Tools/ue_setup_jayadwara2_cape.py
       python Tools/ue_remote.py -c "CAPE=False; exec(open(r'Tools/ue_setup_jayadwara2_cape.py').read())"   # lepas jubah dari BP
J1: jubah SELALU terpakai (juga saat combat) sampai J4 (UJDCapeComponent: lepas/pakai otomatis). Kinematik, tanpa simulasi (J3).
"""
import unreal

J2 = "/Game/Jayadwara/Characters/Jayadwara2"
ROOT = f"{J2}/Cape"
BP_PATH = f"{J2}/BP_Jayadwara2"
COMP_NAME = "Cape"
CAPE = globals().get("CAPE", True)

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary


def log(m):
    unreal.log(f"[Jayadwara2Cape] {m}")


def subobjects(bp):
    out = []
    for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
        d = SDL.get_data(h)
        out.append((h, str(SDL.get_variable_name(d)), SDL.get_object(d)))
    return out


def remove_cape(bp):
    subs = subobjects(bp)
    for h, name, _ in subs:
        if name == COMP_NAME:
            SDS.delete_subobject(subs[0][0], h, bp)
            log(f"komponen {COMP_NAME} dilepas dari BP_Jayadwara2")
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)


def make_abp(mesh):
    path = f"{ROOT}/ABP_Jayadwara2_Cape"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    f = unreal.AnimBlueprintFactory()
    f.set_editor_property("target_skeleton", mesh.get_editor_property("skeleton"))
    f.set_editor_property("parent_class", unreal.AnimInstance)
    f.set_editor_property("preview_skeletal_mesh", mesh)
    abp = asset_tools.create_asset("ABP_Jayadwara2_Cape", ROOT, unreal.AnimBlueprint, f)
    if not unreal.JDEditorToolsLibrary.setup_copy_pose_anim_blueprint(abp):
        raise RuntimeError("setup_copy_pose_anim_blueprint gagal (lihat Output Log)")
    EAL.save_loaded_asset(abp, only_if_is_dirty=False)
    log("ABP_Jayadwara2_Cape: Copy Pose From Mesh (attach parent) -> Output Pose")
    return abp


def add_cape(bp, mesh, abp):
    subs = subobjects(bp)
    mesh_h = next((h for h, name, o in subs if name in ("Mesh", "CharacterMesh0") and isinstance(o, unreal.SkeletalMeshComponent)), None)
    if mesh_h is None:
        raise RuntimeError(f"komponen Mesh tidak ditemukan di BP_Jayadwara2: {[n for _, n, _ in subs]}")
    cape_h = next((h for h, name, _ in subs if name == COMP_NAME), None)
    if cape_h is None:
        params = unreal.AddNewSubobjectParams(parent_handle=mesh_h, new_class=unreal.SkeletalMeshComponent, blueprint_context=bp)
        cape_h, fail = SDS.add_new_subobject(params)
        if not fail.is_empty():
            raise RuntimeError(f"tambah komponen gagal: {fail}")
        SDS.rename_subobject(cape_h, unreal.Text(COMP_NAME))
        log(f"komponen {COMP_NAME} ditambahkan (anak Mesh)")
    comp = SDL.get_object(SDL.get_data(cape_h))
    comp.set_editor_property("skeletal_mesh_asset", mesh)
    comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    comp.set_editor_property("anim_class", abp.generated_class())
    comp.set_editor_property("generate_overlap_events", False)
    comp.set_editor_property("can_character_step_up_on", unreal.CanBeCharacterBase.ECB_NO)
    comp.set_collision_profile_name("NoCollision")
    comp.set_editor_property("relative_location", unreal.Vector(0, 0, 0))
    comp.set_editor_property("relative_rotation", unreal.Rotator(0, 0, 0))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)
    log(f"BP_Jayadwara2.{COMP_NAME}: SK_Jayadwara2_Cape + ABP_Jayadwara2_Cape (kinematik, ikut pose badan)")


def main():
    bp = EAL.load_asset(BP_PATH)
    if bp is None:
        unreal.log_error("[Jayadwara2Cape] BP_Jayadwara2 belum ada: jalankan Tools/ue_setup_jayadwara2.py")
        return
    if not CAPE:
        remove_cape(bp)
        return
    mesh = EAL.load_asset(f"{ROOT}/Mesh/SK_Jayadwara2_Cape")
    if mesh is None:
        unreal.log_error("[Jayadwara2Cape] SK_Jayadwara2_Cape belum ada: jalankan Tools/ue_import_jayadwara2_cape.py")
        return
    remove_cape(bp)                     # lepas rujukan ABP lama supaya bisa dihapus & dibuat ulang
    unreal.SystemLibrary.collect_garbage()
    abp = make_abp(mesh)
    add_cape(bp, mesh, abp)
    log("selesai. Play di Test_GiantScale2 (T = transformasi) untuk menilai jubah di idle & jalan.")


main()
