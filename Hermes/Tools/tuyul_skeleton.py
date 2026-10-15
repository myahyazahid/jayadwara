"""Spesifikasi skeleton Tuyul (K1, Hermes/tuyul_hermes.md): jenis B — nama & hierarki Mannequin,
tanpa twist bone, + `jaw` (mulut bercelah, disetujui di K0). Posisi sendi diukur dari mesh Tripo
`TY_Source` (lihat Hermes/Tools/tuyul_04_measure.py, tuyul_05_centerlines.py; tabel di laporan K1).

Karakter menghadap -Y; kiri karakter = +X (`_l`). Pose rest = pose mesh Tripo (bungkuk, lengan panjang
menggantung melewati lutut; docs/27 arahan desain). 1 unit = 1 m, tinggi 1,0 m.
Satu sumber data untuk rig (tuyul_10_rig.py), bobot (K3), socket, dan export (K3/K5).
Pola: Art/Scripts/jk_skeleton.py.
"""
from mathutils import Vector

SIDES = {"l": +1, "r": -1}

# landmark sisi kiri (+X) diukur dari mesh (m); sisi kanan dicerminkan X kecuali ada di LM_R
LM = {
    "clav_head": (0.030, 0.020, 0.755),
    "shoulder": (0.160, 0.000, 0.750),
    "elbow": (0.235, -0.020, 0.485),
    "wrist": (0.252, -0.020, 0.265),
    "knuckle": (0.248, -0.022, 0.238),
    "hip": (0.100, 0.010, 0.285),
    "knee": (0.110, 0.020, 0.150),
    "ankle": (0.120, 0.020, 0.070),
    "ball": (0.130, -0.060, 0.030),
    "toe": (0.140, -0.130, 0.020),
}
# override sisi kanan (mesh tidak simetris di tangan): koordinat absolut (x sudah negatif)
LM_R = {
    "wrist": (-0.252, -0.020, 0.265),
    "knuckle": (-0.248, -0.020, 0.242),
}
# tulang belakang: pelvis head, spine_01..05 head, spine_05 tail (z) + sedikit lekuk Y (bungkuk)
SPINE = [(0, 0.010, 0.285), (0, 0.010, 0.380), (0, 0.005, 0.475), (0, -0.005, 0.570),
         (0, -0.005, 0.665), (0, 0.000, 0.760)]
NECK = [(0, 0.000, 0.760), (0, 0.000, 0.830), (0, -0.010, 0.880)]     # neck_01, neck_02, head (head)
HEAD_TAIL = (0, -0.030, 0.955)
JAW = ((0, -0.050, 0.860), (0, -0.180, 0.820))                        # engsel -> dagu (mulut menganga)

FINGERS = ["thumb", "index", "middle"]
# titik jari per sisi: (pangkal, sendi-1, sendi-2, ujung) ruang model, m
FINGER_PTS = {
    "l": {
        "thumb": [(0.240, -0.072, 0.235), (0.236, -0.073, 0.215), (0.229, -0.076, 0.190), (0.206, -0.072, 0.163)],
        "index": [(0.251, -0.028, 0.228), (0.247, -0.038, 0.203), (0.235, -0.042, 0.180), (0.211, -0.044, 0.161)],
        "middle": [(0.252, -0.008, 0.222), (0.247, -0.007, 0.203), (0.236, -0.008, 0.190), (0.224, -0.009, 0.181)],
    },
    "r": {
        "thumb": [(-0.237, -0.069, 0.240), (-0.233, -0.067, 0.216), (-0.224, -0.064, 0.196), (-0.208, -0.060, 0.181)],
        "index": [(-0.252, -0.024, 0.240), (-0.248, -0.018, 0.220), (-0.234, -0.014, 0.202), (-0.217, -0.012, 0.190)],
        "middle": [(-0.236, 0.011, 0.245), (-0.231, 0.013, 0.239), (-0.226, 0.014, 0.233), (-0.222, 0.014, 0.228)],
    },
}


def V(t):
    return Vector(t)


def P(name, s):
    if s < 0 and name in LM_R:
        return V(LM_R[name])
    x, y, z = LM[name]
    return Vector((s * x, y, z))


def finger_joints(sd, name):
    """4 titik (pangkal, sendi-1, sendi-2, ujung) jari, diukur dari mesh."""
    return [V(p) for p in FINGER_PTS[sd][name]]


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
        add(n, prev, SPINE[i + 1], SPINE[i + 2] if i < 4 else SPINE[5], connect=True)
        prev = n
    add("neck_01", "spine_05", NECK[0], NECK[1], True)
    add("neck_02", "neck_01", NECK[1], NECK[2], True)
    add("head", "neck_02", NECK[2], HEAD_TAIL, True)
    add("jaw", "head", JAW[0], JAW[1])

    for sd in SIDES:
        s = SIDES[sd]
        add(f"clavicle_{sd}", "spine_05", P("clav_head", s), P("shoulder", s))
        add(f"upperarm_{sd}", f"clavicle_{sd}", P("shoulder", s), P("elbow", s), True)
        add(f"lowerarm_{sd}", f"upperarm_{sd}", P("elbow", s), P("wrist", s), True)
        add(f"hand_{sd}", f"lowerarm_{sd}", P("wrist", s), P("knuckle", s), True)
        for fn in FINGERS:
            J = finger_joints(sd, fn)
            prev = f"hand_{sd}"
            for i in range(3):
                n = f"{fn}_{i + 1:02d}_{sd}"
                add(n, prev, J[i], J[i + 1], connect=(i > 0))
                prev = n
        add(f"thigh_{sd}", "pelvis", P("hip", s), P("knee", s))
        add(f"calf_{sd}", f"thigh_{sd}", P("knee", s), P("ankle", s), True)
        add(f"foot_{sd}", f"calf_{sd}", P("ankle", s), P("ball", s), True)
        add(f"ball_{sd}", f"foot_{sd}", P("ball", s), P("toe", s), True)

    # tulang IK gaya Mannequin (tidak men-deform mesh)
    add("ik_foot_root", "root", (0, 0, 0), (0, 0, 0.10))
    add("ik_hand_root", "root", (0, 0, 0), (0, 0, 0.10))
    for sd in SIDES:
        a = P("ankle", SIDES[sd])
        add(f"ik_foot_{sd}", "ik_foot_root", a, a + Vector((0, -0.10, 0)))
    hr = P("wrist", SIDES["r"])
    add("ik_hand_gun", "ik_hand_root", hr, hr + Vector((0, 0, -0.08)))
    for sd in SIDES:
        h = P("wrist", SIDES[sd])
        add(f"ik_hand_{sd}", "ik_hand_gun", h, h + Vector((0, 0, -0.08)))
    return B


IK_BONES = ["ik_foot_root", "ik_hand_root", "ik_foot_l", "ik_foot_r", "ik_hand_gun", "ik_hand_l", "ik_hand_r"]


def bone_segments():
    return {n: (h, t) for n, _p, h, t, _c in build_bones()}


# Socket (kartu model K0): nama -> (tulang induk, posisi rest)
def build_sockets():
    seg = bone_segments()
    S = {"head_top": ("head", V((0, -0.02, 0.97))), "mouth_fx": ("jaw", V((0, -0.20, 0.83)))}
    for sd in SIDES:
        h, t = seg[f"hand_{sd}"]
        S[f"hand_{sd}_hit"] = (f"hand_{sd}", t + (t - h).normalized() * 0.03)
        S[f"carry_{sd}"] = (f"hand_{sd}", t)
        S[f"foot_{sd}_hit"] = (f"foot_{sd}", seg[f"foot_{sd}"][1])
    return S
