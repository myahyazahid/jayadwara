"""Bandingkan dua hasil audit_karakter.py (model lama vs model baru) + konsep, dan beri vonis. Python sistem, bukan Blender.

Pakai: python -I Art/Scripts/banding_karakter.py --lama <dir audit lama> --baru <dir audit baru> --out <dir>
        [--ref ak] [--toleransi 5] [--iou-turun 0.05]
Hasil di <out>:
  banding_ortho.png   per tampak (depan/samping/belakang): konsep | lama | baru | tumpuk konsep vs baru
                      (merah = hanya konsep, cyan = hanya baru, putih = beririsan) + IoU
  banding_pose.png    per pose: lama 3/4 | baru 3/4 | lama ketiak dari bawah | baru ketiak dari bawah + peregangan
  banding.md          tabel angka lama vs baru dengan vonis per baris; tempel ke laporan
VONIS GAGAL kalau: ada cek audit model baru yang gagal; regangan p99 pose mana pun > lama + toleransi (poin persen);
IoU badan tampak mana pun turun > --iou-turun dari model lama. Exit code 0 = LULUS, 1 = GAGAL.
Peregangan cm (tergantung kerapatan mesh) tidak menggagalkan, tapi ditandai PERIKSA kalau > lama + 3 cm: lihat tulang yang disebut.
Gambar tetap harus DILIHAT: angka tidak menangkap lubang kecil, tekstur salah, atau kulit tembus baju.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("--lama", required=True)
ap.add_argument("--baru", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--ref", default="ak", help="awalan reference plane di Art/Reference (ak = Aksa)")
ap.add_argument("--toleransi", type=float, default=5.0, help="poin persen; regangan p99 baru boleh lebih besar dari lama sebanyak ini")
ap.add_argument("--iou-turun", type=float, default=0.05)
a = ap.parse_args()
LAMA, BARU, OUT = Path(a.lama), Path(a.baru), Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
JL = json.loads((LAMA / "audit.json").read_text(encoding="utf-8"))
JB = json.loads((BARU / "audit.json").read_text(encoding="utf-8"))
H = JB.get("kanvas_tinggi_m", 1.806)
PX_PER_M = 1000 / H
CORE = int(0.27 * PX_PER_M)
BG = (212, 212, 212)


def label(img, text, color=(0, 0, 0)):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, img.width, 18), fill=(255, 255, 255))
    d.text((4, 3), text, fill=color)
    return img


def iou(ref_mask, mask):
    cm = np.zeros_like(mask)
    cm[:, 380 - CORE:380 + CORE] = True
    reg = np.zeros_like(mask)                      # badan: tanpa lengan & kaki bawah (pose Manny beda dari konsep)
    reg[int(1100 - H * PX_PER_M):int(1100 - 0.55 * PX_PER_M), 380 - CORE:380 + CORE] = True
    f = lambda r, m: float((r & m).sum() / max((r | m).sum(), 1))
    return {"penuh": f(ref_mask, mask), "inti": f(ref_mask & cm, mask & cm), "badan": f(ref_mask & reg, mask & reg)}


rows_md, gagal = [], []


def row(nama, lama, baru, vonis):
    rows_md.append(f"| {nama} | {lama} | {baru} | {vonis} |")
    if vonis.startswith("GAGAL"):
        gagal.append(nama)


# ---- cek audit model baru
for c in JB["cek"]:
    if not c["lulus"]:
        row(f"cek audit: {c['cek']}", "", c["detail"], "GAGAL (audit model baru)")
row("tinggi (m)", JL["tinggi_m"], JB["tinggi_m"], "info")
row("tris", JL["tris"], JB["tris"], "info")
row("jumlah tulang", JL["jumlah_tulang"], JB["jumlah_tulang"], "info")
row("slot material", len(JL["slot_material"]), len(JB["slot_material"]), "info")
row("tepi terbuka (boundary)", JL["tepi_terbuka"], JB["tepi_terbuka"],
    "PERIKSA gambar ketiak" if JB["tepi_terbuka"] > JL["tepi_terbuka"] else "info")

# ---- ortografis vs konsep
tiles = []
for v in ("front", "side", "back"):
    ref = Image.open(ROOT / "Art" / "Reference" / f"{a.ref}_ref_{v}.png").convert("RGBA")
    ref_mask = np.asarray(ref)[:, :, 3] > 128
    res = {}
    cols = []
    k = Image.new("RGB", ref.size, BG)
    k.paste(ref, mask=ref.split()[3])
    cols.append(label(k, f"konsep {v}"))
    for nama, d in (("lama", LAMA), ("baru", BARU)):
        m = np.asarray(Image.open(d / f"{v}_mask.png").convert("L")) > 128
        res[nama] = iou(ref_mask, m)
        cols.append(label(Image.open(d / f"{v}_color.png").convert("RGB"),
                          f"{nama}: IoU {res[nama]['penuh']:.2f} badan {res[nama]['badan']:.2f}"))
        if nama == "baru":
            ov = np.zeros(m.shape + (3,), np.uint8) + 30
            ov[ref_mask & ~m] = (230, 60, 60)
            ov[m & ~ref_mask] = (60, 200, 230)
            ov[ref_mask & m] = (240, 240, 240)
            cols.append(label(Image.fromarray(ov), "konsep (merah) vs baru (cyan)"))
    t = Image.new("RGB", (sum(c.width for c in cols) + 6 * 3, ref.height), (255, 0, 255))
    x = 0
    for c in cols:
        t.paste(c, (x, 0))
        x += c.width + 6
    tiles.append(t.crop((0, 0, t.width, 1130)))
    turun = res["lama"]["badan"] - res["baru"]["badan"]
    row(f"IoU badan vs konsep ({v})", f"{res['lama']['badan']:.3f}", f"{res['baru']['badan']:.3f}",
        f"GAGAL (turun {turun:.3f})" if turun > a.iou_turun else "OK")
sheet = Image.new("RGB", (tiles[0].width, sum(t.height for t in tiles)), (255, 255, 255))
y = 0
for t in tiles:
    sheet.paste(t, (0, y))
    y += t.height
sheet.thumbnail((2000, 2400))
sheet.save(OUT / "banding_ortho.png")

# ---- pose
pose_rows = []
for p, pb in JB["pose"].items():
    pl = JL["pose"].get(p)
    sb = pb["peregangan_maks_cm"]
    sl = pl["peregangan_maks_cm"] if pl else None
    if p != "rest":
        rb = pb["regangan_p99_persen"]
        rl = pl["regangan_p99_persen"] if pl else None
        if rl is None:
            row(f"{p}: regangan p99 (%)", "-", rb, "info")
        else:
            worse = rb - rl
            vonis = f"GAGAL (+{worse:.1f} poin)" if worse > a.toleransi else ("LEBIH BAIK" if worse < -a.toleransi else "OK")
            row(f"{p}: regangan p99 (%)", rl, rb, vonis)
            dcm = sb - sl
            row(f"{p}: peregangan maks (cm)", sl, sb,
                f"PERIKSA {pb['terburuk'][0][0]} (+{dcm:.1f} cm)" if dcm > 3.0 else "info")
    cells = []
    for nama, d, val in (("lama", LAMA, sl), ("baru", BARU, sb)):
        cells.append(label(Image.open(d / f"pose_{p}_depan.png").convert("RGB"), f"{p} {nama} {val} cm"))
    for nama, d in (("lama", LAMA), ("baru", BARU)):
        im = Image.open(d / f"pose_{p}_bawah.png").convert("RGB")
        cells.append(label(im, f"ketiak {nama}"))
    h = max(c.height for c in cells)
    r = Image.new("RGB", (sum(c.width for c in cells) + 4 * 3, h), (255, 255, 255))
    x = 0
    for c in cells:
        r.paste(c, (x, 0))
        x += c.width + 4
    pose_rows.append(r)
ps = Image.new("RGB", (max(r.width for r in pose_rows), sum(r.height + 4 for r in pose_rows)), (255, 255, 255))
y = 0
for r in pose_rows:
    ps.paste(r, (0, y))
    y += r.height + 4
ps.save(OUT / "banding_pose.png")

vonis = "GAGAL" if gagal else "LULUS"
md = [f"# Banding karakter: {Path(JB['fbx']).name} vs {Path(JL['fbx']).name}", "",
      f"**VONIS: {vonis}**" + (f" — gagal di: {', '.join(gagal)}" if gagal else ""), "",
      f"Toleransi regangan p99 +{a.toleransi} poin persen, IoU badan boleh turun {a.iou_turun}.", "",
      "| Ukuran | Lama | Baru | Vonis |", "|---|---|---|---|", *rows_md, "",
      "Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan)."]
(OUT / "banding.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
sys.exit(1 if gagal else 0)
