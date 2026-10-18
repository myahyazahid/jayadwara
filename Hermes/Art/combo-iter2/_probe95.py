
import unreal
o = unreal.AnimPoseEvaluationOptions()
for peran in ("light_03", "light_04"):
    seq = unreal.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{peran}")
    L = unreal.AnimationLibrary.get_sequence_length(seq)
    print(f"=== {peran} {L:.2f} s")
    n = int(L/0.1)
    for i in range(n+1):
        t = 0.1*i
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        g = lambda b: unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation
        fr, fl, hr, pv = g("foot_r"), g("foot_l"), g("hand_r"), g("pelvis")
        print(f"t={t:4.1f} kakiR Y={fr.y:6.1f} Z={fr.z:5.1f} | kakiL Y={fl.y:6.1f} Z={fl.z:5.1f} | tanganR Y={hr.y:6.1f} | pelvis Z={pv.z:5.1f}")
