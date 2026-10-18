import unreal

EAL = unreal.EditorAssetLibrary
MX = "/Game/Hermes/ComboIter2/Mixamo"
MONT = "/Game/Hermes/ComboIter2/Montages"

for peran in ("finisher_02", "air_slam"):
    m = EAL.load_asset("%s/AM_Hermes_%s" % (MONT, peran))
    seq_baru = EAL.load_asset("%s/A_Aksa_Mx_%s" % (MX, peran))
    lama = m.get_editor_property("sequence")
    print("[G] %s: seq lama %s (%.3f s) | montage %.3f s | seq baru %.3f s" % (
        peran, lama.get_name() if lama else "-", lama.get_play_length() if lama else 0.0,
        m.get_play_length(), seq_baru.get_play_length()))
    m.set_editor_property("sequence", seq_baru)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    m2 = EAL.load_asset("%s/AM_Hermes_%s" % (MONT, peran))
    s2 = m2.get_editor_property("sequence")
    print("[G] %s: setelah ganti -> seq %s | montage %.3f s" % (
        peran, s2.get_name() if s2 else "-", m2.get_play_length()))
