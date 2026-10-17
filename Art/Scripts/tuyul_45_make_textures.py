"""K4.3 - Buat T_Tuyul_Emit (R=energi Kala, G=RealPulse ubun-ubun, B=ornamen) + T_Tuyul_Color (grade ke palet).

  python Art/Scripts/tuyul_45_make_textures.py

Masukan : Textures/T_Tuyul_Color_src.png (atlas Tripo asli), Art/Export/Textures_Tuyul/_work/render_k4/uv_pos.npy (posisi 3D per texel)
Keluaran: Textures/T_Tuyul_Emit.png, Textures/T_Tuyul_Color.png, Art/Export/Textures_Tuyul/_work/render_k4/emit_preview.png
Zona (dari kartu K4): pendar HANYA di mata + urat dada/lengan + ubun-ubun; G hanya di ubun-ubun.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuyul_paths as P  # noqa: E402

ROOT = P.ROOT
TEX = P.TEX
K4 = P.WORK / "render_k4"
PALET = {"kulit": (0x8E, 0x9A, 0x8B), "kulit bayangan": (0x6F, 0x7A, 0x6D), "cawat": (0x5A, 0x4A, 0x3A), "mata": (0x0B, 0x0B, 0x0B)}

pos = np.load(K4 / "uv_pos.npy")
valid = ~np.isnan(pos[:, :, 2])
x, y, z = pos[:, :, 0], pos[:, :, 1], pos[:, :, 2]
src = np.asarray(Image.open(P.WORK / "T_Tuyul_Color_k2.png").convert("RGB"), dtype=np.float32)
H, W = src.shape[:2]
r, g, b = src[:, :, 0], src[:, :, 1], src[:, :, 2]
V = src.max(axis=2)
mn = src.min(axis=2)
sat = np.where(V > 1e-6, (V - mn) / np.maximum(V, 1e-6), 0)
# atlas ASLI (masih ada merah basah) hanya dipakai untuk peta merah T_Tuyul_Emit
orig = np.asarray(Image.open(TEX / "T_Tuyul_Color_src.png").convert("RGB"), dtype=np.float32)
ro, go, bo = orig[:, :, 0], orig[:, :, 1], orig[:, :, 2]
Vo = orig.max(axis=2)
mno = orig.min(axis=2)
sato = np.where(Vo > 1e-6, (Vo - mno) / np.maximum(Vo, 1e-6), 0)

# hue 0..360
d = V - mn
hue = np.zeros_like(V)
nz = d > 1e-6
rr = nz & (V == r)
gg = nz & (V == g) & ~rr
bb = nz & (V == b) & ~rr & ~gg
hue[rr] = (60 * ((g[rr] - b[rr]) / d[rr]) + 360) % 360
hue[gg] = 60 * ((b[gg] - r[gg]) / d[gg]) + 120
hue[bb] = 60 * ((r[bb] - g[bb]) / d[bb]) + 240

ZONA = {
    "ubun-ubun": valid & (z > 0.925) & (np.abs(x) < 0.13) & (np.abs(y) < 0.13),
    "ubun-puncak": valid & (z > 0.95) & (x ** 2 + y ** 2 < 0.09 ** 2),
    "wajah": valid & (z > 0.80) & (y < -0.04),
    "dada": valid & (z > 0.45) & (z < 0.74) & (y < -0.06) & (np.abs(x) < 0.16),
    "lengan": valid & (np.abs(x) > 0.18) & (z > 0.28) & (z < 0.74),
}
MERAH = valid & (ro > 1.35 * np.maximum(go, bo)) & (ro > 70) & (sato > 0.35)

# R = energi Kala (mata + urat dada/lengan + ubun-ubun)
R = MERAH & (ZONA["wajah"] | ZONA["dada"] | ZONA["lengan"] | ZONA["ubun-ubun"])
# G = RealPulse, HANYA ubun-ubun (puncak tempurung)
G = ZONA["ubun-puncak"] & (V > 60)
# B = ornamen/uang: kuningan di pita leher/dada/pinggang
PITA = valid & (z > 0.45) & (z < 0.82) & (np.abs(x) < 0.20) & (np.abs(y) < 0.20)
B = PITA & (hue > 30) & (hue < 70) & (sat > 0.40) & (V > 90) & ~R & ~G

print("== texel mask ==")
for nm, m in [("R energi Kala", R), ("G RealPulse", G), ("B ornamen", B)]:
    print(f"  {nm:16s} {int(m.sum()):8d}  ({100*m.sum()/max(1,int(valid.sum())):.2f}% permukaan)")
print("  rincian R: wajah", int((MERAH & ZONA['wajah']).sum()), " dada", int((MERAH & ZONA['dada']).sum()),
      " lengan", int((MERAH & ZONA['lengan']).sum()), " ubun", int((MERAH & ZONA['ubun-ubun']).sum()))
print("  zona ubun-puncak (z>0.95, r<9cm):", int(ZONA["ubun-puncak"].sum()), "texel")

# ---- simpan emit (RGBA, kanal R/G/B terpisah)
emit = np.zeros((H, W, 4), dtype=np.uint8)
emit[:, :, 0] = (R * 255).astype(np.uint8)
emit[:, :, 1] = (G * 255).astype(np.uint8)
emit[:, :, 2] = (B * 255).astype(np.uint8)
emit[:, :, 3] = 255
Image.fromarray(emit, "RGBA").save(TEX / "T_Tuyul_Emit.png")
print("simpan T_Tuyul_Emit.png", (TEX / "T_Tuyul_Emit.png").stat().st_size, "byte")

prev = np.zeros((H, W, 3), dtype=np.uint8)
prev[:, :, 0] = emit[:, :, 0]
prev[:, :, 1] = emit[:, :, 1]
prev[:, :, 2] = emit[:, :, 2]
Image.fromarray(prev, "RGB").resize((900, 900)).save(K4 / "emit_preview.png")

# ---- grade warna ke palet terkunci (kurva gamma per kanal, ruang linear)
def s2l(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def l2s(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


kulit = valid & ~MERAH & ~B & (z > 0.20) & (z < 0.80)
cur = np.median(src[kulit], axis=0)

# Target warna: dari KONSEP developer (Reference/tuyul_v01.png), dihitung ulang di sini (bukan tebakan).
ref = np.asarray(Image.open(P.REFERENCE).convert("RGB"), dtype=np.float32)
edge = np.concatenate([ref[0], ref[-1], ref[:, 0], ref[:, -1]])
bgref = np.median(edge, axis=0)
mref = np.abs(ref - bgref).max(axis=2) > 30
vref = ref[mref]
mxr, mnr = vref.max(axis=1), vref.min(axis=1)
satr = np.where(mxr > 1e-6, (mxr - mnr) / np.maximum(mxr, 1e-6), 0)
kulref = (mxr > 60) & (mxr < 230) & (satr < 0.45)
target = np.median(vref[kulref], axis=0)
tint = target.astype(int)
lin_cur = s2l(cur)
lin_tgt = s2l(target)
print(f"\nwarna kulit: atlas #{int(cur[0]):02X}{int(cur[1]):02X}{int(cur[2]):02X} -> konsep #{tint[0]:02X}{tint[1]:02X}{tint[2]:02X}"
      f"   (palet kartu #8E9A8B -> TIDAK dipakai: lihat laporan K4)")
print(f"  konsep p75 #{int(np.percentile(vref[kulref],75,axis=0)[0]):02X}{int(np.percentile(vref[kulref],75,axis=0)[1]):02X}{int(np.percentile(vref[kulref],75,axis=0)[2]):02X}")

lin = s2l(src)
# tone-map eksponensial per kanal: out = 1 - exp(-k*in). Titik hitam tetap 0 (celah gelap tetap gelap),
# midtone terangkat ke warna konsep, highlight terkompresi (tidak klip).
kk = -np.log(np.maximum(1.0 - np.clip(lin_tgt, 0, 0.999), 1e-9)) / np.maximum(lin_cur, 1e-9)
print("  k tone-map per kanal:", np.round(kk, 3))
graded = l2s(1.0 - np.exp(-kk.reshape(1, 1, 3) * lin))
out = np.clip(graded, 0, 255).astype(np.uint8)
Image.fromarray(out, "RGB").save(TEX / "T_Tuyul_Color.png")
print("simpan T_Tuyul_Color.png", (TEX / "T_Tuyul_Color.png").stat().st_size, "byte")

# ---- tabel hex per zona sebelum/sesudah
ZN = {
    "kepala": valid & (z > 0.80), "ubun-ubun": ZONA["ubun-ubun"], "wajah": ZONA["wajah"],
    "dada": ZONA["dada"], "lengan": ZONA["lengan"],
    "pinggul/cawat": valid & (z > 0.18) & (z < 0.46) & (np.abs(x) < 0.22), "kaki": valid & (z < 0.20),
    "kulit (semua)": kulit, "ornamen B": B, "mata/urat R": R,
}
print("\n== hex per zona (median sRGB) ==")
print(f"  {'zona':14s} {'sebelum':>9s} {'sesudah':>9s}   n")
for k, m in ZN.items():
    if m.sum() == 0:
        continue
    a = np.median(src[m], axis=0)
    c = np.median(out[m], axis=0)
    print(f"  {k:14s} #{int(a[0]):02X}{int(a[1]):02X}{int(a[2]):02X}  #{int(c[0]):02X}{int(c[1]):02X}{int(c[2]):02X}   {int(m.sum())}")
qref = np.percentile(vref[kulref], 75, axis=0)
qa = np.percentile(src[kulit], 75, axis=0)
qc = np.percentile(out[kulit], 75, axis=0)
print(f"\n  kulit p75  atlas #{int(qa[0]):02X}{int(qa[1]):02X}{int(qa[2]):02X} -> sesudah #{int(qc[0]):02X}{int(qc[1]):02X}{int(qc[2]):02X}   (konsep #{int(qref[0]):02X}{int(qref[1]):02X}{int(qref[2]):02X})")
qd = np.percentile(out[kulit], 10, axis=0)
print(f"  kulit p10  atlas #{int(np.percentile(src[kulit],10,axis=0)[0]):02X}{int(np.percentile(src[kulit],10,axis=0)[1]):02X}{int(np.percentile(src[kulit],10,axis=0)[2]):02X} -> sesudah #{int(qd[0]):02X}{int(qd[1]):02X}{int(qd[2]):02X}  (bayangan tetap gelap)")
print("  palet kartu (usulan docs/27, dikunci K0): kulit #8E9A8B bayangan #6F7A6D cawat #5A4A3A mata #0B0B0B")
