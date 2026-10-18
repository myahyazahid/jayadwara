
import unreal
EAL = unreal.EditorAssetLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01")
o = unreal.AnimPoseEvaluationOptions()
L = unreal.AnimationLibrary.get_sequence_length(seq)
for bone in ("root","pelvis"):
    xs=[]; ys=[]; zs=[]
    for i in range(0, 21):
        t = min(L*i/20.0, L)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        v = unreal.AnimPoseExtensions.get_bone_pose(p, bone, unreal.AnimPoseSpaces.LOCAL).translation
        xs.append(v.x); ys.append(v.y); zs.append(v.z)
    print(f"{bone} LOCAL X {min(xs):7.2f}..{max(xs):7.2f} Y {min(ys):7.2f}..{max(ys):7.2f} Z {min(zs):7.2f}..{max(zs):7.2f}")
p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, 0.0, o)
rr = unreal.AnimPoseExtensions.get_bone_pose(p, "root", unreal.AnimPoseSpaces.WORLD)
print("root world rot", rr.rotation)
tmp = "/Game/Hermes/ComboIter2/_uji/A_uji_keys"
EAL.delete_asset(tmp)
dup = EAL.duplicate_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01", tmp)
ctrl = unreal.new_object(unreal.AnimSequencerController, dup)
mi = ctrl.get_model_interface()
print("model interface dari controller:", mi, mi.get_class().get_name() if mi else None)
