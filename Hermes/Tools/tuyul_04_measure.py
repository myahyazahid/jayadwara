"""Tuyul K1 — ukur proporsi & landmark dari mesh intake (Blender headless).
  blender --background Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend \
      --python Hermes/Tools/tuyul_04_measure.py
Mencetak profil penampang per ketinggian untuk menentukan posisi sendi (pelvis, spine, neck, head,
jaw, bahu/siku/pergelangan tangan, pinggul/lutut/pergelangan kaki). Tidak mengubah apa pun.
Salinan dari Art/Scripts/jayadwara2_03_measure.py; hanya nama objek/rentang yang diubah.
"""
import numpy as np
import bpy

ob = bpy.data.objects["TY_Source"]
me = ob.data
co = np.array([v.co[:] for v in me.vertices])
print("== PROPORSI (m) ==")
print("tinggi", round(float(co[:, 2].max()), 4), "| lebar X", round(float(co[:, 0].max() - co[:, 0].min()), 4),
      "| dalam Y", round(float(co[:, 1].max() - co[:, 1].min()), 4))

print("== PROFIL PER Z (min/max X, min/max Y) ==")
for z in np.arange(0.99, 0.0, -0.03):
    m = (co[:, 2] >= z - 0.015) & (co[:, 2] < z + 0.015)
    if m.any():
        print(f"  z={z:0.2f} X[{co[m,0].min():+.3f},{co[m,0].max():+.3f}] "
              f"Y[{co[m,1].min():+.3f},{co[m,1].max():+.3f}] n={int(m.sum())}")

print("== SEGMEN X>0 (celah lengan-badan) ==")
for z in np.arange(0.95, 0.05, -0.05):
    m = (co[:, 2] >= z - 0.01) & (co[:, 2] < z + 0.01)
    xs = np.sort(co[m, 0][co[m, 0] > 0.02])
    if len(xs) < 2:
        print(f"  z={z:0.2f} (kosong)")
        continue
    gaps = np.where(np.diff(xs) > 0.02)[0]
    segs, start = [], xs[0]
    for g in gaps:
        segs.append((round(float(start), 3), round(float(xs[g]), 3)))
        start = xs[g + 1]
    segs.append((round(float(start), 3), round(float(xs[-1]), 3)))
    print(f"  z={z:0.2f} {segs}")

print("== SEGMEN X<0 ==")
for z in np.arange(0.95, 0.05, -0.05):
    m = (co[:, 2] >= z - 0.01) & (co[:, 2] < z + 0.01)
    xs = np.sort(co[m, 0][co[m, 0] < -0.02])
    if len(xs) < 2:
        print(f"  z={z:0.2f} (kosong)")
        continue
    gaps = np.where(np.diff(xs) > 0.02)[0]
    segs, start = [], xs[0]
    for g in gaps:
        segs.append((round(float(start), 3), round(float(xs[g]), 3)))
        start = xs[g + 1]
    segs.append((round(float(start), 3), round(float(xs[-1]), 3)))
    print(f"  z={z:0.2f} {segs}")
