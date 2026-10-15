"""Tuyul K1 — telusuri garis pusat badan/lengan/kaki per ketinggian (Blender headless).
  blender --background Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend \
      --python Hermes/Tools/tuyul_05_centerlines.py
Untuk tiap irisan-z: kelompokkan vertex menurut celah X (>2 cm) -> cluster.
Cetak (xmin,xmax,xc, ymin,ymax,yc, n) tiap cluster supaya garis sendi (spine, lengan, kaki) bisa ditelusuri.
Tidak mengubah apa pun.
"""
import numpy as np
import bpy

ob = bpy.data.objects["TY_Source"]
co = np.array([v.co[:] for v in ob.data.vertices])

for z in np.arange(0.99, 0.005, -0.02):
    m = (co[:, 2] >= z - 0.012) & (co[:, 2] < z + 0.012)
    if not m.any():
        continue
    xs = np.sort(co[m, 0])
    gaps = np.where(np.diff(xs) > 0.025)[0]
    bounds = [0] + list(gaps + 1) + [len(xs)]
    parts = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        lo, hi = xs[a], xs[b - 1]
        sel = co[m][(co[m, 0] >= lo - 1e-6) & (co[m, 0] <= hi + 1e-6)]
        parts.append(f"[x{lo:+.3f}..{hi:+.3f} xc{(lo+hi)/2:+.3f} yc{sel[:,1].mean():+.3f} "
                     f"y[{sel[:,1].min():+.3f},{sel[:,1].max():+.3f}] n{len(sel)}]")
    print(f"z={z:0.2f} " + " ".join(parts))
