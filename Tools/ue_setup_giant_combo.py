"""Fase 1 Iterasi 2b — combat Jayadwara = Aksa: montage, notify paritas, profil, level uji (Unreal Editor Python).

Tujuan (docs/23 §6 Iterasi 2b): Jayadwara memakai jurus yang sama dengan Aksa; yang berbeda hanya angka yang berskala
(radius hit, jarak terjang/dodge, shake, hit-stop, jendela parry). Montage raksasa memakai **tabel notify montage Aksa
apa adanya** (dibaca lewat reflection); kalau tidak terbaca, dihitung dengan algoritma yang sama seperti
`ue_setup_light_combo.py` — klip & laju sama, jadi angkanya sama. Paritas ini gate G2b-1, dicek ulang di akhir skrip.

Butuh build C++ proyek apa adanya (JDGA_LightAttack/HeavyAttack/Dodge/Block, JDAnimNotifyState_Hit/ComboWindow), dan hasil:
  Tools/ue_setup_light_combo.py + ue_setup_defense.py + ue_setup_parry.py   combat Aksa = patokan (AM_Aksa_*)
  Tools/ue_setup_giant_mixamo.py                                           A_JD2_Mx_* / A_JD2_Src_* (retarget)
  Tools/ue_setup_jayadwara2.py                                             BP_Jayadwara2, DA_AbilitySet_Jayadwara
Pakai: python Tools/ue_remote.py Tools/ue_setup_giant_combo.py   (editor terbuka, TIDAK sedang Play)

Membuat / mengisi ulang (aman diulang):
  Jayadwara2/Combat/A_JD2_<peran>          salinan animasi sumber (montage tetap valid walau Anims/ dibuat ulang)
  Jayadwara2/Combat/AM_JD2_Light_01..04    notify JD Hit Window + Combo Window (langkah 4 = ekor klip)
  Jayadwara2/Combat/AM_JD2_Lunge, AM_JD2_Back              pembuka arah (terjang lompat kecil, pukul mundur)
  Jayadwara2/Combat/AM_JD2_Finisher_01..03                 cabang finisher berat setelah langkah 1/2/3
  Jayadwara2/Combat/AM_JD2_Air, AM_JD2_AirSlam             serangan udara & hantaman berputar (tanpa root motion)
  Jayadwara2/Combat/AM_JD2_Heavy, AM_JD2_Block, AM_JD2_Stagger
  Jayadwara2/Combat/AM_JD2_Dodge_<arah>, AM_JD2_Parry_01..02   hanya kalau animasinya sudah ada di Aksa
  Data/DA_CombatProfile_Giant              semua slot yang terisi di DA_CombatProfile_Human (gate G2b-2)
  Data/DA_AbilitySet_Jayadwara             atribut awal (Sync penuh), 4 ability, buffer 0,3 s
  BP_Jayadwara2                            ability_set, input_config, combat_profile
  Test_GiantScale                          Dummy_Giant (BP_TrainingDummy x DUMMY_SCALE) 30 m di depan PlayerStart

Bukan bagian skrip ini (tetap Iterasi 6): IMC_Giant, rig kamera + lock-on, syarat transformasi, kalah -> Aksa,
tuning rasa khas raksasa, jurus khas Jayadwara.
"""
import unreal

J2 = "/Game/Jayadwara/Characters/Jayadwara2"
SRC_MX = f"{J2}/Anims/Mixamo"                       # hasil Tools/ue_setup_giant_mixamo.py
SRC_JD2 = f"{J2}/Anims"                             # MM_Attack_0x_JD2 (placeholder lama, cadangan)
COMBAT = f"{J2}/Combat"
DATA = "/Game/Jayadwara/Data"
BP = f"{J2}/BP_Jayadwara2"
DUMMY_BP = "/Game/Jayadwara/Characters/Dummy/BP_TrainingDummy"
MAP = "/Game/Jayadwara/Maps/Test_GiantScale"
AKSA_MONT = "/Game/Jayadwara/Characters/Aksa/Anims/Montages"

# ------------------------------------------------------------------ tabel paritas
# Disalin dari Tools/ue_setup_light_combo.py (18 Okt 2026). Satu animasi sumber = satu tabel notify; kalau Aksa berubah,
# ubah di sini juga. "fallback" = placeholder Mannequin kalau animasi Mixamo-nya belum di-retarget.
STEPS = [
    {"name": "AM_JD2_Light_01", "seq": "A_JD2_Light_01", "mx": "light_01", "fallback": f"{SRC_JD2}/MM_Attack_01_JD2",
     "damage": 10.0, "poise": 5.0, "hit": ("hand_r", 0.28, 0.20), "combo": (0.45, 0.35)},
    {"name": "AM_JD2_Light_02", "seq": "A_JD2_Light_02", "mx": "light_02", "fallback": f"{SRC_JD2}/MM_Attack_02_JD2",
     "damage": 10.0, "poise": 5.0, "hit": ("hand_l", 0.30, 0.20), "combo": (0.48, 0.34)},
    {"name": "AM_JD2_Light_03", "seq": "A_JD2_Light_03", "mx": "light_03", "fallback": f"{SRC_JD2}/MM_Attack_03_JD2",
     "damage": 12.0, "poise": 8.0, "hit": ("foot_r", 0.24, 0.48), "combo": (0.69, 0.35)},
    {"name": "AM_JD2_Light_04", "seq": "A_JD2_Light_04", "mx": "light_04", "fallback": f"{SRC_JD2}/MM_ChargedAttack_JD2",
     "damage": 20.0, "poise": 20.0, "hit": "auto", "combo": None, "combo_mx": True},
]
# Pembuka arah (docs/07 "Combo & arah"): menggantikan langkah 1, combo lanjut ke langkah 2. Jarak gerak x MOVE_SCALE.
OPENERS = {
    "lunge_attack": {"name": "AM_JD2_Lunge", "seq": "A_JD2_Lunge", "mx": "lunge", "fallback": f"{SRC_JD2}/MM_Attack_01_JD2",
                     "damage": 10.0, "poise": 8.0, "hit": ("hand_r", 0.28, 0.20), "combo": (0.45, 0.35),
                     "move_distance": 600.0, "move_duration": 0.35, "move_height": 60.0, "stop_at_target": True},
    "back_attack": {"name": "AM_JD2_Back", "seq": "A_JD2_Back", "mx": "back", "fallback": f"{SRC_JD2}/MM_Attack_03_JD2",
                    "damage": 10.0, "poise": 8.0, "hit": ("foot_r", 0.24, 0.48), "radius": 50.0, "combo": (0.69, 0.35),
                    "move_distance": -150.0, "move_duration": 0.25, "stop_at_target": False},
}
# Cabang finisher: slot kosong = pukulan berat biasa. Finisher 3 hanya terisi kalau animasinya ada ("mx_only").
FINISHERS = [
    {"name": "AM_JD2_Finisher_01", "seq": "A_JD2_Finisher_01", "mx": "finisher_01", "fallback": f"{SRC_JD2}/MM_Attack_03_JD2",
     "hit": ("foot_r", 0.24, 0.48), "rate": 0.8},
    {"name": "AM_JD2_Finisher_02", "seq": "A_JD2_Finisher_02", "mx": "finisher_02", "fallback": f"{SRC_JD2}/MM_ChargedAttack_JD2",
     "hit": "auto", "rate": 0.85, "mx_hits": 2,
     # narae chagi: dua tendangan berjarak < 0,2 s (batas auto) -> jendela dipasang tangan, tidak bertumpuk
     "mx_hit": [("foot_r", 0.40, 0.24), ("foot_r", 0.70, 0.24)]},
    {"name": "AM_JD2_Finisher_03", "seq": "A_JD2_Finisher_03", "mx": "finisher_03", "hit": "auto", "rate": 1.0, "mx_only": True},
]
HEAVY = {"damage": 30.0, "poise": 40.0, "stamina": 25.0, "rate": 0.75, "hit": ("hand_l", 0.32, 0.24)}
BLOCK_HOLD = 0.75
STAGGER = {"name": "AM_JD2_Stagger", "seq": "A_JD2_Stagger"}
# Serangan udara (docs/07 "Serangan udara", revisi 18 Okt 2026: tanpa "ngambang", hantaman berputar di tempat).
AIR = {"name": "AM_JD2_Air", "seq": "A_JD2_Air", "mx": "air", "fallback": f"{SRC_JD2}/MM_Attack_03_JD2",
       "damage": 10.0, "poise": 5.0, "hit": ("foot_r", 0.24, 0.48), "combo": (0.40, 0.40)}
AIR_SLAM = {"name": "AM_JD2_AirSlam", "seq": "A_JD2_AirSlam", "mx": "air_slam", "fallback": f"{SRC_JD2}/MM_ChargedAttack_JD2",
            "damage": 10.0, "poise": 5.0, "hit": "auto", "mx_hit": [("foot_r", 0.40, 0.18)], "blend_out_at_end": True}
AIR_VALUES = {"air_combo_max": 1, "air_hang_time": 0.0, "air_hang_gravity_scale": 1.0, "air_slam_recovery": 0.35}
AIR_SLAM_SPEED, AIR_SLAM_RADIUS = 2000.0, 250.0

# Hasil tes tangan combo Mixamo Aksa (Hermes 17 Okt, lulus developer 18 Okt). Laju & blend HARUS sama supaya rasa sama;
# blend dikali GlobalAnimRateScale mesh raksasa (detik nyata, pola skrip 13 Okt).
MX_LAJU = {"light_01": 1.35, "light_02": 1.35, "light_03": 1.45, "light_04": 1.0, "lunge": 1.5, "back": 1.5,
           "finisher_01": 1.25, "finisher_02": 1.25, "finisher_03": 1.15, "air": 1.2, "air_slam": 1.45}
MX_BLEND = {"air": (0.15, 0.30), "light_01": (0.12, 0.28), "light_02": (0.12, 0.28),
            "light_03": (0.24, 0.30), "light_04": (0.22, 0.30), "air_slam": (0.15, 0.11)}
MX_BLEND_DEFAULT = (0.05, 0.22)
MX_KENA = {"light_01": "tangan", "light_02": "tangan", "light_03": "tangan", "lunge": "tangan", "back": "tangan",
           "light_04": "kaki", "air_slam": "kaki", "finisher_01": "kaki", "finisher_02": "kaki", "finisher_03": "kaki",
           "air": "kaki"}
KENA_BONES = {"tangan": ("hand_l", "hand_r"), "kaki": ("foot_l", "foot_r")}
STRIKE_BONES = ("hand_r", "hand_l", "foot_r", "foot_l")
MIN_PEAK_T = 0.10          # puncak < 0,1 s = transisi masuk animasi, bukan hantaman
COMBO_EKOR = 0.55          # jendela combo = 0,55 s terakhir klip
MX_MAJU = {"light_01": (12.0, 0.30), "light_02": (12.0, 0.30)}   # dorongan maju kecil (cm, detik) — x MOVE_SCALE

# ------------------------------------------------------------------ angka raksasa (docs/23 bagian 5)
MOVE_SCALE_FACTOR = 0.6     # jarak gerak & dodge = x skala raksasa x 0,6
PLAY_RATE = 1.0             # laju terlihat (ala Mebius); ability membagi dengan GlobalAnimRateScale mesh
HUMAN_HIT_RADIUS = 30.0     # x skala raksasa
HIT_STOP = 0.15
SHAKE_SCALE = 2.5
DIRECTION_CM = {"target_search_radius": 800.0, "lunge_min_distance": 250.0, "lunge_stop_distance": 100.0}
GIANT_DEFENSE = {"dodge_distance": 5500.0, "dodge_duration": 0.35, "dodge_i_frame_start": 0.0, "dodge_i_frame_duration": 0.25,
                 "dodge_stamina_cost": 20.0, "block_hold_time": BLOCK_HOLD, "block_damage_reduction": 0.8,
                 "block_stamina_per_hit": 15.0, "block_angle": 140.0, "block_move_speed_scale": 0.4, "block_pushback": 1500.0,
                 "guard_break_stagger_duration": 1.0, "parry_window": 0.25, "parry_lockout": 0.5, "parry_stagger_duration": 1.0}
# Angka rasa parry sama dengan Aksa (Tools/ue_setup_parry.py FEEL); jendela parry tetap 0,25 s (docs/23 bagian 5).
PARRY_FEEL = {"parry_montage_rate": 1.6, "parry_hit_stop_duration": 0.12, "parry_hit_stop_time_dilation": 0.02,
              "parry_slow_mo_duration": 0.35, "parry_slow_mo_time_dilation": 0.35, "parry_camera_shake_scale": 1.5,
              "parry_counter_window": 0.8}
COUNTER = {"damage": 25.0, "poise": 30.0, "rate": 1.2}      # serangan balik setelah parry (AM_JD2_Light_04)
GIANT_ATTRIBUTES = {"max_health": 100.0, "max_stamina": 100.0, "max_poise": 50.0, "max_sync": 100.0,
                    "max_transform_energy": 0.0, "stamina_regen_per_second": 25.0, "stamina_regen_delay": 0.8}
INPUT_BUFFER = 0.3
DUMMY_SCALE = 20.0          # Manny 1,8 m -> ±36 m (Jayadwara 45 m)
DUMMY_DISTANCE = 3000.0
DODGE_KEYS = {"forward": "dodge_forward", "backward": "dodge_back", "left": "dodge_left", "right": "dodge_right"}
# Nama salinan animasi versi 13 Okt (sebelum 2b) yang harus dibersihkan supaya tidak menyisakan aset placeholder.
LEGACY = ["A_JD2_Attack_01", "A_JD2_Attack_02", "A_JD2_Attack_03", "A_JD2_Attack_04"]

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
problems = []


def log(msg):
    unreal.log(f"[Jayadwara2/2b] {msg}")


def fail(msg):
    problems.append(msg)
    unreal.log_error(f"[Jayadwara2/2b] {msg}")


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
    """Semua tulang yang dipakai hit window harus ada di skeleton raksasa."""
    mesh = load(f"{J2}/Mesh/SK_Jayadwara2")
    if not mesh:
        return
    bones = {str(b) for b in unreal.AnimPoseExtensions.get_bone_names(unreal.AnimPoseExtensions.get_reference_pose(mesh.skeleton))}
    for need in ("pelvis",) + STRIKE_BONES:
        if need not in bones:
            fail(f"tulang {need} tidak ada di SK_Jayadwara2")


# ------------------------------------------------------------------ sumber animasi
def source_of(step):
    """Animasi sumber: Mixamo hasil retarget kalau ada, kalau tidak placeholder Mannequin (cadangan)."""
    mx = step.get("mx")
    if mx:
        p = f"{SRC_MX}/A_JD2_Mx_{mx}"
        if EAL.does_asset_exist(p):
            return p, True
        if step.get("mx_only"):
            return None, False
    p = step.get("fallback")
    return (p, False) if p and EAL.does_asset_exist(p) else (None, False)


def is_mx(step):
    return source_of(step)[1]


def blend_of(step, mesh_rate):
    """Blend montage Aksa (detik nyata) x GlobalAnimRateScale mesh raksasa."""
    b = MX_BLEND.get(step.get("mx"), MX_BLEND_DEFAULT) if step.get("mx") and is_mx(step) else (0.08, 0.2)
    return (b[0] * mesh_rate, b[1] * mesh_rate)


def rate_of(step):
    if step.get("mx") and is_mx(step):
        return MX_LAJU.get(step["mx"], 1.0)
    return step.get("rate", 1.0)


# ------------------------------------------------------------------ baca tabel notify Aksa (paritas)
def read_notifies(montage):
    """Baca entri notify montage lewat reflection. None = API tidak tersedia (pakai hitung ulang)."""
    try:
        events = montage.get_editor_property("notifies")
    except Exception:
        return None
    hits, combos = [], []
    for ev in events:
        try:
            cls = str(ev.get_editor_property("notify_state_class"))
            start = round(float(ev.get_editor_property("trigger_time")), 3)
            dur = round(float(ev.get_editor_property("duration")), 3)
        except Exception:
            return None
        if "HitWindow" in cls:
            try:
                hits.append({"socket": str(ev.get_editor_property("socket_name")), "start": start, "dur": dur,
                             "new_hit": bool(ev.get_editor_property("new_hit")),
                             "radius": float(ev.get_editor_property("radius_override"))})
            except Exception:
                return None
        elif "ComboWindow" in cls:
            combos.append((start, dur))
    return {"hits": hits, "combos": combos}


def aksa_table(name):
    """Tabel notify montage Aksa yang setara (AM_JD2_Light_01 <- AM_Aksa_Light_01)."""
    path = f"{AKSA_MONT}/{name.replace('AM_JD2_', 'AM_Aksa_')}"
    return read_notifies(EAL.load_asset(path)) if EAL.does_asset_exist(path) else None


# ------------------------------------------------------------------ waktu hit otomatis (algoritma Aksa)
def strike_timings(seq, count=1, kena=None):
    """[(tulang, mulai, durasi)] dari puncak kecepatan tangan/kaki relatif pelvis. Sama dengan ue_setup_light_combo.py."""
    bones = KENA_BONES[kena] if kena else STRIKE_BONES
    length = AL.get_sequence_length(seq)
    opts = unreal.AnimPoseEvaluationOptions()
    world = unreal.AnimPoseSpaces.WORLD
    dt = 1.0 / 60.0
    prev, samples = None, []
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
        log(f"  {seq.get_name()}: puncak {bone} {speed:.0f} cm/s pada {peak:.2f} s -> hit {timings[-1]}")
    return timings


def combo_ekor(seq):
    length = AL.get_sequence_length(seq)
    start = max(0.05, length - COMBO_EKOR)
    return (round(start, 2), round(length - start - 0.02, 2))


def combo_after(hit, seq):
    start = hit[0] + hit[1] - 0.03
    return (round(start, 2), round(max(0.1, min(0.35, AL.get_sequence_length(seq) - start)), 2))


def hits_for(step, seq, name):
    """Jendela hit: salin dari montage Aksa kalau terbaca, kalau tidak hitung dengan algoritma yang sama."""
    table = aksa_table(name)
    if table and table["hits"]:
        log(f"  {name}: tabel notify disalin dari AM_Aksa_* ({len(table['hits'])} jendela)")
        return [(h["socket"], h["start"], h["dur"], h["new_hit"], h["radius"]) for h in table["hits"]], table
    if isinstance(step.get("hit"), list):
        return [(s, st, d, i > 0, step.get("radius", 0.0)) for i, (s, st, d) in enumerate(step["hit"])], None
    if step.get("hit") == "auto":
        timings = strike_timings(seq, step.get("mx_hits", 1), MX_KENA.get(step.get("mx")))
    elif step.get("hit"):
        timings = [step["hit"]]
    else:
        timings = []
    return [(s, st, d, i > 0, step.get("radius", 0.0)) for i, (s, st, d) in enumerate(timings)], None


def add_combat_notifies(m, step, seq, name, hit_radius=0.0):
    """Track "Combat" baru (montage selalu dibuat ulang, jadi tidak ada track lama) + notify paritas."""
    track = "Combat"
    AL.add_animation_notify_track(m, track, unreal.LinearColor(1.0, 0.3, 0.2, 1.0))
    hits, table = hits_for(step, seq, name)
    for socket, start, dur, new_hit, radius in hits:
        ev = AL.add_animation_notify_state_event(m, track, start, dur, unreal.JDAnimNotifyState_HitWindow)
        ev.set_editor_property("socket_name", socket)
        ev.set_editor_property("new_hit", new_hit)
        if radius or hit_radius:
            ev.set_editor_property("radius_override", radius or hit_radius)
    combos = (table or {}).get("combos") or []
    if not combos:                                     # tabel Aksa tidak terbaca / memang tanpa combo
        combo = step.get("combo")
        if combo == "ekor" or step.get("combo_mx"):
            combo = combo_ekor(seq)
        elif combo == "auto" and hits:
            combo = combo_after(hits[-1][1:3], seq)
        if combo:
            combos = [combo]
    for start, dur in combos:
        AL.add_animation_notify_state_event(m, track, start, dur, unreal.JDAnimNotifyState_ComboWindow)
    return hits, combos


# ------------------------------------------------------------------ montage
def set_blend(m, blend):
    for prop, t in (("blend_in", blend[0]), ("blend_out", blend[1])):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t)
        m.set_editor_property(prop, b)


def ensure_seq(step, seq_name, no_root_motion=False):
    """Salinan animasi sumber di Combat/ (+curve DisableLegIK untuk animasi darat). Sumber tidak diubah."""
    src, _ = source_of(step)
    if not src:
        return None
    path = f"{COMBAT}/{seq_name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    seq = EAL.duplicate_asset(src, path)
    if not seq:
        fail(f"gagal menyalin {src} -> {path}")
        return None
    if no_root_motion:
        seq.set_editor_property("enable_root_motion", False)
    else:
        curve = "DisableLegIK"
        if AL.does_curve_exist(seq, curve, unreal.RawCurveTrackTypes.RCT_FLOAT):
            AL.remove_curve(seq, curve, False)
        AL.add_curve(seq, curve, unreal.RawCurveTrackTypes.RCT_FLOAT, False)
        length = AL.get_sequence_length(seq)
        AL.add_float_curve_keys(seq, curve, [0.0, length], [1.0, 1.0])
    EAL.save_loaded_asset(seq, only_if_is_dirty=False)
    return seq


def make_montage(step, mesh_rate, no_root_motion=False):
    """Montage dari salinan animasi sumber + notify paritas. Dibuat ulang tiap jalan."""
    name = step["name"]
    path = f"{COMBAT}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    seq = ensure_seq(step, step["seq"], no_root_motion)
    if not seq:
        if step.get("mx_only"):
            log(f"{name} dilewati: animasi belum ada (slot finisher kosong = pukulan berat biasa)")
        else:
            fail(f"{name}: sumber animasi tidak ada")
        return None
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset(name, COMBAT, unreal.AnimMontage, f)
    set_blend(m, blend_of(step, mesh_rate))
    if step.get("blend_out_at_end"):
        m.set_editor_property("enable_auto_blend_out", True)
        m.set_editor_property("blend_out_trigger_time", 0.0)
    hits, combos = add_combat_notifies(m, step, seq, name)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    blend = blend_of(step, mesh_rate)
    log(f"{name}: laju {rate_of(step):.2f}, blend {blend[0]:.2f}/{blend[1]:.2f} s, "
        f"hit {[(h[0], h[1], h[2]) for h in hits]}, combo {combos}")
    return m


def make_plain_montage(name, seq_path, mesh_rate, blend, hit=None, hit_radius=0.0, hold=None):
    """Montage tanpa langkah combo: berat, pose tangkis, stagger, dodge, tepisan."""
    path = f"{COMBAT}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    seq = load(seq_path)
    if not seq:
        return None
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset(name, COMBAT, unreal.AnimMontage, f)
    set_blend(m, (blend[0] * mesh_rate, blend[1] * mesh_rate))
    if hit:
        add_combat_notifies(m, {"hit": hit}, seq, name, hit_radius)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    log(f"{name} dari {seq_path.rsplit('/', 1)[-1]}" + (f" (pose ditahan {hold:.2f} s)" if hold else ""))
    return m


def wipe_ours():
    """Hapus montage & salinan animasi milik skrip ini saja (aset lain di folder tidak disentuh)."""
    names = [s["name"] for s in STEPS] + [o["name"] for o in OPENERS.values()] + [f["name"] for f in FINISHERS]
    names += [AIR["name"], AIR_SLAM["name"], "AM_JD2_Heavy", "AM_JD2_Block", STAGGER["name"]]
    names += [f"AM_JD2_Dodge_{k.capitalize()}" for k in DODGE_KEYS] + ["AM_JD2_Parry_01", "AM_JD2_Parry_02"]
    seqs = [s["seq"] for s in STEPS] + [o["seq"] for o in OPENERS.values()] + [f["seq"] for f in FINISHERS]
    seqs += [AIR["seq"], AIR_SLAM["seq"], STAGGER["seq"]] + LEGACY
    for n in names + seqs:
        p = f"{COMBAT}/{n}"
        if EAL.does_asset_exist(p):
            EAL.delete_asset(p)


# ------------------------------------------------------------------ profil
def setup_profile(montages, mesh_rate, giant_scale):
    prof = ensure_data_asset("DA_CombatProfile_Giant", unreal.JDCombatProfile)
    move_scale = giant_scale * MOVE_SCALE_FACTOR
    hit_radius = HUMAN_HIT_RADIUS * giant_scale

    steps = []
    for step, m in zip(STEPS, montages):
        s = unreal.JDAttackStep()
        s.set_editor_property("montage", m)
        s.set_editor_property("damage", step["damage"])
        s.set_editor_property("poise_damage", step["poise"])
        s.set_editor_property("play_rate", rate_of(step))
        s.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
        maju = MX_MAJU.get(step.get("mx")) if is_mx(step) else None
        if maju:                                        # dorongan maju kecil pukulan 1–2 (pola Aksa 12 cm, x skala)
            s.set_editor_property("move_distance", maju[0] * move_scale)
            s.set_editor_property("move_duration", maju[1])
            s.set_editor_property("stop_at_target", True)
        steps.append(s)
    prof.set_editor_property("light_combo", steps)

    for prop, o in OPENERS.items():
        s = unreal.JDAttackStep()
        s.set_editor_property("montage", make_montage(o, mesh_rate))
        s.set_editor_property("damage", o["damage"])
        s.set_editor_property("poise_damage", o["poise"])
        s.set_editor_property("play_rate", rate_of(o))
        s.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
        s.set_editor_property("move_distance", o["move_distance"] * move_scale)
        s.set_editor_property("move_duration", o["move_duration"])
        s.set_editor_property("move_height", o.get("move_height", 0.0) * move_scale)   # terjang = lompat kecil
        s.set_editor_property("stop_at_target", o["stop_at_target"])
        prof.set_editor_property(prop, s)
    for k, v in DIRECTION_CM.items():
        prof.set_editor_property(k, v * move_scale)
    prof.set_editor_property("direction_threshold", 0.5)

    finishers = []
    for fin in FINISHERS:
        s = unreal.JDAttackStep()
        m = make_montage(fin, mesh_rate)
        if m is None:
            finishers.append(s)                          # slot kosong -> pukulan berat biasa
            continue
        s.set_editor_property("montage", m)
        s.set_editor_property("damage", HEAVY["damage"])
        s.set_editor_property("poise_damage", HEAVY["poise"])
        s.set_editor_property("stamina_cost", HEAVY["stamina"])
        s.set_editor_property("play_rate", rate_of(fin))
        s.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
        s.set_editor_property("knockdown", True)         # Jatuh (docs/07 "Reaksi kena pukul")
        finishers.append(s)
    prof.set_editor_property("heavy_finishers", finishers)

    heavy_seq = f"{SRC_MX}/A_JD2_Src_attack_02"
    heavy = make_plain_montage("AM_JD2_Heavy", heavy_seq, mesh_rate, (0.08, 0.2), HEAVY["hit"], hit_radius)
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
    prof.set_editor_property("block_montage",
                             make_plain_montage("AM_JD2_Block", heavy_seq, mesh_rate, (0.15, 0.2), hold=BLOCK_HOLD))

    air = unreal.JDAttackStep()
    air.set_editor_property("montage", make_montage(AIR, mesh_rate, no_root_motion=True))
    air.set_editor_property("damage", AIR["damage"])
    air.set_editor_property("poise_damage", AIR["poise"])
    air.set_editor_property("play_rate", rate_of(AIR))
    air.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
    prof.set_editor_property("air_attack", air)
    slam = unreal.JDAttackStep()
    slam.set_editor_property("montage", make_montage(AIR_SLAM, mesh_rate, no_root_motion=True))
    slam.set_editor_property("damage", AIR_SLAM["damage"])
    slam.set_editor_property("poise_damage", AIR_SLAM["poise"])
    slam.set_editor_property("stamina_cost", HEAVY["stamina"])
    slam.set_editor_property("play_rate", rate_of(AIR_SLAM))
    slam.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
    slam.set_editor_property("knockdown", True)
    prof.set_editor_property("air_slam", slam)
    for k, v in AIR_VALUES.items():
        prof.set_editor_property(k, v)
    prof.set_editor_property("air_slam_speed", AIR_SLAM_SPEED * move_scale)
    prof.set_editor_property("air_slam_radius", AIR_SLAM_RADIUS * giant_scale)

    # ---- dodge per arah & tepisan: hanya kalau animasinya sudah ada (Aksa belum punya -> kosong di dua profil)
    dodge = prof.get_editor_property("dodge_montages")
    for prop, key in (("forward", "Forward"), ("backward", "Backward"), ("left", "Left"), ("right", "Right")):
        seq_path = f"{SRC_MX}/A_JD2_Mx_{DODGE_KEYS[prop]}"
        if EAL.does_asset_exist(seq_path):
            dodge.set_editor_property(key, make_plain_montage(f"AM_JD2_Dodge_{key}", seq_path, mesh_rate, (0.05, 0.15)))
    prof.set_editor_property("dodge_montages", dodge)
    parry = []
    for i in (1, 2):
        seq_path = f"{SRC_MX}/A_JD2_Mx_parry_0{i}"
        if EAL.does_asset_exist(seq_path):
            parry.append(make_plain_montage(f"AM_JD2_Parry_0{i}", seq_path, mesh_rate, (0.04, 0.15)))
    if parry:
        prof.set_editor_property("parry_montages", parry)
    for k, v in PARRY_FEEL.items():
        prof.set_editor_property(k, v)
    prof.set_editor_property("parry_camera_shake", unreal.JDCameraShake_Hit.static_class())
    counter = unreal.JDAttackStep()
    counter.set_editor_property("montage", montages[3])          # serangan balik = pukulan langkah 4 (pola Aksa)
    counter.set_editor_property("damage", COUNTER["damage"])
    counter.set_editor_property("poise_damage", COUNTER["poise"])
    counter.set_editor_property("play_rate", COUNTER["rate"])
    counter.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
    prof.set_editor_property("parry_counter_attack", counter)

    stagger_seq = f"{SRC_MX}/A_JD2_Src_stagger"
    if EAL.does_asset_exist(stagger_seq):
        prof.set_editor_property("stagger_montage",
                                 make_plain_montage(STAGGER["name"], stagger_seq, mesh_rate, (0.08, 0.2)))

    # ---- angka yang memang berskala (docs/23 bagian 5)
    prof.set_editor_property("montage_play_rate", PLAY_RATE)
    prof.set_editor_property("hit_radius", hit_radius)
    prof.set_editor_property("hit_stop_duration", HIT_STOP)
    prof.set_editor_property("hit_stop_time_dilation", 0.05)
    prof.set_editor_property("hit_camera_shake", unreal.JDCameraShake_Hit.static_class())
    prof.set_editor_property("hit_camera_shake_scale", SHAKE_SCALE)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log(f"DA_CombatProfile_Giant terisi: {len(steps)} langkah, {len(finishers)} slot finisher, "
        f"radius hit {hit_radius:.0f} cm, hit-stop {HIT_STOP} s, shake x{SHAKE_SCALE}")
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


# ------------------------------------------------------------------ paritas (gate G2b-1)
def parity_report():
    """Bandingkan tabel notify montage raksasa dengan montage Aksa. Selisih > 0,01 s = gagal."""
    rows, bad, unchecked = [], 0, 0
    for step in STEPS + list(OPENERS.values()) + FINISHERS + [AIR, AIR_SLAM]:
        mine = f"{COMBAT}/{step['name']}"
        theirs = f"{AKSA_MONT}/{step['name'].replace('AM_JD2_', 'AM_Aksa_')}"
        if not (EAL.does_asset_exist(mine) and EAL.does_asset_exist(theirs)):
            continue
        a, b = read_notifies(EAL.load_asset(mine)), read_notifies(EAL.load_asset(theirs))
        if not a or not b:
            unchecked += 1
            continue
        beda = []
        if len(a["hits"]) != len(b["hits"]):
            beda.append(f"jumlah jendela {len(a['hits'])} vs {len(b['hits'])}")
        for i, (x, y) in enumerate(zip(a["hits"], b["hits"])):
            if x["socket"] != y["socket"]:
                beda.append(f"jendela {i + 1}: tulang {x['socket']} vs {y['socket']}")
            if abs(x["start"] - y["start"]) > 0.01 or abs(x["dur"] - y["dur"]) > 0.01:
                beda.append(f"jendela {i + 1}: waktu {x['start']}/{x['dur']} vs {y['start']}/{y['dur']}")
        if len(a["combos"]) != len(b["combos"]):
            beda.append(f"jendela combo {len(a['combos'])} vs {len(b['combos'])}")
        rows.append((step["name"], len(a["hits"]), len(b["hits"]), "OK" if not beda else "; ".join(beda)))
        if beda:
            bad += 1
    if rows:
        log("paritas notify (raksasa vs Aksa):")
        for name, n1, n2, status in rows:
            log(f"  {name:<24} {n1}/{n2} jendela  {status}")
    if bad:
        fail(f"{bad} montage belum paritas dengan Aksa (lihat tabel di atas)")
    elif unchecked:
        log(f"paritas notify: {len(rows)} montage sama; {unchecked} tidak terbaca lewat reflection "
            f"— verifikasi lewat Hermes (docs/23 G2b-1)")
    else:
        log(f"paritas notify: {len(rows)} montage diperiksa, semua sama")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara2/2b] PIE sedang jalan — hentikan Play dulu")
        return
    if not hasattr(unreal, "JDGA_LightAttack"):
        unreal.log_error("[Jayadwara2/2b] C++ combat belum ter-build (JDGA_LightAttack tidak ada)")
        return
    bp = load(BP)
    if not bp:
        return
    d = unreal.get_default_object(bp.generated_class())
    giant_scale = d.get_giant_scale()
    mesh_rate = d.get_editor_property("mesh").get_editor_property("global_anim_rate_scale")
    log(f"skala raksasa {giant_scale:.2f}, GlobalAnimRateScale {mesh_rate:.3f}")
    if not EAL.does_directory_exist(SRC_MX):
        fail(f"{SRC_MX} belum ada — jalankan Tools/ue_setup_giant_mixamo.py dulu (animasi masih placeholder)")

    check_sockets()
    wipe_ours()
    montages = [make_montage(s, mesh_rate) for s in STEPS]
    if any(m is None for m in montages):
        fail("combo ringan tidak lengkap — langkah yang gagal dilewati, profil tetap diisi sebagian")
    prof = setup_profile(montages, mesh_rate, giant_scale)
    setup_pawn(bp, setup_ability_set(), prof)
    place_dummy()
    parity_report()
    if problems:
        unreal.log_warning(f"[Jayadwara2/2b] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("combat Jayadwara2 = Aksa siap: Play di Test_GiantScale (LMB ringan, E berat, Shift dodge, RMB tangkis)")


main()
