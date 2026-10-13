"""Aksa Iterasi 2 — pembangun kepala: loft cincin (profil terukur dari ak_head_*.png) + fitur wajah analitik.

Koordinat dunia Blender (m), kepala menghadap -Y, kiri karakter = +X, z absolut (dagu 1,574; ujung rambut 1,806).
Semua angka di KEYS/FEATURES diukur dari Art/Reference/ak_head_front.png dan ak_head_side.png (1 px = 0,78 mm; chin y=308 px = z 1,574)
dan dikali K=1,032 bila perlu (lihat docs/21). Dipakai oleh aksa_20_head.py. Ubah angka di sini lalu jalankan ulang aksa_20_head.py
untuk iterasi feedback wajah.
"""
import math

import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

Z_BOT, Z_TOP = 1.572, 1.772
LEVELS = 104
FRONT_PTS, BACK_PTS = 60, 28
FRONT_HALF = math.radians(76)

# (z, w setengah lebar, y_depan, y_belakang, p_depan)  — profil tengkorak + wajah, tanpa fitur
KEYS = [
    (1.572, 0.012, -0.058, 0.040, 2.2), (1.580, 0.018, -0.078, 0.046, 2.2), (1.590, 0.027, -0.085, 0.052, 2.2),
    (1.600, 0.035, -0.087, 0.057, 2.3), (1.613, 0.0465, -0.089, 0.062, 2.4), (1.630, 0.0515, -0.087, 0.066, 2.5),
    (1.650, 0.0540, -0.085, 0.070, 2.5), (1.668, 0.0550, -0.082, 0.073, 2.5), (1.682, 0.0556, -0.092, 0.075, 2.4),
    (1.700, 0.0560, -0.096, 0.076, 2.3), (1.720, 0.0560, -0.094, 0.074, 2.2), (1.740, 0.0535, -0.086, 0.068, 2.1),
    (1.756, 0.0470, -0.068, 0.056, 2.0), (1.766, 0.0330, -0.042, 0.038, 2.0), (1.772, 0.0000, 0.0, 0.0, 2.0),
]

EYE_X, EYE_Z = 0.0315, 1.668
EYE_R = 0.0118                      # jari-jari bola mata
EYE_CENTER_Y = -0.0592


def _interp(zs, vals, z):
    """Hermite kubik dengan kemiringan beda-terpusat (Catmull-Rom tak seragam): mulus tanpa plateau di tiap kunci."""
    n = len(zs)
    if z <= zs[0]:
        return vals[0]
    if z >= zs[-1]:
        return vals[-1]
    for i in range(n - 1):
        if zs[i] <= z <= zs[i + 1]:
            break
    h = zs[i + 1] - zs[i]

    def slope(j):
        a, b = max(j - 1, 0), min(j + 1, n - 1)
        return (vals[b] - vals[a]) / (zs[b] - zs[a])

    t = (z - zs[i]) / h
    t2, t3 = t * t, t * t * t
    return ((2 * t3 - 3 * t2 + 1) * vals[i] + (t3 - 2 * t2 + t) * h * slope(i)
            + (-2 * t3 + 3 * t2) * vals[i + 1] + (t3 - t2) * h * slope(i + 1))


def profile(z):
    zs = [k[0] for k in KEYS]
    return tuple(_interp(zs, [k[j] for k in KEYS], z) for j in range(1, 5))


def sgn(x):
    return 1.0 if x >= 0 else -1.0


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def gauss(x, z, cx, cz, sx, sz):
    return math.exp(-(((x - cx) / sx) ** 2 + ((z - cz) / sz) ** 2))


def level_positions():
    """z tiap cincin: rapat di zona mata/hidung/mulut supaya bukaan mata dan bibir cukup tajam."""
    N = 4000
    zs = [Z_BOT + (Z_TOP - Z_BOT) * i / (N - 1) for i in range(N)]
    dens = [1.0 + 2.6 * gauss(0, z, 0, 1.668, 1, 0.011) + 1.5 * gauss(0, z, 0, 1.611, 1, 0.014)
            + 1.2 * gauss(0, z, 0, 1.632, 1, 0.010) + 0.8 * gauss(0, z, 0, 1.687, 1, 0.008) for z in zs]
    cum = [0.0]
    for d in dens[1:]:
        cum.append(cum[-1] + d)
    out = []
    j = 0
    for i in range(LEVELS):
        target = cum[-1] * i / (LEVELS - 1)
        while j < N - 1 and cum[j] < target:
            j += 1
        out.append(zs[j])
    out[0], out[-1] = Z_BOT, Z_TOP
    return out


def ring_angles():
    """Sudut t (0 = depan, + = ke sisi +X): rapat di depan (muka), jarang di belakang."""
    a, b = -FRONT_HALF, FRONT_HALF
    front = [a + (i + 0.5) * (b - a) / FRONT_PTS for i in range(FRONT_PTS)]
    rest = 2 * math.pi - (b - a)
    back = [b + (i + 0.5) * rest / BACK_PTS for i in range(BACK_PTS)]
    return front + back


# ---------------------------------------------------------------- fitur wajah (perpindahan sepanjang normal, m)
def eye_open(x, z):
    """Nilai elips almond mata (<1 = di dalam bukaan); sudut luar sedikit lebih tinggi (slant)."""
    ex = abs(x) - EYE_X
    slant = 0.10 * ex
    return (ex / 0.0168) ** 2 + ((z - EYE_Z - slant) / 0.0056) ** 2


def feature(x, y, z):
    """Perpindahan wajah depan (sepanjang normal); hanya bermakna untuk titik di muka."""
    ax = abs(x)
    d = 0.0
    # --- soket mata + bukaan + tepi kelopak
    e = eye_open(x, z)
    d += -0.0055 * gauss(ax, z, EYE_X, EYE_Z, 0.030, 0.020)                      # soket lebar
    d += -0.0115 * (1.0 - smooth(0.70, 1.0, e))                                  # bukaan: bola mata terlihat di dalamnya
    d += 0.0028 * math.exp(-((e - 1.30) / 0.30) ** 2)                            # tepi kelopak
    d += 0.0035 * gauss(ax, z, 0.034, EYE_Z + 0.0215, 0.027, 0.0075)             # kelopak atas / punggung alis
    # --- alis menonjol
    d += 0.0060 * gauss(ax, z, 0.034, 1.686, 0.030, 0.0065)
    d += 0.0035 * gauss(ax, z, 0.008, 1.683, 0.010, 0.010)                       # glabella
    # --- hidung (jembatan, ujung, sayap)
    zs = [1.680, 1.662, 1.648, 1.636, 1.629, 1.622]
    amp = [0.000, 0.0070, 0.0128, 0.0200, 0.0210, 0.0150]
    wid = [0.0075, 0.0080, 0.0098, 0.0130, 0.0150, 0.0190]
    a_ = _interp(list(reversed(zs)), list(reversed(amp)), z)
    w_ = _interp(list(reversed(zs)), list(reversed(wid)), z)
    if 1.616 < z < 1.683:
        d += a_ * math.exp(-(ax / w_) ** 2)
    d += 0.0105 * gauss(ax, z, 0.0185, 1.6228, 0.0072, 0.0060)                    # sayap hidung
    d += -0.0045 * gauss(ax, z, 0.0075, 1.6178, 0.0035, 0.0028)                   # lubang hidung
    d += -0.0022 * gauss(ax, z, 0.0, 1.6135, 0.0045, 0.0045)                      # filtrum
    # --- bibir + garis mulut + dagu
    d += 0.0058 * gauss(ax, z, 0.0, 1.6152, 0.0170, 0.0042)                       # bibir atas
    d += 0.0068 * gauss(ax, z, 0.0, 1.6038, 0.0160, 0.0048)                       # bibir bawah
    d += -0.0050 * gauss(ax, z, 0.0, 1.6098, 0.0200, 0.0012)                      # garis mulut
    d += -0.0030 * gauss(ax, z, 0.0205, 1.6100, 0.0035, 0.0045)                   # sudut mulut
    d += -0.0032 * gauss(ax, z, 0.0, 1.5965, 0.0140, 0.0030)                      # alur dagu
    d += 0.0030 * gauss(ax, z, 0.0, 1.5850, 0.0140, 0.0080)                       # dagu
    # --- tulang pipi, lekuk pipi, pelipis
    d += 0.0040 * gauss(ax, z, 0.043, 1.648, 0.014, 0.012)
    d += -0.0030 * gauss(ax, z, 0.037, 1.620, 0.013, 0.012)
    d += -0.0020 * gauss(ax, z, 0.054, 1.695, 0.008, 0.016)
    return d


def build_head(bm):
    """Loft cincin kepala -> bm (kulit, tutup bawah & atas). Mengembalikan daftar cincin (vertex)."""
    ts = ring_angles()
    n = len(ts)
    rings = []
    for z in level_positions():
        w, yf, yb, p = profile(z)
        ym = (yf + yb) / 2
        ring = []
        for t in ts:
            s, c = math.sin(t), math.cos(t)
            x = w * sgn(s) * abs(s) ** (2 / p)
            if c >= 0:
                y = ym - (ym - yf) * (c ** (2 / p))
            else:
                y = ym + (yb - ym) * (abs(c) ** (2.0 / 2.0))
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.normal_update()
    # fitur: sepanjang normal, hanya di bagian muka
    for ring in rings[1:-1]:
        for v in ring:
            w, yf, yb, p = profile(v.co.z)
            ym = (yf + yb) / 2
            if v.co.y < ym and abs(v.co.x) < 0.062:
                v.co = v.co + v.normal * feature(v.co.x, v.co.y, v.co.z)
    bm.normal_update()
    return rings


def laplacian(bm, iters=1, factor=0.35, region=None):
    for _ in range(iters):
        new = {}
        for v in bm.verts:
            if region is not None and not region(v):
                continue
            nb = [e.other_vert(v).co for e in v.link_edges]
            if nb:
                avg = sum(nb, Vector()) / len(nb)
                new[v] = v.co.lerp(avg, factor)
        for v, co in new.items():
            v.co = co


def make_bvh(mesh):
    """BVH dari data mesh (salinan koordinat; aman setelah bmesh dibebaskan)."""
    return BVHTree.FromPolygons([tuple(v.co) for v in mesh.vertices], [tuple(p.vertices) for p in mesh.polygons])


def surface_point(bvh, x, z, y_from=-0.3, off=0.0):
    """Titik di permukaan kepala pada (x, z) dilihat dari depan (+Y arah tembak); geser `off` sepanjang normal."""
    hit = bvh.ray_cast(Vector((x, y_from, z)), Vector((0, 1, 0)))
    if hit[0] is None:
        return None, None
    return hit[0] + hit[1] * off, hit[1]
