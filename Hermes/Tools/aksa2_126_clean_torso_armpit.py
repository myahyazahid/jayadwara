"""
Hermes/Tools/aksa2_126_clean_torso_armpit.py
Membersihkan 125 verteks torso/rusuk bawah (|X| <= 0.26m, Z <= 1.28m) dari bobot upperarm_twist_02,
sehingga jaring/selaput melar antara lengan dan rusuk tereliminasi total.
"""
import bpy
from pathlib import Path
from mathutils import Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v20_perfect_anatomy.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v22_clean_webbing.blend"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

vg_map = {vg.name: vg for vg in mesh.vertex_groups}
for name in ["spine_02", "spine_03", "spine_04", "spine_05"]:
    if name not in vg_map:
        vg_map[name] = mesh.vertex_groups.new(name=name)

all_arm_groups = [
    'clavicle_l', 'upperarm_l', 'upperarm_twist_01_l', 'upperarm_twist_02_l', 'lowerarm_l', 'lowerarm_twist_01_l', 'lowerarm_twist_02_l',
    'clavicle_r', 'upperarm_r', 'upperarm_twist_01_r', 'upperarm_twist_02_r', 'lowerarm_r', 'lowerarm_twist_01_r', 'lowerarm_twist_02_r'
]

cleaned_count = 0
for v in mesh.data.vertices:
    x, y, z = v.co
    abs_x = abs(x)

    # 1. Torso samping bawah (|X| <= 0.26m, Z <= 1.28m)
    # Tidak boleh ada tulang lengan sama sekali!
    if abs_x <= 0.26 and z <= 1.28:
        stray_w = 0.0
        for g in list(v.groups):
            vg_name = mesh.vertex_groups[g.group].name
            if vg_name in all_arm_groups:
                stray_w += g.weight
                mesh.vertex_groups[g.group].remove([v.index])
        if stray_w > 0.001:
            cleaned_count += 1
            if z < 1.18:
                vg_map['spine_02'].add([v.index], stray_w * 0.4, 'ADD')
                vg_map['spine_03'].add([v.index], stray_w * 0.6, 'ADD')
            elif z < 1.24:
                vg_map['spine_03'].add([v.index], stray_w * 0.5, 'ADD')
                vg_map['spine_04'].add([v.index], stray_w * 0.5, 'ADD')
            else:
                vg_map['spine_04'].add([v.index], stray_w * 0.6, 'ADD')
                vg_map['spine_05'].add([v.index], stray_w * 0.4, 'ADD')

    # 2. Torso tengah ketiak (|X| <= 0.22m, 1.28m < Z <= 1.36m)
    # Tidak boleh ada upperarm/lowerarm! Clavicle hanya transisi halus jika Z > 1.34m
    elif abs_x <= 0.22 and 1.28 < z <= 1.36:
        stray_arm = 0.0
        for g in list(v.groups):
            vg_name = mesh.vertex_groups[g.group].name
            if 'upperarm' in vg_name or 'lowerarm' in vg_name:
                stray_arm += g.weight
                mesh.vertex_groups[g.group].remove([v.index])
        if stray_arm > 0.001:
            cleaned_count += 1
            vg_map['spine_04'].add([v.index], stray_arm * 0.5, 'ADD')
            vg_map['spine_05'].add([v.index], stray_arm * 0.5, 'ADD')

print(f"Total verteks torso yang dibebaskan dari tarikan lengan: {cleaned_count} verteks")

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

print(f"SK_Aksa2.fbx v22 berhasil diekspor: {res} -> {FBX_OUT}")
bpy.ops.wm.quit_blender()
