"""Jayadwara2 R0 — render ortografis depan/samping/belakang + 3/4 + close-up kepala (Workbench, tekstur apa adanya).

  blender --background Art/Blender/jayadwara2/jayadwara2_v01_tripo.blend --python Art/Scripts/jayadwara2_02_render_views.py -- [outdir]
Skala sama dengan reference plane Jayadwara (1000 px = 1,9 m) untuk panel ortografis; keluaran PNG per view.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else Path(r"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2")
OUT.mkdir(parents=True, exist_ok=True)
ob = bpy.data.objects["JD2_Source"]
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "FLAT"
sh.color_type = "TEXTURE"
sh.show_cavity = False
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
sc.world.color = (0.55, 0.57, 0.6)
sc.render.film_transparent = False
sc.render.image_settings.file_format = "PNG"

cam_d = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
H = 1.99


def shoot(name, loc, target, ortho=None, fov=None, res=(760, 1200)):
    cam.location = Vector(loc)
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam_d.type, cam_d.ortho_scale = "ORTHO", ortho
    else:
        cam_d.type, cam_d.lens = "PERSP", fov or 60
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = str(OUT / f"jd2_{name}.png")
    bpy.ops.render.render(write_still=True)


zc = H / 2
ortho = 1.2 * 1.9 * 1.0     # 760 px pada 1000 px = 1,9 m -> lebar 0,76*1.9... tinggi 1200 px = 2,28 m
ortho = 2.28
shoot("front", (0, -10, zc + 0.06), (0, 0, zc + 0.06), ortho=ortho)
shoot("side", (10, 0, zc + 0.06), (0, 0, zc + 0.06), ortho=ortho)
shoot("back", (0, 10, zc + 0.06), (0, 0, zc + 0.06), ortho=ortho)
a = math.radians(35)
shoot("q34", (math.sin(a) * -4.5, -math.cos(a) * 4.5, 1.1), (0, 0, 0.95), fov=35, res=(900, 1200))
shoot("head_front", (0, -1.2, 1.78), (0, 0, 1.78), fov=30, res=(900, 900))
shoot("head_q34", (-0.7, -1.0, 1.82), (0, 0, 1.76), fov=30, res=(900, 900))
shoot("head_side", (1.2, 0, 1.78), (0, 0, 1.78), fov=30, res=(900, 900))
print("selesai ->", OUT)
