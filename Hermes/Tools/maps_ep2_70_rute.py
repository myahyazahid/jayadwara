"""MK7 — Panjang rute investigasi & kejar Ep02 (Unreal Editor Python, via Tools/ue_remote.py).

Hitung panjang `rute_investigasi` (target +/-560 m) dan `rute_kejar` (target +/-1.266 m)
dari `Art/Level/ep02_layout_v02.json`:
- resample polyline 2D tiap 1 m;
- **tinggi = permukaan pertama line trace dari z = elev(x,y) + 200 cm** (tepat di atas
  permukaan yang diinjak; jadi tanah gang/jalan & atap-naik ikut terhitung, tapi bukan
  overhang yang dilewati di bawahnya: dek jalan layang / atap rumah tinggi);
- panjang = jumlah jarak 3D antar-sampel; cetak per ruas (antar-titik waypoint);
- waktu @500 cm/s (= 5 m/s).
Verifikasi: |panjang - target| <= 3 %.

Pembanding (dilaporkan, bukan gate): panjang 2D datar (= metode generator `panjang()`),
dan panjang dengan tinggi = permukaan pertama trace dari 60 m (over-count karena segmen
lurus rute menclok atap rumah & titik START di bawah dek layang).

Read-only: tidak mengubah level (tak ada spawn/save).

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep2_70_rute.py
"""
import os
import sys
import json
import math

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art", "Level", "ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)

RUTE = {
    "rute_investigasi": (DATA["rute_investigasi"], 560.0),
    "rute_kejar": (DATA["rute_kejar"], 1266.0),
}
STEP = 1.0        # m, jarak antar-sampel
SPEED = 5.0       # m/s (500 cm/s)
TOL = 0.03        # 3 %
Z_SKY = 6000.0    # cm, awal trace pembanding "langit"
Z_OFF = 200.0     # cm, trace tepat di atas permukaan yang diinjak

problems = []
WORLD = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def log(m):
    unreal.log(f"[MK7] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[MK7] {m}")


def _trace(x, y, z0):
    r = unreal.SystemLibrary.line_trace_single(
        WORLD, unreal.Vector(x * 100.0, -y * 100.0, z0), unreal.Vector(x * 100.0, -y * 100.0, z0 - 1500.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if r is None:
        return M.elev(x, y)
    loc = r.to_tuple()[4]
    return (loc.z / 100.0) if loc is not None else M.elev(x, y)


def tinggi_diinjak(x, y):
    """Permukaan pertama trace dari elev(x,y)+2 m -> tanah/atap-naik yang diinjak (meter)."""
    return _trace(x, y, M.elev(x, y) * 100.0 + Z_OFF)


def tinggi_langit(x, y):
    """Permukaan pertama trace dari 60 m -> bisa kena overhang (dek/atap tinggi) (meter)."""
    r = unreal.SystemLibrary.line_trace_single(
        WORLD, unreal.Vector(x * 100.0, -y * 100.0, Z_SKY), unreal.Vector(x * 100.0, -y * 100.0, -200.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if r is None:
        return M.elev(x, y)
    loc = r.to_tuple()[4]
    return (loc.z / 100.0) if loc is not None else M.elev(x, y)


def panjang_rute(pts):
    """Resample tiap STEP m. Kembalikan (total_2d, total_3d, ruas[]) dgn tinggi_diinjak."""
    tot2d = 0.0
    tot3d = 0.0
    ruas = []
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        seg2d = math.hypot(bx - ax, by - ay)
        n = max(1, int(round(seg2d / STEP)))
        zs = []
        prev = None
        seg3d = 0.0
        for j in range(n + 1):
            t = j / n
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t
            z = tinggi_diinjak(x, y)
            zs.append(z)
            cur = (x, y, z)
            if prev is not None:
                seg3d += math.dist(prev, cur)
            prev = cur
        ruas.append({"i": i + 1, "dari": (ax, ay), "ke": (bx, by),
                     "seg2d": seg2d, "seg3d": seg3d, "zmin": min(zs), "zmax": max(zs)})
        tot2d += seg2d
        tot3d += seg3d
    return tot2d, tot3d, ruas


def panjang_datar(pts):
    """Panjang 2D datar = metode generator `panjang()` (tanpa tinggi)."""
    tot = 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, int(round(math.hypot(bx - ax, by - ay) / STEP)))
        px, py = ax, ay
        for j in range(1, n + 1):
            t = j / n
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t
            tot += math.hypot(x - px, y - py)
            px, py = x, y
    return tot


def main():
    log("=" * 86)
    log("MK7 — Panjang rute investigasi & kejar (sampel 1 m; tinggi = permukaan pertama")
    log("       trace dari elev+2 m / 'permukaan yang diinjak'; @500 cm/s)")
    log("=" * 86)
    semua_ok = True
    for nama, (pts, target) in RUTE.items():
        tot2d, tot3d, ruas = panjang_rute(pts)
        datar = panjang_datar(pts)
        waktu = tot3d / SPEED
        diff = (tot3d - target) / target * 100.0
        ok = abs(diff) <= TOL * 100.0
        semua_ok = semua_ok and ok
        log("")
        log(f"--- {nama}: {len(pts)} titik, target {target:.0f} m ---")
        log(f"{'ruas':>4} {'dari':>16} {'ke':>16} {'2D m':>8} {'3D m':>8} {'zmin':>7} {'zmax':>7}")
        for r in ruas:
            log(f"{r['i']:>4} "
                f"{('(%g,%g)' % r['dari']):>16} {('(%g,%g)' % r['ke']):>16} "
                f"{r['seg2d']:>8.2f} {r['seg3d']:>8.2f} {r['zmin']:>7.2f} {r['zmax']:>7.2f}")
        log(f"  TOTAL 3D (diinjak) = {tot3d:.2f} m | target {target:.0f} m | selisih {diff:+.2f} % "
            f"| waktu @5 m/s = {waktu:.1f} s ({waktu / 60:.2f} menit) -> {'OK' if ok else 'GAGAL'}")
        log(f"  [pembanding] 2D datar (generator) = {datar:.2f} m | 2D polylin = {tot2d:.2f} m")
        if not ok:
            fail(f"{nama}: {tot3d:.2f} m di luar +/-3 % dari {target:.0f} m (selisih {diff:+.2f} %)")

    log("")
    log("--- pembanding: tinggi = permukaan pertama trace dari 60 m (over-count) ---")
    for nama, (pts, target) in RUTE.items():
        prev = None
        tot = 0.0
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = max(1, int(round(math.hypot(bx - ax, by - ay) / STEP)))
            for j in range(n + 1):
                t = j / n
                x = ax + (bx - ax) * t
                y = ay + (by - ay) * t
                cur = (x, y, tinggi_langit(x, y))
                if prev is not None:
                    tot += math.dist(prev, cur)
                prev = cur
        log(f"  {nama}: {tot:.2f} m ({(tot - target) / target * 100:+.2f} % vs target {target:.0f} m)")

    log("")
    log("=" * 86)
    if problems:
        log(f"CEK MK7: GAGAL — {len(problems)} masalah")
        for p in problems:
            log(f"  - {p}")
        sys.exit(1)
    log("CEK MK7: LULUS — kedua rute (tinggi = permukaan yang diinjak) dalam +/-3 % target")
    log("=" * 86)


main()
