"""Koreksi putaran badan `air_slam` supaya berhenti menghadap depan (combo iterasi 2).

Masalah (umpan balik developer): "tendangannya memutar selesai di samping". Diukur di
Blender (combo_iter2_probe_yaw.py) pada klip asli: pinggul berputar +465 derajat dan
berhenti di +105 derajat, jadi badan selesai menyamping — bukan menghadap depan.

Jalan yang dipakai: putaran badan di-skala 360/465 (bukan dipotong), yaitu tulang `root`
diberi yaw koreksi yang besarnya mengikuti kemajuan putaran pelvis per frame:

    koreksi_i = -(sisa) * (yaw_pelvis_i / yaw_pelvis_akhir)

dengan sisa = yaw_akhir - 360*round(yaw_akhir/360). Hasilnya badan tetap memutar satu
putaran penuh (360 derajat) dan berhenti menghadap depan, tanpa memotong klip.

Catatan teknis: memakai `unreal.AnimSequencerController.set_bone_track_keys` (UE 5.6),
sama seperti combo_iter2_inplace_ue.py. Rotasi & skala root per frame disalin apa adanya,
hanya yaw-nya yang digeser.

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_putar_ue.py
Log: Hermes/Art/combo-iter2/Log/putar_ue.json
"""
import json
import os

import unreal

MX = "/Game/Hermes/ComboIter2/Mixamo"
LOG = unreal.Paths.convert_relative_path_to_full(
    unreal.Paths.project_dir() + "Hermes/Art/combo-iter2/Log/putar_ue.json")
BONE = "root"
PELVIS = "pelvis"
HANYA = {"air_slam"}

AL = unreal.AnimationLibrary
EAL = unreal.EditorAssetLibrary
hasil = []


def log(msg):
    unreal.log(f"[putar] {msg}")


def yaw_pelvis(seq):
    """Yaw pelvis (WORLD) per frame, sudah dibuka (unwrap) supaya tidak lompat di 180."""
    model = seq.get_editor_property("data_model_interface")
    n = model.get_number_of_frames()
    L = AL.get_sequence_length(seq)
    o = unreal.AnimPoseEvaluationOptions()
    mentah = []
    for i in range(n):
        t = min(L * i / float(n - 1), L)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        q = unreal.AnimPoseExtensions.get_bone_pose(p, PELVIS, unreal.AnimPoseSpaces.WORLD).rotation
        mentah.append(q.rotator().yaw)
    buka = [mentah[0]]
    for y in mentah[1:]:
        d = (y - buka[-1] + 180.0) % 360.0 - 180.0
        buka.append(buka[-1] + d)
    return [y - buka[0] for y in buka]


def putar(seq):
    """Beri yaw koreksi pada tulang root agar putaran badan berakhir di 0 derajat."""
    model = seq.get_editor_property("data_model_interface")
    n = model.get_number_of_frames()
    L = AL.get_sequence_length(seq)
    o = unreal.AnimPoseEvaluationOptions()

    yaw_p = yaw_pelvis(seq)
    akhir = yaw_p[-1]
    sisa = akhir - 360.0 * round(akhir / 360.0)      # bagian yang membuat badan menyamping
    log(f"pelvis berputar {akhir:.1f} deg, sisa menyamping {sisa:.1f} deg")

    pos, rot, scl = [], [], []
    for i in range(n):
        t = min(L * i / float(n - 1), L)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        tr = unreal.AnimPoseExtensions.get_bone_pose(p, BONE, unreal.AnimPoseSpaces.LOCAL)
        pos.append(tr.translation)
        r = tr.rotation.rotator()
        koreksi = -sisa * (yaw_p[i] / akhir) if akhir else 0.0
        rot.append(unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=r.yaw + koreksi).quaternion())
        scl.append(tr.scale3d)

    ctrl = unreal.new_object(unreal.AnimSequencerController, seq)
    ctrl.set_model(model)
    ok = ctrl.set_bone_track_keys(BONE, pos, rot, scl)
    EAL.save_loaded_asset(seq, only_if_is_dirty=False)

    yaw_s = yaw_pelvis(seq)
    log(f"sesudah: pelvis {yaw_s[-1]:.1f} deg (target 360), awal {yaw_s[0]:.1f}")
    return ok, akhir, sisa, yaw_s[-1]


def main():
    for peran in sorted(HANYA):
        seq = unreal.load_asset(f"{MX}/A_Aksa_Mx_{peran}")
        if not seq:
            log(f"LEWAT {peran}: aset tidak ada")
            continue
        ok, sebelum, sisa, sesudah = putar(seq)
        hasil.append({"peran": peran, "ok": bool(ok), "yaw_sebelum": round(sebelum, 1),
                      "sisa_dikoreksi": round(sisa, 1), "yaw_sesudah": round(sesudah, 1)})
        log(f"{peran:12s} {sebelum:.1f} -> {sesudah:.1f} deg | ok={ok}")

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(hasil, f, indent=1)
    log(f"selesai -> {LOG}")


main()
