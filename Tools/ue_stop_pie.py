import unreal

try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.editor_request_end_play()
    print("[PIE] permintaan berhenti dikirim")
except Exception as e:
    print("[PIE] gagal: %s" % e)
