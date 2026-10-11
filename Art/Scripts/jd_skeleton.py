"""Spesifikasi skeleton Jayadwara (Iterasi 1): posisi sendi, tulang bergaya UE5 Mannequin, socket.

Satu sumber data untuk blockout (bentuk) dan rig (armature). Nama tulang: docs/13 bagian 6.1.
Pose rest = A-pose, lengan 30° dari tubuh (docs/14 K8, disesuaikan dari 35°).
Karakter menghadap -Y; kiri karakter = +X (`_l`).
"""
import math

from mathutils import Vector

SIDES = {"l": +1, "r": -1}
ARM_ANGLE = math.radians(30)
UPPERARM_LEN, LOWERARM_LEN, HAND_LEN = 0.32, 0.27, 0.09     # K7: lengan +10% dari konsep

SPINE_Z = [0.99, 1.09, 1.19, 1.29, 1.39, 1.50]               # spine_01..05
NECK_Z = [1.50, 1.58, 1.64]
CROWN_Z = 1.90

CLOTH_FRONT_Z = [1.10, 0.88, 0.66, 0.44]                     # 3 tulang (revisi: lebih panjang seperti konsep)
CLOTH_BACK_Z = [1.10, 0.87, 0.64, 0.42]
HAND_SCALE = 1.30                                             # revisi: sarung tangan konsep besar
CLOTH_FRONT_Y, CLOTH_BACK_Y = -0.118, 0.112      # revisi: menempel ke sabuk pas-badan
CLOTH_FRONT_DY, CLOTH_BACK_DY = -0.02, +0.03      # mengembang menjauhi paha (hem depan y≈-0,20; belakang ≈+0,215)
SCARF_N = 6

# kaki (diukur dari reference plane): A-stance lebar, sepatu sedikit menghadap keluar
HIP_X, KNEE_X, ANKLE_X = 0.10, 0.18, 0.24
BALL_X, TOE_X = 0.26, 0.275


def arm_dir(s):
    return Vector((s * math.sin(ARM_ANGLE), 0.0, -math.cos(ARM_ANGLE)))


def scarf_points(s):
    """7 titik pusat selendang (helai sisi): dari sabuk samping mengembang ke bawah-luar-belakang."""
    start, end = Vector((s * 0.140, -0.02, 1.08)), Vector((s * 0.35, 0.28, 0.50))   # ujung ±0,35 m ke samping, +0,28 m ke belakang (diukur dari sheet)
    pts = []
    for i in range(SCARF_N + 1):
        t = i / SCARF_N
        p = start.lerp(end, t)
        p.x = s * (0.140 + (0.35 - 0.140) * (t ** 0.85))     # sedikit melengkung keluar
        pts.append(p)
    return pts


def cloth_points(z_list, y, dy):
    """Titik pusat panel kain; dy = pergeseran Y per segmen (depan: -, belakang: +) supaya mengembang menjauhi paha."""
    return [Vector((0.0, y + dy * i, z)) for i, z in enumerate(z_list)]


FINGER_LAT = {"index": 0.033, "middle": 0.011, "ring": -0.011, "pinky": -0.033}   # posisi sepanjang sumbu "depan" telapak
FINGER_SC = {"index": 0.96, "middle": 1.0, "ring": 1.0, "pinky": 0.90}
FINGERS = ["thumb", "index", "middle", "ring", "pinky"]


def hand_frame(sd):
    """Frame tangan (kepalan, telapak menghadap paha): (arah lengan d, depan, ke-dalam, titik dasar)."""
    s = SIDES[sd]
    d = arm_dir(s)
    wrist = Vector((s * 0.205, 0, 1.585)) + d * (UPPERARM_LEN + LOWERARM_LEN)
    front = Vector((0, -1, 0))
    front = (front - front.project(d)).normalized()
    inw = Vector((-s, 0, 0))
    inw = (inw - inw.project(d) - inw.project(front)).normalized()
    return d, front, inw, wrist + d * 0.012


def finger_joints(sd, name):
    """4 titik sendi jari terkepal: pangkal, sendi-1, sendi-2, ujung (3 ruas -> tulang `<jari>_01..03`)."""
    d, front, inw, base = hand_frame(sd)

    def pt(lf, iw, fw):
        k = HAND_SCALE
        return base + front * (lf * k) + inw * (iw * k) + d * (fw * k)

    if name == "thumb":
        return [pt(0.052, 0.0, 0.034), pt(0.058, 0.014, 0.068), pt(0.050, 0.036, 0.090), pt(0.034, 0.052, 0.090)]
    lf, sc = FINGER_LAT[name], FINGER_SC[name]
    return [pt(lf, 0.0, 0.092), pt(lf, 0.016, 0.128 * sc), pt(lf, 0.046, 0.140 * sc), pt(lf, 0.062, 0.104 * sc)]


def build_bones():
    """Urutan induk-dulu. Setiap item: (nama, induk, head, tail, connect)."""
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
        clav_head, shoulder = Vector((s * 0.03, 0, 1.50)), Vector((s * 0.205, 0, 1.585))
        add(f"clavicle_{sd}", "spine_05", clav_head, shoulder)
        d = arm_dir(s)
        elbow = shoulder + d * UPPERARM_LEN
        wrist = elbow + d * LOWERARM_LEN
        add(f"upperarm_{sd}", f"clavicle_{sd}", shoulder, elbow, True)
        add(f"lowerarm_{sd}", f"upperarm_{sd}", elbow, wrist, True)
        add(f"hand_{sd}", f"lowerarm_{sd}", wrist, wrist + d * HAND_LEN, True)
        add(f"upperarm_twist_01_{sd}", f"upperarm_{sd}", shoulder.lerp(elbow, 0.5), elbow, True)
        add(f"lowerarm_twist_01_{sd}", f"lowerarm_{sd}", elbow.lerp(wrist, 0.5), wrist, True)
        for fn in FINGERS:                                          # jari terkepal: 3 ruas per jari
            J = finger_joints(sd, fn)
            prev = f"hand_{sd}"
            for i in range(3):
                n = f"{fn}_{i + 1:02d}_{sd}"
                add(n, prev, J[i], J[i + 1], connect=False)
                prev = n

        hip, knee, ankle = Vector((s * HIP_X, 0, 0.91)), Vector((s * KNEE_X, 0, 0.57)), Vector((s * ANKLE_X, 0, 0.12))
        ball, toe = Vector((s * BALL_X, -0.18, 0.05)), Vector((s * TOE_X, -0.28, 0.04))
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

    # tulang IK gaya Mannequin (tidak men-deform mesh)
    add("ik_foot_root", "root", (0, 0, 0), (0, 0, 0.10))
    add("ik_hand_root", "root", (0, 0, 0), (0, 0, 0.10))
    seg_ = {n: (h, t) for n, _p, h, t, _c in B}
    for sd in SIDES:
        a = seg_[f"foot_{sd}"][0]
        add(f"ik_foot_{sd}", "ik_foot_root", a, a + Vector((0, -0.10, 0)))
    hr = seg_["hand_r"][0]
    add("ik_hand_gun", "ik_hand_root", hr, hr + arm_dir(SIDES["r"]) * 0.08)
    for sd in SIDES:
        h = seg_[f"hand_{sd}"][0]
        add(f"ik_hand_{sd}", "ik_hand_gun", h, h + arm_dir(SIDES[sd]) * 0.08)
    return B


IK_BONES = ["ik_foot_root", "ik_hand_root", "ik_foot_l", "ik_foot_r", "ik_hand_gun", "ik_hand_l", "ik_hand_r"]


def bone_segments():
    return {n: (h, t) for n, _p, h, t, _c in build_bones()}


def chain_bones(chain):
    """Daftar nama tulang berurutan untuk rantai: 'scarf_l', 'scarf_r', 'cloth_front', 'cloth_back'."""
    return [n for n, *_ in build_bones() if n.startswith(chain + "_") and n[len(chain) + 1:].isdigit()]


# Socket (docs/13 6.2): nama -> (tulang induk, posisi)
def build_sockets():
    seg = bone_segments()
    S = {}
    for sd in SIDES:
        h, t = seg[f"hand_{sd}"]
        S[f"SOCKET_hand_{sd}"] = (f"hand_{sd}", h.lerp(t, 0.8) + (t - h).normalized() * 0.04)
        S[f"SOCKET_foot_{sd}"] = (f"foot_{sd}", seg[f"foot_{sd}"][1])
    S["SOCKET_chest_sun"] = ("spine_05", Vector((0, -0.176, 1.48)))
    S["SOCKET_eye_l"] = ("head", Vector((+0.05, -0.12, 1.78)))
    S["SOCKET_eye_r"] = ("head", Vector((-0.05, -0.12, 1.78)))
    S["SOCKET_head_top"] = ("head", Vector((0, 0, CROWN_Z)))
    S["SOCKET_back_center"] = ("spine_04", Vector((0, 0.13, 1.45)))
    return S


# Bone yang ikut memberi bobot pada undersuit (bukan root/kain)
SKIN_BONES = (["pelvis"] + [f"spine_{i:02d}" for i in range(1, 6)] + ["neck_01", "neck_02"]
              + [f"{b}_{sd}" for sd in SIDES for b in ("clavicle", "upperarm", "lowerarm", "hand", "thigh", "calf",
                                                        "upperarm_twist_01", "lowerarm_twist_01", "thigh_twist_01", "calf_twist_01")])
