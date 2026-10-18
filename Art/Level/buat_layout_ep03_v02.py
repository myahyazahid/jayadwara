"""Membuat Art/Level/ep03_layout_v02.json dari tata letak docs/32 v1.0 + medan ep03_medan.py, lalu memeriksanya.

Pakai: python -I Art/Level/buat_layout_ep03_v02.py   (menulis JSON dan mencetak hasil cek; harus SEMUA LULUS)
Ubah tata letak di file INI (bukan di JSON), lalu jalankan ulang.

Koreksi 18 Okt 2026: Menara Adikara digeser ke utara (y +15 ... +85) supaya boulevard tidak terpotong.
Sumber desain: docs/32-desain-level-ep03.md bagian 2a (v0.3) dan bagian 8 (H1-H8 disetujui).
"""
import json
import math
import os
import random
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep03_medan as M  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ep03_layout_v02.json")
random.seed(3)

# ================================================================== helper objek
def kotak(id_, pos, ukuran, mi, hancur=False, penalti=None, **kw):
    o = {"id": id_, "jenis": "kotak", "pos": [round(pos[0], 1), round(pos[1], 1)],
         "ukuran": [round(v, 2) for v in ukuran], "mi": mi, "hancur": hancur}
    if hancur:
        o["penalti"] = penalti or "normal"
    o.update(kw)
    return o


def rumah(id_, pos, ukuran, mi="Rumah", mi_atap="Atap", hancur=True, penalti="tinggi", **kw):
    o = kotak(id_, pos, ukuran, mi, hancur, penalti, **kw)
    o["jenis"] = "rumah"
    o["mi_atap"] = mi_atap
    return o


def dinding(id_, a, b, tinggi, tebal, mi, **kw):
    o = {"id": id_, "jenis": "dinding", "dari": list(a), "ke": list(b), "tinggi": tinggi,
         "tebal": tebal, "mi": mi, "hancur": False}
    o.update(kw)
    return o


def bidang(id_, pos, ukuran, mi, z=None, **kw):
    o = {"id": id_, "jenis": "bidang", "pos": [round(pos[0], 1), round(pos[1], 1)],
         "ukuran": [round(v, 2) for v in ukuran], "mi": mi, "hancur": False}
    if z is not None:
        o["z"] = round(z, 2)
    o.update(kw)
    return o


def alas(pos, P, L, yaw=0.0):
    x, y = pos
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    zs = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            lx, ly = P / 2 * i / 2, L / 2 * j / 2
            zs.append(M.elev(x + lx * c - ly * s, y + lx * s + ly * c))
    return min(zs), max(zs)


def tapak_elev(o):
    if o["jenis"] == "dinding":
        (ax, ay), (bx, by) = o["dari"], o["ke"]
        return [M.elev(ax + (bx - ax) * k / 10, ay + (by - ay) * k / 10) for k in range(11)]
    lo, hi = alas(o["pos"], o["ukuran"][0], o["ukuran"][1], o.get("yaw", 0))
    x, y = o["pos"]
    P, L = o["ukuran"][0], o["ukuran"][1]
    c, s_ = math.cos(math.radians(o.get("yaw", 0))), math.sin(math.radians(o.get("yaw", 0)))
    return [M.elev(x + (P / 4 * i) * c - (L / 4 * j) * s_, y + (P / 4 * i) * s_ + (L / 4 * j) * c)
            for i in range(-2, 3) for j in range(-2, 3)]


def alas_pusat(o):
    if o.get("z") is not None:
        return float(o["z"])
    if o["jenis"] == "dinding":
        return M.elev((o["dari"][0] + o["ke"][0]) / 2, (o["dari"][1] + o["ke"][1]) / 2)
    return M.elev(o["pos"][0], o["pos"][1])


OBJEK = []
GED = []          # bangunan yang ditempatkan generator: {"r":[x0,x1,y0,y1],"h":..,"mi":..,"penalti":..,"kelompok":..}
KOS = []          # rect yang tidak boleh diisi bangunan


def kos(x0, x1, y0, y1):
    KOS.append([float(x0), float(x1), float(y0), float(y1)])


def hit(a, b, j=0.0):
    return a[1] + j > b[0] and a[0] - j < b[1] and a[3] + j > b[2] and a[2] - j < b[3]


def tempat(x0, x1, y0, y1, h, mi, penalti, kelompok):
    r = [x0, x1, y0, y1]
    if any(hit(r, k, 4.0) for k in KOS):
        return False
    if any(hit(r, g["r"], 4.0) for g in GED):
        return False
    GED.append({"r": r, "h": h, "mi": mi, "penalti": penalti, "kelompok": kelompok})
    return True


# ================================================================== ruang terpakai
# jalan (dengan trotoar 2 m)
kos(-1100, 1100, M.JALAN_UTAMA_Y[0] - 2, M.JALAN_UTAMA_Y[1] + 2)
for y0, y1 in M.JALAN_SEJAJAR_Y:
    kos(-1100, 1100, y0 - 2, y1 + 2)
for x0, x1 in M.JALAN_MELINTANG_X:
    kos(x0 - 2, x1 + 2, -300, 300)
# plaza, menara, gardu, lahan proyek, kanal
kos(M.PLAZA[0] - 5, M.PLAZA[1] + 5, M.PLAZA[2] - 5, M.PLAZA[3] + 5)
kos(M.MENARA[0] - 20, M.MENARA[1] + 20, M.MENARA[2] - 10, M.MENARA[3] + 20)
for gx, gy, gp, gl in (M.G1, M.G2, M.G3):
    kos(gx - gp / 2 - 20, gx + gp / 2 + 20, gy - gl / 2 - 20, gy + gl / 2 + 20)
kos(M.LAHAN_PROYEK[0] - 5, M.LAHAN_PROYEK[1], M.LAHAN_PROYEK[2] - 5, M.LAHAN_PROYEK[3] + 5)
kos(1040, 1100, -300, 300)
kos(160, 200, 85, 125)                         # Menara Kaca 180 m
kos(500, 540, -130, -70)                       # Apartemen 70 m
kos(-1100, -990, -275, 0)                       # koridor ramp pintu tol
kos(-1045, -995, -42, -4)                       # START + mobil DWARA
kos(-1065, -975, 292, 328)                      # gerbang tol

# 9 ruang terbuka v0.3: 4 parkir, 3 taman, 2 lahan kosong
TERBUKA = [
    (-280, -180, 190, 290, "parkir"),
    (-60, 40, -290, -190, "taman"),
    (260, 380, 190, 290, "lahan kosong"),
    (420, 520, -290, -190, "parkir"),
    (-280, -130, -150, -60, "taman"),
    (60, 170, -150, -40, "parkir"),
    (300, 400, 40, 150, "taman"),
    (-1080, -960, 190, 290, "parkir"),
    (-900, -800, -290, -190, "lahan kosong"),
]
for x0, x1, y0, y1, _ in TERBUKA:
    kos(x0 - 4, x1 + 4, y0 - 4, y1 + 4)

# ================================================================== bangunan modular
H_KACA = [60, 75, 90, 110, 130, 150, 180]
H_APT = [20, 35, 50, 70, 85]

# sektor kaca: 55 x 55 m kandidat, gedung 40-50 m
for x in range(-290, 250, 55):
    for y in range(-285, 290, 55):
        P = random.uniform(38, 46)
        L = random.uniform(38, 46)
        if x + P > 250 or y + L > 290:
            continue
        tempat(x, x + P, y, y + L, random.choice(H_KACA), "MenaraKaca", "tinggi", "KACA_Menara")

# sektor apartemen: 55 x 55 m kandidat, blok 35-45 m
for x in range(250, 690, 55):
    for y in range(-285, 290, 55):
        P = random.uniform(34, 42)
        L = random.uniform(34, 42)
        if x + P > 690 or y + L > 290:
            continue
        tempat(x, x + P, y, y + L, random.choice(H_APT), "Apartemen", "tinggi", "APARTEMEN_Blok")

# ruko zona A: 2 baris menghadap boulevard, 8-14 m
RUKO_POS = []
for y0 in (22, -47):
    for x in range(-1080, -770, 38):
        P, L = 26.0, 22.0
        if tempat(x, x + P, y0, y0 + L, random.choice([8, 10, 14]), "Ruko", "tanpa", "RUKO_Baris"):
            RUKO_POS.append((x + P / 2, y0 + L / 2, P, L))
# baris ketiga zona A (lebih jauh dari boulevard, pengisi blok ruko)
for y0 in (100, -125):
    for x in range(-1080, -800, 60):
        P, L = 30.0, 22.0
        if tempat(x, x + P, y0, y0 + L, random.choice([8, 10, 14]), "Ruko", "tanpa", "RUKO_Baris"):
            RUKO_POS.append((x + P / 2, y0 + L / 2, P, L))
# target 16 ruko: buang 2 paling jauh dari START
if len(RUKO_POS) > 16:
    RUKO_POS.sort(key=lambda p: math.hypot(p[0] + 1020, p[1] + 20), reverse=True)
    for cx, cy, P, L in RUKO_POS[16:]:
        GED[:] = [g for g in GED if not (abs((g["r"][0] + g["r"][1]) / 2 - cx) < 0.01 and abs((g["r"][2] + g["r"][3]) / 2 - cy) < 0.01)]

# tepi plaza utara/selatan: 5 + 5 gedung
for x in range(-735, -455, 56):
    for y0 in (195, -240):
        tempat(x, x + 48, y0, y0 + 45, random.choice([45, 60, 80, 110]), "MenaraKaca", "normal", "PLAZA_Gedung")

# lahan proyek: kantor proyek + 3 bangunan setengah jadi (bukan derek)
PROYEK_BANGUNAN = [
    ("PROYEK_Kantor", (760, -60), (20, 12, 6)),
    ("PROYEK_RangkaA", (820, 150), (30, 25, 9)),
    ("PROYEK_RangkaB", (950, -210), (35, 25, 12)),
    ("PROYEK_RangkaC", (1000, 120), (25, 20, 6)),
]
for _, pos, uk in PROYEK_BANGUNAN:
    GED.append({"r": [pos[0] - uk[0] / 2, pos[0] + uk[0] / 2, pos[1] - uk[1] / 2, pos[1] + uk[1] / 2],
                "h": uk[2], "mi": "Alat", "penalti": "tanpa", "kelompok": "PROYEK_Bangunan"})

# tepatkan jumlah gedung ke 114 (docs v0.3)
def penting(g):
    cx, cy = (g["r"][0] + g["r"][1]) / 2, (g["r"][2] + g["r"][3]) / 2
    if g["kelompok"] in ("PROYEK_Bangunan", "RUKO_Baris", "PLAZA_Gedung"):
        return True
    if abs(cy) < 85:                                  # deret boulevard
        return True
    for gx, gy, gp, gl in (M.G1, M.G2, M.G3):
        if abs(cx - gx) < 110 and abs(cy - gy) < 110:
            return True
    return False


while len(GED) > 108:
    calon = [g for g in GED if not penting(g)]
    if not calon:
        calon = [g for g in GED if g["kelompok"] != "PROYEK_Bangunan"]
    GED.remove(random.choice(calon))

# kalau kurang, isi sisa grid dengan blok kecil
filler_x = list(range(-280, 240, 45)) + list(range(260, 680, 45))
random.shuffle(filler_x)
percobaan = 0
while len(GED) < 108 and percobaan < 20000:
    percobaan += 1
    x = random.choice(filler_x)
    y = random.uniform(-280, 250)
    P = random.uniform(28, 34)
    L = random.uniform(28, 34)
    mi = "MenaraKaca" if x < 250 else "Apartemen"
    kel = "KACA_Menara" if x < 250 else "APARTEMEN_Blok"
    tempat(x, x + P, y, y + L, random.choice(H_KACA if x < 250 else H_APT), mi, "tinggi", kel)
if len(GED) < 108:
    print(f"PERINGATAN: hanya {len(GED)} gedung setelah {percobaan} percobaan filler")

# ================================================================== 18 gedung hancur (6 blok Chaos x 3)
def dekat_gardu(g):
    cx, cy = (g["r"][0] + g["r"][1]) / 2, (g["r"][2] + g["r"][3]) / 2
    return min(abs(cx - gx) + abs(cy - gy) for gx, gy, _, _ in (M.G1, M.G2, M.G3))


calon_hancur = sorted([g for g in GED if g["kelompok"] in ("KACA_Menara", "APARTEMEN_Blok")],
                      key=lambda g: (dekat_gardu(g), abs((g["r"][2] + g["r"][3]) / 2)))
HANCUR = calon_hancur[:18]
for g in HANCUR:
    GED.remove(g)
for i, g in enumerate(HANCUR):
    x0, x1, y0, y1 = g["r"]
    blok = f"BLOK{i // 3 + 1}"
    OBJEK.append(kotak(f"{blok}_Gedung{i % 3 + 1}", ((x0 + x1) / 2, (y0 + y1) / 2),
                       (x1 - x0, y1 - y0, g["h"]), g["mi"], True, g["penalti"],
                       blok_chaos=blok, tukar_puing=True,
                       catatan="satu Geometry Collection per blok 3 gedung (F2)" if i % 3 == 0 else "anggota blok Chaos"))

# ================================================================== kelompok sisa
KELOMPOK = []
for nama, mi, bentuk, extra in (
        ("KACA_Menara", "MenaraKaca", "kotak", {}),
        ("APARTEMEN_Blok", "Apartemen", "kotak", {}),
        ("RUKO_Baris", "Ruko", "kotak", {"penalti": "tanpa"}),
        ("PLAZA_Gedung", "MenaraKaca", "kotak", {"penalti": "normal"}),
        ("PROYEK_Bangunan", "Alat", "kotak", {"penalti": "tanpa"})):
    items = []
    for g in GED:
        if g["kelompok"] != nama:
            continue
        x0, x1, y0, y1 = g["r"]
        items.append([round((x0 + x1) / 2, 2), round((y0 + y1) / 2, 2), round(x1 - x0, 2), round(y1 - y0, 2),
                      round(g["h"], 2), round(random.uniform(-4, 4), 2)])
    if items:
        k = {"id": nama, "bentuk": bentuk, "mi": mi, "hancur": False, "item": items}
        k.update(extra)
        KELOMPOK.append(k)

# latar utara: menara kaca di luar batas (tidak bisa didatangi)
LATAR_UTARA = []
for i, x in enumerate(range(-1000, 1001, 200)):
    LATAR_UTARA.append([float(x), 336.0, 70.0, 46.0, 60.0 + 25.0 * (i % 6), 0.0])
KELOMPOK.append({"id": "LATAR_Utara", "bentuk": "kotak", "mi": "MenaraKaca", "hancur": False,
                 "tanpa_tabrakan": True, "item": LATAR_UTARA})

# latar selatan: Kampung Kali (Ep 2), mesh kasar
LATAR_SELATAN = []
for i, x in enumerate(range(-1000, 1001, 150)):
    LATAR_SELATAN.append([float(x), -334.0, 14.0, 11.0, 6.5 if i % 3 == 0 else 3.5, 0.0])
KELOMPOK.append({"id": "LATAR_Selatan", "bentuk": "rumah", "mi": "RumahLatar", "mi_atap": "AtapLatar",
                 "hancur": False, "tanpa_tabrakan": True, "item": LATAR_SELATAN})

# jalan layang tol + rel layang (ISM)
TOL_PILAR = [[float(x), 310.0, 3.0, 3.0, M.TOL_Z, 0.0] for x in range(-1080, 1101, 60)]
TOL_DEK = [[float(x + 30), 310.0, 60.0, 20.0, 1.5, 0.0] for x in range(-1080, 1080, 60)]
REL_PILAR = [[float(x), -306.0, 3.0, 3.0, M.REL_Z, 0.0] for x in range(-1080, 1101, 60)]
REL_DEK = [[float(x + 30), -306.0, 60.0, 12.0, 1.2, 0.0] for x in range(-1080, 1080, 60)]
KELOMPOK += [
    {"id": "TOL_Pilar", "bentuk": "kotak", "mi": "Tol", "hancur": False, "penalti": "normal", "z": 0.0, "item": TOL_PILAR},
    {"id": "TOL_Dek", "bentuk": "kotak", "mi": "Tol", "hancur": False, "penalti": "normal", "z": M.TOL_Z, "item": TOL_DEK},
    {"id": "REL_Pilar", "bentuk": "kotak", "mi": "RelLayang", "hancur": False, "z": 0.0, "item": REL_PILAR},
    {"id": "REL_Dek", "bentuk": "kotak", "mi": "RelLayang", "hancur": False, "z": M.REL_Z, "item": REL_DEK},
]

# ================================================================== objek unik
# Menara Adikara: cangkang 4 dinding + pelat lantai + inti lift
MX0, MX1, MY0, MY1 = M.MENARA
OBJEK += [
    # dinding selatan bawah: dua sisi dengan pintu masuk 16 m
    dinding("MENARA_DindingSelatanKiri", (MX0, MY0), (MX0 + 18, MY0), 8.0, 1.2, "MenaraAdikara"),
    dinding("MENARA_DindingSelatanKanan", (MX1 - 18, MY0), (MX1, MY0), 8.0, 1.2, "MenaraAdikara"),
    dinding("MENARA_DindingSelatanAtas", (MX0, MY0), (MX1, MY0), 212.0, 1.2, "MenaraAdikara", z=8.0),
    dinding("MENARA_DindingUtara", (MX0, MY1), (MX1, MY1), 220.0, 1.2, "MenaraAdikara"),
    dinding("MENARA_DindingBarat", (MX0, MY0), (MX0, MY1), 220.0, 1.2, "MenaraAdikara"),
    dinding("MENARA_DindingTimur", (MX1, MY0), (MX1, MY1), 220.0, 1.2, "MenaraAdikara"),
]
# pelat lantai (0 = lobby tidak diberi pelat karena pit B1)
for nama, z in (("B1", -8.0), ("L20", 80.0), ("L21", 86.0), ("L22", 92.0), ("L38", 150.0),
                ("L38b", 158.0), ("L50", 200.0), ("L50b", 212.0), ("Atap", 220.0)):
    OBJEK.append(kotak(f"MENARA_Pelat{nama}", ((MX0 + MX1) / 2, (MY0 + MY1) / 2), (70, 70, 0.4), "Lantai", z=z,
                       catatan="pelat lantai"))
# inti lift 14 x 14
CX, CY = (MX0 + MX1) / 2, (MY0 + MY1) / 2
OBJEK += [
    dinding("MENARA_IntiBarat", (CX - 7, CY - 7), (CX - 7, CY + 7), 228.0, 0.8, "Dinding", z=-8.0),
    dinding("MENARA_IntiTimur", (CX + 7, CY - 7), (CX + 7, CY + 7), 228.0, 0.8, "Dinding", z=-8.0),
    dinding("MENARA_IntiUtara", (CX - 7, CY + 7), (CX + 7, CY + 7), 228.0, 0.8, "Dinding", z=-8.0),
    dinding("MENARA_IntiSelatan", (CX - 7, CY - 7), (CX + 7, CY - 7), 228.0, 0.8, "Dinding", z=-8.0),
    kotak("MENARA_LiftKabin", (CX, CY), (6, 6, 3), "Lift", z=0.5, catatan="kabin lift greybox"),
]
# tangga lobby -> B1 (16 anak tangga)
for i in range(16):
    OBJEK.append(kotak(f"MENARA_TanggaB1_{i + 1:02d}", (CX, MY0 + 2 + i * 0.6), (6, 0.6, 0.5), "Tangga",
                       z=round(-i * 0.5, 2), catatan="turun ke B1"))
# partisi interior per lantai yang dimainkan
for lantai, z in (("L20", 80.4), ("L21", 86.4), ("L22", 92.4), ("L38", 150.4), ("L50", 200.4)):
    OBJEK.append(dinding(f"INT_{lantai}_Partisi1", (MX0 + 6, CY - 20), (MX0 + 6, CY + 20), 3.0, 0.3, "Interior", z=z))
    OBJEK.append(dinding(f"INT_{lantai}_Partisi2", (MX0 + 6, CY + 20), (MX1 - 6, CY + 20), 3.0, 0.3, "Interior", z=z))
# B1 ruang kontrol listrik
for i in range(4):
    OBJEK.append(kotak(f"INT_B1_Panel{i + 1}", (MX0 + 10 + i * 6, MY0 + 12), (2, 1, 2.5), "Alat", z=-8.0,
                       catatan="panel listrik ★1"))
# L38 koleksi
for i in range(3):
    OBJEK.append(kotak(f"INT_L38_Koleksi{i + 1}", (MX1 - 12, CY - 8 + i * 8), (3, 3, 2), "Kayu", z=150.4,
                       catatan="lemari koleksi ○ + kujang (H8)"))
# L50 rak server
for i in range(6):
    OBJEK.append(kotak(f"INT_L50_Server{i + 1}", (MX0 + 10 + i * 4, CY + 18), (1.2, 2.4, 3), "Alat", z=200.4,
                       catatan="rak server ★2"))
# atap: parapet + antena
OBJEK += [
    kotak("MENARA_ParapetSelatan", (CX, MY0), (70, 1, 1.2), "Dinding", z=220.0),
    kotak("MENARA_ParapetUtara", (CX, MY1), (70, 1, 1.2), "Dinding", z=220.0),
    kotak("MENARA_ParapetBarat", (MX0, CY), (1, 70, 1.2), "Dinding", z=220.0),
    kotak("MENARA_ParapetTimur", (MX1, CY), (1, 70, 1.2), "Dinding", z=220.0),
    kotak("MENARA_Antena", (CX, CY), (2, 2, 18), "Alat", z=220.0, catatan="antena atap"),
]

# Menara kaca 180 m + apartemen 70 m (landmark, tidak hancur di gameplay)
OBJEK += [
    kotak("KACA_Menara180", (M.MENARA_KACA_180[0], M.MENARA_KACA_180[1]),
          (M.MENARA_KACA_180[2], M.MENARA_KACA_180[3], M.MENARA_KACA_180[4]), "MenaraKaca",
          catatan="landmark 180 m; jangan dijatuhkan saat mencabut G1"),
    kotak("APARTEMEN_70", (M.APARTEMEN_70[0], M.APARTEMEN_70[1]),
          (M.APARTEMEN_70[2], M.APARTEMEN_70[3], M.APARTEMEN_70[4]), "Apartemen",
          catatan="landmark 70 m di samping G2"),
]

# 3 gardu induk
for nama, gx, gy, gp, gl in (("G1", *M.G1), ("G2", *M.G2), ("G3", *M.G3)):
    OBJEK.append(kotak(f"GARDU_{nama}_Bangunan", (gx, gy), (gp, gl, 30), "Gardu",
                       gardu=nama, objektif=True, catatan=f"{nama}: gardu bisa diputus"))
    for i in range(3):
        OBJEK.append(kotak(f"GARDU_{nama}_Trafo{i + 1}", (gx - 20 + i * 20, gy - 10), (10, 8, 4), "Alat",
                           gardu=nama, catatan="trafo"))
    OBJEK += [
        dinding(f"GARDU_{nama}_PagarU", (gx - gp / 2 - 4, gy + gl / 2 + 4), (gx + gp / 2 + 4, gy + gl / 2 + 4), 3, 0.3, "Alat", gardu=nama),
        dinding(f"GARDU_{nama}_PagarS", (gx - gp / 2 - 4, gy - gl / 2 - 4), (gx + gp / 2 + 4, gy - gl / 2 - 4), 3, 0.3, "Alat", gardu=nama),
        dinding(f"GARDU_{nama}_PagarB", (gx - gp / 2 - 4, gy - gl / 2 - 4), (gx - gp / 2 - 4, gy + gl / 2 + 4), 3, 0.3, "Alat", gardu=nama),
        dinding(f"GARDU_{nama}_PagarT", (gx + gp / 2 + 4, gy - gl / 2 - 4), (gx + gp / 2 + 4, gy + gl / 2 + 4), 3, 0.3, "Alat", gardu=nama),
        kotak(f"GARDU_{nama}_Tiang1", (gx - gp / 2 + 2, gy + gl / 2 - 2), (2, 2, 22), "Alat", gardu=nama),
        kotak(f"GARDU_{nama}_Tiang2", (gx + gp / 2 - 2, gy - gl / 2 + 2), (2, 2, 22), "Alat", gardu=nama),
    ]

# plaza: air mancur + videotron
OBJEK += [
    kotak("PLAZA_AirMancurBak", (-600, -70), (24, 24, 1), "AirMancur", catatan="air mancur plaza (digeser ke selatan boulevard)"),
    bidang("PLAZA_AirMancurAir", (-600, -70), (20, 20), "AirMancur", z=1.05, tanpa_tabrakan=True),
    kotak("PLAZA_AirMancurPilar", (-600, -70), (2, 2, 7), "AirMancur", z=1.0),
    kotak("PLAZA_VideotronLayar", (-540, -120), (20, 2, 12), "Videotron", z=8.0, catatan="berita Entitas D"),
    kotak("PLAZA_VideotronKaki1", (-548, -120), (1, 1, 8), "Alat"),
    kotak("PLAZA_VideotronKaki2", (-532, -120), (1, 1, 8), "Alat"),
]

# pintu tol: kanopi + 6 bilik + barikade + mobil DWARA + ramp
OBJEK += [
    kotak("TOLGATE_Kanopi", (-1020, 310), (70, 28, 1.5), "Tol", z=22.0, catatan="gerbang tol barat"),
    kotak("JALAN_MobilDWARA", (-1005, -18), (5, 2, 1.8), "Mobil", catatan="START di sampingnya"),
]
for i in range(6):
    OBJEK.append(kotak(f"TOLGATE_Bilik{i + 1}", (-1050 + i * 12, 310), (6, 8, 3), "Tol", z=0.0))
for i, y in enumerate((-8, 0, 8)):
    OBJEK.append(kotak(f"JALAN_Barikade{i + 1}", (-1050, y), (3, 1, 1.2), "Penanda", catatan="barikade polisi"))

# ramp pintu keluar tol: kurva kuadratik (-1100,-255) -> (-1020,-12)
P0, P1, P2 = (-1100.0, -255.0), (-1035.0, -140.0), (-1020.0, -12.0)
pts = []
for i in range(11):
    t = i / 10.0
    x = (1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * P1[0] + t ** 2 * P2[0]
    y = (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * P1[1] + t ** 2 * P2[1]
    pts.append((x, y, 8.0 * (1 - t)))
for i, (a, b) in enumerate(zip(pts, pts[1:])):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    panjang_seg = math.hypot(dx, dy) + 0.5
    yaw = math.degrees(math.atan2(dy, dx))
    OBJEK.append(kotak(f"RAMP_Tol{i + 1:02d}", (cx, cy), (panjang_seg, 12, 0.6), "Jalan", z=round((a[2] + b[2]) / 2, 2),
                       yaw=round(yaw, 2), catatan="ramp turun dari jalan layang tol"))

# lahan proyek: 3 derek
for i, (dx, dy) in enumerate(((780, 150), (880, -80), (980, 180)), 1):
    OBJEK += [
        kotak(f"PROYEK_Derek{i}_Mast", (dx, dy), (3, 3, 60), "Derek", catatan="derek tower 60 m"),
        kotak(f"PROYEK_Derek{i}_Jib", (dx + 20, dy), (40, 2, 2), "Derek", z=60.0),
        kotak(f"PROYEK_Derek{i}_Penyeimbang", (dx - 8, dy), (10, 3, 3), "Derek", z=58.0),
    ]

# kanal: permukaan air
OBJEK.append(bidang("AIR_KanalBanjir", (1080, 0), (40, 592), "Air", z=M.KANAL_MUKA_AIR, tanpa_tabrakan=True,
                    catatan="Kanal Banjir Timur; dangkal untuk raksasa, zona aman"))

# ================================================================== pohon & tiang
POHON = {
    "Boulevard": [],
    "Plaza": [],
    "Proyek": [],
}
for x in range(-980, 1040, 50):
    for y in (-18.0, 18.0):
        if abs(x - 100) < 60 or abs(x - 600) < 60 or abs(x - 900) < 60:
            continue
        POHON["Boulevard"].append([float(x), y, round(random.uniform(0.8, 1.1), 2)])
for x in range(-740, -440, 40):
    for y in (-140.0, 140.0):
        POHON["Plaza"].append([float(x), y, round(random.uniform(0.9, 1.2), 2)])
for i in range(18):
    POHON["Proyek"].append([round(random.uniform(720, 1040), 1), round(random.uniform(-260, 260), 1), round(random.uniform(0.8, 1.1), 2)])

TIANG = []
for x in range(-1000, 1041, 40):
    TIANG.append([float(x), 14.0])
    TIANG.append([float(x), -14.0])
for x in range(-1000, 1041, 100):
    TIANG.append([float(x), 300.0])
    TIANG.append([float(x), -300.0])

# ================================================================== penanda
PENANDA = [
    {"id": "START", "pos": [-1020, -20], "jenis": "PlayerStart", "hadap_ke": [-430, 50]},
    {"id": "CLUE_1_GrafikListrik", "pos": [-395, 50], "jenis": "titik", "z": -7.5,
     "label": "★1 grafik listrik (B1)"},
    {"id": "CLUE_2_JimatPecah", "pos": [-395, 50], "jenis": "titik", "z": 200.5,
     "label": "★2 jimat pecah (L50)"},
    {"id": "CLUE_O_NotaKolektor", "pos": [-395, 50], "jenis": "titik", "z": 150.5,
     "label": "○ nota kolektor + kujang (L38)"},
    {"id": "CP_Lobi", "pos": [-395, -5], "jenis": "area", "radius": 10, "label": "checkpoint · lobi"},
    {"id": "CP_L22", "pos": [-395, 50], "jenis": "titik", "z": 92.5, "label": "checkpoint · setelah L22"},
    {"id": "CP_Fase1", "pos": [-395, 0], "jenis": "area", "radius": 25, "label": "checkpoint · awal fase 1"},
    {"id": "CP_G2", "pos": [600, -100], "jenis": "area", "radius": 25, "label": "checkpoint · setelah G2"},
    {"id": "CP_Fase2", "pos": [950, -200], "jenis": "area", "radius": 25, "label": "checkpoint · awal fase 2"},
    {"id": "G1", "pos": [100, 105], "jenis": "titik", "label": "G1 gardu · putus 1"},
    {"id": "G2", "pos": [600, -100], "jenis": "titik", "label": "G2 gardu · putus 2"},
    {"id": "G3", "pos": [900, 60], "jenis": "titik", "label": "G3 gardu induk · putus 3"},
    {"id": "TRANSFORMASI", "pos": [-395, 50], "jenis": "titik", "z": 220.5, "label": "transformasi di atap (H5)"},
    {"id": "JAYADWARA_MUNCUL", "pos": [-650, -40], "jenis": "titik", "label": "Jayadwara muncul di plaza"},
    {"id": "BOSS_F1_G1", "pos": [100, 105], "jenis": "titik", "label": "fase 1 · jenglot 36 m di G1"},
    {"id": "BOSS_F1_G2", "pos": [600, -100], "jenis": "titik", "label": "fase 1 · jenglot 31 m di G2"},
    {"id": "BOSS_F1_G3", "pos": [900, 60], "jenis": "titik", "label": "fase 1 · jenglot 27 m di G3"},
    {"id": "BOSS_F2", "pos": [950, -200], "jenis": "titik", "label": "fase 2 · gelap total di tepi kanal"},
    {"id": "SEGEL", "pos": [1035, -200], "jenis": "titik", "label": "segel di tepi kanal"},
]
# penanda interior (Play From Here)
for nama, z in (("B1", -7.5), ("L1", 1.0), ("L20", 80.5), ("L21", 86.5), ("L22", 92.5),
                ("L38", 150.5), ("L50", 200.5), ("Atap", 220.5)):
    PENANDA.append({"id": f"PS_{nama}", "pos": [-395, 50], "jenis": "titik", "z": z,
                    "label": f"Play From Here {nama}"})

# ================================================================== zona
ZONA = [
    {"id": "ZONA_Aman_Boulevard", "x": [-750, 1060], "y": [-12, 12], "warna": "hijau",
     "label": "zona aman: boulevard (koridor kejar)"},
    {"id": "ZONA_Aman_Plaza", "x": [M.PLAZA[0], M.PLAZA[1]], "y": [M.PLAZA[2], M.PLAZA[3]], "warna": "hijau",
     "label": "zona aman: plaza CBD"},
    {"id": "ZONA_Aman_Kanal", "x": [1050, 1100], "y": [-296, 296], "warna": "hijau",
     "label": "zona aman: Kanal Banjir Timur"},
    {"id": "ZONA_TanpaPenalti_Proyek", "x": [700, 1060], "y": [-280, 280], "warna": "ungu",
     "label": "lahan proyek: tanpa penalti"},
    {"id": "ZONA_PenaltiTinggi_Kaca", "x": [-300, 250], "y": [-296, 296], "warna": "merah",
     "label": "penalti tinggi: sektor kaca"},
    {"id": "ZONA_PenaltiTinggi_Apartemen", "x": [250, 690], "y": [-296, 296], "warna": "merah",
     "label": "penalti tinggi: sektor apartemen"},
]

# ================================================================== kamera
KAMERA = [
    {"id": "C1_START_PintuTol", "pos": [-1035, 0], "tinggi_di_atas_tanah": 1.6,
     "lihat_ke": [-430, 50, 60], "fov": 70, "cahaya": "malam"},
    {"id": "C2_Plaza_Menara", "pos": [-700, -100], "tinggi_di_atas_tanah": 1.6,
     "lihat_ke": [-395, 50, 120], "fov": 75, "cahaya": "malam"},
    {"id": "C3_Lobi", "pos": [-395, -15], "tinggi_di_atas_tanah": 1.6,
     "lihat_ke": [-395, 50, 10], "fov": 75, "cahaya": "malam"},
    {"id": "C4_L20_Kantor", "pos": [-420, 35], "z": 82.0,
     "lihat_ke": [-370, 60, 82], "fov": 75, "cahaya": "malam"},
    {"id": "C5_TampakAtas", "pos": [0, 0], "ortho": True, "lebar_ortho": 2400, "cahaya": "malam"},
    {"id": "C6_Atap", "pos": [-362, 50], "z": 222.5,
     "lihat_ke": [900, 60, 0], "fov": 70, "cahaya": "malam"},
    {"id": "C7_MataJayadwara", "pos": [0, 0], "z": 42.0,
     "lihat_ke": [900, 60, 10], "fov": 70, "cahaya": "malam"},
    {"id": "C8_Kanal", "pos": [1035, -150], "z": 1.6,
     "lihat_ke": [1080, 100, 0], "fov": 70, "cahaya": "malam"},
]

# ================================================================== rute
RUTE_AKSA_TANAH = [[-1020, -20], [-1020, 0], [-760, 0], [-700, -40], [-600, -20], [-470, 0], [-432, 0],
                   [-395, 10]]
RUTE_INTERIOR = [[-395, 10, 0], [-395, 50, -8], [-395, 50, 0], [-395, 50, 80], [-395, 50, 86],
                 [-395, 50, 92], [-395, 50, 150], [-395, 50, 200], [-395, 50, 220]]
RUTE_KEJAR = [[-395, 0], [0, 0], [100, 55], [100, 0], [600, 0], [600, -55], [600, 0],
              [900, 0], [900, 15], [900, 0], [1035, -200]]

MI_WARNA = {
    "Air": [70, 110, 150], "Rel": [80, 75, 70], "Jalan": [55, 57, 60], "Paving": [160, 162, 158],
    "Kaca": [95, 140, 175], "Apartemen": [170, 140, 110], "Proyek": [150, 120, 90], "Latar": [90, 95, 100],
    "MenaraKaca": [110, 160, 190], "MenaraAdikara": [120, 90, 140], "Ruko": [190, 170, 140],
    "Gardu": [230, 180, 40], "Derek": [245, 200, 50], "Alat": [220, 170, 40], "Kendaraan": [40, 40, 45],
    "Mobil": [200, 60, 60], "Pohon": [70, 110, 65], "Penanda": [225, 50, 50], "Interior": [200, 200, 195],
    "Lantai": [140, 140, 145], "Dinding": [180, 180, 175], "Tangga": [160, 120, 80], "Lift": [80, 80, 90],
    "Atap": [120, 120, 125], "Videotron": [60, 200, 220], "AirMancur": [90, 150, 190],
    "Tol": [95, 100, 105], "RelLayang": [85, 85, 90], "RumahLatar": [185, 160, 120],
    "AtapLatar": [150, 150, 155], "Kayu": [140, 100, 60],
}

DATA = {
    "versi": "ep03_layout_v02 (18 Okt 2026, docs/32 v1.0, kepadatan v0.3). Dibuat oleh Art/Level/buat_layout_ep03_v02.py — jangan sunting manual",
    "medan_modul": "ep03_medan",
    "satuan": "meter; x = timur, y = utara, z = atas (0 = permukaan Jl. Adikara Raya). UE: X = x*100, Y = -y*100, Z = z*100 (cm)",
    "koreksi": "Menara Adikara digeser ke y +15...+85 (docs/32 tabel lama y -35...+35 menutup boulevard). Semua angka lain mengikuti docs/32 v1.0.",
    "z_otomatis": "objek tanpa 'z': alas = elev titik tengah tapak, nilainya di 'alas_m' (dinding = titik tengah garis); 'pondasi_m' = perpanjang objek ke bawah; 'z' = tinggi alas absolut. Item kelompok tanpa 'z': alas = elev titik tengah item. Tinggi akhir = alas_m (atau z) + z_dasar_relatif",
    "medan": {"x_min": M.BATAS_MEDAN[0], "x_max": M.BATAS_MEDAN[1], "y_min": M.BATAS_MEDAN[2],
              "y_max": M.BATAS_MEDAN[3], "sel": 2.5,
              "material_zona": "pakai fungsi zona_material(x, y) di ep03_medan.py (Air, Rel, Jalan, Paving, Kaca, Apartemen, Proyek, Latar)"},
    "mi_warna": MI_WARNA,
    "objek": OBJEK,
    "kelompok": KELOMPOK,
    "kelompok_catatan": "satu actor per kelompok berisi ISM; item = [x, y, P, L, T, yaw]; bentuk 'rumah' = dinding (T-0,5) + atap 0,5 m (P+0,4 x L+0,4); 'z' kelompok = alas absolut semua item",
    "pohon_kelompok": POHON,
    "pohon_bentuk": {"batang": {"diameter": 0.5, "tinggi": 7.0, "mi": "Kayu"},
                     "tajuk": {"diameter": 7.0, "tinggi": 8.0, "z_relatif": 5.0, "mi": "Pohon"},
                     "catatan": "ukuran x faktor skala (angka ketiga di tiap titik); batang BlockAll, tajuk NoCollision"},
    "tiang_listrik": {"titik": TIANG, "diameter": 0.3, "tinggi": 9.0, "mi": "Kendaraan"},
    "penanda": PENANDA,
    "zona": ZONA,
    "batas_arena": {"x": [M.BATAS_ARENA[0], M.BATAS_ARENA[1]], "y": [M.BATAS_ARENA[2], M.BATAS_ARENA[3]],
                    "tinggi": 120, "catatan": "dinding tak terlihat, menghalangi Aksa dan Jayadwara"},
    "kamera": KAMERA,
    "cahaya": {
        "malam": {"pitch": -35, "yaw": 200, "warna": [0.45, 0.55, 0.85], "intensitas_lux": 2.0,
                  "catatan": "21.00, bulan; lampu kota menyala"},
        "padam": {"pitch": -35, "yaw": 200, "warna": [0.18, 0.22, 0.40], "intensitas_lux": 0.4,
                  "catatan": "setelah gardu putus; hampir gelap"},
        "darurat": {"pitch": -35, "yaw": 200, "warna": [0.90, 0.30, 0.20], "intensitas_lux": 0.8,
                    "catatan": "lampu darurat merah"},
    },
    "rute_aksa_tanah": RUTE_AKSA_TANAH,
    "rute_interior": RUTE_INTERIOR,
    "rute_kejar": RUTE_KEJAR,
    "kecepatan_rute_ms": 5.0,
    "kecepatan_jayadwara_ms": 70.0,
    "kecepatan_catatan": "Aksa MaxWalkSpeed 500 cm/s; Jayadwara ±70 m/s (PR #29). Lintas arena 1810 m ±26 detik.",
    "bangunan_target": 114,
}


def panjang(rute):
    total = 0.0
    for a, b in zip(rute, rute[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1])))
        for k in range(n):
            x0, y0 = a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n
            x1, y1 = a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n
            total += math.hypot(x1 - x0, y1 - y0)
    return total


def periksa():
    gagal = 0
    xmn, xmx, ymn, ymx = M.BATAS_MEDAN
    ids = [o["id"] for o in OBJEK] + [k["id"] for k in KELOMPOK]
    if len(ids) != len(set(ids)):
        print("GAGAL id ganda")
        gagal += 1
    for o in OBJEK:
        if "pos" not in o or o.get("z") is not None or o["id"].startswith("LATAR_"):
            continue
        x, y = o["pos"]
        if not (xmn < x < xmx and ymn < y < ymx):
            print(f"GAGAL di luar medan: {o['id']}")
            gagal += 1
    # hitung bangunan (gedung modular + unik + gardu + proyek; latar tidak dihitung)
    n_gedung = sum(len(k["item"]) for k in KELOMPOK if k["id"] in
                   ("KACA_Menara", "APARTEMEN_Blok", "RUKO_Baris", "PLAZA_Gedung", "PROYEK_Bangunan"))
    n_gedung += sum(1 for o in OBJEK if o.get("blok_chaos"))
    n_gedung += sum(1 for o in OBJEK if o["id"] in ("KACA_Menara180", "APARTEMEN_70")
                    or (o["id"].startswith("GARDU_") and o["id"].endswith("_Bangunan")))
    n_gedung += 1                                      # Menara Adikara (cangkang, bukan satu kotak)
    print(f"bangunan {n_gedung} (target {DATA['bangunan_target']})")
    if n_gedung != DATA["bangunan_target"]:
        print(f"GAGAL jumlah bangunan {n_gedung} != {DATA['bangunan_target']}")
        gagal += 1
    n_hancur = sum(1 for o in OBJEK if o.get("hancur"))
    n_blok = len({o["blok_chaos"] for o in OBJEK if "blok_chaos" in o})
    # uji tumpang-tindih: gedung tidak boleh menutup jalan/plaza/gardu/landmark
    larangan = [
        (-1100, 1100, M.JALAN_UTAMA_Y[0], M.JALAN_UTAMA_Y[1]),
        *[(-1100, 1100, y0, y1) for y0, y1 in M.JALAN_SEJAJAR_Y],
        *[(x0, x1, -300, 300) for x0, x1 in M.JALAN_MELINTANG_X],
        (M.PLAZA[0], M.PLAZA[1], M.PLAZA[2], M.PLAZA[3]),
        (M.MENARA[0], M.MENARA[1], M.MENARA[2], M.MENARA[3]),
        (160, 200, 85, 125), (500, 540, -130, -70),
    ]
    for gx, gy, gp, gl in (M.G1, M.G2, M.G3):
        larangan.append((gx - gp / 2, gx + gp / 2, gy - gl / 2, gy + gl / 2))
    for g in GED:
        for r in larangan:
            if hit(g["r"], r, 0.0):
                print(f"GAGAL gedung menutup area larangan: {g['r']} x {r}")
                gagal += 1
                break
    for i, a in enumerate(GED):
        for b in GED[i + 1:]:
            if hit(a["r"], b["r"], -0.01):
                print(f"GAGAL gedung tumpang tindih: {a['r']} x {b['r']}")
                gagal += 1
                break
    for o in OBJEK:
        if o.get("blok_chaos"):
            x, y = o["pos"]
            P, L = o["ukuran"][0], o["ukuran"][1]
            r = [x - P / 2, x + P / 2, y - L / 2, y + L / 2]
            for k in larangan:
                if hit(r, k, 0.0):
                    print(f"GAGAL gedung hancur menutup area larangan: {o['id']}")
                    gagal += 1
                    break
    print(f"objek {len(OBJEK)} (hancur {n_hancur}, blok Chaos {n_blok})")
    print("kelompok " + ", ".join(f"{k['id']} {len(k['item'])}" for k in KELOMPOK))
    print(f"pohon {sum(len(v) for v in POHON.values())}, tiang {len(TIANG)}, penanda {len(PENANDA)}, zona {len(ZONA)}, kamera {len(KAMERA)}")
    ri = panjang([(p[0], p[1]) for p in RUTE_AKSA_TANAH])
    rk = panjang(RUTE_KEJAR)
    print(f"rute Aksa tanah START -> lobi: {ri:.0f} m (5 m/s: {ri / 5 / 60:.1f} menit)")
    print(f"rute kejar plaza -> G1 -> G2 -> G3 -> kanal: {rk:.0f} m (Jayadwara 70 m/s: {rk / 70:.1f} detik)")
    if n_blok != 6 or n_hancur != 18:
        print("GAGAL blok Chaos harus 6 x 3 = 18 gedung hancur")
        gagal += 1
    print("SEMUA LULUS" if gagal == 0 else f"ADA {gagal} GAGAL")
    return gagal


if __name__ == "__main__":
    for o in OBJEK:
        if o.get("z") is None:
            o["alas_m"] = round(alas_pusat(o), 2)
            if o["jenis"] in ("kotak", "rumah", "kerucut"):
                melayang = o["alas_m"] - min(tapak_elev(o))
                if melayang > 0.3:
                    o["pondasi_m"] = round(melayang + 0.1, 2)
    DATA["rute_panjang_m"] = {"aksa_tanah": round(panjang([(p[0], p[1]) for p in RUTE_AKSA_TANAH]), 2),
                              "kejar": round(panjang(RUTE_KEJAR), 2)}
    g = periksa()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(DATA, f, ensure_ascii=False, indent=1)
    print(f"ditulis: {OUT}")
    sys.exit(1 if g else 0)
