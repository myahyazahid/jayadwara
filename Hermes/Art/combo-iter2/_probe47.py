
import unreal
EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01")
model = seq.get_editor_property("data_model_interface")
print("frames", model.get_number_of_frames(), "keys", model.get_number_of_keys(), "tracks", model.get_num_bone_tracks())
for i in range(model.get_num_bone_tracks()):
    tr = model.get_bone_track_by_index(i)
    name = tr.get_editor_property("bone_name")
    pos = tr.get_editor_property("positional_keys")
    if not pos: continue
    xs = [k.x for k in pos]; ys = [k.y for k in pos]; zs = [k.z for k in pos]
    rng = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))
    if rng > 0.5:
        print(f"  {str(name):20s} n={len(pos):4d} X {min(xs):7.2f}..{max(xs):7.2f} Y {min(ys):7.2f}..{max(ys):7.2f} Z {min(zs):7.2f}..{max(zs):7.2f}")
o = unreal.AnimPoseEvaluationOptions()
p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, 0.0, o)
r = unreal.AnimPoseExtensions.get_bone_pose(p, "root", unreal.AnimPoseSpaces.WORLD)
print("root world rot:", r.rotation, "loc", r.translation)
