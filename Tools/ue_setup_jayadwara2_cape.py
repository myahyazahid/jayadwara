"""Jubah Jayadwara2 (docs/26 J1) — ABP pengikut + komponen jubah di BP_Jayadwara2 (Unreal Editor Python).

Butuh: ue_import_jayadwara2_cape.py; modul editor dengan JDEditorToolsLibrary.setup_copy_pose_anim_blueprint.
Membuat/mengubah:
  /Game/Jayadwara/Characters/Jayadwara2/Cape/ABP_Jayadwara2_Cape   Copy Pose From Mesh (induk attach) -> JD Cape Chains
      (simulasi 5 rantai cape_*: gravitasi, hambatan udara, kapsul paha/betis/pinggul; J1c) -> Output Pose
  BP_Jayadwara2: komponen SkeletalMesh "Cape" di-attach ke Mesh (SK_Jayadwara2_Cape + ABP di atas, tanpa tabrakan)
Pakai: python Tools/ue_remote.py Tools/ue_setup_jayadwara2_cape.py
       python Tools/ue_remote.py -c "CAPE=False; exec(open(r'Tools/ue_setup_jayadwara2_cape.py').read())"   # lepas jubah dari BP
Lepas/pakai: UJDCapeComponent (tombol Y sementara, J1b); pemicu lock-on/aksi combat di J4.
"""
import unreal

J2 = "/Game/Jayadwara/Characters/Jayadwara2"
ROOT = f"{J2}/Cape"
BP_PATH = f"{J2}/BP_Jayadwara2"
COMP_NAME = "Cape"
CAPE = globals().get("CAPE", True)
CHAINS = ["c", "l", "r", "fl", "fr"]
COLLIDERS = [("thigh_l", "calf_l", 0.14), ("thigh_r", "calf_r", 0.14), ("calf_l", "foot_l", 0.095),
             ("calf_r", "foot_r", 0.095), ("pelvis", "spine_03", 0.14)]       # (tulang A, tulang B, radius m authoring)
MARGIN_M = 0.01

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
    log("ABP_Jayadwara2_Cape: Copy Pose From Mesh (attach parent) -> Output Pose")
    # J1c: simulasi rantai (gravitasi, hambatan udara -> terangkat saat jatuh, kapsul kaki). Radius authoring (m) diukur
    # dari mesh; sendi rantai saat diam berjarak >= 1,3 cm dari kapsul ini, jadi pose diam tidak terdorong.
    k = 100.0 * 45.0 / 1.90                                   # m authoring -> cm komponen (skala raksasa di-bake)
    starts = [f"cape_{c}_01" for c in CHAINS]
    ends = [f"cape_{c}_06" for c in CHAINS]
    ca, cb, cr = zip(*[(a, b, r * k) for a, b, r in COLLIDERS])
    n = unreal.JDEditorToolsLibrary.add_cape_chains_node(abp, starts, ends, list(ca), list(cb), list(cr), MARGIN_M * k)
    if n < 0:
        raise RuntimeError("add_cape_chains_node gagal (lihat Output Log)")
    EAL.save_loaded_asset(abp, only_if_is_dirty=False)
    log(f"ABP_Jayadwara2_Cape: + JD Cape Chains ({n} rantai, {len(COLLIDERS)} kapsul; tuning Gravity/AirDrag/Stiffness di ABP)")
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
