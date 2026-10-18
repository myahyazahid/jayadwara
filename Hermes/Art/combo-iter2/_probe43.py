
import unreal
EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01")
mon = EAL.load_asset("/Game/Hermes/ComboIter2/Montages/AM_Hermes_light_01")
print("SEQ:", [x for x in dir(seq) if any(k in x.lower() for k in ("length","play","trim","section","frame","rate","data_model","track"))])
print("MON:", [x for x in dir(mon) if any(k in x.lower() for k in ("length","play","section","trim","blend","rate","slot"))])
print("MOD:", [x for x in dir(unreal) if "Montage" in x or "AnimSequence" in x or "AnimationLibrary" in x])
