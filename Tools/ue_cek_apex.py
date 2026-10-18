import unreal

EAL = unreal.EditorAssetLibrary
PROF = "/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes"
p = EAL.load_asset(PROF)
s = p.get_editor_property("air_slam")
m = s.get_editor_property("montage")

def g(obj, *names):
    for n in names:
        try:
            return obj.get_editor_property(n)
        except Exception:
            continue
    return "?"

print("[X] montage air_slam: %s | %.3f s" % (m.get_name() if m else "-", m.get_play_length() if m else 0.0))
print("[X] air_slam speed=%s recovery=%s radius=%s" % (
    g(s, "speed", "air_slam_speed"), g(s, "recovery"), g(s, "radius")))
print("[X] apex velocity (cm/s) = %s | air_combo_max = %s" % (
    g(p, "air_slam_apex_velocity"), g(p, "air_combo_max")))
