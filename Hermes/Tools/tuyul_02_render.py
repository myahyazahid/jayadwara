"""Tuyul K0 — render ortografis depan/samping/belakang + 3/4 + close-up kepala (Workbench, tekstur apa adanya).

  blender --background Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend \
      --python Hermes/Tools/tuyul_02_render.py -- <outdir>
Keluaran PNG per view. Kanvas 1000 px = 1,0 m (sama untuk semua view).
Salinan dari Art/Scripts/jayadwara2_02_render_views.py; hanya nama objek/tinggi/path yang diubah.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else ROOT / "Hermes" / "Art" / "tuyul" / "Render" / "k0"
if not OUT.is_absolute():
    OUT = ROOT / OUT
OUT.mkdir(parents=True, exist_ok=True)

ob = bpy.data.objects["TY_Source"]
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
H = 1.0


def shoot(name, loc, target, ortho=None, fov=None, res=(900, 1100)):
    cam.location = Vector(loc)
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam_d.type, cam_d.ortho_scale = "ORTHO", ortho
    else:
        cam_d.type, cam_d.lens = "PERSP", fov or 60
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = str(OUT / f"ty_{name}.png")
    bpy.ops.render.render(write_still=True)


zc = H / 2
ortho = 1.3
shoot("front", (0, -10, zc), (0, 0, zc), ortho=ortho)
shoot("side", (10, 0, zc), (0, 0, zc), ortho=ortho)
shoot("back", (0, 10, zc), (0, 0, zc), ortho=ortho)
a = math.radians(35)
shoot("q34", (math.sin(a) * -2.4, -math.cos(a) * 2.4, 0.62), (0, 0, 0.55), fov=40, res=(900, 1100))
shoot("head_front", (0, -0.9, 0.88), (0, 0, 0.88), fov=30, res=(900, 900))
shoot("head_q34", (-0.55, -0.75, 0.92), (0, 0, 0.86), fov=30, res=(900, 900))
shoot("head_side", (0.9, 0, 0.88), (0, 0, 0.88), fov=30, res=(900, 900))
print("selesai ->", OUT)
