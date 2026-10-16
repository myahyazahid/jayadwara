"""Fungsi ketinggian medan Ep01_LawangSapta **v02** (meter; X timur, Y utara, Z atas, 0 = muka desa/sawah).
Sumber: docs/30 bagian 2a (v02, 16 Okt 2026): jarak antarzona ±1,7x v01, ukuran objek tetap ukuran asli, area baru
(desa sebagai titik mulai, base camp Adikara, area pilar tol, hutan + reruntuhan candi perwara).
Data objek: Art/Level/ep01_layout_v02.json. v01 (ep01_medan.py) disimpan sebagai arsip.
Uji mandiri: python -I Art/Level/ep01_medan_v02.py  (harus mencetak SEMUA LULUS)."""
import math


def smoothstep(a, b, v):
    if a == b:
        return 0.0 if v < a else 1.0
    t = max(0.0, min(1.0, (v - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def dist_seg(px, py, ax, ay, bx, by):
    """Jarak titik ke segmen + parameter t (0..1) di segmen."""
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t)), t


def dist_poly(px, py, pts):
    """Jarak ke polyline + posisi relatif (0..1) sepanjang polyline."""
    seglen = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    total = sum(seglen)
    best, best_s, acc = 1e9, 0.0, 0.0
    for (a, b), L in zip(zip(pts, pts[1:]), seglen):
        d, t = dist_seg(px, py, a[0], a[1], b[0], b[1])
        if d < best:
            best, best_s = d, (acc + t * L) / total
        acc += L
    return best, best_s


# ---------------- tata letak (meter) ----------------
BATAS_MEDAN = (-620, 780, -580, 640)           # x_min, x_max, y_min, y_max
GALIAN_RX, GALIAN_RY = 110.0, 95.0              # elips galian 220 x 190 m
UNDAKAN = [(0.45, 15.0), (0.63, 17.5), (0.81, 20.0), (1.00, 22.5)]   # batas e -> tinggi (dasar +15, 4 undakan 2,5 m)
MULUT = {"setengah_lebar": 40.0, "y_awal": -43.0, "y_akhir": -190.0, "z_awal": 15.0, "z_akhir": 4.0}

# profil selatan -> utara di poros bukit (|x| kecil)
PROFIL_Y = [(-580, 0.0), (-480, 0.0), (-200, 3.0), (-95, 25.0), (95, 25.0), (142, 28.0), (167, 35.0), (375, 35.0)]

PLATO = (-100, 100, 167, 375)                   # x0, x1, y0, y1  (+35 m)
SAWAH = (-150, 360, -480, -200)                 # +0 ... +3 m
DESA = (-430, -170, -490, -310)                 # 0 m
BASECAMP = (150, 330, -60, 120)                 # +25 m (diratakan)
JURANG_X = (-470, -488)                         # tepi atas -> dasar jurang
KALI_X, KALI_SETENGAH = -505.0, 7.0

JALAN_AKSES = [(780, -60), (600, -40), (460, -30), (330, -20)]          # punggung bukit +25, dari kota
JALAN_PROYEK = [(95, 250), (170, 230), (230, 170), (250, 120)]          # plato 35 -> base camp 25
JALAN_DESA = [(780, -545), (400, -525), (100, -515), (-150, -470), (-175, -430)]   # dari tenggara ke desa (z ikut medan)
JALAN_SETAPAK = [(-170, -330), (-200, -260), (-190, -180), (-150, -110), (-112, -45)]  # desa -> bibir galian barat

RAM = [   # ram di dalam galian (lebar 6 m), z linear
    {"nama": "ram_barat", "dari": (-112, -8, 25.0), "ke": (-50, -3, 15.0), "lebar": 6.0},
    {"nama": "ram_timur", "dari": (112, -8, 25.0), "ke": (50, -3, 15.0), "lebar": 6.0},
    {"nama": "ram_utara", "dari": (0, 42, 15.0), "ke": (0, 98, 25.0), "lebar": 6.0},
]


def profil_y(y):
    for (y0, z0), (y1, z1) in zip(PROFIL_Y, PROFIL_Y[1:]):
        if y <= y1:
            return lerp(z0, z1, smoothstep(y0, y1, y)) if y >= y0 else z0
    return PROFIL_Y[-1][1]


def galian_e(x, y):
    return math.hypot(x / GALIAN_RX, y / GALIAN_RY)


def di_kotak(x, y, k):
    return k[0] <= x <= k[1] and k[2] <= y <= k[3]


def elev(x, y):
    # 1. bukit: profil utara-selatan x turunan lateral (barat turun lebih cepat ke desa, timur landai ke base camp)
    zs = profil_y(y)
    lat = 1.0 - (smoothstep(330, 520, x) if x >= 0 else smoothstep(170, 420, -x))
    z = zs * lat

    # 2. hutan + bukit di utara plato (landai sampai y 520, lalu curam)
    if y > 375:
        z += min(80.0, (min(y, 520) - 375) * 0.12 + max(0.0, y - 520) * 0.9)

    # 3. punggung bukit jalan akses (+25 m) dari timur
    d, _ = dist_poly(x, y, JALAN_AKSES)
    if x > 300:
        z = max(z, 25.0 * (1.0 - smoothstep(6, 70, d)))

    # 4. base camp Adikara diratakan +25
    if di_kotak(x, y, BASECAMP):
        z = 25.0

    # 5. sawah (0..3) dan desa (0) diratakan
    if di_kotak(x, y, SAWAH):
        z = min(z, 3.0 * (y - SAWAH[2]) / (SAWAH[3] - SAWAH[2]))
    if di_kotak(x, y, DESA):
        z = min(z, 0.0)

    # 6. jurang + kali di barat; tebing seberang naik ke tepi medan
    if x < JURANG_X[0]:
        z = lerp(z, -12.0, smoothstep(JURANG_X[0], JURANG_X[1], x))
        if abs(x - KALI_X) < KALI_SETENGAH:
            z = -14.0
        if x < -525:
            z = -12.0 + (-525 - x) * 0.6

    # 7. galian tapal kuda
    e = galian_e(x, y)
    if e < 1.0:
        for batas, zg in UNDAKAN:
            if e < batas:
                z = zg
                break
    m = MULUT
    if abs(x) < m["setengah_lebar"] and m["y_akhir"] <= y <= m["y_awal"]:
        ramp = lerp(m["z_awal"], m["z_akhir"], (m["y_awal"] - y) / (m["y_awal"] - m["y_akhir"]))
        z = min(z, ramp) if e >= 1.0 else ramp

    # 8. ram di dalam galian
    for r in RAM:
        (ax, ay, az), (bx, by, bz), w = r["dari"], r["ke"], r["lebar"]
        d, t = dist_seg(x, y, ax, ay, bx, by)
        if d <= w / 2:
            z = lerp(az, bz, t)

    # 9. jalan proyek: koridor 8 m, 35 -> 25 m
    d, s = dist_poly(x, y, JALAN_PROYEK)
    if d <= 4:
        z = lerp(35.0, 25.0, s)
    return z


def zona_material(x, y, z=None):
    """Slot material medan (urutan = prioritas). Dipakai skrip Blender M2."""
    if z is None:
        z = elev(x, y)
    if z < -13:
        return "Air"
    if galian_e(x, y) < 1.0 or (abs(x) < MULUT["setengah_lebar"] and MULUT["y_akhir"] <= y <= MULUT["y_awal"]):
        return "Galian"
    for poly, lebar in ((JALAN_AKSES, 4), (JALAN_PROYEK, 4), (JALAN_DESA, 3), (JALAN_SETAPAK, 1.5)):
        if dist_poly(x, y, poly)[0] <= lebar:
            return "Jalan"
    if di_kotak(x, y, PLATO):
        return "Plato"
    if di_kotak(x, y, BASECAMP):
        return "Jalan"
    if di_kotak(x, y, SAWAH):
        return "Sawah"
    if di_kotak(x, y, DESA):
        return "Desa"
    return "Hutan"


TITIK_UJI = {   # (x, y): tinggi target ± toleransi
    "plato_tengah (0,270)": ((0, 270), 35.0, 0.5),
    "gerbang (0,180)": ((0, 180), 35.0, 0.5),
    "kaki_tangga (0,142)": ((0, 142), 28.0, 0.5),
    "bibir_utara (0,100)": ((0, 100), 25.0, 0.6),
    "dasar_galian (0,0)": ((0, 0), 15.0, 0.1),
    "undakan_1 (30,50)": ((30, 50), 17.5, 0.1),
    "bibir_barat (-115,-20)": ((-115, -20), 25.0, 0.6),
    "basecamp (240,30)": ((240, 30), 25.0, 0.1),
    "jalan_akses (600,-40)": ((600, -40), 25.0, 0.5),
    "sawah_tengah (100,-340)": ((100, -340), 1.5, 0.6),
    "desa_tengah (-300,-400)": ((-300, -400), 0.0, 0.1),
    "kali (-505,0)": ((-505, 0), -14.0, 0.1),
    "mulut_galian (0,-120)": ((0, -120), 9.8, 0.6),
    "pilar_tol (600,200)": ((600, 200), 0.0, 1.0),
}

if __name__ == "__main__":
    bad = 0
    for k, ((x, y), tgt, tol) in TITIK_UJI.items():
        z = elev(x, y)
        ok = abs(z - tgt) <= tol
        bad += not ok
        print(f"{'OK ' if ok else 'GAGAL'} {k:26s} z={z:7.2f}  target {tgt}±{tol}")
    rim = [(GALIAN_RX * math.cos(math.radians(a)), GALIAN_RY * math.sin(math.radians(a))) for a in range(360)]
    desa_pts = [(x, y) for x in range(DESA[0], DESA[1] + 1, 5) for y in range(DESA[2], DESA[3] + 1, 5)]
    dmin = min(math.hypot(a[0] - b[0], a[1] - b[1]) for a in rim for b in desa_pts)
    ok_d = dmin >= 250
    print(f"{'OK ' if ok_d else 'GAGAL'} jarak bibir galian -> tepi desa = {dmin:.1f} m (>= 250)")
    print("SEMUA LULUS" if bad == 0 and ok_d else "ADA YANG GAGAL")
