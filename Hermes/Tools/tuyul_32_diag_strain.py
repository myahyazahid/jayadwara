"""K3 diag - cari tepi teregang terburuk pada satu pose + bobot vertex-nya.

  blender --background --factory-startup --python Hermes/Tools/tuyul_32_diag_strain.py -- <fbx> <pose> <profil.json> [height]
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:]
FBX, POSE, PROF = argv[0], argv[1], argv[2]
H = float(argv[3]) if len(argv) > 3 else 1.0

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=FBX)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
mesh = next(o for o in bpy.data.objects if o.type == "MESH")
if max((mesh.matrix_world @ v.co).z for v in mesh.data.vertices) > 20:
    for o in bpy.data.objects:
        if o.parent is None:
            o.scale = o.scale * 0.01
    bpy.context.view_layer.update()

bones = arm.pose.bones
PROFIL = json.loads(Path(PROF).read_text(encoding="utf-8"))
SC = H / 1.806
AX = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}
vgn = {vg.index: vg.name for vg in mesh.vertex_groups}


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


def eval_co():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh.evaluated_get(dg)
    m = ev.to_mesh()
    co = [v.co.copy() for v in m.vertices]
    ev.to_mesh_clear()
    return co


def weights(i):
    return sorted(((vgn[g.group], round(g.weight, 3)) for g in mesh.data.vertices[i].groups if g.weight > 1e-4),
                  key=lambda t: -t[1])


reset_pose()
rest = eval_co()
edges = [(e.vertices[0], e.vertices[1]) for e in mesh.data.edges]
L0 = [(rest[a] - rest[b]).length for a, b in edges]

if POSE in PROFIL.get("pose", {}):
    apply_ops(PROFIL["pose"][POSE])
else:
    A = PROFIL["arah"][POSE]

    def ujung(pb):
        anak = [c for c in pb.children if "twist" not in c.name and not c.name.startswith("ik_")]
        if anak:
            c = max(anak, key=lambda c: (c.head - pb.head).length)
            if (c.head - pb.head).length > 1e-6:
                return arm.matrix_world @ c.head
        return arm.matrix_world @ pb.tail

    for name in sorted(A, key=depth):
        pb = bones[name]
        W = arm.matrix_world @ pb.matrix
        h = arm.matrix_world @ pb.head
        cur = (ujung(pb) - h).normalized()
        R = cur.rotation_difference(Vector(A[name]).normalized()).to_matrix().to_4x4()
        set_world(pb, Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ W)

posed = eval_co()
st = []
for k, (a, b) in enumerate(edges):
    if L0[k] < 1e-6:
        continue
    st.append((abs((posed[a] - posed[b]).length - L0[k]) / L0[k] * 100.0, a, b, k))
st.sort(reverse=True)
print(f"pose={POSE}  tepi={len(st)}  p99={st[len(st)//100][0]:.1f}%  maks={st[0][0]:.1f}%")
print("--- 12 tepi terburuk (ruang model rest) ---")
for s, a, b, k in st[:12]:
    mid = (rest[a] + rest[b]) / 2
    print(f"  {s:7.1f}%  mid=({mid.x:+.3f},{mid.y:+.3f},{mid.z:+.3f})  L0={L0[k]*1000:.1f}mm")
    print(f"      v{a}: {weights(a)}")
    print(f"      v{b}: {weights(b)}")

# sebaran bobot di zona ketiak kiri (x>0.12, 0.55<z<0.80)
print("--- zona ketiak kiri (x>0.12, 0.55<z<0.80) ---")
hist, n = {}, 0
for v in mesh.data.vertices:
    c = v.co
    if c.x > 0.12 and 0.55 < c.z < 0.80:
        n += 1
        w = weights(v.index)
        if w:
            hist[w[0][0]] = hist.get(w[0][0], 0) + 1
print(f"  {n} vertex | dominan:", sorted(hist.items(), key=lambda kv: -kv[1])[:8])
