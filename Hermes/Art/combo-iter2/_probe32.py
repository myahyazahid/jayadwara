
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
opts = unreal.AnimPoseEvaluationOptions()
for nm in ("air", "air_slam", "light_04", "light_01"):
    seq = EAL.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{nm}")
    L = AL.get_sequence_length(seq)
    xs=[];ys=[];zs=[]
    for i in range(0, 21):
        t = min(L * i / 20.0, L)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
        p = unreal.AnimPoseExtensions.get_bone_pose(pose, "root", unreal.AnimPoseSpaces.LOCAL).translation
        xs.append(p.x); ys.append(p.y); zs.append(p.z)
    print(f"{nm:9s} len {L:.2f}s root X {min(xs):7.1f}..{max(xs):7.1f} | Y {min(ys):7.1f}..{max(ys):7.1f} | Z {min(zs):7.1f}..{max(zs):7.1f}")
