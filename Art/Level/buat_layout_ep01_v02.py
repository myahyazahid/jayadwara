"""Membuat Art/Level/ep01_layout_v02.json dari daftar di bawah + medan ep01_medan_v02.py, lalu memeriksanya.
Pakai: python -I Art/Level/buat_layout_ep01_v02.py   (menulis JSON dan mencetak hasil cek; harus berakhir SEMUA LULUS)
Ubah tata letak di file INI (bukan di JSON), lalu jalankan ulang.
Revisi 17 Okt 2026: galian 260 x 230 m (G1), kamera C1/C3/C5/C7/C8 dipindah (G2), alas objek = elev titik tengah tapak (G4).
"""
import json
import math
import os
import random
import sys

if hasattr(sys.stdout, "reconfigure"):   # console Windows (cp1252) tidak bisa mencetak ★
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01_medan_v02 as M  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ep01_layout_v02.json")


def kotak(id_, pos, ukuran, mi, hancur=False, **kw):
    o = {"id": id_, "jenis": "kotak", "pos": list(pos), "ukuran": list(ukuran), "mi": mi, "hancur": hancur}
    o.update(kw)
    return o


def rumah(id_, pos, mi="Desa", hancur=True, **kw):
    o = {"id": id_, "jenis": "rumah", "pos": list(pos), "ukuran": [10, 8, 6], "mi": mi, "hancur": hancur}
    o.update(kw)
    return o


def dinding(id_, a, b, tinggi, tebal, mi, **kw):
    o = {"id": id_, "jenis": "dinding", "dari": list(a), "ke": list(b), "tinggi": tinggi, "tebal": tebal, "mi": mi, "hancur": False}
    o.update(kw)
    return o


OBJEK = []


def alas(o):
    """Alas objek (m) = elev di titik tengah tapak (G4; sebelumnya titik terendah, sehingga di lereng objek tenggelam >1 m).
    Objek ber-'z' memakai z absolut itu. 'z_dasar_relatif' ditambahkan oleh pembaca."""
    if o.get("z") is not None:
        return float(o["z"])
    if o["jenis"] == "tangga":
        return o["dari"][2]
    if o["jenis"] == "dinding":
        return M.elev((o["dari"][0] + o["ke"][0]) / 2, (o["dari"][1] + o["ke"][1]) / 2)
    return M.elev(o["pos"][0], o["pos"][1])


def tapak_elev(o):
    """Elev di 25 titik tapak (kotak/rumah/kerucut/bidang) atau sepanjang garis (dinding)."""
    if o["jenis"] == "dinding":
        (ax, ay), (bx, by) = o["dari"], o["ke"]
        return [M.elev(ax + (bx - ax) * k / 10, ay + (by - ay) * k / 10) for k in range(11)]
    x, y = o["pos"]
    P, Lb = o.get("ukuran", [4, 4])[:2]
    yaw = math.radians(o.get("yaw", 0))
    zs = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            lx, ly = P / 2 * i / 2, Lb / 2 * j / 2
            zs.append(M.elev(x + lx * math.cos(yaw) - ly * math.sin(yaw), y + lx * math.sin(yaw) + ly * math.cos(yaw)))
    return zs


# ---------- candi (plato +35) ----------
OBJEK += [
    {"id": "CANDI_Induk", "jenis": "candi_bertingkat", "pos": [0, 320], "tingkat": [[18, 18, 6], [14, 14, 6], [9, 9, 5], [4, 4, 3]],
     "mi": "Andesit", "hancur": False},
    kotak("CANDI_GerbangTiangKiri", (-3.5, 180), (3, 3, 8), "Andesit"),
    kotak("CANDI_GerbangTiangKanan", (3.5, 180), (3, 3, 8), "Andesit"),
    kotak("CANDI_GerbangAmbang", (0, 180), (10, 3, 2), "Andesit", z_dasar_relatif=6),
    kotak("CANDI_AlasArcaKiri", (-8, 176), (2, 2, 1), "Andesit"),
    kotak("CANDI_ArcaKiri", (-8, 176), (2, 2, 4), "Arca", z_dasar_relatif=1),
    kotak("CANDI_AlasArcaKanan", (8, 176), (2, 2, 1), "Andesit"),
    kotak("CANDI_ArcaKanan", (8, 176), (2, 2, 4), "Arca", z_dasar_relatif=1, catatan="dililit tali derek (adegan 4)"),
    kotak("CANDI_Prasasti", (0, 175), (2, 0.5, 2), "Andesit"),
    {"id": "CANDI_Tangga", "jenis": "tangga", "dari": [0, 142, 28.0], "ke": [0, 167, 35.0], "lebar": 10, "anak_tangga": 28,
     "mi": "Andesit", "hancur": False},
]
# ---------- reruntuhan candi perwara (hutan utara, area baru v02) ----------
for i, (p, yaw) in enumerate([((-70, 420), 12), ((60, 440), -20), ((-20, 485), 35), ((95, 405), 5)], 1):
    OBJEK.append(kotak(f"PERWARA_Reruntuhan{i}", p, (6, 6, 4), "Andesit", yaw=yaw))
# ---------- galian & sekitarnya ----------
OBJEK += [
    kotak("PROYEK_Tenda1", (45, 30), (4, 4, 2.5), "Terpal"),
    kotak("PROYEK_Tenda2", (-75, 7), (4, 4, 2.5), "Terpal"),
    kotak("PROYEK_Tenda3", (-50, -38), (4, 4, 2.5), "Terpal"),
    kotak("PROYEK_Ekskavator", (136, -28), (9, 4, 4), "Alat", yaw=20),
    kotak("PROYEK_Buldoser", (138, 30), (7, 4, 3.5), "Alat", yaw=-10),
    kotak("PROYEK_TrukDerek", (60, 190), (12, 3, 4), "Alat", yaw=30, catatan="keluar lewat jalan proyek di adegan 6"),
    kotak("PROYEK_BatuLatihan", (-196, -205), (2, 1.5, 0.6), "Andesit", catatan="di samping jalan setapak, menghadap desa"),
]
# ---------- base camp Adikara (area baru v02, +25, tanpa penalti) ----------
OBJEK += [
    kotak("BASECAMP_Kantor1", (180, 95), (12, 3, 3), "Alat", hancur=True, milik="Adikara"),
    kotak("BASECAMP_Kantor2", (196, 95), (12, 3, 3), "Alat", hancur=True, milik="Adikara"),
    kotak("BASECAMP_Kantor3", (212, 95), (12, 3, 3), "Alat", hancur=True, milik="Adikara"),
    kotak("BASECAMP_PosMandor", (175, 45), (14, 6, 3), "Alat", hancur=True, milik="Adikara"),
    kotak("BASECAMP_GudangAlat", (290, 80), (24, 14, 7), "Kendaraan", hancur=True, milik="Adikara"),
    kotak("BASECAMP_Truk1", (300, 15), (10, 3, 4), "Alat", yaw=90, hancur=True, milik="Adikara"),
    kotak("BASECAMP_Truk2", (290, 15), (10, 3, 4), "Alat", yaw=90, hancur=True, milik="Adikara"),
    kotak("BASECAMP_Truk3", (280, 15), (10, 3, 4), "Alat", yaw=90, hancur=True, milik="Adikara"),
    kotak("BASECAMP_TumpukanPipa", (250, -40), (12, 6, 3), "Andesit", hancur=True, milik="Adikara"),
    kotak("BASECAMP_TumpukanBesi", (205, -45), (10, 4, 1.5), "Kendaraan", hancur=True, milik="Adikara"),
    dinding("BASECAMP_PagarUtara", (150, 120), (330, 120), 2.5, 0.2, "Alat"),
    dinding("BASECAMP_PagarTimurA", (330, 120), (330, -5), 2.5, 0.2, "Alat"),
    dinding("BASECAMP_PagarTimurB", (330, -35), (330, -60), 2.5, 0.2, "Alat"),
    dinding("BASECAMP_PagarSelatan", (330, -60), (150, -60), 2.5, 0.2, "Alat"),
    dinding("PROYEK_GarisPolisi", (470, -42), (470, -18), 1.0, 0.1, "Penanda", tanpa_tabrakan=True,
            catatan="jalan ke atas ditutup polisi; mobil DWARA lewat jalan desa"),
]
# ---------- desa (titik mulai v02, penalti) ----------
OBJEK += [
    rumah("DESA_D1_Rumah", (-400, -330)),
    rumah("DESA_D2_Rumah", (-360, -345)),
    rumah("DESA_D3_Rumah", (-320, -325)),
    rumah("DESA_D4_Rumah", (-280, -345)),
    kotak("DESA_D5_Warung", (-240, -330), (6, 5, 4), "Kayu", hancur=True),
    kotak("DESA_D6_Warung", (-205, -365), (6, 5, 4), "Kayu", hancur=True),
    kotak("DESA_D7_MenaraAir", (-250, -385), (4, 4, 15), "Alat", hancur=True),
    kotak("DESA_D8_GarduRonda", (-185, -405), (3, 3, 4), "Kayu", hancur=True),
    rumah("DESA_D9_Cadangan", (-410, -385), cadangan=True),
    rumah("DESA_D10_Cadangan", (-350, -470), cadangan=True),
    kotak("DESA_Musala", (-300, -440), (12, 12, 7), "Musala"),
    {"id": "DESA_Lapangan", "jenis": "bidang", "pos": [-250, -445], "ukuran": [36, 20], "mi": "Sawah", "hancur": False},
    kotak("DESA_MobilDWARA", (-160, -432), (5, 2, 1.8), "Kendaraan", yaw=180),
]
for i, p in enumerate([(-420, -420), (-395, -458), (-372, -412), (-335, -398), (-268, -472), (-222, -472), (-385, -478), (-418, -355)], 1):
    OBJEK.append(rumah(f"DESA_RumahLatar{i}", p, hancur=False, catatan="rumah warga tanpa fisika (pengisi desa)"))
# ---------- sawah ----------
for i, p in enumerate([(0, -260), (150, -300), (250, -380), (60, -420), (300, -250)], 1):
    OBJEK.append(kotak(f"SAWAH_Gubuk{i}", p, (3, 3, 3), "Kayu"))
OBJEK.append({"id": "SAWAH_LapanganBola", "jenis": "bidang", "pos": [250, -225], "ukuran": [60, 40], "mi": "Penanda", "hancur": False})
# ---------- area pilar tol (area baru v02, tanpa penalti) ----------
pilar = [(500 + 28.6 * i, 330 - 71.4 * i) for i in range(8)]
for i, p in enumerate(pilar, 1):
    OBJEK.append(kotak(f"TOL_Pilar{i}", (round(p[0], 1), round(p[1], 1)), (5, 5, 40), "Andesit", hancur=True, milik="Adikara"))
for i in (0, 1):   # dua bentang gelagar terpasang, sisanya belum
    a, b = pilar[i], pilar[i + 1]
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    yaw = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    OBJEK.append(kotak(f"TOL_Gelagar{i + 1}", (round(cx, 1), round(cy, 1)), (round(L + 5, 1), 12, 3), "Andesit",
                       z=40.0, yaw=round(yaw, 1), hancur=True, milik="Adikara"))
# ---------- latar jauh (di luar medan, tidak bisa didatangi) ----------
for i, (p, d, t) in enumerate([((-1300, 700), 420, 160), ((-200, 1400), 600, 220), ((1200, 1000), 500, 180),
                               ((1600, -200), 450, 140), ((-1500, -400), 380, 120)], 1):
    OBJEK.append({"id": f"LATAR_Bukit{i}", "jenis": "kerucut", "pos": [p[0], p[1]], "z": 0.0, "ukuran": [d, d, t],
                  "mi": "Hutan", "hancur": False, "tanpa_tabrakan": True})
for i in range(10):
    OBJEK.append({"id": f"LATAR_Kota{i + 1}", "jenis": "kotak", "pos": [100 + 70 * i, -1450 - 40 * (i % 3)], "z": 0.0,
                  "ukuran": [40, 30, 20 + 15 * (i % 4)], "mi": "Kendaraan", "hancur": False, "tanpa_tabrakan": True})

# ---------- pembanding skala: pohon & tiang listrik (instanced) ----------
random.seed(7)


def bebas(x, y, jarak_objek=9.0):
    if M.galian_e(x, y) < 1.15 or M.di_kotak(x, y, M.PLATO) or M.di_kotak(x, y, M.BASECAMP) or M.di_kotak(x, y, M.SAWAH):
        return False
    for poly in (M.JALAN_AKSES, M.JALAN_PROYEK, M.JALAN_DESA, M.JALAN_SETAPAK):
        if M.dist_poly(x, y, poly)[0] < 8:
            return False
    if abs(x - M.KALI_X) < 12 or abs(x) < M.MULUT["setengah_lebar"] + 8 and -200 < y < -40:
        return False
    for o in OBJEK:
        if "pos" in o and o.get("z", None) is None and math.hypot(o["pos"][0] - x, o["pos"][1] - y) < jarak_objek:
            return False
    return True


def sebar(kotak_, jarak, jitter, peluang=1.0):
    x0, x1, y0, y1 = kotak_
    pts = []
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            px, py = x + random.uniform(-jitter, jitter), y + random.uniform(-jitter, jitter)
            if random.random() < peluang and M.BATAS_MEDAN[0] < px < M.BATAS_MEDAN[1] and M.BATAS_MEDAN[2] < py < M.BATAS_MEDAN[3] \
                    and bebas(px, py):
                pts.append([round(px, 1), round(py, 1), round(random.uniform(0.85, 1.2), 2)])
            x += jarak
        y += jarak
    return pts


POHON = {
    "Hutan_Utara": sebar((-460, 470, 380, 630), 28, 9),
    "Hutan_Lereng": sebar((-460, -110, -300, 370), 34, 10, 0.75) + sebar((110, 470, 125, 370), 34, 10, 0.75),
    "Kebun_Penyangga": sebar((-260, -60, -300, -110), 22, 6, 0.8),
    "Kelapa_Desa": sebar((-440, -160, -500, -300), 30, 8, 0.6),
    "Tepi_Kali": sebar((-470, -455, -560, 620), 26, 4),
    "Lembah_Timur": sebar((360, 770, -560, 380), 45, 12, 0.5),
}
TIANG = []
for poly in (M.JALAN_DESA,):
    for (a, b) in zip(poly, poly[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = int(L // 40)
        for k in range(n):
            t = k / max(n, 1)
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + 6
            TIANG.append([round(x, 1), round(y, 1)])
for x in range(-420, -169, 40):   # jalan desa utama
    TIANG.append([x, -372])

PENANDA = [
    {"id": "START", "pos": [-160, -425], "jenis": "PlayerStart", "hadap_ke": [0, 180]},
    {"id": "CLUE_1_JejakEnergi", "pos": [-110, -20], "jenis": "titik", "label": "★1 jejak energi (bibir galian barat)"},
    {"id": "CLUE_2_Tulang", "pos": [-15, 10], "jenis": "titik", "label": "★2 tulang bergeser"},
    {"id": "CLUE_3_Prasasti", "pos": [0, 173], "jenis": "titik", "label": "★3 prasasti"},
    {"id": "LORE_Perwara", "pos": [60, 450], "jenis": "titik", "label": "○ relief candi perwara (opsional, usulan)"},
    {"id": "LORE_BaseCamp", "pos": [200, 102], "jenis": "titik", "label": "○ dokumen relokasi Adikara (opsional, usulan)"},
    {"id": "WAVE_1", "pos": [25, 105], "jenis": "area", "radius": 15, "label": "W1 · 3 kerangka · undakan atas"},
    {"id": "WAVE_2", "pos": [0, 155], "jenis": "area", "radius": 6, "label": "W2 · 5 kerangka · tangga"},
    {"id": "WAVE_3", "pos": [0, 200], "jenis": "area", "radius": 20, "label": "W3 · 6 kerangka · halaman (checkpoint)"},
    {"id": "BOSS_Bangkit", "pos": [20, 10], "jenis": "titik", "label": "Jerangkong bangkit (31 m)"},
    {"id": "TRANSFORMASI", "pos": [-8, 178], "jenis": "titik", "label": "transformasi di arca kiri"},
    {"id": "JAYADWARA_Mulai", "pos": [0, 225], "jenis": "titik", "label": "Jayadwara mulai (45 m)"},
    {"id": "WARGA_Kumpul", "pos": [-250, -445], "jenis": "area", "radius": 20, "label": "titik kumpul warga"},
]
ZONA = [
    {"id": "ZONA_Aman_Sawah", "x": [M.SAWAH[0], M.SAWAH[1]], "y": [M.SAWAH[2], M.SAWAH[3]], "warna": "hijau", "label": "zona aman (tanpa penalti)"},
    {"id": "ZONA_Aman_BaseCamp", "x": [M.BASECAMP[0], M.BASECAMP[1]], "y": [M.BASECAMP[2], M.BASECAMP[3]], "warna": "hijau",
     "label": "milik Adikara: hancur tanpa penalti"},
    {"id": "ZONA_Aman_PilarTol", "x": [470, 720], "y": [-200, 360], "warna": "hijau", "label": "pilar tol Adikara: hancur tanpa penalti"},
    {"id": "ZONA_Penalti_Desa", "x": [M.DESA[0], M.DESA[1]], "y": [M.DESA[2], M.DESA[3]], "warna": "merah", "label": "penalti meter"},
]
KAMERA = [
    {"id": "C1_START_Desa", "pos": [-150, -450], "tinggi_di_atas_tanah": 2.0, "lihat_ke": [-250, -100, 30], "fov": 70, "cahaya": "sore"},
    {"id": "C2_BibirGalianBarat", "pos": [-110, -20], "tinggi_di_atas_tanah": 1.6, "lihat_ke": [20, 10, -5], "fov": 70, "cahaya": "sore"},
    {"id": "C3_GerbangKeTimur", "pos": [0, 226], "tinggi_di_atas_tanah": 1.6, "lihat_ke": [250, 200, 32], "fov": 70, "cahaya": "sore"},
    {"id": "C4_MataJayadwara", "pos": [0, 225], "tinggi_di_atas_tanah": 42, "lihat_ke": [-150, -400, 0], "fov": 70, "cahaya": "senja"},
    {"id": "C5_TampakAtas", "pos": [80, -20], "ortho": True, "lebar_ortho": 2200, "cahaya": "sore"},
    {"id": "C6_DariSawah", "pos": [100, -350], "tinggi_di_atas_tanah": 3, "lihat_ke": [0, 100, 45], "fov": 70, "cahaya": "senja"},
    {"id": "C7_BaseCamp", "pos": [326, -56], "tinggi_di_atas_tanah": 9.0, "lihat_ke": [225, 45, 24], "fov": 70, "cahaya": "sore"},
    {"id": "C8_PilarTolRaksasa", "pos": [760, -250], "tinggi_di_atas_tanah": 42, "lihat_ke": [560, 96, 35], "fov": 70, "cahaya": "senja"},
]
RUTE_AKSA = [[-160, -425], [-175, -430], [-170, -330], [-200, -260], [-190, -180], [-150, -110], [-125, -55], [-110, -20],
             [-112, -5], [-28, -2], [-15, 10], [0, 52], [0, 124], [0, 142], [0, 167], [0, 173]]

DATA = {
    "versi": "ep01_layout_v02 (16 Okt 2026, dari docs/30 bagian 2a). Dibuat oleh Art/Level/buat_layout_ep01_v02.py — jangan sunting manual",
    "medan_modul": "ep01_medan_v02",
    "satuan": "meter; x = timur, y = utara, z = atas (0 = muka desa). UE: X = x*100, Y = -y*100, Z = z*100 (cm)",
    "z_otomatis": "objek tanpa 'z' diletakkan di atas medan: alas = elev titik tengah tapak (nilainya ada di 'alas_m'; dinding = titik tengah garis, tangga = z 'dari'); 'z' = tinggi alas absolut. Tinggi akhir = alas_m (atau z) + z_dasar_relatif; 'pondasi_m' = perpanjang objek ke bawah sebanyak itu (puncak tetap) supaya sisi rendah di lereng tidak melayang",
    "medan": {"x_min": M.BATAS_MEDAN[0], "x_max": M.BATAS_MEDAN[1], "y_min": M.BATAS_MEDAN[2], "y_max": M.BATAS_MEDAN[3],
              "sel": 2.5, "material_zona": "pakai fungsi zona_material(x, y) di ep01_medan_v02.py (Air, Galian, Jalan, Plato, Sawah, Desa, Hutan)"},
    "objek": OBJEK,
    "pohon_kelompok": {k: v for k, v in POHON.items()},
    "pohon_bentuk": {"batang": {"diameter": 0.6, "tinggi": 8.0, "mi": "Kayu"}, "tajuk": {"diameter": 7.0, "tinggi": 9.0, "z_relatif": 6.0, "mi": "Hutan"},
                     "catatan": "ukuran x faktor skala (angka ketiga di tiap titik); batang BlockAll, tajuk NoCollision"},
    "tiang_listrik": {"titik": TIANG, "diameter": 0.3, "tinggi": 9.0, "mi": "Kendaraan"},
    "penanda": PENANDA,
    "zona": ZONA,
    "batas_arena": {"x": [-470, 720], "y": [-525, 500], "tinggi": 120, "catatan": "dinding tak terlihat, menghalangi Aksa dan Jayadwara"},
    "kamera": KAMERA,
    "cahaya": {
        "sore": {"pitch": -25, "yaw": 0, "warna": [1.0, 0.95, 0.88], "intensitas_lux": 8.0,
                 "catatan": "lebih tinggi & netral dari v01 supaya warna zona terbaca saat uji"},
        "senja": {"pitch": -3, "yaw": 0, "warna": [1.0, 0.45, 0.30], "intensitas_lux": 2.0},
        "catatan": "DirectionalLight yaw 0 = sinar menuju +X UE (timur), jadi matahari di barat",
    },
    "rute_aksa": RUTE_AKSA,
}


def periksa():
    gagal = 0
    xmn, xmx, ymn, ymx = M.BATAS_MEDAN
    for o in OBJEK:
        if "pos" not in o or o.get("z") is not None:
            continue
        x, y = o["pos"]
        if not (xmn < x < xmx and ymn < y < ymx):
            print(f"GAGAL di luar medan: {o['id']}")
            gagal += 1
            continue
        zs = tapak_elev(o)
        beda = max(zs) - min(zs)
        if beda > 2.0 and o["jenis"] != "candi_bertingkat":
            print(f"TEMUAN {o['id']}: selisih tanah di tapak {beda:.2f} m")
        a = alas(o)
        if a - min(zs) > 1.0 and o["jenis"] != "candi_bertingkat":
            print(f"TEMUAN {o['id']}: melayang {a - min(zs):.2f} m di sisi rendah tapak (alas {a:.2f} m) -> pondasi_m {o.get('pondasi_m')}")
        if max(zs) - a > 1.0 and o["jenis"] != "candi_bertingkat":
            print(f"TEMUAN {o['id']}: tertanam {max(zs) - a:.2f} m di sisi tinggi tapak (alas {a:.2f} m)")
    for o in OBJEK:
        if o["jenis"] == "dinding" and o.get("z") is None:
            zs = tapak_elev(o)
            if max(zs) - min(zs) > 1.0:
                print(f"TEMUAN {o['id']}: dinding di lereng, selisih sepanjang garis {max(zs) - min(zs):.2f} m")
    # tumpang tindih tapak (kasar, lingkaran)
    tapak = [(o["id"], o["pos"], max(o.get("ukuran", [1, 1])[:2]) / 2) for o in OBJEK if "pos" in o and o.get("z") is None
             and o["jenis"] in ("kotak", "rumah") and not o["id"].startswith(("CANDI_", "LATAR_"))]
    for i in range(len(tapak)):
        for j in range(i + 1, len(tapak)):
            a, b = tapak[i], tapak[j]
            if math.hypot(a[1][0] - b[1][0], a[1][1] - b[1][1]) < (a[2] + b[2]) * 0.8:
                print(f"GAGAL tumpang tindih: {a[0]} x {b[0]}")
                gagal += 1
    for p in PENANDA:
        x, y = p["pos"]
        if not (xmn < x < xmx and ymn < y < ymx):
            print(f"GAGAL penanda di luar medan: {p['id']}")
            gagal += 1
    # panjang rute Aksa di permukaan
    total = 0.0
    for a, b in zip(RUTE_AKSA, RUTE_AKSA[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1])))
        for k in range(n):
            x0, y0 = a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n
            x1, y1 = a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n
            total += math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2 + (M.elev(x1, y1) - M.elev(x0, y0)) ** 2)
    n_pohon = sum(len(v) for v in POHON.values())
    print(f"objek {len(OBJEK)} (hancur {sum(1 for o in OBJEK if o.get('hancur'))}, milik Adikara {sum(1 for o in OBJEK if o.get('milik'))}), "
          f"pohon {n_pohon}, tiang {len(TIANG)}, penanda {len(PENANDA)}, zona {len(ZONA)}, kamera {len(KAMERA)}")
    print(f"rute Aksa START -> ★3: {total:.0f} m (jalan 5 m/s: {total / 5 / 60:.1f} menit)")
    print("SEMUA LULUS" if gagal == 0 else f"ADA {gagal} GAGAL")
    return gagal


if __name__ == "__main__":
    for o in OBJEK:
        if o.get("z") is None:
            o["alas_m"] = round(alas(o), 2)
            if o["jenis"] in ("kotak", "rumah", "kerucut"):   # sisi rendah tapak melayang -> perpanjang ke bawah, puncak tetap
                melayang = o["alas_m"] - min(tapak_elev(o))
                if melayang > 0.3:
                    o["pondasi_m"] = round(melayang + 0.1, 2)
    g = periksa()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:   # LF juga di Windows (git status tetap bersih)
        json.dump(DATA, f, ensure_ascii=False, indent=1)
    print(f"ditulis: {OUT}")
    sys.exit(1 if g else 0)
