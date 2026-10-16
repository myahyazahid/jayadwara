"""V7 — panjang rute Aksa di permukaan medan + waktu jalan + rincian per ruas.

Adaptasi `maps_ep1_70_rute.py` v01 (skrip v01 TIDAK diubah). Beda v02:
rute diambil dari `rute_aksa` (15 titik) di `Art/Level/ep01_layout_v02.json`
(bukan rangkaian RAM + penanda seperti v01), dan tinggi tiap sampel = `elev(x, y)`
dari `Art/Level/ep01_medan_v02.py`.

Ruas dikelompokkan mengikuti tonggak cerita:
START -> ★1 -> ★2 -> kaki tangga -> tangga -> ★3 (prasasti).
Target panduan V7: panjang permukaan **±735 m**; waktu pakai MaxWalkSpeed 500 cm/s.

Pakai (dari WORKTREE): python -X utf8 -I Hermes/Tools/maps_ep1_v02_70_rute.py
"""
import json
import math
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
from ep01_medan_v02 import elev  # noqa: E402

WALK_CM_S = 500.0     # MaxWalkSpeed Aksa (BP_Aksa2)
LANGKAH_M = 1.0       # jarak antar sampel, meter
TARGET_M = 735.0      # target panduan V7 (+/-)

with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
TITIK = [(float(x), float(y)) for x, y in DATA["rute_aksa"]]
PENANDA = {p["id"]: (float(p["pos"][0]), float(p["pos"][1])) for p in DATA["penanda"]}

# tonggak -> indeks titik rute (dicek di main)
TONGGAK = [
    (0, "START", "START (desa, mobil DWARA)"),
    (6, "CLUE_1_JejakEnergi", "★1 jejak energi (bibir galian barat)"),
    (9, "CLUE_2_Tulang", "★2 tulang bergeser"),
    (12, None, "kaki tangga (0,142)"),
    (13, None, "atas tangga (0,167)"),
    (14, "CLUE_3_Prasasti", "★3 prasasti"),
]
GRUP = [(0, 6, "START -> ★1 (desa, jalan setapak turun ke bibir galian)"),
        (6, 9, "★1 -> ★2 (masuk galian, dasar)"),
        (9, 12, "★2 -> kaki tangga (dasar -> mulut galian)"),
        (12, 13, "tangga (naik, 28 balok)"),
        (13, 14, "atas tangga -> ★3 (prasasti)")]


def ruas(a, b, langkah=LANGKAH_M):
    """Panjang permukaan a->b (sampel tiap `langkah` m) + z awal/akhir + lereng maks."""
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(math.ceil(d / langkah)))
    L = 0.0
    maks = 0.0
    z0 = z1 = None
    prev = None
    for i in range(n + 1):
        t = i / n
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        z = elev(x, y)
        if z0 is None:
            z0 = z
        z1 = z
        if prev is not None:
            datar = math.hypot(x - prev[0], y - prev[1])
            L += math.hypot(datar, z - prev[2])
            if datar > 1e-9:
                maks = max(maks, abs(z - prev[2]) / datar)
        prev = (x, y, z)
    return {"datar": d, "permukaan": L, "z0": z0, "z1": z1, "maks": maks}


def main():
    v = WALK_CM_S / 100.0
    print("RUTE AKSA v02 - panjang di permukaan medan (elev), sampel tiap %.0f m" % LANGKAH_M)
    print("MaxWalkSpeed Aksa = %.0f cm/s (%.2f m/s)" % (WALK_CM_S, v))
    print()

    # cek tonggak benar-benar duduk di koordinat penanda
    print("Tonggak rute (indeks | data x,y | elev | vs penanda):")
    for i, pid, nama in TONGGAK:
        x, y = TITIK[i]
        s = ""
        if pid and pid in PENANDA:
            px, py = PENANDA[pid]
            dd = math.hypot(px - x, py - y)
            s = "  vs %s = %.1f m %s" % (pid, dd, "OK" if dd <= 0.5 else "BEDA")
        print("  %2d | (%8.1f,%8.1f) | z=%6.2f m | %s%s" % (i, x, y, elev(x, y), nama, s))
    print()

    print("RINCIAN PER RUAS (rute_aksa: %d titik -> %d ruas)" % (len(TITIK), len(TITIK) - 1))
    print("%-4s %-18s %9s %11s %8s %8s %8s %9s" % (
        "ruas", "dari -> ke", "datar(m)", "permukaan", "z awal", "z akhir", "lereng", "waktu(s)"))
    print("-" * 88)
    tot_d = tot_L = 0.0
    for i in range(len(TITIK) - 1):
        r = ruas(TITIK[i], TITIK[i + 1])
        tot_d += r["datar"]
        tot_L += r["permukaan"]
        print("%-4d %-18s %9.2f %11.2f %8.2f %8.2f %7.1f%% %9.1f" % (
            i + 1, "(%d,%d)->(%d,%d)" % (TITIK[i][0], TITIK[i][1], TITIK[i + 1][0], TITIK[i + 1][1]),
            r["datar"], r["permukaan"], r["z0"], r["z1"], r["maks"] * 100.0, r["permukaan"] / v))
    print("-" * 88)
    print("%-23s %9.2f %11.2f %8s %8s %8s %9.1f" % ("TOTAL", tot_d, tot_L, "", "", "", tot_L / v))
    print()

    print("RINGKASAN PER TONGGAK")
    print("%-50s %9s %11s %8s %9s" % ("bagian", "datar(m)", "permukaan", "naik(m)", "waktu(s)"))
    print("-" * 92)
    for a, b, nama in GRUP:
        d = sum(ruas(TITIK[i], TITIK[i + 1])["datar"] for i in range(a, b))
        L = sum(ruas(TITIK[i], TITIK[i + 1])["permukaan"] for i in range(a, b))
        naik = elev(*TITIK[b]) - elev(*TITIK[a])
        print("%-50s %9.2f %11.2f %+8.2f %9.1f" % (nama, d, L, naik, L / v))
    print("-" * 92)
    naik_tot = elev(*TITIK[-1]) - elev(*TITIK[0])
    print("%-50s %9.2f %11.2f %+8.2f %9.1f" % ("TOTAL", tot_d, tot_L, naik_tot, tot_L / v))
    print()

    lurus = math.hypot(TITIK[-1][0] - TITIK[0][0], TITIK[-1][1] - TITIK[0][1])
    print("Jarak lurus START -> ★3 = %.1f m ; rute permukaan = %.1f m (%.2fx)" % (lurus, tot_L, tot_L / lurus))
    print("Waktu jalan %.1f s = %.1f menit (%.0f cm/s)" % (tot_L / v, tot_L / v / 60.0, WALK_CM_S))
    print("Target panduan V7 = %.0f m (+/-) ; selisih = %+.1f m (%.2f%%)" % (
        TARGET_M, tot_L - TARGET_M, (tot_L - TARGET_M) / TARGET_M * 100.0))
    print()
    lereng_maks = max(ruas(TITIK[i], TITIK[i + 1])["maks"] for i in range(len(TITIK) - 1))
    print("Lereng terjal versi elev analitik = %.0f%% (di ruas %s) -> CATATAN: elev punya diskontinuitas "
          "yang tidak diwakili grid mesh 2,5 m; ukuran lereng yang benar-benar dilalui pawn ada di "
          "maps_ep1_v02_72_rute_mesh.py (line trace)" % (
              lereng_maks * 100.0,
              max(range(len(TITIK) - 1), key=lambda i: ruas(TITIK[i], TITIK[i + 1])["maks"]) + 1))
    ok = abs(tot_L - TARGET_M) <= 0.05 * TARGET_M
    print("CEK V7 rute: %s (target %.0f +/-5%%)" % ("LULUS" if ok else "SELISIH", TARGET_M))
    print("SELESAI")


main()
