"""Jerangkong (jalur B) — tekstur final dari atlas Tripo: BC dibersihkan + Emit (mask) + N/ORM disalin.

Input : Art/Source/jerangkong_tripo_v01.glb (gambar tertanam: Color, NormalGL, ORM; dibaca langsung dari GLB)
        Art/Export/_jk_faces.npz (label tulang + UV per segitiga, dari jerangkong_10_build.py)
Output: Art/Export/Textures_Jerangkong/T_Jerangkong_{BC,N,ORM,Emit}.png (2048²)

- Energi Kala (docs/23 S11): piksel merah jenuh (hue -20..10°, saturasi > ±0,5) jadi mask Emit.R, dan warna dasarnya
  digelapkan (cahaya datang dari emissive, bukan cat merah). Kain tidak menyala (segitiga kain dikecualikan).
- Noda merah muda tipis di tulang: hue digeser ke hue tulang (28°), saturasi dikurangi -> tidak terbaca darah.
- Emit.G = retak titik lemah (pendar di segitiga tengkorak bagian dahi) -> parameter WeakPointPulse di UE.
- Emit.B = gelang perunggu (segitiga lengan di ketinggian gelang dengan warna patina) -> minion menyamarkan gelang (J8).
- Kotak CAP (pojok kiri-bawah, 8x8 px) = warna tulang gelap untuk tutup potongan (CAP_UV di jerangkong_10_build.py).
Normal Tripo = konvensi OpenGL (+Y), sama dengan Blender; skrip import UE membalik hijau.

Jalankan: python -I Art/Scripts/make_textures_jerangkong.py
"""
import io
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
GLB = ROOT / "Art" / "Source" / "jerangkong_tripo_v01.glb"
FACES = ROOT / "Art" / "Export" / "_jk_faces.npz"
OUT = ROOT / "Art" / "Export" / "Textures_Jerangkong"
OUT.mkdir(parents=True, exist_ok=True)

CAP_PX = 8
CAP_COLOR = (110, 82, 64)                      # tulang gelap #6E5240 (docs/23)
KALA_DARK = np.array([0.16, 0.035, 0.03])      # dasar gelap di bawah cahaya Kala
BONE_HUE = 28.0


def glb_images(path):
    data = path.read_bytes()
    assert data[:4] == b"glTF"
    off, js, binc = 12, None, None
    while off < len(data):
        ln, typ = struct.unpack_from("<I4s", data, off)
        chunk = data[off + 8: off + 8 + ln]
        if typ == b"JSON":
            js = json.loads(chunk)
        elif typ == b"BIN\x00":
            binc = chunk
        off += 8 + ln
    out = {}
    for img in js["images"]:
        bv = js["bufferViews"][img["bufferView"]]
        raw = binc[bv.get("byteOffset", 0): bv.get("byteOffset", 0) + bv["byteLength"]]
        out[img.get("name", str(len(out)))] = Image.open(io.BytesIO(raw))
    return out


def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def rgb2hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = (mx - mn) / np.maximum(mx, 1e-6)
    return h, s, mx


def hsv2rgb(h, s, v):
    c = v * s
    x = c * (1 - np.abs((h / 60) % 2 - 1))
    m = v - c
    z = np.zeros_like(h)
    k = (h // 60).astype(int) % 6
    sel = [k == i for i in range(6)]
    R = np.select(sel, [c, x, z, z, x, c])
    G = np.select(sel, [x, c, c, x, z, z])
    B = np.select(sel, [z, z, x, c, c, x])
    return np.stack([R + m, G + m, B + m], -1)


def face_mask(size, fuv, sel):
    """Rasterisasi segitiga UV terpilih (dengan pelebaran 2 px supaya tepi pulau ikut)."""
    W, H = size
    im = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(im)
    for tri in fuv[sel]:
        pts = [(float(u) * W, (1 - float(v)) * H) for u, v in tri]
        dr.polygon(pts, fill=255, outline=255)
    from PIL import ImageFilter
    return np.asarray(im.filter(ImageFilter.MaxFilter(5))).astype(float) / 255


imgs = glb_images(GLB)
key = {k.split("_")[0]: k for k in imgs}
color = imgs[key["Color"]].convert("RGB")
normal = imgs[key["NormalGL"]].convert("RGB")
orm = imgs[key["ORM"]].convert("RGB")
W, H = color.size
fz = np.load(FACES, allow_pickle=False)
labels, fuv, cen = fz["labels"], fz["fuv"], fz["centers"]

a = np.asarray(color).astype(float) / 255
h, s, v = rgb2hsv(a)
hs = np.where(h > 180, h - 360, h)
redhue = (1 - ss(10, 20, hs)) * ss(-40, -20, hs)
E = redhue * ss(0.42, 0.62, s)
cloth = face_mask((W, H), fuv, np.char.startswith(labels, "cloth"))
bone = face_mask((W, H), fuv, ~np.char.startswith(labels, "cloth"))
E = E * (1 - cloth * (1 - bone))                  # kain tidak menyala (tepi bersama tulang tetap)
smear = redhue * ss(0.15, 0.30, s) * (1 - E)
h2 = np.where(smear > 0, hs * (1 - smear) + BONE_HUE * smear, hs) % 360
s2 = s * (1 - 0.35 * smear)
bc = hsv2rgb(h2, s2, v)
# kain merah: netralkan juga (tanpa nyala) -> coklat kain
bc = bc * (1 - E[..., None] * 0.85) + KALA_DARK * E[..., None] * 0.85

# Emit.G: retak dahi = segitiga tengkorak di depan-atas
x, y, z = cen[:, 0], cen[:, 1], cen[:, 2]
forehead = (labels == "head") & (y < -0.12) & (z > 2.07)                 # di atas rongga mata
weak = face_mask((W, H), fuv, forehead) * E
# Emit.B: gelang = segitiga lengan di ketinggian gelang
arm = np.isin(labels, ["upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r"])
band = ((z > 1.52) & (z < 1.72)) | ((z > 0.78) & (z < 0.97))
orn_faces = face_mask((W, H), fuv, arm & band)
hh, sat_, val = h, s, v
patina = ss(55, 75, hh) * (1 - ss(190, 215, hh)) * ss(0.10, 0.22, sat_)      # hijau-teal kusam
bronze = ss(15, 25, hh) * (1 - ss(45, 55, hh)) * ss(0.35, 0.5, sat_) * ss(0.25, 0.4, val)
orn = np.clip(orn_faces * np.maximum(patina, bronze * 0.8) * 1.6, 0, 1)

# kotak CAP
bc8 = (np.clip(bc, 0, 1) * 255).astype(np.uint8)
bc8[H - CAP_PX:, :CAP_PX] = CAP_COLOR
emit = np.stack([E, weak, orn], -1)
emit[H - CAP_PX:, :CAP_PX] = 0
n8 = np.asarray(normal).copy()
n8[H - CAP_PX:, :CAP_PX] = (128, 128, 255)
o8 = np.asarray(orm).copy()
o8[H - CAP_PX:, :CAP_PX] = (255, 230, 0)                                      # AO 1, kasar, non-logam

Image.fromarray(bc8).save(OUT / "T_Jerangkong_BC.png")
Image.fromarray(n8).save(OUT / "T_Jerangkong_N.png")
Image.fromarray(o8).save(OUT / "T_Jerangkong_ORM.png")
Image.fromarray((np.clip(emit, 0, 1) * 255).astype(np.uint8)).save(OUT / "T_Jerangkong_Emit.png")
oa = np.asarray(orm).astype(float) / 255
print(f"atlas {W}x{H}; Kala {(E > 0.5).mean():.3f}, noda dinetralkan {(smear > 0.5).mean():.3f}, "
      f"retak {(weak > 0.3).mean():.4f}, gelang {(orn > 0.3).mean():.4f}")
print(f"ORM rata-rata R(AO)={oa[..., 0].mean():.2f} G(rough)={oa[..., 1].mean():.2f} B(metal)={oa[..., 2].mean():.2f}")
print("->", OUT)
