
import unreal
o = unreal.AnimPoseEvaluationOptions()
for peran in ("light_01", "light_02"):
    seq = unreal.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{peran}")
    L = unreal.AnimationLibrary.get_sequence_length(seq)
    print(f"=== {peran} panjang {L:.2f} s")
    n = 22
    for i in range(n+1):
        t = L*i/n
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        g = lambda b: unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation
        fl, fr, pv, hl = g("foot_l"), g("foot_r"), g("pelvis"), g("hand_r")
        print(f"t={t:4.2f} kakiL Y={fl.y:6.1f} Z={fl.z:5.1f} | kakiR Y={fr.y:6.1f} Z={fr.z:5.1f} | pelvis Y={pv.y:5.1f} | tanganR Y={hl.y:6.1f}")
