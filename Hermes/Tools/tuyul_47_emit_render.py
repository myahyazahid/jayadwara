"""K4.5 - Render pendar: Cycles, dunia hampir hitam, tanpa lampu -> hanya emissive yang terlihat.

  blender --background <v07 blend> --python Hermes/Tools/tuyul_47_emit_render.py -- <outdir>
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else ROOT / "Hermes" / "Art" / "tuyul" / "Render" / "k4"
if not OUT.is_absolute():
    OUT = ROOT / OUT
OUT.mkdir(parents=True, exist_ok=True)

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 24
sc.cycles.use_denoising = True
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.file_format = "PNG"
w = bpy.data.worlds.new("gelap")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.012, 0.014, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sc.world = w

cam_d = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam


def shoot(name, loc, target, fov=40, res=(760, 950)):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_d.type, cam_d.lens = "PERSP", fov
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = str(OUT / f"glow_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", name)


a = math.radians(35)
shoot("depan", (0, -2.0, 0.55), (0, 0, 0.50), 40)
shoot("q34", (math.sin(a) * -2.0, -math.cos(a) * 2.0, 0.70), (0, 0, 0.55), 40)
shoot("kepala", (0, -0.75, 0.90), (0, 0, 0.88), 30, (760, 760))
shoot("ubun", (-0.5, -0.5, 1.45), (0, 0, 0.93), 30, (760, 760))
print("selesai ->", OUT)
