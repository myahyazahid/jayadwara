
import unreal
EAL = unreal.EditorAssetLibrary
print("data:", EAL.list_assets("/Game/Hermes/ComboIter2/Data"))
print("mixamo ada?", EAL.does_asset_exist("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air"))
print("montage:", EAL.list_assets("/Game/Hermes/ComboIter2/Montages"))
