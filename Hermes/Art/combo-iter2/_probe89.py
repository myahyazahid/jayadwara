
import unreal
o = unreal.AnimPoseEvaluationOptions()
for peran in ("light_01", "light_02"):
    seq = unreal.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{peran}")
    L = unreal.AnimationLibrary.get_sequence_length(seq)
    ys = {"foot_l": [], "foot_r": []}
    print(f"=== {peran} {L:.2f} s")
    for i in range(13):
        t = L*i/12
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        g = lambda b: unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation
        fl, fr = g("foot_l"), g("foot_r")
        ys["foot_l"].append(fl.y); ys["foot_r"].append(fr.y)
        print(f"t={t:4.2f} kakiL Y={fl.y:6.1f} Z={fl.z:5.1f} | kakiR Y={fr.y:6.1f} Z={fr.z:5.1f}")
    for k, v in ys.items():
        print(f"   {k}: rentang Y {min(v):.1f}..{max(v):.1f} (geser {max(v)-min(v):.1f} cm)")
