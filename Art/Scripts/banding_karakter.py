"""Bandingkan hasil audit_karakter.py: model baru vs model pembanding (lama) vs konsep, dan beri vonis. Python sistem, bukan Blender.

Pakai: python -I Art/Scripts/banding_karakter.py --baru <dir audit baru> --out <dir>
        [--lama <dir audit pembanding>] [--ref ak | --ref "Hermes/Art/tuyul/Reference/ref_{v}.png" | --ref none]
        [--toleransi 5] [--iou-turun 0.05]
  --lama  hasil audit model pembanding (model lama yang digantikan, atau model sejenis yang sudah disetujui developer
          dengan PROFIL POSE YANG SAMA). Tanpa --lama: hanya cek audit + gambar, vonis = PERLU NILAI DEVELOPER.
  --ref   konsep untuk siluet: awalan di Art/Reference (ak -> ak_ref_front.png ...), pola path dengan {v} (front/side/back),
          atau none. Gambar konsep harus berkanvas sama (760x1200, 1000 px = --height audit, telapak y=1100, tengah x=380).
Hasil di <out>:
  banding_ortho.png   per tampak: konsep | lama | baru | tumpuk (merah = hanya acuan, cyan = hanya baru, putih = beririsan);
                      acuan = konsep, atau model lama kalau tanpa konsep
  banding_pose.png    per pose: lama 3/4 | baru 3/4 | lama dekat | baru dekat (render dekat sesuai profil, mis. ketiak)
  banding.md          tabel angka lama vs baru + vonis per baris; tempel ke laporan
VONIS GAGAL kalau: ada cek audit model baru yang gagal; regangan p99 pose mana pun > lama + toleransi (poin persen);
IoU badan tampak mana pun turun > --iou-turun dari model lama. Exit code 0 = LULUS, 1 = GAGAL, 3 = PERLU NILAI DEVELOPER.
Peregangan cm (tergantung kerapatan mesh) tidak menggagalkan, tapi ditandai PERIKSA kalau > lama + 3 cm.
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
ap.add_argument("--baru", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--lama")
ap.add_argument("--ref", default="ak")
ap.add_argument("--toleransi", type=float, default=5.0, help="poin persen; regangan p99 baru boleh lebih besar dari lama sebanyak ini")
ap.add_argument("--iou-turun", type=float, default=0.05)
a = ap.parse_args()
BARU, OUT = Path(a.baru), Path(a.out)
LAMA = Path(a.lama) if a.lama else None
OUT.mkdir(parents=True, exist_ok=True)
JB = json.loads((BARU / "audit.json").read_text(encoding="utf-8"))
JL = json.loads((LAMA / "audit.json").read_text(encoding="utf-8")) if LAMA else None
H = JB.get("kanvas_tinggi_m", 1.806)
HT = JB.get("tinggi_m", H)
PX_PER_M = 1000 / H
CORE = min(int(0.27 * HT / 1.806 * PX_PER_M), 379)
BG = (212, 212, 212)
MODELS = [("lama", LAMA, JL), ("baru", BARU, JB)] if LAMA else [("baru", BARU, JB)]


def ref_path(v):
    if a.ref.lower() == "none":
        return None
    p = Path(a.ref.replace("{v}", v)) if "{v}" in a.ref else ROOT / "Art" / "Reference" / f"{a.ref}_ref_{v}.png"
    return p if p.is_absolute() or p.exists() else ROOT / p


def label(img, text):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, img.width, 18), fill=(255, 255, 255))
    d.text((4, 3), text, fill=(0, 0, 0))
    return img


def iou(ref_mask, mask):
    cm = np.zeros_like(mask)
    cm[:, 380 - CORE:380 + CORE] = True
    reg = np.zeros_like(mask)                      # badan: tanpa lengan & kaki bawah (pose rest beda dari konsep)
    reg[max(int(1100 - HT * PX_PER_M), 0):int(1100 - 0.55 * HT / 1.806 * PX_PER_M), 380 - CORE:380 + CORE] = True
    f = lambda r, m: float((r & m).sum() / max((r | m).sum(), 1))
    return {"penuh": f(ref_mask, mask), "inti": f(ref_mask & cm, mask & cm), "badan": f(ref_mask & reg, mask & reg)}


def hstack(cells, gap=6):
    h = max(c.height for c in cells)
    r = Image.new("RGB", (sum(c.width for c in cells) + gap * (len(cells) - 1), h), (255, 255, 255))
    x = 0
    for c in cells:
        r.paste(c, (x, 0))
        x += c.width + gap
    return r


def vstack(rows, gap=4):
    s = Image.new("RGB", (max(r.width for r in rows), sum(r.height + gap for r in rows)), (255, 255, 255))
    y = 0
    for r in rows:
        s.paste(r, (0, y))
        y += r.height + gap
    return s


rows_md, gagal = [], []


def row(nama, lama, baru, vonis):
    rows_md.append(f"| {nama} | {lama} | {baru} | {vonis} |")
    if vonis.startswith("GAGAL"):
        gagal.append(nama)


g = lambda j, k: j[k] if j else "-"
for c in JB["cek"]:
    if not c["lulus"]:
        row(f"cek audit: {c['cek']}", "", c["detail"], "GAGAL (audit model baru)")
if JL and JL.get("profil") != JB.get("profil"):
    row("profil pose", JL.get("profil"), JB.get("profil"), "GAGAL (pembanding harus memakai profil pose yang sama)")
row("tinggi (m)", g(JL, "tinggi_m"), JB["tinggi_m"], "info")
row("tris", g(JL, "tris"), JB["tris"], "info")
row("jumlah tulang", g(JL, "jumlah_tulang"), JB["jumlah_tulang"], "info")
row("slot material", len(JL["slot_material"]) if JL else "-", len(JB["slot_material"]), "info")
row("tepi terbuka (boundary)", g(JL, "tepi_terbuka"), JB["tepi_terbuka"],
    "PERIKSA gambar dekat" if JL and JB["tepi_terbuka"] > JL["tepi_terbuka"] else "info")

# ---- ortografis
tiles = []
for v in ("front", "side", "back"):
    rp = ref_path(v)
    masks, cols = {}, []
    ref_mask = None
    if rp is not None and rp.exists():
        ref = Image.open(rp).convert("RGBA")
        ref_mask = np.asarray(ref)[:, :, 3] > 128
        k = Image.new("RGB", ref.size, BG)
        k.paste(ref, mask=ref.split()[3])
        cols.append(label(k, f"konsep {v}"))
    elif rp is not None:
        row(f"konsep {v}", "", str(rp), "GAGAL (file konsep tidak ada; pakai --ref none kalau memang tidak ada)")
    for nama, d, _ in MODELS:
        m = np.asarray(Image.open(d / f"{v}_mask.png").convert("L")) > 128
        masks[nama] = m
        t = f"{nama}"
        if ref_mask is not None:
            t += f": IoU {iou(ref_mask, m)['penuh']:.2f} badan {iou(ref_mask, m)['badan']:.2f}"
        cols.append(label(Image.open(d / f"{v}_color.png").convert("RGB"), t))
    acuan, acuan_nama = (ref_mask, "konsep") if ref_mask is not None else (masks.get("lama"), "lama")
    if acuan is not None:
        mb = masks["baru"]
        ov = np.zeros(mb.shape + (3,), np.uint8) + 30
        ov[acuan & ~mb] = (230, 60, 60)
        ov[mb & ~acuan] = (60, 200, 230)
        ov[acuan & mb] = (240, 240, 240)
        cols.append(label(Image.fromarray(ov), f"{acuan_nama} (merah) vs baru (cyan)"))
    tiles.append(hstack(cols).crop((0, 0, sum(c.width for c in cols) + 6 * (len(cols) - 1), 1130)))
    if ref_mask is not None:
        ib = iou(ref_mask, masks["baru"])["badan"]
        if LAMA:
            il = iou(ref_mask, masks["lama"])["badan"]
            row(f"IoU badan vs konsep ({v})", f"{il:.3f}", f"{ib:.3f}", f"GAGAL (turun {il - ib:.3f})" if il - ib > a.iou_turun else "OK")
        else:
            row(f"IoU badan vs konsep ({v})", "-", f"{ib:.3f}", "info")
sheet = vstack(tiles, 0)
sheet.thumbnail((2000, 2400))
sheet.save(OUT / "banding_ortho.png")

# ---- pose
pose_rows = []
for p, pb in JB["pose"].items():
    pl = JL["pose"].get(p) if JL else None
    if p != "rest":
        rb = pb["regangan_p99_persen"]
        if pl is None:
            row(f"{p}: regangan p99 (%)", "-", rb, "info")
        else:
            rl = pl["regangan_p99_persen"]
            worse = rb - rl
            row(f"{p}: regangan p99 (%)", rl, rb,
                f"GAGAL (+{worse:.1f} poin)" if worse > a.toleransi else ("LEBIH BAIK" if worse < -a.toleransi else "OK"))
            dcm = pb["peregangan_maks_cm"] - pl["peregangan_maks_cm"]
            row(f"{p}: peregangan maks (cm)", pl["peregangan_maks_cm"], pb["peregangan_maks_cm"],
                f"PERIKSA {pb['terburuk'][0][0]} (+{dcm:.1f} cm)" if dcm > 3.0 else "info")
    cells = []
    for nama, d, j in MODELS:
        if (j["pose"].get(p)) is None:
            continue
        cells.append(label(Image.open(d / f"pose_{p}_depan.png").convert("RGB"), f"{p} {nama} p99 {j['pose'][p]['regangan_p99_persen']}%"))
    for nama, d, j in MODELS:
        dk = j.get("kamera_dekat")
        f = d / f"pose_{p}_{dk}.png"
        if dk and f.exists():
            cells.append(label(Image.open(f).convert("RGB"), f"{dk} {nama}"))
    if cells:
        pose_rows.append(hstack(cells, 4))
vstack(pose_rows).save(OUT / "banding_pose.png")

vonis = "GAGAL" if gagal else ("LULUS" if LAMA else "PERLU NILAI DEVELOPER (tanpa pembanding)")
md = [f"# Banding karakter: {Path(JB['fbx']).name}" + (f" vs {Path(JL['fbx']).name}" if JL else " (tanpa pembanding)"), "",
      f"**VONIS: {vonis}**" + (f" — gagal di: {', '.join(gagal)}" if gagal else ""), "",
      f"Profil pose: {JB.get('profil')}. Toleransi regangan p99 +{a.toleransi} poin persen, IoU badan boleh turun {a.iou_turun}.", "",
      "| Ukuran | Lama | Baru | Vonis |", "|---|---|---|---|", *rows_md, "",
      "Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan)."]
(OUT / "banding.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
sys.exit(1 if gagal else (0 if LAMA else 3))
