
import unreal
EAL = unreal.EditorAssetLibrary
for role in ("light_01","light_02","light_03","light_04","lunge","back","air","air_slam"):
    seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_" + role)
    model = seq.get_editor_property("data_model_interface")
    print("==", role, "frames", model.get_number_of_frames())
    for i in range(model.get_num_bone_tracks()):
        tr = model.get_bone_track_by_index(i)
        name = str(tr.get_editor_property("name"))
        data = tr.get_editor_property("internal_track_data")
        pos = data.get_positional_keys()
        if not pos: continue
        xs=[k.x for k in pos]; ys=[k.y for k in pos]; zs=[k.z for k in pos]
        rng = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))
        if rng > 0.5:
            print(f"   {name:22s} n={len(pos):4d} X {min(xs):7.2f}..{max(xs):7.2f} Y {min(ys):7.2f}..{max(ys):7.2f} Z {min(zs):7.2f}..{max(zs):7.2f}")
