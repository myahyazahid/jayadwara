"""Jayadwara2 R4 — analisis atlas Tripo: persentase zona warna, texel 'lain' (noda hijau/biru/ungu/abu), lokasi 3D-nya, peta zona.

  python -I Art/Scripts/analyze_atlas_jayadwara2.py            (setelah jayadwara2_15_dump_uv.py)
Keluaran: ringkasan di stdout + Art/Export/_jd2/_atlas_zones.png (kiri atlas asli, kanan peta zona)."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jd2_atlas as A

bc = np.asarray(Image.open(A.TEX / "T_Jayadwara2_BC_src.png").convert("RGB"), np.float32) / 255.0
H, W = bc.shape[:2]
P = A.texel_positions(W, H)
used = ~np.isnan(P[..., 0])
lab = A.zone_labels(bc)
names = ["hitam", "merah", "emas", "putih/krem", "lain"]
print(f"atlas {W}x{H}; texel terpakai {used.mean() * 100:.1f}%")
for i, n in enumerate(names):
    m = used & (lab == i)
    print(f"  {n:11s}: {m.sum():8d} texel ({m.sum() / used.sum() * 100:5.1f}% dari terpakai)")
other = used & (lab == 4)
h, s, v = A.rgb_to_hsv(bc)
print("texel 'lain' per hue (derajat):", {f"{a}-{a + 60}": int((other & (h >= a) & (h < a + 60)).sum()) for a in range(0, 360, 60)}, "| rendah-saturasi:", int((other & (s < 0.3)).sum()))
for nm, mk in (("hijau/biru/ungu (h 62-330, s>0.2)", other & (h >= 62) & (h < 330) & (s > 0.2)), ("abu/silver (s<0.2, v 0.25-0.62)", other & (s < 0.2) & (v >= 0.24) & (v < 0.62))):
    ys, xs = np.where(mk)
    if len(ys) == 0:
        print(f"  {nm}: 0 texel")
        continue
    pp = P[ys, xs]
    print(f"  {nm}: {len(ys)} texel; bbox 3D x[{np.nanmin(pp[:,0]):+.2f},{np.nanmax(pp[:,0]):+.2f}] y[{np.nanmin(pp[:,1]):+.2f},{np.nanmax(pp[:,1]):+.2f}] z[{np.nanmin(pp[:,2]):.2f},{np.nanmax(pp[:,2]):.2f}]; pusat z={np.nanmedian(pp[:,2]):.2f} x={np.nanmedian(pp[:,0]):+.2f}")
pal = np.array([[20, 20, 20], [200, 30, 40], [230, 190, 40], [240, 240, 235], [60, 220, 60]], np.uint8)
zm = pal[lab]
zm[~used] = (70, 70, 70)
Image.fromarray(np.concatenate([(bc * 255).astype(np.uint8), zm], axis=1)).resize((2048, 1024)).save(A.ROOT / "Art" / "Export" / "_jd2" / "_atlas_zones.png")
