"""Buat set tekstur Jayadwara dari data UV (NPZ dari 07_uv_unwrap.py).

Pakai: python -I Art/Scripts/make_textures.py <uv_faces.npz> [out_dir]
Keluaran (8-bit PNG) per slot S ∈ {Armor, Body, Cloth, Face} di <out_dir> (default Art/Export/Textures):
  T_Jayadwara_<S>_Mask.png  RGBA = zona warna: R merah, G emas, B hitam, A putih (docs/13 6.3; untuk recolor Kala/Kembar)
  T_Jayadwara_<S>_BC.png    BaseColor sebagai PENGALI warna zona (putih = tanpa perubahan); panel kain depan/belakang 0,8 (crimson)
  T_Jayadwara_<S>_N.png     Normal (OpenGL, +Y). Kain: ornamen emas sedikit timbul; lainnya datar
  T_Jayadwara_<S>_ORM.png   R=AO (bake Cycles dari _bake/AO_<S>.png bila ada, kalau tidak putih), G=Roughness, B=Metallic
  T_Jayadwara_Face_Emit.png R=emissive (mata & permata dada) — nilai KONSTAN, tidak dikaitkan ke meter Sync (aturan IP)
Resolusi: Armor 2048, Cloth 2048, Body 1024, Face 1024 (docs/13 6.4). Padding 8 px (isi dari piksel terdekat).
Batik: motif kawung gaya (umum); bukan batik larangan keraton; tetap perlu review budayawan (docs/06).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
NPZ = Path(sys.argv[1])
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "Art" / "Export" / "Textures"
OUT.mkdir(parents=True, exist_ok=True)

SIZE = {"Armor": 2048, "Cloth": 2048, "Body": 1024, "Face": 1024}
PAD = 8
BATIK_TILE_M = 0.09          # sisi satu motif kawung (meter) pada kain
ROUGH = {"red": 0.36, "gold": 0.32, "black": 0.62, "white": 0.28, "marun": 0.55, "gem": 0.15, "eye": 0.15}
METAL = {"red": 0.0, "gold": 0.20, "black": 0.0, "white": 0.0, "marun": 0.0, "gem": 0.0, "eye": 0.0}
CLOTH_ROUGH = 0.80

d = np.load(NPZ)
uv, mat, zone, area, part = d["uv"], d["mat"], d["zone"], d["area"], d["part"]
slots = [str(s) for s in d["slots"]]
zones = [str(z) for z in d["zones"]]


def raster_ids(tris, ids, size):
    """Gambar segitiga UV ke peta id (0 = kosong, id+1). Piksel: x=u*size, y=(1-v)*size."""
    im = Image.new("I", (size, size), 0)
    dr = ImageDraw.Draw(im)
    for t, i in zip(tris, ids):
        dr.polygon([(float(u) * size, (1.0 - float(v)) * size) for u, v in t], fill=int(i) + 1)
    return np.asarray(im)


def pad(img_ids, px):
    """Isi piksel kosong dari piksel terisi terdekat (jarak <= px)."""
    empty = img_ids == 0
    dist, (iy, ix) = ndi.distance_transform_edt(empty, return_indices=True)
    out = img_ids.copy()
    near = empty & (dist <= px)
    out[near] = img_ids[iy[near], ix[near]]
    return out


def kawung(u, v):
    """Tinggi motif kawung gaya: lingkaran berpotongan pada kisi persegi + titik di pusat. u,v koordinat tile ∈ [0,1)."""
    h = np.zeros_like(u)
    r, w = 0.5 / np.sqrt(2.0), 0.035
    for cx, cy in ((0.0, 0.0), (0.5, 0.5), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)):
        dist = np.hypot(u - cx, v - cy)
        h = np.maximum(h, np.clip(1.0 - np.abs(dist - r) / w, 0, 1))
    for cx, cy in ((0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75), (0.5, 0.0), (0.5, 1.0), (0.0, 0.5), (1.0, 0.5)):
        h = np.maximum(h, np.clip(1.0 - np.hypot(u - cx, v - cy) / 0.045, 0, 1))
    return h


def to_u8(a):
    return np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)


report = []
for mi, slot in enumerate(slots):
    size = SIZE[slot]
    sel = mat == mi
    t_uv, t_zone, t_area = uv[sel], zone[sel], area[sel]
    ids = pad(raster_ids(t_uv, t_zone, size), PAD)
    cover = raster_ids(t_uv, np.zeros(len(t_uv), dtype=int), size) > 0
    # statistik UV: texel density (px per meter) dan tumpang-tindih
    uv_area_px = 0.5 * np.abs((t_uv[:, 1, 0] - t_uv[:, 0, 0]) * (t_uv[:, 2, 1] - t_uv[:, 0, 1])
                              - (t_uv[:, 2, 0] - t_uv[:, 0, 0]) * (t_uv[:, 1, 1] - t_uv[:, 0, 1])) * size * size
    density = float(np.sqrt(uv_area_px.sum() / t_area.sum()))
    overlap = max(0.0, 1.0 - cover.sum() / max(uv_area_px.sum(), 1))
    report.append((slot, size, density, cover.mean(), overlap))

    zid = ids - 1
    zmask = lambda name: (zid == zones.index(name))
    R, G, B, A = zmask("red") | zmask("marun"), zmask("gold"), zmask("black"), zmask("white")
    mask = np.stack([R, G, B, A], axis=-1).astype(np.float32)
    Image.fromarray(to_u8(mask), "RGBA").save(OUT / f"T_Jayadwara_{slot}_Mask.png")

    # BaseColor (pengali) & normal
    bc = np.ones((size, size, 3), np.float32)
    nrm = np.zeros((size, size, 3), np.float32)
    nrm[..., 2] = 1.0
    rough = np.zeros((size, size), np.float32)
    metal = np.zeros((size, size), np.float32)
    for zi, zn in enumerate(zones):
        m = zid == zi
        rough[m] = ROUGH[zn]
        metal[m] = METAL[zn]
    rough[ids == 0] = 0.6
    if slot == "Cloth":
        # Revisi (konsep): kain merah polos + ORNAMEN EMAS di bagian bawah (pita ganda, berlian bertingkat + titik,
        # chevron mengikuti ujung runcing). Panel depan/belakang = crimson lebih gelap. Koordinat lokal per strip:
        # island kain sudah diorientasi (panjang searah -V) -> t = 0 di sabuk, 1 di ujung; l = melintang.
        pnames = [str(x) for x in d["part_names"]] if "part_names" in d.files else []
        pid = pad(raster_ids(t_uv, part[sel], size), PAD) - 1
        orn = np.zeros((size, size), bool)
        yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
        uu, vv = (xx + 0.5) / size, 1.0 - (yy + 0.5) / size
        LW = 0.0045                                                        # setengah lebar garis ornamen (m)
        for k, nm in enumerate(pnames):
            if not nm.startswith("JD_Cloth_") or nm.endswith("Trim"):
                continue
            tri = part[sel] == k
            if not tri.any():
                continue
            pu = t_uv[tri][..., 0]
            pv = t_uv[tri][..., 1]
            umin, umax, vmin, vmax = pu.min(), pu.max(), pv.min(), pv.max()
            m = pid == k
            m2u = size / density                                           # meter per unit UV
            x = (uu[m] - (umin + umax) / 2) * m2u                          # melintang (m), 0 = tengah strip
            y = (vmax - vv[m]) * m2u                                       # dari sabuk ke bawah (m)
            Lm = (vmax - vmin) * m2u
            Wm = (umax - umin) * m2u
            scarf = "Scarf" in nm
            y0 = Lm * (0.50 if scarf else 0.56)                            # awal zona ornamen
            o = (np.abs(y - y0) < LW) | (np.abs(y - (y0 + 0.022)) < LW * 0.7)
            a_, b_ = Wm * (0.30 if scarf else 0.32), Lm * 0.12
            yc = y0 + 0.04 + b_
            dd = np.abs(x) / a_ + np.abs(y - yc) / b_
            o |= np.abs(dd - 1.0) * min(a_, b_) < LW
            o |= np.abs(dd - 0.55) * min(a_, b_) < LW * 0.8
            o |= np.hypot(x, y - yc) < 0.010
            for sx in (-1, 1):
                o |= np.hypot(x - sx * a_ * 1.15, y - yc) < 0.007
            for j, off in enumerate((0.05, 0.085)):                       # chevron di bawah berlian
                ych = yc + b_ + off
                o |= (np.abs((y - ych) - (0.5 - np.abs(x) / max(Wm, 1e-3)) * 0.09) < LW * 0.8) & (y > yc + b_)
            orn[m] = o
            if not scarf:
                bc[m] = 0.80                                               # panel depan/belakang: crimson lebih gelap
        orn &= (ids != 0) & R
        G = G | orn
        R = R & ~orn
        mask = np.stack([R, G, B, A], axis=-1).astype(np.float32)
        Image.fromarray(to_u8(mask), "RGBA").save(OUT / f"T_Jayadwara_{slot}_Mask.png")
        h = ndi.gaussian_filter(orn.astype(np.float32), 1.2)               # ornamen sedikit timbul
        gy, gx = np.gradient(h)
        n = np.stack([-gx * 4.0, gy * 4.0, np.ones_like(h)], axis=-1)
        n /= np.linalg.norm(n, axis=-1, keepdims=True)
        nrm = n
        rough[ids != 0] = CLOTH_ROUGH
        metal[:] = np.where(G, 0.30, 0.0)
        rough = np.where(G, 0.50, rough)
        report[-1] += (0.0,)
    Image.fromarray(to_u8(bc), "RGB").save(OUT / f"T_Jayadwara_{slot}_BC.png")
    Image.fromarray(to_u8(nrm * 0.5 + 0.5), "RGB").save(OUT / f"T_Jayadwara_{slot}_N.png")
    ao = np.ones((size, size), np.float32)
    ao_path = OUT / "_bake" / f"AO_{slot}.png"
    if ao_path.exists():                      # AO hasil bake Cycles (09_bake_ao.py): haluskan noise, jaga kontras
        raw = np.asarray(Image.open(ao_path).convert("L")).astype(np.float32) / 255.0
        ao = np.clip(ndi.gaussian_filter(raw, 1.0), 0.0, 1.0) ** 0.85
        ao = 0.55 + 0.45 * ao                 # revisi: AO lembut (gaya cat stylized konsep); AO penuh membuat merah kusam
        ao[ids == 0] = 1.0
    orm = np.stack([ao, rough, metal], axis=-1)
    Image.fromarray(to_u8(orm), "RGB").save(OUT / f"T_Jayadwara_{slot}_ORM.png")
    if slot == "Face":
        emit = (zmask("gem") | zmask("eye")).astype(np.float32)
        Image.fromarray(to_u8(emit), "L").save(OUT / "T_Jayadwara_Face_Emit.png")

print(f"{'slot':6s} {'ukuran':>7s} {'density px/m':>13s} {'terisi':>8s} {'tumpang-tindih':>15s}")
for r in report:
    print(f"{r[0]:6s} {r[1]:7d} {r[2]:13.0f} {r[3] * 100:7.1f}% {r[4] * 100:14.2f}%" + "")
print("keluaran:", OUT)
