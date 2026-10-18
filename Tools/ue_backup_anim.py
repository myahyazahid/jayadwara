import unreal

EAL = unreal.EditorAssetLibrary
BK = "/Game/Hermes/ComboIter2/_Backup_Lama"
if not EAL.does_directory_exist(BK):
    EAL.make_directory(BK)

ASAL = [
    "/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_finisher_02",
    "/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air_slam",
    "/Game/Hermes/ComboIter2/Mixamo/Raw/A_Aksa_Mx_finisher_02",
    "/Game/Hermes/ComboIter2/Mixamo/Raw/A_Aksa_Mx_air_slam",
    "/Game/Hermes/ComboIter2/Montages/AM_Hermes_finisher_02",
    "/Game/Hermes/ComboIter2/Montages/AM_Hermes_air_slam",
]

for p in ASAL:
    if not EAL.does_asset_exist(p):
        print("[B] lewat (tidak ada): %s" % p)
        continue
    nama = p.split("/")[-1] + "_LAMA"
    dst = "%s/%s" % (BK, nama)
    if EAL.does_asset_exist(dst):
        EAL.delete_asset(dst)
    if EAL.duplicate_asset(p, dst):
        a = EAL.load_asset(dst)
        ex = ""
        if isinstance(a, unreal.AnimSequence) or isinstance(a, unreal.AnimMontage):
            ex = " | %.3f s" % a.get_play_length()
        print("[B] OK %s -> %s%s" % (p.split('/')[-1], dst.split('/')[-1], ex))
    else:
        print("[B] GAGAL %s" % p)
