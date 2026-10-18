
import unreal
AL = unreal.AnimationLibrary; EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air_slam")
o = unreal.AnimPoseEvaluationOptions(); L = AL.get_sequence_length(seq)
ys=[]
for i in range(0,11):
    t=min(L*i/10.0,L)
    p=unreal.AnimPoseExtensions.get_anim_pose_at_time(seq,t,o)
    ys.append(unreal.AnimPoseExtensions.get_bone_pose(p,"pelvis",unreal.AnimPoseSpaces.WORLD).translation.y)
print("air_slam pelvis Y", round(min(ys),1), round(max(ys),1))
