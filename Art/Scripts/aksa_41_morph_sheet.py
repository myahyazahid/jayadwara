"""Susun grid morph target dari render aksa_41_render_morphs.py (Python sistem). Pakai: python -I aksa_41_morph_sheet.py <outdir>"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

d = Path(sys.argv[1])
files = sorted(d.glob("morph_*.png"), key=lambda f: (f.stem != "morph_netral", f.stem))
cols = 3
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 420, rows * 420), (200, 200, 200))
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB")
    ImageDraw.Draw(im).text((8, 8), f.stem[6:], fill=(0, 0, 0))
    sheet.paste(im, ((i % cols) * 420, (i // cols) * 420))
sheet.save(d / "morphs.png")
print("->", d / "morphs.png")
