"""Tuyul K1 — render close-up ketat tangan KIRI (hitung jari).
  blender --background Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend \
      --python Hermes/Tools/tuyul_16_hand_zoom.py -- <outdir>
"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else ROOT / "Hermes" / "Art" / "tuyul" / "Render" / "k1"
if not OUT.is_absolute():
    OUT = ROOT / OUT
OUT.mkdir(parents=True, exist_ok=True)

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"
sh.color_type = "TEXTURE"
sh.show_shadows = False
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
sc.world.color = (0.5, 0.52, 0.56)
cam_d = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam


def shoot(tag, loc, target, ortho, res=(1100, 1100)):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_d.type, cam_d.ortho_scale = "ORTHO", ortho
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = str(OUT / f"hz_{tag}.png")
    bpy.ops.render.render(write_still=True)


T = (0.235, -0.04, 0.19)
shoot("side", (5, -0.04, 0.19), T, 0.17)
shoot("front", (0.235, -5, 0.19), T, 0.17)
shoot("back", (0.235, 5, 0.19), T, 0.17)
print("selesai ->", OUT)
