
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
src = "/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air"
tmp = "/Game/Hermes/ComboIter2/_TMP_air_test"
EAL.delete_asset(tmp)
dup = EAL.duplicate_asset(src, tmp)
print("dup:", dup.get_name())

opts = unreal.AnimPoseEvaluationOptions()
def ukur(seq, bone="root"):
    L = AL.get_sequence_length(seq)
    xs=[];ys=[];zs=[]; rots=[]
    for i in range(0, 21):
        t = min(L * i / 20.0, L)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
        tr = unreal.AnimPoseExtensions.get_bone_pose(pose, bone, unreal.AnimPoseSpaces.LOCAL)
        xs.append(tr.translation.x); ys.append(tr.translation.y); zs.append(tr.translation.z)
        rots.append(tr.rotation)
    dot = min(abs(rots[0].x*r.x+rots[0].y*r.y+rots[0].z*r.z+rots[0].w*r.w) for r in rots)
    print(f"  {bone}: X {min(xs):7.2f}..{max(xs):7.2f} Y {min(ys):7.2f}..{max(ys):7.2f} Z {min(zs):7.2f}..{max(zs):7.2f} | rot min|dot| {dot:.4f}")

print("sebelum:"); ukur(dup)
print("hapus track root ->", AL.remove_bone_animation(dup, "root"))
EAL.save_loaded_asset(dup, only_if_is_dirty=False)
print("sesudah:"); ukur(dup)
