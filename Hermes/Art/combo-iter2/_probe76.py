
import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
print("level sekarang:", les.get_current_level().get_name() if les.get_current_level() else None)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    cls = a.get_class().get_name()
    if "Aksa" in cls or "Dummy" in cls or "PlayerStart" in cls:
        try: ap = a.get_editor_property("auto_possess_player")
        except Exception: ap = "-"
        print(f"  {cls:28s} {a.get_actor_label():24s} loc={a.get_actor_location()} possess={ap}")
