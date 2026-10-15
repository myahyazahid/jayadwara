"""
Hermes/Tools/aksa2_121_fix_hip_webbing.py
Perbaiki 9 verteks pinggul/paha (Z=0.78..0.80m) yang salah terikat ke upperarm_twist_02_l.
Kembalikan bobotnya 100% ke pelvis dan thigh_l sesuai verteks tetangganya.
Simpan ke aksa2_v20_perfect_anatomy.blend dan ekspor ke SK_Aksa2.fbx.
"""
import bpy
from pathlib import Path
from mathutils import Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v19_clean_arm_armpit.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v20_perfect_anatomy.blend"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

vg_map = {vg.name: vg for vg in mesh.vertex_groups}

# 9 verteks spesifik di pinggul kiri yang salah terikat ke lengan atas
stray_hip_verts = [113, 1365, 3302, 4729, 4864, 6287, 9911, 12457, 16900]

# Juga cek semua verteks lain di bawah Z < 0.90m yang memiliki bobot lengan
all_arm_groups = [
    'clavicle_l', 'upperarm_l', 'upperarm_twist_01_l', 'upperarm_twist_02_l', 'lowerarm_l', 'lowerarm_twist_01_l', 'lowerarm_twist_02_l',
    'clavicle_r', 'upperarm_r', 'upperarm_twist_01_r', 'upperarm_twist_02_r', 'lowerarm_r', 'lowerarm_twist_01_r', 'lowerarm_twist_02_r'
]

cleaned_count = 0
for v in mesh.data.vertices:
    if v.co.z < 0.88 and abs(v.co.x) < 0.30:
        has_stray = False
        for g in list(v.groups):
            vg_name = mesh.vertex_groups[g.group].name
            if vg_name in all_arm_groups:
                mesh.vertex_groups[g.group].remove([v.index])
                has_stray = True
        if has_stray:
            cleaned_count += 1
            # Berikan bobot ke pelvis (70%) dan thigh_l (30%)
            vg_map['pelvis'].add([v.index], 0.70, 'ADD')
            if v.co.x > 0:
                vg_map['thigh_l'].add([v.index], 0.30, 'ADD')
            else:
                vg_map['thigh_r'].add([v.index], 0.30, 'ADD')

print(f"Total verteks pinggul/paha yang dibebaskan dari lengan atas: {cleaned_count} verteks")

# Normalisasi 4 influences
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
print(f"Tersimpan di: {BLEND_OUT}")

# Ekspor FBX standar proyek
tmp_coll = bpy.data.collections.new("ExportTemp")
bpy.context.scene.collection.children.link(tmp_coll)

body_dup = mesh.copy()
body_dup.data = mesh.data.copy()
body_dup.name = body_dup.data.name = "SK_Aksa2"
tmp_coll.objects.link(body_dup)

arm_dup = arm.copy()
arm_dup.data = arm.data.copy()
arm_dup.animation_data_clear()
arm_dup.name = "Armature"
tmp_coll.objects.link(arm_dup)

mw = body_dup.matrix_world.copy()
body_dup.parent = None
body_dup.matrix_world = mw
for m in body_dup.modifiers:
    if m.type == "ARMATURE":
        m.object = arm_dup

BAKE_CM = 100.0
for o in (arm_dup, body_dup):
    o.matrix_world = Matrix.Scale(BAKE_CM, 4) @ o.matrix_world
bpy.context.view_layer.update()

with bpy.context.temp_override(active_object=arm_dup, selected_objects=[arm_dup, body_dup], selected_editable_objects=[arm_dup, body_dup]):
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

body_dup.parent = arm_dup
body_dup.matrix_parent_inverse = arm_dup.matrix_world.inverted()

for o in bpy.context.view_layer.objects:
    o.select_set(False)
export_objs = [arm_dup, body_dup]
for o in export_objs:
    o.select_set(True)

rna = bpy.ops.export_scene.fbx.get_rna_type().properties
def enum_ok(prop, value):
    p = rna.get(prop)
    return p is not None and value in [i.identifier for i in p.enum_items]

wanted = dict(
    filepath=str(FBX_OUT),
    use_selection=True,
    object_types={"ARMATURE", "MESH"},
    use_mesh_modifiers=True,
    add_leaf_bones=False,
    use_armature_deform_only=False,
    bake_anim=False,
    use_triangles=True,
    global_scale=1.0,
    apply_unit_scale=True,
    use_custom_props=False,
    embed_textures=False,
    use_tspace=False,
)
for prop, val in (("axis_forward", "-Y"), ("axis_up", "Z"),
                  ("armature_nodetype", "NULL"), ("mesh_smooth_type", "FACE"),
                  ("apply_scale_options", "FBX_SCALE_ALL"), ("colors_type", "SRGB")):
    if enum_ok(prop, val):
        wanted[prop] = val

kwargs = {k: v for k, v in wanted.items() if k in rna}
with bpy.context.temp_override(selected_objects=export_objs, selected_editable_objects=export_objs, active_object=arm_dup):
    res = bpy.ops.export_scene.fbx(**kwargs)

print(f"SK_Aksa2.fbx v20 berhasil diekspor: {res} -> {FBX_OUT}")
bpy.ops.wm.quit_blender()
