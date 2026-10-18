
import unreal
seq = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
print("data_model:", type(seq.get_editor_property("data_model")))
print("iface:", type(seq.get_editor_property("data_model_interface")))
