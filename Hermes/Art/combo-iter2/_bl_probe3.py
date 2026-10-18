
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
    fcs = fcurves_of(ob)
    print("OBJ", ob.name, ob.type, "fcurves", len(fcs))
    seen = set()
    for fc in fcs:
        seen.add(fc.data_path)
    for p in sorted(seen)[:8]:
        print("   P", p)
    for p in sorted(seen):
        if p.endswith(".location"):
            print("   LOC", p)
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
print("ARM bones", len(arm.data.bones))
for b in arm.data.bones:
    if "root" in b.name.lower() or "hip" in b.name.lower():
        print("BONE", b.name, "parent", b.parent.name if b.parent else None)
