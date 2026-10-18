import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
PATH = "/Game/Hermes/ComboIter2/Montages/AM_Hermes_finisher_02"
PROF = "/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes"

m = EAL.load_asset(PATH)
prof = EAL.load_asset(PROF)
step = list(prof.get_editor_property("heavy_finishers"))[1]

print("[D] montage %s | panjang %.3f s | rate aset %.2f" % (
    m.get_name(), m.get_play_length(), m.get_editor_property("rate_scale")))
print("[D] profil: play_rate %.2f | damage %.1f | move_dist %.1f | stop_at_target %s | stamina %.1f" % (
    step.get_editor_property("play_rate"), step.get_editor_property("damage"),
    step.get_editor_property("move_distance"), step.get_editor_property("b_stop_at_target"),
    step.get_editor_property("stamina_cost")))

for ev in AL.get_animation_notify_events(m):
    nama = ""
    n = ev.get_editor_property("notify")
    nsc = ev.get_editor_property("notify_state_class")
    cls = n.get_class().get_name() if n else (nsc.get_class().get_name() if nsc else "?")
    t = AL.get_anim_notify_event_trigger_time(ev)
    d = AL.get_anim_notify_event_duration(ev)
    extra = ""
    obj = n or nsc
    if obj:
        try:
            extra = "socket=%s new_hit=%s" % (obj.get_editor_property("socket_name"),
                                              obj.get_editor_property("new_hit"))
        except Exception:
            pass
    print("[D] %-34s %-8s t=%.3f d=%.3f (nyata %.3f-%.3f) %s" % (
        cls, str(ev.get_editor_property("notify_name")), t, d, t / 1.25, (t + d) / 1.25, extra))
