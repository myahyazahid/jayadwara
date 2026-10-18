
import unreal
p = unreal.load_asset("/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes")
for n in ("air_slam_speed","air_slam_recovery","air_hang_time","air_hang_gravity_scale","air_slam_gravity_scale"):
    try: print(n, "=", p.get_editor_property(n))
    except Exception as e: print(n, "err", str(e)[:60])
