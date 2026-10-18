
import unreal
EAL = unreal.EditorAssetLibrary
for n in ("A_pangkas_test","A_pangkas_test2","A_pangkas_test3","A_pangkas_test4","A_pangkas_test5"):
    p = "/Game/Hermes/ComboIter2/_uji/" + n
    if EAL.does_asset_exist(p):
        EAL.delete_asset(p); print("hapus", n)
print("sisa _uji:", EAL.list_assets("/Game/Hermes/ComboIter2/_uji"))
