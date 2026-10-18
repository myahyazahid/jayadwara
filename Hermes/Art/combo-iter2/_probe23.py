
import unreal
print(unreal.AnimDataController.set_bone_track_keys.__doc__)
print("---- spaces:", [x for x in dir(unreal.AnimPoseSpaces) if not x.startswith("_")])
seq = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
opts = unreal.AnimPoseEvaluationOptions()
pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, 0.2, opts)
loc = unreal.AnimPoseExtensions.get_bone_pose(pose, "pelvis", unreal.AnimPoseSpaces.LOCAL)
print("local:", loc.translation, loc.rotation, loc.scale3d)
