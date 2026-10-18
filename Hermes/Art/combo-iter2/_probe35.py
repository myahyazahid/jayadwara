
import unreal
o = unreal.AnimPoseEvaluationOptions()
print([x for x in dir(o) if not x.startswith("_")])
for p in ("extract_root_motion", "retarget_transforms", "evaluate_curves"):
    try:
        print(p, "=", o.get_editor_property(p))
    except Exception:
        pass
seq = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
opts = unreal.AnimPoseEvaluationOptions()
pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, 0.0, opts)
print("head z (cek revert):", round(unreal.AnimPoseExtensions.get_bone_pose(pose, "head", unreal.AnimPoseSpaces.WORLD).translation.z, 1))
