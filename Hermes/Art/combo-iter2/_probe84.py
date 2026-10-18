
import unreal
seq = unreal.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
o = unreal.AnimPoseEvaluationOptions()
L = unreal.AnimationLibrary.get_sequence_length(seq)
prev = None
for i in range(0, 31):
    t = L*i/30.0
    p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
    g = lambda b: unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation
    fl, fr, pv = g("foot_l"), g("foot_r"), g("pelvis")
    sp = 0.0 if prev is None else ((fl - prev).length() / (L/30.0))
    prev = fl
    print(f"t={t:4.2f} kakiL Y={fl.y:6.1f} Z={fl.z:6.1f} (spd {sp:6.0f}) | kakiR Z={fr.z:6.1f} | pelvis Z={pv.z:6.1f}")
