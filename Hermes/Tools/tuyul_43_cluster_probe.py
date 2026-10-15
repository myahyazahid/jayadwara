"""K4.2c - Klasterkan warna per zona (cari koin kuningan, mata, gigi) + peta merah per zona.

  python Hermes/Tools/tuyul_43_cluster_probe.py
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
red = np.asarray(Image.open(ART / "Texture" / "T_Tuyul_RedMask_k2.png").convert("L")) > 128

Z = {
    "ubun-ubun": valid & (z > 0.925) & (np.abs(x) < 0.13) & (np.abs(y) < 0.13),
    "wajah": valid & (z > 0.80) & (y < -0.04),
    "leher": valid & (z > 0.74) & (z <= 0.82) & (np.abs(x) < 0.14),
    "dada": valid & (z > 0.45) & (z < 0.74) & (y < -0.06) & (np.abs(x) < 0.16),
    "lengan": valid & (np.abs(x) > 0.18) & (z > 0.28) & (z < 0.74),
    "pinggul": valid & (z > 0.18) & (z < 0.46) & (np.abs(x) < 0.22),
}
print("zona / texel / merah(%)")
for k, m in Z.items():
    print(f"  {k:10s} {int(m.sum()):8d}  merah {100*(red&m).sum()/max(1,m.sum()):5.1f}%")


def kmeans(P, k=7, iters=14, seed=0):
    rng = np.random.default_rng(seed)
    C = P[rng.choice(len(P), k, replace=False)].copy()
    for _ in range(iters):
        d = ((P[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
        lab = d.argmin(axis=1)
        for j in range(k):
            if (lab == j).any():
                C[j] = P[lab == j].mean(axis=0)
    return C, lab


rng = np.random.default_rng(1)
for zn in ["wajah", "leher", "dada", "pinggul"]:
    m = Z[zn]
    idx = np.argwhere(m)
    if len(idx) > 120000:
        idx = idx[rng.choice(len(idx), 120000, replace=False)]
    P = col[idx[:, 0], idx[:, 1]]
    C, lab = kmeans(P, k=7)
    print(f"\n== klaster zona {zn} (n={len(P)}) ==")
    for j in np.argsort(-np.bincount(lab, minlength=7)):
        sel = idx[lab == j]
        if len(sel) == 0:
            continue
        c = C[j]
        p3 = np.nanmean(pos[sel[:, 0], sel[:, 1]], axis=0)
        print(f"  #{int(c[0]):02X}{int(c[1]):02X}{int(c[2]):02X}  {100*(lab==j).mean():5.1f}%  n={len(sel):6d}  pos x{p3[0]:+.2f} y{p3[1]:+.2f} z{p3[2]:+.2f}")

# di mana saja merah berada (posisi 3D rata2)
ri = np.argwhere(red & valid)
p3 = pos[ri[:, 0], ri[:, 1]]
print("\n== merah: sebaran 3D ==")
print(f"  n={len(ri)}  x {np.percentile(p3[:,0],5):+.2f}..{np.percentile(p3[:,0],95):+.2f}  y {np.percentile(p3[:,1],5):+.2f}..{np.percentile(p3[:,1],95):+.2f}  z {np.percentile(p3[:,2],5):+.2f}..{np.percentile(p3[:,2],95):+.2f}")
zb = {}
for xx, zz in zip(p3[:, 0], p3[:, 2]):
    k = (round(xx / 0.05), round(zz / 0.05))
    zb[k] = zb.get(k, 0) + 1
print("  bin x/z terpadat (5 cm):", sorted(zb.items(), key=lambda kv: -kv[1])[:10])
