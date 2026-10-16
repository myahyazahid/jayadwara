"""Membuat Art/Level/ep02_layout_v02.json dari daftar di bawah + medan ep02_medan_v02.py, lalu memeriksanya.
Pakai: python -I Art/Level/buat_layout_ep02_v02.py   (menulis JSON dan mencetak hasil cek; harus berakhir SEMUA LULUS)
Ubah tata letak di file INI (bukan di JSON), lalu jalankan ulang. Sumber desain: docs/31 bagian 2a (tata letak v02).
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep02_medan_v02 as M  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ep02_layout_v02.json")
random.seed(2)

# penalti meter sinkronisasi (docs/31 bagian 3E): tinggi | normal | tanpa ; tidak bisa hancur = hancur False
def kotak(id_, pos, ukuran, mi, hancur=False, penalti=None, **kw):
    o = {"id": id_, "jenis": "kotak", "pos": [round(pos[0], 1), round(pos[1], 1)], "ukuran": [round(v, 2) for v in ukuran],
         "mi": mi, "hancur": hancur}
    if hancur:
        o["penalti"] = penalti or "normal"
    o.update(kw)
    return o


def rumah(id_, pos, ukuran, mi="Rumah", mi_atap="Atap", hancur=True, penalti="tinggi", **kw):
    """ukuran = [P, L, T]; T = tinggi sampai puncak atap (1 lantai 3,5 m, 2 lantai 6,5 m); atap = pelat 0,5 m."""
    o = kotak(id_, pos, ukuran, mi, hancur, penalti, **kw)
    o["jenis"] = "rumah"
    o["mi_atap"] = mi_atap
    return o


def dinding(id_, a, b, tinggi, tebal, mi, **kw):
    o = {"id": id_, "jenis": "dinding", "dari": list(a), "ke": list(b), "tinggi": tinggi, "tebal": tebal, "mi": mi, "hancur": False}
    o.update(kw)
    return o


def alas(pos, P, L, yaw=0.0):
    """Alas otomatis = elev terendah di tapak (sama dengan aturan Hermes)."""
    x, y = pos
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    zs = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            lx, ly = P / 2 * i / 2, L / 2 * j / 2
            zs.append(M.elev(x + lx * c - ly * s, y + lx * s + ly * c))
    return min(zs), max(zs)


OBJEK = []
TERPAKAI = []          # tapak objek tunggal (x0, x1, y0, y1) yang tidak boleh diisi rumah kelompok


def pakai(x, y, P, L, jarak=1.0):
    TERPAKAI.append((x - P / 2 - jarak, x + P / 2 + jarak, y - L / 2 - jarak, y + L / 2 + jarak))


def bebas(x, y, P, L):
    for k in TERPAKAI:
        if x + P / 2 > k[0] and x - P / 2 < k[1] and y + L / 2 > k[2] and y - L / 2 < k[3]:
            return False
    return True


# =========================== KAMPUNG INTI (penalti tinggi) ===========================
GANG_SAMPING_Y = [91.0, 39.0, -13.0]            # lebar 2
GANG_KECIL_X = [-200.0, -140.0, -80.0, 30.0, 90.0, 150.0]   # utara-selatan, lebar 1,2

# --- bangunan penting ---
OBJEK += [
    kotak("KAMPUNG_PosRT", (-34, 91), (4, 4, 3), "Kayu", catatan="checkpoint; titik kumpul warga (tidak hancur)"),
    kotak("KAMPUNG_Musala", (78, 65), (14, 14, 8), "Musala", catatan="tidak bisa hancur"),
    rumah("KAMPUNG_RumahKemalingan", (-170, 78), (9, 8, 6.5), catatan="★1; tangga bambu di belakang (utara) ke atap"),
    kotak("KAMPUNG_WarungCCTV", (143, 110), (6, 5, 3.5), "Kayu", True, "tinggi", catatan="★2; CCTV di tiang depan, jual mainan"),
    kotak("KAMPUNG_TiangCCTV", (143, 114), (0.3, 0.3, 5), "Kendaraan"),
    kotak("KAMPUNG_GangBuntu_Beringin", (-222, -22), (2.5, 2.5, 12), "Kayu", catatan="○ sesajen di bawahnya"),
    {"id": "KAMPUNG_GangBuntu_Tajuk", "jenis": "kerucut", "pos": [-222, -22], "ukuran": [18, 18, 12], "z_dasar_relatif": 7,
     "mi": "Pohon", "hancur": False, "tanpa_tabrakan": True},
    kotak("KAMPUNG_Sesajen", (-218, -24), (1, 1, 0.5), "Penanda"),
]
for o in OBJEK:
    if "pos" in o and o["jenis"] in ("kotak", "rumah"):
        pakai(o["pos"][0], o["pos"][1], o["ukuran"][0], o["ukuran"][1], 2.0)
pakai(-222, -22, 22, 22, 0)                     # halaman gang buntu
pakai(-26, 140, 12, 10, 0)                      # mulut gang

# --- blok Chaos: 8 deret x 4 rumah, pinggir kali (selatan) dan jalan raya (utara) (F2) ---
BLOK = [(-220, -43), (-120, -43), (60, -43), (150, -43), (-200, 133), (-100, 133), (50, 133), (140, 133)]
for b, (bx, by) in enumerate(BLOK, 1):
    for r in range(4):
        x = bx - 13.5 + r * 9
        OBJEK.append(rumah(f"BLOK{b}_Rumah{r + 1}", (x, by), (8.2, 9, 6.5 if r % 2 else 3.5), blok_chaos=f"BLOK{b}",
                           catatan="satu Geometry Collection per deret (F2)"))
    pakai(bx, by, 37, 10, 0.6)

# --- atap yang bisa dinaiki (F5): jalur T1 -> T2 -> T3, rumah 1 lantai 3,5 m berderet, papan di atas gang ---
JALUR_ATAP = [(-170, 98), (-150, 98), (-130, 92), (-112, 72), (-96, 52), (-78, 39), (-55, 30), (-30, 30), (0, 30), (30, 30),
              (60, 28), (90, 26), (117, 26)]
ATAP = []
for (a, b) in zip(JALUR_ATAP, JALUR_ATAP[1:]):
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(round(L / 9.6)))
    for k in range(n):
        ATAP.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
ATAP.append(JALUR_ATAP[-1])
PAPAN = []
for i, (x, y) in enumerate(ATAP, 1):
    near_gang = any(abs(y - g) < 5.0 for g in GANG_SAMPING_Y) or any(abs(x - g) < 5.0 for g in GANG_KECIL_X + [M.GANG_UTAMA_X])
    if near_gang:
        PAPAN.append((x, y))
        continue
    OBJEK.append(rumah(f"ATAP_Naik{i:02d}", (x, y), (8.6, 8.6, 3.5), mi_atap="AtapNaik", atap_naik=True,
                       catatan="atap bertanda (jemuran/antena), bisa dinaiki Aksa (F5)"))
    pakai(x, y, 8.6, 8.6, 0.6)
for i, (x, y) in enumerate(PAPAN, 1):
    z0, _ = alas((x, y), 9, 1)
    OBJEK.append(kotak(f"ATAP_Papan{i:02d}", (x, y), (9.6, 1.0, 0.15), "Kayu", z=round(z0 + 3.5, 2),
                       catatan="papan antar-atap di atas gang"))
    pakai(x, y, 9.6, 2.0, 0)
OBJEK.append(kotak("ATAP_TanggaBambu", (-170, 84.5), (1.0, 1.0, 6.5), "Kayu", catatan="naik ke atap rumah kemalingan → T1"))

# --- rumah kelompok (instanced): sisa kampung inti, tukar puing (F2) ---
def isi_rumah(kotak_, gang_y, gang_x, lebar_gang_y=2.0, lebar_gang_x=1.2, peluang=1.0):
    x0, x1, y0, y1 = kotak_
    out = []
    pita = sorted([y0] + [g for g in gang_y if y0 < g < y1] + [y1])
    for ya, yb in zip(pita, pita[1:]):
        ya2, yb2 = ya + lebar_gang_y / 2, yb - lebar_gang_y / 2
        tinggi_pita = yb2 - ya2
        baris = max(1, int(tinggi_pita // 9.5))
        L = tinggi_pita / baris
        for r in range(baris):
            cy = ya2 + L * (r + 0.5)
            kol = sorted([x0] + [g for g in gang_x if x0 < g < x1] + [x1])
            for xa, xb in zip(kol, kol[1:]):
                xa2, xb2 = xa + lebar_gang_x / 2, xb - lebar_gang_x / 2
                x = xa2
                while x < xb2 - 5:
                    P = min(random.uniform(6.5, 9.0), xb2 - x)
                    if P < 5:
                        break
                    cx = x + P / 2
                    Lr = L - random.uniform(0.6, 1.2)
                    if random.random() < peluang and bebas(cx, cy, P - 0.4, Lr):
                        T = 6.5 if random.random() < 0.3 else 3.5
                        out.append([round(cx, 2), round(cy, 2), round(P - 0.4, 2), round(Lr, 2), T, 0])
                    x += P
    return out


RUMAH_INTI = isi_rumah((M.KAMPUNG[0], M.KAMPUNG[1], M.KAMPUNG[2] + 1, M.KAMPUNG[3]), GANG_SAMPING_Y,
                       GANG_KECIL_X + [M.GANG_UTAMA_X - 0.65, M.GANG_UTAMA_X + 0.65])
# gang utama 2,5 m: buang rumah yang menyentuh koridor
RUMAH_INTI = [h for h in RUMAH_INTI if abs(h[0] - M.GANG_UTAMA_X) > h[2] / 2 + 1.25]

# kampung seberang (penalti normal), lebih jarang, halaman lebih luas
RUMAH_SEBERANG = isi_rumah((-470, 450, -328, -138), [-280, -230, -180], [-400, -300, -200, -100, 0, 100, 200, 300, 400],
                           lebar_gang_y=4.0, lebar_gang_x=4.0, peluang=0.3)

# kampung pinggir barat (penalti normal), jarang, antara rel dan kampung inti
RUMAH_BARAT = isi_rumah((M.KAMPUNG_BARAT[0], M.KAMPUNG_BARAT[1], M.KAMPUNG_BARAT[2] + 1, M.KAMPUNG_BARAT[3]), [91, 39, -13],
                        [-470, -410, -350, -300], lebar_gang_y=4.0, lebar_gang_x=4.0, peluang=0.35)
RUMAH_BARAT = [h for h in RUMAH_BARAT if not M.di_kotak(h[0], h[1], (-455, -385, -86, -50))]

# =========================== JALAN RAYA, RUKO, BLOK KOTA, JALAN LAYANG ===========================
RUKO = []
x = -532.0
while x < 690:
    P = random.uniform(16, 24)
    if x + P > 690:
        break
    RUKO.append([round(x + P / 2, 2), 181.5, round(P - 1, 2), 26, round(random.choice([7, 8.5, 10]), 1), 0])
    x += P
KOTA = []
for gx in range(-520, 640, 40):
    for gy in range(215, 360, 40):
        if random.random() < 0.8:
            P, L = random.uniform(18, 32), random.uniform(18, 30)
            KOTA.append([round(gx + 18 + random.uniform(-3, 3), 2), round(gy + 16 + random.uniform(-3, 3), 2),
                         round(P, 2), round(L, 2), round(random.choice([10, 12, 15, 18, 20]), 1), 0])
PILAR = [[float(px), 155.0, 3.0, 3.0, 13.5, 0] for px in range(-680, 700, 60)]
DEK = [[round(px + 30, 1), 155.0, 60.0, 14.0, 1.5, 0] for px in range(-680, 640, 60)]

OBJEK += [
    kotak("JALAN_MobilDWARA", (-46, 158), (5, 2, 1.8), "Kendaraan", catatan="START di sampingnya"),
    kotak("JALAN_Mobil1", (-330, 160), (4.5, 2, 1.6), "Mobil", True, "tanpa", curian=True),
    kotak("JALAN_Mobil2", (-250, 150), (4.5, 2, 1.6), "Mobil", True, "tanpa", curian=True),
    kotak("JALAN_Mobil3", (60, 160), (4.5, 2, 1.6), "Mobil", True, "tanpa", curian=True),
    kotak("JALAN_Angkot", (300, 150), (5, 2, 2), "Mobil", True, "tanpa", curian=True),
    kotak("JALAN_Gerobak1", (110, 150), (2, 1.2, 1.4), "Kayu", True, "tanpa", curian=True),
    kotak("JALAN_Gerobak2", (-140, 160), (2, 1.2, 1.4), "Kayu", True, "tanpa", curian=True),
    dinding("JALAN_GarisPolisiBarat", (-500, 145), (-500, 165), 1.0, 0.1, "Penanda", tanpa_tabrakan=True),
    dinding("JALAN_GarisPolisiTimur", (680, 145), (680, 165), 1.0, 0.1, "Penanda", tanpa_tabrakan=True),
    kotak("JALAN_MobilPemadamBarat", (-492, 155), (8, 2.5, 3), "Penanda"),
    kotak("JALAN_MobilPemadamTimur", (672, 155), (8, 2.5, 3), "Penanda"),
]

# =========================== PASAR (tutup, F4) ===========================
OBJEK += [
    kotak("PASAR_Los1", (272, 105), (120, 50, 8), "Kota", True, "normal"),
    kotak("PASAR_Los2", (272, 45), (120, 50, 8), "Kota", True, "normal"),
    kotak("PASAR_Los3", (272, -10), (120, 30, 6), "Kota", True, "normal"),
    dinding("PASAR_GerbangDikunci", (205, 70), (205, 92), 4.0, 0.4, "Penanda", catatan="gerbang pasar dikunci (dibuka Ep 4)"),
]

# =========================== GUDANG & PABRIK ADIKARA (tanpa penalti) ===========================
OBJEK += [
    kotak("GUDANG_Gudang1", (425, 104), (90, 48, 14), "Adikara", True, "tanpa", milik="Adikara"),
    kotak("GUDANG_Gudang2", (535, 104), (90, 48, 14), "Adikara", True, "tanpa", milik="Adikara"),
    kotak("GUDANG_Pabrik", (640, 95), (80, 60, 18), "Adikara", True, "tanpa", milik="Adikara"),
    kotak("GUDANG_Cerobong", (668, 118), (5, 5, 35), "Adikara", True, "tanpa", milik="Adikara"),
    kotak("GUDANG_Truk1", (420, 55), (10, 3, 4), "Alat", True, "tanpa", milik="Adikara", yaw=90),
    kotak("GUDANG_Truk2", (432, 55), (10, 3, 4), "Alat", True, "tanpa", milik="Adikara", yaw=90),
    kotak("GUDANG_Truk3", (444, 55), (10, 3, 4), "Alat", True, "tanpa", milik="Adikara", yaw=90),
    kotak("GUDANG_PosJaga", (370, 135), (5, 4, 3), "Alat", True, "tanpa", milik="Adikara"),
    kotak("GUDANG_Dermaga", (485, -68), (70, 26, 1.0), "Kota", True, "tanpa", milik="Adikara", z=3.5,
          catatan="dermaga bongkar ke kali"),
    dinding("GUDANG_PagarBarat", (360, 140), (360, -45), 2.5, 0.2, "Alat", milik="Adikara"),
    dinding("GUDANG_PagarUtara", (378, 140), (690, 140), 2.5, 0.2, "Alat", milik="Adikara"),
]
KONTAINER = []
for i, gx in enumerate(range(470, 690, 16)):
    for gy in (-5, 6, 17, 28):
        if random.random() < 0.85:
            KONTAINER.append([float(gx), float(gy), 12.0, 2.5, 2.6 * random.choice([1, 1, 2]), 0])

# =========================== REL + STASIUN (penalti normal) ===========================
OBJEK += [
    kotak("REL_JembatanJalan", (-550, 155), (20, 34, 3), "Kota", z=M.Z_REL - 3, catatan="rel di atas jalan raya (celah tanggul)"),
    kotak("REL_JembatanKali", (-550, -105), (12, 40, 2), "Kota", z=M.Z_REL - 2, catatan="tidak bisa hancur"),
    kotak("REL_JembatanInspeksi", (-550, -133), (20, 12, 3), "Kota", z=M.Z_REL - 3),
    kotak("STASIUN_Bangunan", (-625, 60), (40, 20, 8), "Kota", True, "normal"),
    kotak("STASIUN_AtapPeron", (-575, 60), (6, 140, 0.5), "Kota", True, "normal", z=M.Z_REL + 3.5),
]
z0, _ = alas((-575, 60), 10, 140)
OBJEK.append(kotak("STASIUN_Peron", (-575, 60), (10, 140, round(M.Z_REL - z0 - 0.2, 2)), "Kota", True, "normal",
                   catatan="peron sejajar puncak rel"))
OBJEK.append({"id": "REL_Kereta", "jenis": "kotak", "pos": [-550, 250], "ukuran": [3.2, 80, 4], "mi": "Kendaraan", "hancur": False,
              "catatan": "rangkaian kereta diam (penanda bahaya ringan; bergerak nanti)"})

# =========================== BANTARAN, KALI, PINTU AIR, JEMBATAN ===========================
OBJEK += [
    {"id": "BANTARAN_LapanganTepiKali", "jenis": "bidang", "pos": [-420, -68], "ukuran": [60, 30], "mi": "Lapangan", "hancur": False,
     "catatan": "titik gabung kawanan + transformasi"},
    kotak("BANTARAN_Perahu1", (-250, -78), (6, 2, 1), "Kayu"),
    kotak("BANTARAN_Perahu2", (90, -78), (6, 2, 1), "Kayu"),
    kotak("BANTARAN_Gubuk1", (-330, -70), (5, 4, 3), "Kayu", True, "normal"),
    kotak("BANTARAN_Gubuk2", (260, -70), (5, 4, 3), "Kayu", True, "normal"),
    {"id": "AIR_Kali", "jenis": "bidang", "pos": [0, -105], "ukuran": [1400, 42], "z": 0.0, "mi": "Air", "hancur": False,
     "tanpa_tabrakan": True},
    {"id": "AIR_AnakKali", "jenis": "bidang", "pos": [-505, -362], "ukuran": [32, 476], "z": 0.0, "mi": "Air", "hancur": False,
     "tanpa_tabrakan": True},
    kotak("PINTUAIR_MenaraBarat", (-528, -128), (6, 6, 13.5), "Kota", z=-1.5, catatan="tidak bisa hancur; T5 di puncak (+12)"),
    kotak("PINTUAIR_MenaraTimur", (-482, -128), (6, 6, 13.5), "Kota", z=-1.5),
    kotak("PINTUAIR_Jembatan", (-505, -128), (40, 4, 1.0), "Kota", z=6.0),
    kotak("PINTUAIR_Daun", (-505, -128), (30, 0.6, 7.5), "Alat", z=-1.5),
    # jembatan gantung kuning (landmark), dek di +4,0
    kotak("JEMBATAN_GantungDek", (-105, -105), (1.5, 52, 0.2), "JembatanKuning", z=4.0),
    kotak("JEMBATAN_GantungTiangU1", (-106.5, -78), (0.4, 0.4, 8), "JembatanKuning"),
    kotak("JEMBATAN_GantungTiangU2", (-103.5, -78), (0.4, 0.4, 8), "JembatanKuning"),
    kotak("JEMBATAN_GantungTiangS1", (-106.5, -132), (0.4, 0.4, 8), "JembatanKuning"),
    kotak("JEMBATAN_GantungTiangS2", (-103.5, -132), (0.4, 0.4, 8), "JembatanKuning"),
    kotak("JEMBATAN_BetonDek", (156, -105), (8, 54, 1.0), "Kota", z=3.5, catatan="mobil; evakuasi warga ke selatan"),
]

# =========================== SELATAN: lapangan bola, sawah, SUTET, menara air ===========================
OBJEK += [
    {"id": "SELATAN_LapanganBola", "jenis": "bidang", "pos": [-200, -414], "ukuran": [105, 68], "mi": "Lapangan", "hancur": False},
    kotak("SELATAN_MenaraAir_Tiang", (260, -230), (3, 3, 24), "Kota", True, "normal"),
    kotak("SELATAN_MenaraAir_Tangki", (260, -230), (8, 8, 6), "Kota", True, "normal", z_dasar_relatif=24),
]
for i, sx in enumerate((-400, -40, 320, 660), 1):
    OBJEK.append(kotak(f"SELATAN_SUTET{i}", (sx, -520), (8, 8, 48), "Kendaraan", True, "tanpa", catatan="pembanding skala 48 m"))
for i, (gx, gy) in enumerate([(-350, -470), (100, -380), (400, -450), (550, -380)], 1):
    OBJEK.append(kotak(f"SELATAN_Gubuk{i}", (gx, gy), (3, 3, 3), "Kayu"))

# =========================== LATAR (di luar medan) ===========================
for i in range(9):
    OBJEK.append({"id": f"LATAR_GedungAdikara{i + 1}", "jenis": "kotak", "pos": [-480 + 120 * i, 520 + 60 * (i % 3)], "z": M.Z_UTARA,
                  "ukuran": [45, 40, 60 + 25 * (i % 4)], "mi": "Kota", "hancur": False, "tanpa_tabrakan": True,
                  "catatan": "Distrik Adikara (Ep 3), tidak bisa didatangi"})

# =========================== POHON & TIANG (pembanding skala) ===========================
def sebar(kotak_, jarak, jitter, peluang, cek):
    x0, x1, y0, y1 = kotak_
    pts = []
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            px, py = x + random.uniform(-jitter, jitter), y + random.uniform(-jitter, jitter)
            if random.random() < peluang and cek(px, py):
                pts.append([round(px, 1), round(py, 1), round(random.uniform(0.8, 1.2), 2)])
            x += jarak
        y += jarak
    return pts


def jauh_dari_rumah(px, py, kelompok, r=5.0):
    return all(abs(px - h[0]) > h[2] / 2 + r or abs(py - h[1]) > h[3] / 2 + r for h in kelompok)


POHON = {
    "Bantaran": sebar((-535, 700, -80, -62), 24, 5, 0.7, lambda x, y: not (430 < x < 540) and abs(x + 105) > 6 and abs(x - 156) > 8
                       and not M.di_kotak(x, y, (-455, -385, -86, -50))),
    "Seberang": sebar((-470, 450, -325, -140), 30, 8, 0.5, lambda x, y: jauh_dari_rumah(x, y, RUMAH_SEBERANG) and y < -140),
    "Selatan": sebar((-480, 700, -595, -345), 50, 15, 0.45, lambda x, y: not M.di_kotak(x, y, (-262, -138, -458, -370))
                     and abs(y + 520) > 8),
    "TepiRel": sebar((-700, -575, -595, 380), 28, 6, 0.6, lambda x, y: not M.di_kotak(x, y, (-655, -570, 30, 190))
                     and not (135 < y < 175) and not (-135 < y < -80)),
    "Lahan_Kosong": sebar((455, 700, -325, -140), 30, 8, 0.5, lambda x, y: True),
}
TIANG = [[round(M.GANG_UTAMA_X + 1.8, 1), float(y)] for y in range(-40, 141, 30)]
TIANG += [[float(x), 144.0] for x in range(-520, 690, 45)]
TIANG += [[float(x), -138.0] for x in range(-460, 450, 45)]

# =========================== KELOMPOK INSTANCED ===========================
KELOMPOK = [
    {"id": "KAMPUNG_RumahInti", "bentuk": "rumah", "mi": "Rumah", "mi_atap": "Atap", "hancur": True, "penalti": "tinggi",
     "tukar_puing": True, "item": RUMAH_INTI},
    {"id": "BARAT_Rumah", "bentuk": "rumah", "mi": "Rumah", "mi_atap": "Atap", "hancur": True, "penalti": "normal",
     "tukar_puing": True, "item": RUMAH_BARAT},
    {"id": "SEBERANG_Rumah", "bentuk": "rumah", "mi": "Rumah", "mi_atap": "Atap", "hancur": True, "penalti": "normal",
     "tukar_puing": True, "item": RUMAH_SEBERANG},
    {"id": "JALAN_Ruko", "bentuk": "kotak", "mi": "Kota", "hancur": True, "penalti": "normal", "tukar_puing": True, "item": RUKO},
    {"id": "KOTA_Blok", "bentuk": "kotak", "mi": "Kota", "hancur": True, "penalti": "normal", "tukar_puing": True, "item": KOTA},
    {"id": "LAYANG_Pilar", "bentuk": "kotak", "mi": "Layang", "hancur": True, "penalti": "normal", "tukar_puing": True,
     "z": M.Z_UTARA, "item": PILAR},
    {"id": "LAYANG_Dek", "bentuk": "kotak", "mi": "Layang", "hancur": True, "penalti": "normal", "tukar_puing": True,
     "z": M.Z_UTARA + 13.5, "item": DEK},
    {"id": "GUDANG_Kontainer", "bentuk": "kotak", "mi": "Adikara", "hancur": True, "penalti": "tanpa", "milik": "Adikara",
     "tukar_puing": True, "item": KONTAINER},
]

PENANDA = [
    {"id": "START", "pos": [-40, 155], "jenis": "PlayerStart", "hadap_ke": [-105, -105]},
    {"id": "CLUE_1_JejakKaki", "pos": [-170, 72], "jenis": "titik", "label": "★1 jejak kaki naik atap (rumah kemalingan)"},
    {"id": "CLUE_2_CCTV", "pos": [143, 106], "jenis": "titik", "label": "★2 CCTV warung + mainan"},
    {"id": "CLUE_O_Sesajen", "pos": [-218, -27], "jenis": "titik", "label": "○ sesajen (gang buntu, opsional)"},
    {"id": "CP_Kejar", "pos": [-26, 86], "jenis": "area", "radius": 6, "label": "checkpoint · awal kejar (pos RT)"},
    {"id": "T1", "pos": [-170, 98], "jenis": "titik", "di_atap": True, "label": "T1 atap"},
    {"id": "T2", "pos": [-78, 39], "jenis": "titik", "di_atap": True, "label": "T2 atap seng"},
    {"id": "T3", "pos": [117, 26], "jenis": "titik", "di_atap": True, "label": "T3 atap → gang"},
    {"id": "CP_Tuyul3", "pos": [117, 20], "jenis": "area", "radius": 5, "label": "checkpoint · setelah tuyul ke-3"},
    {"id": "T4", "pos": [-105, -105], "jenis": "titik", "z": 4.2, "label": "T4 jembatan gantung"},
    {"id": "T5", "pos": [-528, -128], "jenis": "titik", "z": 12.2, "label": "T5 menara pintu air"},
    {"id": "UMPAN_Mainan", "pos": [146, 100], "jenis": "titik", "label": "umpan mainan (warung)"},
    {"id": "UMPAN_Yuyu", "pos": [-250, -70], "jenis": "titik", "label": "umpan yuyu (bantaran)"},
    {"id": "GABUNG", "pos": [-420, -68], "jenis": "area", "radius": 15, "label": "kawanan bergabung → tuyul raksasa 45 m"},
    {"id": "TRANSFORMASI", "pos": [-400, -62], "jenis": "titik", "label": "Aksa transformasi"},
    {"id": "JAYADWARA_Mulai", "pos": [-380, -105], "jenis": "titik", "label": "Jayadwara mulai di kali (45 m)"},
    {"id": "CP_Fase1", "pos": [-380, -100], "jenis": "area", "radius": 20, "label": "checkpoint · fase 1"},
    {"id": "BOSS_Fase1_Tujuan", "pos": [525, 60], "jenis": "area", "radius": 30, "label": "fase 1: boss lari bawa mobil ke gudang"},
    {"id": "BOSS_Fase2_Asli", "pos": [600, 10], "jenis": "titik", "label": "fase 2: tuyul besar ASLI (gudang)"},
    {"id": "BOSS_Fase2_Palsu1", "pos": [-612, 60], "jenis": "titik", "label": "fase 2: tuyul besar palsu (stasiun)"},
    {"id": "BOSS_Fase2_Palsu2", "pos": [-200, -414], "jenis": "titik", "label": "fase 2: tuyul besar palsu (lapangan bola)"},
    {"id": "CP_Fase2", "pos": [0, -105], "jenis": "area", "radius": 20, "label": "checkpoint · fase 2"},
    {"id": "WARGA_Kumpul", "pos": [0, -470], "jenis": "area", "radius": 25, "label": "warga mengungsi (sawah selatan)"},
]
ZONA = [
    {"id": "ZONA_PenaltiTinggi_Kampung", "x": [M.KAMPUNG[0], M.KAMPUNG[1]], "y": [M.KAMPUNG[2], M.KAMPUNG[3]], "warna": "merah",
     "label": "penalti tinggi (kampung padat)"},
    {"id": "ZONA_Aman_Kali", "x": [-700, 700], "y": [M.KALI_Y[0] - 3, M.TANGGUL_Y[1]], "warna": "hijau",
     "label": "zona aman: kali + bantaran + lapangan tepi kali"},
    {"id": "ZONA_Aman_AnakKali", "x": [M.ANAK_KALI_X[0] - 5, M.ANAK_KALI_X[1] + 5], "y": [-600, M.KALI_Y[0] - 3], "warna": "hijau",
     "label": "zona aman: anak kali"},
    {"id": "ZONA_Aman_Selatan", "x": [-480, 700], "y": [-600, -340], "warna": "hijau", "label": "zona aman: lapangan bola + sawah kota"},
    {"id": "ZONA_TanpaPenalti_Gudang", "x": [M.GUDANG[0], M.GUDANG[1]], "y": [M.GUDANG[2], M.GUDANG[3]], "warna": "ungu",
     "label": "milik Adikara: hancur tanpa penalti"},
]
KAMERA = [
    {"id": "C1_START_MulutGang", "pos": [-40, 155], "tinggi_di_atas_tanah": 1.6, "lihat_ke": [-105, -105, 4], "fov": 70, "cahaya": "siang"},
    {"id": "C2_AtapT2", "pos": [-96, 52], "tinggi_di_atas_tanah": 5.1, "lihat_ke": [117, 26, 8], "fov": 75, "cahaya": "sore"},
    {"id": "C3_JembatanGantung", "pos": [-105, -82], "tinggi_di_atas_tanah": 1.6, "lihat_ke": [-505, -128, 8], "fov": 70, "cahaya": "sore"},
    {"id": "C4_MataJayadwara", "pos": [-380, -105], "tinggi_di_atas_tanah": 42, "lihat_ke": [525, 60, 6], "fov": 70, "cahaya": "keemasan"},
    {"id": "C5_TampakAtas", "pos": [0, -100], "ortho": True, "lebar_ortho": 1450, "cahaya": "siang"},
    {"id": "C6_DariLapanganBola", "pos": [-200, -414], "tinggi_di_atas_tanah": 1.6, "lihat_ke": [-26, 80, 10], "fov": 70, "cahaya": "keemasan"},
    {"id": "C7_GudangAdikara", "pos": [400, -20], "tinggi_di_atas_tanah": 1.6, "lihat_ke": [600, 100, 10], "fov": 70, "cahaya": "sore"},
    {"id": "C8_JalanLayangRaksasa", "pos": [-300, 120], "tinggi_di_atas_tanah": 42, "lihat_ke": [400, 155, 24], "fov": 70, "cahaya": "keemasan"},
]
RUTE_INVESTIGASI = [[-40, 155], [-26, 145], [-26, 91], [-26, 86], [-80, 91], [-140, 91], [-170, 86], [-170, 72],
                    [-140, 91], [-26, 91], [30, 91], [90, 91], [143, 100], [143, 106]]
RUTE_KEJAR = [[-26, 86], [-170, 84.5], [-170, 98]] + [list(p) for p in JALUR_ATAP[1:]] + \
             [[117, 20], [90, -13], [-26, -13], [-26, -50], [-105, -60], [-105, -78], [-105, -105], [-105, -80],
              [-300, -70], [-480, -72], [-528, -122]]

# warna MI_Ep02_<Nama> (sRGB). 8 slot medan + objek; satu master M_Hermes_Greybox (parameter Warna)
MI_WARNA = {
    "Air": [91, 143, 176], "Rel": [90, 85, 80], "Jalan": [70, 72, 75], "Gudang": [150, 150, 145], "Paving": [170, 172, 165],
    "Kampung": [185, 160, 120], "Bantaran": [120, 155, 85], "Sawah": [126, 170, 80],
    "Rumah": [205, 185, 150], "Atap": [150, 150, 155], "AtapNaik": [230, 110, 40], "Kota": [120, 128, 122],
    "Layang": [95, 100, 105], "Adikara": [125, 92, 142], "Alat": [230, 180, 40], "Kayu": [140, 100, 60],
    "Kendaraan": [40, 40, 45], "Mobil": [200, 60, 60], "Musala": [240, 240, 235], "JembatanKuning": [245, 205, 40],
    "Lapangan": [105, 165, 75], "Pohon": [70, 110, 65], "Penanda": [225, 50, 50],
}

DATA = {
    "versi": "ep02_layout_v02 (16 Okt 2026, dari docs/31 bagian 2a). Dibuat oleh Art/Level/buat_layout_ep02_v02.py — jangan sunting manual",
    "medan_modul": "ep02_medan_v02",
    "satuan": "meter; x = timur, y = utara, z = atas (0 = muka air kali). UE: X = x*100, Y = -y*100, Z = z*100 (cm)",
    "z_otomatis": "objek/item tanpa 'z' diletakkan di atas medan: alas = elev terendah di tapak; 'z' = tinggi alas absolut",
    "medan": {"x_min": M.BATAS_MEDAN[0], "x_max": M.BATAS_MEDAN[1], "y_min": M.BATAS_MEDAN[2], "y_max": M.BATAS_MEDAN[3],
              "sel": 2.5, "material_zona": "pakai fungsi zona_material(x, y) di ep02_medan_v02.py "
                                          "(Air, Rel, Jalan, Gudang, Paving, Kampung, Bantaran, Sawah)"},
    "mi_warna": MI_WARNA,
    "objek": OBJEK,
    "kelompok": KELOMPOK,
    "kelompok_catatan": "satu actor per kelompok berisi ISM; item = [x, y, P, L, T, yaw]; bentuk 'rumah' = dinding (T-0,5) + atap 0,5 m "
                        "(P+0,4 x L+0,4); 'z' kelompok = alas absolut semua item",
    "pohon_kelompok": POHON,
    "pohon_bentuk": {"batang": {"diameter": 0.5, "tinggi": 7.0, "mi": "Kayu"}, "tajuk": {"diameter": 7.0, "tinggi": 8.0, "z_relatif": 5.0, "mi": "Pohon"},
                     "catatan": "ukuran x faktor skala (angka ketiga di tiap titik); batang BlockAll, tajuk NoCollision"},
    "tiang_listrik": {"titik": TIANG, "diameter": 0.3, "tinggi": 9.0, "mi": "Kendaraan"},
    "penanda": PENANDA,
    "zona": ZONA,
    "batas_arena": {"x": [M.BATAS_ARENA[0], M.BATAS_ARENA[1]], "y": [M.BATAS_ARENA[2], M.BATAS_ARENA[3]], "tinggi": 120,
                    "catatan": "dinding tak terlihat, menghalangi Aksa dan Jayadwara"},
    "kamera": KAMERA,
    "cahaya": {
        "siang": {"pitch": -62, "yaw": 20, "warna": [1.0, 0.98, 0.94], "intensitas_lux": 10.0, "catatan": "12.30, bayangan pendek"},
        "sore": {"pitch": -30, "yaw": 0, "warna": [1.0, 0.92, 0.80], "intensitas_lux": 8.0, "catatan": "15.30"},
        "keemasan": {"pitch": -10, "yaw": 5, "warna": [1.0, 0.70, 0.42], "intensitas_lux": 5.0, "catatan": "17.00, matahari di barat ujung kali"},
        "catatan": "DirectionalLight yaw 0 = sinar menuju +X UE (timur), jadi matahari di barat",
    },
    "rute_investigasi": RUTE_INVESTIGASI,
    "rute_kejar": RUTE_KEJAR,
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
            continue
        P, Lb = o.get("ukuran", [4, 4])[:2]
        lo, hi = alas((x, y), P, Lb, o.get("yaw", 0))
        if hi - lo > 2.0 and o["jenis"] != "bidang":
            print(f"TEMUAN {o['id']}: selisih tanah di tapak {hi - lo:.2f} m")
    # rumah kelompok tidak menimpa objek tunggal / gang utama, tidak saling tumpang
    for k in KELOMPOK:
        for h in k["item"]:
            if not (xmn < h[0] < xmx and ymn < h[1] < ymx):
                print(f"GAGAL item di luar medan: {k['id']} {h}")
                gagal += 1
    for nama, grup in (("inti", RUMAH_INTI), ("barat", RUMAH_BARAT), ("seberang", RUMAH_SEBERANG)):
        sel = {}
        for i, h in enumerate(grup):
            sel.setdefault((int(h[0] // 20), int(h[1] // 20)), []).append(i)
        for i, a in enumerate(grup):
            cx, cy = int(a[0] // 20), int(a[1] // 20)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for j in sel.get((cx + dx, cy + dy), []):
                        if j <= i:
                            continue
                        b = grup[j]
                        if abs(a[0] - b[0]) < (a[2] + b[2]) / 2 - 0.01 and abs(a[1] - b[1]) < (a[3] + b[3]) / 2 - 0.01:
                            print(f"GAGAL rumah {nama} tumpang tindih: {a} x {b}")
                            gagal += 1
    for o in OBJEK:
        if o["jenis"] in ("kotak", "rumah") and o.get("z") is None and not o["id"].startswith(("LATAR_", "KAMPUNG_GangBuntu")):
            x, y = o["pos"]
            P, L = o["ukuran"][:2]
            for h in RUMAH_INTI:
                if abs(x - h[0]) < (P + h[2]) / 2 - 0.01 and abs(y - h[1]) < (L + h[3]) / 2 - 0.01:
                    print(f"GAGAL rumah kelompok menimpa {o['id']}")
                    gagal += 1
                    break
    lebar_gang = min(abs(h[0] - M.GANG_UTAMA_X) - h[2] / 2 for h in RUMAH_INTI)
    ok_g = lebar_gang >= 1.25
    print(f"{'OK ' if ok_g else 'GAGAL'} gang utama bebas: jarak rumah terdekat ke poros {lebar_gang:.2f} m (>= 1,25)")
    gagal += not ok_g
    for p in PENANDA:
        x, y = p["pos"]
        if not (xmn < x < xmx and ymn < y < ymx):
            print(f"GAGAL penanda di luar medan: {p['id']}")
            gagal += 1
    n_hancur = sum(1 for o in OBJEK if o.get("hancur"))
    n_tanpa = sum(1 for o in OBJEK if o.get("penalti") == "tanpa")
    n_chaos = len({o["blok_chaos"] for o in OBJEK if "blok_chaos" in o})
    n_atap = sum(1 for o in OBJEK if o.get("atap_naik"))
    n_pohon = sum(len(v) for v in POHON.values())
    print(f"objek {len(OBJEK)} (hancur {n_hancur}, tanpa penalti {n_tanpa}, blok Chaos {n_chaos} x 4 rumah, atap naik {n_atap}, "
          f"papan {len(PAPAN)})")
    print("kelompok " + ", ".join(f"{k['id']} {len(k['item'])}" for k in KELOMPOK))
    print(f"pohon {n_pohon}, tiang {len(TIANG)}, penanda {len(PENANDA)}, zona {len(ZONA)}, kamera {len(KAMERA)}")
    ri, rk = panjang(RUTE_INVESTIGASI), panjang(RUTE_KEJAR)
    print(f"rute investigasi START -> ★1 -> ★2: {ri:.0f} m (jalan 5 m/s: {ri / 5 / 60:.1f} menit)")
    print(f"rute kejar pos RT -> T5: {rk:.0f} m (lari 6 m/s: {rk / 6 / 60:.1f} menit)")
    if n_chaos != 8:
        print("GAGAL blok Chaos harus 8 (F2)")
        gagal += 1
    print("SEMUA LULUS" if gagal == 0 else f"ADA {gagal} GAGAL")
    return gagal


if __name__ == "__main__":
    g = periksa()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:   # LF juga di Windows (git status tetap bersih)
        json.dump(DATA, f, ensure_ascii=False, indent=1)
    print(f"ditulis: {OUT}")
    sys.exit(1 if g else 0)
