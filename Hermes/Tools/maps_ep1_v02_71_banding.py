"""V7 — lembar perbandingan C4 v01 vs v02 (berdampingan) -> Render/banding_C4_v01_v02.png.

Input (read-only, tidak diubah):
  v01: Hermes/Art/maps_ep1/Render/C4_MataJayadwara_senja.png
  v02: Hermes/Art/maps_ep1/v02/Render/C4_MataJayadwara_senja.png
Output: Hermes/Art/maps_ep1/v02/Render/banding_C4_v01_v02.png

Pakai (dari WORKTREE): python -X utf8 -I Hermes/Tools/maps_ep1_v02_71_banding.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
V01 = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "Render", "C4_MataJayadwara_senja.png")
V02 = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Render", "C4_MataJayadwara_senja.png")
OUT = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Render", "banding_C4_v01_v02.png")

W_PANEL = 1280
H_PANEL = 720
H_HEAD = 74
H_LABEL = 112
H_FOOT = 132
BAR = (18, 18, 22)
FG = (238, 238, 238)
FG2 = (255, 214, 120)

KIRI = [
    "v01  ·  medan 800 x 700 m  ·  arena 530 x 550 m",
    "plato candi 120 m  ·  galian 120 x 100 m  ·  START di garis polisi (bukit)",
    "C4 dari (0, 225) tinggi 42 m, fov 70, cahaya senja",
]
KANAN = [
    "v02  ·  medan 1400 x 1220 m  ·  arena 1190 x 1025 m",
    "plato candi 200 m  ·  galian 220 x 190 m  ·  START di desa (mobil DWARA)",
    "C4 dari (0, 225) tinggi 42 m, fov 70, cahaya senja",
]
FOOT = [
    "C4 \"Mata Jayadwara\" — v01 (kiri) vs v02 (kanan): komposisi kamera sama, jarak antarzona v02 ~1,7x lebih jauh.",
    "Galian v02 lebih besar & berundak lebih lebar; desa (titik mulai) kini terpisah jauh dari candi; 775 pohon + 30 tiang sebagai pembanding skala.",
]


RESAMPLE = getattr(getattr(Image, "Resampling", Image), "LANCZOS", 1)


def font(size, bold=False):
    for nama in (("arialbd.ttf" if bold else "arial.ttf"), "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nama, size)
        except Exception:  # noqa: BLE001
            continue
    return ImageFont.load_default()


def main():
    for p in (V01, V02):
        if not os.path.exists(p):
            print("GAGAL: tidak ada " + p)
            return 1
    a = Image.open(V01).convert("RGB").resize((W_PANEL, H_PANEL), RESAMPLE)
    b = Image.open(V02).convert("RGB").resize((W_PANEL, H_PANEL), RESAMPLE)

    W = W_PANEL * 2
    H = H_HEAD + H_PANEL + H_LABEL + H_FOOT
    im = Image.new("RGB", (W, H), BAR)
    d = ImageDraw.Draw(im)
    im.paste(a, (0, H_HEAD))
    im.paste(b, (W_PANEL, H_HEAD))

    f_head = font(38, True)
    f_lab = font(26, True)
    f_sub = font(26)
    f_foot = font(23)
    f_tag = font(34, True)

    d.text((24, 16), "BANDING C4 — v01 vs v02 (greybox Ep01_LawangSapta)", font=f_head, fill=FG)
    d.line([(0, H_HEAD - 3), (W, H_HEAD - 3)], fill=(70, 70, 78), width=3)

    # tag besar di tiap panel
    for i, (tag, x0) in enumerate((("v01", 0), ("v02", W_PANEL))):
        d.rectangle([x0 + 14, H_HEAD + 14, x0 + 128, H_HEAD + 68], fill=(0, 0, 0))
        d.text((x0 + 30, H_HEAD + 18), tag, font=f_tag, fill=FG2)

    y = H_HEAD + H_PANEL
    d.line([(0, y), (W, y)], fill=(70, 70, 78), width=3)
    for i, (baris, x0) in enumerate(((KIRI, 0), (KANAN, W_PANEL))):
        for j, t in enumerate(baris):
            d.text((x0 + 20, y + 10 + j * 30), t, font=f_sub, fill=FG if j == 0 else (200, 200, 205))

    y2 = y + H_LABEL
    d.line([(0, y2), (W, y2)], fill=(70, 70, 78), width=3)
    for j, t in enumerate(FOOT):
        d.text((24, y2 + 12 + j * 40), t, font=f_foot, fill=FG)
    d.text((24, y2 + 12 + 2 * 40), "Sumber: %s | %s" % (
        os.path.relpath(V01, REPO).replace("\\", "/"), os.path.relpath(V02, REPO).replace("\\", "/")),
        font=f_sub, fill=(150, 150, 158))

    im.save(OUT)
    print("tulis: " + OUT)
    print("ukuran: %dx%d (panel %dx%d, v01=%s, v02=%s)" % (
        W, H, W_PANEL, H_PANEL, Image.open(V01).size, Image.open(V02).size))
    print("SELESAI")
    return 0


sys.exit(main())
