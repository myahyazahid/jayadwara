
import unreal
print("map:", unreal.SystemLibrary.get_world_name(unreal.EditorLevelLibrary.get_editor_world()))
bp = unreal.load_asset("/Game/Hermes/ComboIter2/BP_Aksa_Hermes")
cdo = unreal.get_default_object(bp.generated_class())
mc = cdo.get_editor_property("mesh")
print("mesh:", mc.get_skeletal_mesh_asset().get_name(), "| anim class:", mc.get_anim_instance_class().get_name() if mc.get_anim_instance_class() else None)
print("rel loc:", mc.get_editor_property("relative_location"), "| rel rot:", mc.get_editor_property("relative_rotation"))
sk = unreal.load_asset("/Game/Jayadwara/Characters/Aksa2/Mesh/SK_Aksa2")
print("SK_Aksa2 bounds:", sk.get_bounds().box_extent if hasattr(sk,"get_bounds") else "?")
