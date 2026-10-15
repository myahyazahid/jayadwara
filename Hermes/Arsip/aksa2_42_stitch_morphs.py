"""Susun grid morph target Aksa2 dan buat lembar komparasi vs SK_Aksa lama."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
OUT_DIR = ROOT / "Hermes" / "Art" / "aksa2" / "Render" / "h3b"
LAMA_SHEET = ROOT / "Art" / "Export" / "_aksa_morphs.png"

EXP_NAMES = [
    "netral",
    "ak_blink_L",
    "ak_blink_R",
    "ak_smile",
    "ak_angry",
    "ak_mouth_open",
    "ak_brow_up",
    "ak_wince",
    "ak_sad",
]

cols = 3
rows = 3
tile_w, tile_h = 420, 420
sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), (220, 220, 220))

for i, name in enumerate(EXP_NAMES):
    fpath = OUT_DIR / f"morph_{name}.png"
    if fpath.exists():
        im = Image.open(fpath).convert("RGB")
        draw = ImageDraw.Draw(im)
        draw.rectangle([6, 6, 170, 28], fill=(0, 0, 0))
        draw.text((10, 8), name, fill=(255, 255, 255))
        sheet.paste(im, ((i % cols) * tile_w, (i // cols) * tile_h))

sheet_out = OUT_DIR / "morph_sheet.png"
sheet.save(sheet_out)
print(f"Morph sheet tersimpan ke: {sheet_out}")

# Lembar komparasi berdampingan
if LAMA_SHEET.exists():
    im_lama = Image.open(LAMA_SHEET).convert("RGB")
    im_baru = Image.open(sheet_out).convert("RGB")

    h_target = max(im_lama.height, im_baru.height)
    if im_lama.height != h_target:
        im_lama = im_lama.resize((int(im_lama.width * h_target / im_lama.height), h_target))
    if im_baru.height != h_target:
        im_baru = im_baru.resize((int(im_baru.width * h_target / im_baru.height), h_target))

    total_w = im_lama.width + im_baru.width
    comp = Image.new("RGB", (total_w, h_target), (180, 180, 180))
    comp.paste(im_lama, (0, 0))
    comp.paste(im_baru, (im_lama.width, 0))

    draw_c = ImageDraw.Draw(comp)
    draw_c.rectangle([10, 10, 320, 38], fill=(0, 0, 0))
    draw_c.text((16, 14), "SK_Aksa (Lama / Stylized)", fill=(255, 255, 255))
    draw_c.rectangle([im_lama.width + 10, 10, im_lama.width + 320, 38], fill=(0, 0, 0))
    draw_c.text((im_lama.width + 16, 14), "SK_Aksa2 (Baru / Realistis)", fill=(255, 255, 255))

    comp_out = OUT_DIR / "morph_compare.png"
    comp.save(comp_out)
    print(f"Lembar komparasi morph tersimpan ke: {comp_out}")

    # Buat juga thumbnail kompresi untuk vision_analyze
    comp_thumb = comp.copy()
    comp_thumb.thumbnail((1200, 1200))
    comp_thumb.save(OUT_DIR / "morph_compare_thumb.jpg", quality=85)
    print("Thumbnail komparasi morph tersimpan.")
