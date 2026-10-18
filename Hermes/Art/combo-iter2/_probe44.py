
import unreal
EAL = unreal.EditorAssetLibrary
print("CTRL:", [x for x in dir(unreal.AnimSequencerController) if not x.startswith("_")])
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01")
dmi = seq.get_editor_property("data_model_interface")
print("DMI class:", dmi.get_class().get_name() if dmi else None)
c = dmi.get_controller()
print("controller class:", c.get_class().get_name())
print("CTRLINST:", [x for x in dir(c) if not x.startswith("_")])
