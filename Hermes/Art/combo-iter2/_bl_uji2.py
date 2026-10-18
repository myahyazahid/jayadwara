
import bpy
props = [p.identifier for p in bpy.ops.import_scene.fbx.get_rna_type().properties]
print("[props-import]", [p for p in props if "bone" in p or "axis" in p or "scale" in p])
eprops = [p.identifier for p in bpy.ops.export_scene.fbx.get_rna_type().properties]
print("[props-export]", [p for p in eprops if "bone" in p or "axis" in p or "scale" in p or "apply" in p])
