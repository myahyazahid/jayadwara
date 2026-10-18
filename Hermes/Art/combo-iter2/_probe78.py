
import unreal
w = unreal.EditorLevelLibrary.get_editor_world()
print("map:", w.get_name(), "|", w.get_outer().get_name() if w.get_outer() else None)
bp = unreal.load_asset("/Game/Hermes/ComboIter2/BP_Aksa_Hermes")
cdo = unreal.get_default_object(bp.generated_class())
mc = cdo.get_editor_property("mesh")
print("mesh:", mc.get_skeletal_mesh_asset().get_name(), "| anim class:", mc.get_anim_instance_class().get_name() if mc.get_anim_instance_class() else None)
print("rel loc:", mc.get_editor_property("relative_location"))
