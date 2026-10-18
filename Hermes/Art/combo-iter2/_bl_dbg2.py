
import bpy, mathutils, os
SRC = r"C:\repository\unreal_engine\jayadwara_hermes_combo\Hermes\Art\combo-iter2\Mixamo"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(SRC, "air.fbx"))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
hips = arm.pose.bones["mixamorig:Hips"]
print("arm scale", tuple(round(v,4) for v in arm.matrix_world.to_scale()))
print("bone matrix_local scale", tuple(round(v,4) for v in hips.bone.matrix_local.to_scale()))
scene = bpy.context.scene
f0, f1 = 1, 46
scene.frame_set(f0)
p0 = (arm.matrix_world @ hips.matrix).translation.copy()
M = (arm.matrix_world.to_3x3() @ hips.bone.matrix_local.to_3x3())
Minv = M.inverted()
for f in range(f0, f1+1):
    scene.frame_set(f)
    p = (arm.matrix_world @ hips.matrix).translation
    d = mathutils.Vector((p.x - p0.x, p.y - p0.y, p.z - p0.z))
    hips.location = hips.location - (Minv @ d)
    hips.keyframe_insert("location", frame=f)
for f in (f0, 23, f1):
    scene.frame_set(f)
    p = (arm.matrix_world @ hips.matrix).translation
    print("sesudah", f, "dunia", tuple(round(v,3) for v in p))
