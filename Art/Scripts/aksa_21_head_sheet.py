"""Aksa Iterasi 2 — lembar perbandingan kepala: konsep (kiri) vs model (kanan), depan dan samping, + 3/4 model.

Pakai: python -I Art/Scripts/aksa_21_head_sheet.py <dir_render> [out.png]
Konsep: Art/Reference/ak_head_front.png (321x485) dan ak_head_side.png (305x450), digandakan 2x supaya sama dengan render.
Output default: <dir_render>/head_compare.png (depan+samping berdampingan) dan head_q34.png tetap terpisah.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "Art" / "Reference"
src = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else src / "head_compare.png"

tiles = []
for v, size in (("front", (642, 970)), ("side", (610, 900))):
    ref = Image.open(REF / f"ak_head_{v}.png").convert("RGB").resize(size, Image.LANCZOS)
    mod = Image.open(src / f"head_{v}.png").convert("RGB")
    row = Image.new("RGB", (size[0] * 2, size[1]), (230, 230, 230))
    row.paste(ref, (0, 0))
    row.paste(mod, (size[0], 0))
    d = ImageDraw.Draw(row)
    d.text((8, 8), f"konsep {v}", fill=(0, 0, 0))
    d.text((size[0] + 8, 8), f"model {v}", fill=(0, 0, 0))
    tiles.append(row)
sheet = Image.new("RGB", (tiles[0].width + tiles[1].width, max(t.height for t in tiles)), (230, 230, 230))
sheet.paste(tiles[0], (0, 0))
sheet.paste(tiles[1], (tiles[0].width, 0))
sheet.thumbnail((2400, 1400))
sheet.save(out)
print("->", out)
