
import unreal
EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01")
model = seq.get_editor_property("data_model_interface")
tr = model.get_bone_track_by_index(0)
print("TR:", [x for x in dir(tr) if not x.startswith("_")])
it = tr.get_editor_property("internal_track") if hasattr(tr, "get_editor_property") else None
print("IT:", [x for x in dir(it) if not x.startswith("_")] if it else None)
print("names[0:5]", model.get_bone_track_names()[:5])
