"""Jubah Jayadwara2 J2 — T_Jayadwara2_Cape_Mask (RGBA zona warna untuk recolor di MI) + _Mask.json (docs/26 J2).

  python -I Art/Scripts/make_textures_jayadwara2_cape.py        (setelah jayadwara2_cape_14_export.py menulis T_Jayadwara2_Cape_BC.png)
Kanal sama dengan badan (M_Jayadwara2_Master / M_Jayadwara2_Cape_Master): R merah, G emas, B hitam, A putih/krem.
Klasifikasi warna = jd2_atlas.zone_labels (sama dengan badan). Jubah tidak punya zona hitam di desainnya: texel gelap
(lipatan merah dalam bayangan) & "lain" dimasukkan ke MERAH supaya recolor merah ikut mewarnai lipatan. B = 0.
Tepi dilembutkan (blur 1,2 px) dan dinormalisasi (jumlah kanal = 1). Bagian ornamen skrip (bros, rantai, yoke lama)
memakai titik atlas bersih, jadi ikut zonanya otomatis.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jd2_atlas as A  # noqa: E402

ROOT = HERE.parents[1]
TEX = ROOT / "Art" / "Export" / "Textures_Jayadwara2_Cape"
bc = np.asarray(Image.open(TEX / "T_Jayadwara2_Cape_BC.png").convert("RGB"), np.float32) / 255.0
lab = A.zone_labels(bc)
red = (lab == 1) | (lab == 0) | (lab == 4)
gold = lab == 2
white = lab == 3
ch = []
for m in (red, gold, np.zeros_like(red), white):
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    ch.append(np.asarray(im, np.float32) / 255.0)
M = np.stack(ch, axis=-1)
M /= np.maximum(M.sum(axis=-1, keepdims=True), 1e-6)
Image.fromarray((M * 255 + 0.5).astype(np.uint8), "RGBA").save(TEX / "T_Jayadwara2_Cape_Mask.png")


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


bl = lin(bc)
luma = bl @ np.array([0.2126, 0.7152, 0.0722], np.float32)
info = {}
for k, n in enumerate(("red", "gold", "black", "white")):
    w = M[..., k]
    tot = float(w.sum()) or 1.0
    info[n] = {"texel_share": round(float(w.mean()), 4),
               "ref_luma_linear": round(float((luma * w).sum() / tot), 4),
               "mean_color_linear": [round(float((bl[..., c] * w).sum() / tot), 4) for c in range(3)]}
json.dump(info, open(TEX / "T_Jayadwara2_Cape_Mask.json", "w"), indent=2)
dbg = np.zeros_like(bc)
dbg[..., 0] = M[..., 0]
dbg[..., 1] = M[..., 1] * 0.8
dbg[..., 2] = M[..., 3]
Image.fromarray((dbg * 255).astype(np.uint8)).resize((1024, 1024)).save(ROOT / "Art" / "Export" / "_jd2c" / "_mask_debug.png")
print("zona:", {k: (v["texel_share"], v["ref_luma_linear"]) for k, v in info.items()})
