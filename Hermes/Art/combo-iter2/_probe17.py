
import unreal
EAL = unreal.EditorAssetLibrary
for nm in ("air", "air_slam", "light_04", "light_01"):
    seq = EAL.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{nm}")
    model = seq.data_model_interface
    print("==", nm, "frames", model.get_number_of_frames())
    for bone in ("root", "pelvis"):
        t = model.get_bone_track_by_name(bone)
        it = t.get_editor_property("internal_track_data")
        pos = it.get_editor_property("pos_keys")
        if not pos:
            print("  ", bone, "tanpa pos_keys")
            continue
        xs=[k.x for k in pos]; ys=[k.y for k in pos]; zs=[k.z for k in pos]
        print(f"   {bone:7s} n={len(pos):3d} X {min(xs):7.1f}..{max(xs):7.1f} | Y {min(ys):7.1f}..{max(ys):7.1f} | Z {min(zs):7.1f}..{max(zs):7.1f}")
