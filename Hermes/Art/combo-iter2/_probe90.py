
import unreal
o = unreal.AnimPoseEvaluationOptions()
for peran in ("light_01", "light_02"):
    seq = unreal.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{peran}")
    L = unreal.AnimationLibrary.get_sequence_length(seq)
    print(f"=== {peran} {L:.2f} s (mulai di klip asli 0.18)")
    n = int(L/0.05)
    for i in range(n+1):
        t = 0.05*i
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        g = lambda b: unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation
        hl, hr, fl, fr = g("hand_l"), g("hand_r"), g("foot_l"), g("foot_r")
        print(f"t={t:4.2f} (asli {0.18+t:4.2f}) tanganL Y={hl.y:6.1f} tanganR Y={hr.y:6.1f} | kakiL Y={fl.y:6.1f} kakiR Y={fr.y:6.1f} Z={fr.z:5.1f}")
