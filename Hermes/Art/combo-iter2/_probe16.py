
import unreal
EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
model = seq.data_model_interface
t = model.get_bone_track_by_name("pelvis")
print("track:", type(t), [x for x in dir(t) if not x.startswith("_")][:30])
try:
    it = t.get_editor_property("internal_track")
    print("internal:", [x for x in dir(it) if not x.startswith("_")][:20])
    pos = it.get_editor_property("pos_keys")
    print("pos n", len(pos), pos[0])
    xs=[k.x for k in pos]; ys=[k.y for k in pos]; zs=[k.z for k in pos]
    print("X", round(min(xs),1), round(max(xs),1), "| Y", round(min(ys),1), round(max(ys),1), "| Z", round(min(zs),1), round(max(zs),1))
except Exception as e:
    print("GAGAL:", e)
