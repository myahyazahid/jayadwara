"""Buat referensi ortografis ternormalisasi dari sheet konsep Jayadwara.

Input : docs/concept-art/jayadwara_final.webp (1530x1028)
Output: Art/Reference/jd_ref_{front,side,back,34}.png  (RGBA, 760x1200, latar transparan)
        Art/Reference/jd_{head_detail,detail_*,hero_pose,palette}.png  (crop apa adanya)

Normalisasi: tinggi badan (telapak kaki -> puncak helm, TANPA tanduk) = 1000 px = 1,9 m,
telapak kaki di baris y=1100, figur dipusatkan di x=380. Semua view memakai skala yang sama
(sheet menggambar keempat view pada skala yang sama: tanduk teratas dan telapak kaki sejajar).

Jalankan: python -I Art/Scripts/make_reference_planes.py
Catatan: ini sumber AI beresolusi rendah (±360 px tinggi badan) -> hanya untuk proporsi & siluet.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "concept-art" / "jayadwara_final.webp"
OUT = ROOT / "Art" / "Reference"
OUT.mkdir(parents=True, exist_ok=True)

BG = 233                       # abu latar sheet
SOLE_Y = 454.5                 # y telapak kaki pada sheet (60 + 394.5)
CROWN_Y = 93.0                 # y puncak helm tanpa tanduk pada sheet (60 + 33)
CANVAS_W, CANVAS_H = 760, 1200
BODY_PX = 1000                 # tinggi badan di kanvas
SOLE_CANVAS_Y = 1100
SCALE = BODY_PX / (SOLE_Y - CROWN_Y)

# kotak sempit per figur (koordinat sheet): kiri, atas, kanan, bawah
VIEWS = {
    "front": (652, 60, 810, 470),
    "side": (833, 60, 945, 470),
    "back": (944, 60, 1095, 470),
    "34": (1100, 60, 1225, 470),
}

# crop apa adanya (koordinat sheet)
PLAIN = {
    "head_detail": (1245, 55, 1510, 400),
    "detail_chest": (760, 535, 932, 715),
    "detail_shoulder": (942, 535, 1115, 715),
    "detail_belt": (1125, 535, 1315, 715),
    "detail_leg": (1328, 535, 1505, 715),
    "hero_pose": (25, 85, 725, 940),
    "palette": (765, 840, 1000, 930),
}

sheet = Image.open(SRC).convert("RGB")
arr = np.asarray(sheet).astype(int)


def figure_mask(box):
    """Mask figur di dalam box: piksel beda dari latar, lubang diisi (faceplate putih), komponen terbesar."""
    l, t, r, b = box
    dist = np.abs(arr - BG).sum(axis=2) > 45
    m = np.zeros_like(dist)
    m[t:b, l:r] = dist[t:b, l:r]
    m[:, : l + 6] = False   # garis tepi panel / sliver tetangga tepat di tepi kotak
    m = ndi.binary_closing(m, structure=np.ones((3, 3)), iterations=2)
    m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m)
    if n > 1:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        m = lab == (1 + int(np.argmax(sizes)))
    return m


def body_center_x(mask, name):
    ys, xs = np.where(mask)
    if name == "side":  # garis tengah badan di tinggi dada-pinggul, bukan bbox (selendang asimetris)
        rows = (np.arange(mask.shape[0]) >= 60 + 90) & (np.arange(mask.shape[0]) <= 60 + 225)
        sel = mask & rows[:, None]
        return float(np.where(sel)[1].mean())
    return (xs.min() + xs.max()) / 2.0


report = []
for name, box in VIEWS.items():
    mask = figure_mask(box)
    cx = body_center_x(mask, name)
    # affine (output -> input): x_in = a*u + b*v + c ; y_in = d*u + e*v + f
    inv = 1.0 / SCALE
    c = cx - (CANVAS_W / 2) * inv
    f = SOLE_Y - SOLE_CANVAS_Y * inv
    coeffs = (inv, 0, c, 0, inv, f)
    rgb = sheet.transform((CANVAS_W, CANVAS_H), Image.AFFINE, coeffs, resample=Image.BICUBIC, fillcolor=(BG, BG, BG))
    m_img = Image.fromarray((mask * 255).astype(np.uint8)).transform(
        (CANVAS_W, CANVAS_H), Image.AFFINE, coeffs, resample=Image.BILINEAR, fillcolor=0
    )
    m_img = m_img.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 200 else (0 if v < 40 else int((v - 40) * 255 / 160)))
    out = rgb.convert("RGBA")
    out.putalpha(m_img)
    out.save(OUT / f"jd_ref_{name}.png")
    ys, xs = np.where(np.asarray(m_img) > 128)
    report.append((name, round(cx, 1), (xs.min(), ys.min(), xs.max(), ys.max())))

for name, box in PLAIN.items():
    sheet.crop(box).save(OUT / f"jd_{name}.png")

print(f"skala = {SCALE:.3f} px kanvas per px sheet")
for name, cx, bb in report:
    print(f"ref {name:5s} pusat x sheet={cx:6.1f}  bbox alfa (x0,y0,x1,y1)={bb}")
