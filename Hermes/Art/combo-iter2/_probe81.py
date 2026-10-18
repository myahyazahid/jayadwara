
import unreal
abp = unreal.load_asset("/Game/Jayadwara/Characters/Aksa/Anims/ABP_Aksa")
print("ABP target skeleton:", abp.get_editor_property("target_skeleton").get_path_name() if abp.get_editor_property("target_skeleton") else None)
for p in ("/Game/Jayadwara/Characters/Aksa/Mesh/SKEL_Aksa", "/Game/Jayadwara/Characters/Aksa2/Mesh/SKEL_Aksa2"):
    try:
        sk = unreal.load_asset(p)
        print(sk.get_name(), "kompatibel:", [c.get_name() for c in sk.get_editor_property("compatible_skeletons")])
    except Exception as e:
        print(p, "err", str(e)[:80])
