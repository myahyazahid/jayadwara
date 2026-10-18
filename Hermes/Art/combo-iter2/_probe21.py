
import unreal
p = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes")
for prop in ("air_attack", "air_slam", "lunge_attack", "back_attack"):
    s = p.get_editor_property(prop)
    print("==", prop)
    for f in ("montage", "play_rate", "move_distance", "move_height", "move_duration", "stop_at_target",
              "stamina_cost", "damage", "hit_stop", "air_combo_max", "air_hang_time", "air_hang_gravity_scale", "air_slam_speed"):
        try:
            v = s.get_editor_property(f)
            print("   ", f, "=", v if not hasattr(v, "get_name") else v.get_name())
        except Exception:
            pass
for f in ("air_combo_max", "air_hang_time", "air_hang_gravity_scale", "air_slam_speed", "montage_play_rate"):
    try:
        print("profil", f, "=", p.get_editor_property(f))
    except Exception as e:
        print("profil", f, "tidak ada")
