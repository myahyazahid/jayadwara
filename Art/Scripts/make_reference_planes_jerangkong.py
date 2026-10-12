"""Buat referensi ortografis ternormalisasi dari konsep Jerangkong (docs/20 & docs/24, Iterasi 0 model Jerangkong).

Input : docs/concept-art/jerangkong_v01.webp (1774x887: depan, samping hadap kiri, belakang + tengkorak 3/4 + chart skala)
Output: Art/Reference/jk_ref_{front,side,back}.png   (RGBA 900x1200, latar transparan)
        Art/Reference/jk_head_34.png, jk_scale_chart.png, jk_detail_*.png   (crop apa adanya)
        Art/Reference/jk_palette.png                                         (swatch hasil ukur, lihat PALETTE)

Normalisasi: tinggi konsep (telapak -> puncak tengkorak di tampak depan) = 1000 px = 2,2 m, telapak di baris y=1100,
garis tengah di x=450. Ketiga view digambar pada skala dan garis tanah yang sama di sheet (garis tanah y=827-829,
puncak tengkorak y=55-57 di ketiga view).
Garis tengah: depan/belakang = rata-rata titik tengah tengkorak dan kedua telapak; samping = titik tengah pergelangan kaki
(tengkorak & lengan menggantung jauh ke depan, jadi tidak dipakai).

PENTING: tampak samping = postur konsep apa adanya (bungkuk berlebihan, tengkorak ±0,47 m di depan pinggul).
Model memakai "bungkuk sedang" (docs/24 S2); target posisi tengkorak ditandai landmark di scene, bukan di gambar.

Jalankan: python -I Art/Scripts/make_reference_planes_jerangkong.py
Catatan: sumber AI beresolusi rendah (±770 px tinggi figur, 1 px sheet ≈ 2,9 mm) -> hanya untuk proporsi & siluet.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "concept-art" / "jerangkong_v01.webp"
OUT = ROOT / "Art" / "Reference"
OUT.mkdir(parents=True, exist_ok=True)

SOLE_Y = 827.0                 # telapak / garis tanah (sheet)
TOP_Y = 57.0                   # puncak tengkorak tampak depan (sheet)
H = 2.2
CANVAS_W, CANVAS_H = 900, 1200
BODY_PX = 1000
SOLE_CANVAS_Y = 1100
SCALE = BODY_PX / (SOLE_Y - TOP_Y)
HOLE_MAX = 600                 # px sheet; lubang lebih besar (celah lengan-badan-kaki) tetap transparan

# kotak sempit per figur (sheet): kiri, atas, kanan, bawah (bawah = di atas bayangan garis tanah)
VIEWS = {
    "front": (28, 40, 458, 827),
    "side": (498, 40, 775, 827),
    "back": (798, 40, 1222, 827),
}

# crop apa adanya (sheet)
PLAIN = {
    "head_34": (1277, 40, 1683, 540),             # tengkorak 3/4 close-up (titik lemah, retak, pecahan batu, akar)
    "scale_chart": (1350, 545, 1700, 845),        # skala vs Jayadwara (konsep ±0,85x; model 0,7x)
    "detail_skull_front": (185, 45, 305, 195),
    "detail_skull_side": (500, 45, 640, 200),
    "detail_ribcage": (140, 105, 350, 345),       # pelat rusuk + tulang dada + energi di sela rusuk
    "detail_spine_back": (890, 95, 1130, 360),    # ruas belakang + energi + tulang belikat
    "detail_pelvis_cloth": (160, 315, 345, 660),  # panggul, simpul kain, kain batik depan
    "detail_cloth_back": (865, 315, 1105, 705),
    "detail_cloth_side": (630, 330, 775, 630),
    "detail_arm_bracelet": (340, 205, 425, 295),  # gelang lengan atas (perunggu patina + ornamen)
    "detail_wrist_bracelet": (385, 495, 455, 565),
    "detail_hand": (30, 520, 125, 700),
    "detail_hand_side": (525, 540, 615, 720),
    "detail_knee": (115, 520, 185, 600),          # lutut + inti energi
    "detail_foot_front": (55, 735, 205, 830),     # kaki menggumpal tanah
    "detail_foot_side": (540, 735, 755, 830),
}

# swatch palet (sheet): nama -> (kotak, filter). Hasil ukur ditulis ke docs/24 bagian 3.
PALETTE = {
    "tulang_terang": ((50, 300, 115, 520), lambda p: (p[:, 0] > 165) & (p[:, 0] - p[:, 2] > 20) & (p[:, 0] - p[:, 2] < 75)),
    "tulang_gelap": ((50, 300, 115, 520), lambda p: (p[:, 0] > 95) & (p[:, 0] < 150) & (p[:, 0] - p[:, 2] > 20)),
    "tanah": ((60, 760, 200, 826), lambda p: (p[:, 0] < 120) & (p[:, 0] - p[:, 2] > 12) & (p[:, 1] >= p[:, 2])),
    "lumut": ((28, 40, 458, 827), lambda p: (p[:, 1] > p[:, 0] + 3) & (p[:, 1] > p[:, 2] + 20)),
    "kain_dasar": ((200, 380, 290, 600), lambda p: (p.sum(axis=1) < 200) & (p[:, 0] >= p[:, 2])),
    "batik_motif": ((200, 380, 290, 600), lambda p: (p[:, 0] > 140) & (p[:, 0] - p[:, 2] > 55)),
    "perunggu": ((30, 510, 85, 550), lambda p: (p[:, 1] >= p[:, 0] - 8) & (p[:, 2] > 60) & (p.sum(axis=1) < 400)),
    "kala_merah": ((195, 110, 285, 145), lambda p: (p[:, 0] > 170) & (p[:, 1] < 90) & (p[:, 2] < 90)),
}

sheet = Image.open(SRC).convert("RGB")
arr = np.asarray(sheet).astype(int)
# latar sedikit bergradasi (183-184); ambil per baris dari celah kosong di antara figur
BG_ROW = np.median(arr[:, 470:495], axis=1)


def figure_mask(box):
    """Mask figur: piksel beda dari latar; hanya lubang kecil diisi (sela rusuk), celah lengan-badan tetap; komponen terbesar."""
    l, t, r, b = box
    dist = np.abs(arr - BG_ROW[:, None, :]).sum(axis=2) > 40
    m = np.zeros_like(dist)
    m[t:b, l:r] = dist[t:b, l:r]
    m = ndi.binary_opening(m, structure=np.ones((3, 3)))
    m = ndi.binary_closing(m, structure=np.ones((3, 3)), iterations=2)
    holes = ndi.binary_fill_holes(m) & ~m
    hl, hn = ndi.label(holes)
    if hn:
        hsz = ndi.sum(holes, hl, range(1, hn + 1))
        m |= np.isin(hl, 1 + np.where(hsz < HOLE_MAX)[0])
    lab, n = ndi.label(m)
    if n > 1:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        m = lab == (1 + int(np.argmax(sizes)))
    return m


def mid_of_rows(mask, y0, y1, x0=None, x1=None):
    """Titik tengah ekstrem kiri-kanan (opsional dibatasi kolom x0..x1), dirata-ratakan di baris y0..y1."""
    mids = []
    for y in range(y0, y1 + 1):
        row = mask[y].copy()
        if x0 is not None:
            row[:x0] = False
            row[x1:] = False
        xs = np.where(row)[0]
        if len(xs):
            mids.append((xs.min() + xs.max()) / 2.0)
    return float(np.mean(mids))


def body_center_x(mask, name, box):
    if name == "side":      # pergelangan kaki (tengkorak & lengan menggantung ke depan)
        return mid_of_rows(mask, 745, 775, box[0] + 130, box[2])
    # tengkorak (di atas bahu) + titik tengah kedua telapak (figur sedikit asimetris; lumbar tertutup lengan/kain)
    skull = mid_of_rows(mask, 60, 100)
    feet = mid_of_rows(mask, 805, 822)
    return (skull + feet) / 2.0


report = []
for name, box in VIEWS.items():
    mask = figure_mask(box)
    cx = body_center_x(mask, name, box)
    inv = 1.0 / SCALE                        # affine (output -> input)
    coeffs = (inv, 0, cx - (CANVAS_W / 2) * inv, 0, inv, SOLE_Y - SOLE_CANVAS_Y * inv)
    rgb = sheet.transform((CANVAS_W, CANVAS_H), Image.AFFINE, coeffs, resample=Image.BICUBIC, fillcolor=(184, 184, 184))
    m_img = Image.fromarray((mask * 255).astype(np.uint8)).transform(
        (CANVAS_W, CANVAS_H), Image.AFFINE, coeffs, resample=Image.BILINEAR, fillcolor=0)
    m_img = m_img.filter(ImageFilter.GaussianBlur(1.2)).point(
        lambda v: 255 if v > 200 else (0 if v < 40 else int((v - 40) * 255 / 160)))
    out = rgb.convert("RGBA")
    out.putalpha(m_img)
    out.save(OUT / f"jk_ref_{name}.png")
    ys, xs = np.where(np.asarray(m_img) > 128)
    report.append((name, round(cx, 1), (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))))

for name, box in PLAIN.items():
    sheet.crop(box).save(OUT / f"jk_{name}.png")

# swatch palet: shadow (p20) / mid (median) / highlight (p80)
sw = Image.new("RGB", (len(PALETTE) * 120, 170), (230, 230, 230))
d = ImageDraw.Draw(sw)
hexes = {}
for i, (k, (box, f)) in enumerate(PALETTE.items()):
    l, t, r, b = box
    p = arr[t:b, l:r].reshape(-1, 3)
    p = p[f(p)]
    lum = p @ np.array([0.299, 0.587, 0.114])
    order = np.argsort(lum)
    pick = lambda q: p[order[int(q * (len(p) - 1))]]                      # noqa: E731
    med = np.median(p, axis=0).astype(int)
    hx = lambda c: "#%02X%02X%02X" % tuple(int(v) for v in c)             # noqa: E731
    hexes[k] = (hx(pick(0.2)), hx(med), hx(pick(0.8)), len(p))
    d.rectangle([i * 120 + 8, 8, i * 120 + 112, 100], fill=tuple(int(v) for v in med))
    d.text((i * 120 + 8, 108), k, fill=(0, 0, 0))
    d.text((i * 120 + 8, 124), hexes[k][1], fill=(0, 0, 0))
    d.text((i * 120 + 8, 140), f"n={len(p)}", fill=(80, 80, 80))
sw.save(OUT / "jk_palette.png")

print(f"skala = {SCALE:.3f} px kanvas per px sheet  ({H * 1000 / (SOLE_Y - TOP_Y):.3f} mm per px sheet)")
for name, cx, bb in report:
    print(f"ref {name:5s} pusat x sheet={cx:6.1f}  bbox alfa (x0,y0,x1,y1)={bb}")
print("palet (p20 / median / p80, n):")
for k, v in hexes.items():
    print(f"  {k:14s} {v}")
