
import unreal
p = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes")
for k in ("air_hang_time","air_hang_gravity_scale","air_combo_max","air_slam_speed"):
    try: print(k, "=", p.get_editor_property(k))
    except Exception as e: print(k, "ERR", str(e)[:80])
print("props air:", [x for x in dir(p) if "air" in x.lower()][:20])
seq = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
o = unreal.AnimPoseEvaluationOptions(); L = unreal.AnimationLibrary.get_sequence_length(seq)
zs=[]
for i in range(0,21):
    t=L*i/20.0
    pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(seq,t,o)
    zs.append(unreal.AnimPoseExtensions.get_bone_pose(pose,"pelvis",unreal.AnimPoseSpaces.WORLD).translation.z)
print("air pelvis Z", round(min(zs),1), round(max(zs),1))
