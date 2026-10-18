import unreal

EAL = unreal.EditorAssetLibrary
PATH = "/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes"
BARU = 1.25

prof = EAL.load_asset(PATH)
if not prof:
    print("[R] DA tidak ketemu")
else:
    fins = list(prof.get_editor_property("heavy_finishers"))
    if len(fins) < 2:
        print("[R] finisher kurang dari 2, dilewati")
    else:
        s = fins[1]
        lama = s.get_editor_property("play_rate")
        m = s.get_editor_property("montage")
        s.set_editor_property("play_rate", BARU)
        fins[1] = s
        prof.set_editor_property("heavy_finishers", fins)
        EAL.save_loaded_asset(prof)

        # baca balik
        prof2 = EAL.load_asset(PATH)
        fins2 = list(prof2.get_editor_property("heavy_finishers"))
        s2 = fins2[1]
        m2 = s2.get_editor_property("montage")
        print("[R] finisher_02: %s | laju %.2f -> %.2f | panjang %.2f s -> nyata %.2f s" % (
            m2.get_name() if m2 else "-", lama, s2.get_editor_property("play_rate"),
            m2.get_play_length() if m2 else 0.0,
            (m2.get_play_length() / s2.get_editor_property("play_rate")) if m2 else 0.0))
        print("[R] semua finisher: %s" % [
            "%s@%.2f" % (x.get_editor_property("montage").get_name() if x.get_editor_property("montage") else "-",
                         x.get_editor_property("play_rate")) for x in fins2])
