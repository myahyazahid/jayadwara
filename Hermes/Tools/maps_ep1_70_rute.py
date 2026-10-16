"""M7 — panjang rute Aksa di permukaan medan + perkiraan waktu jalan (Python biasa, `-I`).

Rute (Hermes/maps_ep1_hermes.md §M7):
START → CLUE_1 → turun ram timur → CLUE_2 → ram utara → kaki tangga → tangga → CLUE_3.
Tinggi tiap sampel = `elev(x, y)` (Art/Level/ep01_medan.py); sampel tiap 1 m (garis lurus antar titik).
Waktu jalan = panjang permukaan / MaxWalkSpeed Aksa (500 cm/s = 5 m/s).

Pakai (dari WORKTREE): python -I Hermes/Tools/maps_ep1_70_rute.py
"""
import json
import math
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
from ep01_medan import RAM, elev  # noqa: E402

WALK_CM_S = 500.0      # MaxWalkSpeed Aksa (BP_Aksa)
LANGKAH_M = 1.0        # jarak antar sampel, meter

with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v01.json"), encoding="utf-8") as f:
    DATA = json.load(f)
POS = {p["id"]: (float(p["pos"][0]), float(p["pos"][1])) for p in DATA["penanda"]}
RAM_PTS = {r["nama"]: ((float(r["dari"][0]), float(r["dari"][1])),
                       (float(r["ke"][0]), float(r["ke"][1]))) for r in RAM}

KAKI_TANGGA = (0.0, 87.5)     # dari PROFIL_Y ep01_medan (uji M0: elev = 28,0)
ATAS_TANGGA = (0.0, 112.5)    # ujung atas SM_Ep01_Tangga (elev = 35,0)

RUTE = [
    ("START -> CLUE_1", POS["START"], POS["CLUE_1_JejakEnergi"]),
    ("CLUE_1 -> masuk ram timur", POS["CLUE_1_JejakEnergi"], RAM_PTS["ram_timur"][0]),
    ("ram timur (turun)", RAM_PTS["ram_timur"][0], RAM_PTS["ram_timur"][1]),
    ("keluar ram timur -> CLUE_2", RAM_PTS["ram_timur"][1], POS["CLUE_2_Tulang"]),
    ("CLUE_2 -> masuk ram utara", POS["CLUE_2_Tulang"], RAM_PTS["ram_utara"][0]),
    ("ram utara (naik)", RAM_PTS["ram_utara"][0], RAM_PTS["ram_utara"][1]),
    ("keluar ram utara -> kaki tangga", RAM_PTS["ram_utara"][1], KAKI_TANGGA),
    ("tangga (naik)", KAKI_TANGGA, ATAS_TANGGA),
    ("atas tangga -> CLUE_3", ATAS_TANGGA, POS["CLUE_3_Prasasti"]),
]


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
    print("RUTE AKSA - panjang di permukaan medan (elev), sampel tiap %.0f m" % LANGKAH_M)
    print("MaxWalkSpeed Aksa = %.0f cm/s (%.2f m/s)" % (WALK_CM_S, v))
    print()
    print("Titik rute (data x, y -> UE X=%.0f*x, Y=-%.0f*y):" % (100, 100))
    titik = [RUTE[0][1]] + [b for _, _, b in RUTE]
    for (x, y) in titik:
        print("  (%8.1f, %8.1f)  z = %6.2f m" % (x, y, elev(x, y)))
    print()
    print("%-32s %9s %11s %8s %8s %8s %9s" % (
        "ruas", "datar(m)", "permukaan", "z awal", "z akhir", "lereng", "waktu(s)"))
    print("-" * 90)
    tot_d = tot_L = 0.0
    for nama, a, b in RUTE:
        r = ruas(a, b)
        tot_d += r["datar"]
        tot_L += r["permukaan"]
        print("%-32s %9.2f %11.2f %8.2f %8.2f %7.1f%% %9.1f" % (
            nama, r["datar"], r["permukaan"], r["z0"], r["z1"],
            r["maks"] * 100.0, r["permukaan"] / v))
    print("-" * 90)
    print("%-32s %9.2f %11.2f %8s %8s %8s %9.1f" % ("TOTAL", tot_d, tot_L, "", "", "", tot_L / v))
    print()
    print("Ringkas: datar %.1f m | permukaan %.1f m | naik total %.1f m | waktu %.1f s (%.1f menit)" % (
        tot_d, tot_L, sum(ruas(a, b)["z1"] - ruas(a, b)["z0"] for _, a, b in RUTE),
        tot_L / v, tot_L / v / 60.0))
    lurus = math.hypot(POS["CLUE_3_Prasasti"][0] - POS["START"][0],
                       POS["CLUE_3_Prasasti"][1] - POS["START"][1])
    print("Jarak lurus START -> CLUE_3 = %.1f m (rute %.1f m, %.2fx)" % (lurus, tot_L, tot_L / lurus))
    print("SELESAI")


main()
