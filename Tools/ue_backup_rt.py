import unreal

EAL = unreal.EditorAssetLibrary
BK = "/Game/Hermes/ComboIter2/_Backup_Lama"

for nama in ("A_Aksa_Mx_finisher_02", "A_Aksa_Mx_air_slam"):
    asal = "/Game/Hermes/ComboIter2/Mixamo/" + nama
    dst = "%s/%s_RT_LAMA" % (BK, nama)
    if EAL.does_asset_exist(dst):
        EAL.delete_asset(dst)
    if EAL.duplicate_asset(asal, dst):
        a = EAL.load_asset(dst)
        print("[B2] OK %s (retarget) %.3f s" % (nama, a.get_play_length() if a else 0.0))
    else:
        print("[B2] GAGAL %s" % nama)
