
import bpy, sys
path = r"C:\repository\unreal_engine\jayadwara_hermes_combo\Hermes\Art\combo-iter2\Mixamo\air.fbx"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=path)
for ob in bpy.data.objects:
    print("OBJ", ob.name, ob.type, "loc", tuple(round(v,2) for v in ob.location))
    ad = ob.animation_data
    if ad and ad.action:
        paths = {}
        for fc in ad.action.fcurves:
            paths.setdefault(fc.data_path, 0)
            paths[fc.data_path] += 1
        for p, n in sorted(paths.items())[:14]:
            print("   FC", p, n)
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
print("ARM", arm.name, "bones", len(arm.data.bones))
for b in ("root", "mixamorig:Hips", "Hips", "mixamorig:Root"):
    if b in arm.data.bones:
        print("BONE", b, "parent", arm.data.bones[b].parent.name if arm.data.bones[b].parent else None)
