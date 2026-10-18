
import unreal
p = unreal.load_asset("/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes")
for i, s in enumerate(p.get_editor_property("light_combo")):
    m = s.get_editor_property("montage")
    print(f"light[{i}] {m.get_name():22s} panjang {m.get_editor_property('sequence_length'):.2f} | rate {s.get_editor_property('play_rate'):.2f} | maju {s.get_editor_property('move_distance'):.0f} cm / {s.get_editor_property('move_duration'):.2f} s | tinggi {s.get_editor_property('move_height'):.0f} | stop {s.get_editor_property('stop_at_target')}")
print("air_hang_time", round(p.get_editor_property("air_hang_time"),2), "| air_slam_speed", p.get_editor_property("air_slam_speed"))
