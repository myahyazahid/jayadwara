"""
Hermes/Tools/aksa2_150_cut_fused_faces.py
Menghapus 186 face jembatan artifisial AI yang menyatukan lengan ke rusuk/torso (Z=1.07..1.33m),
sehingga lengan dan jaket terpisah mandiri secara topologi 3D seperti model game asli.
"""
import bpy
import bmesh
from pathlib import Path
from mathutils import Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v24_ultimate_clean.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v26_clean_topology.blend"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh_obj = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm_obj = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
vg = {vg.index: vg.name for vg in mesh_obj.vertex_groups}

bm = bmesh.new()
bm.from_mesh(mesh_obj.data)
bm.faces.ensure_lookup_table()
bm.verts.ensure_lookup_table()

# Cari face yang memiliki vertex torso DAN vertex arm
fused_faces = []
for f in bm.faces:
    bones_in_face = set()
    for v in f.verts:
        v_orig = mesh_obj.data.vertices[v.index]
        if v_orig.groups:
            g_max = max(v_orig.groups, key=lambda g: g.weight)
            bones_in_face.add(vg.get(g_max.group, '?'))
    
    has_torso = any('spine' in b or 'pelvis' in b for b in bones_in_face)
    has_arm = any('upperarm' in b or 'lowerarm' in b for b in bones_in_face)
    if has_torso and has_arm:
        fused_faces.append(f)

print(f"Menghapus {len(fused_faces)} face jembatan yang menyatukan lengan ke rusuk...")
bmesh.ops.delete(bm, geom=fused_faces, context='FACES_ONLY')

bm.to_mesh(mesh_obj.data)
bm.free()
mesh_obj.data.update()

# Normalisasi 4 influences
bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
print(f"Tersimpan di: {BLEND_OUT}")

# Ekspor FBX standar proyek
tmp_coll = bpy.data.collections.new("ExportTemp")
bpy.context.scene.collection.children.link(tmp_coll)

body_dup = mesh_obj.copy()
body_dup.data = mesh_obj.data.copy()
body_dup.name = body_dup.data.name = "SK_Aksa2"
tmp_coll.objects.link(body_dup)

arm_dup = arm_obj.copy()
arm_dup.data = arm_obj.data.copy()
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

print(f"SK_Aksa2.fbx v26 (Clean Topology) berhasil diekspor: {res} -> {FBX_OUT}")
bpy.ops.wm.quit_blender()
