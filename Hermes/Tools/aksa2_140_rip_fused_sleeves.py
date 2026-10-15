"""
Hermes/Tools/aksa2_140_rip_fused_sleeves.py
Memotong jembatan poligon yang menyatukan lengan baju ke badan jaket (Z=1.03..1.16m, |X|=0.25..0.27m).
Memisahkan lengan menjadi silinder mandiri sehingga tangan bisa bebas bergerak tanpa menarik badan jaket.
"""
import bpy
import bmesh
from pathlib import Path
from mathutils import Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v24_ultimate_clean.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v25_separated_sleeves.blend"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh_obj = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm_obj = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# Gunakan bmesh untuk mencari dan memotong edge yang menempel
bm = bmesh.new()
bm.from_mesh(mesh_obj.data)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()

# Cari edge jembatan yang menghubungkan sisi luar (|X| > 0.258m) dan sisi dalam (|X| < 0.258m) pada Z=1.03..1.16m
bridge_edges = []
for e in bm.edges:
    v1, v2 = e.verts
    c1, c2 = v1.co, v2.co
    z_avg = (c1.z + c2.z) / 2
    if 1.02 <= z_avg <= 1.16:
        # Sisi kanan (X negatif)
        if c1.x < 0 and c2.x < 0:
            if (c1.x < -0.258 and c2.x > -0.258) or (c2.x < -0.258 and c1.x > -0.258):
                bridge_edges.append(e)
        # Sisi kiri (X positif)
        elif c1.x > 0 and c2.x > 0:
            if (c1.x > 0.258 and c2.x < 0.258) or (c2.x > 0.258 and c1.x < 0.258):
                bridge_edges.append(e)

print(f"Ditemukan {len(bridge_edges)} edge jembatan yang menyatukan lengan ke badan. Memotong edge...")

# Pisahkan edge (edge split)
res = bmesh.ops.split_edges(bm, edges=bridge_edges)

# Tulis kembali ke mesh
bm.to_mesh(mesh_obj.data)
bm.free()
mesh_obj.data.update()

# Sekarang, perbaiki pembobotan pada verteks yang baru dipisah:
# Verteks dengan |X| > 0.258m adalah milik lengan -> berikan ke lowerarm
# Verteks dengan |X| <= 0.258m adalah milik badan -> berikan ke spine_03 / spine_04
vg_map = {vg.name: vg for vg in mesh_obj.vertex_groups}

for v in mesh_obj.data.vertices:
    abs_x = abs(v.co.x)
    z = v.co.z
    # Pada zona pemisahan (Z=1.02..1.16m)
    if 1.02 <= z <= 1.16:
        # Jika di sisi badan (|X| <= 0.258m): hapus semua lowerarm/upperarm, berikan ke spine
        if abs_x <= 0.258:
            stray = 0.0
            for g in list(v.groups):
                vg_name = mesh_obj.vertex_groups[g.group].name
                if 'lowerarm' in vg_name or 'upperarm' in vg_name or 'clavicle' in vg_name:
                    stray += g.weight
                    mesh_obj.vertex_groups[g.group].remove([v.index])
            if stray > 0.001:
                vg_map['spine_03'].add([v.index], stray, 'ADD')
        
        # Jika di sisi lengan (|X| > 0.258m): hapus semua spine/pelvis, berikan ke lowerarm
        elif abs_x > 0.258 and abs_x < 0.35:
            stray = 0.0
            for g in list(v.groups):
                vg_name = mesh_obj.vertex_groups[g.group].name
                if 'spine' in vg_name or 'pelvis' in vg_name or 'thigh' in vg_name:
                    stray += g.weight
                    mesh_obj.vertex_groups[g.group].remove([v.index])
            if stray > 0.001:
                bone_arm = 'lowerarm_l' if v.co.x > 0 else 'lowerarm_r'
                vg_map[bone_arm].add([v.index], stray, 'ADD')

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

print(f"SK_Aksa2.fbx v25 (Separated Sleeves) berhasil diekspor: {res} -> {FBX_OUT}")
bpy.ops.wm.quit_blender()
