"""Aksa Iterasi 1 — susun lembar perbandingan konsep vs proxy dan hitung IoU siluet (Python sistem, bukan Blender).

Pakai: python -I Art/Scripts/aksa_12_compare_sheet.py <dir_render> [out.png]
Per view (depan, samping, belakang): kolom 1 = konsep (Art/Reference/ak_ref_*.png), kolom 2 = proxy (warna),
kolom 3 = tumpukan (merah = hanya konsep, cyan = hanya proxy, putih = beririsan). Konsep 1,75 m dan proxy 1,806 m
sama-sama 1000 px tinggi badan, jadi ditumpuk tanpa resample. IoU inti = |x| < 0,27 m dari tengah; IoU badan = inti dan z > 0,55 m (tanpa lengan dan kaki bawah, yang ditentukan pose rest Manny).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "Art" / "Reference"
src = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else src / "compare.png"
PX_PER_M = 1000 / 1.806
CORE = int(0.27 * PX_PER_M)

tiles, lines = [], []
for v in ("front", "side", "back"):
    ref = Image.open(REF / f"ak_ref_{v}.png").convert("RGBA")
    ref_mask = np.asarray(ref)[:, :, 3] > 128
    color = Image.open(src / f"{v}_color.png").convert("RGB")
    mask = np.asarray(Image.open(src / f"{v}_mask.png").convert("L")) > 128
    bg = Image.new("RGB", ref.size, (212, 212, 212))
    bg.paste(ref, mask=ref.split()[3])
    ov = np.zeros(mask.shape + (3,), np.uint8) + 30
    ov[ref_mask & ~mask] = (230, 60, 60)
    ov[mask & ~ref_mask] = (60, 200, 230)
    ov[ref_mask & mask] = (240, 240, 240)
    iou = (ref_mask & mask).sum() / max((ref_mask | mask).sum(), 1)
    cm = np.zeros_like(mask)
    cm[:, 380 - CORE:380 + CORE] = True
    rm, pm = ref_mask & cm, mask & cm
    core = (rm & pm).sum() / max((rm | pm).sum(), 1)
    reg = np.zeros_like(mask)                       # badan: tanpa lengan dan tanpa kaki bawah (pose Manny beda dari konsep)
    reg[int(1100 - 1.806 * PX_PER_M):int(1100 - 0.55 * PX_PER_M), 380 - CORE:380 + CORE] = True
    rb, pb = ref_mask & reg, mask & reg
    body = (rb & pb).sum() / max((rb | pb).sum(), 1)
    lines.append(f"{v}: IoU {iou:.3f}  inti {core:.3f}  badan {body:.3f}")
    row = Image.new("RGB", (ref.width * 3, ref.height))
    row.paste(bg, (0, 0))
    row.paste(color, (ref.width, 0))
    row.paste(Image.fromarray(ov), (ref.width * 2, 0))
    ImageDraw.Draw(row).text((8, 8), lines[-1], fill=(0, 0, 0))
    tiles.append(row.crop((0, 60, row.width, 1130)))
    t = tiles[-1].copy()
    t.thumbnail((1500, 1100))
    t.save(src / f"compare_{v}.png")
sheet = Image.new("RGB", (tiles[0].width, sum(t.height for t in tiles)))
y = 0
for t in tiles:
    sheet.paste(t, (0, y))
    y += t.height
sheet.thumbnail((1500, 1500))
sheet.save(out)
print("\n".join(lines), "\n->", out)
