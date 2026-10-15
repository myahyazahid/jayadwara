"""K2.4 - Analisis tekstur warna: porsi piksel merah (calon 'merah basah').

  blender --background <blend> --python Hermes/Tools/tuyul_25_tex_audit.py -- <outdir>

Daftar image di blend, lalu untuk gambar warna terbesar hitung:
  - porsi piksel "merah" (R > 0.30 dan R > 1.4*G dan R > 1.4*B)
  - porsi "sangat merah" (R > 0.55, G < 0.25, B < 0.25)
Simpan pratinjau mask (putih=merah) ke <outdir>/tex_red_mask.png.
"""
import sys
from pathlib import Path
import numpy as np
import bpy

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(a[0]) if a else ROOT / "Hermes" / "Art" / "tuyul" / "Render" / "k2"
if not OUT.is_absolute():
    OUT = ROOT / OUT
OUT.mkdir(parents=True, exist_ok=True)

print("=== IMAGE di blend ===")
cand = []
for im in bpy.data.images:
    n = im.size[0] * im.size[1]
    print(f"  {im.name:40s} {im.size[0]}x{im.size[1]} px={n} packed={bool(im.packed_file)}")
    if im.size[0] > 0:
        cand.append((n, im))
if not cand:
    raise SystemExit("tidak ada image")
cand.sort(key=lambda t: -t[0])
img = cand[0][1]
w, h = img.size
print(f"\n=== analisis: {img.name} {w}x{h} ===")

px = np.empty(w * h * 4, dtype=np.float32)
img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)
r, g, b = px[..., 0], px[..., 1], px[..., 2]

red = (r > 0.30) & (r > 1.4 * g) & (r > 1.4 * b)
deep = (r > 0.55) & (g < 0.25) & (b < 0.25)
tot = w * h
print(f"piksel merah       : {int(red.sum())} ({100*red.sum()/tot:.2f}%)")
print(f"piksel sangat merah: {int(deep.sum())} ({100*deep.sum()/tot:.2f}%)")
print(f"rata-rata RGB semua: R={r.mean():.3f} G={g.mean():.3f} B={b.mean():.3f}")

# pratinjau mask (putih = merah)
mask = np.zeros((h, w, 4), dtype=np.float32)
mask[..., 3] = 1.0
mask[red] = (1, 1, 1, 1)
mimg = bpy.data.images.new("redmask", width=w, height=h, alpha=True)
mimg.pixels.foreach_set(mask.reshape(-1))
mimg.filepath_raw = str(OUT / "tex_red_mask.png")
mimg.file_format = "PNG"
mimg.save()
print("mask ->", OUT / "tex_red_mask.png")
