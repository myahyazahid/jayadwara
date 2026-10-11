"""Iterasi 6 (docs/13) — pawn raksasa uji: BP_Jayadwara + game mode + level Test_GiantScale (Unreal Editor Python).

Butuh: build C++ dengan AJDGiantCharacter, hasil ue_import_jayadwara.py dan ue_setup_retarget.py.
Membuat / mengisi ulang:
  /Game/Jayadwara/Characters/Jayadwara/BP_Jayadwara   parent AJDGiantCharacter, SK_Jayadwara + ABP_Jayadwara, IA_*
  /Game/Jayadwara/Core/BP_JDGameMode_Giant             pawn BP_Jayadwara (uji; transformasi sungguhan di Fase 1)
  /Game/Jayadwara/Maps/Test_GiantScale                 salinan Test_Greybox dengan GameMode Override di atas
  Anims/BS_Idle_Walk_Run_JD: sumbu Speed = nilai BlendSpace Mannequin x sqrt(skala raksasa), pasangan dari
  GlobalAnimRateScale = 1/sqrt(skala) di AJDGiantCharacter (skala Froude). Jalankan ulang kalau GiantHeightCm berubah.
  Mesh/PA_Jayadwara: dibangun ulang, 1 kapsul per anggota badan (PA_BODIES), tanpa selendang/kain/IK.
  Anims/ABP_Jayadwara: node Anim Dynamics untuk 4 rantai selendang/kain (docs/13 D5), dengan bola penolak di paha.
Langkah PA & Anim Dynamics butuh modul editor C++ JayadwaraEditor (unreal.JDEditorToolsLibrary).
Pakai: python Tools/ue_remote.py Tools/ue_setup_giant.py
"""
import unreal

JD = "/Game/Jayadwara/Characters/Jayadwara"
CORE = "/Game/Jayadwara/Core"
SRC_MAP = "/Game/Jayadwara/Maps/Test_Greybox"
MAP = "/Game/Jayadwara/Maps/Test_GiantScale"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def make_bp(folder, name, parent):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", parent)
    log(f"{name} dibuat (parent {parent.__name__})")
    return asset_tools.create_asset(name, folder, unreal.Blueprint, f)


def finish(bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)


def scale_blendspace(factor):
    """Sampel & batas sumbu Speed BS raksasa = BS Mannequin x factor (selalu dari sumber, jadi aman diulang)."""
    src = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/BS_Idle_Walk_Run")
    bs = EAL.load_asset(f"{JD}/Anims/BS_Idle_Walk_Run_JD")
    src_samples = src.get_editor_property("sample_data")
    samples = []
    for s, o in zip(bs.get_editor_property("sample_data"), src_samples):
        v = o.get_editor_property("sample_value")
        s.set_editor_property("sample_value", unreal.Vector(v.x, v.y * factor, v.z))
        samples.append(s)
    params = []
    for i, p in enumerate(bs.get_editor_property("blend_parameters")):
        if i == 1:                                               # sumbu 1 = Speed
            p.set_editor_property("max", src.get_editor_property("blend_parameters")[1].get_editor_property("max") * factor)
        params.append(p)
    bs.set_editor_property("blend_parameters", params)
    bs.set_editor_property("sample_data", samples)
    EAL.save_loaded_asset(bs, only_if_is_dirty=False)
    log(f"BS_Idle_Walk_Run_JD: Speed x{factor:.2f} (jog {600 * factor:.0f} cm/s)")


PA_BODIES = ["pelvis", "spine_01", "spine_03", "spine_05", "neck_01", "head",
             "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
             "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r"]
PA_EXCLUDE = ["scarf_", "cloth_", "ik_"]          # digerakkan Anim Dynamics / tulang IK, bukan body fisika

# (awal, akhir, ayun°, twist°): selendang lebih lentur dari panel kain depan/belakang
CHAINS = [("scarf_l_01", "scarf_l_06", 40.0, 10.0), ("scarf_r_01", "scarf_r_06", 40.0, 10.0),
          ("cloth_front_01", "cloth_front_03", 30.0, 5.0), ("cloth_back_01", "cloth_back_03", 30.0, 5.0)]
CLOTH_LIMIT_BONES = ["thigh_l", "thigh_r", "calf_l", "calf_r"]
CLOTH_LIMIT_RADIUS = 11.0                         # cm, skala 1 (± tebal paha model); dikali skala raksasa
BODY_EXTENT = 4.0                                 # cm, skala 1; dikali skala raksasa
# Diuji di PIE (12 Okt 2026, 45 m): Component space meregang karena mesh berskala 23,68; World space meregang saat
# bergerak; Actor space stabil. Percepatan karakter (acc > 0) atau gravitasi > 1 membuat rantai memanjang/melayang
# setelah berhenti. Jadi kain mengikuti gerak badan (pinggul, kaki, belok), belum inersia lari-berhenti.
SIM_SPACE_ACTOR, ACC_SCALE, GRAVITY_SCALE = 1, 0.0, 1.0
# DIMATIKAN: Actor space juga merusak SKALA tulang keluaran (panel kain menyusut hilang, selendang jadi garis tipis).
# Anim Dynamics UE 5.6.1 tidak mendukung mesh berskala 23,68 di komponen. Jalan keluar yang direncanakan: skala
# raksasa di-bake ke mesh (docs/13 Iterasi 6). Sampai itu, selendang/kain kaku mengikuti pinggul.
ENABLE_ANIM_DYNAMICS = False


def setup_physics_asset():
    mesh = EAL.load_asset(f"{JD}/Mesh/SK_Jayadwara")
    pa = EAL.load_asset(f"{JD}/Mesh/PA_Jayadwara")
    n = unreal.JDEditorToolsLibrary.rebuild_physics_asset(pa, mesh, PA_BODIES, PA_EXCLUDE, 30.0)
    EAL.save_loaded_asset(pa, only_if_is_dirty=False)
    log(f"PA_Jayadwara: {n} body (target {len(PA_BODIES)})")


def setup_anim_dynamics(scale):
    abp = EAL.load_asset(f"{JD}/Anims/ABP_Jayadwara")
    # Foot IK Mannequin (Control Rig) ikut dari ABP_Unarmed; ia mengandaikan orientasi tulang & ukuran Manny sehingga
    # kaki Jayadwara mengangkang dan telapak terpuntir. Dilepas; foot IK raksasa dibuat sendiri nanti (Fase 1).
    log(f"ABP_Jayadwara: {unreal.JDEditorToolsLibrary.bypass_anim_graph_nodes(abp, 'ControlRig')} node Control Rig dilepas")
    if not ENABLE_ANIM_DYNAMICS:
        EAL.save_loaded_asset(abp, only_if_is_dirty=False)
        log("ABP_Jayadwara: Anim Dynamics dimatikan (lihat ENABLE_ANIM_DYNAMICS)")
        return
    chains = []
    for start, end, swing, twist in CHAINS:
        c = unreal.JDAnimDynamicsChain()
        c.set_editor_property("start_bone", start)
        c.set_editor_property("end_bone", end)
        c.set_editor_property("swing_limit", swing)
        c.set_editor_property("twist_limit", twist)
        e = BODY_EXTENT * scale                                  # Actor space = satuan dunia
        c.set_editor_property("box_extents", unreal.Vector(e, e, e))
        c.set_editor_property("collision_radius", e)
        chains.append(c)
    n = unreal.JDEditorToolsLibrary.add_anim_dynamics_chains(abp, chains, CLOTH_LIMIT_BONES, CLOTH_LIMIT_RADIUS * scale,
                                                             SIM_SPACE_ACTOR, ACC_SCALE, GRAVITY_SCALE)
    EAL.save_loaded_asset(abp, only_if_is_dirty=False)
    log(f"ABP_Jayadwara: {n} rantai Anim Dynamics")


def main():
    bp = make_bp(JD, "BP_Jayadwara", unreal.JDGiantCharacter)
    d = unreal.get_default_object(bp.generated_class())
    mesh = d.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh_asset", EAL.load_asset(f"{JD}/Mesh/SK_Jayadwara"))
    mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    mesh.set_editor_property("anim_class", EAL.load_asset(f"{JD}/Anims/ABP_Jayadwara").generated_class())
    for prop, path in (("move_action", "/Game/Input/Actions/IA_Move"),
                       ("look_action", "/Game/Input/Actions/IA_Look"),
                       ("mouse_look_action", "/Game/Input/Actions/IA_MouseLook"),
                       ("jump_action", "/Game/Input/Actions/IA_Jump")):
        d.set_editor_property(prop, EAL.load_asset(path))
    finish(bp)
    giant_scale = unreal.get_default_object(bp.generated_class()).get_giant_scale()
    scale_blendspace(giant_scale ** 0.5)
    setup_physics_asset()
    setup_anim_dynamics(giant_scale)

    gm = make_bp(CORE, "BP_JDGameMode_Giant", unreal.JDGameMode)
    g = unreal.get_default_object(gm.generated_class())
    g.set_editor_property("default_pawn_class", bp.generated_class())
    g.set_editor_property("player_controller_class", EAL.load_asset(f"{CORE}/BP_JDPlayerController").generated_class())
    finish(gm)

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    # Jangan EAL.duplicate_asset untuk map: salinan tertahan di memori dan load_level membuat editor crash
    # ("World Memory Leaks", UE 5.6.1). new_level_from_template memakai Test_Greybox sebagai template.
    if EAL.does_asset_exist(MAP):
        les.load_level(MAP)
    else:
        les.new_level_from_template(MAP, SRC_MAP)
        log("Test_GiantScale dibuat dari Test_Greybox")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", gm.generated_class())
    # PlayerStart di tengah lantai, menghadap blok "gedung" di -X (pawn raksasa butuh ruang kapsul ±9,5 x 22,5 m)
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if isinstance(a, unreal.PlayerStart):
            a.set_actor_location_and_rotation(unreal.Vector(2000, 0, 2400), unreal.Rotator(roll=0, pitch=0, yaw=180), False, False)
    les.save_current_level()
    s = unreal.get_default_object(bp.generated_class())
    log(f"BP_Jayadwara skala {s.get_giant_scale():.2f}; Test_GiantScale siap (Play di level ini)")


main()
