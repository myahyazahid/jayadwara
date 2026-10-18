
import unreal
EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01")
model = seq.get_editor_property("data_model_interface")
for i in range(min(model.get_num_bone_tracks(), 8)):
    tr = model.get_bone_track_by_index(i)
    d = tr.get_editor_property("internal_track_data")
    print(f"{str(tr.get_editor_property('name')):22s} pos={len(d.get_positional_keys()):4d} rot={len(d.get_rotational_keys()):4d} scl={len(d.get_scale_keys()):4d}")
for nm in ("root","pelvis"):
    if model.is_valid_bone_track_name(nm):
        tr = model.get_bone_track_by_name(nm)
        d = tr.get_editor_property("internal_track_data")
        pos = d.get_positional_keys()
        print(nm, "pos", len(pos), "rot", len(d.get_rotational_keys()))
        if pos:
            print("   pertama", pos[0], "terakhir", pos[-1])
