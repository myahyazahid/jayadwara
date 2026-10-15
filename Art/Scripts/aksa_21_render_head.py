"""Aksa Iterasi 2 — render kepala (depan, samping, 3/4) berbingkai sama dengan Art/Reference/ak_head_{front,side}.png.

Headless: blender --background Art/Blender/aksa/aksa_v02_head.blend --python Art/Scripts/aksa_21_render_head.py -- <outdir>
Output: <outdir>/head_front.png (642x970), head_side.png (610x900), head_q34.png (900x1100, perspektif, miring kiri-atas).
Skala referensi: 1 px = 0,78 mm; front: tengah (x=0, z=1,625), side: tengah (y=-0,0177, z=1,642). Eevee, 2 sun + dunia abu.
Lanjut: python -I Art/Scripts/aksa_21_head_sheet.py <outdir>
"""
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else r"C:\repository\unreal_engine\jayadwara\Art\Export"
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
try:
    sc.render.engine = "BLENDER_EEVEE"
except TypeError as e:
    print("engine:", e)
    raise
sc.render.film_transparent = False
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.render.image_settings.file_format = "PNG"
sc.render.resolution_percentage = 100
try:
    sc.eevee.taa_render_samples = 32
except Exception:  # noqa: BLE001
    pass

for ob in bpy.data.objects:
    if ob.name.startswith("AK_REF") or ob.name.startswith("AK_LM") or ob.type in {"EMPTY", "ARMATURE"}:
        ob.hide_render = True

world = bpy.data.worlds.new("_head_world")
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.62, 0.64, 0.68, 1)
bg.inputs["Strength"].default_value = 0.9
sc.world = world


def sun(name, rot, energy):
    d = bpy.data.lights.new(name, "SUN")
    d.energy = energy
    d.angle = math.radians(25)
    o = bpy.data.objects.new(name, d)
    sc.collection.objects.link(o)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    return o


sun("key", (55, 0, -35), 3.2)          # dari depan-kiri-atas
sun("fill", (70, 0, 55), 1.1)          # dari depan-kanan, lebih lembut
sun("rim", (120, 0, 160), 1.4)         # dari belakang untuk siluet rambut

cam_d = bpy.data.cameras.new("_headcam")
cam = bpy.data.objects.new("_headcam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
MM = 0.00078


def shoot(name, w, h):
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


# depan
cam_d.type = "ORTHO"
cam_d.ortho_scale = 485 * MM
cam_d.clip_start, cam_d.clip_end = 0.1, 10
cam.location = (0.0, -1.0, 1.625)
cam.rotation_euler = (math.radians(90), 0, 0)
shoot("head_front", 642, 970)
# samping (hadap kiri gambar)
cam_d.ortho_scale = 450 * MM
cam.location = (1.0, -0.0177, 1.642)
cam.rotation_euler = (math.radians(90), 0, math.radians(90))
shoot("head_side", 610, 900)
# 3/4 perspektif
cam_d.type = "PERSP"
cam_d.lens = 85
tgt = Vector((0.0, -0.02, 1.655))
cam.location = (0.42, -0.62, 1.74)
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
shoot("head_q34", 900, 1100)
print("render kepala selesai ->", OUT)
