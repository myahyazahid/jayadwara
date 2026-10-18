
import unreal
AL = unreal.AnimationLibrary
EAL = unreal.EditorAssetLibrary
roles = ["light_01","light_02","light_03","light_04","lunge","back","finisher_01","finisher_02","finisher_03","air","air_slam"]
for r in roles:
    seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_" + r)
    if not seq: continue
    L = AL.get_sequence_length(seq); o = unreal.AnimPoseEvaluationOptions()
    ys = []; zs = []
    for i in range(0, 25):
        t = min(L*i/24.0, L)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        v = unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).translation
        ys.append(v.y); zs.append(v.z)
    print(f"{r:12s} pelvis Y awal {ys[0]:7.1f} akhir {ys[-1]:7.1f} min {min(ys):7.1f} max {max(ys):7.1f} | Z {zs[0]:6.1f}..{zs[-1]:6.1f}")
