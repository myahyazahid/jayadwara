
import unreal
o = unreal.AnimPoseEvaluationOptions()
BONES = ["head","pelvis","hand_l","hand_r","foot_l","foot_r","lowerarm_l","lowerarm_r"]
def pose(peran, akhir=False):
    seq = unreal.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{peran}")
    L = unreal.AnimationLibrary.get_sequence_length(seq)
    p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, L if akhir else 0.0, o)
    return {b: unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation for b in BONES}, L
for a, b in (("light_01","light_02"), ("light_02","light_03"), ("light_03","light_04")):
    pa, La = pose(a, True); pb, Lb = pose(b, False)
    d = {k: (pa[k]-pb[k]).length() for k in BONES}
    print(f"{a} ({La:.2f}s) -> {b} ({Lb:.2f}s): " + ", ".join(f"{k} {v:.0f}" for k,v in sorted(d.items(), key=lambda x:-x[1])[:4]) + f" | rerata {sum(d.values())/len(d):.1f}")
