
import unreal
p = unreal.load_asset("/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes")
for i, s in enumerate(p.get_editor_property("light_combo")):
    m = s.get_editor_property("montage")
    L = m.get_editor_property("sequence_length"); r = s.get_editor_property("play_rate")
    bi = m.get_editor_property("blend_in").get_editor_property("blend_time")
    print(f"light[{i}] {m.get_name():20s} {L:.2f}s @{r:.2f}x = {L/r:.2f}s nyata | blend_in {bi:.2f} | maju {s.get_editor_property('move_distance'):.0f}cm")
