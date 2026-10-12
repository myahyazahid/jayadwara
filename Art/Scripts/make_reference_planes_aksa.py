"""Buat referensi ortografis ternormalisasi dari turnaround Aksa (docs/21, Iterasi 0 model Aksa).

Input : docs/concept-art/aksa_turnaround_v01.webp (1774x887: depan, samping hadap kiri, belakang + kepala depan/samping)
Output: Art/Reference/ak_ref_{front,side,back}.png   (RGBA 760x1200, latar transparan)
        Art/Reference/ak_head_{front,side}.png, ak_detail_*.png   (crop apa adanya)
        Art/Reference/ak_palette.png                              (swatch hasil ukur, lihat PALETTE)

Normalisasi: tinggi badan (telapak sepatu -> ujung rambut tertinggi) = 1000 px = 1,75 m, telapak di baris y=1100,
tengah badan di x=380. Ketiga view digambar pada skala dan garis tanah yang sama di sheet (diverifikasi:
garis tanah y=823-824, sol sepatu menjorok ±4 px di bawahnya -> SOLE_Y = 827).
Garis tengah: depan/belakang = rata-rata titik tengah kepala dan bahu; samping = titik tengah pinggul-kaki.

Jalankan: python -I Art/Scripts/make_reference_planes_aksa.py
Catatan: sumber AI beresolusi rendah (±780 px tinggi badan) -> hanya untuk proporsi & siluet.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "concept-art" / "aksa_turnaround_v01.webp"
OUT = ROOT / "Art" / "Reference"
OUT.mkdir(parents=True, exist_ok=True)

BG = 212                       # abu latar sheet
SOLE_Y = 827.0                 # telapak sepatu (sheet)
TOP_Y = 47.0                   # ujung rambut tertinggi (sheet)
H = 1.75
CANVAS_W, CANVAS_H = 760, 1200
BODY_PX = 1000
SOLE_CANVAS_Y = 1100
SCALE = BODY_PX / (SOLE_Y - TOP_Y)

# kotak sempit per figur (sheet): kiri, atas, kanan, bawah
VIEWS = {
    "front": (28, 38, 420, 842),
    "side": (463, 38, 640, 842),
    "back": (695, 38, 1062, 842),
}

# crop apa adanya (sheet)
PLAIN = {
    "head_front": (1100, 160, 1421, 645),
    "head_side": (1436, 175, 1741, 625),
    "detail_collar": (125, 120, 320, 300),       # kerah berbatik + kalung + liontin
    "detail_sash": (130, 340, 360, 620),         # sabuk, simpul & selendang, kantong paha (depan)
    "detail_sash_side": (480, 340, 627, 620),    # selendang dari samping
    "detail_glove": (22, 385, 125, 505),
    "detail_boot_front": (55, 700, 170, 835),
    "detail_boot_side": (463, 700, 627, 840),
    "detail_leg": (95, 440, 270, 700),           # kantong kargo + strap paha
    "detail_emblem": (780, 150, 980, 320),       # emblem punggung + garis jahit
}

# swatch palet (sheet): nama -> (kotak, filter opsional). Hasil ukur ditulis ke docs/21 bagian 3.
PALETTE = {
    "jaket_navy": ((80, 200, 345, 370), lambda p: (p[:, 2] - p[:, 0] > 6) & (p.sum(axis=1) < 330)),
    "kaos_hitam": ((200, 250, 260, 340), lambda p: p.sum(axis=1) < 200),
    "celana": ((100, 440, 330, 700), lambda p: p.sum(axis=1) < 260),
    "kulit": ((50, 330, 110, 400), lambda p: (p[:, 0] - p[:, 2] > 45) & (p[:, 0] > 130)),
    "rambut": ((180, 50, 260, 100), lambda p: p.sum(axis=1) < 200),
    "batik": ((235, 400, 300, 570), lambda p: (p[:, 0] - p[:, 2] > 35) & (p[:, 0] < 200) & (p[:, 0] > 70)),
    "emas": ((855, 190, 905, 230), lambda p: (p[:, 0] > 140) & (p[:, 0] - p[:, 2] > 60)),
    "sepatu": ((60, 700, 420, 826), lambda p: p.sum(axis=1) < 200),
}

sheet = Image.open(SRC).convert("RGB")
arr = np.asarray(sheet).astype(int)


def figure_mask(box):
    """Mask figur: piksel beda dari latar; garis tanah tipis dibuang (opening vertikal); lubang diisi; komponen terbesar."""
    l, t, r, b = box
    dist = np.abs(arr - BG).sum(axis=2) > 45
    m = np.zeros_like(dist)
    m[t:b, l:r] = dist[t:b, l:r]
    m = ndi.binary_opening(m, structure=np.ones((5, 1)))
    m = ndi.binary_closing(m, structure=np.ones((3, 3)), iterations=2)
    m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m)
    if n > 1:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        m = lab == (1 + int(np.argmax(sizes)))
    return m


def mid_of_rows(mask, y0, y1):
    """Titik tengah ekstrem kiri-kanan, dirata-ratakan di baris y0..y1."""
    mids = []
    for y in range(y0, y1 + 1):
        xs = np.where(mask[y])[0]
        if len(xs):
            mids.append((xs.min() + xs.max()) / 2.0)
    return float(np.mean(mids))


def body_center_x(mask, name):
    if name == "side":      # pinggul sampai betis: tidak terpengaruh lengan/selendang yang menjulur
        return mid_of_rows(mask, 380, 600)
    return (mid_of_rows(mask, 85, 115) + mid_of_rows(mask, 215, 260)) / 2.0     # kepala + bahu


report = []
for name, box in VIEWS.items():
    mask = figure_mask(box)
    cx = body_center_x(mask, name)
    inv = 1.0 / SCALE                        # affine (output -> input)
    coeffs = (inv, 0, cx - (CANVAS_W / 2) * inv, 0, inv, SOLE_Y - SOLE_CANVAS_Y * inv)
    rgb = sheet.transform((CANVAS_W, CANVAS_H), Image.AFFINE, coeffs, resample=Image.BICUBIC, fillcolor=(BG, BG, BG))
    m_img = Image.fromarray((mask * 255).astype(np.uint8)).transform(
        (CANVAS_W, CANVAS_H), Image.AFFINE, coeffs, resample=Image.BILINEAR, fillcolor=0)
    m_img = m_img.filter(ImageFilter.GaussianBlur(1.2)).point(
        lambda v: 255 if v > 200 else (0 if v < 40 else int((v - 40) * 255 / 160)))
    out = rgb.convert("RGBA")
    out.putalpha(m_img)
    out.save(OUT / f"ak_ref_{name}.png")
    ys, xs = np.where(np.asarray(m_img) > 128)
    report.append((name, round(cx, 1), (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))))

for name, box in PLAIN.items():
    sheet.crop(box).save(OUT / f"ak_{name}.png")

# swatch palet
sw = Image.new("RGB", (len(PALETTE) * 120, 150), (230, 230, 230))
d = ImageDraw.Draw(sw)
hexes = {}
for i, (k, (box, f)) in enumerate(PALETTE.items()):
    l, t, r, b = box
    p = arr[t:b, l:r].reshape(-1, 3)
    p = p[f(p)]
    med = np.median(p, axis=0).astype(int)
    hexes[k] = "#%02X%02X%02X" % tuple(med)
    d.rectangle([i * 120 + 8, 8, i * 120 + 112, 100], fill=tuple(int(v) for v in med))
    d.text((i * 120 + 8, 108), k, fill=(0, 0, 0))
    d.text((i * 120 + 8, 124), hexes[k], fill=(0, 0, 0))
sw.save(OUT / "ak_palette.png")

print(f"skala = {SCALE:.3f} px kanvas per px sheet  ({H * 1000 / (SOLE_Y - TOP_Y):.3f} mm per px sheet)")
for name, cx, bb in report:
    print(f"ref {name:5s} pusat x sheet={cx:6.1f}  bbox alfa (x0,y0,x1,y1)={bb}")
print("palet (median piksel terfilter):", hexes)
