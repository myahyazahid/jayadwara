"""Jayadwara2 (docs/25 R1/R6) — retarget, ABP, BP, Physics Asset, Anim Dynamics, GameMode, level uji (Unreal Editor Python).

Butuh: hasil ue_import_jayadwara2.py; IK_Mannequin & BP_Jayadwara dari setup model lama (TIDAK diubah).
Membuat (semua di folder/nama baru; model lama utuh):
  /Game/Jayadwara/Characters/Jayadwara2/Rig/IK_Jayadwara2, RTG_Mannequin_To_Jayadwara2
  /Game/Jayadwara/Characters/Jayadwara2/Anims/<nama>_JD2, ABP_Jayadwara2 (+ BS skala Froude, Anim Dynamics scarf/cloth_front)
  /Game/Jayadwara/Characters/Jayadwara2/BP_Jayadwara2     salinan BP_Jayadwara (setelan kamera/input sama), mesh & ABP diganti
  /Game/Jayadwara/Core/BP_JDGameMode_Giant2               pawn BP_Jayadwara2
  /Game/Jayadwara/Maps/Test_GiantScale2                   salinan Test_GiantScale; Jayadwara LAMA berdiri di samping (JD_Lama)
Pakai: python Tools/ue_remote.py Tools/ue_setup_jayadwara2.py   (ulangi setelah ue_import_jayadwara2.py: skeleton dibuat ulang)
"""
import math
import os
import warnings

import unreal

J1 = "/Game/Jayadwara/Characters/Jayadwara"
J2 = "/Game/Jayadwara/Characters/Jayadwara2"
AKSA_RIG = "/Game/Jayadwara/Characters/Aksa/Rig"
CORE = "/Game/Jayadwara/Core"
SRC_MAP = "/Game/Jayadwara/Maps/Test_GiantScale"
MAP = "/Game/Jayadwara/Maps/Test_GiantScale2"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
ANIMS = [
    "/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed",
    "/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_01",
    "/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_02",
    "/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_03",
]
SUFFIX = "_JD2"
DISABLED_OPS = ["Run IK Rig"]          # FBIK pada mesh 45 m menurunkan pinggul (docs/13 Iterasi 6b)
# Postur (13 Okt 2026). Idle Manny sendiri membungkuk ke depan ("ready stance": segmen pinggul>dada 12°, leher>kepala 24°, kepala maju
# 29 cm pada 45 m) dan auto-align chain-to-chain meniru bentuk itu (spine_01 -12,9°, neck_01 -23,2° pada pose retarget).
# Koreksi satu tulang (revisi pertama: spine_01 -3,5° & neck_01 -12°) menyamakan posisi kepala tetapi memberi kurva S/swayback
# (dada atas condong BELAKANG 6°). Revisi 2: offset 4 tulang dicari dengan Gauss-Newton atas ukuran nyata (idle hasil retarget) ke
# target segmen [pinggul>dada, dada bawah>atas, dada>leher, leher>kepala] = [4°, 2°, 2°, 8°] (tegak, kepala sedikit maju).
# Derajat rotasi sumbu X lokal pada pose retarget TARGET, diterapkan setelah auto-align. Ukur ulang bila Manny/skeleton berubah.
# Kaki (revisi 2b): idle Manny berdiri dengan lutut tertekuk & satu kaki di depan (paha kiri 16° dari vertikal, kaki kiri 3,5 m di depan);
# bersama pinggul mundur itu membuat dada tampak condong ke belakang pada proporsi Tripo (paha pendek, betis panjang). Offset kaki dicari
# dengan Gauss-Newton (target: paha>betis kiri 4°/kanan 0°, betis>telapak ≈1°, tinggi pergelangan ≈ 332 cm).
POSTURE_DEG = {"spine_01": 1.0, "spine_03": 5.89, "spine_05": 3.18, "neck_01": -7.68,
               "thigh_l": -23.19, "thigh_r": -0.29, "calf_l": 26.27, "calf_r": 22.42}
# SEMUA tulang ini harus diset berurutan (yang tak tercantum = 0): auto-align meninggalkan sisa offset di spine_02/04 & neck_02 dan
# set_rotation_offset tak independen antar tetangga; hanya urutan lengkap ini yang mereproduksi hasil ukur.
# Kuda-kuda (14 Okt 2026, developer): idle Jayadwara2 mengangkang (jarak telapak 1.609 cm = 42 % tinggi) vs model lama 769 cm
# (20 %). Rotasi sumbu Z lokal paha pada pose retarget: +10 derajat paha kiri melebarkan ±300 cm (diukur), jadi paha dirapatkan.
# Tanda kanan dicerminkan; ukur ulang (report_lean mencetak jarak telapak) bila skeleton/anim berubah.
STANCE_DEG = {"thigh_l": -12.6, "thigh_r": 12.6}
# Kaki yang dirapatkan jadi lebih tegak -> pergelangan turun ke bawah lantai; akar pose retarget dinaikkan (cm, ruang komponen)
# supaya tinggi pergelangan idle kembali ke tinggi rest (v06: 0,1336 m = ±316 cm). Ukur ulang lewat log "kuda-kuda" bila STANCE_DEG diubah.
STANCE_ROOT_UP_CM = float(globals().get("STANCE_ROOT_UP_CM", 97.0))   # diukur 14 Okt (badan v06): pergelangan 219 -> target ±316 cm
POSTURE_BONES = ["spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "neck_02",
                 "thigh_l", "thigh_r", "calf_l", "calf_r"]

PA_BODIES = ["pelvis", "spine_01", "spine_03", "spine_05", "neck_01", "head",
             "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
             "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r"]
PA_EXCLUDE = ["scarf_", "cloth_", "ik_"]
# R3d (13 Okt 2026): sayap & kain depan kini KINEMATIK (bobot pinggul+paha, jayadwara2_22_rig_r3.py). Rantai Anim Dynamics
# membuat sayap terlempar seperti ekor saat lompat di UE, dan tulang scarf_*/cloth_* kini berbobot 0 -> tidak ada node AD.
CHAINS = []
CLOTH_LIMIT_BONES = ["thigh_l", "thigh_r", "calf_l", "calf_r"]
CLOTH_LIMIT_RADIUS = 11.0
BODY_EXTENT = 4.0
SIM_SPACE_COMPONENT, ACC_SCALE, GRAVITY_SCALE = 0, 0.1, 1.0

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
ST = unreal.RetargetSourceOrTarget


def log(m):
    unreal.log(f"[Jayadwara2] {m}")


def fresh(folder, name, cls, factory):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    return asset_tools.create_asset(name, folder, cls, factory)


def make_ik_rig(folder, name, mesh):
    rig = fresh(folder, name, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    c = unreal.IKRigController.get_controller(rig)
    c.set_skeletal_mesh(mesh)
    if not c.apply_auto_generated_retarget_definition():
        unreal.log_warning(f"[Jayadwara2] {name}: auto retarget definition gagal")
    c.apply_auto_fbik()
    chains = [str(ch.get_editor_property("chain_name")) for ch in c.get_retarget_chains()]
    log(f"{name}: root={c.get_retarget_root()} chain={len(chains)}: {chains}")
    EAL.save_loaded_asset(rig, only_if_is_dirty=False)
    return rig


def retarget(mesh):
    manny = EAL.load_asset(MANNY)
    ik_m = EAL.load_asset(f"{AKSA_RIG}/IK_Mannequin")
    ik_j = make_ik_rig(f"{J2}/Rig", "IK_Jayadwara2", mesh)
    rtg = fresh(f"{J2}/Rig", "RTG_Mannequin_To_Jayadwara2", unreal.IKRetargeter, unreal.IKRetargetFactory())
    r = unreal.IKRetargeterController.get_controller(rtg)
    r.set_ik_rig(ST.SOURCE, ik_m)
    r.set_ik_rig(ST.TARGET, ik_j)
    r.set_preview_mesh(ST.SOURCE, manny)
    r.set_preview_mesh(ST.TARGET, mesh)
    r.add_default_ops()
    r.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    r.auto_align_all_bones(ST.TARGET, unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN)
    for bone in POSTURE_BONES + [b for b in STANCE_DEG if b not in POSTURE_BONES]:
        deg = POSTURE_DEG.get(bone, 0.0)
        a = math.radians(deg) / 2.0
        q = unreal.Quat(x=math.sin(a), y=0.0, z=0.0, w=math.cos(a))
        if bone in STANCE_DEG:                                              # aduksi/abduksi (sumbu Z lokal), setelah pitch
            b_ = math.radians(STANCE_DEG[bone]) / 2.0
            q = q * unreal.Quat(x=0.0, y=0.0, z=math.sin(b_), w=math.cos(b_))
        r.set_rotation_offset_for_retarget_pose_bone(bone, q, ST.TARGET)
    if STANCE_ROOT_UP_CM:
        base = r.get_root_offset_in_retarget_pose(ST.TARGET)
        r.set_root_offset_in_retarget_pose(unreal.Vector(base.x, base.y, base.z + STANCE_ROOT_UP_CM), ST.TARGET)
    log(f"pose retarget: {POSTURE_DEG}; kuda-kuda (Z): {STANCE_DEG}, akar +{STANCE_ROOT_UP_CM:.0f} cm")
    for op in DISABLED_OPS:
        i = r.get_index_of_op_by_name(op)
        if i >= 0:
            r.set_retarget_op_enabled(i, False)
    log("RTG ops: " + str([str(r.get_op_name(i)) + ("" if r.get_retarget_op_enabled(i) else " (mati)")
                           for i in range(r.get_num_retarget_ops())]))
    EAL.save_loaded_asset(rtg, only_if_is_dirty=False)

    dest = f"{J2}/Anims"
    bp_path = f"{J2}/BP_Jayadwara2"
    if EAL.does_asset_exist(bp_path):                                       # lepas rujukan ABP supaya bisa dihapus
        bp = EAL.load_asset(bp_path)
        unreal.get_default_object(bp.generated_class()).get_editor_property("mesh").set_editor_property("anim_class", None)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        EAL.save_loaded_asset(bp, only_if_is_dirty=False)
        unreal.SystemLibrary.collect_garbage()
    for a in (EAL.list_assets(dest, recursive=True) if EAL.does_directory_exist(dest) else []):
        EAL.delete_asset(str(a).split(".")[0])
    left = EAL.list_assets(dest, recursive=True) if EAL.does_directory_exist(dest) else []
    if left:
        raise RuntimeError(f"gagal menghapus isi {dest}: {left}")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unreal.JDEditorToolsLibrary.retarget_assets_to_folder([EAL.load_asset(a) for a in ANIMS], manny, mesh, rtg,
                                                              dest, SUFFIX, True)
    EAL.save_directory(dest, only_if_is_dirty=False, recursive=True)
    if EAL.does_asset_exist(f"{dest}/ABP_Unarmed{SUFFIX}"):
        EAL.rename_asset(f"{dest}/ABP_Unarmed{SUFFIX}", f"{dest}/ABP_Jayadwara2")
        EAL.save_asset(f"{dest}/ABP_Jayadwara2", only_if_is_dirty=False)
    log(f"retarget: {len(EAL.list_assets(dest, recursive=False))} aset di {dest}")
    path = os.path.join(unreal.Paths.project_content_dir(), "Jayadwara/Characters/Jayadwara2/Anims/ABP_Jayadwara2.uasset")
    raw = open(path, "rb").read()
    miss = [n for n in (f"Anims/BS_Idle_Walk_Run{SUFFIX}", f"Anims/MM_Jump{SUFFIX}", f"Anims/MM_Land{SUFFIX}") if n.encode() not in raw]
    if miss:
        unreal.log_error(f"[Jayadwara2] ABP_Jayadwara2 di disk tidak merujuk: {miss}")
    else:
        log("ABP_Jayadwara2 di disk merujuk BlendSpace & anim di Anims/ (OK)")


def report_lean():
    """Kepala - pinggul pada MM_Idle_JD2 (cm, ruang komponen; Y = depan)."""
    seq = EAL.load_asset(f"{J2}/Anims/MM_Idle{SUFFIX}")
    pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, 0.0, unreal.AnimPoseEvaluationOptions())
    g = lambda b: unreal.AnimPoseExtensions.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation
    p, h = g("pelvis"), g("head")
    lean = math.degrees(math.atan2(h.y - p.y, h.z - p.z))
    segs = [("pelvis", "spine_03"), ("spine_03", "spine_05"), ("spine_05", "neck_02"), ("neck_02", "head")]
    ang = [math.degrees(math.atan2(g(b).y - g(a).y, g(b).z - g(a).z)) for a, b in segs]
    log(f"idle: kepala - pinggul = ({h.x - p.x:.0f}, {h.y - p.y:.0f}, {h.z - p.z:.0f}) cm, condong depan {lean:.1f}°; "
        f"segmen pinggul>dada/dada/leher/kepala = {[round(v, 1) for v in ang]} (target [4, 2, 2, 8])")
    leg = lambda a, b: math.degrees(math.atan2(g(b).y - g(a).y, -(g(b).z - g(a).z)))
    fl, fr = g("foot_l"), g("foot_r")
    log(f"kuda-kuda: jarak telapak kiri-kanan {fl.x - fr.x:.0f} cm (model lama 769), maju-mundur {fl.y - fr.y:.0f} cm; "
        f"tinggi telapak L/R {fl.z:.0f}/{fr.z:.0f}")
    log(f"kaki: paha>betis L/R = {leg('thigh_l', 'calf_l'):.1f}/{leg('thigh_r', 'calf_r'):.1f}, betis>telapak L/R = "
        f"{leg('calf_l', 'foot_l'):.1f}/{leg('calf_r', 'foot_r'):.1f} (target 4/0, 1/1); tinggi pergelangan L/R = {g('foot_l').z:.0f}/{g('foot_r').z:.0f} cm (target 332)")


def scale_blendspace(factor):
    src = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/BS_Idle_Walk_Run")
    bs = EAL.load_asset(f"{J2}/Anims/BS_Idle_Walk_Run{SUFFIX}")
    samples = []
    for s, o in zip(bs.get_editor_property("sample_data"), src.get_editor_property("sample_data")):
        v = o.get_editor_property("sample_value")
        s.set_editor_property("sample_value", unreal.Vector(v.x, v.y * factor, v.z))
        samples.append(s)
    params = []
    for i, p in enumerate(bs.get_editor_property("blend_parameters")):
        if i == 1:
            p.set_editor_property("max", src.get_editor_property("blend_parameters")[1].get_editor_property("max") * factor)
        params.append(p)
    bs.set_editor_property("blend_parameters", params)
    bs.set_editor_property("sample_data", samples)
    EAL.save_loaded_asset(bs, only_if_is_dirty=False)
    log(f"BS_Idle_Walk_Run{SUFFIX}: Speed x{factor:.2f}")


def physics_and_cloth(mesh, scale):
    pa = EAL.load_asset(f"{J2}/Mesh/PA_Jayadwara2")
    n = unreal.JDEditorToolsLibrary.rebuild_physics_asset(pa, mesh, PA_BODIES, PA_EXCLUDE, 30.0)
    EAL.save_loaded_asset(pa, only_if_is_dirty=False)
    log(f"PA_Jayadwara2: {n} body (target {len(PA_BODIES)})")
    abp = EAL.load_asset(f"{J2}/Anims/ABP_Jayadwara2")
    log(f"ABP_Jayadwara2: {unreal.JDEditorToolsLibrary.bypass_anim_graph_nodes(abp, 'ControlRig')} node Control Rig dilepas")
    if not CHAINS:
        EAL.save_loaded_asset(abp, only_if_is_dirty=False)
        log("ABP_Jayadwara2: tanpa Anim Dynamics (sayap/kain kinematik)")
        return
    chains = []
    for start, end, swing, twist in CHAINS:
        c = unreal.JDAnimDynamicsChain()
        c.set_editor_property("start_bone", start)
        c.set_editor_property("end_bone", end)
        c.set_editor_property("swing_limit", swing)
        c.set_editor_property("twist_limit", twist)
        e = BODY_EXTENT * scale
        c.set_editor_property("box_extents", unreal.Vector(e, e, e))
        c.set_editor_property("collision_radius", e)
        chains.append(c)
    n = unreal.JDEditorToolsLibrary.add_anim_dynamics_chains(abp, chains, CLOTH_LIMIT_BONES, CLOTH_LIMIT_RADIUS * scale,
                                                             SIM_SPACE_COMPONENT, ACC_SCALE, GRAVITY_SCALE)
    EAL.save_loaded_asset(abp, only_if_is_dirty=False)
    log(f"ABP_Jayadwara2: {n} rantai Anim Dynamics")


def make_pawn(mesh):
    path = f"{J2}/BP_Jayadwara2"
    if not EAL.does_asset_exist(path):
        if EAL.duplicate_asset(f"{J1}/BP_Jayadwara", path) is None:
            raise RuntimeError("duplikat BP_Jayadwara gagal")
        log("BP_Jayadwara2 = salinan BP_Jayadwara")
    bp = EAL.load_asset(path)
    d = unreal.get_default_object(bp.generated_class())
    m = d.get_editor_property("mesh")
    m.set_editor_property("skeletal_mesh_asset", mesh)
    m.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    m.set_editor_property("anim_class", EAL.load_asset(f"{J2}/Anims/ABP_Jayadwara2").generated_class())
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)
    return bp


def make_level(bp):
    gm_path = f"{CORE}/BP_JDGameMode_Giant2"
    if not EAL.does_asset_exist(gm_path):
        f = unreal.BlueprintFactory()
        f.set_editor_property("parent_class", unreal.JDGameMode)
        gm = asset_tools.create_asset("BP_JDGameMode_Giant2", CORE, unreal.Blueprint, f)
    else:
        gm = EAL.load_asset(gm_path)
    g = unreal.get_default_object(gm.generated_class())
    g.set_editor_property("default_pawn_class", bp.generated_class())
    g.set_editor_property("player_controller_class", EAL.load_asset(f"{CORE}/BP_JDPlayerController").generated_class())
    unreal.BlueprintEditorLibrary.compile_blueprint(gm)
    EAL.save_loaded_asset(gm, only_if_is_dirty=False)

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if EAL.does_asset_exist(MAP):
        les.load_level(MAP)
    else:
        les.new_level_from_template(MAP, SRC_MAP)
        log("Test_GiantScale2 dibuat dari Test_GiantScale")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", gm.generated_class())
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = eas.get_all_level_actors()
    start = next((a for a in actors if isinstance(a, unreal.PlayerStart)), None)
    # Jayadwara lama diam di samping pemain (sebagai pembanding), tidak di-possess
    for a in actors:
        if a.get_actor_label() == "JD_Lama":
            eas.destroy_actor(a)
    if start is not None:
        loc = start.get_actor_location()
        old = EAL.load_asset(f"{J1}/BP_Jayadwara")
        a = eas.spawn_actor_from_class(old.generated_class(), unreal.Vector(loc.x, loc.y + 3000.0, loc.z),
                                       start.get_actor_rotation())
        a.set_actor_label("JD_Lama")
    les.save_current_level()
    log("Test_GiantScale2 siap: Play = Jayadwara2; Jayadwara lama (JD_Lama) berdiri 30 m di sisi kanan")


def main():
    mesh = EAL.load_asset(f"{J2}/Mesh/SK_Jayadwara2")
    if mesh is None:
        unreal.log_error("[Jayadwara2] SK_Jayadwara2 belum ada: jalankan Tools/ue_import_jayadwara2.py")
        return
    retarget(mesh)
    report_lean()
    bp = make_pawn(mesh)
    scale = unreal.get_default_object(bp.generated_class()).get_giant_scale()
    scale_blendspace(scale ** 0.5)
    physics_and_cloth(mesh, scale)
    make_level(bp)


main()
