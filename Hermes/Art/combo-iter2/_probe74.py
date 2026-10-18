
import unreal
sk = unreal.load_asset("/Game/Jayadwara/Characters/Aksa2/Mesh/SKEL_Aksa2")
print("props:", [x for x in dir(sk) if "bone" in x.lower() or "compat" in x.lower() or "retarget" in x.lower()])
bt = None
for nm in ("bone_tree", "reference_skeleton"):
    try:
        bt = sk.get_editor_property(nm); print(nm, "->", bt); break
    except Exception as e:
        print(nm, "err", str(e)[:60])
if bt:
    print("bt props:", [x for x in dir(bt) if not x.startswith("_")][:20])
    try:
        info = bt.get_editor_property("final_ref_bone_info")
        print("tulang:", len(info), [str(i.get_editor_property("name")) for i in info[:10]])
    except Exception as e:
        print("info err", str(e)[:100])
