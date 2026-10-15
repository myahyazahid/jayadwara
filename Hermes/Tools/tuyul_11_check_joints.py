"""Tuyul K1 — periksa setiap sendi berada di dalam volume mesh.

  blender --background Hermes/Art/tuyul/Blender/tuyul_v02_skeleton.blend \
      --python Hermes/Tools/tuyul_11_check_joints.py
Untuk tiap tulang deform: uji head & tail dengan ray-cast BVH (paritas 3 arah, suara terbanyak).
Cetak DI DALAM / DI LUAR + jarak ke permukaan terdekat. Tidak mengubah apa pun.
"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ob = bpy.data.objects["TY_Source"]
arm = bpy.data.objects["TY_Armature"]
dg = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(ob, dg)

DIRS = [Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0)),
        Vector((0, 0, -1)), Vector((-1, 0, 0)), Vector((0, -1, 0))]


def _hits(origin, d):
    n, o = 0, origin.copy()
    for _ in range(128):
        loc, nor, idx, dist = bvh.ray_cast(o, d)
        if loc is None:
            break
        n += 1
        o = loc + d * 1e-5
    return n


JIT = [Vector((0.0131, 0.0073, 0.0)), Vector((0.0, 0.0117, 0.0059)), Vector((0.0091, 0.0, 0.0137))]


def parity(p):
    return sum(1 for i, d in enumerate(DIRS) if _hits(p, (d + JIT[i % 3]).normalized()) % 2 == 1) >= 4


def normal(p):
    loc, nor, idx, dist = bvh.find_nearest(p, 3.0)
    return loc is not None and (p - loc).dot(nor) < 0


def nearest(p):
    loc, nor, idx, dist = bvh.find_nearest(p, 3.0)
    return dist if loc is not None else -1.0


bad = []
print(f"{'tulang':16s} {'titik':5s} {'pos (x,y,z)':>26s} {'A':>2s} {'B':>2s}  d(mm)")
for b in arm.data.bones:
    if not b.use_deform or b.name == "root":   # root = tulang kendali di tanah (di luar mesh by design)
        continue
    for tag, p in (("head", b.head_local), ("tail", b.tail_local)):
        a, nb = parity(p), normal(p)
        ok = a and nb
        if not ok:
            bad.append((b.name, tag, a, nb, nearest(p)))
        print(f"{b.name:16s} {tag:5s} {str(tuple(round(v,3) for v in p)):>26s} "
              f"{'Y' if a else '-':>2s} {'Y' if nb else '-':>2s}  {nearest(p)*1000:5.1f}  {'OK' if ok else '<-- LUAR'}")

print()
if bad:
    print(f"!! {len(bad)} titik sendi gagal:")
    for n, t, a, nb, d in bad:
        print(f"   {n}.{t}: paritas={'in' if a else 'OUT'} normal={'in' if nb else 'OUT'} d={d*1000:.0f}mm")
else:
    print("LULUS: semua sendi di dalam volume mesh (kedua metode setuju).")
