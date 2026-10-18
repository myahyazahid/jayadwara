import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
PATH = "/Game/Hermes/ComboIter2/Montages/AM_Hermes_finisher_02"
TRACK = "Combat"

# puncak tendangan (cek_retarget): foot_r @0,767 s dan @0,967 s
BARU = [(0.65, 0.22, "foot_r", False), (0.85, 0.20, "foot_r", True)]

m = EAL.load_asset(PATH)

combo = []
for ev in AL.get_animation_notify_events(m):
    nsc = ev.get_editor_property("notify_state_class")
    if nsc and "ComboWindow" in nsc.get_class().get_name():
        combo.append((round(AL.get_anim_notify_event_trigger_time(ev), 3),
                      round(AL.get_anim_notify_event_duration(ev), 3)))
print("[H] combo window lama: %s" % combo)

AL.remove_animation_notify_events_by_track(m, TRACK)
for start, dur, socket, new_hit in BARU:
    ev = AL.add_animation_notify_state_event(m, TRACK, start, dur, unreal.JDAnimNotifyState_HitWindow)
    ev.set_editor_property("socket_name", socket)
    ev.set_editor_property("new_hit", new_hit)
for start, dur in combo:
    AL.add_animation_notify_state_event(m, TRACK, start, dur, unreal.JDAnimNotifyState_ComboWindow)

EAL.save_loaded_asset(m)

m2 = EAL.load_asset(PATH)
for ev in AL.get_animation_notify_events(m2):
    nsc = ev.get_editor_property("notify_state_class")
    n = ev.get_editor_property("notify")
    cls = nsc.get_class().get_name() if nsc else (n.get_class().get_name() if n else "?")
    t = AL.get_anim_notify_event_trigger_time(ev)
    d = AL.get_anim_notify_event_duration(ev)
    if nsc and "HitWindow" in cls:
        print("[H] %s t=%.3f d=%.3f (nyata %.3f-%.3f) socket=%s new_hit=%s" % (
            cls, t, d, t / 1.25, (t + d) / 1.25,
            nsc.get_editor_property("socket_name"), nsc.get_editor_property("new_hit")))
    else:
        print("[H] %s t=%.3f d=%.3f (nyata %.3f-%.3f)" % (cls, t, d, t / 1.25, (t + d) / 1.25))
