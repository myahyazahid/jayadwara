
import unreal
EAL = unreal.EditorAssetLibrary
src = "/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01"
tmp = "/Game/Hermes/ComboIter2/_uji/A_uji_keys"
EAL.delete_asset(tmp)
dup = EAL.duplicate_asset(src, tmp)
model = dup.get_editor_property("data_model_interface")
print("model:", model.get_class().get_name())
print("MODEL:", [x for x in dir(model) if x.startswith("get_") or "track" in x.lower() or "key" in x.lower()])
try:
    ctrl = unreal.new_object(unreal.AnimSequencerController, dup)
    print("ctrl:", ctrl)
except Exception as e:
    print("new_object gagal:", e)
