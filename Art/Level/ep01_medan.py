"""Fungsi ketinggian medan Ep01_LawangSapta (meter; X timur, Y utara, Z atas, 0 = muka desa).
Sumber: docs/30 bagian 2 (tata letak konsep 15 Okt 2026). Data objek: Art/Level/ep01_layout_v01.json.
Uji mandiri: python -I Art/Level/ep01_medan.py  (harus mencetak SEMUA LULUS)."""
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
    qx, qy = ax + dx * t, ay + dy * t
    return math.hypot(px - qx, py - qy), t


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


# --- profil selatan → utara di poros bukit (|x| kecil) ---
PROFIL_Y = [(-420, 0.0), (-270, 0.0), (-120, 3.0), (-60, 25.0), (60, 25.0), (87.5, 28.0), (112.5, 35.0), (225, 35.0)]

JALAN_AKSES = [(460, -50), (340, -32), (250, -28), (175, -22), (140, -20)]
JALAN_PROYEK = [(58, 150), (105, 128), (148, 70), (168, 10), (180, -24)]   # 35 m → 25 m

# ram di dalam galian (lebar 6 m), z linear dari awal ke akhir
RAM = [
    {"nama": "ram_timur", "dari": (72, -8, 25.0), "ke": (26, -3, 15.0), "lebar": 6.0},
    {"nama": "ram_utara", "dari": (0, 25, 15.0), "ke": (0, 62, 25.0), "lebar": 6.0},
]


def profil_y(y):
    for (y0, z0), (y1, z1) in zip(PROFIL_Y, PROFIL_Y[1:]):
        if y <= y1:
            return lerp(z0, z1, smoothstep(y0, y1, y)) if y >= y0 else z0
    return PROFIL_Y[-1][1]


def elev(x, y):
    # 1. bukit: profil utara-selatan dikali turunan lateral (barat lebih cepat turun, timur lebih landai)
    zs = profil_y(y)
    if x >= 0:
        lat = 1.0 - smoothstep(160, 280, x)
    else:
        lat = 1.0 - smoothstep(90, 220, -x)
    z = zs * lat

    # 2. punggung bukit jalan akses (+25 m) dari timur
    d, _ = dist_poly(x, y, JALAN_AKSES)
    if x > 120:
        z = max(z, 25.0 * (1.0 - smoothstep(4, 45, d)))

    # 3. hutan dan bukit lebih tinggi di utara (batas)
    if y > 225:
        z += min(45.0, (y - 225) * 0.9)

    # 4. sawah (selatan-tenggara) dan desa (barat daya): diratakan
    if -90 <= x <= 210 and -270 <= y <= -110:
        z = min(z, 3.0 * (y + 270) / 160.0)
    if -260 <= x <= -80 and -325 <= y <= -200:
        z = min(z, 0.0)

    # 5. jurang + kali di barat
    if x < -255:
        t = smoothstep(-255, -272, x)
        z = lerp(z, -12.0, t)
        if abs(x + 285) < 7:
            z = -14.0
        if x < -305:
            z = -12.0 + (-305 - x) * 1.2

    # 6. galian tapal kuda (pusat 0,0; elips 140 x 120; 4 undakan 2,5 m; dasar +15)
    e = math.hypot(x / 70.0, y / 60.0)
    if e < 1.0:
        if e < 0.45:
            zg = 15.0
        elif e < 0.63:
            zg = 17.5
        elif e < 0.81:
            zg = 20.0
        else:
            zg = 22.5
        z = zg
    # mulut galian terbuka ke selatan: koridor lebar 50 m, dasar +15 turun ke +4 di y = -110
    if abs(x) < 25 and -110 <= y <= -27:
        ramp = lerp(15.0, 4.0, (-27 - y) / 83.0)
        z = min(z, ramp) if e >= 1.0 else ramp

    # 7. ram di dalam galian
    for r in RAM:
        (ax, ay, az), (bx, by, bz), w = r["dari"], r["ke"], r["lebar"]
        d, t = dist_seg(x, y, ax, ay, bx, by)
        if d <= w / 2:
            z = lerp(az, bz, t)

    # 8. jalan proyek: koridor 8 m, 35 → 25 m
    d, s = dist_poly(x, y, JALAN_PROYEK)
    if d <= 4:
        z = lerp(35.0, 25.0, s)
    return z


TITIK_UJI = {   # (x, y): tinggi target ± toleransi
    "plato_tengah (0,170)": ((0, 170), 35.0, 0.5),
    "gerbang (0,125)": ((0, 125), 35.0, 0.5),
    "kaki_tangga (0,87.5)": ((0, 87.5), 28.0, 0.5),
    "bibir_utara (0,62)": ((0, 62), 25.0, 0.6),
    "dasar_galian (0,0)": ((0, 0), 15.0, 0.1),
    "undakan_1 (20,33)": ((20, 33), 17.5, 0.1),
    "START (140,-20)": ((140, -20), 25.0, 1.0),
    "batu_latihan (110,-60)": ((110, -60), 25.0, 2.0),
    "sawah_tengah (60,-190)": ((60, -190), 1.5, 0.6),
    "desa_tengah (-170,-260)": ((-170, -260), 0.0, 0.1),
    "kali (-285,0)": ((-285, 0), -14.0, 0.1),
    "mulut_galian (0,-80)": ((0, -80), 8.0, 0.3),
}

if __name__ == "__main__":
    bad = 0
    for k, ((x, y), tgt, tol) in TITIK_UJI.items():
        z = elev(x, y)
        ok = abs(z - tgt) <= tol
        bad += not ok
        print(f"{'OK ' if ok else 'GAGAL'} {k:28s} z={z:6.2f}  target {tgt}±{tol}")
    # jarak bibir galian -> rumah desa terdekat
    import itertools
    rim = [(70 * math.cos(a), 60 * math.sin(a)) for a in [i * math.pi / 180 for i in range(360)]]
    desa_pts = [(x, y) for x in range(-260, -79, 5) for y in range(-325, -199, 5)]
    dmin = min(math.hypot(a[0] - b[0], a[1] - b[1]) for a in rim for b in desa_pts)
    print(f"{'OK ' if dmin >= 150 else 'GAGAL'} jarak bibir galian -> tepi desa = {dmin:.1f} m (>= 150)")
    print("SEMUA LULUS" if bad == 0 and dmin >= 150 else "ADA YANG GAGAL")
