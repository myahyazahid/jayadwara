
import unreal
print("AnimDataController?", hasattr(unreal, "AnimDataController"))
print("AnimLibrary bone/pose:", [x for x in dir(unreal.AnimationLibrary) if "bone" in x.lower() or "pose" in x.lower()])
if hasattr(unreal, "AnimDataController"):
    print("controller methods:", [x for x in dir(unreal.AnimDataController) if not x.startswith("_")])
seq = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
print("seq props:", [x for x in dir(seq) if "bone" in x.lower() or "model" in x.lower() or "data" in x.lower()])
