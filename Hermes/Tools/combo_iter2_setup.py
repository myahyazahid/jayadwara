"""M5 combo iterasi 2: montage + combat profile + pawn + level uji, semua di /Game/Hermes/ComboIter2.

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_setup.py

Membuat (aman diulang):
  ComboIter2/Montages/AM_Hermes_<peran>            montage dari A_Aksa_Mx_<peran> + notify JD Hit/Combo Window
  ComboIter2/Data/DA_CombatProfile_Human_Hermes    duplikat DA_CombatProfile_Human, montage diisi
  ComboIter2/BP_Aksa_Hermes                        duplikat BP_Aksa, combat_profile = profil Hermes
  ComboIter2/Maps/Test_Hermes_ComboIter2           duplikat Test_Combat + BP_Aksa_Hermes di PlayerStart

Waktu hit: puncak kecepatan tulang yang diharapkan (kaki untuk tendangan, tangan untuk pukulan) relatif pelvis,
logika strike_timings dari Tools/ue_setup_light_combo.py + dua penyesuaian yang dicatat di laporan:
  (1) puncak dicari di keluarga tulang yang diharapkan — pada animasi Mixamo ini ayunan tangan sering lebih cepat
      dari tendangannya, jadi pencarian global menaruh jendela hit di tangan;
  (2) puncak < 0,1 s diabaikan (transisi masuk animasi, blend_in 0,08 s).
"""
import json
import os

import unreal

DEST = "/Game/Hermes/ComboIter2"
MONTAGES = f"{DEST}/Montages"
MX = f"{DEST}/Mixamo"
DATA = f"{DEST}/Data"
MAPS = f"{DEST}/Maps"
LOG_DIR = os.path.join(unreal.Paths.project_dir(), "Hermes/Art/combo-iter2/Log")
SRC_PROFILE = "/Game/Jayadwara/Data/DA_CombatProfile_Human"
SRC_AKSA = "/Game/Jayadwara/Characters/Aksa/BP_Aksa"
SRC_MAP = "/Game/Jayadwara/Maps/Test_Combat"

STRIKE_BONES = ("hand_r", "hand_l", "foot_r", "foot_l")
KENA_BONE = {"tangan": ("hand_l", "hand_r"), "kaki": ("foot_l", "foot_r")}
T_AWAL = 0.10

# Jalankan hanya peran tertentu (montage lain jangan dibuat ulang: notify + laju sudah disetel).
# Kosongkan set() kalau mau membuat ulang semua montage dari nol.
HANYA = {"air_slam"}

# peran -> pengaturan montage (docs/07 + Hermes/combo_iter2_hermes.md §6)
PERAN = {
    "light_01": {"kena": "tangan", "hits": 1, "combo": True},
    "light_02": {"kena": "tangan", "hits": 1, "combo": True},
    "light_03": {"kena": "tangan", "hits": 1, "combo": True},
    "light_04": {"kena": "kaki", "hits": 1, "combo": False},
    "lunge": {"kena": "tangan", "hits": 1, "combo": True},
    "back": {"kena": "tangan", "hits": 1, "combo": True},
    "finisher_01": {"kena": "kaki", "hits": 1, "combo": False},
    "finisher_02": {"kena": "kaki", "hits": 2, "combo": False},
    "finisher_03": {"kena": "kaki", "hits": 1, "combo": False},
    "air": {"kena": "kaki", "hits": 1, "combo": True},
    # air_slam: dulu tanpa hit window karena damage diharapkan dari ApplyAreaHit di C++
    # (JDGA_HeavyAttack). Versi C++ di worktree sekarang tidak memanggilnya lagi, jadi
    # hantaman tidak memberi damage sama sekali -> umpan balik: "kok ga bisa ngehit musuh".
    # Jendela hit eksplisit: kaki kanan menyabet naik 10,7 -> 139,7 cm dan memuncak di
    # 1,867 s klip asli (= 0,45 s montage), jadi 0,40-0,58 s menutup seluruh sabetan.
    "air_slam": {"kena": "kaki", "hits": 1, "combo": False,
                 "hit_manual": [("foot_r", 0.40, 0.18)]},
    # belum ada FBX-nya (dilaporkan): heavy, dodge_forward/back/left/right, parry_01/02
    "dodge_forward": {"kena": None, "hits": 0, "combo": False, "blend": (0.05, 0.15)},
    "dodge_back": {"kena": None, "hits": 0, "combo": False, "blend": (0.05, 0.15)},
    "dodge_left": {"kena": None, "hits": 0, "combo": False, "blend": (0.05, 0.15)},
    "dodge_right": {"kena": None, "hits": 0, "combo": False, "blend": (0.05, 0.15)},
    "parry_01": {"kena": None, "hits": 0, "combo": False, "blend": (0.04, 0.15)},
    "parry_02": {"kena": None, "hits": 0, "combo": False, "blend": (0.04, 0.15)},
}

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
problems = []


def log(msg):
    unreal.log(f"[combo_setup] {msg}")


def fail(msg):
    problems.append(msg)
    unreal.log_error(f"[combo_setup] {msg}")


def ada(path):
    return EAL.does_asset_exist(path)


def strike_timings(seq, count=1, keluarga=None):
    """[(tulang, mulai, durasi)] dari puncak kecepatan relatif pelvis (salinan strike_timings proyek + 2 penyesuaian)."""
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
        if prev:
            for b in STRIKE_BONES:
                if t >= T_AWAL and (keluarga is None or b in keluarga):
                    samples.append(((pos[b] - prev[b]).length() / dt, b, t))
        prev = pos
    samples.sort(reverse=True)
    peaks = []
    for speed, bone, t in samples:
        if len(peaks) >= count:
            break
        if all(abs(t - p[2]) >= 0.2 for p in peaks):
            peaks.append((speed, bone, t))
    if not peaks:
        fail(f"{seq.get_name()}: tidak ada puncak kecepatan tulang {keluarga}")
        return []
    timings = []
    for speed, bone, peak in sorted(peaks, key=lambda p: p[2]):
        start = max(0.0, peak - 0.12)
        timings.append((bone, round(start, 2), round(min(0.22, length - start), 2)))
        log(f"{seq.get_name()}: puncak {bone} {speed:.0f} cm/s @{peak:.2f} s -> hit {timings[-1]}")
    return timings


def combo_after(hit, seq):
    start = hit[1] + hit[2] - 0.03
    return (round(start, 2), round(max(0.1, min(0.35, AL.get_sequence_length(seq) - start)), 2))


def add_notifies(m, cfg, seq, info):
    track = "Combat"
    if track in [str(n) for n in AL.get_animation_notify_track_names(m)]:
        AL.remove_animation_notify_events_by_track(m, track)
    else:
        AL.add_animation_notify_track(m, track, unreal.LinearColor(1.0, 0.3, 0.2, 1.0))
    if cfg["hits"] == 0:
        info["hit"] = []
        info["combo"] = None
        return
    # hit_manual: waktu jendela ditentukan tangan (untuk jurus yang puncak kecepatannya
    # bukan sabetan, mis. hantaman udara yang memutar). Isinya [(tulang, mulai, durasi)].
    hits = ([(s, st, d) for s, st, d in cfg["hit_manual"]] if cfg.get("hit_manual")
            else strike_timings(seq, cfg["hits"], KENA_BONE.get(cfg["kena"])))
    # dua jendela tidak boleh bertumpuk: kalau bertumpuk, satu jurus bisa mencatat 2 damage dalam 0,02 s
    for i in range(len(hits) - 1):
        socket, start, dur = hits[i]
        nxt = hits[i + 1][1]
        if start + dur > nxt - 0.01:
            hits[i] = (socket, start, round(max(0.10, nxt - start - 0.01), 2))
    if len(hits) < cfg["hits"]:
        fail(f"{m.get_name()}: hanya {len(hits)} hit window, seharusnya {cfg['hits']}")
    for i, (socket, start, dur) in enumerate(hits):
        ev = AL.add_animation_notify_state_event(m, track, start, dur, unreal.JDAnimNotifyState_HitWindow)
        ev.set_editor_property("socket_name", socket)
        ev.set_editor_property("new_hit", i > 0)
    info["hit"] = [{"tulang": s, "mulai": st, "durasi": d} for s, st, d in hits]
    info["combo"] = None
    if cfg["combo"] and hits:
        c = combo_after(hits[-1], seq)
        AL.add_animation_notify_state_event(m, track, c[0], c[1], unreal.JDAnimNotifyState_ComboWindow)
        info["combo"] = {"mulai": c[0], "durasi": c[1]}


def buat_montage(peran, cfg):
    seq_path = f"{MX}/A_Aksa_Mx_{peran}"
    if not ada(seq_path):
        return None
    seq = EAL.load_asset(seq_path)
    name = f"AM_Hermes_{peran}"
    path = f"{MONTAGES}/{name}"
    if ada(path):
        EAL.delete_asset(path)                    # dibuat ulang supaya notify tidak dobel
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset(name, MONTAGES, unreal.AnimMontage, f)
    bin_, bout = cfg.get("blend", (0.08, 0.2))
    for prop, t in (("blend_in", bin_), ("blend_out", bout)):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t)
        m.set_editor_property(prop, b)
    info = {"peran": peran, "montage": path, "animasi": seq_path,
            "panjang_s": round(AL.get_sequence_length(seq), 3),
            "blend": [bin_, bout], "laju": 1.0}
    add_notifies(m, cfg, seq, info)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    log(f"{name}: {info['panjang_s']} s, hit {info['hit']}, combo {info['combo']}")
    return m, info


def pastikan_profil():
    dst = f"{DATA}/DA_CombatProfile_Human_Hermes"
    if not ada(dst):
        EAL.duplicate_asset(SRC_PROFILE, dst)
        log(f"profil diduplikat: {SRC_PROFILE} -> {dst}")
    prof = EAL.load_asset(dst)
    if prof is None:
        fail(f"profil tidak bisa dimuat: {dst}")
    return prof


def isi_profil(prof, montages):
    # combo ringan
    # struct di dalam TArray adalah nilai: ubah salinan, lalu ganti elemen list (bukan set_editor_property di elemen)
    steps = list(prof.get_editor_property("light_combo"))
    for i in range(4):
        peran = f"light_0{i + 1}"
        if peran in montages:
            while len(steps) <= i:
                steps.append(unreal.JDAttackStep())
            s = steps[i]
            s.set_editor_property("montage", montages[peran])
            steps[i] = s
    prof.set_editor_property("light_combo", steps)

    for prop, peran in (("lunge_attack", "lunge"), ("back_attack", "back")):
        s = prof.get_editor_property(prop)
        if peran in montages:
            s.set_editor_property("montage", montages[peran])
            if peran == "lunge":
                s.set_editor_property("move_height", 60.0)
                s.set_editor_property("move_duration", 0.35)
            prof.set_editor_property(prop, s)

    # finisher berat: slot 0/1/2
    fins = list(prof.get_editor_property("heavy_finishers"))
    for i, peran in enumerate(("finisher_01", "finisher_02", "finisher_03")):
        if peran in montages:
            while len(fins) <= i:
                fins.append(unreal.JDAttackStep())
            s = fins[i]
            s.set_editor_property("montage", montages[peran])
            if peran == "finisher_02":
                s.set_editor_property("play_rate", 1.25)
            fins[i] = s
    prof.set_editor_property("heavy_finishers", fins)

    if "heavy" in montages:
        s = prof.get_editor_property("heavy_attack")
        s.set_editor_property("montage", montages["heavy"])
        prof.set_editor_property("heavy_attack", s)

    for prop, peran in (("air_attack", "air"), ("air_slam", "air_slam")):
        s = prof.get_editor_property(prop)
        if peran in montages:
            s.set_editor_property("montage", montages[peran])
            prof.set_editor_property(prop, s)

    dm = prof.get_editor_property("dodge_montages")
    for field, peran in (("forward", "dodge_forward"), ("backward", "dodge_back"),
                         ("left", "dodge_left"), ("right", "dodge_right")):
        if peran in montages:
            dm.set_editor_property(field, montages[peran])
    prof.set_editor_property("dodge_montages", dm)

    if "parry_01" in montages or "parry_02" in montages:
        parry = [montages[p] for p in ("parry_01", "parry_02") if p in montages]
        prof.set_editor_property("parry_montages", parry)
        prof.set_editor_property("parry_montage_rate", 1.0)

    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    return prof


def baca_balik(prof):
    """Cetak isi profil dari get_editor_property (bukti, bukan klaim)."""
    out = {}
    lc = prof.get_editor_property("light_combo")
    out["light_combo"] = [s.get_editor_property("montage").get_name() if s.get_editor_property("montage") else None
                          for s in lc]
    for prop in ("lunge_attack", "back_attack", "heavy_attack", "air_attack", "air_slam"):
        s = prof.get_editor_property(prop)
        m = s.get_editor_property("montage")
        out[prop] = {"montage": m.get_name() if m else None,
                     "move_height": round(s.get_editor_property("move_height"), 2),
                     "move_duration": round(s.get_editor_property("move_duration"), 3)}
    out["heavy_finishers"] = []
    for s in prof.get_editor_property("heavy_finishers"):
        m = s.get_editor_property("montage")
        out["heavy_finishers"].append({"montage": m.get_name() if m else None,
                                       "play_rate": round(s.get_editor_property("play_rate"), 2)})
    dm = prof.get_editor_property("dodge_montages")
    out["dodge_montages"] = {f: (dm.get_editor_property(f).get_name() if dm.get_editor_property(f) else None)
                             for f in ("forward", "backward", "left", "right")}
    out["parry_montages"] = [m.get_name() for m in prof.get_editor_property("parry_montages")]
    out["parry_montage_rate"] = round(prof.get_editor_property("parry_montage_rate"), 2)
    out["montage_play_rate"] = round(prof.get_editor_property("montage_play_rate"), 2)
    log("profil (baca balik): " + json.dumps(out, ensure_ascii=False))
    return out


def buat_pawn(prof):
    dst = f"{DEST}/BP_Aksa_Hermes"
    if not ada(dst):
        EAL.duplicate_asset(SRC_AKSA, dst)
        log(f"pawn diduplikat: {SRC_AKSA} -> {dst}")
    bp = EAL.load_asset(dst)
    d = unreal.get_default_object(bp.generated_class())
    d.get_editor_property("combat_component").set_editor_property("combat_profile", prof)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)
    cek = unreal.get_default_object(bp.generated_class()).get_editor_property("combat_component").get_editor_property("combat_profile")
    log(f"BP_Aksa_Hermes.combat_profile = {cek.get_path_name() if cek else None}")
    if not cek or "ComboIter2" not in cek.get_path_name():
        fail("BP_Aksa_Hermes: combat_profile bukan profil Hermes")
    return bp


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[combo_setup] PIE sedang jalan — hentikan Play dulu")
        return
    os.makedirs(LOG_DIR, exist_ok=True)
    for folder in (MONTAGES, DATA, MAPS, f"{DEST}/Rig"):
        if not EAL.does_directory_exist(folder):
            EAL.make_directory(folder)

    montages, infos = {}, []
    for peran, cfg in PERAN.items():
        if HANYA and peran not in HANYA:
            log(f"LEWAT {peran}: di luar HANYA, montage-nya tidak dibuat ulang")
            continue
        if not ada(f"{MX}/A_Aksa_Mx_{peran}"):
            continue
        hasil = buat_montage(peran, cfg)
        if hasil:
            montages[peran], info = hasil
            infos.append(info)
    log(f"{len(montages)} montage dibuat: {sorted(montages)}")

    prof = pastikan_profil()
    if prof:
        prof = isi_profil(prof, montages)
        isi = baca_balik(prof)
        buat_pawn(prof)
        nama_log = "montage.json" if not HANYA else "montage_" + "_".join(sorted(HANYA)) + ".json"
        with open(os.path.join(LOG_DIR, nama_log), "w", encoding="utf-8") as fh:
            json.dump({"montages": infos, "profil": isi,
                       "level": "dibuat oleh combo_iter2_level.py"}, fh, indent=2, ensure_ascii=False)
        log(f"{nama_log} ditulis ({len(infos)} montage)")

    if problems:
        unreal.log_warning(f"[combo_setup] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("setup combo iterasi 2 selesai")


main()
