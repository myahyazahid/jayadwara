
import bpy, os
SRC = r"C:\repository\unreal_engine\jayadwara_hermes_combo\Hermes\Art\combo-iter2\Mixamo\air.fbx"
OUT = r"C:\repository\unreal_engine\jayadwara_hermes_combo\Hermes\Art\combo-iter2\Mixamo\_uji"
os.makedirs(OUT, exist_ok=True)

varian = [
    ("a", False, "FBX_SCALE_NONE"),
    ("b", False, "FBX_SCALE_ALL"),
    ("c", True,  "FBX_SCALE_ALL"),
]
for tag, auto, skala in varian:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=SRC, automatic_bone_orientation=auto)
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    f = os.path.join(OUT, f"air_{tag}.fbx")
    bpy.ops.export_scene.fbx(filepath=f, use_selection=True, bake_anim=True,
                             bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False,
                             bake_anim_force_startend_keying=True, add_leaf_bones=False,
                             apply_scale_options=skala, axis_forward="-Z", axis_up="Y")
    print("[uji]", tag, "auto_orient=", auto, "skala=", skala, "->", os.path.getsize(f), "byte")
