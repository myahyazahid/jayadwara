"""Bandingkan siluet blockout (npz dari 04_silhouette_export.py) dengan reference plane.

Pakai: python -I Art/Scripts/silhouette_compare.py <npz> [out_overlay.png]
Kanvas = kanvas reference plane (760x1200; 1000 px = 1,90 m; telapak kaki di y=1100; tengah badan x=380).
Warna overlay: putih = sama-sama terisi, merah = hanya referensi (blockout kurang), biru = hanya blockout (kelebihan).
Lengan di A-pose 30° (K8) vs konsep ±12° -> area lengan dikecualikan dari IoU "inti".
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "Art" / "Reference"
PX_PER_M = 1000 / 1.90
W, HCV, SOLE = 760, 1200, 1100


def raster(tris, flip_y=False):
    im = Image.new("L", (W, HCV), 0)
    d = ImageDraw.Draw(im)
    for t in tris:
        pts = [(380 + float(a) * PX_PER_M, SOLE - float(z) * PX_PER_M) for a, z in t]
        d.polygon(pts, fill=255)
    return np.asarray(im) > 0


def z_to_row(z):
    return int(round(SOLE - z * PX_PER_M))


def iou(a, b):
    u = (a | b).sum()
    return (a & b).sum() / u if u else float("nan")


def compare(name, mask_b, out=None):
    ref = np.asarray(Image.open(REF / f"jd_ref_{name}.png").split()[-1]) > 128
    # kecualikan lengan: kolom |x|>0.24 m pada tinggi 0.95..1.62 m (hanya tampak depan)
    ex = np.zeros_like(ref)
    if name == "front":
        r0, r1 = z_to_row(1.62), z_to_row(0.88)
        c0, c1 = int(380 - 0.24 * PX_PER_M), int(380 + 0.24 * PX_PER_M)
        ex[r0:r1, :c0] = True
        ex[r0:r1, c1:] = True
    print(f"\n== {name}: IoU total = {iou(mask_b, ref):.3f} | IoU tanpa area lengan = {iou(mask_b & ~ex, ref & ~ex):.3f}")
    bands = [("sepatu/greave", 0.0, 0.30), ("lutut/betis", 0.30, 0.62), ("paha/kain", 0.62, 0.95),
             ("pinggul/sabuk", 0.95, 1.22), ("dada", 1.22, 1.62), ("kepala+tanduk", 1.62, 2.0)]
    print(f"   {'band':16s} {'IoU':>6s} {'lebar ref':>10s} {'lebar blok':>11s} {'selisih':>8s}  (lebar = maks. rentang x, m)")
    for label, z0, z1 in bands:
        r0, r1 = z_to_row(z1), z_to_row(z0)
        sel_ex = ex[r0:r1]
        a, b = (mask_b[r0:r1] & ~sel_ex), (ref[r0:r1] & ~sel_ex)

        def width(m):
            cols = np.where(m.any(axis=0))[0]
            return (cols.max() - cols.min() + 1) / PX_PER_M if len(cols) else 0.0

        wr, wb = width(b), width(a)
        print(f"   {label:16s} {iou(a, b):6.3f} {wr:10.3f} {wb:11.3f} {wb - wr:+8.3f}")
    if out:
        img = np.zeros((HCV, W, 3), np.uint8)
        both, only_ref, only_b = ref & mask_b, ref & ~mask_b, mask_b & ~ref
        img[both] = (235, 235, 235)
        img[only_ref] = (230, 60, 60)
        img[only_b] = (70, 120, 255)
        img[ex & ~ref & ~mask_b] = (40, 40, 40)
        Image.fromarray(img).save(out)


def main():
    data = np.load(sys.argv[1])
    out_base = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    for name in ("front", "side"):
        compare(name, raster(data[name]), out=(out_base.with_name(out_base.stem + f"_{name}.png") if out_base else None))


if __name__ == "__main__":
    main()
