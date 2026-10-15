"""K4.2b - Probe ornamen/koin: cari texel keemasan, petakan ke posisi 3D, klasterkan.

  python Hermes/Tools/tuyul_42_ornament_probe.py

Butuh uv_pos.npy (dari tuyul_41_uv3d.py). Membaca atlas sRGB apa adanya lewat PIL.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
ART = ROOT / "Hermes" / "Art" / "tuyul"

pos = np.load(ART / "Render" / "k4" / "uv_pos.npy")
valid = ~np.isnan(pos[:, :, 2])
x, y, z = pos[:, :, 0], pos[:, :, 1], pos[:, :, 2]

col = np.asarray(Image.open(ART / "Textures" / "T_Tuyul_Color.png").convert("RGB"), dtype=np.float32)
H, W = col.shape[:2]
print("atlas", W, "x", H, " terisi", f"{100*valid.sum()/(W*H):.2f}%")

mx = col.max(axis=2)
mn = col.min(axis=2)
sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
r, g, b = col[:, :, 0], col[:, :, 1], col[:, :, 2]

emas = valid & (sat > 0.25) & (r > b) & (g > b) & (mx > 90)
print(f"texel keemasan (sat>0,25, R>B, G>B, V>90): {int(emas.sum())} ({100*emas.sum()/(W*H):.3f}%)")
for nm, m in {
    "kepala": (z > 0.80), "wajah": (z > 0.80) & (y < -0.04), "dada": (z > 0.45) & (z < 0.74) & (y < -0.06) & (np.abs(x) < 0.16),
    "lengan": (np.abs(x) > 0.18) & (z > 0.28) & (z < 0.74), "pinggul": (z > 0.18) & (z < 0.46) & (np.abs(x) < 0.22), "kaki": (z < 0.20),
}.items():
    print(f"  emas di {nm:8s}: {int((emas & valid & m).sum()):8d}")

# klaster 3D: bin 5 cm
ex, ey, ez = x[emas], y[emas], z[emas]
print(f"\nsebaran posisi texel emas: x {ex.min():.3f}..{ex.max():.3f}  y {ey.min():.3f}..{ey.max():.3f}  z {ez.min():.3f}..{ez.max():.3f}")
bins = {}
for xx, yy, zz in zip(ex, ey, ez):
    k = (round(xx / 0.05), round(yy / 0.05), round(zz / 0.05))
    bins[k] = bins.get(k, 0) + 1
top = sorted(bins.items(), key=lambda kv: -kv[1])[:18]
print("18 bin terpadat (5 cm):")
for (bx, by, bz), n in top:
    print(f"  x{bx*0.05:+.2f} y{by*0.05:+.2f} z{bz*0.05:+.2f} : {n} texel")

# warna contoh di klaster terpadat
bx, by, bz = top[0][0]
m = (np.abs(ex - bx * 0.05) < 0.025) & (np.abs(ey - by * 0.05) < 0.025) & (np.abs(ez - bz * 0.05) < 0.025)
print("\ncontoh warna di klaster terpadat (median):", np.median(col[emas][m], axis=0))

# ---- warna kulit vs palet, di texel yang BUKAN merah & BUKAN emas
red = np.asarray(Image.open(ART / "Texture" / "T_Tuyul_RedMask_k2.png").convert("L")) > 128
kulit = valid & ~red & ~emas
print(f"\ntexel kulit (bukan merah, bukan emas): {int(kulit.sum())}")
med = np.median(col[kulit], axis=0)
print("kulit median sRGB:", "#" + "".join(f"{int(v):02X}" for v in med), " (palet usulan #8E9A8B)")
