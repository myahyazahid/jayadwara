"""Spike skeleton model Aksa (docs/19 Iterasi 0) — analisis FBX Manny hasil Tools/ue_export_manny.py.

STATUS: teruji 12 Okt 2026 (UE 5.6.1, SKM_Manny_Simple). Catatan: importer Blender menjadikan node `root` sebagai OBJEK armature (bukan tulang); tulang akar = pelvis, ik_foot_root, ik_hand_root, interaction, center_of_mass.
Jalankan headless (tidak menyentuh sesi Blender yang terbuka):
  blender --background --factory-startup --python Art/Scripts/aksa_spike_analyze_manny.py
Mencetak + menulis Art/Reference/manny/manny_rest.json:
  jumlah/nama/hierarki tulang, posisi sendi (m), tinggi mesh, sudut A-pose lengan (dari vertikal),
  lebar kaki, rotasi root/armature. Dipakai untuk memutuskan A1/A3 (docs/19 §Temuan) dan sudut pose rest (docs/21 D2).
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
FBX = ROOT / "Art" / "Reference" / "manny" / "SKM_Manny_Simple.fbx"
OUT = ROOT / "Art" / "Reference" / "manny" / "manny_rest.json"
JOINTS = ["pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "neck_02", "head",
          "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "thigh_l", "calf_l", "foot_l", "ball_l",
          "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r", "thigh_r", "calf_r", "foot_r", "ball_r"]

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=str(FBX))

arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
print("armature:", [(a.name, tuple(round(v, 4) for v in a.scale), tuple(round(math.degrees(v), 1) for v in a.rotation_euler)) for a in arms])
print("mesh:", [(m.name, len(m.data.polygons)) for m in meshes])
arm = max(arms, key=lambda a: len(a.data.bones))
mw = arm.matrix_world

# tinggi mesh (ruang dunia)
zs = [(m.matrix_world @ Vector(c)).z for m in meshes for c in m.bound_box]
height = max(zs) - min(zs)
unit = 0.01 if height > 20 else 1.0           # FBX cm yang tidak dikonversi importer -> ke meter
print(f"tinggi mesh {height:.3f} (unit blender) -> {height * unit:.3f} m; skala ke meter = {unit}")


def pos(name):
    b = arm.data.bones.get(name)
    return None if b is None else (mw @ b.head_local) * unit


joints = {n: tuple(round(c, 4) for c in pos(n)) for n in JOINTS if pos(n) is not None}
missing = [n for n in JOINTS if n not in joints]
print("bone:", len(arm.data.bones), "| root:", [b.name for b in arm.data.bones if b.parent is None], "| tidak ada:", missing)


def angle_from_down(a, b):
    v = Vector(joints[b]) - Vector(joints[a])
    return round(math.degrees(v.angle(Vector((0, 0, -1)))), 1)


report = {"height_m": round(height * unit, 4), "bone_count": len(arm.data.bones), "missing": missing, "joints_m": joints,
          "armature_scale": list(arm.scale), "armature_rot_deg": [round(math.degrees(v), 2) for v in arm.rotation_euler]}
if not missing:
    report["arm_angle_deg"] = {"upperarm": angle_from_down("upperarm_l", "lowerarm_l"),
                               "lowerarm": angle_from_down("lowerarm_l", "hand_l"),
                               "whole": angle_from_down("upperarm_l", "hand_l")}
    report["stance_m"] = {"hip_x": joints["thigh_l"][0], "knee_x": joints["calf_l"][0], "ankle_x": joints["foot_l"][0]}
    report["leg_len_m"] = round(joints["thigh_l"][2] - joints["foot_l"][2], 3)
    report["hierarchy"] = {b.name: (b.parent.name if b.parent else None) for b in arm.data.bones}
print(json.dumps({k: v for k, v in report.items() if k not in ("hierarchy", "joints_m")}, indent=1))
OUT.write_text(json.dumps(report, indent=1), encoding="utf-8")
print("ditulis:", OUT)
