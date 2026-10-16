"""Gambar pratinjau tampak atas Ep 2 v02 dari ep02_layout_v02.json + ep02_medan_v02.py (acuan render Hermes V2/C5).
Pakai: python -I Art/Level/pratinjau_ep02_v02.py [keluaran.png]   (butuh Pillow; default docs/visual/ep02_layout_v02_atas.png)
Utara di atas, 1 px = 1 m, warna = MI_WARNA di JSON."""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
import ep02_medan_v02 as M  # noqa: E402

D = json.load(open(os.path.join(DIR, "ep02_layout_v02.json"), encoding="utf-8"))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DIR, "..", "..", "docs", "visual", "ep02_layout_v02_atas.png")
X0, X1, Y0, Y1 = M.BATAS_MEDAN
W, H = X1 - X0, Y1 - Y0
WARNA = {k: tuple(v) for k, v in D["mi_warna"].items()}
img = Image.new("RGB", (W, H))
px = img.load()
for j in range(0, H, 2):
    for i in range(0, W, 2):
        x, y = X0 + i + 1, Y1 - j - 1
        z = M.elev(x, y)
        c = WARNA[M.zona_material(x, y, z)]
        k = 0.88 + 0.012 * max(-2.0, min(12.0, z))          # sedikit lebih terang di tempat tinggi
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


for k in D["kelompok"]:
    w = WARNA[k.get("mi_atap", k["mi"])]
    for h in k["item"]:
        kotak(h[0], h[1], h[2] + (0.4 if k["bentuk"] == "rumah" else 0), h[3] + (0.4 if k["bentuk"] == "rumah" else 0), h[5], w,
              (60, 60, 60) if k["bentuk"] == "rumah" else None)
for o in D["objek"]:
    if o["id"].startswith("LATAR_") or o["id"].startswith("AIR_"):
        continue
    if o["jenis"] == "dinding":
        dr.line([P(*o["dari"]), P(*o["ke"])], fill=WARNA[o["mi"]], width=2)
    elif o["jenis"] == "kerucut":
        x, y = o["pos"]
        r = o["ukuran"][0] / 2
        dr.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=WARNA[o["mi"]])
    else:
        warna = WARNA[o.get("mi_atap", o["mi"])]
        kotak(o["pos"][0], o["pos"][1], o["ukuran"][0], o["ukuran"][1], o.get("yaw", 0), warna,
              (0, 0, 0) if o["jenis"] != "bidang" else (255, 255, 255))
for pts in D["pohon_kelompok"].values():
    for x, y, s in pts:
        r = 3.5 * s
        dr.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=WARNA["Pohon"])
for z in D["zona"]:
    warna = {"merah": (200, 30, 30), "hijau": (30, 140, 60), "ungu": (110, 60, 140)}[z["warna"]]
    dr.rectangle([P(z["x"][0], z["y"][1]), P(z["x"][1], z["y"][0])], outline=warna, width=2)
b = D["batas_arena"]
dr.rectangle([P(b["x"][0], b["y"][1]), P(b["x"][1], b["y"][0])], outline=(200, 0, 0), width=3)
dr.line([P(*p) for p in D["rute_investigasi"]], fill=(240, 200, 0), width=3)
dr.line([P(*p) for p in D["rute_kejar"]], fill=(220, 20, 20), width=3)
for p in D["penanda"]:
    x, y = p["pos"]
    r = p.get("radius", 4)
    dr.ellipse([P(x - r, y + r), P(x + r, y - r)], outline=(255, 255, 255), width=2)
    dr.text((P(x, y)[0] + r + 2, P(x, y)[1] - 6), p["id"], fill=(255, 255, 255))
for k in D["kamera"]:
    if k.get("ortho"):
        continue
    x, y = k["pos"]
    tx, ty = k["lihat_ke"][:2]
    a = math.atan2(ty - y, tx - x)
    dr.line([P(x, y), P(x + 40 * math.cos(a), y + 40 * math.sin(a))], fill=(0, 0, 0), width=2)
    dr.text((P(x, y)[0] + 4, P(x, y)[1] + 4), k["id"].split("_")[0], fill=(0, 0, 0))
for gx in range(X0, X1 + 1, 100):
    dr.line([P(gx, Y1), P(gx, Y1 - 6)], fill=(0, 0, 0))
dr.text((8, 8), "Ep02_KampungKali v02 · utara di atas · 1 px = 1 m · grid 100 m di tepi atas", fill=(255, 255, 255))
img.save(OUT, optimize=True)
print(f"ditulis: {os.path.normpath(OUT)} ({W} x {H} px)")
