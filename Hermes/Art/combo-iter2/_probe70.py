
import unreal
p = unreal.load_asset("/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes")
print("sebelum: hang_time", p.get_editor_property("air_hang_time"), "gravity", p.get_editor_property("air_hang_gravity_scale"))
p.set_editor_property("air_hang_time", 0.10)
p.set_editor_property("air_hang_gravity_scale", 0.6)
unreal.EditorAssetLibrary.save_loaded_asset(p, only_if_is_dirty=False)
print("sesudah: hang_time", p.get_editor_property("air_hang_time"), "gravity", p.get_editor_property("air_hang_gravity_scale"))
