
import unreal
EAL = unreal.EditorAssetLibrary
SRC = "/Game/Hermes/ComboIter2/BP_Aksa_Hermes"
DST = "/Game/Hermes/ComboIter2/BP_Aksa2_Hermes"
if EAL.does_asset_exist(DST):
    EAL.delete_asset(DST)
bp = EAL.duplicate_asset(SRC, DST)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo = unreal.get_default_object(bp.generated_class())
mc = cdo.get_editor_property("mesh")
print("sebelum mesh:", mc.get_skeletal_mesh_asset().get_name(), "| anim:", mc.get_editor_property("anim_class").get_name() if mc.get_editor_property("anim_class") else None)
sk = unreal.load_asset("/Game/Jayadwara/Characters/Aksa2/Mesh/SK_Aksa2")
mc.set_skeletal_mesh_asset(sk)
cdo.set_editor_property("mesh", mc)
EAL.save_loaded_asset(bp, only_if_is_dirty=False)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo = unreal.get_default_object(bp.generated_class())
mc = cdo.get_editor_property("mesh")
print("sesudah mesh:", mc.get_skeletal_mesh_asset().get_name(), "| anim:", mc.get_editor_property("anim_class").get_name() if mc.get_editor_property("anim_class") else None)
for nm, m in (("Manny", unreal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")), ("Aksa2", sk)):
    try:
        b = m.get_bounds()
        print(f"  {nm}: extent Z {b.box_extent.z:.1f} origin Z {b.origin.z:.1f}")
    except Exception as e:
        print("  bounds err", str(e)[:80])
