"""Skeleton Jayadwara2 (docs/25 R4): nama & hierarki SAMA dengan jd_skeleton.py (89 tulang), posisi sendi diukur dari mesh Tripo
`jayadwara2_v01_tripo.blend` (landmark diperiksa lewat overlay pada render ortografis, R1).

Beda dengan model lama: pose rest = berdiri santai (lengan turun, bukan A-pose 30°), kaki selebar bahu, tangan terkepal kaku.
Koordinat: 1 unit = 1 m, menghadap -Y, kiri karakter = +X (`_l`). Tinggi 1,99 m dengan tanduk (helm 1,90).
"""
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from jd_skeleton import FINGER_LAT, FINGER_SC, FINGERS, IK_BONES, SKIN_BONES, SIDES  # noqa: E402,F401

# ------------------------------------------------------------------ landmark sisi kiri (+X); sisi kanan dicerminkan
LM = {
    "clav_head": (0.03, -0.01, 1.50),
    "shoulder": (0.235, -0.03, 1.55),
    "elbow": (0.285, -0.07, 1.29),
    "wrist": (0.325, -0.09, 1.03),
    "hand_end": (0.335, -0.10, 0.90),
    "hip": (0.10, 0.0, 0.98),
    "knee": (0.19, -0.04, 0.63),
    "ankle": (0.25, 0.03, 0.14),
    "ball": (0.30, -0.12, 0.06),
    "toe": (0.31, -0.24, 0.04),
    "scarf_start": (0.33, -0.09, 1.10),            # sayap sisi = selendang (K5): lembar menggantung hampir vertikal
    "scarf_end": (0.37, -0.10, 0.42),
}
SPINE_Z = [0.99, 1.09, 1.19, 1.29, 1.39, 1.50]
NECK_Z = [1.50, 1.58, 1.64]
CROWN_Z = 1.90
CLOTH_FRONT_Z, CLOTH_BACK_Z = [1.10, 0.88, 0.66, 0.44], [1.10, 0.87, 0.64, 0.42]
CLOTH_FRONT_Y, CLOTH_BACK_Y = -0.218, 0.11       # kain depan = lembar vertikal y≈-0,218 (diukur); belakang tidak ada panel di mesh
CLOTH_FRONT_DY, CLOTH_BACK_DY = 0.0, +0.02
SCARF_N = 6
HAND_SCALE = 0.95


def P(name, s):
    x, y, z = LM[name]
    return Vector((s * x, y, z))


def scarf_points(s):
    a, b = P("scarf_start", s), P("scarf_end", s)
    pts = []
    for i in range(SCARF_N + 1):
        t = i / SCARF_N
        p = a.lerp(b, t)
        p.x = s * (abs(a.x) + (abs(b.x) - abs(a.x)) * t)
        pts.append(p)
    return pts


def cloth_points(z_list, y, dy):
    return [Vector((0.0, y + dy * i, z)) for i, z in enumerate(z_list)]


def hand_frame(sd):
    s = SIDES[sd]
    wrist, end = P("wrist", s), P("hand_end", s)
    d = (end - wrist).normalized()
    front = Vector((0, -1, 0))
    front = (front - front.project(d)).normalized()
    inw = Vector((-s, 0, 0))
    inw = (inw - inw.project(d) - inw.project(front)).normalized()
    return d, front, inw, wrist + d * 0.012


def finger_joints(sd, name):
    d, front, inw, base = hand_frame(sd)

    def pt(lf, iw, fw):
        k = HAND_SCALE
        return base + front * (lf * k) + inw * (iw * k) + d * (fw * k)

    if name == "thumb":
        return [pt(0.052, 0.0, 0.034), pt(0.058, 0.014, 0.068), pt(0.050, 0.036, 0.090), pt(0.034, 0.052, 0.090)]
    lf, sc = FINGER_LAT[name], FINGER_SC[name]
    return [pt(lf, 0.0, 0.092), pt(lf, 0.016, 0.128 * sc), pt(lf, 0.046, 0.140 * sc), pt(lf, 0.062, 0.104 * sc)]


def build_bones():
    """Urutan induk-dulu: (nama, induk, head, tail, connect). Struktur identik dengan jd_skeleton.build_bones()."""
    B = []

    def add(name, parent, head, tail, connect=False):
        B.append((name, parent, Vector(head), Vector(tail), connect))

    add("root", None, (0, 0, 0), (0, 0, 0.15))
    add("pelvis", "root", (0, 0, 0.93), (0, 0, SPINE_Z[0]))
    prev = "pelvis"
    for i in range(5):
        n = f"spine_{i + 1:02d}"
        add(n, prev, (0, 0, SPINE_Z[i]), (0, 0, SPINE_Z[i + 1]), connect=True)
        prev = n
    add("neck_01", "spine_05", (0, 0, NECK_Z[0]), (0, 0, NECK_Z[1]), True)
    add("neck_02", "neck_01", (0, 0, NECK_Z[1]), (0, 0, NECK_Z[2]), True)
    add("head", "neck_02", (0, 0, NECK_Z[2]), (0, 0, CROWN_Z), True)

    for sd, s in SIDES.items():
        shoulder, elbow, wrist, hend = P("shoulder", s), P("elbow", s), P("wrist", s), P("hand_end", s)
        add(f"clavicle_{sd}", "spine_05", P("clav_head", s), shoulder)
        add(f"upperarm_{sd}", f"clavicle_{sd}", shoulder, elbow, True)
        add(f"lowerarm_{sd}", f"upperarm_{sd}", elbow, wrist, True)
        add(f"hand_{sd}", f"lowerarm_{sd}", wrist, hend, True)
        add(f"upperarm_twist_01_{sd}", f"upperarm_{sd}", shoulder.lerp(elbow, 0.5), elbow, True)
        add(f"lowerarm_twist_01_{sd}", f"lowerarm_{sd}", elbow.lerp(wrist, 0.5), wrist, True)
        for fn in FINGERS:
            J = finger_joints(sd, fn)
            prev = f"hand_{sd}"
            for i in range(3):
                n = f"{fn}_{i + 1:02d}_{sd}"
                add(n, prev, J[i], J[i + 1], connect=False)
                prev = n

        hip, knee, ankle, ball, toe = (P(k, s) for k in ("hip", "knee", "ankle", "ball", "toe"))
        add(f"thigh_{sd}", "pelvis", hip, knee)
        add(f"calf_{sd}", f"thigh_{sd}", knee, ankle, True)
        add(f"thigh_twist_01_{sd}", f"thigh_{sd}", hip.lerp(knee, 0.5), knee, True)
        add(f"calf_twist_01_{sd}", f"calf_{sd}", knee.lerp(ankle, 0.5), ankle, True)
        add(f"foot_{sd}", f"calf_{sd}", ankle, ball, True)
        add(f"ball_{sd}", f"foot_{sd}", ball, toe, True)

        pts = scarf_points(s)
        prev = "pelvis"
        for i in range(SCARF_N):
            n = f"scarf_{sd}_{i + 1:02d}"
            add(n, prev, pts[i], pts[i + 1], connect=(i > 0))
            prev = n

    for chain, zs, y, dy in (("cloth_front", CLOTH_FRONT_Z, CLOTH_FRONT_Y, CLOTH_FRONT_DY),
                             ("cloth_back", CLOTH_BACK_Z, CLOTH_BACK_Y, CLOTH_BACK_DY)):
        pts = cloth_points(zs, y, dy)
        prev = "pelvis"
        for i in range(len(pts) - 1):
            n = f"{chain}_{i + 1:02d}"
            add(n, prev, pts[i], pts[i + 1], connect=(i > 0))
            prev = n

    add("ik_foot_root", "root", (0, 0, 0), (0, 0, 0.10))
    add("ik_hand_root", "root", (0, 0, 0), (0, 0, 0.10))
    seg_ = {n: (h, t) for n, _p, h, t, _c in B}
    for sd in SIDES:
        a = seg_[f"foot_{sd}"][0]
        add(f"ik_foot_{sd}", "ik_foot_root", a, a + Vector((0, -0.10, 0)))
    hr = seg_["hand_r"][0]
    add("ik_hand_gun", "ik_hand_root", hr, hr + Vector((0, 0, -0.08)))
    for sd in SIDES:
        h = seg_[f"hand_{sd}"][0]
        add(f"ik_hand_{sd}", "ik_hand_gun", h, h + Vector((0, 0, -0.08)))
    return B


def bone_segments():
    return {n: (h, t) for n, _p, h, t, _c in build_bones()}


def chain_bones(chain):
    return [n for n, *_ in build_bones() if n.startswith(chain + "_") and n[len(chain) + 1:].isdigit()]


def build_sockets():
    seg = bone_segments()
    S = {}
    for sd in SIDES:
        h, t = seg[f"hand_{sd}"]
        S[f"SOCKET_hand_{sd}"] = (f"hand_{sd}", h.lerp(t, 0.8) + (t - h).normalized() * 0.03)
        S[f"SOCKET_foot_{sd}"] = (f"foot_{sd}", seg[f"foot_{sd}"][1])
    S["SOCKET_chest_sun"] = ("spine_05", Vector((0, -0.20, 1.445)))
    S["SOCKET_eye_l"] = ("head", Vector((+0.04, -0.14, 1.75)))
    S["SOCKET_eye_r"] = ("head", Vector((-0.04, -0.14, 1.75)))
    S["SOCKET_head_top"] = ("head", Vector((0, 0, CROWN_Z)))
    S["SOCKET_back_center"] = ("spine_04", Vector((0, 0.13, 1.45)))
    return S
