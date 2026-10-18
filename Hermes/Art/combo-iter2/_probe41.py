
import unreal
AL = unreal.AnimationLibrary; EAL = unreal.EditorAssetLibrary
for r in ("light_01","light_02","light_04"):
    seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_" + r)
    L = AL.get_sequence_length(seq); o = unreal.AnimPoseEvaluationOptions()
    print("==", r, "panjang", round(L,2))
    out = []
    for i in range(0, 15):
        t = min(L*i/14.0, L)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        pv = unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).translation
        fr = unreal.AnimPoseExtensions.get_bone_pose(p, "foot_r", unreal.AnimPoseSpaces.WORLD).translation
        fl = unreal.AnimPoseExtensions.get_bone_pose(p, "foot_l", unreal.AnimPoseSpaces.WORLD).translation
        out.append(f"t={t:4.2f} pelvisY={pv.y:6.1f} kakiR={fr.y:6.1f} kakiL={fl.y:6.1f}")
    print("\n".join(out))
