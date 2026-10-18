"""Ukur gerak satu animasi retarget di UE, per frame (combo iterasi 2).

Dipakai untuk menjawab "kenapa karakter seperti bergeser ke samping": memisahkan
  * translasi WORLD pelvis (X = samping, Y = depan, Z = tinggi),
  * translasi LOCAL pelvis & root (apa yang dibawa klip),
  * yaw (putaran badan) root dan pelvis.
Hanya membaca, tidak menyimpan apa pun ke aset.

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_probe_ue.py
Log : Hermes/Art/combo-iter2/Log/probe_ue.json
"""
import json
import math
import os

import unreal

MX = "/Game/Hermes/ComboIter2/Mixamo"
LOG = unreal.Paths.convert_relative_path_to_full(
    unreal.Paths.project_dir() + "Hermes/Art/combo-iter2/Log/probe_ue.json")
PERAN = ["air_slam"]


def yaw(q):
    """Yaw (derajat) dari quaternion: arah hadap pada bidang XY."""
    fwd = unreal.Vector(1.0, 0.0, 0.0)
    r = q.rotator()
    return round(r.yaw, 1)


def main():
    o = unreal.AnimPoseEvaluationOptions()
    hasil = []
    for peran in PERAN:
        seq = unreal.load_asset(f"{MX}/A_Aksa_Mx_{peran}")
        if not seq:
            unreal.log_error(f"[probe_ue] aset tidak ada: {peran}")
            continue
        L = unreal.AnimationLibrary.get_sequence_length(seq)
        model = seq.get_editor_property("data_model_interface")
        n = model.get_number_of_frames()
        baris = []
        for i in range(n):
            t = min(L * i / float(max(n - 1, 1)), L)
            p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
            pw = unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD)
            pl = unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.LOCAL)
            rl = unreal.AnimPoseExtensions.get_bone_pose(p, "root", unreal.AnimPoseSpaces.LOCAL)
            hw = unreal.AnimPoseExtensions.get_bone_pose(p, "head", unreal.AnimPoseSpaces.WORLD)
            baris.append({
                "frame": i,
                "t": round(t, 3),
                "pelvis_wx": round(pw.translation.x, 1),
                "pelvis_wy": round(pw.translation.y, 1),
                "pelvis_wz": round(pw.translation.z, 1),
                "pelvis_lx": round(pl.translation.x, 1),
                "pelvis_ly": round(pl.translation.y, 1),
                "root_lx": round(rl.translation.x, 1),
                "root_ly": round(rl.translation.y, 1),
                "root_yaw": yaw(rl.rotation),
                "pelvis_yaw": yaw(pl.rotation),
                "head_wx": round(hw.translation.x, 1),
                "head_wy": round(hw.translation.y, 1),
            })
        rentang = {}
        for k in ("pelvis_wx", "pelvis_wy", "pelvis_wz", "pelvis_lx", "pelvis_ly",
                  "root_lx", "root_ly", "root_yaw", "pelvis_yaw", "head_wx", "head_wy"):
            v = [b[k] for b in baris]
            rentang[k] = [min(v), max(v), round(max(v) - min(v), 1)]
        hasil.append({"peran": peran, "panjang": round(L, 3), "frame": n,
                      "rentang": rentang, "sampel": baris})
        unreal.log(f"[probe_ue] {peran} {L:.3f} s / {n} frame")
        for k, v in rentang.items():
            unreal.log(f"[probe_ue]   {k:12s} {v[0]:8.1f} .. {v[1]:8.1f}  (rentang {v[2]:6.1f})")
        unreal.log("[probe_ue] frame | pelvisW x/y/z      | pelvisL x/y   | root yaw | headW x/y")
        for b in baris:
            unreal.log("[probe_ue] %5d | %7.1f %7.1f %7.1f | %6.1f %6.1f | %7.1f | %7.1f %7.1f" % (
                b["frame"], b["pelvis_wx"], b["pelvis_wy"], b["pelvis_wz"],
                b["pelvis_lx"], b["pelvis_ly"], b["root_yaw"], b["head_wx"], b["head_wy"]))

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(hasil, f, indent=1)
    unreal.log(f"[probe_ue] json -> {LOG}")


main()
