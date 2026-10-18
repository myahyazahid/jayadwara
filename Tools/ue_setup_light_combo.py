"""Fase 1 Iterasi 2 — combo pukulan ringan: montage, Gameplay Cue SFX, combat profile, dummy (Unreal Editor Python).

Butuh: build C++ Iterasi 2 (UJDGA_LightAttack, UJDCombatProfile, UJDTrainingDummy, notify JD Hit/Combo Window),
hasil Tools/ue_setup_combat.py (Iterasi 1), dan SFX slot 01–02 sudah diimport (Tools/ue_import_audio.py).
Pakai: python Tools/ue_remote.py Tools/ue_setup_light_combo.py
Membuat / mengisi ulang (aman diulang):
  Aksa/Anims/Attack/A_Aksa_Attack_01..04     salinan MM_Attack_01..03 + MM_ChargedAttack (Mannequin; root motion) + curve DisableLegIK = 1
  ABP_Aksa                                    node Control Rig foot IK dilepas (tanpa ini tendangan ditarik ke tanah)
  Aksa/Anims/Montages/AM_Aksa_Light_01..04   dari salinan di atas, notify track "Combat":
                                              JD Hit Window (tulang & waktu dari analisis kecepatan tangan/kaki) +
                                              JD Combo Window (langkah 1–3)
  Aksa/Anims/Montages/AM_Aksa_Lunge, AM_Aksa_Back   pembuka maju (terjang) & mundur (docs/07 "Combo & arah")
  Aksa/Anims/Montages/AM_Aksa_Finisher_01..03       cabang finisher pukulan berat setelah langkah 1 / 2 / 3
  Aksa/Anims/Attack/A_Aksa_Air, A_Aksa_AirSlam      salinan tanpa root motion (gerak dari lompatan) untuk serangan udara
  Aksa/Anims/Montages/AM_Aksa_Air, AM_Aksa_AirSlam  pukulan udara & hantaman ke bawah (docs/07 "Serangan udara")
  Abilities/GameplayCues/GC_Hit_Light, GC_Hit_Heavy   JDGameplayCueNotify_Sound + S_Combat_Punch_*
  Data/DA_CombatProfile_Human                4 langkah (damage 10/10/12/20), pembuka arah, finisher berat, shake JDCameraShake_Hit, hit-stop 0,06 s
  Data/DA_AbilitySet_Aksa                    + JDGA_LightAttack pada Input.Attack.Light
  Data/DA_AbilitySet_Dummy, Characters/Dummy/BP_TrainingDummy (Manny, ABP_Unarmed)
  BP_Aksa: combat_profile;  Test_Combat: 1 dummy di tengah arena menghadap PlayerStart
Animasi Mixamo: jalankan Tools/ue_import_mixamo.py lalu Tools/ue_mixamo_postproses.py (pangkas + in-place) dulu; langkah
yang punya A_Aksa_Mx_<peran> (kunci "mx") otomatis memakainya (waktu hit otomatis per keluarga tulang, jendela combo di
ekor klip, laju & blend per peran dari hasil tes tangan Hermes 17 Okt), sisanya tetap placeholder Mannequin. Terjang = lompat kecil (move_height).
"hit": "auto" = tulang & waktu dicari dari puncak kecepatan tangan/kaki (relatif pelvis); hasilnya di-log, salin ke STEPS
supaya tetap. Pembuka & finisher memakai ulang animasi langkah (placeholder) sampai animasi Mixamo khusus ada (docs/23 6.1).
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
# Combo 4 pukulan (keputusan developer 16 Okt 2026, docs/07): langkah 4 = finisher, sementara MM_ChargedAttack.
STEPS = [
    {"name": "AM_Aksa_Light_01", "seq": "A_Aksa_Attack_01", "source": f"{ATTACK}/MM_Attack_01", "damage": 10.0, "poise": 5.0,
     "hit": ("hand_r", 0.28, 0.20), "combo": (0.45, 0.35), "mx": "light_01"},
    {"name": "AM_Aksa_Light_02", "seq": "A_Aksa_Attack_02", "source": f"{ATTACK}/MM_Attack_02", "damage": 10.0, "poise": 5.0,
     "hit": ("hand_l", 0.30, 0.20), "combo": (0.48, 0.34), "mx": "light_02"},
    {"name": "AM_Aksa_Light_03", "seq": "A_Aksa_Attack_03", "source": f"{ATTACK}/MM_Attack_03", "damage": 12.0, "poise": 8.0,
     "hit": ("foot_r", 0.24, 0.48), "combo": (0.69, 0.35), "mx": "light_03"},
    {"name": "AM_Aksa_Light_04", "seq": "A_Aksa_Attack_04", "source": f"{ATTACK}/MM_ChargedAttack", "damage": 20.0, "poise": 20.0,
     "hit": "auto", "combo": None, "combo_mx": True, "mx": "light_04"},
]
# Pembuka arah (docs/07 "Combo & arah"): menggantikan langkah 1, combo lanjut ke langkah 2. Gerak dari root motion source.
OPENERS = {
    "lunge_attack": {"name": "AM_Aksa_Lunge", "seq": "A_Aksa_Attack_01", "damage": 10.0, "poise": 8.0,
                     "hit": ("hand_r", 0.28, 0.20), "combo": (0.45, 0.35),
                     "move_distance": 600.0, "move_duration": 0.35, "move_height": 60.0, "stop_at_target": True,
                     "mx": "lunge"},
    "back_attack": {"name": "AM_Aksa_Back", "seq": "A_Aksa_Attack_03", "damage": 10.0, "poise": 8.0,
                    "hit": ("foot_r", 0.24, 0.48), "radius": 50.0, "combo": (0.69, 0.35),
                    "move_distance": -150.0, "move_duration": 0.25, "stop_at_target": False, "mx": "back"},
}
DIRECTION = {"target_search_radius": 800.0, "lunge_min_distance": 250.0, "lunge_stop_distance": 100.0,
             "direction_threshold": 0.5}
# Cabang finisher pukulan berat setelah langkah 1 / 2 / 3 (slot kosong = AM_Aksa_Heavy dari ue_setup_defense.py).
# Finisher 3 tanpa placeholder: hanya terisi kalau animasi Mixamo finisher_03 ada ("mx_only").
# Stamina & damage sama dengan pukulan berat (docs/23 bagian 5).
FINISHERS = [
    {"name": "AM_Aksa_Finisher_01", "seq": "A_Aksa_Attack_03", "hit": ("foot_r", 0.24, 0.48), "rate": 0.8, "mx": "finisher_01"},
    {"name": "AM_Aksa_Finisher_02", "seq": "A_Aksa_Attack_04", "hit": "auto", "rate": 0.85, "mx": "finisher_02", "mx_hits": 2,
     # narae chagi (klip 18 Okt): dua tendangan berjarak < 0,2 s (batas auto) -> jendela dipasang tangan, tidak bertumpuk
     "mx_hit": [("foot_r", 0.40, 0.24), ("foot_r", 0.70, 0.24)]},
    {"name": "AM_Aksa_Finisher_03", "hit": "auto", "rate": 1.0, "mx": "finisher_03", "mx_only": True},
]
HEAVY = {"damage": 30.0, "poise": 40.0, "stamina": 25.0}
# Serangan udara (docs/07 "Serangan udara", 16 Okt 2026). Salinan animasi tanpa root motion supaya tidak melayang/tertahan.
AIR = {"name": "AM_Aksa_Air", "seq": "A_Aksa_Air", "source": f"{ATTACK}/MM_Attack_03", "damage": 10.0, "poise": 5.0,
       "hit": ("foot_r", 0.24, 0.48), "combo": (0.40, 0.40), "mx": "air"}
# Hantaman udara = berputar di tempat (tanpa menukik, tanpa damage area): damage dari 1 hit window di sabetan kaki kanan.
# Montage dipertahankan penuh sampai ujung klip (blend out di ujung, bukan di panjang - blend_out) supaya sabetan tidak terpotong.
AIR_SLAM = {"name": "AM_Aksa_AirSlam", "seq": "A_Aksa_AirSlam", "source": f"{ATTACK}/MM_ChargedAttack", "mx": "air_slam",
            "damage": 10.0, "poise": 5.0, "hit": "auto", "mx_hit": [("foot_r", 0.40, 0.18)], "blend_out_at_end": True}
# Animasi Mixamo hasil Tools/ue_import_mixamo.py (peran = kunci "mx"). Kalau ada, menggantikan placeholder: waktu hit
# dicari otomatis ("mx_hits" = jumlah kena, mis. narae chagi 2x), jendela combo tepat setelah hit terakhir.
MIXAMO = "/Game/Jayadwara/Characters/Aksa/Anims/Mixamo"
# Revisi 18 Okt 2026 (docs/07 "Serangan udara"): 1 serangan udara per lompatan (LMB atau E berbagi jatah), tanpa "ngambang".
AIR_VALUES = {"air_combo_max": 1, "air_hang_time": 0.0, "air_hang_gravity_scale": 1.0,
              "air_slam_speed": 2000.0, "air_slam_radius": 250.0, "air_slam_recovery": 0.35}
# Hasil tes tangan combo Mixamo (Hermes, 17 Okt 2026; Hermes/Laporan/2026-10-17-combo-iter2.md). Dipakai hanya untuk
# langkah yang memakai animasi Mixamo; placeholder Mannequin tetap dengan nilai di atas.
# Laju main: wind-up ~0,43 s -> ~0,27 s tanpa memotong klip.
MX_LAJU = {"light_01": 1.35, "light_02": 1.35, "light_03": 1.45, "light_04": 1.0, "lunge": 1.5, "back": 1.5,
           "finisher_01": 1.25, "finisher_02": 1.25, "finisher_03": 1.15, "air": 1.2, "air_slam": 1.45}
MX_BLEND = {"air": (0.15, 0.30), "light_01": (0.12, 0.28), "light_02": (0.12, 0.28),
            "light_03": (0.24, 0.30), "light_04": (0.22, 0.30), "air_slam": (0.15, 0.11)}
MX_BLEND_DEFAULT = (0.05, 0.22)
# Keluarga tulang yang kena per jurus: puncak kecepatan global kadang jatuh di tangan walau jurusnya tendangan.
MX_KENA = {"light_01": "tangan", "light_02": "tangan", "light_03": "tangan", "lunge": "tangan", "back": "tangan",
           "light_04": "kaki", "air_slam": "kaki", "finisher_01": "kaki", "finisher_02": "kaki", "finisher_03": "kaki", "air": "kaki"}
KENA_BONES = {"tangan": ("hand_l", "hand_r"), "kaki": ("foot_l", "foot_r")}
MIN_PEAK_T = 0.10          # puncak < 0,1 s = transisi masuk animasi (blend_in), bukan hantaman
COMBO_EKOR = 0.55          # jendela combo = 0,55 s terakhir klip: tekanan cepat tidak memotong animasi yang jalan
# Klip Mixamo pukulan 1-2 menggeser kaki belakang ke belakang (ancang-ancang); root motion sudah diratakan, jadi kapsul
# didorong maju sedikit supaya tidak terbaca mundur (move_height 0 = meluncur datar).
MX_MAJU = {"light_01": (12.0, 0.30), "light_02": (12.0, 0.30)}
STRIKE_BONES = ("hand_r", "hand_l", "foot_r", "foot_l")
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


def apply_mixamo(steps):
    """Pakai animasi Mixamo untuk langkah yang punya hasil retarget di MIXAMO (dict langkah diubah di tempat)."""
    for step in steps:
        path = f"{MIXAMO}/A_Aksa_Mx_{step.get('mx')}"
        if step.get("mx") and EAL.does_asset_exist(path):
            step["seq_path"] = path
            step["rate"] = MX_LAJU.get(step["mx"], 1.0)
            step["blend"] = MX_BLEND.get(step["mx"], MX_BLEND_DEFAULT)
            if "hit" in step:                                     # hantaman ke bawah: kena area, tanpa hit window
                step["hit"] = step.get("mx_hit") or "auto"
                step["hits"] = step.get("mx_hits", 1)
                step["kena"] = MX_KENA.get(step["mx"])
            if step.get("combo") or step.get("combo_mx"):
                step["combo"] = "ekor"
            if step["mx"] in MX_MAJU:
                step["maju"] = MX_MAJU[step["mx"]]
            log(f"{step['name']}: animasi Mixamo {step['mx']}")


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
    path = step.get("seq_path") or f"{SEQS}/{step['seq']}"
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


# ------------------------------------------------------------------ waktu hit otomatis
def strike_timings(seq, count=1, kena=None):
    """[(tulang, mulai, durasi)] hit window dari puncak kecepatan tangan/kaki relatif pelvis (root motion tidak ikut).
    count > 1: puncak berikutnya yang berjarak >= 0,2 s dari puncak sebelumnya (jurus 2x kena).
    kena = "tangan" / "kaki" (animasi Mixamo): hanya tulang keluarga itu, puncak < MIN_PEAK_T diabaikan."""
    bones = KENA_BONES[kena] if kena else STRIKE_BONES
    length = AL.get_sequence_length(seq)
    opts = unreal.AnimPoseEvaluationOptions()
    world = unreal.AnimPoseSpaces.WORLD
    dt = 1.0 / 60.0
    prev, samples = None, []          # (kecepatan, tulang, waktu): tulang tercepat tiap frame
    for i in range(int(length / dt) + 1):
        t = min(i * dt, length)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
        pelvis = unreal.AnimPoseExtensions.get_bone_pose(pose, "pelvis", world).translation
        pos = {b: unreal.AnimPoseExtensions.get_bone_pose(pose, b, world).translation - pelvis for b in STRIKE_BONES}
        if prev and (not kena or t >= MIN_PEAK_T):
            samples.append(max(((pos[b] - prev[b]).length() / dt, b, t) for b in bones))
        prev = pos
    peaks = []
    for speed, bone, peak in sorted(samples, reverse=True):
        if len(peaks) >= count:
            break
        if all(abs(peak - p[2]) >= 0.2 for p in peaks):
            peaks.append((speed, bone, peak))
    if not peaks:
        peaks = [(0.0, "hand_r", length * 0.4)]
    timings = []
    for speed, bone, peak in sorted(peaks, key=lambda p: p[2]):
        start = max(0.0, peak - 0.12)
        timings.append((bone, round(start, 2), round(min(0.22, length - start), 2)))
        log(f"{seq.get_name()}: puncak {bone} {speed:.0f} cm/s pada {peak:.2f} s -> hit {timings[-1]} (salin ke STEPS supaya tetap)")
    return timings


def resolve_hits(step, seq):
    hit = step["hit"]
    if isinstance(hit, list):
        return hit
    return strike_timings(seq, step.get("hits", 1), step.get("kena")) if hit == "auto" else [hit]


def combo_after(hit, seq):
    """Jendela combo mulai sesaat sebelum hit window tutup, sampai ±0,35 s (dibatasi panjang animasi)."""
    start = hit[1] + hit[2] - 0.03
    return (round(start, 2), round(max(0.1, min(0.35, AL.get_sequence_length(seq) - start)), 2))


def combo_ekor(seq):
    """Jendela combo di COMBO_EKOR terakhir klip (sisa 0,02 s di ujung)."""
    length = AL.get_sequence_length(seq)
    start = max(0.05, length - COMBO_EKOR)
    return (round(start, 2), round(length - start - 0.02, 2))


def set_blend(m, step, default):
    blend_in, blend_out = step.get("blend", default)
    for prop, t in (("blend_in", blend_in), ("blend_out", blend_out)):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t)
        m.set_editor_property(prop, b)


# ------------------------------------------------------------------ montage
def ensure_montage(step):
    path = f"{MONTAGES}/{step['name']}"
    src = ensure_sequence(step)
    seq_path = step.get("seq_path") or f"{SEQS}/{step['seq']}"
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
    set_blend(m, step, (0.08, 0.2))

    add_combat_notifies(m, step, src)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    return m


def add_combat_notifies(m, step, seq):
    track = "Combat"
    if track in [str(n) for n in AL.get_animation_notify_track_names(m)]:
        AL.remove_animation_notify_events_by_track(m, track)
    else:
        AL.add_animation_notify_track(m, track, unreal.LinearColor(1.0, 0.3, 0.2, 1.0))
    hits = resolve_hits(step, seq)
    for i, (socket, start, dur) in enumerate(hits):
        hit = AL.add_animation_notify_state_event(m, track, start, dur, unreal.JDAnimNotifyState_HitWindow)
        hit.set_editor_property("socket_name", socket)
        hit.set_editor_property("new_hit", i > 0)          # kena ke-2 dst. boleh mengenai korban yang sama
        if step.get("radius"):
            hit.set_editor_property("radius_override", step["radius"])
    socket, start, dur = hits[-1]
    combo = step.get("combo")
    if combo:
        if combo == "auto":
            combo = combo_after((socket, start, dur), seq)
        elif combo == "ekor":
            combo = combo_ekor(seq)
        AL.add_animation_notify_state_event(m, track, combo[0], combo[1], unreal.JDAnimNotifyState_ComboWindow)


def ensure_extra_montage(step):
    """Montage pembuka/finisher dari salinan animasi langkah (A_Aksa_Attack_0x); dibuat ulang tiap jalan."""
    path = f"{MONTAGES}/{step['name']}"
    seq = load(step.get("seq_path") or f"{SEQS}/{step['seq']}")
    if not seq:
        return None
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset(step["name"], MONTAGES, unreal.AnimMontage, f)
    set_blend(m, step, (0.08, 0.2))
    add_combat_notifies(m, step, seq)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    log(f"{step['name']} dari {(step.get('seq_path') or step['seq']).rsplit('/', 1)[-1]}")
    return m


def ensure_air_montage(step):
    """Salinan animasi tanpa root motion + montage (dibuat ulang tiap jalan). Tanpa "hit" = tanpa notify (hantaman area)."""
    path, seq_path = f"{MONTAGES}/{step['name']}", step.get("seq_path") or f"{SEQS}/{step['seq']}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    if not EAL.does_asset_exist(seq_path):
        EAL.duplicate_asset(step["source"], seq_path)
    seq = load(seq_path)
    if not seq:
        return None
    seq.set_editor_property("enable_root_motion", False)
    EAL.save_loaded_asset(seq, only_if_is_dirty=False)
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset(step["name"], MONTAGES, unreal.AnimMontage, f)
    set_blend(m, step, (0.06, 0.2))
    if step.get("blend_out_at_end"):
        m.set_editor_property("enable_auto_blend_out", True)
        m.set_editor_property("blend_out_trigger_time", 0.0)
    if step.get("hit"):
        add_combat_notifies(m, step, seq)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    log(f"{step['name']} dari {step['seq']} (tanpa root motion)")
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


def set_rate_move(s, step):
    s.set_editor_property("play_rate", step.get("rate", 1.0))
    if step.get("maju"):
        s.set_editor_property("move_distance", step["maju"][0])
        s.set_editor_property("move_duration", step["maju"][1])
        s.set_editor_property("move_height", 0.0)
        s.set_editor_property("stop_at_target", True)


def setup_profile(montages):
    prof = ensure_data_asset("DA_CombatProfile_Human", unreal.JDCombatProfile)
    steps = []
    for step, m in zip(STEPS, montages):
        s = unreal.JDAttackStep()
        s.set_editor_property("montage", m)
        s.set_editor_property("damage", step["damage"])
        s.set_editor_property("poise_damage", step["poise"])
        s.set_editor_property("hit_cue", tag("GameplayCue.Hit.Light"))
        set_rate_move(s, step)
        steps.append(s)
    prof.set_editor_property("light_combo", steps)

    for prop, o in OPENERS.items():
        s = unreal.JDAttackStep()
        s.set_editor_property("montage", ensure_extra_montage(o))
        s.set_editor_property("damage", o["damage"])
        s.set_editor_property("poise_damage", o["poise"])
        s.set_editor_property("hit_cue", tag("GameplayCue.Hit.Light"))
        s.set_editor_property("move_distance", o["move_distance"])
        s.set_editor_property("move_duration", o["move_duration"])
        s.set_editor_property("move_height", o.get("move_height", 0.0))
        s.set_editor_property("stop_at_target", o["stop_at_target"])
        s.set_editor_property("play_rate", o.get("rate", 1.0))
        prof.set_editor_property(prop, s)
    for k, v in DIRECTION.items():
        prof.set_editor_property(k, v)
    finishers = []
    for fin in FINISHERS:
        s = unreal.JDAttackStep()
        if fin.get("mx_only") and not fin.get("seq_path"):
            finishers.append(s)                                   # slot kosong -> pukulan berat biasa
            continue
        s.set_editor_property("montage", ensure_extra_montage(fin))
        s.set_editor_property("damage", HEAVY["damage"])
        s.set_editor_property("poise_damage", HEAVY["poise"])
        s.set_editor_property("stamina_cost", HEAVY["stamina"])
        s.set_editor_property("play_rate", fin["rate"])
        s.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
        s.set_editor_property("knockdown", True)           # Jatuh (docs/07 "Reaksi kena pukul", Iterasi 4)
        finishers.append(s)
    prof.set_editor_property("heavy_finishers", finishers)

    air = unreal.JDAttackStep()
    air.set_editor_property("montage", ensure_air_montage(AIR))
    air.set_editor_property("damage", AIR["damage"])
    air.set_editor_property("poise_damage", AIR["poise"])
    air.set_editor_property("hit_cue", tag("GameplayCue.Hit.Light"))
    air.set_editor_property("play_rate", AIR.get("rate", 1.0))
    prof.set_editor_property("air_attack", air)
    slam = unreal.JDAttackStep()
    slam.set_editor_property("montage", ensure_air_montage(AIR_SLAM))
    slam.set_editor_property("damage", AIR_SLAM["damage"])
    slam.set_editor_property("poise_damage", AIR_SLAM["poise"])
    slam.set_editor_property("stamina_cost", HEAVY["stamina"])
    slam.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
    slam.set_editor_property("play_rate", AIR_SLAM.get("rate", 1.0))
    slam.set_editor_property("knockdown", True)
    prof.set_editor_property("air_slam", slam)
    for k, v in AIR_VALUES.items():
        prof.set_editor_property(k, v)
    prof.set_editor_property("montage_play_rate", 1.0)
    prof.set_editor_property("hit_radius", 30.0)
    prof.set_editor_property("hit_stop_duration", 0.06)
    prof.set_editor_property("hit_stop_time_dilation", 0.05)
    prof.set_editor_property("hit_camera_shake", unreal.JDCameraShake_Hit.static_class())
    prof.set_editor_property("hit_camera_shake_scale", 1.0)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log(f"DA_CombatProfile_Human terisi: {len(steps)} langkah, pembuka terjang/mundur, {len(finishers)} finisher berat, serangan udara")
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
    apply_mixamo(STEPS + list(OPENERS.values()) + FINISHERS + [AIR, AIR_SLAM])
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
        log("setup combo ringan selesai (4 langkah + arah + finisher)")


main()
