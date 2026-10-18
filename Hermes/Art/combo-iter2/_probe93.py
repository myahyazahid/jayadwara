
import unreal
o = unreal.AnimPoseEvaluationOptions()
for peran in ("light_01", "light_02"):
    seq = unreal.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{peran}")
    L = unreal.AnimationLibrary.get_sequence_length(seq)
    fr, fl, fz = [], [], []
    n = int(L/0.04)
    for i in range(n+1):
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, 0.04*i, o)
        g = lambda b: unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation
        fr.append(g("foot_r").y); fl.append(g("foot_l").y); fz.append(g("foot_r").z)
    print(f"{peran} {L:.2f}s: kakiR Y {min(fr):.1f}..{max(fr):.1f} (mundur {max(fr)-min(fr):.1f} cm) | kakiL Y {min(fl):.1f}..{max(fl):.1f} | kakiR Z maks {max(fz):.1f}")
