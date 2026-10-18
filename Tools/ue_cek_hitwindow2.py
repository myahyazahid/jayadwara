import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
PATH = "/Game/Hermes/ComboIter2/Montages/AM_Hermes_finisher_02"
PROF = "/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes"

def g(obj, *names):
    for n in names:
        try:
            return obj.get_editor_property(n)
        except Exception:
            continue
    return "?"

m = EAL.load_asset(PATH)
prof = EAL.load_asset(PROF)
step = list(prof.get_editor_property("heavy_finishers"))[1]

print("[D] montage %s | panjang %.3f s" % (m.get_name(), m.get_play_length()))
print("[D] profil finisher_02: play_rate %s | damage %s | move_dist %s | stamina %s" % (
    g(step, "play_rate"), g(step, "damage"), g(step, "move_distance"), g(step, "stamina_cost")))

for ev in AL.get_animation_notify_events(m):
    n = ev.get_editor_property("notify")
    nsc = ev.get_editor_property("notify_state_class")
    cls = n.get_class().get_name() if n else (nsc.get_class().get_name() if nsc else "?")
    t = AL.get_anim_notify_event_trigger_time(ev)
    d = AL.get_anim_notify_event_duration(ev)
    obj = n or nsc
    print("[D] %-32s t=%.3f d=%.3f (nyata %.3f-%.3f) socket=%s new_hit=%s" % (
        cls, t, d, t / 1.25, (t + d) / 1.25, g(obj, "socket_name"), g(obj, "new_hit")))
