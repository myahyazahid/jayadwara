
import unreal
EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01")
model = seq.get_editor_property("data_model_interface")
data = model.get_bone_track_by_index(0).get_editor_property("internal_track_data")
print("DATA:", [x for x in dir(data) if not x.startswith("_")])
print("EXT:", [x for x in dir(unreal.RawAnimSequenceTrackExtensions) if not x.startswith("_")])
