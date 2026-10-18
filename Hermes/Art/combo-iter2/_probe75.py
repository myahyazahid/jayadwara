
import unreal
for path in ("/Game/Jayadwara/Characters/Aksa2/Mesh/SKEL_Aksa2", "/Game/Characters/Mannequins/Meshes/SK_Mannequin"):
    sk = unreal.load_asset(path)
    bt = sk.get_editor_property("bone_tree")
    print("==", sk.get_name(), "tulang:", len(bt))
    for i in (0, 1, 2):
        try:
            t = bt[i].to_tuple()
            print("   ", [x for x in t if isinstance(x, str)][:3])
        except Exception as e:
            print("   err", str(e)[:80])
    print("   compatible:", [c.get_name() if hasattr(c, "get_name") else c for c in sk.get_editor_property("compatible_skeletons")])
