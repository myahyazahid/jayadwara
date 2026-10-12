"""Buat set tekstur dasar Aksa dari data UV (NPZ dari aksa_50_uv.py).

Pakai: python -I Art/Scripts/make_textures_aksa.py [uv_faces.npz] [out_dir]
Keluaran (8-bit PNG) di <out_dir> (default Art/Export/Textures_Aksa), prefix T_Aksa_<Slot>_:
  Skin  2048: BC, N, ORM, SSS (mask kulit untuk subsurface)
  Eyes   512: BC, N (datar), ORM (kornea lewat Clear Coat di material, tetap 5 slot)
  Hair  1024: BC, N, ORM
  Cloth 2048: Mask (R jaket, G kaus, B celana, A batik), BC, N, ORM
  Gear  1024: BC, N, ORM
BC = warna zona (vertex color AK_Zone dari model, diinterpolasi barycentric) + variasi halus; ORM R=AO (putih; bake Cycles bila
Art/Export/Textures_Aksa/_bake/AO_<Slot>.png ada), G=roughness per zona, B=metallic. Normal OpenGL (+Y).
Batik: kawung gaya (motif umum, bukan larangan keraton) pada zona `batik` (kerah dalam & selendang); perlu review budayawan (docs/06).
Tekstur ini DASAR: developer menimpa/mengecat (kulit, lipatan, keausan) di atasnya. Jalankan ulang hanya bila UV berubah.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
NPZ = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Art" / "Export" / "_uv_faces_aksa.npz"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "Art" / "Export" / "Textures_Aksa"
OUT.mkdir(parents=True, exist_ok=True)

SIZE = {"Skin": 2048, "Eyes": 512, "Hair": 1024, "Cloth": 2048, "Gear": 1024}
PAD = {"Skin": 8, "Eyes": 4, "Hair": 6, "Cloth": 8, "Gear": 6}
ROUGH = {"skin": 0.55, "hair": 0.52, "eye": 0.10, "sclera": 0.10, "jacket": 0.86, "shirt": 0.90, "pants": 0.84, "batik": 0.80,
         "gold": 0.30, "boots": 0.55, "gloves": 0.62, "belt": 0.58, "stone": 0.28, "hair_hi": 0.40, "iris": 0.10, "pupil": 0.10, "lip": 0.45,
         "sole": 0.85}
METAL = {"gold": 1.0}
WEAVE_M = 0.0035            # jarak benang kain (m)
BATIK_TILE_M = 0.045        # sisi satu motif kawung (m)
BATIK_MOTIF = (0.52, 0.34, 0.14)   # sRGB motif kawung pada batik #5A3B2B: cokelat-emas redup (tidak bersaing dengan emas zirah/perhiasan)

d = np.load(NPZ)
uv, col, mat, zone, area, part, pos = d["uv"], d["col"], d["mat"], d["zone"], d["area"], d["part"], d["pos"]
slots = [str(s) for s in d["slots"]]
zones = [str(z) for z in d["zones"]]
pnames = [str(x) for x in d["part_names"]]


def zi(n):
    return zones.index(n)


def lin2srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def srgb2lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_u8(a):
    return np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)


def noise(size, sigma, seed_off=0):
    n = np.random.default_rng(100 + seed_off).standard_normal((size, size)).astype(np.float32)
    n = ndi.gaussian_filter(n, sigma, mode="wrap")
    return n / (n.std() + 1e-9)


def rasterize(tris_uv, order, size):
    """Per piksel: indeks segitiga (gambar terakhir menang; -1 = kosong) + koordinat barisentrik."""
    tid = np.full((size, size), -1, np.int32)
    bary = np.zeros((size, size, 3), np.float32)
    for k in order:
        x = tris_uv[k][:, 0] * size
        y = (1.0 - tris_uv[k][:, 1]) * size
        x0, x1 = int(np.floor(x.min() - 0.5)), int(np.ceil(x.max() + 0.5))
        y0, y1 = int(np.floor(y.min() - 0.5)), int(np.ceil(y.max() + 0.5))
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, size - 1), min(y1, size - 1)
        if x1 < x0 or y1 < y0:
            continue
        den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(den) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / den
        l1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / den
        l2 = 1 - l0 - l1
        m = (l0 >= -0.02) & (l1 >= -0.02) & (l2 >= -0.02)
        if not m.any():
            continue
        tid[y0:y1 + 1, x0:x1 + 1][m] = k
        bary[y0:y1 + 1, x0:x1 + 1][m] = np.stack([l0[m], l1[m], l2[m]], axis=-1)
    return tid, bary


def kawung(u, v):
    h = np.zeros_like(u)
    r, w = 0.5 / np.sqrt(2.0), 0.035
    for cx, cy in ((0.0, 0.0), (0.5, 0.5), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)):
        h = np.maximum(h, np.clip(1.0 - np.abs(np.hypot(u - cx, v - cy) - r) / w, 0, 1))
    for cx, cy in ((0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75), (0.5, 0.0), (0.5, 1.0), (0.0, 0.5), (1.0, 0.5)):
        h = np.maximum(h, np.clip(1.0 - np.hypot(u - cx, v - cy) / 0.045, 0, 1))
    return h


def normal_from_height(h, strength):
    gy, gx = np.gradient(h)
    n = np.stack([-gx * strength, gy * strength, np.ones_like(h)], axis=-1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


report = []
for mi, slot in enumerate(slots):
    size = SIZE[slot]
    sel = np.where(mat == mi)[0]
    t_uv, t_col, t_zone, t_area, t_part = uv[sel], col[sel], zone[sel], area[sel], part[sel]
    if slot == "Eyes":                     # sklera dari belakang ke depan, lalu iris, lalu pupil (proyeksi planar tumpang tindih)
        pri = np.array([0 if pnames[p].startswith("AK_EyeSclera") else 1 if "Iris" in pnames[p] else 2 for p in t_part])
        y = pos[sel][..., 1].mean(axis=1)
        order = np.lexsort((-y, pri))
    else:
        order = np.arange(len(sel))
    tid, bary = rasterize(t_uv, order, size)
    covered = tid >= 0
    dist, (iy, ix) = ndi.distance_transform_edt(~covered, return_indices=True)
    filled = covered | (dist <= PAD[slot])
    tid_f, bary_f = tid[iy, ix], bary[iy, ix]
    tt = np.clip(tid_f, 0, None)
    color_lin = (t_col[tt] * bary_f[..., None]).sum(axis=2)           # linear
    zid = np.where(filled, t_zone[tt], -1)
    uv_area_px = 0.5 * np.abs((t_uv[:, 1, 0] - t_uv[:, 0, 0]) * (t_uv[:, 2, 1] - t_uv[:, 0, 1])
                              - (t_uv[:, 2, 0] - t_uv[:, 0, 0]) * (t_uv[:, 1, 1] - t_uv[:, 0, 1])) * size * size
    density = float(np.sqrt(uv_area_px.sum() / t_area.sum()))
    report.append((slot, size, density, covered.mean()))
    zm = lambda name: (zid == zi(name))   # noqa: E731
    color_lin[~filled] = color_lin[filled].mean(axis=0)
    var_lo, var_hi = noise(size, 24, mi), noise(size, 1.4, mi + 10)

    rough = np.full((size, size), 0.6, np.float32)
    metal = np.zeros((size, size), np.float32)
    for zn in zones:
        rough[zm(zn)] = ROUGH[zn]
        if zn in METAL:
            metal[zm(zn)] = METAL[zn]
    height = np.zeros((size, size), np.float32)
    ao = np.ones((size, size), np.float32)
    extras = {}
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)

    if slot == "Skin":
        sk = zm("skin")
        k = 1.0 + 0.0 * var_lo + 0.010 * var_hi                                          # tanpa variasi frekuensi rendah: beda antar island terlihat sebagai tambalan di seam
        color_lin = np.where(sk[..., None], color_lin * k[..., None], color_lin)
        height = 0.35 * var_hi + 0.2 * noise(size, 0.7, 40)                                               # pori halus
        rough = np.where(sk, 0.55 + 0.03 * var_hi, rough)
        srgb = lin2srgb(np.clip(color_lin, 0, 1))
        ratio = srgb[..., 0] / np.maximum(srgb[..., 1], 1e-3)
        lipness = np.clip((ratio - 1.48) / (1.78 - 1.48), 0, 1) * sk
        rough = np.where(sk, rough - 0.12 * lipness, rough)
        lum = 0.299 * srgb[..., 0] + 0.587 * srgb[..., 1] + 0.114 * srgb[..., 2]
        stub = np.clip((0.42 - lum) / 0.30, 0, 1) * sk                     # rambut cukur (fade) di kulit kepala: tanpa SSS, lebih kasar
        rough = np.where(sk, rough + 0.15 * stub, rough)
        height = height + 0.6 * stub * noise(size, 0.6, 41)
        extras["SSS"] = np.where(sk, (1.0 - 0.85 * lipness) * (1.0 - 0.9 * stub), 0.0).astype(np.float32)
    elif slot == "Eyes":
        for u0 in (0.25, 0.75):
            dx, dy = (xx + 0.5) / size - u0, 0.5 - (yy + 0.5) / size
            r = np.hypot(dx, dy)
            ang = np.arctan2(dy, dx)
            iris_r = 0.11
            fib = 0.5 + 0.5 * np.sin(ang * 48 + 3 * noise(size, 2, 5)) * np.clip(1 - np.abs(r / iris_r - 0.7) * 1.6, 0, 1)
            m_iris = zm("iris") & (np.abs(dx) < 0.25)
            ring = np.clip((r / iris_r - 0.78) / 0.22, 0, 1)
            kk = (0.78 + 0.35 * fib) * (1 - 0.55 * ring)
            color_lin = np.where(m_iris[..., None], color_lin * kk[..., None], color_lin)
            edge = np.clip((r - 0.12) / 0.1, 0, 1)
            m_scl = zm("sclera") & (np.abs(dx) < 0.25)
            tint = np.array([0.92, 0.84, 0.82])
            color_lin = np.where(m_scl[..., None], color_lin * (1 - edge[..., None] * (1 - tint) * 0.9), color_lin)
    elif slot == "Hair":
        hr = zm("hair") | zm("hair_hi")
        color_lin = np.where(hr[..., None], color_lin * (1.0 + 0.10 * var_hi + 0.06 * var_lo)[..., None], color_lin)
        height = 0.25 * var_hi
    elif slot == "Cloth":
        px_per_thread = max(WEAVE_M * density, 2.0)
        weave = (np.sin(2 * np.pi * xx / px_per_thread) * np.sin(2 * np.pi * yy / px_per_thread)).astype(np.float32)
        height = 0.5 * weave + 0.25 * var_hi
        cl = zm("jacket") | zm("shirt") | zm("pants")
        color_lin = np.where(cl[..., None], color_lin * (1.0 + 0.05 * var_lo + 0.03 * weave)[..., None], color_lin)
        bt = zm("batik")
        tile_px = BATIK_TILE_M * density
        motif = np.clip(kawung(((xx / tile_px) % 1.0).astype(np.float32), ((yy / tile_px) % 1.0).astype(np.float32)) * 1.6, 0, 1)
        motif = ndi.gaussian_filter(motif, 0.6)
        mot_lin = srgb2lin(np.array(BATIK_MOTIF, np.float32))
        color_lin = np.where(bt[..., None], color_lin * (1 - motif[..., None]) + mot_lin * motif[..., None] * (1 + 0.08 * var_hi[..., None]),
                             color_lin)
        height = np.where(bt, height + 0.9 * motif, height)
        rough = np.where(bt, 0.80 - 0.1 * motif, rough)
        extras["Mask"] = np.stack([zm("jacket"), zm("shirt"), zm("pants"), bt], axis=-1).astype(np.float32)
    elif slot == "Gear":
        lea = zm("boots") | zm("gloves") | zm("belt")
        grain = 0.7 * noise(size, 1.0, 51) + 0.3 * noise(size, 3.0, 52)
        height = np.where(lea, grain, 0.1 * var_hi)
        color_lin = np.where(lea[..., None], color_lin * (1.0 + 0.10 * var_lo + 0.06 * grain)[..., None], color_lin)
        gd = zm("gold")
        color_lin = np.where(gd[..., None], color_lin * (1.0 + 0.06 * var_lo)[..., None], color_lin)
        rough = np.where(gd, 0.30 + 0.06 * var_lo, rough)

    bc = lin2srgb(np.clip(color_lin, 0, 1))
    nrm = normal_from_height(ndi.gaussian_filter(height, 0.5), {"Skin": 0.25, "Hair": 0.35, "Cloth": 0.6, "Gear": 0.4, "Eyes": 0.0}[slot])
    ao_path = OUT / "_bake" / f"AO_{slot}.png"
    if ao_path.exists():
        raw = np.asarray(Image.open(ao_path).convert("L")).astype(np.float32) / 255.0
        ao = 0.55 + 0.45 * np.clip(ndi.gaussian_filter(raw, 1.0), 0, 1)
        ao[~filled] = 1.0
    orm = np.stack([ao, np.clip(rough, 0.04, 1), metal], axis=-1)
    Image.fromarray(to_u8(bc), "RGB").save(OUT / f"T_Aksa_{slot}_BC.png")
    Image.fromarray(to_u8(orm), "RGB").save(OUT / f"T_Aksa_{slot}_ORM.png")
    Image.fromarray(to_u8(nrm * 0.5 + 0.5), "RGB").save(OUT / f"T_Aksa_{slot}_N.png")
    if "SSS" in extras:
        Image.fromarray(to_u8(extras["SSS"]), "L").save(OUT / f"T_Aksa_{slot}_SSS.png")
    if "Mask" in extras:
        Image.fromarray(to_u8(extras["Mask"]), "RGBA").save(OUT / f"T_Aksa_{slot}_Mask.png")
    print(f"{slot}: ok", flush=True)

print(f"{'slot':6s} {'ukuran':>7s} {'density px/m':>13s} {'terisi':>8s}")
for r in report:
    print(f"{r[0]:6s} {r[1]:7d} {r[2]:13.0f} {r[3] * 100:7.1f}%")
print("keluaran:", OUT)
