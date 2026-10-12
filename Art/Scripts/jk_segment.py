"""Segmentasi mesh Tripo Jerangkong menjadi tulang/potongan (numpy saja; dipakai jerangkong_11_pieces.py di Blender
dan bisa diuji di luar Blender).

label_faces(V, F, bones) -> array nama tulang per segitiga.
Langkah: (1) kapsul terdekat (jarak ke segmen tulang - jari-jari), (2) aturan wilayah (tengkorak/rahang, rusuk, kain),
(3) potongan bidang di sendi supaya batas potongan lurus, (4) penghalusan mayoritas tetangga untuk bintik kecil.
Semua angka dalam meter, ruang model (rest), karakter menghadap -Y, kiri = +X.
"""
import numpy as np

# kapsul label: tulang -> list (a, b, r) dalam koordinat model; None = pakai segmen tulang itu sendiri
R_LIMB = {"upperarm": 0.065, "lowerarm": 0.075, "thigh": 0.075, "calf": 0.075}


def _seg_dist(P, a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-12), 0.0, 1.0)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def capsules(bones):
    B = {n: (np.asarray(h, float), np.asarray(t, float)) for n, (h, t) in bones.items()}
    C = {}
    for sd, s in (("l", 1.0), ("r", -1.0)):
        for b, r in R_LIMB.items():
            h, t = B[f"{b}_{sd}"]
            C[f"{b}_{sd}"] = [(h, t, r)]
        w, k = B[f"hand_{sd}"]
        tip = B[f"middle_03_{sd}"][1]
        C[f"hand_{sd}"] = [(w, k, 0.07), (k, tip, 0.08)]
        a, ball = B[f"foot_{sd}"]
        toe = B[f"ball_{sd}"][1]
        C[f"foot_{sd}"] = [(a, ball, 0.10), (ball, toe, 0.10), (a + np.array([0, 0.14, -0.12]), a, 0.10)]
        c0, c1 = B[f"clavicle_{sd}"]
        C[f"clavicle_{sd}"] = [(c0 + np.array([s * 0.06, 0, 0]), c1, 0.04),                     # selangka
                               (np.array([s * 0.15, 0.13, 1.86]), np.array([s * 0.16, 0.12, 1.62]), 0.07)]  # belikat
    for n in ("spine_01", "spine_02", "neck_01", "neck_02"):
        h, t = B[n]
        C[n] = [(h, t, 0.05)]
    C["head"] = [(B["head"][0], B["head"][1], 0.06), (np.array([0, -0.235, 2.04]),) * 2 + (0.14,)]
    C["jaw"] = [(B["jaw"][0] + np.array([0.07, 0, 0]), B["jaw"][1], 0.035),
                (B["jaw"][0] + np.array([-0.07, 0, 0]), B["jaw"][1], 0.035)]
    C["pelvis"] = [(np.array([-0.17, 0.0, 1.31]), np.array([0.17, 0.0, 1.31]), 0.10),
                   (np.array([0, 0.06, 1.38]), np.array([0, 0.09, 1.22]), 0.08)]
    C["spine_04"] = [(B["spine_03"][0], B["spine_05"][1], 0.05)]                                # badan rusuk: lihat aturan
    return C


def joint_cuts(bones):
    """(induk, anak, titik sendi, normal ke arah anak, radius pengaruh)"""
    B = {n: (np.asarray(h, float), np.asarray(t, float)) for n, (h, t) in bones.items()}
    cuts = []

    def nrm(v):
        return v / np.linalg.norm(v)

    for sd in ("l", "r"):
        for par, ch, r in (("upperarm", "lowerarm", 0.13), ("lowerarm", "hand", 0.13), ("thigh", "calf", 0.14),
                           ("calf", "foot", 0.14)):
            p, c = B[f"{par}_{sd}"], B[f"{ch}_{sd}"]
            n = nrm(nrm(p[1] - p[0]) + nrm(c[1] - c[0])) if ch != "foot" else nrm(p[1] - p[0])
            cuts.append((f"{par}_{sd}", f"{ch}_{sd}", c[0], n, r))
    return cuts


def label_faces(V, F, bones, iters=3):
    V = np.asarray(V, float)
    F = np.asarray(F)
    P = V[F].mean(axis=1)
    C = capsules(bones)
    names = list(C)
    D = np.full((len(P), len(names)), np.inf)
    for j, n in enumerate(names):
        for a, b, r in C[n]:
            D[:, j] = np.minimum(D[:, j], _seg_dist(P, a, b) - r)
    lab = np.array(names, dtype=object)[np.argmin(D, axis=1)]
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    ax = np.abs(x)

    # rusuk: kotak toraks di luar lengan; menimpa tulang belakang & kapsul lain
    arm_d = np.minimum.reduce([_seg_dist(P, bones[f"upperarm_{s}"][0], bones[f"upperarm_{s}"][1]) for s in "lr"])
    ribs = (z > 1.50) & (z < 1.88) & (ax < 0.31) & (y < 0.20) & (y > -0.27) & (arm_d > 0.07)
    # selangka hanya di atas (z > 1,80) atau belikat di punggung (y > 0,05); sisanya rusuk
    keep = np.isin(lab, ["clavicle_l", "clavicle_r"]) & ((z > 1.80) | (y > 0.05))
    lab[ribs & ~keep] = "spine_04"
    # kapsul tengkorak/rahang hanya berlaku di dalam bola tengkorak (diatur di bawah)
    lab[np.isin(lab, ["head", "jaw"])] = "neck_02"
    # tulang belakang toraks di belakang rusuk ikut rusuk (bukan poros)
    lab[(lab == "spine_02") & (z > 1.52)] = "spine_04"

    # tengkorak vs rahang vs leher
    sk = np.linalg.norm(P - np.array([0, -0.235, 2.04]), axis=1)
    skull = (sk < 0.175) & (ax < 0.16) & (z > 1.83)
    lab[skull] = "head"
    j0, j1 = np.asarray(bones["jaw"][0]), np.asarray(bones["jaw"][1])
    # garis gigi: bidang miring dari engsel ke dagu, sedikit di atas segmen rahang
    jaw_line = j0[2] + (y - j0[1]) * ((j1[2] - j0[2]) / (j1[1] - j0[1])) + 0.03
    jaw = skull & (z < jaw_line) & (y < j0[1] + 0.03) & (z < 1.97)
    lab[jaw] = "jaw"

    # kain: lembaran tipis di depan/belakang panggul-paha, diukur dari kapsul paha
    thigh_d = np.minimum.reduce([_seg_dist(P, bones[f"thigh_{s}"][0], bones[f"thigh_{s}"][1]) for s in "lr"])
    calf_d = np.minimum.reduce([_seg_dist(P, bones[f"calf_{s}"][0], bones[f"calf_{s}"][1]) for s in "lr"])
    hand_d = np.minimum.reduce([_seg_dist(P, bones[f"hand_{s}"][0], bones[f"middle_03_{s}"][1]) for s in "lr"])
    cloth_zone = (z > 0.50) & (z < 1.40) & (ax < 0.26) & (thigh_d > 0.085) & (calf_d > 0.08) & (hand_d > 0.12)
    cloth_zone &= ~np.isin(lab, ["pelvis"]) | (z < 1.24)
    front = y < 0.0
    lab[cloth_zone & front] = "cloth_front"
    lab[cloth_zone & ~front] = "cloth_back"

    # potongan bidang di sendi
    for par, ch, j, n, r in joint_cuts(bones):
        m = np.isin(lab, [par, ch]) & (np.linalg.norm(P - j, axis=1) < r)
        side = (P[m] - j) @ n > 0
        lab[np.where(m)[0][side]] = ch
        lab[np.where(m)[0][~side]] = par

    lab = _smooth(F, lab, iters)
    return lab


def _smooth(F, lab, iters):
    """Mayoritas tetangga (berbagi vertex) untuk segitiga yang hampir dikepung label lain."""
    nf = len(F)
    nv = F.max() + 1
    vf = [[] for _ in range(nv)]
    for i, f in enumerate(F):
        for v in f:
            vf[v].append(i)
    nb = [set() for _ in range(nf)]
    for fl in vf:
        for i in fl:
            nb[i].update(fl)
    for _ in range(iters):
        new = lab.copy()
        for i in range(nf):
            ls = [lab[j] for j in nb[i] if j != i]
            if not ls:
                continue
            vals, cnt = np.unique(np.array(ls, dtype=object), return_counts=True)
            k = int(np.argmax(cnt))
            if vals[k] != lab[i] and cnt[k] >= 0.7 * len(ls):
                new[i] = vals[k]
        lab = new
    return lab

