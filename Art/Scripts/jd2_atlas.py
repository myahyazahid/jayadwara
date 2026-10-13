"""Jayadwara2 — pembantu atlas: posisi 3D per texel (rasterisasi segitiga di ruang UV) dan klasifikasi zona warna.
Dipakai make_textures_jayadwara2.py dan analyze_atlas_jayadwara2.py (python -I; butuh Art/Export/_jd2/_mesh_uv.npz dari jayadwara2_15_dump_uv.py)."""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TEX = ROOT / "Art" / "Export" / "Textures_Jayadwara2"


def load_mesh():
    D = np.load(ROOT / "Art" / "Export" / "_jd2" / "_mesh_uv.npz")
    return D["tri_pos"], D["tri_uv"]


def texel_positions(W, H):
    """P[H, W, 3] (meter, ruang rest; NaN = tak terpetakan)."""
    tp, tu = load_mesh()
    P = np.full((H, W, 3), np.nan, np.float32)
    for pos, uv in zip(tp, tu):
        px = uv[:, 0] * (W - 1)
        py = (1.0 - uv[:, 1]) * (H - 1)
        x0, x1 = int(np.floor(px.min())), int(np.ceil(px.max()))
        y0, y1 = int(np.floor(py.min())), int(np.ceil(py.max()))
        if x1 < 0 or y1 < 0 or x0 >= W or y0 >= H:
            continue
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W - 1), min(y1, H - 1)
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        den = (py[1] - py[2]) * (px[0] - px[2]) + (px[2] - px[1]) * (py[0] - py[2])
        if abs(den) < 1e-9:
            continue
        l0 = ((py[1] - py[2]) * (xs - px[2]) + (px[2] - px[1]) * (ys - py[2])) / den
        l1 = ((py[2] - py[0]) * (xs - px[2]) + (px[0] - px[2]) * (ys - py[2])) / den
        l2 = 1.0 - l0 - l1
        m = (l0 >= -0.02) & (l1 >= -0.02) & (l2 >= -0.02)
        if not m.any():
            continue
        pts = l0[m, None] * pos[0] + l1[m, None] * pos[1] + l2[m, None] * pos[2]
        P[ys[m], xs[m]] = pts


    return P


def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(axis=-1), rgb.min(axis=-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m, (mx - r) / np.where(m, d, 1), 0)
    gc = np.where(m, (mx - g) / np.where(m, d, 1), 0)
    bc = np.where(m, (mx - b) / np.where(m, d, 1), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = (h / 6.0) % 1.0
    h = np.where(m, h, 0.0)
    s = np.where(mx > 1e-6, d / np.where(mx > 1e-6, mx, 1), 0)
    return h * 360.0, s, mx


def zone_labels(bc):
    """0 hitam, 1 merah, 2 emas, 3 putih/krem, 4 lain (hijau/biru/ungu/abu bernoda). bc: float sRGB [H, W, 3]."""
    h, s, v = rgb_to_hsv(bc)
    lab = np.full(h.shape, 4, np.int8)
    lab[(v < 0.24)] = 0
    lab[(v >= 0.24) & ((h >= 345) | (h < 14)) & (s > 0.40)] = 1
    lab[(v >= 0.40) & (h >= 24) & (h < 62) & (s > 0.30)] = 2
    lab[(v >= 0.62) & (s < 0.28)] = 3
    # oranye-coklat peralihan emas<->merah (h 14-24) -> ke terdekat berdasarkan hue
    tr = (lab == 4) & (v >= 0.24) & (h >= 14) & (h < 24) & (s > 0.30)
    lab[tr & (h < 19)] = 1
    lab[tr & (h >= 19)] = 2
    return lab
