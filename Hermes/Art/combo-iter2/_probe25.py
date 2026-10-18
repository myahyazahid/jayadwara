
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air")
model = seq.data_model_interface
ctrl = unreal.AnimDataController()
print("set_model ada:", hasattr(ctrl, "set_model"))
try:
    ctrl.set_model(model)
    print("set_model OK")
except Exception as e:
    print("set_model GAGAL:", e)

opts = unreal.AnimPoseEvaluationOptions()
L = AL.get_sequence_length(seq)
dt = 1.0 / 60.0
n = int(L / dt) + 1
pos, rot, scl = [], [], []
for i in range(n):
    t = min(i * dt, L)
    pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
    tr = unreal.AnimPoseExtensions.get_bone_pose(pose, "root", unreal.AnimPoseSpaces.LOCAL)
    pos.append(tr.translation); rot.append(tr.rotation); scl.append(tr.scale3d)
p0 = pos[0]
print("n keys", n, "p0", p0)
pos2 = [unreal.Vector(p0.x, p0.y, p0.z) for _ in range(n)]
ctrl.open_bracket(seq, "in-place")
ok = ctrl.set_bone_track_keys("root", pos2, rot, scl, True)
ctrl.close_bracket(seq)
print("set_bone_track_keys ->", ok)
EAL.save_loaded_asset(seq, only_if_is_dirty=False)

# verifikasi
xs=[];ys=[];zs=[]
for i in range(0, 21):
    t = min(L * i / 20.0, L)
    pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
    p = unreal.AnimPoseExtensions.get_bone_pose(pose, "root", unreal.AnimPoseSpaces.LOCAL).translation
    xs.append(p.x); ys.append(p.y); zs.append(p.z)
print(f"root sesudah: X {min(xs):.2f}..{max(xs):.2f} Y {min(ys):.2f}..{max(ys):.2f} Z {min(zs):.2f}..{max(zs):.2f}")
