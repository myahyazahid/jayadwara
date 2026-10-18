import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
PROF = "/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes"
MONT = "/Game/Hermes/ComboIter2/Montages"

prof = EAL.load_asset(PROF)

def cek(m, laju, label):
    if not m:
        print("[F] %s: kosong" % label)
        return
    p = m.get_play_length()
    print("[F] %s: %s | %.3f s | laju %.2f -> nyata %.3f s" % (label, m.get_name(), p, laju, p / max(laju, 0.01)))
    for ev in AL.get_animation_notify_events(m):
        nsc = ev.get_editor_property("notify_state_class")
        if nsc and "HitWindow" in nsc.get_class().get_name():
            t = AL.get_anim_notify_event_trigger_time(ev)
            d = AL.get_anim_notify_event_duration(ev)
            try:
                nh = nsc.get_editor_property("new_hit")
            except Exception:
                nh = "?"
            print("[F]    hit %.3f-%.3f (nyata %.3f-%.3f) socket=%s new_hit=%s" % (
                t, t + d, t / laju, (t + d) / laju,
                nsc.get_editor_property("socket_name"), nh))

fins = list(prof.get_editor_property("heavy_finishers"))
cek(fins[1].get_editor_property("montage"), fins[1].get_editor_property("play_rate"), "finisher_02 (LMB+LMB+E)")
slam = prof.get_editor_property("air_slam")
cek(slam.get_editor_property("montage"), slam.get_editor_property("play_rate"), "air_slam (lompat+E)")
print("[F] air_combo_max=%s" % prof.get_property_value("air_combo_max"))
