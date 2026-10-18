"""Ukur kurva yaw tulang `root` (dan pelvis) per frame pada animasi hasil retarget.

Dipakai untuk memutuskan koreksi putaran `air_slam`: perlu tahu bentuk kurvanya
(monoton? berhenti di derajat berapa?) sebelum memilih cara membetulkan.

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_probe_root_yaw.py
Log: Hermes/Art/combo-iter2/Log/root_yaw.txt
"""
import os

import unreal

MX = "/Game/Hermes/ComboIter2/Mixamo"
LOG = unreal.Paths.convert_relative_path_to_full(
    unreal.Paths.project_dir() + "Hermes/Art/combo-iter2/Log/root_yaw.txt")
PERAN = "air_slam"
AL = unreal.AnimationLibrary

seq = unreal.load_asset(f"{MX}/A_Aksa_Mx_{PERAN}")
o = unreal.AnimPoseEvaluationOptions()
L = AL.get_sequence_length(seq)
model = seq.get_editor_property("data_model_interface")
n = model.get_number_of_frames()

baris = [f"{PERAN}: {L:.3f} s, {n} frame, {n / L:.0f} fps"]
baris.append("   t    root_lokal  pelvis_world")
for i in range(n):
    t = min(L * i / float(n - 1), L)
    p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
    r = unreal.AnimPoseExtensions.get_bone_pose(p, "root", unreal.AnimPoseSpaces.LOCAL).rotation.rotator()
    pv = unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).rotation.rotator()
    baris.append("%5.2f  %8.1f  %10.1f" % (t, r.yaw, pv.yaw))

os.makedirs(os.path.dirname(LOG), exist_ok=True)
with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(baris) + "\n")
print("\n".join(baris))
