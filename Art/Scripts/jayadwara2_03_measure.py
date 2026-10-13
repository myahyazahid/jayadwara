"""Jayadwara2 R0 — ukur pose/proporsi/warna dari model terimpor (Blender headless).
  blender --background Art/Blender/jayadwara2_v01_tripo.blend --python Art/Scripts/jayadwara2_03_measure.py
"""
import colorsys
import numpy as np
import bpy
import bmesh

ob = bpy.data.objects["JD2_Source"]
me = ob.data
co = np.array([v.co[:] for v in me.vertices])
print("== PROPORSI (m) ==")
print("tinggi total", co[:, 2].max().round(3), "lebar maks (X)", (co[:, 0].max() - co[:, 0].min()).round(3),
      "kedalaman (Y)", (co[:, 1].max() - co[:, 1].min()).round(3))
# tinggi helm tanpa tanduk: lihat profil lebar X di pita atas kepala
for z in np.arange(1.99, 1.55, -0.03):
    m = (co[:, 2] >= z - 0.015) & (co[:, 2] < z + 0.015)
    if m.any():
        print(f"  z={z:.2f}  X[{co[m,0].min():+.3f},{co[m,0].max():+.3f}]  Y[{co[m,1].min():+.3f},{co[m,1].max():+.3f}]  n={m.sum()}")
print("== POSE: sebaran X per ketinggian (celah lengan-badan) ==")
for z in (1.50, 1.35, 1.20, 1.05, 0.90, 0.75, 0.55, 0.35, 0.15):
    m = (co[:, 2] >= z - 0.01) & (co[:, 2] < z + 0.01)
    xs = np.sort(co[m, 0][co[m, 0] > 0])
    gaps = np.where(np.diff(xs) > 0.015)[0]
    segs = []
    start = xs[0]
    for g in gaps:
        segs.append((round(start, 3), round(xs[g], 3))); start = xs[g + 1]
    segs.append((round(start, 3), round(xs[-1], 3)))
    print(f"  z={z:.2f} segmen X>0: {segs}")

# tekstur: persentase piksel abu/silver (saturasi rendah, value menengah-tinggi), di luar faceplate
img = next(i for i in bpy.data.images if i.name.startswith("Color_"))
px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)[:, :3]
px = px[::7]
mx, mn = px.max(1), px.min(1)
sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
grey = (sat < 0.12) & (mx > 0.25) & (mx < 0.9)
white = (sat < 0.12) & (mx >= 0.9)
dark = mx <= 0.12
print(f"== TEKSTUR == abu-abu/silver {grey.mean()*100:.2f}% | putih {white.mean()*100:.2f}% | gelap {dark.mean()*100:.1f}%")
# UV: berapa persen atlas terpakai
bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.active
area = 0.0
for f in bm.faces:
    u = [l[uv].uv for l in f.loops]
    area += abs(sum(u[i].x * u[(i+1) % len(u)].y - u[(i+1) % len(u)].x * u[i].y for i in range(len(u)))) / 2
print(f"== UV == luas terpakai {area*100:.1f}% dari atlas (jika >100% ada tumpang tindih)")
bm.free()
