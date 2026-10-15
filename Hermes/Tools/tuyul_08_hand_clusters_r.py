"""Tuyul K1 — klaster halus region lengan/tangan KANAN (x<-0.13) per pita z 1cm.
  blender --background Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend \
      --python Hermes/Tools/tuyul_08_hand_clusters_r.py
"""
import numpy as np
import bpy

ob = bpy.data.objects["TY_Source"]
co = np.array([v.co[:] for v in ob.data.vertices])
GAP = 0.02

for z in np.arange(0.33, 0.11, -0.01):
    m = (co[:, 2] >= z - 0.005) & (co[:, 2] < z + 0.005) & (co[:, 0] < -0.13)
    if not m.any():
        continue
    s = co[m]
    s = s[np.argsort(-s[:, 0])]   # urut dari x paling negatif
    cl, start = [], 0
    for i in range(1, len(s)):
        if s[i - 1, 0] - s[i, 0] > GAP:
            cl.append(s[start:i]); start = i
    cl.append(s[start:])
    parts = []
    for c in cl:
        parts.append(f"[x{c[:,0].min():+.3f}..{c[:,0].max():+.3f} xc{c[:,0].mean():+.3f} "
                     f"y{c[:,1].min():+.3f}..{c[:,1].max():+.3f} yc{c[:,1].mean():+.3f} n{len(c)}]")
    print(f"z={z:0.2f} " + " ".join(parts))
