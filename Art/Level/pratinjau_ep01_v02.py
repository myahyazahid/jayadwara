"""Gambar pratinjau tampak atas Ep 1 v02 dari ep01_layout_v02.json + ep01_medan_v02.py (acuan render C5 dan peta ketinggian).
Pakai: python -I Art/Level/pratinjau_ep01_v02.py [keluaran.png]   (butuh Pillow; default docs/visual/ep01_layout_v02_atas.png)
Utara di atas, 1 px = 1 m."""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
import ep01_medan_v02 as M  # noqa: E402

D = json.load(open(os.path.join(DIR, "ep01_layout_v02.json"), encoding="utf-8"))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DIR, "..", "..", "docs", "visual", "ep01_layout_v02_atas.png")
X0, X1, Y0, Y1 = M.BATAS_MEDAN
W, H = X1 - X0, Y1 - Y0

ZONA_WARNA = {"Air": (70, 120, 170), "Galian": (176, 90, 50), "Jalan": (150, 120, 90), "Plato": (150, 150, 140),
              "Sawah": (100, 160, 90), "Desa": (190, 120, 100), "Hutan": (70, 100, 65)}
MI_WARNA = {"Andesit": (120, 120, 125), "Arca": (200, 190, 120), "Terpal": (60, 100, 160), "Alat": (230, 190, 40),
            "Kendaraan": (230, 190, 40), "Kayu": (110, 80, 50), "Desa": (190, 70, 60), "Musala": (245, 245, 245),
            "Sawah": (120, 180, 100), "Penanda": (255, 255, 255), "Hutan": (60, 90, 55)}

img = Image.new("RGB", (W, H))
px = img.load()
for j in range(0, H, 2):
    for i in range(0, W, 2):
        x, y = X0 + i + 1, Y1 - j - 1
        z = M.elev(x, y)
        c = ZONA_WARNA[M.zona_material(x, y, z)]
        k = 0.80 + 0.0075 * max(-6.0, min(40.0, z))         # makin tinggi makin terang; undakan galian ikut terbaca
        c = tuple(min(255, int(v * k)) for v in c)
        for di in (0, 1):
            for dj in (0, 1):
                if i + di < W and j + dj < H:
                    px[i + di, j + dj] = c
dr = ImageDraw.Draw(img)


def P(x, y):
    return (x - X0, Y1 - y)


def kotak(x, y, Pj, L, yaw, warna, garis=None):
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    pts = [P(x + a * c - b * s, y + a * s + b * c) for a, b in ((-Pj / 2, -L / 2), (Pj / 2, -L / 2), (Pj / 2, L / 2), (-Pj / 2, L / 2))]
    dr.polygon(pts, fill=warna, outline=garis)


for o in D["objek"]:
    if o["id"].startswith("LATAR_"):
        continue
    warna = MI_WARNA.get(o["mi"], (200, 200, 200))
    j = o["jenis"]
    if j == "dinding":
        dr.line([P(*o["dari"][:2]), P(*o["ke"][:2])], fill=warna, width=2)
    elif j == "tangga":
        dr.line([P(*o["dari"][:2]), P(*o["ke"][:2])], fill=(235, 235, 235), width=max(2, int(o["lebar"])))
    elif j == "candi_bertingkat":
        x, y = o["pos"]
        for tk in o["tingkat"]:
            kotak(x, y, tk[0], tk[1], 0, warna, (0, 0, 0))
    elif j == "kerucut":
        x, y = o["pos"]
        r = o["ukuran"][0] / 2
        dr.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=warna)
    else:
        outline = (255, 255, 255) if j == "bidang" else ((200, 40, 40) if o.get("hancur") else (0, 0, 0))
        kotak(o["pos"][0], o["pos"][1], o["ukuran"][0], o["ukuran"][1], o.get("yaw", 0), warna, outline)
for pts in D["pohon_kelompok"].values():
    for x, y, s in pts:
        r = 3.0 * s
        dr.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(40, 80, 40))
for x, y in D["tiang_listrik"]["titik"]:
    dr.ellipse([P(x - 1.5, y + 1.5), P(x + 1.5, y - 1.5)], fill=(20, 20, 20))
for z in D["zona"]:
    warna = {"merah": (200, 30, 30), "hijau": (30, 140, 60)}[z["warna"]]
    dr.rectangle([P(z["x"][0], z["y"][1]), P(z["x"][1], z["y"][0])], outline=warna, width=2)
b = D["batas_arena"]
dr.rectangle([P(b["x"][0], b["y"][1]), P(b["x"][1], b["y"][0])], outline=(220, 0, 0), width=3)
dr.line([P(*p) for p in D["rute_aksa"]], fill=(255, 255, 255), width=3)
for p in D["penanda"]:
    x, y = p["pos"]
    r = p.get("radius", 5)
    dr.ellipse([P(x - r, y + r), P(x + r, y - r)], outline=(255, 230, 0), width=2)
    dr.text((P(x, y)[0] + r + 3, P(x, y)[1] - 6), p["id"], fill=(255, 255, 255))
for k in D["kamera"]:
    if k.get("ortho"):
        continue
    x, y = k["pos"]
    tx, ty = k["lihat_ke"][:2]
    a = math.atan2(ty - y, tx - x)
    dr.line([P(x, y), P(x + 45 * math.cos(a), y + 45 * math.sin(a))], fill=(0, 0, 0), width=2)
    dr.text((P(x, y)[0] + 4, P(x, y)[1] + 4), k["id"].split("_")[0], fill=(0, 0, 0))
for gx in range(X0, X1 + 1, 100):
    dr.line([P(gx, Y1), P(gx, Y1 - 6)], fill=(0, 0, 0))
rx, ry = M.GALIAN_RX * 2, M.GALIAN_RY * 2
dr.text((8, 8), f"Ep01_LawangSapta v02 · galian {rx:.0f} x {ry:.0f} m, dalam {25 - M.UNDAKAN[0][1]:.0f} m · utara di atas · 1 px = 1 m · "
                "grid 100 m di tepi atas", fill=(255, 255, 255))
img.save(OUT, optimize=True)
print(f"ditulis: {os.path.normpath(OUT)} ({W} x {H} px)")
