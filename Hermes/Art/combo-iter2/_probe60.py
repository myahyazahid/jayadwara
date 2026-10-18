
import unreal
EAL = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary
SRC = "/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air_slam"
TMP = "/Game/Hermes/ComboIter2/_uji/A_pangkas_test2"
dup = EAL.duplicate_asset(SRC, TMP)
model = dup.get_editor_property("data_model_interface")
ctrl = unreal.new_object(unreal.AnimSequencerController, dup)
ctrl.set_model(model)
T0, T1, FPS = 1.40, 1.90, 24.0
n = int(round((T1 - T0) * FPS)) + 1
o = unreal.AnimPoseEvaluationOptions()
poses = [unreal.AnimPoseExtensions.get_anim_pose_at_time(dup, T0 + (T1-T0)*i/float(n-1), o) for i in range(n)]
for cara in ("set_play_length", "frame_number"):
    try:
        if cara == "set_play_length":
            ctrl.set_play_length((T1 - T0))
        else:
            ctrl.set_number_of_frames(unreal.FrameNumber(value=n))
        print(cara, "OK -> panjang", round(AL.get_sequence_length(dup), 3), "frame", model.get_number_of_frames())
        break
    except Exception as e:
        print(cara, "gagal:", str(e)[:120])
nama = list(model.get_bone_track_names())
gagal = 0
for b in nama:
    pos=[]; rot=[]; scl=[]
    for p in poses:
        tr = unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.LOCAL)
        pos.append(tr.translation); rot.append(tr.rotation); scl.append(tr.scale3d)
    try:
        if not ctrl.set_bone_track_keys(b, pos, rot, scl): gagal += 1
    except Exception: gagal += 1
EAL.save_loaded_asset(dup, only_if_is_dirty=False)
print("track gagal", gagal, "| panjang", round(AL.get_sequence_length(dup), 3))
o2 = unreal.AnimPoseEvaluationOptions()
for i in (0, n//2, n-1):
    p = unreal.AnimPoseExtensions.get_anim_pose_at_time(dup, (T1-T0)*i/float(n-1), o2)
    h = unreal.AnimPoseExtensions.get_bone_pose(p, "head", unreal.AnimPoseSpaces.WORLD).translation
    pv = unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).translation
    print(f"  t={i}: kepala Z {h.z:.1f} pelvis Z {pv.z:.1f}")
