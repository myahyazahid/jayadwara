
import unreal
AL = unreal.AnimationLibrary; EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air_slam")
o = unreal.AnimPoseEvaluationOptions(); L = AL.get_sequence_length(seq)
print("panjang", round(L,2), "frame", seq.get_editor_property("data_model_interface").get_number_of_frames())
for i in range(0, 28):
    t = L*i/27.0
    p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
    g = lambda b: unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation
    r = unreal.AnimPoseExtensions.get_bone_pose(p, "root", unreal.AnimPoseSpaces.LOCAL).translation
    pv = g("pelvis"); hv = g("head"); h = g("hand_r")
    print(f"t={t:4.2f} rootZ={r.z:6.1f} pelvisZ={pv.z:6.1f} kepalaZ={hv.z:6.1f} tanganR Z={h.z:6.1f} Y={h.y:6.1f}")
