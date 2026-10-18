
import unreal
p = unreal.load_asset("/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes")
seq = unreal.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
print("profil:", p.get_name() if p else None, "| seq:", seq.get_name() if seq else None)
if p:
    for k in ("air_hang_time","air_hang_gravity_scale","air_combo_max","air_slam_speed","air_slam_recovery"):
        try: print(" ", k, "=", p.get_editor_property(k))
        except Exception as e: print(" ", k, "ERR", str(e)[:60])
if seq:
    o = unreal.AnimPoseEvaluationOptions(); L = unreal.AnimationLibrary.get_sequence_length(seq)
    zs=[]; hz=[]
    for i in range(0,21):
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, L*i/20.0, o)
        zs.append(unreal.AnimPoseExtensions.get_bone_pose(pose,"pelvis",unreal.AnimPoseSpaces.WORLD).translation.z)
        hz.append(unreal.AnimPoseExtensions.get_bone_pose(pose,"head",unreal.AnimPoseSpaces.WORLD).translation.z)
    print("air pelvis Z", round(min(zs),1), round(max(zs),1), "| kepala Z", round(min(hz),1), round(max(hz),1))
