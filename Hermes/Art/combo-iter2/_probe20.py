
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
print("len", AL.get_sequence_length(seq))
for f in (0, 10, 20, 30, 40):
    try:
        p = AL.get_bone_pose_for_frame(seq, "pelvis", f, False)
        print(f, "pelvis", p.translation)
    except Exception as e:
        print(f, "GAGAL", str(e)[:100])
