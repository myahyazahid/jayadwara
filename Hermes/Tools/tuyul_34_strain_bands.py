"""K3 diag - regangan p99 per pita panjang tepi + peta spasial tepi terburuk.

  blender --background --factory-startup --python Hermes/Tools/tuyul_34_strain_bands.py -- <fbx> <profil.json> <height>
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:]
FBX, PROF, H = argv[0], argv[1], float(argv[2])
BANDS = [(0.0, 0.002), (0.002, 0.004), (0.004, 0.008), (0.008, 0.02), (0.02, 9.9)]

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=FBX)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
mesh = next(o for o in bpy.data.objects if o.type == "MESH")
U = mesh.matrix_world.to_scale().x
if max((mesh.matrix_world @ v.co).z for v in mesh.data.vertices) > 20:
    for o in bpy.data.objects:
        if o.parent is None:
            o.scale = o.scale * 0.01
    bpy.context.view_layer.update()
    U = mesh.matrix_world.to_scale().x

bones = arm.pose.bones
PROFIL = json.loads(Path(PROF).read_text(encoding="utf-8"))
SC = H / 1.806
AX = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}


def depth(name):
    n, b_ = 0, arm.data.bones[name]
    while b_.parent:
        n, b_ = n + 1, b_.parent
    return n


def reset_pose():
    arm.data.pose_position = "POSE"
    for pb in bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def set_world(pb, W):
    pb.matrix = arm.matrix_world.inverted() @ W
    bpy.context.view_layer.update()


def apply_ops(ops):
    for name, axis, val in sorted(ops, key=lambda o: depth(o[0])):
        pb = bones[name]
        W = arm.matrix_world @ pb.matrix
        if axis == "down":
            set_world(pb, Matrix.Translation((0, 0, -val * SC)) @ W)
        else:
            h = W.translation.copy()
            set_world(pb, Matrix.Translation(h) @ Matrix.Rotation(math.radians(val), 4, AX[axis]) @ Matrix.Translation(-h) @ W)


def ujung(pb):
    anak = [c for c in pb.children if "twist" not in c.name and not c.name.startswith("ik_")]
    if anak:
        c = max(anak, key=lambda c: (c.head - pb.head).length)
        if (c.head - pb.head).length > 1e-6:
            return arm.matrix_world @ c.head
    return arm.matrix_world @ pb.tail


def apply_arah(A):
    for name in sorted(A, key=depth):
        pb = bones[name]
        W = arm.matrix_world @ pb.matrix
        h = arm.matrix_world @ pb.head
        cur = (ujung(pb) - h).normalized()
        R = cur.rotation_difference(Vector(A[name]).normalized()).to_matrix().to_4x4()
        set_world(pb, Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ W)


def eval_co():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh.evaluated_get(dg)
    m = ev.to_mesh()
    co = [v.co.copy() for v in m.vertices]
    ev.to_mesh_clear()
    return co


reset_pose()
rest = eval_co()
edges = [(e.vertices[0], e.vertices[1]) for e in mesh.data.edges]
L0 = [(rest[a] - rest[b]).length * U for a, b in edges]
POSES = {k: v for k, v in PROFIL["pose"].items() if k != "rest"}
names = list(POSES) + list(PROFIL.get("arah", {}))
acc = {b: [] for b in BANDS}
allp = []
worst_map = {}
for pn in names:
    reset_pose()
    if pn in POSES:
        apply_ops(POSES[pn])
    else:
        apply_arah(PROFIL["arah"][pn])
    posed = eval_co()
    st = []
    for k, (a, b) in enumerate(edges):
        if L0[k] < 1e-6:
            continue
        st.append((abs((posed[a] - posed[b]).length * U - L0[k]) / L0[k] * 100.0, k))
    st.sort(reverse=True)
    allp.append(st[len(st) // 100][0])
    for bi, (lo, hi) in enumerate(BANDS):
        sub = sorted((s for s, k in st if lo <= L0[k] < hi), reverse=True)
        if len(sub) >= 20:
            acc[BANDS[bi]].append(sub[len(sub) // 100])
    if pn in ("lengan_depan_atas", "jongkok", "tangan_terangkat"):
        for s, k in st[:len(st) // 100]:
            a, b = edges[k]
            c = (rest[a] + rest[b]) / 2 * U
            key = (round(c.x * 5) / 5, round(c.z * 5) / 5)
            worst_map[key] = worst_map.get(key, 0) + 1

print(f"FILE {FBX}  H={H}  tepi={len(L0)}")
print(f"  p99 semua pose: rata2 {sum(allp)/len(allp):.1f}%  maks {max(allp):.1f}%")
for lo, hi in BANDS:
    v = acc[(lo, hi)]
    if v:
        print(f"  tepi {lo*1000:5.1f}-{hi*1000:5.1f} mm (n={len(v)} pose): p99 rata2 {sum(v)/len(v):6.1f}%  maks {max(v):7.1f}%")
    else:
        print(f"  tepi {lo*1000:5.1f}-{hi*1000:5.1f} mm: tidak ada")
print("  peta 1% terburuk (x,z dalam m, 3 pose lengan):")
for (x, z), c in sorted(worst_map.items(), key=lambda kv: -kv[1])[:10]:
    print(f"    x={x:+.2f} z={z:+.2f}  {c} tepi")
