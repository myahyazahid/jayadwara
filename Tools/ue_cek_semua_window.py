import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
DIR = "/Game/Hermes/ComboIter2/Montages"

PUNCAK = {
    "air": 0.65, "air_slam": 1.25, "back": 0.25, "lunge": 0.95,
    "finisher_01": 0.5, "finisher_02": 0.767, "finisher_03": 1.417,
    "light_01": 0.55, "light_02": 0.633, "light_03": 0.95, "light_04": 0.933,
}

for nama, puncak in sorted(PUNCAK.items()):
    m = EAL.load_asset("%s/AM_Hermes_%s" % (DIR, nama))
    if not m:
        print("[K] %-12s montage tidak ada" % nama)
        continue
    wins = []
    for ev in AL.get_animation_notify_events(m):
        nsc = ev.get_editor_property("notify_state_class")
        if nsc and "HitWindow" in nsc.get_class().get_name():
            t = AL.get_anim_notify_event_trigger_time(ev)
            d = AL.get_anim_notify_event_duration(ev)
            wins.append((round(t, 3), round(t + d, 3)))
    panjang = m.get_play_length()
    ok = any(a <= puncak <= b for a, b in wins)
    print("[K] %-12s panjang %.2f puncak %.2f | jendela %s | pas? %s" % (
        nama, panjang, puncak, wins, "YA" if ok else "TIDAK"))
