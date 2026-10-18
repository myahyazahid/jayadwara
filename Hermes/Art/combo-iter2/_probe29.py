
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
tmp = "/Game/Hermes/ComboIter2/_TMP_air_test"
EAL.delete_asset(tmp)
dup = EAL.duplicate_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air", tmp)
opts = unreal.AnimPoseEvaluationOptions()

def ukur(seq, label):
    L = AL.get_sequence_length(seq)
    rx=[];ry=[];rz=[]; px=[];py=[];pz=[]; prot=[]
    for i in range(0, 21):
        t = min(L * i / 20.0, L)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
        r = unreal.AnimPoseExtensions.get_bone_pose(pose, "root", unreal.AnimPoseSpaces.LOCAL)
        p = unreal.AnimPoseExtensions.get_bone_pose(pose, "pelvis", unreal.AnimPoseSpaces.WORLD)
        rx.append(r.translation.x); ry.append(r.translation.y); rz.append(r.translation.z)
        px.append(p.translation.x); py.append(p.translation.y); pz.append(p.translation.z)
        prot.append(p.rotation)
    dot = min(abs(prot[0].x*q.x+prot[0].y*q.y+prot[0].z*q.z+prot[0].w*q.w) for q in prot)
    print(f"{label}: root X {min(rx):6.1f}..{max(rx):6.1f} Y {min(ry):6.1f}..{max(ry):6.1f} Z {min(rz):6.1f}..{max(rz):6.1f}")
    print(f"          pelvis dunia X {min(px):6.1f}..{max(px):6.1f} Y {min(py):6.1f}..{max(py):6.1f} Z {min(pz):6.1f}..{max(pz):6.1f} | rot pelvis min|dot| {dot:.3f}")

ukur(dup, "sebelum")
dup.set_editor_property("enable_root_motion", True)
dup.set_editor_property("force_root_lock", True)
EAL.save_loaded_asset(dup, only_if_is_dirty=False)
ukur(dup, "force_root_lock")
print("props:", dup.get_editor_property("enable_root_motion"), dup.get_editor_property("force_root_lock"))
