"""
Hermes/Tools/aksa2_330_test_perfect_armpit_separation.py
Penyempurnaan Total Geometri dan Rigging Aksa2:
1. Merge doubles 2mm -> menutup 26 celah mikro bawaan Tripo AI (0 open edges).
2. Memisahkan 59 face jembatan ketiak yang menyatukan lengan ke pinggang.
3. Menutup (cap/fill) lubang torso dan lengan secara watertight (0 boundary edges).
4. Penugasan bobot bersih: Torso -> spine_04, Lengan -> upperarm.
5. Rekalkulasi normal permukaan menghadap ke luar.
6. Sinkronisasi lapisan kain (< 7mm).
7. Menguji pose lompat dinamis dan mengukur peregangan.
"""
import bpy
import bmesh
import math
import mathutils
from pathlib import Path
from mathutils import Vector, Matrix
from collections import defaultdict

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v33_synchronized_cloth.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v34_flawless_watertight.blend"
CLEAN_BC = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "Textures" / "T_Aksa2_BC.png"

bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

bm = bmesh.new()
bm.from_mesh(mesh.data)

# 1. Merge doubles 2mm untuk menutup 26 celah mikro bawaan AI
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
print("Merge doubles 2mm selesai. Open edges:", len([e for e in bm.edges if e.is_boundary]))

# 2. Cari dan hapus 59 face jembatan ketiak (Z: 1.05..1.28m)
armpit_edges = []
for e in bm.edges:
    c1, c2 = e.verts[0].co, e.verts[1].co
    if (1.05 <= c1.z <= 1.28 and 1.05 <= c2.z <= 1.28) and ((abs(c1.x) < 0.245 and abs(c2.x) > 0.255) or (abs(c2.x) < 0.245 and abs(c1.x) > 0.255)):
        armpit_edges.append(e)

bridge_faces = list(set(f for e in armpit_edges for f in e.link_faces))
print(f"Menghapus {len(bridge_faces)} bridge faces ketiak...")
bmesh.ops.delete(bm, geom=bridge_faces, context="FACES_ONLY")

# 3. Tutup lubang yang terbentuk dengan holes_fill
open_edges = [e for e in bm.edges if e.is_boundary]
print(f"Boundary edges yang akan ditutup: {len(open_edges)}")
res_fill = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
print(f"Holes fill menambahkan {len(res_fill['faces'])} faces penutup baru.")

# 4. Rekalkulasi normal ke luar
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Verifikasi integritas manifold
rem_open = [e for e in bm.edges if e.is_boundary]
print(f"VERIFIKASI INTEGRITAS: Sisa boundary edges = {len(rem_open)} (HARUS 0)")

bm.to_mesh(mesh.data)
bm.free()

# 5. Penugasan bobot bersih pada area ketiak
vg = {vg.index: vg.name for vg in mesh.vertex_groups}
vg_by_name = {vg.name: vg for vg in mesh.vertex_groups}

for v in mesh.data.vertices:
    ax = abs(v.co.x)
    side = "_l" if v.co.x > 0 else "_r"
    
    # Area Torso samping (|X| <= 0.245m, Z <= 1.28m): 100% spine
    if ax <= 0.245 and v.co.z <= 1.28:
        for g in list(v.groups):
            bname = vg.get(g.group, "")
            if any(k in bname for k in ["arm", "hand", "clavicle", "ring", "index", "thumb"]):
                mesh.vertex_groups[g.group].remove([v.index])
        vg_by_name["spine_04"].add([v.index], 1.0, "ADD")
    
    # Area Selongsong lengan bawah/ketiak (0.245m < |X| <= 0.29m, 1.05m <= Z <= 1.25m): 100% upperarm
    elif 0.245 < ax <= 0.29 and 1.05 <= v.co.z <= 1.25:
        lower_w = 0.0
        for g in list(v.groups):
            bname = vg.get(g.group, "")
            if "lowerarm" in bname or "hand" in bname:
                lower_w += g.weight
                mesh.vertex_groups[g.group].remove([v.index])
        if lower_w > 0.01:
            target_bone = f"upperarm{side}"
            vg_by_name[target_bone].add([v.index], lower_w, "ADD")

# 6. Sinkronisasi lapisan kain ganda (< 7mm)
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

bpy.context.view_layer.objects.active = mesh
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
print(f"Model v34 tersimpan: {BLEND_OUT}")

# 7. Uji Pose Lompat
if arm.animation_data:
    arm.animation_data_clear()
arm.data.pose_position = "POSE"
bones = arm.pose.bones
for pb in bones:
    pb.location = (0, 0, 0)
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.rotation_euler = (0, 0, 0)
    pb.scale = (1, 1, 1)

AX = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}
def set_world(pb, W):
    pb.matrix = arm.matrix_world.inverted() @ W
    bpy.context.view_layer.update()

jump_ops = [
    ["pelvis", "down", -0.15],
    ["thigh_l", "x", -50], ["calf_l", "x", 75], ["foot_l", "x", -20],
    ["thigh_r", "x", -35], ["calf_r", "x", 65], ["foot_r", "x", -15],
    ["spine_02", "x", 12], ["spine_03", "x", 12],
    ["upperarm_l", "y", -70], ["upperarm_l", "x", 25],
    ["lowerarm_l", "z", -75], ["lowerarm_l", "x", 35],
    ["hand_l", "z", -25],
    ["upperarm_r", "y", 70], ["upperarm_r", "x", 25],
    ["lowerarm_r", "z", 75], ["lowerarm_r", "x", 35],
    ["hand_r", "z", 25],
]
for op in jump_ops:
    name, axis, val = op[0], op[1], op[2]
    pb = bones[name]
    W = arm.matrix_world @ pb.matrix
    if axis == "down":
        W.translation.z -= val
        set_world(pb, W)
    elif axis in AX:
        h = arm.matrix_world @ pb.head
        R = Matrix.Rotation(math.radians(val), 4, AX[axis])
        set_world(pb, Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ W)

bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
eval_m = mesh.evaluated_get(deps).to_mesh()

stretches = []
for e in mesh.data.edges:
    v1, v2 = e.vertices
    lr = (mesh.data.vertices[v1].co - mesh.data.vertices[v2].co).length
    lp = (eval_m.vertices[v1].co - eval_m.vertices[v2].co).length
    diff = lp - lr
    if diff > 0.08: # > 8cm
        d1 = vg.get(max(mesh.data.vertices[v1].groups, key=lambda g: g.weight).group, "?") if mesh.data.vertices[v1].groups else "?"
        d2 = vg.get(max(mesh.data.vertices[v2].groups, key=lambda g: g.weight).group, "?") if mesh.data.vertices[v2].groups else "?"
        stretches.append((diff, lr, lp, v1, v2, d1, d2))

stretches.sort(key=lambda s: s[0], reverse=True)
print(f"UJI POSE LOMPAT v34: Edges stretching > 8cm: {len(stretches)}")
for s in stretches[:10]:
    print(f"  Stretch={s[0]*100:5.1f}cm (rest={s[1]*100:4.1f}cm -> pose={s[2]*100:4.1f}cm): Vert {s[3]} ({s[5]}) <-> Vert {s[4]} ({s[6]})")
