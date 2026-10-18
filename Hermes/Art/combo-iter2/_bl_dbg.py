
import bpy, mathutils, os
SRC = r"C:\repository\unreal_engine\jayadwara_hermes_combo\Hermes\Art\combo-iter2\Mixamo"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(SRC, "air.fbx"))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
hips = arm.pose.bones["mixamorig:Hips"]
print("parent hips:", hips.parent.name if hips.parent else None, "| bones:", len(arm.data.bones))

def fcs(ob):
    ad = ob.animation_data; act = ad.action
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in getattr(strip, "channelbags", []):
                out.extend(cb.fcurves)
    return out

allfc = fcs(arm)
print("fcurves", len(allfc), "contoh", allfc[0].data_path)
fr = [f.range() for f in allfc]
f0, f1 = int(min(r[0] for r in fr)), int(max(r[1] for r in fr))
print("rentang", f0, f1)
scene = bpy.context.scene
pos0 = None
for f in (f0, (f0+f1)//2, f1):
    scene.frame_set(f)
    p = (arm.matrix_world @ hips.matrix).translation
    print(f, "dunia", tuple(round(v,3) for v in p), "lokal", tuple(round(v,3) for v in hips.location))
scene.frame_set(f0)
p0 = (arm.matrix_world @ hips.matrix).translation.copy()
R_inv = hips.bone.matrix_local.to_3x3().inverted()
for f in range(f0, f1+1):
    scene.frame_set(f)
    p = (arm.matrix_world @ hips.matrix).translation
    d = mathutils.Vector((p.x - p0.x, p.y - p0.y, 0.0))
    hips.location = hips.location - (R_inv @ d)
    hips.keyframe_insert("location", frame=f)
for f in (f0, (f0+f1)//2, f1):
    scene.frame_set(f)
    p = (arm.matrix_world @ hips.matrix).translation
    print("sesudah", f, "dunia", tuple(round(v,3) for v in p))
