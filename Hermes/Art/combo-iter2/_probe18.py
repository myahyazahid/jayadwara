
import unreal
EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
model = seq.data_model_interface
t = model.get_bone_track_by_name("pelvis")
it = t.get_editor_property("internal_track_data")
print("raw dir:", [x for x in dir(it) if not x.startswith("_")])
print("frames", model.get_number_of_frames(), "fps", model.get_frame_rate())
