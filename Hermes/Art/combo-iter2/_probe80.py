
import unreal
EAL = unreal.EditorAssetLibrary
DST = "/Game/Hermes/ComboIter2/BP_Aksa2_Hermes"
if EAL.does_asset_exist(DST):
    EAL.delete_asset(DST)
bp = EAL.duplicate_asset("/Game/Hermes/ComboIter2/BP_Aksa_Hermes", DST)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo = unreal.get_default_object(bp.generated_class())
mc = cdo.get_editor_property("mesh")
print("sebelum:", mc.get_skeletal_mesh_asset().get_name())
sk2 = unreal.load_asset("/Game/Jayadwara/Characters/Aksa2/Mesh/SK_Aksa2")
ok = mc.set_skeletal_mesh_asset(sk2)
print("set_skeletal_mesh_asset ->", ok, "| sekarang:", mc.get_skeletal_mesh_asset().get_name())
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_loaded_asset(bp, only_if_is_dirty=False)
# verifikasi dari objek yang dimuat ulang
bp2 = unreal.load_asset(DST)
cdo2 = unreal.get_default_object(bp2.generated_class())
print("setelah simpan:", cdo2.get_editor_property("mesh").get_skeletal_mesh_asset().get_name())
sk = unreal.load_asset("/Game/Jayadwara/Characters/Aksa2/Mesh/SK_Aksa2")
for nm, m in (("Aksa v1", unreal.load_asset("/Game/Jayadwara/Characters/Aksa/Mesh/SK_Aksa")), ("Aksa2", sk)):
    try:
        b = m.get_bounds(); print(f"  {nm}: extent Z {b.box_extent.z:.1f} origin Z {b.origin.z:.1f}")
    except Exception as e: print("  bounds err", nm, str(e)[:60])
