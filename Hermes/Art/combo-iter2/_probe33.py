
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
opts = unreal.AnimPoseEvaluationOptions()
w = unreal.AnimPoseSpaces.WORLD
for nm in ("air", "light_01"):
    seq = EAL.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{nm}")
    L = AL.get_sequence_length(seq)
    print("==", nm, round(L, 2))
    for t in (0.0, L/2, L):
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
        vals = {}
        for b in ("root", "pelvis", "head", "foot_l"):
            p = unreal.AnimPoseExtensions.get_bone_pose(pose, b, w).translation
            vals[b] = (round(p.x,1), round(p.y,1), round(p.z,1))
        print("  t", round(t,2), vals)
