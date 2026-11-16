"""Ekspor gerak tulang animasi combat ke JSON untuk pemutar visual "Daftar Jurus" (Unreal Editor Python).

Pakai: python Tools/ue_remote.py Tools/ue_export_combat_motion.py
Hasil: Saved/CombatMotion/combat_motion.json (±0,5 MB). Unggah file itu ke thread proyek; pemutar 3D di browser memakainya.
Isi: per animasi, posisi dunia 21 tulang (cm, sumbu UE: X depan, Y kanan, Z atas) tiap 1/30 s, termasuk root motion,
plus jendela kena/combo dari notify montage. Tidak mengubah aset apa pun. Animasi yang belum ada dilewati.
"""
import json
import os

import unreal

AKSA = "/Game/Jayadwara/Characters/Aksa/Anims"
MONT = f"{AKSA}/Montages"
SEQ = f"{AKSA}/Attack"
MANNY = "/Game/Characters/Mannequins/Anims/Unarmed/Attack"
# (id, judul, montage (untuk notify), animasi yang dipakai montage, cadangan kalau animasi belum ada)
# Animasi ditulis langsung: isi slot montage (SlotAnimTracks) tidak bisa dibaca dari Python.
MOVES = [
    ("light_01", "Pukulan 1", f"{MONT}/AM_Aksa_Light_01", f"{SEQ}/A_Aksa_Attack_01", f"{MANNY}/MM_Attack_01"),
    ("light_02", "Pukulan 2", f"{MONT}/AM_Aksa_Light_02", f"{SEQ}/A_Aksa_Attack_02", f"{MANNY}/MM_Attack_02"),
    ("light_03", "Pukulan 3", f"{MONT}/AM_Aksa_Light_03", f"{SEQ}/A_Aksa_Attack_03", f"{MANNY}/MM_Attack_03"),
    ("light_04", "Pukulan 4", f"{MONT}/AM_Aksa_Light_04", f"{SEQ}/A_Aksa_Attack_04", f"{MANNY}/MM_ChargedAttack"),
    ("lunge", "Terjang", f"{MONT}/AM_Aksa_Lunge", f"{SEQ}/A_Aksa_Attack_01", None),
    ("back", "Pukul mundur", f"{MONT}/AM_Aksa_Back", f"{SEQ}/A_Aksa_Attack_03", None),
    ("heavy", "Pukulan berat", f"{MONT}/AM_Aksa_Heavy", f"{SEQ}/A_Aksa_Attack_02", None),
    ("finisher_01", "Finisher 1", f"{MONT}/AM_Aksa_Finisher_01", f"{SEQ}/A_Aksa_Attack_03", None),
    ("finisher_02", "Finisher 2", f"{MONT}/AM_Aksa_Finisher_02", f"{SEQ}/A_Aksa_Attack_04", None),
    ("air", "Tendangan udara", f"{MONT}/AM_Aksa_Air", f"{SEQ}/A_Aksa_Air", None),
    ("air_slam", "Hantaman ke bawah", f"{MONT}/AM_Aksa_AirSlam", f"{SEQ}/A_Aksa_AirSlam", None),
    ("stagger", "Stagger", f"{MONT}/AM_Aksa_Stagger", f"{SEQ}/A_Aksa_Stagger",
     "/Game/Characters/Mannequins/Anims/Rifle/HitReact/MM_HitReact_Front_Hvy_01"),
]
BONES = ["root", "pelvis", "spine_01", "spine_03", "spine_05", "neck_01", "head",
         "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
         "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r"]
FPS = 30.0
OUT = os.path.join(unreal.Paths.project_saved_dir(), "CombatMotion")

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
        montage = EAL.load_asset(montage_path) if EAL.does_asset_exist(montage_path) else None
        path = seq_path if EAL.does_asset_exist(seq_path) else fallback if fallback and EAL.does_asset_exist(fallback) else None
        seq = EAL.load_asset(path) if path else None
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
