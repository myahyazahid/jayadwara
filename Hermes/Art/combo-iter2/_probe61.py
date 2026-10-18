
import unreal
EAL = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary
SRC = "/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air_slam"
TMP = "/Game/Hermes/ComboIter2/_uji/A_pangkas_test3"
dup = EAL.duplicate_asset(SRC, TMP)
model = dup.get_editor_property("data_model_interface")
ctrl = unreal.new_object(unreal.AnimSequencerController, dup)
ctrl.set_model(model)
print("fps awal", model.get_frame_rate().numerator, "/", model.get_frame_rate().denominator)
T0, T1, FPS = 1.40, 1.90, 24.0
n = int(round((T1 - T0) * FPS)) + 1
o = unreal.AnimPoseEvaluationOptions()
poses = [unreal.AnimPoseExtensions.get_anim_pose_at_time(dup, T0 + (T1-T0)*i/float(n-1), o) for i in range(n)]
try:
    ctrl.set_frame_rate(unreal.FrameRate(numerator=24, denominator=1))
    print("fps ->", model.get_frame_rate().numerator)
except Exception as e:
    print("set_frame_rate gagal:", str(e)[:150])
ctrl.set_play_length(T1 - T0)
print("panjang", round(AL.get_sequence_length(dup), 3), "frame", model.get_number_of_frames())
for b in list(model.get_bone_track_names()):
    pos=[]; rot=[]; scl=[]
    for p in poses:
        tr = unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.LOCAL)
        pos.append(tr.translation); rot.append(tr.rotation); scl.append(tr.scale3d)
    ctrl.set_bone_track_keys(b, pos, rot, scl)
EAL.save_loaded_asset(dup, only_if_is_dirty=False)
print("panjang akhir", round(AL.get_sequence_length(dup), 3), "frame", model.get_number_of_frames())
o2 = unreal.AnimPoseEvaluationOptions()
for i in (0, 3, 6, 9, 12):
    t = (T1-T0)*i/12.0
    p = unreal.AnimPoseExtensions.get_anim_pose_at_time(dup, t, o2)
    h = unreal.AnimPoseExtensions.get_bone_pose(p, "head", unreal.AnimPoseSpaces.WORLD).translation
    hr = unreal.AnimPoseExtensions.get_bone_pose(p, "hand_r", unreal.AnimPoseSpaces.WORLD).translation
    print(f"  t={t:4.2f} kepala Z {h.z:6.1f} tanganR Z {hr.z:6.1f}")
