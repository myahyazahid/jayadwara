
import unreal
AL = unreal.AnimationLibrary; EAL = unreal.EditorAssetLibrary
for r in ("light_01","light_02","light_03","light_04","back","air"):
    seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_" + r)
    o = unreal.AnimPoseEvaluationOptions(); L = AL.get_sequence_length(seq)
    ys=[]
    for i in range(0,11):
        t=min(L*i/10.0,L)
        p=unreal.AnimPoseExtensions.get_anim_pose_at_time(seq,t,o)
        ys.append(unreal.AnimPoseExtensions.get_bone_pose(p,"pelvis",unreal.AnimPoseSpaces.WORLD).translation.y)
    print(f"{r:10s} pelvis world Y {min(ys):7.1f}..{max(ys):7.1f}")
