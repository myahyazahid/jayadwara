"""K4.2d - Cari merah KETAT di atlas ASLI (mata + urat) vs peta merah longgar K2.

  python Hermes/Tools/tuyul_44_red_probe.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
ART = ROOT / "Hermes" / "Art" / "tuyul"
pos = np.load(ART / "Render" / "k4" / "uv_pos.npy")
valid = ~np.isnan(pos[:, :, 2])
x, y, z = pos[:, :, 0], pos[:, :, 1], pos[:, :, 2]
src = np.asarray(Image.open(ART / "Textures" / "T_Tuyul_Color_src.png").convert("RGB"), dtype=np.float32)
loose = np.asarray(Image.open(ART / "Texture" / "T_Tuyul_RedMask_k2.png").convert("L")) > 128
print("atlas asli:", src.shape, " peta merah K2:", int(loose.sum()))

r, g, b = src[:, :, 0], src[:, :, 1], src[:, :, 2]
mx = src.max(axis=2)
mn = src.min(axis=2)
sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
for nm, m in {
    "longgar (K2): R-max>15 & R>56": loose,
    "ketat A: R>1.35*max(G,B) & R>70": (r > 1.35 * np.maximum(g, b)) & (r > 70),
    "ketat B: + sat>0,35": (r > 1.35 * np.maximum(g, b)) & (r > 70) & (sat > 0.35),
    "ketat C: + sat>0,45": (r > 1.35 * np.maximum(g, b)) & (r > 70) & (sat > 0.45),
}.items():
    n = int((m & valid).sum())
    print(f"  {nm:34s} {n:8d}  ({100*n/max(1,int(valid.sum())):.2f}% permukaan)")

ketat = (r > 1.35 * np.maximum(g, b)) & (r > 70) & (sat > 0.35) & valid
Z = {
    "ubun-ubun": (z > 0.925) & (np.abs(x) < 0.13) & (np.abs(y) < 0.13),
    "wajah": (z > 0.80) & (y < -0.04),
    "kepala": (z > 0.80),
    "dada": (z > 0.45) & (z < 0.74) & (y < -0.06) & (np.abs(x) < 0.16),
    "lengan": (np.abs(x) > 0.18) & (z > 0.28) & (z < 0.74),
    "pinggul": (z > 0.18) & (z < 0.46) & (np.abs(x) < 0.22),
    "kaki": (z < 0.20),
}
print("\nmerah KETAT (B) per zona:")
for k, m in Z.items():
    print(f"  {k:10s} {int((ketat & m).sum()):7d}")

ri = np.argwhere(ketat)
p3 = pos[ri[:, 0], ri[:, 1]]
print(f"\nsebaran 3D merah ketat: x {p3[:,0].min():+.3f}..{p3[:,0].max():+.3f}  y {p3[:,1].min():+.3f}..{p3[:,1].max():+.3f}  z {p3[:,2].min():+.3f}..{p3[:,2].max():+.3f}")
bins = {}
for xx, yy, zz in p3:
    bins[(round(xx / 0.03), round(yy / 0.03), round(zz / 0.03))] = bins.get((round(xx / 0.03), round(yy / 0.03), round(zz / 0.03)), 0) + 1
print("20 bin 3 cm terpadat:")
for (bx, by, bz), n in sorted(bins.items(), key=lambda kv: -kv[1])[:20]:
    print(f"  x{bx*0.03:+.2f} y{by*0.03:+.2f} z{bz*0.03:+.2f} : {n}")

# warna contoh merah ketat
print("\ncontoh warna merah ketat (median):", np.median(src[ketat], axis=0))
print("contoh warna merah longgar (median):", np.median(src[loose], axis=0))
print("warna kulit non-merah (median):", np.median(src[valid & ~loose], axis=0))
