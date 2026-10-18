
import unreal
o = unreal.AnimPoseEvaluationOptions()
BONES = ["head","pelvis","hand_l","hand_r","foot_l","foot_r","lowerarm_l","lowerarm_r","upperarm_l","upperarm_r"]
def pose(peran, t):
    seq = unreal.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{peran}")
    L = unreal.AnimationLibrary.get_sequence_length(seq)
    p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, min(max(t,0.0),L), o)
    return {b: unreal.AnimPoseExtensions.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation for b in BONES}, L
def jarak(a, b):
    return sum((a[k]-b[k]).length() for k in BONES)/len(BONES)
for A, B in (("light_02","light_03"), ("light_03","light_04")):
    pa, La = pose(A, 0.0)
    _, La = pose(A, 0.0)
    pB, Lb = pose(B, 0.0)
    # ujung A: geser potongan ekor A
    print(f"--- {A} -> {B} | {A} panjang {La:.2f} {B} panjang {Lb:.2f}")
    for d in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        pa_end, _ = pose(A, La - d)
        print(f"   potong ekor {A} {d:.1f}s lebih awal (jadi {La-d:.2f}s): selisih {jarak(pa_end, pB):5.1f} cm")
    pa_end2, _ = pose(A, La)
    for s in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        pBs, _ = pose(B, s)
        print(f"   mulai {B} {s:.1f}s lebih lambat (jadi {Lb-s:.2f}s): selisih {jarak(pa_end2, pBs):5.1f} cm")
