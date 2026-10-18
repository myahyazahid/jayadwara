
import unreal
bp = unreal.load_asset("/Game/Hermes/ComboIter2/BP_Aksa2_Hermes")
cdo = unreal.get_default_object(bp.generated_class())
mc = cdo.get_editor_property("mesh")
print("slot komponen:", mc.get_num_materials())
for i in range(mc.get_num_materials()):
    m = mc.get_material(i)
    print("   ", i, m.get_name() if m else None)
sk = unreal.load_asset("/Game/Jayadwara/Characters/Aksa2/Mesh/SK_Aksa2")
print("material mesh v2:")
for i, m in enumerate(sk.get_editor_property("materials")):
    print("   ", i, m.get_editor_property("material_interface").get_name() if m.get_editor_property("material_interface") else None,
          "| slot:", m.get_editor_property("material_slot_name"))
