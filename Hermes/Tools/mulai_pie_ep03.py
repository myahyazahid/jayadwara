import unreal
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
unreal.log(f"[TP] subsystem={sub}")
for n in ("editor_request_begin_play", "editor_play_simulate", "editor_request_end_play"):
    unreal.log(f"[TP] has {n}: {hasattr(sub, n)}")
if hasattr(sub, "editor_request_begin_play"):
    sub.editor_request_begin_play()
    unreal.log("[TP] begin_play dipanggil")
else:
    unreal.log_error("[TP] editor_request_begin_play tidak ada")
