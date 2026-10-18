
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
opts = unreal.AnimPoseEvaluationOptions()
world = unreal.AnimPoseSpaces.WORLD
for nm in ("air", "air_slam", "light_04", "light_01"):
    seq = EAL.load_asset(f"/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_{nm}")
    L = AL.get_sequence_length(seq)
    xs = []; ys = []; zs = []
    for i in range(0, 41):
        t = min(L * i / 40.0, L)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
        p = unreal.AnimPoseExtensions.get_bone_pose(pose, "pelvis", world).translation
        xs.append(p.x); ys.append(p.y); zs.append(p.z)
    print(f"{nm:9s} X {min(xs):8.1f}..{max(xs):8.1f} | Y {min(ys):8.1f}..{max(ys):8.1f} | Z {min(zs):8.1f}..{max(zs):8.1f}")
