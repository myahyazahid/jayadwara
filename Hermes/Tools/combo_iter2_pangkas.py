"""Pangkas animasi hasil retarget ke satu rentang waktu saja (combo iterasi 2).

Kenapa: `JDGA_HeavyAttack::ActivateAirSlam` (baris 108) memakai `Profile->AirSlam.Montage`
sebagai **pose menukik** — ability berhenti saat mendarat, lalu `Montage_Stop(0.2)`. Klip
`air_slam` dari Mixamo adalah animasi lompat-slam penuh 2,67 s: karakter naik 1 m dulu
(kepala 154 -> 248 cm) baru menghantam. Karena itu yang terlihat cuma ancang-ancang lalu
terpotong -> "kayak ke-skip".

Yang dilakukan: ambil hanya bagian menukik (t 1,50-1,90 s: kepala 149 -> 49 cm, tangan
120 -> -4 cm), tulis ulang SEMUA track tulang pada 30 fps, panjang 0,4 s. FBX asli tidak
disentuh; yang berubah hanya aset hasil retarget di sandbox.

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_pangkas.py
Log: Hermes/Art/combo-iter2/Log/pangkas.json
"""
import json
import os

import unreal

MX = "/Game/Hermes/ComboIter2/Mixamo"
LOG = unreal.Paths.convert_relative_path_to_full(
    unreal.Paths.project_dir() + "Hermes/Art/combo-iter2/Log/pangkas.json")
FPS = 30

# peran -> (mulai_detik_di_klip_asli, durasi_detik)
PANGKAS = {
    "air_slam": (1.50, 0.40),
    # air: ekor 0,65 s hanya recovery diam -> memutar penuh terasa kaku setelah
    # tendangan. Dipotong di 0,90 s supaya montage selesai saat masih di udara
    # lalu blend balik ke animasi lompat/jatuh.
    "air": (0.00, 0.90),
    # light_01/light_02: kaki belakang geser 33 cm ke belakang saat ancang-ancang
    # (0-0,6 s) dan kaki depan geser balik 34 cm saat recovery (1,4-1,6 s).
    # Dua bagian itu yang terbaca "bergerak ke belakang" -> dibuang.
    "light_01": (0.10, 1.30),
    "light_02": (0.10, 1.35),
    # light_03/light_04: 0,45 s ancang-ancang + 0,5 s ekor diam. Dipotong supaya
    # sambungan pukulan 2->3 dan 3->4 tidak berhenti lama di pose netral.
    "light_03": (0.45, 1.20),
    "light_04": (0.50, 1.05),
}
# jalankan hanya peran tertentu (klip lain sudah dipangkas, memangkas ulang akan
# mengambil rentang dari klip yang sudah pendek)
HANYA = {"light_03", "light_04"}

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
hasil = []


def log(msg):
    unreal.log(f"[pangkas] {msg}")


def rentang(seq, n=9):
    o = unreal.AnimPoseEvaluationOptions()
    L = AL.get_sequence_length(seq)
    hz, pz, hy = [], [], []
    for i in range(n):
        t = L * i / float(n - 1)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        hz.append(unreal.AnimPoseExtensions.get_bone_pose(p, "head", unreal.AnimPoseSpaces.WORLD).translation.z)
        pz.append(unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).translation.z)
        hy.append(unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).translation.y)
    return {
        "panjang": round(L, 3),
        "kepala_z": [round(min(hz), 1), round(max(hz), 1)],
        "pelvis_z": [round(min(pz), 1), round(max(pz), 1)],
        "pelvis_y": [round(min(hy), 1), round(max(hy), 1)],
    }


def pangkas(seq, t0, dur):
    model = seq.get_editor_property("data_model_interface")
    ctrl = unreal.new_object(unreal.AnimSequencerController, seq)
    ctrl.set_model(model)
    n = int(round(dur * FPS)) + 1
    # PENTING: sampel dulu (klip masih utuh), baru potong panjangnya, baru tulis kunci.
    o = unreal.AnimPoseEvaluationOptions()
    poses = [unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t0 + dur * i / float(n - 1), o)
             for i in range(n)]
    ctrl.set_frame_rate(unreal.FrameRate(numerator=FPS, denominator=1))
    ctrl.set_play_length(dur)
    frame = model.get_number_of_frames()
    for b in list(model.get_bone_track_names()):
        pos, rot, scl = [], [], []
        for p in poses:
            tr = unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.LOCAL)
            pos.append(tr.translation)
            rot.append(tr.rotation)
            scl.append(tr.scale3d)
        ctrl.set_bone_track_keys(b, pos, rot, scl)
    EAL.save_loaded_asset(seq, only_if_is_dirty=False)
    return frame, len(list(model.get_bone_track_names()))


def main():
    for peran, (t0, dur) in PANGKAS.items():
        if HANYA and peran not in HANYA:
            log(f"LEWAT {peran}: sudah dipangkas sebelumnya")
            continue
        seq = EAL.load_asset(f"{MX}/A_Aksa_Mx_{peran}")
        if not seq:
            log(f"LEWAT {peran}: aset tidak ada")
            continue
        sebelum = rentang(seq)
        frame, ntulang = pangkas(seq, t0, dur)
        sesudah = rentang(seq)
        hasil.append({"peran": peran, "potong": [t0, dur], "frame": frame,
                      "tulang": ntulang, "sebelum": sebelum, "sesudah": sesudah})
        log(f"{peran:10s} {sebelum['panjang']}s -> {sesudah['panjang']}s ({frame} frame) | "
            f"kepala Z {sebelum['kepala_z']} -> {sesudah['kepala_z']} | "
            f"pelvis Z {sesudah['pelvis_z']} | pelvis Y {sesudah['pelvis_y']}")

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(hasil, f, indent=1)
    log(f"selesai: {len(hasil)} animasi -> {LOG}")


main()
