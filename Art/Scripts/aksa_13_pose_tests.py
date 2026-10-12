"""Aksa Iterasi 1 — 6 uji pose silat + metrik peregangan (cm absolut) per bagian.

Jalankan di Blender (aksa_v01_proxy.blend terbuka, setelah aksa_11_proxy.py). Membuat action `AK_PoseTest`:
frame 1 = rest, 2 kuda-kuda, 3 pukul, 4 tendang tinggi, 5 dodge, 6 jongkok, 7 tangan terangkat. Rotasi dalam RUANG ARMATURE
(sumbu +X kiri, -Y depan, +Z atas, tidak bergantung pada orientasi tulang Manny): tiap operasi = (tulang, sumbu, derajat),
diterapkan dari induk ke anak, pivot di kepala tulang. Setelah itu menghitung peregangan tepi (selisih panjang tepi vs rest,
cm absolut) per bagian dan mencetak yang terburuk. Pose tidak mengubah pose rest (frame 1) dan tidak ikut export.
"""
import importlib
import math
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C

importlib.reload(C)
arm = C.get_arm()
scene = bpy.context.scene
AX = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}

POSES = {
    "rest": [],
    "kuda_kuda": [("pelvis", "down", 0.20), ("thigh_l", "y", -48), ("thigh_r", "y", 48), ("calf_l", "y", 36), ("calf_r", "y", -36),
                  ("upperarm_l", "x", -55), ("upperarm_r", "x", -55), ("lowerarm_l", "x", -75), ("lowerarm_r", "x", -75),
                  ("foot_l", "y", 12), ("foot_r", "y", -12)],
    "pukul": [("spine_02", "z", 18), ("spine_03", "z", 14), ("upperarm_r", "x", -80), ("lowerarm_r", "x", -8),
              ("upperarm_l", "x", -60), ("lowerarm_l", "x", -95), ("thigh_l", "x", -20), ("calf_l", "x", 25), ("thigh_r", "x", 12)],
    "tendang_tinggi": [("spine_02", "x", 12), ("spine_03", "x", 10), ("thigh_r", "x", -105), ("calf_r", "x", 8), ("foot_r", "x", -25),
                       ("upperarm_l", "y", -30), ("upperarm_r", "y", 55), ("lowerarm_r", "x", -40), ("pelvis", "down", 0.05)],
    "dodge": [("spine_01", "x", 12), ("spine_02", "x", 14), ("spine_03", "x", 14), ("neck_01", "x", 8), ("pelvis", "down", 0.08),
              ("thigh_l", "x", -25), ("calf_l", "x", 35), ("thigh_r", "x", 18), ("upperarm_l", "x", -40), ("upperarm_r", "x", -40),
              ("lowerarm_l", "x", -70), ("lowerarm_r", "x", -70)],
    "jongkok": [("pelvis", "down", 0.46), ("spine_01", "x", -12), ("spine_02", "x", -14), ("thigh_l", "x", -100), ("thigh_r", "x", -100),
                ("calf_l", "x", 118), ("calf_r", "x", 118), ("foot_l", "x", -20), ("foot_r", "x", -20),
                ("upperarm_l", "x", -45), ("upperarm_r", "x", -45)],
    "tangan_terangkat": [("clavicle_l", "y", -12), ("clavicle_r", "y", 12), ("upperarm_l", "y", -150), ("upperarm_r", "y", 150),
                         ("lowerarm_l", "y", -10), ("lowerarm_r", "y", 10)],
}
ORDER = ["pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "neck_02", "head", "clavicle_l", "clavicle_r",
         "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r", "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l",
         "foot_r", "ball_l", "ball_r"]


def reset_pose():
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def apply(ops):
    reset_pose()
    ops = sorted(ops, key=lambda o: ORDER.index(o[0]))
    for name, axis, val in ops:
        pb = arm.pose.bones[name]
        M = pb.matrix.copy()
        if axis == "down":
            pb.matrix = Matrix.Translation((0, 0, -val)) @ M
        else:
            R = Matrix.Rotation(math.radians(val), 4, AX[axis])
            head = M.translation.copy()
            pb.matrix = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ M
        bpy.context.view_layer.update()


def key_all(frame):
    for pb in arm.pose.bones:
        pb.keyframe_insert("location", frame=frame)
        pb.keyframe_insert("rotation_quaternion" if pb.rotation_mode == "QUATERNION" else "rotation_euler", frame=frame)


if arm.animation_data:
    arm.animation_data.action = None
for a in list(bpy.data.actions):
    if a.name == "AK_PoseTest":
        bpy.data.actions.remove(a)
arm.animation_data_create()
act = bpy.data.actions.new("AK_PoseTest")
arm.animation_data.action = act
frames = {}
for i, (pname, ops) in enumerate(POSES.items(), start=1):
    apply(ops)
    key_all(i)
    frames[pname] = i
act["frames"] = frames
scene.frame_start, scene.frame_end = 1, len(POSES)
print("action AK_PoseTest:", frames)


# ---- peregangan tepi (cm absolut) vs rest
parts = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("AK_") and not o.name.startswith("AK_REF")]


def edge_lengths(frame):
    scene.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    for o in parts:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        out[o.name] = [(me.vertices[e.vertices[0]].co - me.vertices[e.vertices[1]].co).length for e in me.edges]
        ev.to_mesh_clear()
    return out


rest = edge_lengths(1)
worst_all = []
for pname, f in frames.items():
    if pname == "rest":
        continue
    cur = edge_lengths(f)
    w = []
    for n, rl in rest.items():
        d = max((abs(a - b) for a, b in zip(rl, cur[n])), default=0.0)
        w.append((d * 100, n))
    w.sort(reverse=True)
    worst_all.append((pname, w[0], w[1], w[2]))
    print(f"  {pname:17s} peregangan maks {w[0][0]:5.2f} cm ({w[0][1]}) | {w[1][0]:5.2f} ({w[1][1]}) | {w[2][0]:5.2f} ({w[2][1]})")
scene.frame_set(1)
reset_pose()
print("peregangan terburuk keseluruhan: %.2f cm" % max(x[1][0] for x in worst_all))
bpy.ops.wm.save_mainfile()
