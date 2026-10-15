"""Tuyul K1 — temukan pusat tiap jari (komponen 'di dalam mesh') per pita z.
  blender --background Hermes/Art/tuyul/Blender/tuyul_v02_skeleton.blend \
      --python Hermes/Tools/tuyul_15_fingers.py
Grid 3mm; cetak centroid tiap komponen + ukuran. Untuk sisi kiri (x>0) dan kanan (x<0).
"""
from collections import deque

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


STEP = 0.002


def comps(z, x0, x1, y0, y1):
    nx, ny = int((x1 - x0) / STEP) + 1, int((y1 - y0) / STEP) + 1
    grid = [[inside(Vector((x0 + i * STEP, y0 + j * STEP, z))) for j in range(ny)] for i in range(nx)]
    seen = [[False] * ny for _ in range(nx)]
    out = []
    for i in range(nx):
        for j in range(ny):
            if grid[i][j] and not seen[i][j]:
                q, cell = deque([(i, j)]), []
                seen[i][j] = True
                while q:
                    a, b = q.popleft()
                    cell.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        na, nb = a + da, b + db
                        if 0 <= na < nx and 0 <= nb < ny and grid[na][nb] and not seen[na][nb]:
                            seen[na][nb] = True
                            q.append((na, nb))
                if len(cell) >= 3:
                    cx = sum(x0 + a * STEP for a, _ in cell) / len(cell)
                    cy = sum(y0 + b * STEP for _, b in cell) / len(cell)
                    out.append((cx, cy, len(cell)))
    return sorted(out, key=lambda t: t[1])


for side, x0, x1 in (("KIRI", 0.20, 0.29), ("KANAN", -0.29, -0.20)):
    print(f"===== {side} =====")
    for z in (0.25, 0.24, 0.23, 0.22, 0.21, 0.20, 0.19, 0.18, 0.17, 0.16, 0.15):
        cs = comps(z, x0, x1, -0.13, 0.05)
        txt = " | ".join(f"({c[0]:+.3f},{c[1]:+.3f})n{c[2]}" for c in cs)
        print(f"  z={z:0.2f}: {txt}")
