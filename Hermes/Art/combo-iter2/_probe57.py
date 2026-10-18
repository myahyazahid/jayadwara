
import unreal
EAL = unreal.EditorAssetLibrary
for n in ("A_uji_a","A_uji_b","A_uji_c","A_uji_keys_v2","A_uji_keys"):
    p = "/Game/Hermes/ComboIter2/_uji/" + n
    if EAL.does_asset_exist(p):
        print("hapus", n, EAL.delete_asset(p))
print("folder tersisa:", EAL.does_directory_exist("/Game/Hermes/ComboIter2/_uji"))
