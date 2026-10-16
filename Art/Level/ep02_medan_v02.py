"""Fungsi ketinggian medan Ep02_KampungKali tata letak **v02** (meter; X timur, Y utara, Z atas, 0 = muka air kali).
Sumber: docs/31 bagian 2a (v02, 16 Okt 2026, opsi B: perluas + area baru). Kampung inti ±1,3x v01 tetap padat;
cincin luar: gudang Adikara, jalan layang, stasiun, pintu air + anak kali, lapangan bola + sawah kota.
Data objek: Art/Level/ep02_layout_v02.json (dibuat Art/Level/buat_layout_ep02_v02.py).
Uji mandiri: python -I Art/Level/ep02_medan_v02.py  (harus mencetak SEMUA LULUS)."""
import math


def smoothstep(a, b, v):
    if a == b:
        return 0.0 if v < a else 1.0
    t = max(0.0, min(1.0, (v - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def di_kotak(x, y, k):
    return k[0] <= x <= k[1] and k[2] <= y <= k[3]


# ---------------- tata letak (meter) ----------------
BATAS_MEDAN = (-700, 700, -600, 400)            # x_min, x_max, y_min, y_max (1400 x 1000 m)
BATAS_ARENA = (-650, 690, -600, 330)            # ±1340 x 930 m

Z_UTARA = 9.0                                   # jalan raya, ruko, blok kota
JALAN_RAYA_Y = (145.0, 165.0)
KAMPUNG = (-260, 195, -50, 140)                 # kampung padat inti (penalti tinggi)
KAMPUNG_BARAT = (-530, -265, -50, 140)          # kampung pinggir barat, jarang (penalti normal)
PASAR = (205, 340, -30, 140)
GUDANG = (360, 690, -45, 140)                   # milik Adikara, diratakan
Z_GUDANG = 6.0
TANGGUL_Y = (-56.0, -50.0)                      # puncak tanggul +5, jalan setapak 6 m
BANTARAN_Y = (-82.0, -60.0)                     # +3,5
KALI_Y = (-125.0, -85.0)                        # lebar 40 m
Z_TANGGUL, Z_BANTARAN, Z_DASAR_KALI = 5.0, 3.5, -1.5
ANAK_KALI_X = (-520.0, -490.0)                  # dari pintu air ke selatan
SEBERANG_Y = (-330.0, -130.0)                   # kampung seberang + lahan kosong, +3,5
Z_SEBERANG = 3.5
SELATAN = (-700, 700, -600, -340)               # lapangan bola + sawah kota, +3,0
Z_SELATAN = 3.0
JALAN_INSPEKSI_Y = (-136.0, -130.0)

REL_X = (-560.0, -540.0)                        # puncak tanggul rel
REL_KAKI = 9.0                                  # lebar lereng tanggul tiap sisi
Z_REL = 12.0                                    # puncak rel (tanggul ±3–8,5 m di atas tanah)
REL_CELAH_Y = [(138.0, 172.0), (-88.0, -122.0), (-139.0, -127.0)]   # jalan raya, kali, jalan inspeksi: lewat jembatan
GANG_UTAMA_X = -26.0


def tanah_dasar(x, y):
    """Medan tanpa rel dan air (dipakai juga untuk menghitung tinggi tanggul rel)."""
    if y >= JALAN_RAYA_Y[0]:
        return Z_UTARA
    if y >= TANGGUL_Y[1]:                       # kampung & pasar: turun pelan 9 -> 5 ke selatan
        z = 5.0 + (y - TANGGUL_Y[1]) / (JALAN_RAYA_Y[0] - TANGGUL_Y[1]) * 4.0
        if di_kotak(x, y, GUDANG):
            z = Z_GUDANG
        else:                                   # tepi gudang menyambung landai (10 m)
            dx = max(GUDANG[0] - x, 0.0, x - GUDANG[1])
            dy = max(GUDANG[2] - y, 0.0, y - GUDANG[3])
            d = math.hypot(dx, dy)
            if d < 10.0 and x > GUDANG[0] - 10:
                z = lerp(Z_GUDANG, z, smoothstep(0, 10, d))
        return z
    if y >= TANGGUL_Y[0]:
        return Z_TANGGUL
    if y >= BANTARAN_Y[1]:                      # lereng tanggul 5 -> 3,5
        return lerp(Z_BANTARAN, Z_TANGGUL, smoothstep(BANTARAN_Y[1], TANGGUL_Y[0], y))
    if y >= BANTARAN_Y[0]:
        return Z_BANTARAN
    if y >= KALI_Y[1]:                          # tebing utara kali 3,5 -> -1,5
        return lerp(Z_DASAR_KALI, Z_BANTARAN, smoothstep(KALI_Y[1], BANTARAN_Y[0], y))
    if y >= KALI_Y[0]:
        return Z_DASAR_KALI
    if y >= SEBERANG_Y[1]:                      # tebing selatan kali -1,5 -> 3,5
        return lerp(Z_DASAR_KALI, Z_SEBERANG, smoothstep(KALI_Y[0], SEBERANG_Y[1], y))
    if y >= SELATAN[3]:
        return lerp(Z_SELATAN, Z_SEBERANG, smoothstep(SELATAN[3], SEBERANG_Y[0], y))
    return Z_SELATAN


def di_anak_kali(x, y):
    return ANAK_KALI_X[0] <= x <= ANAK_KALI_X[1] and y < KALI_Y[0] + 2


def elev(x, y):
    z = tanah_dasar(x, y)
    # anak kali: dasar -1,5, tebing 4 m
    if y < KALI_Y[0] + 2:
        d = max(ANAK_KALI_X[0] - x, x - ANAK_KALI_X[1])
        if d <= 0:
            z = Z_DASAR_KALI
        elif d < 4:
            z = lerp(Z_DASAR_KALI, z, smoothstep(0, 4, d))
    # tanggul rel (kecuali di celah jembatan)
    if not any(a <= y <= b or b <= y <= a for a, b in REL_CELAH_Y):
        d = max(REL_X[0] - x, x - REL_X[1])
        if d <= 0:
            z = Z_REL
        elif d < REL_KAKI:
            z = max(z, lerp(Z_REL, z, smoothstep(0, REL_KAKI, d)))
    return z


def zona_material(x, y, z=None):
    """Slot material medan (urutan = prioritas). Dipakai skrip Blender V2."""
    if z is None:
        z = elev(x, y)
    if z < 0.5 and (KALI_Y[0] - 1 <= y <= KALI_Y[1] + 1 or di_anak_kali(x, y)):
        return "Air"
    if REL_X[0] - REL_KAKI <= x <= REL_X[1] + REL_KAKI and z > tanah_dasar(x, y) + 0.3:
        return "Rel"
    if JALAN_RAYA_Y[0] <= y <= JALAN_RAYA_Y[1] or JALAN_INSPEKSI_Y[0] <= y <= JALAN_INSPEKSI_Y[1]:
        return "Jalan"
    if abs(x - GANG_UTAMA_X) <= 1.25 and KAMPUNG[2] <= y <= KAMPUNG[3] + 5:
        return "Jalan"
    if TANGGUL_Y[0] <= y <= TANGGUL_Y[1]:
        return "Jalan"                          # jalan setapak di puncak tanggul
    if di_kotak(x, y, GUDANG):
        return "Gudang"
    if y > JALAN_RAYA_Y[1] or di_kotak(x, y, PASAR) or (x < REL_X[0] - REL_KAKI and y > TANGGUL_Y[1]):
        return "Paving"
    if di_kotak(x, y, KAMPUNG) or di_kotak(x, y, KAMPUNG_BARAT):
        return "Kampung"
    if KALI_Y[1] < y < TANGGUL_Y[0]:
        return "Bantaran"
    if SEBERANG_Y[0] <= y < KALI_Y[0] and x < 450:
        return "Kampung"
    if y < SELATAN[3] or SEBERANG_Y[0] <= y < KALI_Y[0]:
        return "Sawah"
    return "Bantaran"


TITIK_UJI = {   # (x, y): tinggi target ± toleransi
    "jalan_raya (0,155)": ((0, 155), 9.0, 0.05),
    "blok_kota (200,300)": ((200, 300), 9.0, 0.05),
    "pos_rt (-26,91)": ((-26, 91), 7.89, 0.05),
    "kampung_selatan (0,-40)": ((0, -40), 5.21, 0.05),
    "puncak_tanggul (0,-53)": ((0, -53), 5.0, 0.05),
    "bantaran (-420,-68)": ((-420, -68), 3.5, 0.05),
    "dasar_kali (0,-105)": ((0, -105), -1.5, 0.05),
    "anak_kali (-505,-300)": ((-505, -300), -1.5, 0.05),
    "kampung_seberang (0,-230)": ((0, -230), 3.5, 0.05),
    "lapangan_bola (-200,-414)": ((-200, -414), 3.0, 0.05),
    "gudang (525,60)": ((525, 60), 6.0, 0.05),
    "rel (-550,0)": ((-550, 0), 12.0, 0.05),
    "rel_celah_jalan (-550,155)": ((-550, 155), 9.0, 0.05),
    "rel_celah_kali (-550,-105)": ((-550, -105), -1.5, 0.05),
}

if __name__ == "__main__":
    bad = 0
    for k, ((x, y), tgt, tol) in TITIK_UJI.items():
        z = elev(x, y)
        ok = abs(z - tgt) <= tol
        bad += not ok
        print(f"{'OK ' if ok else 'GAGAL'} {k:28s} z={z:7.2f}  target {tgt}±{tol}  slot {zona_material(x, y)}")
    # kemiringan maksimum yang bisa dijalani Aksa di luar tebing kali/tanggul rel (< 45°)
    curam = 0
    for x in range(-690, 691, 10):
        for y in range(-590, 391, 2):
            if KALI_Y[0] - 8 < y < BANTARAN_Y[0] + 2 or REL_X[0] - REL_KAKI - 2 < x < REL_X[1] + REL_KAKI + 2 \
                    or ANAK_KALI_X[0] - 6 < x < ANAK_KALI_X[1] + 6:
                continue
            if abs(elev(x, y + 2) - elev(x, y)) / 2 > 1.0:
                curam += 1
    print(f"{'OK ' if curam == 0 else 'GAGAL'} lereng > 45° di area jalan kaki: {curam}")
    bad += curam > 0
    print("SEMUA LULUS" if bad == 0 else "ADA YANG GAGAL")
