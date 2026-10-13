"""Jerangkong (jalur B, docs/20 Iterasi 5) — retarget, ABP, Physics Asset, BP boss & minion, penempatan di level uji.

Butuh: hasil Tools/ue_import_jerangkong.py, IK_Mannequin (ue_setup_retarget.py), modul editor JayadwaraEditor.
Pakai: python Tools/ue_remote.py Tools/ue_setup_jerangkong.py
Membuat / mengisi ulang (per varian boss "Jerangkong" dan minion "Kerangka"):
  Jerangkong/Rig/IK_<V>, RTG_Mannequin_To_<V>   pose retarget: HANYA lengan disejajarkan ke A-pose Manny; tulang belakang,
                                                leher, dan kaki tetap pose rest (bungkuk sedang & kuda-kuda lebar, docs/24 S2/S3)
  Jerangkong/Anims_<V>/ABP_<V>                  ABP_Unarmed + 3 serangan hasil retarget; foot IK Control Rig Mannequin dilepas;
                                                Anim Dynamics untuk kain cloth_front/back_01..03 (boss saja;
                                                minion: kain kaku, lihat VARIANTS)
  Jerangkong/Mesh/PA_<V>                        1 kapsul per tulang utama (tanpa kain/IK)
  Jerangkong/BP_Jerangkong                      parent AJDGiantCharacter (30,66 m ter-bake, kapsul & laju animasi skala raksasa)
  Jerangkong/BP_Kerangka                        parent Character (1,86 m)
  Level (hanya kalau PLACE_IN_LEVELS = True): 1 BP_Jerangkong di Test_GiantScale (±41 m di depan-kiri PlayerStart,
  menghadap pemain), 3 BP_Kerangka di Test_Greybox. Default False: aktor JK_* yang sudah ada dihapus dari level supaya
  level uji tetap ringan di laptop developer; minion/boss baru ditaruh saat iterasinya (F1 Iterasi 5 & 8).
"""
import math
import os
import warnings

import unreal

JK = "/Game/Jayadwara/Characters/Jerangkong"
IK_MANNY = "/Game/Jayadwara/Characters/Aksa/Rig/IK_Mannequin"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
ANIMS = [
    "/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed",
    "/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_01",
    "/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_02",
    "/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_03",
]
PLACE_IN_LEVELS = False                                  # True = taruh contoh boss/minion di level uji (berat di laptop)
MODEL_H_CM = 219.0                                       # puncak tengkorak model Blender (docs/24)
VARIANTS = {
    "Jerangkong": {"mesh": "SK_Jerangkong", "scale": 14.0, "suffix": "_JK", "cloth_dynamics": True},
    # Uji PIE 12 Okt 2026: di skala manusia rantai kain melar ke bawah & bergetar cepat (sama dengan selendang Aksa:
    # gravitasi > batas solver). Minion kecil & sampai 6 sekaligus -> kain kaku ikut panggul.
    "Kerangka": {"mesh": "SK_Kerangka", "scale": 0.85, "suffix": "_KR", "cloth_dynamics": False},
}
ALIGN_BONES = [f"{b}_{s}" for s in "lr" for b in ("clavicle", "upperarm", "lowerarm", "hand")]
PA_BODIES = ["pelvis", "spine_01", "spine_03", "spine_05", "neck_01", "head",
             "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
             "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r"]
PA_EXCLUDE = ["cloth_", "ik_"]
CLOTH = [("cloth_front_01", "cloth_front_03", 30.0, 5.0), ("cloth_back_01", "cloth_back_03", 30.0, 5.0)]
CLOTH_LIMIT_BONES = ["thigh_l", "thigh_r"]
CLOTH_LIMIT_M = 0.05             # radius bola paha (m, ruang model). Kain depan ±0,07-0,10 m dari sumbu paha (Aksa: jangan mulai di dalam bola)
BODY_EXTENT_M = 0.025
SIM_SPACE_COMPONENT, ACC_SCALE, GRAVITY_SCALE = 0, 0.1, 1.0

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
ST = unreal.RetargetSourceOrTarget


def log(msg):
    unreal.log(f"[Jerangkong] {msg}")


def fresh(folder, name, cls, factory):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    return asset_tools.create_asset(name, folder, cls, factory)


def make_ik_rig(name, mesh):
    rig = fresh(f"{JK}/Rig", name, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    c = unreal.IKRigController.get_controller(rig)
    c.set_skeletal_mesh(mesh)
    c.apply_auto_generated_retarget_definition()
    c.apply_auto_fbik()
    log(f"{name}: root={c.get_retarget_root()} chain={len(c.get_retarget_chains())}")
    EAL.save_loaded_asset(rig, only_if_is_dirty=False)
    return rig


def detach_bp_anim(bp_path):
    if EAL.does_asset_exist(bp_path):
        bp = EAL.load_asset(bp_path)
        unreal.get_default_object(bp.generated_class()).get_editor_property("mesh").set_editor_property("anim_class", None)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        EAL.save_loaded_asset(bp, only_if_is_dirty=False)
        unreal.SystemLibrary.collect_garbage()


def scale_blendspace(path, factor):
    src = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/BS_Idle_Walk_Run")
    bs = EAL.load_asset(path)
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


def setup_variant(v, cfg, ik_m, manny):
    mesh = EAL.load_asset(f"{JK}/Mesh/{cfg['mesh']}")
    ik = make_ik_rig(f"IK_{v}", mesh)
    rtg = fresh(f"{JK}/Rig", f"RTG_Mannequin_To_{v}", unreal.IKRetargeter, unreal.IKRetargetFactory())
    r = unreal.IKRetargeterController.get_controller(rtg)
    r.set_ik_rig(ST.SOURCE, ik_m)
    r.set_ik_rig(ST.TARGET, ik)
    r.set_preview_mesh(ST.SOURCE, manny)
    r.set_preview_mesh(ST.TARGET, mesh)
    r.add_default_ops()
    r.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    r.auto_align_bones(ALIGN_BONES, unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN, ST.TARGET)
    i = r.get_index_of_op_by_name("Run IK Rig")              # FK murni (sama dengan Jayadwara: FBIK menggeser pinggul)
    if i >= 0:
        r.set_retarget_op_enabled(i, False)
    EAL.save_loaded_asset(rtg, only_if_is_dirty=False)

    dest = f"{JK}/Anims_{v}"
    detach_bp_anim(f"{JK}/BP_{v}")
    for a in (EAL.list_assets(dest, recursive=True) if EAL.does_directory_exist(dest) else []):
        EAL.delete_asset(str(a).split(".")[0])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unreal.JDEditorToolsLibrary.retarget_assets_to_folder([EAL.load_asset(a) for a in ANIMS], manny, mesh, rtg,
                                                              dest, cfg["suffix"], True)
    EAL.save_directory(dest, only_if_is_dirty=False, recursive=True)
    abp_path = f"{dest}/ABP_{v}"
    EAL.rename_asset(f"{dest}/ABP_Unarmed{cfg['suffix']}", abp_path)
    abp = EAL.load_asset(abp_path)
    n_cr = unreal.JDEditorToolsLibrary.bypass_anim_graph_nodes(abp, "ControlRig")
    k = cfg["scale"] * 100.0                                 # m model -> cm mesh ter-bake
    chains = []
    for start, end, swing, twist in (CLOTH if cfg["cloth_dynamics"] else []):
        c = unreal.JDAnimDynamicsChain()
        c.set_editor_property("start_bone", start)
        c.set_editor_property("end_bone", end)
        c.set_editor_property("swing_limit", swing)
        c.set_editor_property("twist_limit", twist)
        e = BODY_EXTENT_M * k
        c.set_editor_property("box_extents", unreal.Vector(e, e, e))
        c.set_editor_property("collision_radius", e)
        chains.append(c)
    n_ad = unreal.JDEditorToolsLibrary.add_anim_dynamics_chains(abp, chains, CLOTH_LIMIT_BONES, CLOTH_LIMIT_M * k,
                                                                SIM_SPACE_COMPONENT, ACC_SCALE, GRAVITY_SCALE)
    EAL.save_loaded_asset(abp, only_if_is_dirty=False)
    if v == "Jerangkong":
        scale_blendspace(f"{dest}/BS_Idle_Walk_Run{cfg['suffix']}", math.sqrt(cfg["scale"]))   # = sqrt(skala raksasa), sama dengan Jayadwara
    pa = EAL.load_asset(f"{JK}/Mesh/PA_{v}")
    n_pa = unreal.JDEditorToolsLibrary.rebuild_physics_asset(pa, mesh, PA_BODIES, PA_EXCLUDE, 30.0)
    EAL.save_loaded_asset(pa, only_if_is_dirty=False)
    names = sorted(str(n).rsplit("/", 1)[1].split(".")[0] for n in EAL.list_assets(dest, recursive=False))
    log(f"{v}: {len(names)} aset anim, ControlRig dilepas {n_cr}, Anim Dynamics {n_ad}, PA {n_pa} body")
    return mesh, abp


def make_bp(name, parent):
    path = f"{JK}/{name}"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", parent)
    return asset_tools.create_asset(name, JK, unreal.Blueprint, f)


def setup_bps(meshes):
    # boss: AJDGiantCharacter, skala raksasa = tinggi mesh / tinggi model
    bp = make_bp("BP_Jerangkong", unreal.JDGiantCharacter)
    d = unreal.get_default_object(bp.generated_class())
    h = MODEL_H_CM * VARIANTS["Jerangkong"]["scale"]
    for prop, val in (("giant_height_cm", h), ("mesh_height_cm", h), ("authored_height_cm", MODEL_H_CM),
                      ("authored_capsule_radius", 45.0), ("authored_capsule_half_height", MODEL_H_CM / 2)):
        d.set_editor_property(prop, val)
    m = d.get_editor_property("mesh")
    m.set_editor_property("skeletal_mesh_asset", meshes["Jerangkong"][0])
    m.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    m.set_editor_property("anim_class", meshes["Jerangkong"][1].generated_class())
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)
    log(f"BP_Jerangkong: tinggi {h:.0f} cm, skala raksasa {unreal.get_default_object(bp.generated_class()).get_giant_scale():.2f}")

    # minion: Character biasa
    bpk = make_bp("BP_Kerangka", unreal.Character)
    d = unreal.get_default_object(bpk.generated_class())
    hh = MODEL_H_CM * VARIANTS["Kerangka"]["scale"] / 2
    cap = d.get_editor_property("capsule_component")
    cap.set_editor_property("capsule_half_height", hh)
    cap.set_editor_property("capsule_radius", 34.0)
    m = d.get_editor_property("mesh")
    m.set_editor_property("skeletal_mesh_asset", meshes["Kerangka"][0])
    m.set_editor_property("relative_location", unreal.Vector(0, 0, -hh))
    m.set_editor_property("relative_rotation", unreal.Rotator(roll=0, pitch=0, yaw=-90))
    m.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    m.set_editor_property("anim_class", meshes["Kerangka"][1].generated_class())
    unreal.BlueprintEditorLibrary.compile_blueprint(bpk)
    EAL.save_loaded_asset(bpk, only_if_is_dirty=False)
    log(f"BP_Kerangka: kapsul r34 hh{hh:.0f}")
    return bp, bpk


def ground_z(world, x, y):
    hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 100000), unreal.Vector(x, y, -100000),
                                                 unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
                                                 unreal.DrawDebugTrace.NONE, True)
    return hit.to_tuple()[4].z if hit and hit.to_tuple()[0] else 0.0


def place(map_path, bp, spots, half_h, tag):
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level(map_path)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith(tag):
            eas.destroy_actor(a)
    if not PLACE_IN_LEVELS:
        les.save_current_level()
        log(f"{map_path.rsplit('/', 1)[1]}: aktor {tag}* dihapus (PLACE_IN_LEVELS = False)")
        return
    ps = next((a for a in eas.get_all_level_actors() if isinstance(a, unreal.PlayerStart)), None)
    base = ps.get_actor_location() if ps else unreal.Vector(0, 0, 0)
    for i, (dx, dy, yaw) in enumerate(spots):
        x, y = base.x + dx, base.y + dy
        z = ground_z(world, x, y) + half_h + 5
        a = eas.spawn_actor_from_class(bp.generated_class(), unreal.Vector(x, y, z), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
        a.set_actor_label(f"{tag}{i + 1:02d}")
    les.save_current_level()
    log(f"{map_path.rsplit('/', 1)[1]}: {len(spots)} x {tag}")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jerangkong] PIE sedang jalan — hentikan Play dulu")
        return
    ik_m = EAL.load_asset(IK_MANNY)
    manny = EAL.load_asset(MANNY)
    meshes = {v: setup_variant(v, cfg, ik_m, manny) for v, cfg in VARIANTS.items()}
    bp, bpk = setup_bps(meshes)
    giant_half = MODEL_H_CM * VARIANTS["Jerangkong"]["scale"] / 2
    # PlayerStart Test_GiantScale (2000, 0) menghadap -X; boss ±41 m di depan-kiri di area terbuka (tidak tertutup
    # Building_1_30m), menghadap pemain (yaw 39°)
    place("/Game/Jayadwara/Maps/Test_GiantScale", bp, [(-3200, -2600, 39)], giant_half, "JK_Boss_")
    place("/Game/Jayadwara/Maps/Test_Greybox", bpk, [(600, -250, 180), (700, 0, 180), (600, 250, 180)],
          MODEL_H_CM * VARIANTS["Kerangka"]["scale"] / 2, "JK_Minion_")


main()
