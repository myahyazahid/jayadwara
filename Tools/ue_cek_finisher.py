import unreal

EAL = unreal.EditorAssetLibrary
prof = EAL.load_asset("/Game/Jayadwara/Data/DA_CombatProfile_Human")
if not prof:
    print("[F] DA tidak ketemu")
else:
    print("[F] montage_play_rate profil = %.2f" % prof.get_editor_property("montage_play_rate"))
    fins = prof.get_editor_property("heavy_finishers")
    for i, s in enumerate(fins):
        m = s.get_editor_property("montage")
        rate = s.get_editor_property("play_rate")
        if m:
            ln = m.get_play_length()
            print("[F] finisher[%d] %s | rate %.2f | panjang %.2f s -> efektif %.2f s" % (
                i, m.get_name(), rate, ln, ln / max(rate, 0.01)))
        else:
            print("[F] finisher[%d] kosong (pakai pukulan berat biasa)" % i)

    steps = prof.get_editor_property("light_combo")
    for i, s in enumerate(steps):
        m = s.get_editor_property("montage")
        rate = s.get_editor_property("play_rate")
        if m:
            ln = m.get_play_length()
            print("[F] light[%d] %s | rate %.2f | %.2f s -> efektif %.2f s" % (
                i, m.get_name(), rate, ln, ln / max(rate, 0.01)))

    air = prof.get_editor_property("air_attack")
    if air.get_editor_property("montage"):
        m = air.get_editor_property("montage")
        print("[F] air %s | %.2f s" % (m.get_name(), m.get_play_length()))
