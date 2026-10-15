"""Fase 1 Iterasi 2 — combo pukulan ringan: montage, Gameplay Cue SFX, combat profile, dummy (Unreal Editor Python).

Butuh: build C++ Iterasi 2 (UJDGA_LightAttack, UJDCombatProfile, UJDTrainingDummy, notify JD Hit/Combo Window),
hasil Tools/ue_setup_combat.py (Iterasi 1), dan SFX slot 01–02 sudah diimport (Tools/ue_import_audio.py).
Pakai: python Tools/ue_remote.py Tools/ue_setup_light_combo.py
Membuat / mengisi ulang (aman diulang):
  Aksa/Anims/Attack/A_Aksa_Attack_01..03     salinan MM_Attack_01..03 (Mannequin; root motion) + curve DisableLegIK = 1
  ABP_Aksa                                    node Control Rig foot IK dilepas (tanpa ini tendangan ditarik ke tanah)
  Aksa/Anims/Montages/AM_Aksa_Light_01..03   dari salinan di atas, notify track "Combat":
                                              JD Hit Window (tulang & waktu dari analisis kecepatan tangan/kaki) +
                                              JD Combo Window (langkah 1–2)
  Abilities/GameplayCues/GC_Hit_Light, GC_Hit_Heavy   JDGameplayCueNotify_Sound + S_Combat_Punch_*
  Data/DA_CombatProfile_Human                3 langkah (damage 10/10/18), shake JDCameraShake_Hit, hit-stop 0,06 s
  Data/DA_AbilitySet_Aksa                    + JDGA_LightAttack pada Input.Attack.Light
  Data/DA_AbilitySet_Dummy, Characters/Dummy/BP_TrainingDummy (Manny, ABP_Unarmed)
  BP_Aksa: combat_profile;  Test_Combat: 1 dummy di tengah arena menghadap PlayerStart
Animasi placeholder: ganti dengan Jab/Cross/Hook Mixamo cukup dengan mengganti SOURCE + waktu di STEPS lalu jalankan ulang.
"""
import unreal

ATTACK = "/Game/Characters/Mannequins/Anims/Unarmed/Attack"
MONTAGES = "/Game/Jayadwara/Characters/Aksa/Anims/Montages"
SEQS = "/Game/Jayadwara/Characters/Aksa/Anims/Attack"
ABP = "/Game/Jayadwara/Characters/Aksa/Anims/ABP_Aksa"
LEG_IK_CURVE = "DisableLegIK"
CUES = "/Game/Jayadwara/Abilities/GameplayCues"
DATA = "/Game/Jayadwara/Data"
DUMMY = "/Game/Jayadwara/Characters/Dummy"
AUDIO = "/Game/Jayadwara/Audio/Combat"
MAP = "/Game/Jayadwara/Maps/Test_Combat"

# Waktu (s, laju 1,0) dari analisis kecepatan tulang MM_Attack_* (12 Okt 2026): puncak tangan kanan 0,40 s, tangan kiri
# 0,40 s, tendangan kanan 0,33 s (+ ayunan kedua 0,55–0,72 s). Hit window mengapit puncak; combo window setelahnya.
STEPS = [
    {"name": "AM_Aksa_Light_01", "seq": "A_Aksa_Attack_01", "source": f"{ATTACK}/MM_Attack_01", "damage": 10.0, "poise": 5.0,
     "hit": ("hand_r", 0.28, 0.20), "combo": (0.45, 0.35)},
    {"name": "AM_Aksa_Light_02", "seq": "A_Aksa_Attack_02", "source": f"{ATTACK}/MM_Attack_02", "damage": 10.0, "poise": 5.0,
     "hit": ("hand_l", 0.30, 0.20), "combo": (0.48, 0.34)},
    {"name": "AM_Aksa_Light_03", "seq": "A_Aksa_Attack_03", "source": f"{ATTACK}/MM_Attack_03", "damage": 18.0, "poise": 15.0,
     "hit": ("foot_r", 0.24, 0.48), "combo": None},
]
CUE_SETS = {"GC_Hit_Light": ("GameplayCue.Hit.Light", "S_Combat_Punch_Light"),
            "GC_Hit_Heavy": ("GameplayCue.Hit.Heavy", "S_Combat_Punch_Heavy")}
DUMMY_ATTRIBUTES = {"max_health": 200.0, "max_stamina": 0.0, "max_poise": 20.0, "max_sync": 0.0,
                    "max_transform_energy": 0.0, "stamina_regen_per_second": 0.0}

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
problems = []


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def fail(msg):
    problems.append(msg)
    unreal.log_error(f"[Jayadwara] {msg}")


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


def make_bp(folder, name, parent):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", parent)
    bp = asset_tools.create_asset(name, folder, unreal.Blueprint, f)
    log(f"{name} dibuat")
    return bp


def ensure_data_asset(name, cls):
    path = f"{DATA}/{name}"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    f = unreal.DataAssetFactory()
    f.set_editor_property("data_asset_class", cls)
    a = asset_tools.create_asset(name, DATA, cls, f)
    log(f"{name} dibuat")
    return a


def compile_save(bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)


# ------------------------------------------------------------------ foot IK
def setup_leg_ik():
    """Lepas node Control Rig foot IK dari ABP_Aksa (sama seperti ABP Jerangkong, docs/20).

    Node itu menarik telapak kaki ke tanah setiap frame, jadi tendangan montage tidak terlihat (kaki kanan 29 cm,
    seharusnya 113 cm pada 0,33 s). Mematikannya lewat alpha curve tidak bisa dari Python karena AlphaCurveName
    terpasang sebagai pin di graph. Akibat: telapak kaki tidak menyesuaikan tangga/miring (tidak penting di greybox).
    Curve DisableLegIK tetap ditaruh di animasi serangan untuk foot IK versi F2.
    """
    abp = load(ABP)
    if not abp:
        return
    removed = unreal.JDEditorToolsLibrary.bypass_anim_graph_nodes(abp, "ControlRig")
    EAL.save_loaded_asset(abp, only_if_is_dirty=False)
    log(f"ABP_Aksa: {removed} node Control Rig foot IK dilepas" if removed else "ABP_Aksa: foot IK sudah dilepas")


def ensure_sequence(step):
    """Salinan animasi sumber di folder Aksa + curve DisableLegIK = 1 sepanjang animasi (sumber Mannequin tidak diubah)."""
    path = f"{SEQS}/{step['seq']}"
    if EAL.does_asset_exist(path):
        seq = EAL.load_asset(path)
    else:
        seq = EAL.duplicate_asset(step["source"], path)
        log(f"{step['seq']} disalin dari {step['source'].rsplit('/', 1)[1]}")
    if AL.does_curve_exist(seq, LEG_IK_CURVE, unreal.RawCurveTrackTypes.RCT_FLOAT):
        AL.remove_curve(seq, LEG_IK_CURVE, False)
    AL.add_curve(seq, LEG_IK_CURVE, unreal.RawCurveTrackTypes.RCT_FLOAT, False)
    length = AL.get_sequence_length(seq)
    AL.add_float_curve_keys(seq, LEG_IK_CURVE, [0.0, length], [1.0, 1.0])
    EAL.save_loaded_asset(seq, only_if_is_dirty=False)
    return seq


# ------------------------------------------------------------------ montage
def ensure_montage(step):
    path = f"{MONTAGES}/{step['name']}"
    src = ensure_sequence(step)
    seq_path = f"{SEQS}/{step['seq']}"
    if EAL.does_asset_exist(path) and path not in [p.split(".")[0] for p in EAL.find_package_referencers_for_asset(seq_path, False)]:
        EAL.delete_asset(path)                                   # montage lama masih menunjuk animasi Mannequin asli
        log(f"{step['name']} dibuat ulang dari salinan")
    if EAL.does_asset_exist(path):
        m = EAL.load_asset(path)
    else:
        if not src:
            return None
        f = unreal.AnimMontageFactory()
        f.set_editor_property("source_animation", src)
        m = asset_tools.create_asset(step["name"], MONTAGES, unreal.AnimMontage, f)
        log(f"{step['name']} dibuat dari {src.get_name()}")

    # Masuk cepat supaya combo terasa responsif, keluar agak halus.
    for prop, t in (("blend_in", 0.08), ("blend_out", 0.2)):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t)
        m.set_editor_property(prop, b)

    track = "Combat"
    if track in [str(n) for n in AL.get_animation_notify_track_names(m)]:
        AL.remove_animation_notify_events_by_track(m, track)
    else:
        AL.add_animation_notify_track(m, track, unreal.LinearColor(1.0, 0.3, 0.2, 1.0))

    socket, start, dur = step["hit"]
    hit = AL.add_animation_notify_state_event(m, track, start, dur, unreal.JDAnimNotifyState_HitWindow)
    hit.set_editor_property("socket_name", socket)
    if step["combo"]:
        AL.add_animation_notify_state_event(m, track, step["combo"][0], step["combo"][1], unreal.JDAnimNotifyState_ComboWindow)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    return m


# ------------------------------------------------------------------ cue & data
def setup_cues():
    for name, (cue_tag, sound_base) in CUE_SETS.items():
        sounds = [EAL.load_asset(p.split(".")[0]) for p in EAL.list_assets(AUDIO, False, False)
                  if p.rsplit("/", 1)[1].startswith(sound_base + "_") or p.rsplit("/", 1)[1].split(".")[0] == sound_base]
        sounds = [s for s in sounds if isinstance(s, unreal.SoundBase)]
        if not sounds:
            fail(f"{name}: suara {sound_base}* belum ada di {AUDIO} (jalankan Tools/ue_import_audio.py)")
        bp = make_bp(CUES, name, unreal.JDGameplayCueNotify_Sound)
        d = unreal.get_default_object(bp.generated_class())
        d.set_editor_property("gameplay_cue_tag", tag(cue_tag))
        d.set_editor_property("sounds", sounds)
        compile_save(bp)
        log(f"{name}: {cue_tag}, {len(sounds)} variasi suara")


def setup_profile(montages):
    prof = ensure_data_asset("DA_CombatProfile_Human", unreal.JDCombatProfile)
    steps = []
    for step, m in zip(STEPS, montages):
        s = unreal.JDAttackStep()
        s.set_editor_property("montage", m)
        s.set_editor_property("damage", step["damage"])
        s.set_editor_property("poise_damage", step["poise"])
        s.set_editor_property("hit_cue", tag("GameplayCue.Hit.Light"))
        steps.append(s)
    prof.set_editor_property("light_combo", steps)
    prof.set_editor_property("montage_play_rate", 1.0)
    prof.set_editor_property("hit_radius", 30.0)
    prof.set_editor_property("hit_stop_duration", 0.06)
    prof.set_editor_property("hit_stop_time_dilation", 0.05)
    prof.set_editor_property("hit_camera_shake", unreal.JDCameraShake_Hit.static_class())
    prof.set_editor_property("hit_camera_shake_scale", 1.0)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log("DA_CombatProfile_Human terisi")
    return prof


def setup_aksa(prof):
    aset = load(f"{DATA}/DA_AbilitySet_Aksa")
    if aset:
        entry = unreal.JDAbilitySet_Ability()
        entry.set_editor_property("ability", unreal.JDGA_LightAttack.static_class())
        entry.set_editor_property("input_tag", tag("Input.Attack.Light"))
        # Ability lain (berat/dodge/tangkis dari ue_setup_defense.py) dipertahankan.
        others = [e for e in aset.get_editor_property("abilities")
                  if e.get_editor_property("ability") != unreal.JDGA_LightAttack.static_class()]
        aset.set_editor_property("abilities", [entry] + others)
        EAL.save_loaded_asset(aset, only_if_is_dirty=False)
        log("DA_AbilitySet_Aksa: JDGA_LightAttack -> Input.Attack.Light")
    aksa = load("/Game/Jayadwara/Characters/Aksa/BP_Aksa")
    if aksa:
        d = unreal.get_default_object(aksa.generated_class())
        d.get_editor_property("combat_component").set_editor_property("combat_profile", prof)
        compile_save(aksa)
        log("BP_Aksa: combat_profile = DA_CombatProfile_Human")


def setup_dummy():
    aset = ensure_data_asset("DA_AbilitySet_Dummy", unreal.JDAbilitySet)
    attrs = aset.get_editor_property("attributes")
    for k, v in DUMMY_ATTRIBUTES.items():
        attrs.set_editor_property(k, v)
    aset.set_editor_property("attributes", attrs)
    EAL.save_loaded_asset(aset, only_if_is_dirty=False)

    bp = make_bp(DUMMY, "BP_TrainingDummy", unreal.JDTrainingDummy)
    d = unreal.get_default_object(bp.generated_class())
    mesh = d.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh_asset", load("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"))
    abp = load("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed")
    if abp:
        mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
        mesh.set_editor_property("anim_class", abp.generated_class())
    mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -96.0))
    mesh.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
    d.set_editor_property("ability_set", aset)
    compile_save(bp)
    log("BP_TrainingDummy siap")
    return bp


def place_dummy(bp):
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level(MAP)
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("Dummy_"):
            eas.destroy_actor(a)
    ps = next((a for a in eas.get_all_level_actors() if isinstance(a, unreal.PlayerStart)), None)
    base = ps.get_actor_location() if ps else unreal.Vector(-1200, 0, 100)
    # 4 m di depan PlayerStart, menghadap pemain.
    a = eas.spawn_actor_from_class(bp.generated_class(), unreal.Vector(base.x + 400, base.y, 98),
                                   unreal.Rotator(roll=0, pitch=0, yaw=180))
    a.set_actor_label("Dummy_01")
    a.set_folder_path("Combat")
    les.save_current_level()
    log("Test_Combat: Dummy_01 ditaruh 4 m di depan PlayerStart")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara] PIE sedang jalan — hentikan Play dulu")
        return
    if not hasattr(unreal, "JDGA_LightAttack"):
        unreal.log_error("[Jayadwara] C++ Iterasi 2 belum ter-build (JDGA_LightAttack tidak ada)")
        return
    setup_leg_ik()
    montages = [ensure_montage(s) for s in STEPS]
    setup_cues()
    prof = setup_profile(montages)
    setup_aksa(prof)
    place_dummy(setup_dummy())
    if problems:
        unreal.log_warning(f"[Jayadwara] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("setup combo ringan Iterasi 2 selesai")


main()
