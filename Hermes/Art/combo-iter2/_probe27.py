
import unreal
seq = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
model = seq.data_model_interface
print("model dir:", [x for x in dir(model) if not x.startswith("_")])
try:
    c = model.get_controller()
    print("controller:", c, type(c))
except Exception as e:
    print("get_controller GAGAL:", str(e)[:120])
