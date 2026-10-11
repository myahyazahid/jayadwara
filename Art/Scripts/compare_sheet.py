"""Gabungkan render (render_compare.py) dengan reference plane: [konsep | model | tumpang] per view.

Pakai: python -I Art/Scripts/compare_sheet.py <render_dir> <out.png> [scale]
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RD = Path(sys.argv[1])
OUT = Path(sys.argv[2])
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
BG = (238, 238, 238)
cols = []
for v in ("front", "side", "back"):
    rp = RD / f"render_{v}.png"
    if not rp.exists():
        continue
    ref = Image.open(ROOT / "Art" / "Reference" / f"jd_ref_{v}.png").convert("RGBA")
    ren = Image.open(rp).convert("RGBA")
    a = Image.new("RGBA", ref.size, BG + (255,))
    a.alpha_composite(ref)
    b = Image.new("RGBA", ref.size, BG + (255,))
    b.alpha_composite(ren)
    c = Image.new("RGBA", ref.size, BG + (255,))
    ghost = ref.copy()
    ghost.putalpha(ghost.getchannel("A").point(lambda x: x * 0.45))
    c.alpha_composite(ren)
    c.alpha_composite(ghost)
    cols += [a, b, c]
W = sum(i.width for i in cols) + 6 * (len(cols) - 1)
sheet = Image.new("RGB", (W, cols[0].height), (255, 0, 255))
x = 0
for i in cols:
    sheet.paste(i.convert("RGB"), (x, 0))
    x += i.width + 6
sheet = sheet.resize((int(sheet.width * SCALE), int(sheet.height * SCALE)), Image.LANCZOS)
sheet.save(OUT)
print(OUT, sheet.size)
