
import unreal
print("ada kelas?", hasattr(unreal, "AnimationSequencerDataModel"))
if hasattr(unreal, "AnimationSequencerDataModel"):
    print([x for x in dir(unreal.AnimationSequencerDataModel) if not x.startswith("_")])
seq = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
m = seq.data_model_interface
print("kelas asli:", m.get_class().get_name())
print("methods:", [x for x in dir(m) if "set" in x.lower() or "add" in x.lower() or "control" in x.lower()])
