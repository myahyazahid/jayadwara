
import unreal
p = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes")
for k in ("air_slam_speed", "air_slam_radius", "air_slam_recovery"):
    print("sebelum", k, p.get_editor_property(k))
p.set_editor_property("air_slam_speed", 500.0)
p.set_editor_property("air_slam_recovery", 0.45)
step = p.get_editor_property("air_slam")
print("step montage", step.get_editor_property("montage").get_name(), "rate", step.get_editor_property("play_rate"))
step.set_editor_property("play_rate", 1.0)
p.set_editor_property("air_slam", step)
unreal.EditorAssetLibrary.save_loaded_asset(p, only_if_is_dirty=False)
for k in ("air_slam_speed", "air_slam_recovery"):
    print("sesudah", k, p.get_editor_property(k))
