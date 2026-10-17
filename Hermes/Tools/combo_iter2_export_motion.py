"""SALINAN SANDBOX dari Tools/ue_export_combat_motion.py (combo iterasi 2, M4).

Ekspor gerak tulang animasi combat ke JSON untuk pemutar visual "Daftar Jurus" (Unreal Editor Python).

Pakai: python Tools/ue_remote.py Hermes/Tools/combo_iter2_export_motion.py
Hasil: Hermes/Art/combo-iter2/Log/combat_motion.json (salinan sandbox).
Isi: per animasi, posisi dunia 21 tulang (cm, sumbu UE: X depan, Y kanan, Z atas) tiap 1/30 s, termasuk root motion,
plus jendela kena/combo dari notify montage. Tidak mengubah aset apa pun. Animasi yang belum ada dilewati.
"""
import json
import os

import unreal

DEST = "/Game/Hermes/ComboIter2"
MONT = f"{DEST}/Montages"
SEQ = f"{DEST}/Mixamo"
# (id, judul, montage (untuk notify), animasi yang dipakai montage, cadangan kalau animasi belum ada)
# Animasi ditulis langsung: isi slot montage (SlotAnimTracks) tidak bisa dibaca dari Python.
# peran Mixamo yang ada di sandbox (montage Hermes + animasi hasil retarget)
MOVES = [
    ("light_01", "Pukulan 1 (jab)", f"{MONT}/AM_Hermes_light_01", f"{SEQ}/A_Aksa_Mx_light_01", None),
    ("light_02", "Pukulan 2 (cross)", f"{MONT}/AM_Hermes_light_02", f"{SEQ}/A_Aksa_Mx_light_02", None),
    ("light_03", "Pukulan 3 (hook)", f"{MONT}/AM_Hermes_light_03", f"{SEQ}/A_Aksa_Mx_light_03", None),
    ("light_04", "Pukulan 4 (tendangan putar belakang)", f"{MONT}/AM_Hermes_light_04", f"{SEQ}/A_Aksa_Mx_light_04", None),
    ("lunge", "Terjang", f"{MONT}/AM_Hermes_lunge", f"{SEQ}/A_Aksa_Mx_lunge", None),
    ("back", "Pukul mundur", f"{MONT}/AM_Hermes_back", f"{SEQ}/A_Aksa_Mx_back", None),
    ("finisher_01", "Finisher 1 (dwi chagi)", f"{MONT}/AM_Hermes_finisher_01", f"{SEQ}/A_Aksa_Mx_finisher_01", None),
    ("finisher_02", "Finisher 2 (narae chagi)", f"{MONT}/AM_Hermes_finisher_02", f"{SEQ}/A_Aksa_Mx_finisher_02", None),
    ("finisher_03", "Finisher 3 (ringan x3)", f"{MONT}/AM_Hermes_finisher_03", f"{SEQ}/A_Aksa_Mx_finisher_03", None),
    ("air", "Tendangan udara", f"{MONT}/AM_Hermes_air", f"{SEQ}/A_Aksa_Mx_air", None),
    ("air_slam", "Hantaman ke bawah", f"{MONT}/AM_Hermes_air_slam", f"{SEQ}/A_Aksa_Mx_air_slam", None),
]
BONES = ["root", "pelvis", "spine_01", "spine_03", "spine_05", "neck_01", "head",
         "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
         "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r"]
FPS = 30.0
OUT = os.path.join(unreal.Paths.project_dir(), "Hermes/Art/combo-iter2/Log")

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
PE = unreal.AnimPoseExtensions


def log(msg):
    unreal.log(f"[CombatMotion] {msg}")


def windows(montage):
    """Jendela JD Hit Window / JD Combo Window dari notify montage (detik animasi). Gagal baca = kosong, ekspor tetap jalan."""
    out = {"hit": [], "combo": []}
    if not montage:
        return out
    try:
        for ev in AL.get_animation_notify_events(montage):
            state = ev.get_editor_property("notify_state_class")
            name = state.get_class().get_name() if state else ""
            key = "hit" if "HitWindow" in name else "combo" if "ComboWindow" in name else None
            if not key:
                continue
            start = AL.get_anim_notify_event_trigger_time(ev)
            entry = [round(start, 3), round(start + AL.get_anim_notify_event_duration(ev), 3)]
            if key == "hit":
                entry.append(str(state.get_editor_property("socket_name")))
            out[key].append(entry)
    except Exception as e:  # noqa: BLE001
        log(f"{montage.get_name()}: notify tidak terbaca ({e})")
    return out


def sample(seq):
    length = AL.get_sequence_length(seq)
    opts = unreal.AnimPoseEvaluationOptions()
    names = {str(b) for b in PE.get_bone_names(PE.get_anim_pose_at_time(seq, 0.0, opts))}
    bones = [b for b in BONES if b in names]
    frames = []
    n = int(length * FPS) + 1
    for i in range(n):
        pose = PE.get_anim_pose_at_time(seq, min(i / FPS, length), opts)
        row = []
        for b in bones:
            t = PE.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation
            row += [round(t.x, 1), round(t.y, 1), round(t.z, 1)]
        frames.append(row)
    return length, bones, frames


def main():
    os.makedirs(OUT, exist_ok=True)
    result = {"fps": FPS, "units": "cm, X depan, Y kanan, Z atas", "moves": []}
    for move_id, title, montage_path, seq_path, fallback in MOVES:
        # unreal.load_asset langsung: EditorAssetLibrary bisa kosong setelah editor dibuka ulang
        montage = unreal.load_asset(montage_path)
        seq = unreal.load_asset(seq_path) or (unreal.load_asset(fallback) if fallback else None)
        if seq is None:
            log(f"{title}: animasi belum ada, dilewati")
            continue
        length, bones, frames = sample(seq)
        result["moves"].append({"id": move_id, "title": title, "anim": seq.get_name(), "length": round(length, 3),
                                "bones": bones, "frames": frames, "windows": windows(montage)})
        log(f"{title}: {seq.get_name()} {length:.2f} s, {len(frames)} frame")
    path = os.path.join(OUT, "combat_motion.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, separators=(",", ":"))
    log(f"selesai: {len(result['moves'])} animasi -> {path} ({os.path.getsize(path) // 1024} KB)")


main()
