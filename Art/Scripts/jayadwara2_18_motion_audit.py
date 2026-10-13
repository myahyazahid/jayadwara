"""Jayadwara2 — audit gerak kaki & kain: rest, jalan (2 fase), lompat (lutut ditarik), mendarat (jongkok), dilihat dari
samping, belakang 3/4, depan 3/4, dan BAWAH (kamera di bawah selangkangan, seperti saat raksasa melompati kamera).

  blender --background <file.blend> --python Art/Scripts/jayadwara2_18_motion_audit.py -- <tag>
Keluaran: Art/Export/_jd2/audit_<tag>/<pose>_<kamera>.png + lembar gabungan _sheet.png
Juga mencetak: jumlah tepi terbuka (lubang/sobek) pada mesh, dan tepi yang meregang > 4 cm per pose (badan vs kain).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

tag = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "x"
OUT = rf"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2\audit_{tag}"
os.makedirs(OUT, exist_ok=True)
arm = bpy.data.objects["JD2_Armature"]
body = bpy.data.objects["JD2_Body"]
sc = bpy.context.scene
sc.frame_set(1)
if arm.animation_data:
    arm.animation_data.action = None

# --- tepi terbuka di mesh rest (lubang dari split/hapus pulau)
bm = bmesh.new()
bm.from_mesh(body.data)
open_edges = sum(1 for e in bm.edges if e.is_boundary)
src = bpy.data.objects.get("JD2_Source")
src_open = 0
if src:
    b2 = bmesh.new(); b2.from_mesh(src.data); src_open = sum(1 for e in b2.edges if e.is_boundary); b2.free()
print(f"tepi terbuka: badan {open_edges} (sumber Tripo {src_open})")
edges = np.array([(e.verts[0].index, e.verts[1].index) for e in bm.edges])
bm.free()
import json
mac = json.loads(body["jd2_macro"]) if "jd2_macro" in body else ["?"] * len(body.data.vertices)
cloth_v = np.array([str(m).startswith(("WING", "CLOTH")) for m in mac])
cloth_e = cloth_v[edges[:, 0]] | cloth_v[edges[:, 1]]


def reset():
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def rot(bone, axis, deg):
    pb = arm.pose.bones[bone]
    h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()


def lift(dz):
    pb = arm.pose.bones["pelvis"]
    m = pb.matrix.copy()
    m.translation.z += dz
    pb.matrix = m
    bpy.context.view_layer.update()


# karakter menghadap -Y: rotasi X negatif = paha maju
POSES = {
    "rest": lambda: None,
    "jalan_a": lambda: (rot("thigh_l", "X", -28), rot("calf_l", "X", 6), rot("thigh_r", "X", 18), rot("calf_r", "X", 30),
                        rot("upperarm_l", "X", 22), rot("upperarm_r", "X", -22)),
    "jalan_b": lambda: (rot("thigh_r", "X", -28), rot("calf_r", "X", 6), rot("thigh_l", "X", 18), rot("calf_l", "X", 30),
                        rot("upperarm_r", "X", 22), rot("upperarm_l", "X", -22)),
    "lompat": lambda: (rot("thigh_l", "X", -55), rot("calf_l", "X", 80), rot("thigh_r", "X", -40), rot("calf_r", "X", 70),
                       rot("upperarm_l", "Y", -30), rot("upperarm_r", "Y", 30), lift(0.25)),
    "mendarat": lambda: (rot("thigh_l", "X", -60), rot("calf_l", "X", 95), rot("thigh_r", "X", -60), rot("calf_r", "X", 95),
                         rot("foot_l", "X", -35), rot("foot_r", "X", -35), lift(-0.30), rot("spine_02", "X", 12)),
    "langkah_lebar": lambda: (rot("thigh_l", "Y", 25), rot("thigh_r", "Y", -25), lift(-0.06)),
}
CAMS = {"samping": (2.6, 0, 0.75), "belakang34": (1.4, 2.0, 0.85), "depan34": (-1.4, -2.0, 0.85), "bawah": (0.5, -0.9, -0.9)}   # dekat: pinggul-kaki

sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light, sh.color_type, sh.show_cavity = "FLAT", "TEXTURE", False
sh.show_backface_culling = False
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
sc.world.color = (0.45, 0.5, 0.55)
for o in bpy.data.objects:
    if o.type in {"ARMATURE", "EMPTY"} or o.name.startswith(("JD2_Source", "JD2_Body_LOD")):
        o.hide_render = True
cd = bpy.data.cameras.new("auditcam")
cam = bpy.data.objects.new("auditcam", cd)
sc.collection.objects.link(cam)
sc.camera = cam
cd.type = "PERSP"
cd.lens = 55
sc.render.resolution_x, sc.render.resolution_y = 600, 700


def positions():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    me = ev.to_mesh()
    P = np.array([ev.matrix_world @ v.co for v in me.vertices])
    ev.to_mesh_clear()
    return P


reset()
P0 = positions()
L0 = np.linalg.norm(P0[edges[:, 0]] - P0[edges[:, 1]], axis=1)
print(f"{'pose':14s} {'badan>4cm':>9s} {'badan>8cm':>9s} {'kain>4cm':>9s} {'kain>8cm':>9s} {'maks cm':>8s}")
files = []
for pn, fn in POSES.items():
    reset()
    fn()
    P = positions()
    d = np.abs(np.linalg.norm(P[edges[:, 0]] - P[edges[:, 1]], axis=1) - L0)
    print(f"{pn:14s} {(d[~cloth_e] > .04).sum():9d} {(d[~cloth_e] > .08).sum():9d} {(d[cloth_e] > .04).sum():9d} {(d[cloth_e] > .08).sum():9d} {d.max() * 100:8.1f}")
    for cn, loc in CAMS.items():
        target = Vector((0, 0, 0.62 if cn != "bawah" else 0.75))
        cam.location = Vector(loc) * (1.0 if cn != "bawah" else 1.0)
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        f = os.path.join(OUT, f"{pn}_{cn}.png")
        sc.render.filepath = f
        bpy.ops.render.render(write_still=True)
        files.append(f)
reset()
print("selesai ->", OUT)
