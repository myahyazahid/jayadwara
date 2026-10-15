"""
Hermes/Tools/aksa2_170_perfect_manifold_rig.py
Penyempurnaan Total Aksa2 (Clean Manifold & Smooth Anatomy):
1. Mempertahankan 100% geometri utuh (37.988 tris) tanpa menghapus face/edge sama sekali -> ZERO ROBEKAN / ZERO LUBANG.
2. Membebaskan verteks pinggul/paha (Z < 0.88m) dari tulang lengan -> alihkan ke pelvis/thigh.
3. Menstabilkan rusuk ketiak (|X| <= 0.23m, Z <= 1.33m): meredam tarikan clavicle/upperarm -> alihkan ke spine_04/spine_05.
4. Menjaga sendi siku (|X| >= 0.25m) tetap memiliki transisi alami upperarm_twist_02 dan lowerarm -> tidak kempis/penyok.
5. Normalisasi 4 influences dan ekspor SK_Aksa2.fbx standar proyek.
"""
import bpy
from pathlib import Path
from mathutils import Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v17_perfect_rig.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v30_perfect_manifold.blend"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

vg_map = {vg.name: vg for vg in mesh.vertex_groups}
for name in ["spine_02", "spine_03", "spine_04", "spine_05", "pelvis", "thigh_l", "thigh_r"]:
    if name not in vg_map:
        vg_map[name] = mesh.vertex_groups.new(name=name)

all_arm_groups = [
    'clavicle_l', 'upperarm_l', 'upperarm_twist_01_l', 'upperarm_twist_02_l', 'lowerarm_l', 'lowerarm_twist_01_l', 'lowerarm_twist_02_l',
    'clavicle_r', 'upperarm_r', 'upperarm_twist_01_r', 'upperarm_twist_02_r', 'lowerarm_r', 'lowerarm_twist_01_r', 'lowerarm_twist_02_r'
]

cleaned_hip = 0
cleaned_torso = 0

for v in mesh.data.vertices:
    x, y, z = v.co
    abs_x = abs(x)

    # 1. Bersihkan pinggul/paha bawah (Z < 0.88m, |X| < 0.30m) dari tulang lengan
    if z < 0.88 and abs_x < 0.30:
        stray_hip = 0.0
        for g in list(v.groups):
            vg_name = mesh.vertex_groups[g.group].name
            if vg_name in all_arm_groups:
                stray_hip += g.weight
                mesh.vertex_groups[g.group].remove([v.index])
        if stray_hip > 0.001:
            cleaned_hip += 1
            vg_map["pelvis"].add([v.index], stray_hip * 0.7, "ADD")
            if x > 0:
                vg_map["thigh_l"].add([v.index], stray_hip * 0.3, "ADD")
            else:
                vg_map["thigh_r"].add([v.index], stray_hip * 0.3, "ADD")

    # 2. Bersihkan rusuk/torso ketiak (|X| <= 0.23m, Z <= 1.33m)
    elif abs_x <= 0.23 and z <= 1.33:
        # Hapus upperarm dan lowerarm dari torso ketiak
        stray_arm = 0.0
        for g in list(v.groups):
            vg_name = mesh.vertex_groups[g.group].name
            if 'upperarm' in vg_name or 'lowerarm' in vg_name:
                stray_arm += g.weight
                mesh.vertex_groups[g.group].remove([v.index])
        if stray_arm > 0.001:
            cleaned_torso += 1
            vg_map["spine_04"].add([v.index], stray_arm * 0.5, "ADD")
            vg_map["spine_05"].add([v.index], stray_arm * 0.5, "ADD")

        # Redam clavicle di bawah ketiak (Z <= 1.33m)
        for clav_name in ['clavicle_l', 'clavicle_r']:
            if clav_name in vg_map:
                try:
                    w = vg_map[clav_name].weight(v.index)
                except RuntimeError:
                    w = 0.0
                if w > 0.01:
                    if z < 1.26:
                        vg_map[clav_name].remove([v.index])
                        vg_map['spine_03'].add([v.index], w * 0.4, 'ADD')
                        vg_map['spine_04'].add([v.index], w * 0.6, 'ADD')
                        cleaned_torso += 1
                    else:
                        max_w = (z - 1.26) / (1.33 - 1.26) * 0.20
                        if w > max_w:
                            diff = w - max_w
                            vg_map[clav_name].add([v.index], -diff, 'ADD')
                            vg_map['spine_04'].add([v.index], diff * 0.6, 'ADD')
                            vg_map['spine_05'].add([v.index], diff * 0.4, 'ADD')
                            cleaned_torso += 1

print(f"Hasil penyempurnaan manifold:")
print(f"  - Verteks pinggul dibebaskan dari tulang lengan: {cleaned_hip} verteks")
print(f"  - Verteks rusuk ketiak diselaraskan ke torso: {cleaned_torso} penyesuaian")

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

print(f"SK_Aksa2.fbx v30 (Perfect Manifold) berhasil diekspor: {res} -> {FBX_OUT}")
bpy.ops.wm.quit_blender()
