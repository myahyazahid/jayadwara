
import unreal
skel = unreal.load_asset("/Game/Jayadwara/Characters/Aksa2/Mesh/SKEL_Aksa2")
mesh = unreal.load_asset("/Game/Jayadwara/Characters/Aksa2/Mesh/SK_Aksa2")
bp   = unreal.load_asset("/Game/Jayadwara/Characters/Aksa2/BP_Aksa2")
manny_skel = unreal.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
print("skel:", skel.get_path_name() if skel else None)
print("sama dgn SK_Mannequin?", skel == manny_skel if (skel and manny_skel) else None)
if skel:
    try: print("jumlah tulang:", skel.get_editor_property("bone_tree").get_editor_property("num_bones") if hasattr(skel, "bone_tree") else "?")
    except Exception as e: print("bone err", str(e)[:80])
print("mesh:", mesh.get_path_name() if mesh else None, "| skeleton:", mesh.get_editor_property("skeleton").get_path_name() if mesh else None)
print("bp:", bp.get_path_name() if bp else None, "| parent:", bp.get_editor_property("parent_class").get_name() if bp else None)
try:
    cdo = unreal.get_default_object(bp.generated_class())
    mc = cdo.get_editor_property("mesh")
    print("mesh di BP:", mc.get_skeletal_mesh_asset().get_name() if mc and mc.get_skeletal_mesh_asset() else None,
          "| anim bp:", mc.get_anim_instance_class().get_name() if mc and mc.get_anim_instance_class() else None)
except Exception as e:
    print("cdo err", str(e)[:150])
