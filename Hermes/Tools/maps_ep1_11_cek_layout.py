#!/usr/bin/env python3
"""M1 — Cek data layout Ep01_LawangSapta.

Baca Art/Level/ep01_layout_v01.json, impor elev dari Art/Level/ep01_medan.py,
lalu cetak tabel: id, jenis, pos, alas (m), selisih tanah di tapak (maks - min).

Lulus jika:
- 43 objek, 11 penanda, 2 zona, 6 kamera terbaca;
- semua pos di dalam batas medan (x -340..460, y -420..280);
- objek DESA_* alasnya 0,0 m; objek CANDI_* (kecuali tangga) alasnya 35,0 m.
Selisih tanah > 2 m dicatat sebagai temuan (bukan kegagalan).

Jalankan dari WORKTREE:  python -I Hermes/Tools/maps_ep1_11_cek_layout.py
"""
import sys
import os
import json
import math

# --- path WORKTREE dari lokasi skrip ini (Hermes/Tools/...) ---
HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(WORKTREE, "Art", "Level"))
from ep01_medan import elev  # noqa: E402

LAYOUT = os.path.join(WORKTREE, "Art", "Level", "ep01_layout_v01.json")
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
    """Ambil (P, L) tapak objek sesuai jenis."""
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

findings = []
rows = []

for o in OBJEK:
    idd = o["id"]
    jenis = o["jenis"]
    yaw = o.get("yaw", 0.0)
    zrel = o.get("z_dasar_relatif", 0.0)

    if "pos" in o:
        cx, cy = o["pos"]
        P, L = footprint_pl(o)
        pts = sampel_rect(cx, cy, P, L, yaw)
        zmin, zmax, zdif = stats(pts)
        pos_str = "(%g, %g)" % (cx, cy)
    elif jenis == "tangga":
        ax, ay, az = o["dari"]
        bx, by, bz = o["ke"]
        zmin, zmax, zdif = az, bz, 0.0
        cx, cy = (ax + bx) / 2.0, (ay + by) / 2.0
        pos_str = "dari(%g,%g,%g)->ke(%g,%g,%g)" % (ax, ay, az, bx, by, bz)
    elif jenis == "dinding":
        ax, ay = o["dari"]
        bx, by = o["ke"]
        pts = sampel_seg(ax, ay, bx, by)
        zmin, zmax, zdif = stats(pts)
        cx, cy = (ax + bx) / 2.0, (ay + by) / 2.0
        pos_str = "dari(%g,%g)->ke(%g,%g)" % (ax, ay, bx, by)
    else:
        zmin = zmax = zdif = 0.0
        cx = cy = 0.0
        pos_str = "?"

    alas = zmin  # alas = elev terendah di tapak (sebelum z_dasar_relatif)
    rows.append((idd, jenis, pos_str, alas, zdif, zrel))

    if zdif > 2.0:
        findings.append("TEMUAN selisih tanah: %-26s %.2f m (>2) — tapak miring/lereng" % (idd, zdif))
    if "pos" in o and not (XMIN <= cx <= XMAX and YMIN <= cy <= YMAX):
        findings.append("GAGAL pos di luar medan: %-26s (%g, %g)" % (idd, cx, cy))

# --- cetak tabel objek ---
print("TABEL OBJEK (id | jenis | pos | alas m | selisih m | z_dasar_relatif)")
print("-" * 104)
hdr = "%-26s %-16s %-40s %7s %8s %5s" % ("id", "jenis", "pos", "alas", "selisih", "zrel")
print(hdr)
print("-" * 104)
for (idd, jenis, pos_str, alas, zdif, zrel) in rows:
    print("%-26s %-16s %-40s %7.2f %8.2f %5.1f" % (idd, jenis, pos_str, alas, zdif, zrel))
print()

# --- cek jumlah ---
n_obj = len(OBJEK)
n_pen = len(PENANDA)
n_zon = len(ZONA)
n_kam = len(KAMERA)
print("Jumlah: objek=%d (target 43) | penanda=%d (11) | zona=%d (2) | kamera=%d (6)" %
      (n_obj, n_pen, n_zon, n_kam))

# --- cek alas DESA / CANDI ---
TOL = 0.6
desa_bad = []
candi_bad = []
for (idd, jenis, pos_str, alas, zdif, zrel) in rows:
    if idd.startswith("DESA_") and abs(alas - 0.0) > TOL:
        desa_bad.append((idd, alas))
    if idd.startswith("CANDI_") and jenis != "tangga" and abs(alas - 35.0) > TOL:
        candi_bad.append((idd, alas))

print("Cek alas DESA_* = 0,0 m (tol %.1f): %s" % (TOL, "OK" if not desa_bad else "GAGAL"))
for idd, a in desa_bad:
    print("   ! %s alas=%.2f" % (idd, a))
print("Cek alas CANDI_* (kec. tangga) = 35,0 m (tol %.1f): %s" % (TOL, "OK" if not candi_bad else "GAGAL"))
for idd, a in candi_bad:
    print("   ! %s alas=%.2f" % (idd, a))

# --- cek pos penanda/kamera/zona/batas di dalam medan ---
def in_box(x, y):
    return XMIN <= x <= XMAX and YMIN <= y <= YMAX

pos_bad = []
for p in PENANDA:
    x, y = p["pos"]
    if not in_box(x, y):
        pos_bad.append("penanda %s (%g,%g)" % (p["id"], x, y))
for k in KAMERA:
    x, y = k["pos"]
    if not in_box(x, y):
        pos_bad.append("kamera %s (%g,%g)" % (k["id"], x, y))
for z in ZONA:
    xa, xb = z["x"]
    ya, yb = z["y"]
    if not (in_box(xa, ya) and in_box(xb, yb)):
        pos_bad.append("zona %s" % z["id"])
xa, xb = BATAS["x"]
ya, yb = BATAS["y"]
if not (in_box(xa, ya) and in_box(xb, yb)):
    pos_bad.append("batas_arena")

# --- ringkas temuan ---
all_findings = findings + [("GAGAL pos di luar medan: " + s) for s in pos_bad]
print()
print("Temuan (selisih > 2 m dan pos di luar medan):")
if all_findings:
    for s in all_findings:
        print("  - " + s)
else:
    print("  (tidak ada)")

# --- verdict ---
ok = (
    n_obj == 43 and n_pen == 11 and n_zon == 2 and n_kam == 6
    and not desa_bad and not candi_bad and not pos_bad
)
print()
if ok:
    print("M1 LULUS")
else:
    print("M1 GAGAL (lihat di atas)")
