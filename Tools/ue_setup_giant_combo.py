"""Fase 1 Iterasi 2–3 (+ awal Iterasi 6) — combat Jayadwara2: combo ringan, berat, dodge, tangkis + parry (Unreal Editor Python).

Ability sama dengan Aksa (JDGA_LightAttack); yang beda hanya montage & DA_CombatProfile_Giant ("satu sistem, dua skala").
Butuh: build C++ dengan kompensasi GlobalAnimRateScale di JDGA_LightAttack (13 Okt 2026), hasil ue_setup_light_combo.py
(GC_Hit_*, BP_TrainingDummy, DA_InputConfig_Human) dan ue_setup_jayadwara2.py (MM_Attack_0x_JD2).
Pakai: python Tools/ue_remote.py Tools/ue_setup_giant_combo.py
Membuat / mengisi ulang (aman diulang; jalankan ulang setelah ue_setup_jayadwara2.py karena animasi dibuat ulang):
  Jayadwara2/Combat/A_JD2_Attack_01..03     salinan MM_Attack_0x_JD2 (ue_setup_jayadwara2.py menghapus isi Anims/ tiap jalan)
  Jayadwara2/Combat/AM_JD2_Light_01..03     notify JD Hit Window + JD Combo Window, waktu sama dengan Aksa (animasi sumber sama)
  Jayadwara2/Combat/AM_JD2_Heavy, AM_JD2_Block   sama dengan AM_Aksa_Heavy/Block (ue_setup_defense.py), dari A_JD2_Attack_02
  Data/DA_CombatProfile_Giant               damage 10/10/18, laju terlihat 0,55, radius hit x skala, hit-stop 0,12 s, shake lebih besar;
                                            berat 30/40/25, dodge & tangkis/parry (GIANT_DEFENSE, parry 0,25 s)
  Data/DA_AbilitySet_Jayadwara              atribut awal (Sync penuh), ringan/berat/dodge/tangkis, buffer input 0,3 s
  BP_Jayadwara2                             ability_set, input_config (DA_InputConfig_Human; IMC_Giant di Iterasi 6), combat_profile
  Test_GiantScale                           Dummy_Giant: BP_TrainingDummy x DUMMY_SCALE, 30 m di depan PlayerStart
"""
import unreal

J2 = "/Game/Jayadwara/Characters/Jayadwara2"
SRC = f"{J2}/Anims"
COMBAT = f"{J2}/Combat"
DATA = "/Game/Jayadwara/Data"
BP = f"{J2}/BP_Jayadwara2"
DUMMY_BP = "/Game/Jayadwara/Characters/Dummy/BP_TrainingDummy"
MAP = "/Game/Jayadwara/Maps/Test_GiantScale"

# Waktu dalam detik animasi (laju 1,0) = sama dengan STEPS di ue_setup_light_combo.py.
STEPS = [
    {"name": "AM_JD2_Light_01", "seq": "A_JD2_Attack_01", "source": f"{SRC}/MM_Attack_01_JD2", "damage": 10.0, "poise": 5.0,
     "hit": ("hand_r", 0.28, 0.20), "combo": (0.45, 0.35)},
    {"name": "AM_JD2_Light_02", "seq": "A_JD2_Attack_02", "source": f"{SRC}/MM_Attack_02_JD2", "damage": 10.0, "poise": 5.0,
     "hit": ("hand_l", 0.30, 0.20), "combo": (0.48, 0.34)},
    {"name": "AM_JD2_Light_03", "seq": "A_JD2_Attack_03", "source": f"{SRC}/MM_Attack_03_JD2", "damage": 18.0, "poise": 15.0,
     "hit": ("foot_r", 0.24, 0.48), "combo": None},
]
HEAVY = {"hit": ("hand_l", 0.32, 0.24), "damage": 30.0, "poise": 40.0, "stamina": 25.0, "rate": 0.75}
BLOCK_HOLD = 0.75
# Detik nyata. Dodge: durasi & i-frame manusia / 0,55 (laju terlihat raksasa), jarak ±0,6 x proporsional skala.
GIANT_DEFENSE = {"dodge_distance": 5500.0, "dodge_duration": 0.64, "dodge_i_frame_start": 0.0, "dodge_i_frame_duration": 0.45,
                 "dodge_stamina_cost": 20.0, "block_hold_time": BLOCK_HOLD, "block_damage_reduction": 0.8,
                 "block_stamina_per_hit": 15.0, "block_angle": 140.0, "block_move_speed_scale": 0.4, "block_pushback": 1500.0,
                 "guard_break_stagger_duration": 1.0, "parry_window": 0.25, "parry_lockout": 0.5, "parry_stagger_duration": 1.0}
PLAY_RATE = 0.55            # laju terlihat (docs/23 bagian 5); ability membagi dengan GlobalAnimRateScale mesh (±0,205)
HUMAN_HIT_RADIUS = 30.0     # x skala raksasa
BLEND_IN_S, BLEND_OUT_S = 0.12, 0.3   # detik nyata; blend montage ikut diperlambat GlobalAnimRateScale
HIT_STOP = 0.12
SHAKE_SCALE = 2.5
GIANT_ATTRIBUTES = {"max_health": 100.0, "max_stamina": 100.0, "max_poise": 100.0, "max_sync": 100.0,
                    "max_transform_energy": 0.0, "stamina_regen_per_second": 25.0, "stamina_regen_delay": 0.8}
INPUT_BUFFER = 0.3
DUMMY_SCALE = 20.0          # Manny 1,8 m -> ±36 m (Jayadwara 45 m)
DUMMY_DISTANCE = 3000.0

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
problems = []


def log(msg):
    unreal.log(f"[Jayadwara2] {msg}")


def fail(msg):
    problems.append(msg)
    unreal.log_error(f"[Jayadwara2] {msg}")


def load(path):
    a = EAL.load_asset(path)
    if a is None:
        fail(f"aset tidak ada: {path}")
    return a


def tag(name):
    t = unreal.JDEditorToolsLibrary.make_gameplay_tag(name)
    if name not in t.export_text():
        fail(f"tag tidak terdaftar: {name}")
    return t


def ensure_data_asset(name, cls):
    path = f"{DATA}/{name}"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    f = unreal.DataAssetFactory()
    f.set_editor_property("data_asset_class", cls)
    a = asset_tools.create_asset(name, DATA, cls, f)
    log(f"{name} dibuat")
    return a


def check_sockets():
    mesh = load(f"{J2}/Mesh/SK_Jayadwara2")
    if not mesh:
        return
    bones = {str(b) for b in unreal.AnimPoseExtensions.get_bone_names(unreal.AnimPoseExtensions.get_reference_pose(mesh.skeleton))}
    for s in STEPS:
        if s["hit"][0] not in bones:
            fail(f"tulang {s['hit'][0]} tidak ada di SK_Jayadwara2")


# ------------------------------------------------------------------ montage
def make_montages(mesh_rate):
    """Buat ulang salinan animasi + montage tiap jalan (sumber MM_Attack_0x_JD2 bisa berubah setelah retarget ulang)."""
    out = []
    for name in ("AM_JD2_Heavy", "AM_JD2_Block"):                # merujuk A_JD2_Attack_02: hapus dulu
        if EAL.does_asset_exist(f"{COMBAT}/{name}"):
            EAL.delete_asset(f"{COMBAT}/{name}")
    for step in STEPS:
        for p in (f"{COMBAT}/{step['name']}", f"{COMBAT}/{step['seq']}"):
            if EAL.does_asset_exist(p):
                EAL.delete_asset(p)
        if not EAL.does_asset_exist(step["source"]):
            fail(f"{step['source']} tidak ada (jalankan ue_setup_jayadwara2.py)")
            out.append(None)
            continue
        seq = EAL.duplicate_asset(step["source"], f"{COMBAT}/{step['seq']}")
        f = unreal.AnimMontageFactory()
        f.set_editor_property("source_animation", seq)
        m = asset_tools.create_asset(step["name"], COMBAT, unreal.AnimMontage, f)

        for prop, t in (("blend_in", BLEND_IN_S), ("blend_out", BLEND_OUT_S)):
            b = m.get_editor_property(prop)
            b.set_editor_property("blend_time", t * mesh_rate)
            m.set_editor_property(prop, b)

        AL.add_animation_notify_track(m, "Combat", unreal.LinearColor(1.0, 0.3, 0.2, 1.0))
        socket, start, dur = step["hit"]
        hit = AL.add_animation_notify_state_event(m, "Combat", start, dur, unreal.JDAnimNotifyState_HitWindow)
        hit.set_editor_property("socket_name", socket)
        if step["combo"]:
            AL.add_animation_notify_state_event(m, "Combat", step["combo"][0], step["combo"][1], unreal.JDAnimNotifyState_ComboWindow)
        EAL.save_loaded_asset(seq, only_if_is_dirty=False)
        EAL.save_loaded_asset(m, only_if_is_dirty=False)
        log(f"{step['name']} dari {step['source'].rsplit('/', 1)[1]} (hit {socket})")
        out.append(m)
    return out


def make_extra_montage(name, seq_path, mesh_rate, blend_in, blend_out, hit=None):
    path = f"{COMBAT}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    seq = load(seq_path)
    if not seq:
        return None
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset(name, COMBAT, unreal.AnimMontage, f)
    for prop, t in (("blend_in", blend_in), ("blend_out", blend_out)):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t * mesh_rate)
        m.set_editor_property(prop, b)
    if hit:
        AL.add_animation_notify_track(m, "Combat", unreal.LinearColor(1.0, 0.3, 0.2, 1.0))
        n = AL.add_animation_notify_state_event(m, "Combat", hit[1], hit[2], unreal.JDAnimNotifyState_HitWindow)
        n.set_editor_property("socket_name", hit[0])
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    log(f"{name} dari {seq_path.rsplit('/', 1)[1]}")
    return m


# ------------------------------------------------------------------ data
def setup_profile(montages, giant_scale, mesh_rate):
    prof = ensure_data_asset("DA_CombatProfile_Giant", unreal.JDCombatProfile)
    steps = []
    for step, m in zip(STEPS, montages):
        s = unreal.JDAttackStep()
        s.set_editor_property("montage", m)
        s.set_editor_property("damage", step["damage"])
        s.set_editor_property("poise_damage", step["poise"])
        s.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))      # suara lebih berat untuk raksasa
        steps.append(s)
    prof.set_editor_property("light_combo", steps)
    prof.set_editor_property("montage_play_rate", PLAY_RATE)
    prof.set_editor_property("hit_radius", HUMAN_HIT_RADIUS * giant_scale)
    prof.set_editor_property("hit_stop_duration", HIT_STOP)
    prof.set_editor_property("hit_stop_time_dilation", 0.05)
    prof.set_editor_property("hit_camera_shake", unreal.JDCameraShake_Hit.static_class())
    prof.set_editor_property("hit_camera_shake_scale", SHAKE_SCALE)

    src = f"{COMBAT}/A_JD2_Attack_02"
    heavy = make_extra_montage("AM_JD2_Heavy", src, mesh_rate, BLEND_IN_S, BLEND_OUT_S, HEAVY["hit"])
    block = make_extra_montage("AM_JD2_Block", src, mesh_rate, 0.15, 0.2)
    h = unreal.JDAttackStep()
    h.set_editor_property("montage", heavy)
    h.set_editor_property("damage", HEAVY["damage"])
    h.set_editor_property("poise_damage", HEAVY["poise"])
    h.set_editor_property("stamina_cost", HEAVY["stamina"])
    h.set_editor_property("play_rate", HEAVY["rate"])
    h.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
    prof.set_editor_property("heavy_attack", h)
    for k, v in GIANT_DEFENSE.items():
        prof.set_editor_property(k, v)
    prof.set_editor_property("block_montage", block)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log(f"DA_CombatProfile_Giant: laju {PLAY_RATE}, radius hit {HUMAN_HIT_RADIUS * giant_scale:.0f} cm, hit-stop {HIT_STOP} s")
    return prof


def setup_ability_set():
    aset = ensure_data_asset("DA_AbilitySet_Jayadwara", unreal.JDAbilitySet)
    attrs = aset.get_editor_property("attributes")
    for k, v in GIANT_ATTRIBUTES.items():
        attrs.set_editor_property(k, v)
    aset.set_editor_property("attributes", attrs)
    entries = []
    for cls, input_tag in ((unreal.JDGA_LightAttack, "Input.Attack.Light"), (unreal.JDGA_HeavyAttack, "Input.Attack.Heavy"),
                           (unreal.JDGA_Dodge, "Input.Dodge"), (unreal.JDGA_Block, "Input.Block")):
        entry = unreal.JDAbilitySet_Ability()
        entry.set_editor_property("ability", cls.static_class())
        entry.set_editor_property("input_tag", tag(input_tag))
        entries.append(entry)
    aset.set_editor_property("abilities", entries)
    aset.set_editor_property("input_buffer_time", INPUT_BUFFER)
    EAL.save_loaded_asset(aset, only_if_is_dirty=False)
    log("DA_AbilitySet_Jayadwara: ringan, berat, dodge, tangkis; buffer 0,3 s")
    return aset


def setup_pawn(bp, aset, prof):
    d = unreal.get_default_object(bp.generated_class())
    d.set_editor_property("ability_set", aset)
    d.set_editor_property("input_config", load(f"{DATA}/DA_InputConfig_Human"))
    d.get_editor_property("combat_component").set_editor_property("combat_profile", prof)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)
    log("BP_Jayadwara2: ability_set, input_config, combat_profile terisi")


def place_dummy():
    dummy = load(DUMMY_BP)
    if not dummy:
        return
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level(MAP)
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("Dummy_Giant"):
            eas.destroy_actor(a)
    ps = next((a for a in eas.get_all_level_actors() if isinstance(a, unreal.PlayerStart)), None)
    if ps is None:
        fail("Test_GiantScale tidak punya PlayerStart")
        return
    fwd = ps.get_actor_forward_vector()
    xy = ps.get_actor_location() + unreal.Vector(fwd.x, fwd.y, 0.0) * DUMMY_DISTANCE
    # Tapak dummy di lantai: trace ke bawah, lalu pusat kapsul = lantai + setengah tinggi kapsul berskala.
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(xy.x, xy.y, xy.z + 50000), unreal.Vector(xy.x, xy.y, xy.z - 50000),
                                                 unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
    floor_z = hit.to_tuple()[4].z if hit and hit.to_tuple()[0] else 0.0
    a = eas.spawn_actor_from_class(dummy.generated_class(), unreal.Vector(xy.x, xy.y, floor_z + 96.0 * DUMMY_SCALE + 5.0),
                                   unreal.Rotator(roll=0, pitch=0, yaw=ps.get_actor_rotation().yaw + 180.0))
    a.set_actor_scale3d(unreal.Vector(DUMMY_SCALE, DUMMY_SCALE, DUMMY_SCALE))
    a.set_actor_label("Dummy_Giant")
    a.set_folder_path("Combat")
    les.save_current_level()
    log(f"Test_GiantScale: Dummy_Giant (x{DUMMY_SCALE:.0f}) {DUMMY_DISTANCE / 100:.0f} m di depan PlayerStart, lantai z={floor_z:.0f}")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara2] PIE sedang jalan — hentikan Play dulu")
        return
    bp = load(BP)
    if not bp:
        return
    d = unreal.get_default_object(bp.generated_class())
    giant_scale = d.get_giant_scale()
    mesh_rate = d.get_editor_property("mesh").get_editor_property("global_anim_rate_scale")
    log(f"skala raksasa {giant_scale:.2f}, GlobalAnimRateScale {mesh_rate:.3f}")
    check_sockets()
    montages = make_montages(mesh_rate)
    prof = setup_profile(montages, giant_scale, mesh_rate)
    setup_pawn(bp, setup_ability_set(), prof)
    place_dummy()
    if problems:
        unreal.log_warning(f"[Jayadwara2] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("combat Jayadwara2 siap: Play di Test_GiantScale (LMB ringan, E berat, Shift dodge, RMB tangkis)")


main()
