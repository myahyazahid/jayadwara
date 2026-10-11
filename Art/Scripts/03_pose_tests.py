"""Iterasi 1 — uji pose rig proxy. Pose didefinisikan lewat ARAH tulang (ruang dunia), bukan sudut lokal,
jadi tidak bergantung pada roll tulang. Hasil disimpan sebagai Action `JD_PoseTest` (frame 1..6).

Karakter menghadap -Y; kiri karakter = +X. Frame: 1 A-pose, 2 kuda-kuda, 3 pukul, 4 tendang, 5 injak, 6 jongkok.
"""
import math

import bpy
from mathutils import Matrix, Vector

ARM_NAME = "JD_Armature"
ANKLE_Z = 0.12
rad = math.radians


def V(x, y, z):
    return Vector((x, y, z)).normalized()


def mir(v):
    return Vector((-v.x, v.y, v.z))


def reset(arm):
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def _apply(pb, new_matrix):
    pb.matrix = new_matrix
    bpy.context.view_layer.update()


def aim(arm, bone, direction):
    """Putar tulang di sekitar head-nya agar arah head->tail = direction."""
    pb = arm.pose.bones[bone]
    cur = (pb.tail - pb.head).normalized()
    R = cur.rotation_difference(direction).to_matrix().to_4x4()
    h = pb.head.copy()
    _apply(pb, Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ pb.matrix)


def rot(arm, bone, axis, deg):
    pb = arm.pose.bones[bone]
    h = pb.head.copy()
    R = Matrix.Rotation(rad(deg), 4, axis)
    _apply(pb, Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ pb.matrix)


def move(arm, bone, vec):
    pb = arm.pose.bones[bone]
    m = pb.matrix.copy()
    m.translation += Vector(vec)
    _apply(pb, m)


def ground(arm, calf_bone):
    """Turunkan/naikkan pelvis agar pergelangan kaki `calf_bone` tepat di tinggi lantai."""
    z = arm.pose.bones[calf_bone].tail.z
    move(arm, "pelvis", (0, 0, ANKLE_Z - z))


def _foot_rest():
    """Arah ankle -> ball sisi kiri pada rest pose, diambil dari spesifikasi skeleton."""
    import sys
    sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
    import jd_skeleton as SK
    h, t = SK.bone_segments()["foot_l"]
    return (t - h).normalized()


FOOT_REST = _foot_rest()


def legs(arm, thigh, calf, side):
    """thigh/calf: vektor arah untuk sisi kiri (+X); sisi kanan dicerminkan."""
    for sd, f in (("l", lambda v: v), ("r", mir)):
        if sd in side:
            aim(arm, f"thigh_{sd}", f(thigh[sd]))
            aim(arm, f"calf_{sd}", f(calf[sd]))
            aim(arm, f"foot_{sd}", f(FOOT_REST))


def arm_chain(arm, sd, upper, lower, hand=None):
    aim(arm, f"upperarm_{sd}", upper)
    aim(arm, f"lowerarm_{sd}", lower)
    aim(arm, f"hand_{sd}", hand or lower)


def pose_kuda_kuda(arm):
    t, c = V(0.80, -0.10, -0.59), V(0.03, 0.02, -1.0)
    legs(arm, {"l": t, "r": t}, {"l": c, "r": c}, "lr")
    ground(arm, "calf_l")
    arm_chain(arm, "l", V(0.35, 0.20, -0.91), V(-0.35, -0.85, -0.2))            # kepalan di pinggang
    arm_chain(arm, "r", V(-0.30, -0.75, -0.58), V(-0.05, -0.85, 0.45))          # tangan depan menjaga


def pose_pukul(arm):
    for b, d in (("spine_02", 8), ("spine_03", 8), ("spine_04", 9)):
        rot(arm, b, "Z", d)
    legs(arm, {"l": V(0.12, -0.55, -0.83), "r": V(-0.20, 0.55, -0.81)},
         {"l": V(0.0, 0.10, -1.0), "r": V(0.0, -0.10, -1.0)}, "lr")
    ground(arm, "calf_l")
    arm_chain(arm, "r", V(-0.12, -0.99, -0.02), V(-0.10, -0.99, -0.02))         # pukulan lurus
    arm_chain(arm, "l", V(0.25, 0.35, -0.90), V(-0.2, -0.85, 0.45))


def pose_tendang(arm):
    for b, d in (("spine_02", -4), ("spine_03", -4), ("spine_04", -4)):
        rot(arm, b, "X", d)
    legs(arm, {"l": V(0.08, -0.97, 0.22), "r": V(-0.10, 0.0, -1.0)},
         {"l": V(0.05, -0.97, 0.20), "r": V(-0.03, 0.0, -1.0)}, "lr")
    aim(arm, "foot_l", V(0.0, -0.7, 0.7))
    ground(arm, "calf_r")
    arm_chain(arm, "l", V(0.75, 0.10, -0.65), V(0.78, 0.10, -0.62))
    arm_chain(arm, "r", V(-0.75, 0.10, -0.65), V(-0.78, 0.10, -0.62))


def pose_injak(arm):
    legs(arm, {"l": V(0.10, -0.74, 0.66), "r": V(-0.08, 0.05, -1.0)},
         {"l": V(0.0, 0.05, -1.0), "r": V(-0.04, 0.05, -1.0)}, "lr")
    ground(arm, "calf_r")
    arm_chain(arm, "l", V(0.60, -0.20, -0.50), V(0.45, -0.85, -0.10))
    arm_chain(arm, "r", V(-0.60, -0.20, -0.50), V(-0.45, -0.85, -0.10))


def pose_jongkok(arm):
    for b, d in (("spine_01", 5), ("spine_02", 5), ("spine_03", 5), ("spine_04", 5)):
        rot(arm, b, "X", d)
    t, c = V(0.10, -0.85, -0.51), V(0.0, 0.62, -0.78)
    legs(arm, {"l": t, "r": t}, {"l": c, "r": c}, "lr")
    ground(arm, "calf_l")
    arm_chain(arm, "l", V(0.20, -0.85, -0.45), V(0.10, -0.95, -0.20))
    arm_chain(arm, "r", V(-0.20, -0.85, -0.45), V(-0.10, -0.95, -0.20))


def pose_tangan_atas(arm):                    # kedua lengan terangkat terbuka (uji pauldron vs helm & telinga)
    arm_chain(arm, "l", V(0.55, 0.0, 0.83), V(0.45, -0.05, 0.89))
    arm_chain(arm, "r", V(-0.55, 0.0, 0.83), V(-0.45, -0.05, 0.89))


def pose_raih_depan(arm):                     # kedua lengan lurus ke depan (uji pauldron vs dada)
    arm_chain(arm, "l", V(0.25, -0.96, 0.10), V(0.10, -0.99, 0.10))
    arm_chain(arm, "r", V(-0.25, -0.96, 0.10), V(-0.10, -0.99, 0.10))


def pose_tendang_tinggi(arm):                 # tendangan setinggi kepala (uji kain & sabuk vs paha)
    for b, d in (("spine_02", -4), ("spine_03", -4), ("spine_04", -4)):
        rot(arm, b, "X", d)
    legs(arm, {"l": V(0.05, -0.45, 0.89), "r": V(-0.10, 0.0, -1.0)},
         {"l": V(0.05, -0.50, 0.86), "r": V(-0.03, 0.0, -1.0)}, "lr")
    aim(arm, "foot_l", V(0.0, -0.5, 0.85))
    ground(arm, "calf_r")
    arm_chain(arm, "l", V(0.80, 0.10, -0.55), V(0.85, 0.10, -0.50))
    arm_chain(arm, "r", V(-0.80, 0.10, -0.55), V(-0.85, 0.10, -0.50))


def pose_tangkis(arm):                        # penjagaan: kedua lengan bawah tegak di depan wajah
    arm_chain(arm, "l", V(0.45, -0.50, -0.74), V(-0.15, -0.35, 0.92))
    arm_chain(arm, "r", V(-0.45, -0.50, -0.74), V(0.15, -0.35, 0.92))


def pose_bungkuk(arm):                        # membungkuk ke depan 48° (uji pelat dada/punggung vs sabuk)
    for b in ("spine_01", "spine_02", "spine_03", "spine_04"):
        rot(arm, b, "X", 12)
    rot(arm, "head", "X", -20)


def pose_putar_badan(arm):                    # memutar badan 48° (uji pelat dada vs pauldron & kain)
    for b in ("spine_01", "spine_02", "spine_03", "spine_04"):
        rot(arm, b, "Z", 12)


def pose_tengok(arm):                         # menoleh 55° (uji helm/tanduk vs pauldron & kerah)
    for b, d in (("neck_01", 10), ("neck_02", 10), ("head", 35)):
        rot(arm, b, "Z", d)


POSES = [("a_pose", None), ("kuda_kuda", pose_kuda_kuda), ("pukul", pose_pukul),
         ("tendang", pose_tendang), ("injak", pose_injak), ("jongkok", pose_jongkok),
         ("tangan_atas", pose_tangan_atas), ("raih_depan", pose_raih_depan), ("tendang_tinggi", pose_tendang_tinggi),
         ("tangkis", pose_tangkis), ("bungkuk", pose_bungkuk), ("putar_badan", pose_putar_badan), ("tengok", pose_tengok)]


def build_action():
    arm = bpy.data.objects[ARM_NAME]
    bpy.context.view_layer.objects.active = arm
    if arm.animation_data is None:
        arm.animation_data_create()
    old = bpy.data.actions.get("JD_PoseTest")
    if old:
        bpy.data.actions.remove(old)
    arm.animation_data.action = bpy.data.actions.new("JD_PoseTest")
    for frame, (name, fn) in enumerate(POSES, start=1):
        reset(arm)
        if fn:
            fn(arm)
        for pb in arm.pose.bones:
            pb.keyframe_insert("location", frame=frame)
            pb.keyframe_insert("rotation_quaternion", frame=frame)
        print(f"frame {frame}: {name}")
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, len(POSES)
    bpy.context.scene.frame_set(1)
    return arm


arm = build_action()
print("pose test siap:", [p[0] for p in POSES])
