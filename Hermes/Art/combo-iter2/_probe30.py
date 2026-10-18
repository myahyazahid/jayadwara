
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
tmp = "/Game/Hermes/ComboIter2/_TMP_air_test"
EAL.delete_asset(tmp)
dup = EAL.duplicate_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air", tmp)
opts = unreal.AnimPoseEvaluationOptions()

def ringkas(seq, label):
    L = AL.get_sequence_length(seq)
    pw=[]; fw=[]
    for i in range(0, 31):
        t = min(L * i / 30.0, L)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
        p = unreal.AnimPoseExtensions.get_bone_pose(pose, "pelvis", unreal.AnimPoseSpaces.WORLD)
        f = unreal.AnimPoseExtensions.get_bone_pose(pose, "foot_r", unreal.AnimPoseSpaces.WORLD)
        pw.append(p.rotation); fw.append(f.translation)
    dot = min(abs(pw[0].x*q.x+pw[0].y*q.y+pw[0].z*q.z+pw[0].w*q.w) for q in pw)
    # sudut rotasi pelvis dunia (derajat) relatif frame 0
    import math
    ang = 2*math.degrees(math.acos(min(1.0, abs(dot))))
    print(f"{label}: pelvis dunia rot maks {ang:6.1f} deg | foot_r Y {min(t.y for t in fw):7.1f}..{max(t.y for t in fw):7.1f} Z {min(t.z for t in fw):6.1f}..{max(t.z for t in fw):6.1f}")

ringkas(dup, "sebelum     ")
AL.remove_bone_animation(dup, "root")
EAL.save_loaded_asset(dup, only_if_is_dirty=False)
ringkas(dup, "tanpa root   ")
