"""Spesifikasi skeleton Jerangkong (docs/20 6.1, jalur B): posisi sendi diukur dari mesh Tripo (`JK_Source`).

Satu sumber data untuk rig (jerangkong_10_rig.py), segmentasi potongan (jerangkong_11_pieces.py), socket, dan export.
Nama tulang = Mannequin (tanpa twist) + `jaw` + `cloth_front/back_01..03` + tulang IK. Pose rest = pose mesh Tripo
(bungkuk sedang, lengan menggantung; docs/24 S2/S3). Karakter menghadap -Y; kiri karakter = +X (`_l`).
Model asimetris (siku kanan lebih rendah), jadi kiri & kanan diukur terpisah, tidak dicerminkan.
Cara ukur: profil penampang per 4 cm (pusat median), pendar merah sendi dari tekstur warna, render ortografis bergrid.
"""
from mathutils import Vector

SIDES = {"l": +1, "r": -1}

# sendi lengan & kaki per sisi (m)
ARM = {
    "l": dict(clav=(0.04, 0.02, 1.86), shoulder=(0.34, -0.04, 1.85), elbow=(0.435, -0.09, 1.335),
              wrist=(0.51, -0.17, 0.80), knuckle=(0.50, -0.17, 0.62), tip=(0.46, -0.15, 0.40)),
    "r": dict(clav=(-0.04, 0.02, 1.86), shoulder=(-0.35, -0.03, 1.85), elbow=(-0.48, -0.06, 1.27),
              wrist=(-0.54, -0.13, 0.80), knuckle=(-0.52, -0.12, 0.62), tip=(-0.45, -0.10, 0.40)),
}
LEG = {
    "l": dict(hip=(0.17, -0.01, 1.27), knee=(0.265, -0.09, 0.77), ankle=(0.31, 0.0, 0.21),
              ball=(0.33, -0.17, 0.05), toe=(0.33, -0.34, 0.04)),
    "r": dict(hip=(-0.17, -0.01, 1.27), knee=(-0.275, -0.10, 0.77), ankle=(-0.275, 0.01, 0.21),
              ball=(-0.30, -0.17, 0.05), toe=(-0.31, -0.34, 0.04)),
}
SPINE = [(0, 0.0, 1.27), (0, 0.03, 1.38), (0, 0.05, 1.46), (0, 0.06, 1.55), (0, 0.07, 1.65), (0, 0.06, 1.75),
         (0, 0.03, 1.85)]                                         # pelvis head, spine_01..05 head, spine_05 tail
NECK = [(0, 0.03, 1.85), (0, -0.03, 1.93), (0, -0.09, 1.98)]     # neck_01, neck_02, head (head)
HEAD_TAIL = (0, -0.20, 2.17)
SKULL_CENTER = (0, -0.235, 2.04)                                  # pusat kubah tengkorak (bola ±0,14)
JAW = ((0, -0.165, 1.955), (0, -0.31, 1.885))                     # engsel -> dagu
CLOTH_FRONT = [(0, -0.13, 1.36), (0, -0.15, 1.12), (0, -0.16, 0.88), (0, -0.17, 0.62)]
CLOTH_BACK = [(0, 0.14, 1.36), (0, 0.16, 1.12), (0, 0.17, 0.88), (0, 0.18, 0.62)]

FINGERS = ["thumb", "index", "middle", "ring", "pinky"]
# jari: offset pangkal (sepanjang sumbu depan telapak) & panjang relatif; geometri jari kaku ikut hand_* (docs/24 S7)
FINGER_FRONT = {"thumb": -0.045, "index": -0.035, "middle": -0.012, "ring": 0.012, "pinky": 0.033}
FINGER_LEN = {"thumb": 0.55, "index": 0.95, "middle": 1.0, "ring": 0.95, "pinky": 0.8}


def V(t):
    return Vector(t)


def finger_joints(sd, name):
    """4 titik (pangkal, sendi-1, sendi-2, ujung) di sepanjang garis knuckle -> ujung, digeser ke depan/belakang."""
    a = ARM[sd]
    knuckle, tip, wrist = V(a["knuckle"]), V(a["tip"]), V(a["wrist"])
    d = (tip - knuckle)
    front = Vector((0, -1, 0))
    front = (front - front.project(d)).normalized()
    off = front * -FINGER_FRONT[name]
    if name == "thumb":
        base = wrist.lerp(knuckle, 0.55) + off
        end = base + d.normalized() * d.length * FINGER_LEN[name] + front * 0.03
    else:
        base = knuckle + off
        end = base + d * FINGER_LEN[name]
    return [base.lerp(end, t) for t in (0.0, 0.45, 0.78, 1.0)]


def build_bones():
    """Urutan induk-dulu. Setiap item: (nama, induk, head, tail, connect)."""
    B = []

    def add(name, parent, head, tail, connect=False):
        B.append((name, parent, V(head), V(tail), connect))

    add("root", None, (0, 0, 0), (0, 0, 0.15))
    add("pelvis", "root", SPINE[0], SPINE[1])
    prev = "pelvis"
    for i in range(5):
        n = f"spine_{i + 1:02d}"
        add(n, prev, SPINE[i + 1], SPINE[i + 2] if i < 4 else SPINE[6], connect=True)
        prev = n
    add("neck_01", "spine_05", NECK[0], NECK[1], True)
    add("neck_02", "neck_01", NECK[1], NECK[2], True)
    add("head", "neck_02", NECK[2], HEAD_TAIL, True)
    add("jaw", "head", JAW[0], JAW[1])

    for sd in SIDES:
        a, g = ARM[sd], LEG[sd]
        add(f"clavicle_{sd}", "spine_05", a["clav"], a["shoulder"])
        add(f"upperarm_{sd}", f"clavicle_{sd}", a["shoulder"], a["elbow"], True)
        add(f"lowerarm_{sd}", f"upperarm_{sd}", a["elbow"], a["wrist"], True)
        add(f"hand_{sd}", f"lowerarm_{sd}", a["wrist"], a["knuckle"], True)
        for fn in FINGERS:
            J = finger_joints(sd, fn)
            prev = f"hand_{sd}"
            for i in range(3):
                n = f"{fn}_{i + 1:02d}_{sd}"
                add(n, prev, J[i], J[i + 1], connect=(i > 0))
                prev = n
        add(f"thigh_{sd}", "pelvis", g["hip"], g["knee"])
        add(f"calf_{sd}", f"thigh_{sd}", g["knee"], g["ankle"], True)
        add(f"foot_{sd}", f"calf_{sd}", g["ankle"], g["ball"], True)
        add(f"ball_{sd}", f"foot_{sd}", g["ball"], g["toe"], True)

    for chain, pts in (("cloth_front", CLOTH_FRONT), ("cloth_back", CLOTH_BACK)):
        prev = "pelvis"
        for i in range(len(pts) - 1):
            n = f"{chain}_{i + 1:02d}"
            add(n, prev, pts[i], pts[i + 1], connect=(i > 0))
            prev = n

    # tulang IK gaya Mannequin (tidak men-deform mesh)
    add("ik_foot_root", "root", (0, 0, 0), (0, 0, 0.10))
    add("ik_hand_root", "root", (0, 0, 0), (0, 0, 0.10))
    for sd in SIDES:
        a = V(LEG[sd]["ankle"])
        add(f"ik_foot_{sd}", "ik_foot_root", a, a + Vector((0, -0.10, 0)))
    hr = V(ARM["r"]["wrist"])
    add("ik_hand_gun", "ik_hand_root", hr, hr + Vector((0, 0, -0.08)))
    for sd in SIDES:
        h = V(ARM[sd]["wrist"])
        add(f"ik_hand_{sd}", "ik_hand_gun", h, h + Vector((0, 0, -0.08)))
    return B


IK_BONES = ["ik_foot_root", "ik_hand_root", "ik_foot_l", "ik_foot_r", "ik_hand_gun", "ik_hand_l", "ik_hand_r"]


def bone_segments():
    return {n: (h, t) for n, _p, h, t, _c in build_bones()}


# ---- potongan (docs/20 bagian 4): nama -> (tulang pivot SM, bisa rontok?)
PIECES = {
    "Skull": ("head", True), "Jaw": ("jaw", False), "Ribs": ("spine_04", True), "Spine": ("spine_02", False),
    "Pelvis": ("pelvis", False),
    "UpperArmL": ("upperarm_l", True), "UpperArmR": ("upperarm_r", True),
    "LowerArmL": ("lowerarm_l", True), "LowerArmR": ("lowerarm_r", True),
    "HandL": ("hand_l", True), "HandR": ("hand_r", True),
    "ThighL": ("thigh_l", True), "ThighR": ("thigh_r", True),
    "CalfL": ("calf_l", True), "CalfR": ("calf_r", True),
    "FootL": ("foot_l", True), "FootR": ("foot_r", True),
}
# tulang yang boleh membawa vertex tiap potongan (bobot kaku 1,0 ke salah satunya; kain: bobot halus rantai)
PIECE_BONES = {
    "Skull": ["head"], "Jaw": ["jaw"], "Ribs": ["spine_03", "spine_04", "spine_05", "clavicle_l", "clavicle_r"],
    "Spine": ["spine_01", "spine_02", "neck_01", "neck_02"],
    "Pelvis": ["pelvis", "cloth_front_01", "cloth_front_02", "cloth_front_03", "cloth_back_01", "cloth_back_02", "cloth_back_03"],
}
for _sd, _S in (("l", "L"), ("r", "R")):
    for _p, _b in (("UpperArm", "upperarm"), ("LowerArm", "lowerarm"), ("Hand", "hand"), ("Thigh", "thigh"),
                   ("Calf", "calf"), ("Foot", "foot")):
        PIECE_BONES[f"{_p}{_S}"] = [f"{_b}_{_sd}"]


# Socket (docs/20 6.3): nama -> (tulang induk, posisi rest)
def build_sockets():
    seg = bone_segments()
    S = {
        "skull_weakpoint": ("head", V((0.0, -0.30, 2.13))),          # pusat retak dahi
        "mouth_fx": ("jaw", V((0.0, -0.32, 1.92))),
        "chest_core": ("spine_04", V((0.0, -0.02, 1.68))),
    }
    for sd in SIDES:
        h, t = seg[f"hand_{sd}"]
        S[f"hand_{sd}_hit"] = (f"hand_{sd}", t.lerp(V(ARM[sd]["tip"]), 0.5))
        S[f"foot_{sd}_hit"] = (f"foot_{sd}", seg[f"foot_{sd}"][1])
    S["throw_r"] = ("hand_r", seg["hand_r"][1])
    return S
