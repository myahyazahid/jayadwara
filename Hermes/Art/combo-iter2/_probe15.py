
import unreal
EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
model = seq.data_model_interface
print("model methods:", [x for x in dir(model) if "bone" in x.lower() or "frame" in x.lower()][:25])
names = model.get_bone_track_names()
print("n tracks", len(names), names[:6])
for bone in ("root", "pelvis"):
    if bone in names:
        keys = model.get_bone_track_keys(bone)
        print(bone, "tipe", type(keys), "len", len(keys))
        pos = keys[0] if isinstance(keys, tuple) else None
        if pos:
            xs = [k.x for k in pos]; ys = [k.y for k in pos]; zs = [k.z for k in pos]
            print("   X", round(min(xs),1), round(max(xs),1), "| Y", round(min(ys),1), round(max(ys),1),
                  "| Z", round(min(zs),1), round(max(zs),1), "| n", len(pos))
