
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
tmp = "/Game/Hermes/ComboIter2/_TMP_air_test"
EAL.delete_asset(tmp)
dup = EAL.duplicate_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air", tmp)

def rentang(seq, label, extract):
    o = unreal.AnimPoseEvaluationOptions()
    o.set_editor_property("extract_root_motion", extract)
    L = AL.get_sequence_length(seq)
    ys = []; zs = []; hy = []
    for i in range(0, 21):
        t = min(L * i / 20.0, L)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        r = unreal.AnimPoseExtensions.get_bone_pose(pose, "root", unreal.AnimPoseSpaces.LOCAL).translation
        h = unreal.AnimPoseExtensions.get_bone_pose(pose, "head", unreal.AnimPoseSpaces.WORLD).translation
        ys.append(r.y); zs.append(r.z); hy.append(h.z)
    print(f"{label} extract={extract}: root Y {min(ys):7.1f}..{max(ys):7.1f} Z {min(zs):6.1f}..{max(zs):6.1f} | head Z {min(hy):6.1f}..{max(hy):6.1f}")

rentang(dup, "sebelum", False)
rentang(dup, "sebelum", True)
dup.set_editor_property("enable_root_motion", True)
dup.set_editor_property("force_root_lock", True)
EAL.save_loaded_asset(dup, only_if_is_dirty=False)
rentang(dup, "rootlock", False)
rentang(dup, "rootlock", True)
