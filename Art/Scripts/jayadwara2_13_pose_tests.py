"""Jayadwara2 R1/R3 — 13 pose uji (pose sama dengan model lama, 03_pose_tests.py) + peregangan + contact sheet.

  blender --background Art/Blender/jayadwara2/jayadwara2_v02_rig_spike.blend --python Art/Scripts/jayadwara2_13_pose_tests.py -- [outdir]
Pose didefinisikan lewat ARAH tulang (ruang dunia), jadi bisa dipakai ulang di rest berbeda. Hasil: Action `JD_PoseTest`
(disimpan ke .blend), PNG per pose + `_sheet.png` di outdir (default Art/Export/_jd2/poses), tabel peregangan di stdout.
"""
import math
import sys
import types
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

SCRIPTS = Path(r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
sys.path.insert(0, str(SCRIPTS))
import jd2_skeleton as SK

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else Path(r"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2\poses")
OUT.mkdir(parents=True, exist_ok=True)

# 03_pose_tests mengimpor jd_skeleton (bone_segments) untuk arah telapak -> pakai skeleton baru
fake = types.ModuleType("jd_skeleton")
fake.bone_segments = SK.bone_segments
sys.modules["jd_skeleton"] = fake
src = (SCRIPTS / "03_pose_tests.py").read_text(encoding="utf-8")
src = src.replace('ARM_NAME = "JD_Armature"', 'ARM_NAME = "JD2_Armature"')
src = src.replace("ANKLE_Z = 0.12", f"ANKLE_Z = {SK.LM['ankle'][2]}")
ns = {"__name__": "pose03"}
exec(compile(src, "03_pose_tests.py", "exec"), ns)
sys.modules["jd_skeleton"] = sys.modules.get("jd_skeleton_real", fake)
POSES = [p[0] for p in ns["POSES"]]

scene = bpy.context.scene
arm = bpy.data.objects["JD2_Armature"]
body = bpy.data.objects["JD2_Body"]
mesh = body.data
edges = np.array([e.vertices[:] for e in mesh.edges])
import json
_mac = json.loads(body["jd2_macro"]) if "jd2_macro" in body else None
_iscloth = np.array([str(m).startswith(("WING", "CLOTH")) for m in _mac]) if _mac else np.zeros(len(mesh.vertices), bool)
cloth_edge = _iscloth[edges[:, 0]] | _iscloth[edges[:, 1]]   # R3: metrik dipisah badan vs kain/sayap

# ------------------------------------------------------------------ peregangan
def positions():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    me = ev.to_mesh()
    P = np.array([ev.matrix_world @ v.co for v in me.vertices], float)
    ev.to_mesh_clear()
    return P

scene.frame_set(1)
rest = positions()
L0 = np.linalg.norm(rest[edges[:, 0]] - rest[edges[:, 1]], axis=1)
print(f"{'pose':16s} {'rasio min':>9s} {'rasio maks':>10s} {'ubah maks cm':>13s} {'tepi>4cm':>9s} {'tepi>8cm':>9s} | {'BADAN maks cm':>13s} {'>4cm':>6s} {'>8cm':>6s} | {'KAIN maks cm':>12s} {'>4cm':>6s}")
worst = {}
for f, name in enumerate(POSES, start=1):
    scene.frame_set(f)
    bpy.context.view_layer.update()
    P = positions()
    L1 = np.linalg.norm(P[edges[:, 0]] - P[edges[:, 1]], axis=1)
    d = np.abs(L1 - L0)
    r = L1 / np.maximum(L0, 1e-9)
    db, dc = d[~cloth_edge], d[cloth_edge]
    print(f"{name:16s} {r.min():9.2f} {r.max():10.2f} {d.max()*100:13.1f} {(d>0.04).sum():9d} {(d>0.08).sum():9d} | {db.max()*100:13.1f} {(db>0.04).sum():6d} {(db>0.08).sum():6d} | {dc.max()*100:12.1f} {(dc>0.04).sum():6d}")
    worst[name] = d

# ------------------------------------------------------------------ render
sc = scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light, sh.color_type, sh.show_cavity = "FLAT", "TEXTURE", False
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
sc.world.color = (0.55, 0.57, 0.6)
sc.render.image_settings.file_format = "PNG"
sc.render.resolution_x, sc.render.resolution_y = 480, 640
cam_d = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
cam_d.lens = 45
for o in bpy.data.objects:
    if o.type in {"EMPTY"}:
        o.hide_render = True
arm.hide_render = True

def shoot(path, loc, target):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)

az = math.radians(40)
for f, name in enumerate(POSES, start=1):
    scene.frame_set(f)
    bpy.context.view_layer.update()
    shoot(OUT / f"pose_{f:02d}_{name}_q.png", (-math.sin(az) * 4.4, -math.cos(az) * 4.4, 1.2), (0, 0, 1.0))
    shoot(OUT / f"pose_{f:02d}_{name}_s.png", (4.4, 0, 1.1), (0, 0, 1.0))
scene.frame_set(1)
bpy.ops.wm.save_mainfile()
print("selesai ->", OUT)
