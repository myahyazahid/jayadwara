
import bpy
path = r"C:\repository\unreal_engine\jayadwara_hermes_combo\Hermes\Art\combo-iter2\Mixamo\air.fbx"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=path)

def fcurves_of(ob):
    ad = ob.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "layers") and len(act.layers):
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for cb in getattr(strip, "channelbags", []):
                    out.extend(cb.fcurves)
        return out
    return list(getattr(act, "fcurves", []))

for ob in bpy.data.objects:
    print("OBJ", ob.name, ob.type)
    fcs = fcurves_of(ob)
    print("   n_fcurves", len(fcs))
    seen = {}
    for fc in fcs:
        seen.setdefault(fc.data_path, [0, 0])
        seen[fc.data_path][fc.array_index] = 1
    for p, idx in list(seen.items()):
        if "location" in p or p.endswith("location"):
            print("   LOC-FC", p, idx)

arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
print("ARM bones", len(arm.data.bones))
for b in arm.data.bones:
    if "root" in b.name.lower() or "hip" in b.name.lower():
        print("BONE", b.name, "parent", b.parent.name if b.parent else None)
