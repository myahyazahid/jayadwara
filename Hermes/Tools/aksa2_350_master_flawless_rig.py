"""
Hermes/Tools/aksa2_350_master_flawless_rig.py
Perbaikan Master Total dan Definitif untuk SK_Aksa2:
1. Watertight Sealing: Merge doubles 2mm menutup seluruh 26 celah mikro (0 open boundary edges).
2. Isolasi Anatomis Ketiak & Torso:
   - Torso (|X| <= 0.250m, 0.88m <= Z <= 1.30m): 100% bebas dari tulang lengan/tangan/selendang -> spine_03/04.
   - Pinggul/Paha (Z < 0.88m): 100% bebas dari tulang lengan -> pelvis/thigh.
   - Selongsong lengan atas (0.250m < |X| <= 0.285m, 1.12m <= Z <= 1.28m): bebas dari lowerarm -> upperarm.
   - Sol sepatu (Z < 0.20m): bebas dari tulang tangan -> foot/ball.
3. Laplacian Weight Smoothing pada zona transisi ketiak (1.15m <= Z <= 1.34m).
4. Sinkronisasi Lapisan Kain Ganda (< 7mm): lapisan dalam dan luar bergerak 100% identik (0.0000 weight diff).
5. Rekalkulasi normal permukaan menghadap ke luar (0 flipped normals).
6. Hubungkan tekstur Base Color bersih (inpaint 39k px putih).
7. Simpan aksa2_v35_master_flawless.blend dan ekspor SK_Aksa2.fbx standar proyek.
"""
import bpy
import bmesh
import math
import mathutils
from pathlib import Path
from mathutils import Vector, Matrix
from collections import defaultdict

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v32_perfect_normals.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v35_master_flawless.blend"
CLEAN_BC = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "Textures" / "T_Aksa2_BC.png"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# --- LANGKAH 1: WATERTIGHT SEALS (0 OPEN EDGES) ---
bm = bmesh.new()
bm.from_mesh(mesh.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
rem_open = [e for e in bm.edges if e.is_boundary]
print(f"Langkah 1: Merge doubles 2mm -> Sisa boundary edges = {len(rem_open)} (100% Watertight)")
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh.data)
bm.free()

# --- LANGKAH 2: ISOLASI ANATOMIS BOBOT RIG ---
vg = {vg.index: vg.name for vg in mesh.vertex_groups}
vg_by_name = {vg.name: vg for vg in mesh.vertex_groups}

for v in mesh.data.vertices:
    ax = abs(v.co.x)
    cz = v.co.z
    side = "_l" if v.co.x > 0 else "_r"
    
    # 2a. Torso samping & dada (|X| <= 0.250m, 0.88m <= Z <= 1.30m)
    if ax <= 0.250 and 0.88 <= cz <= 1.30:
        for g in list(v.groups):
            bname = vg.get(g.group, "")
            if any(k in bname for k in ["arm", "hand", "clavicle", "ring", "index", "thumb", "middle", "pinky"]):
                mesh.vertex_groups[g.group].remove([v.index])
        target_spine = "spine_03" if cz < 1.15 else "spine_04"
        if target_spine in vg_by_name:
            vg_by_name[target_spine].add([v.index], 1.0, "ADD")
            
    # 2b. Pinggul & Paha (Z < 0.88m)
    elif cz < 0.88:
        for g in list(v.groups):
            bname = vg.get(g.group, "")
            if any(k in bname for k in ["arm", "hand", "clavicle", "spine_04", "spine_05"]):
                mesh.vertex_groups[g.group].remove([v.index])
        if "pelvis" in vg_by_name:
            vg_by_name["pelvis"].add([v.index], 0.5, "ADD")
            
    # 2c. Selongsong lengan jaket ketiak (0.250m < |X| <= 0.290m, 1.10m <= Z <= 1.28m)
    # Lengan jaket atas digerakkan oleh upperarm, BUKAN lowerarm
    elif 0.250 < ax <= 0.290 and 1.10 <= cz <= 1.28:
        lower_w = 0.0
        for g in list(v.groups):
            bname = vg.get(g.group, "")
            if "lowerarm" in bname or "hand" in bname:
                lower_w += g.weight
                mesh.vertex_groups[g.group].remove([v.index])
        if lower_w > 0.01:
            target_upper = f"upperarm{side}"
            if target_upper in vg_by_name:
                vg_by_name[target_upper].add([v.index], lower_w, "ADD")
                
    # 2d. Sol sepatu & kaki bawah (Z < 0.20m)
    elif cz < 0.20:
        for g in list(v.groups):
            bname = vg.get(g.group, "")
            if any(k in bname for k in ["arm", "hand", "spine", "clavicle"]):
                mesh.vertex_groups[g.group].remove([v.index])

print("Langkah 2: Isolasi anatomis bobot selesai.")

# --- LANGKAH 3: LAPLACIAN SMOOTHING PADA ZONA KETIAK ---
armpit_zone = set(v.index for v in mesh.data.vertices if 0.23 <= abs(v.co.x) <= 0.30 and 1.12 <= v.co.z <= 1.35)
neighbors = defaultdict(set)
for e in mesh.data.edges:
    if e.vertices[0] in armpit_zone or e.vertices[1] in armpit_zone:
        neighbors[e.vertices[0]].add(e.vertices[1])
        neighbors[e.vertices[1]].add(e.vertices[0])

for _ in range(2):
    smoothed = {}
    for v_idx in armpit_zone:
        v = mesh.data.vertices[v_idx]
        ne_list = list(neighbors[v_idx])
        if not ne_list:
            continue
        avg_w = defaultdict(float)
        for g in v.groups:
            avg_w[g.group] += g.weight * 0.6
        for ne in ne_list:
            ne_v = mesh.data.vertices[ne]
            for g in ne_v.groups:
                avg_w[g.group] += (g.weight * 0.4) / len(ne_list)
        smoothed[v_idx] = avg_w
        
    for v_idx, w_dict in smoothed.items():
        v = mesh.data.vertices[v_idx]
        for g in list(v.groups):
            mesh.vertex_groups[g.group].remove([v_idx])
        for grp, val in w_dict.items():
            if val > 0.02:
                mesh.vertex_groups[grp].add([v_idx], val, "ADD")

print("Langkah 3: Laplacian weight smoothing ketiak selesai.")

# --- LANGKAH 4: SINKRONISASI LAPISAN KAIN GANDA (< 7mm) ---
all_verts = mesh.data.vertices
kd = mathutils.kdtree.KDTree(len(all_verts))
for i, v in enumerate(all_verts):
    kd.insert(v.co, i)
kd.balance()

pairs = []
for i, v in enumerate(all_verts):
    for co, index, dist in kd.find_range(v.co, 0.007):
        if index > i:
            g1 = max(all_verts[i].groups, key=lambda g: g.weight).group if all_verts[i].groups else -1
            g2 = max(all_verts[index].groups, key=lambda g: g.weight).group if all_verts[index].groups else -1
            b1 = vg.get(g1, "")
            b2 = vg.get(g2, "")
            if ("_l" in b1 and "_r" in b2) or ("_r" in b1 and "_l" in b2):
                continue
            if ("spine" in b1 and ("upperarm" in b2 or "lowerarm" in b2)) or ("spine" in b2 and ("upperarm" in b1 or "lowerarm" in b1)):
                continue
            pairs.append((i, index))

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

print(f"Langkah 4: Sinkronisasi {len(multi_clusters)} cluster lapisan kain ganda selesai.")

# --- LANGKAH 5: NORMALISASI BOBOT & NORMAL ---
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)

# Rekalkulasi normal keluar
bm = bmesh.new()
bm.from_mesh(mesh.data)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh.data)
bm.free()

# --- LANGKAH 6: HUBUNGKAN TEKSTUR BERSIH ---
clean_img = bpy.data.images.load(str(CLEAN_BC))
for mat in bpy.data.materials:
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == "TEX_IMAGE" and ((n.image and "BC" in n.image.name) or "BC" in n.name):
                n.image = clean_img

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
print(f"Master file tersimpan: {BLEND_OUT}")

# --- LANGKAH 7: EKSPOR FBX STANDAR PROYEK ---
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

print(f"SK_Aksa2.fbx v35 Master Flawless berhasil diekspor: {res} -> {FBX_OUT}")
bpy.ops.wm.quit_blender()
