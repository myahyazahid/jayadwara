"""Jubah Jayadwara2 J0 — render badan + jubah (depan/samping/belakang/3/4) dengan titik kait & garis bantu.

  blender --background Art/Blender/jayadwara2/jayadwara2_cape_v00_intake.blend --python Art/Scripts/jayadwara2_cape_02_render.py -- \
      [outdir] [--cape JD2_Cape_Source] [--no-cape] [--tag v00]
Panel ortografis sama skalanya dengan render R0 (tinggi 1200 px = 2,28 m). Titik kait = bola kuning,
garis dagu (batas kerah K9) = garis biru, garis mata kaki = garis hijau. Keluaran: jd2c_<tag>_<view>.png
"""
import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("outdir", nargs="?", default=r"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2c")
ap.add_argument("--cape", default="JD2_Cape_Source")
ap.add_argument("--tag", default="v00")
ap.add_argument("--no-cape", action="store_true")
args = ap.parse_args(argv)
OUT, CAPE, TAG = Path(args.outdir), args.cape, args.tag
OUT.mkdir(parents=True, exist_ok=True)

sc = bpy.context.scene
for o in bpy.data.objects:
    o.hide_render = True
show = [bpy.data.objects["JD2_Body"]]
if not args.no_cape and CAPE in bpy.data.objects:
    show.append(bpy.data.objects[CAPE])
for o in show:
    o.hide_render = False
    for c in o.users_collection:
        c.hide_render = False

# penanda: bola di titik kait, batang tipis di garis dagu & mata kaki
mk = bpy.data.materials.new("jd2c_marker")
mk.diffuse_color = (1.0, 0.85, 0.1, 1)
ml = bpy.data.materials.new("jd2c_line_chin")
ml.diffuse_color = (0.1, 0.5, 1.0, 1)
mh = bpy.data.materials.new("jd2c_line_hem")
mh.diffuse_color = (0.1, 0.9, 0.3, 1)


def marker(loc, r, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=16, ring_count=8)
    o = bpy.context.active_object
    o.scale = scale
    o.data.materials.append(mat)
    return o


chin_z = 1.61
for o in [o for o in bpy.data.objects if o.name.startswith("JD2C_ANCHOR_")]:
    marker(o.location, 0.018, mk)
    if o.name.endswith("chin"):
        chin_z = o.location.z
lines = [marker((0, 0, chin_z), 1.0, ml, scale=(0.9, 0.9, 0.0025)),
         marker((0, 0, 0.10), 1.0, mh, scale=(0.9, 0.9, 0.0025))]

sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"
sh.color_type = "TEXTURE"
sh.show_cavity = False
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
sc.world.color = (0.55, 0.57, 0.6)
sc.render.film_transparent = False
sc.render.image_settings.file_format = "PNG"

cam_d = bpy.data.cameras.new("cam_jd2c")
cam = bpy.data.objects.new("cam_jd2c", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
zc = 1.99 / 2 + 0.06


def shoot(name, loc, target, ortho=None, fov=None, res=(760, 1200)):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam_d.type, cam_d.ortho_scale = "ORTHO", ortho
    else:
        cam_d.type, cam_d.lens = "PERSP", fov or 60
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = str(OUT / f"jd2c_{TAG}_{name}.png")
    bpy.ops.render.render(write_still=True)


shoot("front", (0, -10, zc), (0, 0, zc), ortho=2.28)
shoot("side", (10, 0, zc), (0, 0, zc), ortho=2.28)
shoot("back", (0, 10, zc), (0, 0, zc), ortho=2.28)
for o in lines:                     # garis bantu hanya untuk panel ortografis
    o.hide_render = True
a = math.radians(145)
shoot("q34back", (math.sin(a) * -4.5, -math.cos(a) * 4.5, 1.2), (0, 0, 0.95), fov=35, res=(900, 1200))
a = math.radians(35)
shoot("q34", (math.sin(a) * -4.5, -math.cos(a) * 4.5, 1.2), (0, 0, 0.95), fov=35, res=(900, 1200))
shoot("collar", (0.9, 0.9, 1.75), (0, 0.02, 1.5), fov=35, res=(900, 900))
print("selesai ->", OUT)
