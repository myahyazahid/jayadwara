
import unreal
EAL = unreal.EditorAssetLibrary
for nm in ("air", "air_slam", "light_04", "light_01"):
    seq = EAL.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{nm}")
    model = seq.data_model_interface
    print("==", nm)
    for bone in ("root", "pelvis"):
        it = model.get_bone_track_by_name(bone).get_editor_property("internal_track_data")
        pos = it.get_positional_keys()
        if not pos:
            print("   ", bone, "tanpa pos keys")
            continue
        xs=[k.x for k in pos]; ys=[k.y for k in pos]; zs=[k.z for k in pos]
        print(f"   {bone:7s} n={len(pos):4d} X {min(xs):7.1f}..{max(xs):7.1f} | Y {min(ys):7.1f}..{max(ys):7.1f} | Z {min(zs):7.1f}..{max(zs):7.1f}")
