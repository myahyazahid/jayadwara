"""Fungsi ketinggian medan Ep03_Adikara (meter; X timur, Y utara, Z atas, 0 = permukaan Jl. Adikara Raya).

Sumber: docs/32-desain-level-ep03.md v1.0 (tata letak v02 + kepadatan v0.3, H1-H8 disetujui 18 Okt 2026).
Koreksi koordinat 18 Okt 2026: Menara Adikara digeser 50 m ke utara (y +15 ... +85) supaya boulevard
(y -12 ... +12) tidak terpotong; tabel docs/32 sebelumnya menaruh menara di y -35 ... +35 sehingga
badan menara menutup jalan. Plaza tetap x -750 ... -450, y -150 ... +150.

Medan CBD hampir datar; satu-satunya relief: pit B1 di dalam Menara Adikara (-8 m) dan Kanal Banjir
Timur di batas timur (muka air -1,5 m, dasar -4 m). Jalan layang tol (dek +15 m) dan rel layang
(dek +12 m) adalah geometri, bukan medan.

Data objek: Art/Level/ep03_layout_v02.json (dibuat Art/Level/buat_layout_ep03_v02.py).
Uji mandiri: python -I Art/Level/ep03_medan.py  (harus mencetak SEMUA LULUS).
"""
import math

# ---------------- batas ----------------
BATAS_MEDAN = (-1100.0, 1100.0, -350.0, 350.0)      # x_min, x_max, y_min, y_max (2200 x 700 m)
BATAS_ARENA = (-750.0, 1060.0, -296.0, 296.0)       # 1810 x 592 m (docs: +-1830 x 600)

# ---------------- jalan dan batas alami ----------------
JALAN_UTAMA_Y = (-12.0, 12.0)                       # Jl. Adikara Raya, lebar 24
JALAN_SEJAJAR_Y = ((165.0, 180.0), (-180.0, -165.0))
JALAN_MELINTANG_X = ((-120.0, -100.0), (240.0, 260.0), (690.0, 700.0))
TOL_Y = (300.0, 320.0)                              # jalan layang tol, dek 15 m
TOL_Z = 15.0
TOL_PILAR_JARAK = 60.0
REL_Y = (-312.0, -300.0)                            # rel layang, dek 12 m
REL_Z = 12.0
KANAL_X = (1060.0, 1100.0)                          # Kanal Banjir Timur, lebar 40
KANAL_MUKA_AIR = -1.5
KANAL_DASAR = -4.0

# ---------------- kawasan ----------------
ZONA_A_X = (-1100.0, -750.0)                        # ruko pintu tol
PLAZA = (-750.0, -450.0, -150.0, 150.0)             # x0, x1, y0, y1
MENARA = (-430.0, -360.0, 15.0, 85.0)               # Menara Adikara 70 x 70, tinggi 220
MENARA_PIT = (-420.0, -370.0, 25.0, 75.0)           # lubang B1 (-8 m)
SEKTOR_KACA = (-300.0, 250.0)
SEKTOR_APARTEMEN = (250.0, 690.0)
LAHAN_PROYEK = (700.0, 1060.0, -280.0, 280.0)
G1 = (100.0, 105.0, 70.0, 50.0)                     # x, y, P, L
G2 = (600.0, -100.0, 70.0, 50.0)
G3 = (900.0, 60.0, 70.0, 50.0)
MENARA_KACA_180 = (180.0, 105.0, 40.0, 40.0, 180.0)
APARTEMEN_70 = (520.0, -100.0, 40.0, 60.0, 70.0)
START = (-1020.0, -20.0)
JAYADWARA_MUNCUL = (-650.0, -40.0)
B1_Z = -8.0


def di_kotak(x, y, k):
    return k[0] <= x <= k[1] and k[2] <= y <= k[3]


def _jalan(x, y):
    if JALAN_UTAMA_Y[0] <= y <= JALAN_UTAMA_Y[1] and -1100.0 <= x <= 1060.0:
        return True
    for y0, y1 in JALAN_SEJAJAR_Y:
        if y0 <= y <= y1:
            return True
    for x0, x1 in JALAN_MELINTANG_X:
        if x0 <= x <= x1 and -296.0 <= y <= 296.0:
            return True
    return False


def elev(x, y):
    """Tinggi medan (m). Datar 0 kecuali pit B1 dan kanal timur."""
    if di_kotak(x, y, MENARA_PIT):
        return B1_Z
    if x >= KANAL_X[0]:
        return KANAL_DASAR
    if x >= KANAL_X[0] - 10.0:                       # lereng barat kanal 1050 -> 1060
        t = (x - (KANAL_X[0] - 10.0)) / 10.0
        return KANAL_MUKA_AIR * t
    return 0.0


def zona_material(x, y):
    """Slot material medan (8): Air, Rel, Jalan, Paving, Kaca, Apartemen, Proyek, Latar."""
    if x >= KANAL_X[0] - 10.0:
        return "Air"
    if y < REL_Y[0] or y > TOL_Y[1]:
        return "Latar"
    if REL_Y[0] <= y <= REL_Y[1]:
        return "Rel"
    if _jalan(x, y):
        return "Jalan"
    if di_kotak(x, y, PLAZA) or di_kotak(x, y, MENARA) or x < ZONA_A_X[1]:
        return "Paving"
    if x < SEKTOR_KACA[1]:
        return "Kaca"
    if x < SEKTOR_APARTEMEN[1]:
        return "Apartemen"
    if x <= LAHAN_PROYEK[1]:
        return "Proyek"
    return "Latar"


# ---------------- titik uji (x, y, elev yang diharapkan) ----------------
TITIK_UJI = [
    ("START", -1020.0, -20.0, 0.0),
    ("Plaza air mancur", -600.0, 0.0, 0.0),
    ("Lobi menara", -395.0, 10.0, 0.0),
    ("B1 pit", -395.0, 50.0, -8.0),
    ("G1", 100.0, 105.0, 0.0),
    ("G2", 600.0, -100.0, 0.0),
    ("G3", 900.0, 60.0, 0.0),
    ("Tepi kanal (lereng)", 1055.0, 0.0, -0.75),
    ("Dasar kanal", 1080.0, 0.0, -4.0),
    ("Bawah jalan layang tol", 0.0, 310.0, 0.0),
    ("Bawah rel layang", 0.0, -306.0, 0.0),
    ("Ruko zona A", -900.0, 0.0, 0.0),
    ("Lahan proyek", 800.0, -200.0, 0.0),
    ("Lahan proyek timur", 1000.0, 200.0, 0.0),
    ("Latar utara", 0.0, 340.0, 0.0),
    ("Latar selatan", 0.0, -340.0, 0.0),
]


def _uji():
    gagal = 0
    for nama, x, y, harap in TITIK_UJI:
        z = elev(x, y)
        ok = abs(z - harap) <= 0.001
        print(f"{'OK ' if ok else 'GAGAL'} {nama:24s} elev({x:7.1f}, {y:7.1f}) = {z:6.2f} m (harap {harap:6.2f})")
        gagal += not ok
    # slot material tidak boleh kosong / di luar 8 nama
    slot = {"Air", "Rel", "Jalan", "Paving", "Kaca", "Apartemen", "Proyek", "Latar"}
    for nama, x, y, _ in TITIK_UJI:
        s = zona_material(x, y)
        ok = s in slot
        if not ok:
            print(f"GAGAL slot material {nama}: {s}")
            gagal += 1
    print("SEMUA LULUS" if gagal == 0 else f"ADA {gagal} GAGAL")
    return gagal


if __name__ == "__main__":
    raise SystemExit(1 if _uji() else 0)
