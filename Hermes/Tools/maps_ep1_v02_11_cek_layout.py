#!/usr/bin/env python3
"""V1 — Cek data layout Ep01_LawangSapta **v02**.

Baca Art/Level/ep01_layout_v02.json, impor elev dari Art/Level/ep01_medan_v02.py,
lalu cetak tabel: id, jenis, pos, alas (m), selisih tanah di tapak (maks - min).

Aturan alas v02 (bagian 2 panduan):
- objek TANPA "z": alas = elev terendah di tapak (seperti v01);
- objek DENGAN "z": alas = z absolut (mis. gelagar tol z=40, latar jauh z=0).
Objek latar jauh LATAR_* memang di luar medan (dibiarkan, bukan kegagalan).

Lulus jika:
- 88 objek, 13 penanda, 4 zona, 8 kamera, 775 pohon, 30 tiang terbaca;
- objek DESA_* alasnya 0,0 m; CANDI_* (kecuali tangga) alasnya 35,0 m;
- objek BASECAMP_* alasnya 25,0 m.
Selisih tanah > 2 m dicatat sebagai temuan (bukan kegagalan).

Jalankan dari WORKTREE:  python -I Hermes/Tools/maps_ep1_v02_11_cek_layout.py
"""
import sys
import os
import json
import math

# --- path WORKTREE dari lokasi skrip ini (Hermes/Tools/...) ---
HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(WORKTREE, "Art", "Level"))
from ep01_medan_v02 import elev  # noqa: E402

LAYOUT = os.path.join(WORKTREE, "Art", "Level", "ep01_layout_v02.json")
with open(LAYOUT, encoding="utf-8") as f:
    DATA = json.load(f)

MEDAN = DATA["medan"]
XMIN, XMAX = MEDAN["x_min"], MEDAN["x_max"]
YMIN, YMAX = MEDAN["y_min"], MEDAN["y_max"]


def frange(a, b, step):
    """Titik dari a ke b dengan step, selalu menyertakan kedua ujung."""
    vals = []
    x = a
    while x < b - 1e-9:
        vals.append(x)
        x += step
    if not vals or abs(vals[-1] - b) > 1e-9:
        vals.append(b)
    return vals


def rot_pt(cx, cy, u, v, yaw_deg):
    """Rotasi CCW (0 = menghadap timur/+x)."""
    a = math.radians(yaw_deg)
    ca, sa = math.cos(a), math.sin(a)
    return cx + u * ca - v * sa, cy + u * sa + v * ca


def sampel_rect(cx, cy, P, L, yaw_deg, step=1.0):
    """Sampel elev di persegi tapak P x L (meter) setelah rotasi yaw."""
    hx, hy = P / 2.0, L / 2.0
    pts = []
    us = frange(-hx, hx, step)
    vs = frange(-hy, hy, step)
    for u in us:
        for v in vs:
            wx, wy = rot_pt(cx, cy, u, v, yaw_deg)
            pts.append((wx, wy, elev(wx, wy)))
    return pts


def sampel_seg(ax, ay, bx, by, step=1.0):
    """Sampel elev sepanjang segmen dari (ax,ay) ke (bx,by)."""
    length = math.hypot(bx - ax, by - ay)
    n = max(1, int(length / step))
    pts = []
    for i in range(n + 1):
        t = i / n
        x = ax + (bx - ax) * t
        y = ay + (by - ay) * t
        pts.append((x, y, elev(x, y)))
    return pts


def stats(pts):
    zs = [p[2] for p in pts]
    return min(zs), max(zs), max(zs) - min(zs)


def footprint_pl(o):
    """Ambil (P, L) tapak objek sesuai jenis. kerucut: [diameter, diameter, tinggi]."""
    j = o["jenis"]
    if j == "candi_bertingkat":
        t0 = o["tingkat"][0]
        return t0[0], t0[1]
    uk = o["ukuran"]
    return uk[0], uk[1]


OBJEK = DATA["objek"]
PENANDA = DATA["penanda"]
ZONA = DATA["zona"]
KAMERA = DATA["kamera"]
BATAS = DATA["batas_arena"]
POHON = DATA["pohon_kelompok"]
TIANG = DATA["tiang_listrik"]

N_POHON = sum(len(v) for v in POHON.values())
N_TIANG = len(TIANG["titik"])

findings = []
rows = []
n_z = 0
n_out_medan_latar = 0

for o in OBJEK:
    idd = o["id"]
    jenis = o["jenis"]
    yaw = o.get("yaw", 0.0)
    zrel = o.get("z_dasar_relatif", 0.0)
    zabs = o.get("z", None)

    if "pos" in o:
        cx, cy = o["pos"]
        pos_str = "(%g, %g)" % (cx, cy)
        if zabs is not None:
            alas, zdif, sumber = zabs, 0.0, "z"
            n_z += 1
        else:
            P, L = footprint_pl(o)
            pts = sampel_rect(cx, cy, P, L, yaw)
            zmin, zmax, zdif = stats(pts)
            alas, sumber = zmin, "elev"
            if zdif > 2.0:
                findings.append("TEMUAN selisih tanah: %-24s %.2f m (>2) — tapak miring/lereng" % (idd, zdif))
    elif jenis == "tangga":
        ax, ay, az = o["dari"]
        bx, by, bz = o["ke"]
        alas, zdif, sumber = az, 0.0, "dari"
        cx, cy = (ax + bx) / 2.0, (ay + by) / 2.0
        pos_str = "dari(%g,%g,%g)->ke(%g,%g,%g)" % (ax, ay, az, bx, by, bz)
    elif jenis == "dinding":
        ax, ay = o["dari"]
        bx, by = o["ke"]
        pts = sampel_seg(ax, ay, bx, by)
        zmin, zmax, zdif = stats(pts)
        alas, sumber = zmin, "elev"
        cx, cy = (ax + bx) / 2.0, (ay + by) / 2.0
        pos_str = "dari(%g,%g)->ke(%g,%g)" % (ax, ay, bx, by)
    else:
        alas = zdif = 0.0
        cx = cy = 0.0
        sumber = "?"
        pos_str = "?"

    rows.append((idd, jenis, pos_str, alas, zdif, zrel, sumber))

    if "pos" in o and not (XMIN <= cx <= XMAX and YMIN <= cy <= YMAX):
        if idd.startswith("LATAR_"):
            n_out_medan_latar += 1
        else:
            findings.append("GAGAL pos di luar medan: %-24s (%g, %g)" % (idd, cx, cy))

# --- cetak tabel objek ---
print("TABEL OBJEK v02 (id | jenis | pos | alas m | selisih m | z_dasar_relatif | sumber alas)")
print("-" * 112)
print("%-24s %-16s %-40s %7s %8s %5s %6s" % ("id", "jenis", "pos", "alas", "selisih", "zrel", "sumber"))
print("-" * 112)
for (idd, jenis, pos_str, alas, zdif, zrel, sumber) in rows:
    print("%-24s %-16s %-40s %7.2f %8.2f %5.1f %6s" % (idd, jenis, pos_str, alas, zdif, zrel, sumber))
print()

# --- cek jumlah ---
n_obj = len(OBJEK)
n_pen = len(PENANDA)
n_zon = len(ZONA)
n_kam = len(KAMERA)
print("Jumlah: objek=%d (target 88) | penanda=%d (13) | zona=%d (4) | kamera=%d (8) | pohon=%d (775) | tiang=%d (30)"
      % (n_obj, n_pen, n_zon, n_kam, N_POHON, N_TIANG))
print("Objek dengan alas z absolut: %d | objek LATAR_* di luar medan (dibiarkan): %d" % (n_z, n_out_medan_latar))
print("Pohon per kelompok: " + ", ".join("%s=%d" % (k, len(v)) for k, v in POHON.items()))

# --- cek alas DESA / CANDI / BASECAMP ---
TOL = 0.6
desa_bad = []
candi_bad = []
basecamp_bad = []
for (idd, jenis, pos_str, alas, zdif, zrel, sumber) in rows:
    if idd.startswith("DESA_") and abs(alas - 0.0) > TOL:
        desa_bad.append((idd, alas))
    if idd.startswith("CANDI_") and jenis != "tangga" and abs(alas - 35.0) > TOL:
        candi_bad.append((idd, alas))
    if idd.startswith("BASECAMP_") and abs(alas - 25.0) > TOL:
        basecamp_bad.append((idd, alas))

print()
print("Cek alas DESA_* = 0,0 m (tol %.1f): %s" % (TOL, "OK" if not desa_bad else "GAGAL"))
for idd, a in desa_bad:
    print("   ! %s alas=%.2f" % (idd, a))
print("Cek alas CANDI_* (kec. tangga) = 35,0 m (tol %.1f): %s" % (TOL, "OK" if not candi_bad else "GAGAL"))
for idd, a in candi_bad:
    print("   ! %s alas=%.2f" % (idd, a))
print("Cek alas BASECAMP_* = 25,0 m (tol %.1f): %s" % (TOL, "OK" if not basecamp_bad else "GAGAL"))
for idd, a in basecamp_bad:
    print("   ! %s alas=%.2f" % (idd, a))

# --- catatan tambahan: dinding (dari->ke) dengan selisih tanah > 2 m ---
catatan_dinding = [(idd, zdif) for (idd, jenis, pos_str, alas, zdif, zrel, sumber) in rows
                   if jenis == "dinding" and zdif > 2.0]
print()
print("Catatan tambahan (dinding, tidak dicek generator): %s" %
      ("; ".join("%s %.2f m" % (i, z) for i, z in catatan_dinding) if catatan_dinding else "(tidak ada)"))

# --- ringkas temuan ---
print()
print("Temuan (selisih tanah > 2 m dan pos di luar medan selain LATAR_*):")
if findings:
    for s in findings:
        print("  - " + s)
else:
    print("  (tidak ada)")

# --- verdict ---
ok = (
    n_obj == 88 and n_pen == 13 and n_zon == 4 and n_kam == 8
    and N_POHON == 775 and N_TIANG == 30
    and not desa_bad and not candi_bad and not basecamp_bad
    and not [s for s in findings if s.startswith("GAGAL")]
)
print()
if ok:
    print("V1 LULUS")
else:
    print("V1 GAGAL (lihat di atas)")
