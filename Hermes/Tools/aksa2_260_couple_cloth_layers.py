"""
Hermes/Tools/aksa2_260_couple_cloth_layers.py
Menyinkronkan 100% bobot verteks pada lapisan kain ganda (inner lining & outer shell):
- Mengidentifikasi pasangan verteks yang berhimpitan (< 7mm) pada lengan, bahu, pergelangan tangan, dan jaket.
- Menyamakan bobot skinning pada lapisan dalam dan luar agar bergerak 100% sinkron.
- Menghilangkan total masalah robekan, lubang compang-camping, dan kulit tembus jaket saat animasi lompat/jatuh.
- Ekspor SK_Aksa2.fbx standar proyek.
"""
import bpy
import mathutils
from pathlib import Path
from mathutils import Matrix
from collections import defaultdict

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v32_perfect_normals.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v33_synchronized_cloth.blend"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
vg = {vg.index: vg.name for vg in mesh.vertex_groups}

all_verts = mesh.data.vertices
print(f"Total verteks model: {len(all_verts)}")

kd = mathutils.kdtree.KDTree(len(all_verts))
for i, v in enumerate(all_verts):
    kd.insert(v.co, i)
kd.balance()

# Cari pasangan berjarak < 7mm pada anggota tubuh yang sama
pairs = []
for i, v in enumerate(all_verts):
    for co, index, dist in kd.find_range(v.co, 0.007):
        if index > i:
            g1 = max(all_verts[i].groups, key=lambda g: g.weight).group if all_verts[i].groups else -1
            g2 = max(all_verts[index].groups, key=lambda g: g.weight).group if all_verts[index].groups else -1
            b1 = vg.get(g1, "")
            b2 = vg.get(g2, "")
            # Lewati jika menghubungkan sisi berlawanan (kiri vs kanan)
            if ("_l" in b1 and "_r" in b2) or ("_r" in b1 and "_l" in b2):
                continue
            # Lewati jika menghubungkan torso dan lengan (hindari jembatan ketiak)
            if ("spine" in b1 and ("upperarm" in b2 or "lowerarm" in b2)) or ("spine" in b2 and ("upperarm" in b1 or "lowerarm" in b1)):
                continue
            pairs.append((i, index))

print(f"Ditemukan {len(pairs)} pasangan verteks lapisan kain ganda yang akan disinkronkan.")

# Bentuk cluster komponen terhubung (connected components)
parent = {}
def find(i):
    if parent.setdefault(i, i) != i:
        parent[i] = find(parent[i])
    return parent[i]

def union(i, j):
    root_i, root_j = find(i), find(j)
    if root_i != root_j:
        parent[root_i] = root_j

for v1_idx, v2_idx in pairs:
    union(v1_idx, v2_idx)

clusters = defaultdict(list)
for i in range(len(all_verts)):
    if i in parent:
        clusters[find(i)].append(i)

multi_clusters = [c for c in clusters.values() if len(c) > 1]
print(f"Total cluster lapisan kain yang disatukan: {len(multi_clusters)}")

# Sinkronkan bobot di dalam tiap cluster
for c in multi_clusters:
    avg_weights = defaultdict(float)
    for v_idx in c:
        v = mesh.data.vertices[v_idx]
        for g in v.groups:
            avg_weights[g.group] += g.weight / len(c)
    
    for v_idx in c:
        v = mesh.data.vertices[v_idx]
        for g in list(v.groups):
            mesh.vertex_groups[g.group].remove([v_idx])
        for g_group, w in avg_weights.items():
            if w > 0.005:
                mesh.vertex_groups[g_group].add([v_idx], w, "ADD")

print("Sinkronisasi bobot lapisan kain selesai!")

# Normalisasi 4 influences
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)

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

print(f"SK_Aksa2.fbx v33 (Synchronized Cloth Layers) berhasil diekspor: {res} -> {FBX_OUT}")
bpy.ops.wm.quit_blender()
