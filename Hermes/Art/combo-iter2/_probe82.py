
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
bp2 = unreal.load_asset("/Game/Hermes/ComboIter2/BP_Aksa2_Hermes")
cls2 = bp2.generated_class()
lama = None
for a in eas.get_all_level_actors():
    if a.get_class().get_name() == "BP_Aksa_Hermes_C":
        lama = a; break
if not lama:
    print("pawn lama tidak ditemukan"); raise SystemExit
loc = lama.get_actor_location(); rot = lama.get_actor_rotation()
print("lama:", lama.get_actor_label(), loc)
baru = eas.spawn_actor_from_class(cls2, loc, rot)
baru.set_actor_label("BP_Aksa2_Hermes")
baru.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
print("baru:", baru.get_actor_label(), baru.get_class().get_name(), baru.get_actor_location(),
      "| mesh:", baru.get_editor_property("mesh").get_skeletal_mesh_asset().get_name())
eas.destroy_actor(lama)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
print("level disimpan")
for a in eas.get_all_level_actors():
    if "Aksa" in a.get_class().get_name():
        print("  sisa:", a.get_actor_label(), a.get_class().get_name())
