"""Iterasi 1 — ekspor segitiga terproyeksi (depan XZ, samping YZ) pose rest ke .npz untuk silhouette_compare.py.

Jalankan di Blender. Argumen lewat variabel OUT_NPZ (default: scratchpad via env JD_NPZ atau Art/Export).
"""
import os

import bpy
import numpy as np

OUT_NPZ = globals().get("OUT_NPZ") or os.path.join(r"C:\repository\unreal_engine\jayadwara\Art\Export", "_silhouette.npz")

bpy.context.scene.frame_set(1)          # A-pose (frame 1 Action JD_PoseTest = pose rest)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()

front, side = [], []
for ob in bpy.data.objects:
    if ob.type != "MESH" or not ob.name.startswith("JD_"):
        continue
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    mw = ev.matrix_world
    co = np.array([tuple(mw @ v.co) for v in me.vertices], dtype=np.float32)
    for lt in me.loop_triangles:
        tri = co[list(lt.vertices)]
        front.append(tri[:, [0, 2]])    # x, z
        side.append(tri[:, [1, 2]])     # y, z
    ev.to_mesh_clear()
np.savez(OUT_NPZ, front=np.array(front), side=np.array(side))
print("tri:", len(front), "->", OUT_NPZ)
