"""Jayadwara2 R4 — tekstur turunan dari atlas Tripo + geometri: BC (texel peralihan di-snap, soket mata), T_Jayadwara2_Emit (R permata, G mata),
T_Jayadwara2_Mask (RGBA zona warna: R merah, G emas, B hitam, A putih/krem; untuk recolor Kala/Kembar) + T_Jayadwara2_Mask.json (luminans referensi per zona).

  python -I Art/Scripts/make_textures_jayadwara2.py          (setelah jayadwara2_15_dump_uv.py)
Tiap texel atlas diberi posisi 3D (rasterisasi segitiga di ruang UV). Zona: permata = berlian putih di dada
(|x|<0,035, 1,40<z<1,50, menghadap depan); mata = lobus krem terang di bawah alis (|x|<0,085, 1,715<z<1,775, depan).
Permata: texel TERANG di zona (menjaga bentuk lukisan Tripo). MATA (revisi 1, 13 Okt 2026): Tripo tidak punya celah mata (hanya lobus krem), jadi
celah miring DILUKIS: dua celah meruncing (ujung dalam lebih rendah, ujung luar naik = tatapan tegas) + soket gelap di sekelilingnya pada BC.
Atlas asli Tripo disimpan sekali sebagai T_Jayadwara2_BC_src.png (sumber; jangan ditimpa); T_Jayadwara2_BC.png = hasil lukis.
Aturan IP: emissive konstan, tidak dikaitkan ke meter Sync; mata = celah miring, bukan lensa bulat.
Keluaran: Art/Export/Textures_Jayadwara2/T_Jayadwara2_Emit.png, T_Jayadwara2_BC.png + _jd2/_emit_debug.png (overlay).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import jd2_atlas as A

ROOT = Path(__file__).resolve().parents[2]
TEX = ROOT / "Art" / "Export" / "Textures_Jayadwara2"
SRC_BC = TEX / "T_Jayadwara2_BC_src.png"
if not SRC_BC.exists():
    import shutil
    shutil.copy(TEX / "T_Jayadwara2_BC.png", SRC_BC)             # atlas Tripo asli (hasil jayadwara2_14_export.py)
bc = np.asarray(Image.open(SRC_BC).convert("RGB"), np.float32) / 255.0
H, W = bc.shape[:2]

P = A.texel_positions(W, H)

# --- R4: snap texel "lain" (peralihan emas<->merah, tepi anti-alias; atlas Tripo sendiri bersih: tanpa hijau/biru/ungu) ke warna tetangga valid terdekat
_used = ~np.isnan(P[..., 0])
_lab0 = A.zone_labels(bc)
_stray = _used & (_lab0 == 4)
_valid = ~_stray
for _it in range(8):
    if not _stray.any():
        break
    _acc = np.zeros_like(bc)
    _cnt = np.zeros(bc.shape[:2], np.float32)
    for _dy in (-1, 0, 1):
        for _dx in (-1, 0, 1):
            if _dy == 0 and _dx == 0:
                continue
            _v = np.roll(_valid, (_dy, _dx), (0, 1))
            _acc += np.roll(bc, (_dy, _dx), (0, 1)) * _v[..., None]
            _cnt += _v
    _fill = _stray & (_cnt > 0)
    bc[_fill] = _acc[_fill] / _cnt[_fill, None]
    _valid = _valid | _fill
    _stray = _stray & ~_fill
print(f"texel peralihan di-snap: {int((_used & (_lab0 == 4)).sum())}; sisa {int(_stray.sum())}")

x, y, z = P[..., 0], P[..., 1], P[..., 2]
bright = bc.min(axis=2)                      # texel putih/krem terang -> min kanal tinggi
lum = bc.mean(axis=2)
front = y < -0.12
gem = front & (np.abs(x) < 0.035) & (z > 1.40) & (z < 1.50) & (bright > 0.70)
# --- mata: dua celah meruncing (kiri +X, kanan -X); (x, z) meter; ujung dalam lebih rendah, ujung luar naik
EYE_IN, EYE_OUT = (0.022, 1.727), (0.102, 1.769)        # revisi 4: pita PANJANG ke samping-belakang kepala, ujung luar naik & runcing (seperti Jayadwara lama)
EYE_HALF_MAX = 0.0115                                    # setengah tebal maksimum (m) di dekat ujung dalam; meruncing ke 0 di ujung luar
EYE_TAPER = 0.65                                          # eksponen runcing: half(t) = MAX * (1 - t)^TAPER
EYE_MIN = 0.0015
EYE_AA = 0.003                                           # lebar anti-alias (≈ 1 texel di wajah)
SOCKET = 0.006                                           # tepi soket gelap di luar celah (m)


def slit_dist(sgn):
    """(jarak ke garis tengah celah, posisi 0..1 di sepanjang celah)"""
    a = np.array([sgn * EYE_IN[0], EYE_IN[1]])
    b = np.array([sgn * EYE_OUT[0], EYE_OUT[1]])
    ab = b - a
    q = np.stack([x, z], axis=-1) - a
    t = np.clip((q @ ab) / (ab @ ab), 0.0, 1.0)
    d = np.linalg.norm(q - t[..., None] * ab, axis=-1)
    return d, t


eye = np.zeros((H, W), np.float32)
socket = np.zeros((H, W), np.float32)
for sgn in (1.0, -1.0):
    d, t = slit_dist(sgn)
    half = np.maximum(EYE_HALF_MAX * (1 - t) ** EYE_TAPER, EYE_MIN)
    zone = (y < -0.03) & (y > -0.20) & (np.abs(x) < 0.13)       # depan + sisi wajah (visor melingkar ke samping)
    eye = np.maximum(eye, np.where(zone, np.clip((half - d) / EYE_AA + 0.5, 0.0, 1.0), 0.0))
    socket = np.maximum(socket, np.where(zone, np.clip(1.0 - (d - half) / SOCKET, 0.0, 1.0), 0.0).astype(np.float32))
socket[np.isnan(x)] = 0.0
# revisi 5: pita mata berhenti di batas area merah (sirip/pipi merah di pelipis) — dipotong menurut warna ASLI atlas Tripo
redness = np.clip((bc[..., 0] - np.maximum(bc[..., 1], bc[..., 2]) - 0.12) / 0.16, 0.0, 1.0)
redness = np.asarray(Image.fromarray((redness * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255.0
eye = eye * (1.0 - redness)
socket = socket * (1.0 - redness)


def soften(mask, grow=2, blur=1.2):
    im = Image.fromarray((mask * 255).astype(np.uint8))
    if grow > 0:
        im = im.filter(ImageFilter.MaxFilter(2 * grow + 1))
    im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im)


emit = np.zeros((H, W, 3), np.uint8)
emit[..., 0] = soften(gem)
emit[..., 1] = np.asarray(Image.fromarray((np.clip(eye, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0)))
Image.fromarray(emit).save(TEX / "T_Jayadwara2_Emit.png")
# BC: soket gelap (merah-hitam tua) di sekeliling celah; inti celah sendiri terang krem agar tetap terbaca bila emissive dimatikan
dark = np.array([0.045, 0.02, 0.02], np.float32)
sock = np.asarray(Image.fromarray((socket * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32)[..., None] / 255.0
bc_new = bc * (1 - sock * 0.92) + dark * sock * 0.92
core = emit[..., 1:2].astype(np.float32) / 255.0
bc_new = bc_new * (1 - core) + np.array([1.0, 0.95, 0.78], np.float32) * core
Image.fromarray((np.clip(bc_new, 0, 1) * 255).astype(np.uint8)).save(TEX / "T_Jayadwara2_BC.png")
# --- R4: Mask zona warna dari BC FINAL (RGBA: R merah, G emas, B hitam, A putih/krem), tepi dilembutkan & dinormalisasi (jumlah = 1)
_labf = A.zone_labels(bc_new)
_labf[_labf == 4] = 0
_onehot = {0: _labf == 1, 1: _labf == 2, 2: _labf == 0, 3: _labf == 3}      # kanal R,G,B,A = merah, emas, hitam, putih
_ch = []
for _k in range(4):
    _im = Image.fromarray((_onehot[_k] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    _ch.append(np.asarray(_im, np.float32) / 255.0)
_m = np.stack(_ch, axis=-1)
_m[~_used] = (0.0, 0.0, 1.0, 0.0)
_m /= np.maximum(_m.sum(axis=-1, keepdims=True), 1e-6)
Image.fromarray((_m * 255 + 0.5).astype(np.uint8)).save(TEX / "T_Jayadwara2_Mask.png")


def _lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


_bl = _lin(np.clip(bc_new, 0, 1))
_luma = _bl @ np.array([0.2126, 0.7152, 0.0722], np.float32)
import json
_info = {}
for _k, _n in enumerate(("red", "gold", "black", "white")):
    _w = _m[..., _k] * _used
    _tot = float(_w.sum()) or 1.0
    _info[_n] = {"texel_share": round(float(_w.sum() / _used.sum()), 4),
                 "ref_luma_linear": round(float((_luma * _w).sum() / _tot), 4),
                 "mean_color_linear": [round(float((_bl[..., c] * _w).sum() / _tot), 4) for c in range(3)]}
json.dump(_info, open(TEX / "T_Jayadwara2_Mask.json", "w"), indent=2)
print("zona:", {k: (v["texel_share"], v["ref_luma_linear"]) for k, v in _info.items()})

dbg = (np.clip(bc_new, 0, 1) * 255).astype(np.uint8).copy()
dbg[emit[..., 0] > 40] = (0, 255, 255)
dbg[emit[..., 1] > 40] = (0, 255, 0)
Image.fromarray(dbg).resize((1024, 1024)).save(ROOT / "Art" / "Export" / "_jd2" / "_emit_debug.png")
print(f"permata {int(gem.sum())} texel, mata {int((eye > 0.5).sum())} texel (atlas {W}x{H}); posisi terpetakan {int((~np.isnan(x)).sum())}")

# --- debug: proyeksi depan zona wajah (texel -> (x, z)) dari atlas asli (kiri) dan hasil (kanan); 2000 px/m
def face_projection(img, name, x0=-0.12, x1=0.12, z0=1.67, z1=1.82, scale=2000):
    Wp, Hp = int((x1 - x0) * scale), int((z1 - z0) * scale)
    out = np.full((Hp, Wp, 3), 40, np.uint8)
    m = front & (x > x0) & (x < x1) & (z > z0) & (z < z1)
    ix = ((x[m] - x0) * scale).astype(int).clip(0, Wp - 1)
    iz = ((z1 - z[m]) * scale).astype(int).clip(0, Hp - 1)
    for dx in (0, 1):
        for dz in (0, 1):
            out[(iz + dz).clip(0, Hp - 1), (ix + dx).clip(0, Wp - 1)] = (np.clip(img[m], 0, 1) * 255).astype(np.uint8)
    return out


pa, pb = face_projection(bc, "src"), face_projection(bc_new, "new")
Image.fromarray(np.concatenate([pa, pb], axis=1)).save(ROOT / "Art" / "Export" / "_jd2" / "_face_proj.png")
