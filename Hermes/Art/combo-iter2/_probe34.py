
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
opts = unreal.AnimPoseEvaluationOptions()
w = unreal.AnimPoseSpaces.WORLD
for p in ("/Game/Hermes/ComboIter2/Mixamo/Raw/A_Aksa_Mx_air",
          "/Game/Hermes/ComboIter2/Mixamo/Raw/A_Aksa_Mx_light_01"):
    seq = EAL.load_asset(p)
    print("==", p.split("/")[-1], round(AL.get_sequence_length(seq),2))
    pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, 0.0, opts)
    for b in ("root", "pelvis", "head", "foot_l"):
        try:
            t = unreal.AnimPoseExtensions.get_bone_pose(pose, b, w).translation
            print("   ", b, (round(t.x,1), round(t.y,1), round(t.z,1)))
        except Exception as e:
            print("   ", b, "tidak ada")
