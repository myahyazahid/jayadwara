import unreal

EAL = unreal.EditorAssetLibrary
for folder in ("/Game/Jayadwara/Anims/Mixamo/Raw", "/Game/Jayadwara/Anims/Mixamo"):
    print("[L] %s -> %s" % (folder, EAL.list_assets(folder, True, False)))
