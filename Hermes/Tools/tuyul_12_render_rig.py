"""Tuyul K1 — render tulang tembus pandang (bukti visual sendi di dalam mesh).

  blender --background Hermes/Art/tuyul/Blender/tuyul_v02_skeleton.blend \
      --python Hermes/Tools/tuyul_12_render_rig.py -- <outdir>
Dua lintasan: (1) mesh opaque bertekstur; (2) penanda sendi (bola: hijau=di dalam, merah=di luar)
+ batang tulang (biru) di latar transparan. Overlay via ffmpeg (lihat catatan di laporan).
"""
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else ROOT / "Hermes" / "Art" / "tuyul" / "Render" / "k1"
if not OUT.is_absolute():
    OUT = ROOT / OUT
OUT.mkdir(parents=True, exist_ok=True)

ob = bpy.data.objects["TY_Source"]
arm = bpy.data.objects["TY_Armature"]
dg = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(ob, dg)

DIRS = [Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0)),
        Vector((0, 0, -1)), Vector((-1, 0, 0)), Vector((0, -1, 0))]
JIT = [Vector((0.0131, 0.0073, 0.0)), Vector((0.0, 0.0117, 0.0059)), Vector((0.0091, 0.0, 0.0137))]


def _hits(o, d):
    n, p = 0, o.copy()
    for _ in range(128):
        loc, nor, idx, dist = bvh.ray_cast(p, d)
        if loc is None:
            break
        n += 1
        p = loc + d * 1e-5
    return n


def inside(p):
    par = sum(1 for i, d in enumerate(DIRS) if _hits(p, (d + JIT[i % 3]).normalized()) % 2 == 1) >= 4
    loc, nor, idx, dist = bvh.find_nearest(p, 3.0)
    nor_ok = loc is not None and (p - loc).dot(nor) < 0
    return par and nor_ok


GREEN, RED, BLUE = (0.1, 1.0, 0.2, 1), (1.0, 0.1, 0.1, 1), (0.2, 0.5, 1.0, 1)
sc = bpy.context.scene
viz = bpy.data.collections.new("VIZ_K1")
sc.collection.children.link(viz)


def _move(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    viz.objects.link(o)


def ball(p, color, r=0.006):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=p, segments=10, ring_count=6)
    o = bpy.context.active_object
    o.color = color
    _move(o)


def rod(p0, p1, color, r=0.0025):
    d = p1 - p0
    if d.length < 1e-6:
        return
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, location=(p0 + p1) / 2)
    o = bpy.context.active_object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    o.color = color
    _move(o)


nbad = 0
for b in arm.data.bones:
    if not b.use_deform or b.name == "root":
        continue
    h, t = b.head_local, b.tail_local
    rod(h, t, BLUE)
    for p in (h, t):
        ok = inside(p)
        ball(p, GREEN if ok else RED)
        nbad += 0 if ok else 1
print(f"penanda sendi: {nbad} titik merah (di luar) dari total")

cam_d = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
sc.render.engine = "BLENDER_WORKBENCH"
sc.view_settings.view_transform = "Standard"
sh = sc.display.shading
sh.light = "STUDIO"
sh.show_shadows = False
sh.show_cavity = False


def shoot(tag, loc, target, ortho, res=(900, 900)):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_d.type, cam_d.ortho_scale = "ORTHO", ortho
    sc.render.resolution_x, sc.render.resolution_y = res
    # pass 1: mesh
    ob.hide_render = False
    viz.hide_render = True
    sh.color_type = "TEXTURE"
    sc.render.film_transparent = False
    sc.render.filepath = str(OUT / f"rig_{tag}_mesh.png")
    bpy.ops.render.render(write_still=True)
    # pass 2: tulang
    ob.hide_render = True
    viz.hide_render = False
    sh.color_type = "OBJECT"
    sc.render.film_transparent = True
    sc.render.filepath = str(OUT / f"rig_{tag}_bones.png")
    bpy.ops.render.render(write_still=True)


shoot("front", (0, -5, 0.5), (0, 0, 0.5), 1.15)
shoot("side", (5, 0, 0.5), (0, 0, 0.5), 1.15)
shoot("q34", (-3.5, -3.5, 1.4), (0, 0, 0.5), 1.2)
shoot("hand", (0.2, -5, 0.19), (0.23, 0, 0.19), 0.34, res=(900, 900))
print("selesai ->", OUT)
