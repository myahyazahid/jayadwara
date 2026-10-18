
import unreal, os
LOG = r"C:\repository\unreal_engine\jayadwara_hermes_combo\Hermes\Art\combo-iter2\Log\_uji_keys.txt"
def w(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")
open(LOG, "w", encoding="utf-8").close()

EAL = unreal.EditorAssetLibrary
tmp = "/Game/Hermes/ComboIter2/_uji/A_uji_keys_v2"
dup = EAL.duplicate_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_01", tmp)
model = dup.get_editor_property("data_model_interface")
w(f"model {model.get_class().get_name()} frames {model.get_number_of_frames()}")

ctrl = unreal.new_object(unreal.AnimSequencerController, dup)
w("ctrl dibuat")
try:
    ctrl.set_model(model)
    w("set_model OK")
except Exception as e:
    w("set_model GAGAL: " + str(e))
w("model interface sekarang: " + str(ctrl.get_model_interface()))

o = unreal.AnimPoseEvaluationOptions()
L = unreal.AnimationLibrary.get_sequence_length(dup)
n = model.get_number_of_frames()
pos = []; rot = []; scl = []
for i in range(n):
    t = min(L * i / float(n - 1), L)
    p = unreal.AnimPoseExtensions.get_anim_pose_at_time(dup, t, o)
    tr = unreal.AnimPoseExtensions.get_bone_pose(p, "root", unreal.AnimPoseSpaces.LOCAL)
    pos.append(tr.translation); rot.append(tr.rotation); scl.append(tr.scale3d)
w(f"disampel {len(pos)} kunci; Y awal {pos[0].y:.2f} max {max(k.y for k in pos):.2f}")
y0 = pos[0].y
baru = [unreal.Vector(k.x, y0, k.z) for k in pos]
try:
    ok = ctrl.set_bone_track_keys("root", baru, rot, scl)
    w("set_bone_track_keys -> " + str(ok))
except Exception as e:
    w("set_bone_track_keys GAGAL: " + str(e))
EAL.save_loaded_asset(dup, only_if_is_dirty=False)
w("disimpan")
ys=[]; hy=[]
for i in range(0, 13):
    t = min(L*i/12.0, L)
    p = unreal.AnimPoseExtensions.get_anim_pose_at_time(dup, t, o)
    ys.append(unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).translation.y)
    hy.append(unreal.AnimPoseExtensions.get_bone_pose(p, "head", unreal.AnimPoseSpaces.WORLD).translation.z)
w(f"HASIL pelvis world Y {min(ys):.1f}..{max(ys):.1f} | kepala Z {min(hy):.1f}..{max(hy):.1f}")
print(open(LOG, encoding="utf-8").read())
