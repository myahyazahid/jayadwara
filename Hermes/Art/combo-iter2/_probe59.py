
import unreal
EAL = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary
SRC = "/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air_slam"
TMP = "/Game/Hermes/ComboIter2/_uji/A_pangkas_test"
if EAL.does_asset_exist(TMP):
    EAL.delete_asset(TMP)
dup = EAL.duplicate_asset(SRC, TMP)
model = dup.get_editor_property("data_model_interface")
ctrl = unreal.new_object(unreal.AnimSequencerController, dup)
ctrl.set_model(model)

T0, T1, FPS = 1.40, 1.90, 24.0
n = int(round((T1 - T0) * FPS)) + 1
o = unreal.AnimPoseEvaluationOptions()
poses = []
for i in range(n):
    t = T0 + (T1 - T0) * i / float(n - 1)
    poses.append(unreal.AnimPoseExtensions.get_anim_pose_at_time(dup, t, o))
nama = list(model.get_bone_track_names())
print("tulang", len(nama), "kunci", n)
try:
    ctrl.set_number_of_frames(n)
    print("set_number_of_frames ->", model.get_number_of_frames())
except Exception as e:
    print("set_number_of_frames gagal:", e)
gagal = 0
for b in nama:
    pos = []; rot = []; scl = []
    for p in poses:
        tr = unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.LOCAL)
        pos.append(tr.translation); rot.append(tr.rotation); scl.append(tr.scale3d)
    try:
        if not ctrl.set_bone_track_keys(b, pos, rot, scl):
            gagal += 1
    except Exception:
        gagal += 1
print("track gagal", gagal)
EAL.save_loaded_asset(dup, only_if_is_dirty=False)
print("panjang baru", round(AL.get_sequence_length(dup), 3))
for i in (0, n // 2, n - 1):
    p = poses[i]
    h = unreal.AnimPoseExtensions.get_bone_pose(p, "head", unreal.AnimPoseSpaces.WORLD).translation
    print("cek pose head Z", round(h.z, 1))
