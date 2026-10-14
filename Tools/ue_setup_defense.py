"""Fase 1 Iterasi 3 — pukulan berat, dodge, tangkis + parry, dummy menyerang (Unreal Editor Python).

Butuh: build C++ Iterasi 3 (UJDGA_HeavyAttack/Dodge/Block, JDTrainingDummy mode menyerang), hasil
ue_setup_light_combo.py (Iterasi 2) dan SFX slot 03–05 sudah diimport (Audio/pilihan.json + Tools/ue_import_audio.py).
Pakai: python Tools/ue_remote.py Tools/ue_setup_defense.py
Membuat / mengisi ulang (aman diulang):
  Aksa/Anims/Montages/AM_Aksa_Heavy     dari A_Aksa_Attack_02 (hook kiri dengan rendah badan), diputar 0,75x
  Aksa/Anims/Montages/AM_Aksa_Block     dari A_Aksa_Attack_02; frame BLOCK_HOLD (kedua kepalan di depan dagu) ditahan
  Aksa/Anims/Attack/A_Aksa_Stagger + Montages/AM_Aksa_Stagger   dari MM_HitReact_Front_Hvy_01 (Rifle, placeholder)
  GC_Hit_Blocked, GC_Parry, GC_Dodge     JDGameplayCueNotify_Sound + S_Combat_Block/Parry/Dodge
  DA_CombatProfile_Human                 + pukulan berat, dodge, tangkis/parry, stagger (angka docs/23 bagian 5)
  DA_AbilitySet_Aksa                     ringan + berat (E) + dodge (Shift) + tangkis (RMB)
  DA_CombatProfile_Dummy, DA_AbilitySet_Dummy (+ pukulan ringan tanpa input), BP_TrainingDummy (profil)
  Test_Combat: Dummy_Attacker (mode menyerang) 5 m di samping Dummy_01
Animasi placeholder (Mixamo menyusul, docs/23 bagian 6.1): ganti SOURCE/waktu di HEAVY/BLOCK/STAGGER lalu jalankan ulang.
Dodge belum punya animasi (gerak dari root motion source); isi DODGE_SOURCES kalau animasi dodge 4 arah sudah ada.
"""
import unreal

AKSA = "/Game/Jayadwara/Characters/Aksa"
SEQS = f"{AKSA}/Anims/Attack"
MONTAGES = f"{AKSA}/Anims/Montages"
CUES = "/Game/Jayadwara/Abilities/GameplayCues"
DATA = "/Game/Jayadwara/Data"
AUDIO = "/Game/Jayadwara/Audio/Combat"
DUMMY = "/Game/Jayadwara/Characters/Dummy/BP_TrainingDummy"
MAP = "/Game/Jayadwara/Maps/Test_Combat"

# Waktu dalam detik animasi; analisis tulang 13 Okt 2026 (A_Aksa_Attack_02: badan turun 0,2–0,3 s, tangan kiri paling
# depan 0,5 s; 0,7–0,8 s kedua kepalan setinggi dagu di depan badan).
HEAVY = {"name": "AM_Aksa_Heavy", "seq": f"{SEQS}/A_Aksa_Attack_02", "hit": ("hand_l", 0.32, 0.24),
         "damage": 30.0, "poise": 40.0, "stamina": 25.0, "rate": 0.75}
BLOCK = {"name": "AM_Aksa_Block", "seq": f"{SEQS}/A_Aksa_Attack_02", "hold": 0.75}
STAGGER = {"name": "AM_Aksa_Stagger", "seq": f"{SEQS}/A_Aksa_Stagger",
           "source": "/Game/Characters/Mannequins/Anims/Rifle/HitReact/MM_HitReact_Front_Hvy_01"}
DODGE_SOURCES = {}     # {"Forward": "/Game/.../A_Aksa_Dodge_F", ...} (montage dibuat AM_Aksa_Dodge_<arah>)

HUMAN = {"dodge_distance": 400.0, "dodge_duration": 0.35, "dodge_i_frame_start": 0.0, "dodge_i_frame_duration": 0.25,
         "dodge_stamina_cost": 20.0, "block_hold_time": BLOCK["hold"], "block_damage_reduction": 0.8,
         "block_stamina_per_hit": 15.0, "block_angle": 140.0, "block_move_speed_scale": 0.4, "block_pushback": 300.0,
         "guard_break_stagger_duration": 1.0, "parry_window": 0.2, "parry_lockout": 0.5, "parry_stagger_duration": 1.0}
CUE_SETS = {"GC_Hit_Blocked": ("GameplayCue.Hit.Blocked", "S_Combat_Block"),
            "GC_Parry": ("GameplayCue.Parry", "S_Combat_Parry"),
            "GC_Dodge": ("GameplayCue.Dodge", "S_Combat_Dodge")}

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


def make_montage(folder, name, seq_path, hit=None, blend_in=0.08, blend_out=0.2):
    """Montage baru dari seq_path (dibuat ulang tiap jalan), opsional dengan JD Hit Window."""
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    seq = load(seq_path)
    if not seq:
        return None
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset(name, folder, unreal.AnimMontage, f)
    for prop, t in (("blend_in", blend_in), ("blend_out", blend_out)):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t)
        m.set_editor_property(prop, b)
    if hit:
        AL.add_animation_notify_track(m, "Combat", unreal.LinearColor(1.0, 0.3, 0.2, 1.0))
        n = AL.add_animation_notify_state_event(m, "Combat", hit[1], hit[2], unreal.JDAnimNotifyState_HitWindow)
        n.set_editor_property("socket_name", hit[0])
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    log(f"{name} dari {seq_path.rsplit('/', 1)[1]}")
    return m


def attack_step(montage, damage, poise, stamina, rate, cue):
    s = unreal.JDAttackStep()
    s.set_editor_property("montage", montage)
    s.set_editor_property("damage", damage)
    s.set_editor_property("poise_damage", poise)
    s.set_editor_property("stamina_cost", stamina)
    s.set_editor_property("play_rate", rate)
    s.set_editor_property("hit_cue", tag(cue))
    return s


def upsert_abilities(aset, entries):
    """Ganti/tambah ability per kelas tanpa membuang ability lain di set."""
    keep = [e for e in aset.get_editor_property("abilities")
            if e.get_editor_property("ability") not in [c for c, _ in entries]]
    for cls, input_tag in entries:
        e = unreal.JDAbilitySet_Ability()
        e.set_editor_property("ability", cls)
        if input_tag:
            e.set_editor_property("input_tag", tag(input_tag))
        keep.append(e)
    aset.set_editor_property("abilities", keep)
    EAL.save_loaded_asset(aset, only_if_is_dirty=False)


# ------------------------------------------------------------------ aset
def setup_stagger_seq():
    if not EAL.does_asset_exist(STAGGER["seq"]):
        EAL.duplicate_asset(STAGGER["source"], STAGGER["seq"])
        log("A_Aksa_Stagger disalin dari MM_HitReact_Front_Hvy_01")
    return make_montage(MONTAGES, STAGGER["name"], STAGGER["seq"], blend_in=0.05, blend_out=0.25)


def setup_cues():
    for name, (cue_tag, sound_base) in CUE_SETS.items():
        sounds = [EAL.load_asset(p.split(".")[0]) for p in EAL.list_assets(AUDIO, False, False)
                  if p.rsplit("/", 1)[1].split(".")[0] == sound_base or p.rsplit("/", 1)[1].startswith(sound_base + "_")]
        sounds = [s for s in sounds if isinstance(s, unreal.SoundBase)]
        if not sounds:
            fail(f"{name}: suara {sound_base}* belum ada di {AUDIO} (jalankan Tools/ue_import_audio.py)")
        bp = make_bp(CUES, name, unreal.JDGameplayCueNotify_Sound)
        d = unreal.get_default_object(bp.generated_class())
        d.set_editor_property("gameplay_cue_tag", tag(cue_tag))
        d.set_editor_property("sounds", sounds)
        compile_save(bp)
        log(f"{name}: {cue_tag}, {len(sounds)} variasi suara")


def fill_defense(prof, values, block_montage, stagger_montage, dodge_montages):
    for k, v in values.items():
        prof.set_editor_property(k, v)
    prof.set_editor_property("block_montage", block_montage)
    prof.set_editor_property("stagger_montage", stagger_montage)
    dm = unreal.JDDirectionalMontages()
    for k, m in dodge_montages.items():
        dm.set_editor_property(k.lower(), m)
    prof.set_editor_property("dodge_montages", dm)


def setup_human(stagger):
    heavy = make_montage(MONTAGES, HEAVY["name"], HEAVY["seq"], HEAVY["hit"])
    block = make_montage(MONTAGES, BLOCK["name"], BLOCK["seq"], blend_in=0.1, blend_out=0.15)
    dodges = {d: make_montage(MONTAGES, f"AM_Aksa_Dodge_{d}", src, blend_in=0.05, blend_out=0.15)
              for d, src in DODGE_SOURCES.items()}

    prof = load(f"{DATA}/DA_CombatProfile_Human")
    if not prof:
        return
    prof.set_editor_property("heavy_attack", attack_step(heavy, HEAVY["damage"], HEAVY["poise"], HEAVY["stamina"],
                                                         HEAVY["rate"], "GameplayCue.Hit.Heavy"))
    fill_defense(prof, HUMAN, block, stagger, dodges)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log("DA_CombatProfile_Human: berat 30/40/25, dodge 4 m 0,35 s (i-frame 0,25 s), tangkis 80%, parry 0,2 s")

    aset = load(f"{DATA}/DA_AbilitySet_Aksa")
    if aset:
        upsert_abilities(aset, [(unreal.JDGA_LightAttack.static_class(), "Input.Attack.Light"),
                                (unreal.JDGA_HeavyAttack.static_class(), "Input.Attack.Heavy"),
                                (unreal.JDGA_Dodge.static_class(), "Input.Dodge"),
                                (unreal.JDGA_Block.static_class(), "Input.Block")])
        log("DA_AbilitySet_Aksa: ringan, berat (E), dodge (Shift), tangkis (RMB)")


def setup_dummy(stagger):
    prof = ensure_data_asset("DA_CombatProfile_Dummy", unreal.JDCombatProfile)
    light = load(f"{MONTAGES}/AM_Aksa_Light_01")
    prof.set_editor_property("light_combo", [attack_step(light, 10.0, 10.0, 0.0, 1.0, "GameplayCue.Hit.Light")])
    prof.set_editor_property("montage_play_rate", 1.0)
    prof.set_editor_property("hit_radius", 30.0)
    prof.set_editor_property("hit_stop_duration", 0.06)
    prof.set_editor_property("hit_stop_time_dilation", 0.05)
    prof.set_editor_property("stagger_montage", stagger)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)

    aset = load(f"{DATA}/DA_AbilitySet_Dummy")
    if aset:
        upsert_abilities(aset, [(unreal.JDGA_LightAttack.static_class(), None)])

    bp = load(DUMMY)
    if bp:
        d = unreal.get_default_object(bp.generated_class())
        d.get_editor_property("combat_component").set_editor_property("combat_profile", prof)
        compile_save(bp)
        log("BP_TrainingDummy: DA_CombatProfile_Dummy (pukulan 10, stagger), JDGA_LightAttack tanpa input")
    return bp


def place_attacker(bp):
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level(MAP)
    actors = eas.get_all_level_actors()
    for a in actors:
        if a.get_actor_label() == "Dummy_Attacker":
            eas.destroy_actor(a)
    ref = next((a for a in actors if a.get_actor_label() == "Dummy_01"), None)
    ps = next((a for a in actors if isinstance(a, unreal.PlayerStart)), None)
    if not ref or not ps:
        fail("Test_Combat: Dummy_01 / PlayerStart tidak ada (jalankan ue_setup_light_combo.py)")
        return
    loc = ref.get_actor_location()
    a = eas.spawn_actor_from_class(bp.generated_class(), unreal.Vector(loc.x, loc.y + 500.0, loc.z), ref.get_actor_rotation())
    a.set_actor_label("Dummy_Attacker")
    a.set_folder_path("Combat")
    a.set_editor_property("attack_mode", True)
    les.save_current_level()
    log("Test_Combat: Dummy_Attacker (mode menyerang) 5 m di samping Dummy_01")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara] PIE sedang jalan — hentikan Play dulu")
        return
    if not hasattr(unreal, "JDGA_Block"):
        unreal.log_error("[Jayadwara] C++ Iterasi 3 belum ter-build (JDGA_Block tidak ada)")
        return
    stagger = setup_stagger_seq()
    setup_cues()
    setup_human(stagger)
    bp = setup_dummy(stagger)
    if bp:
        place_attacker(bp)
    if problems:
        unreal.log_warning(f"[Jayadwara] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("setup Iterasi 3 selesai")


main()
