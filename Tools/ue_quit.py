import unreal

try:
    unreal.SystemLibrary.quit_editor()
    print("[QUIT] editor diminta keluar")
except Exception as e:
    print("[QUIT] gagal: %s" % e)
