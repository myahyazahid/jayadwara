"""Tuyul K1 — peta ASCII 'di dalam mesh' irisan tangan kiri & kanan.
  blender --background Hermes/Art/tuyul/Blender/tuyul_v02_skeleton.blend \
      --python Hermes/Tools/tuyul_14_probe_inside.py
Kolom = x (0.005 m), baris = y dari depan(-Y) ke belakang(+Y). '#'=di dalam, '.'=di luar.
"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ob = bpy.data.objects["TY_Source"]
dg = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(ob, dg)
DIRS = [Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0)),
        Vector((0, 0, -1)), Vector((-1, 0, 0)), Vector((0, -1, 0))]


def _hits(o, d):
    n, p = 0, o.copy()
    for _ in range(128):
        loc, nor, idx, dist = bvh.ray_cast(p, d)
        if loc is None:
            break
        n += 1
        p = loc + d * 1e-5
    return n


def inside(p):
    par = sum(1 for d in DIRS if _hits(p, d) % 2 == 1) >= 4
    loc, nor, idx, dist = bvh.find_nearest(p, 3.0)
    return par and loc is not None and (p - loc).dot(nor) < 0


for side, xr in (("KIRI", (0.17, 0.29)), ("KANAN", (-0.29, -0.17))):
    for z in (0.22, 0.21, 0.20, 0.19, 0.18):
        print(f"== {side} z={z:0.2f} ==")
        ys = [round(-0.10 + 0.005 * i, 3) for i in range(27)]
        xs = [round(xr[0] + 0.005 * i, 3) for i in range(25)]
        print("      " + "".join("|" if abs(x) < 0.02 else " " for x in xs))
        for y in ys:
            row = "".join("#" if inside(Vector((x, y, z))) else "." for x in xs)
            print(f"y{y:+.3f} {row}")
        print(f"       x {xs[0]:+.3f} .. {xs[-1]:+.3f}")
