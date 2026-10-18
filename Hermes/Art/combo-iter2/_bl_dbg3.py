
import bpy, os
SRC = r"C:\repository\unreal_engine\jayadwara_hermes_combo\Hermes\Art\combo-iter2\Mixamo"
OUT = os.path.join(SRC, "inplace")
def head_z(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    hb = None
    for b in arm.pose.bones:
        if b.name.lower().endswith("head"):
            hb = b; break
    bpy.context.scene.frame_set(1)
    p = (arm.matrix_world @ hb.matrix).translation
    print(f"   {os.path.basename(path)}: head dunia z={p.z:.3f} y={p.y:.3f} | arm scale {tuple(round(v,3) for v in arm.matrix_world.to_scale())}")

print("ASLI:"); head_z(os.path.join(SRC, "air.fbx"))
print("HASIL EKSPOR:"); head_z(os.path.join(OUT, "air.fbx"))
