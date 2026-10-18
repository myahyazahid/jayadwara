import unreal

EAL = unreal.EditorAssetLibrary
MONT = "/Game/Hermes/ComboIter2/Montages"

for peran in ("finisher_02", "air_slam"):
    p = "%s/AM_Hermes_%s" % (MONT, peran)
    ok = EAL.reload_asset(p)
    m = EAL.load_asset(p)
    print("[R2] %s reload=%s panjang=%.3f s" % (peran, ok, m.get_play_length() if m else 0.0))
