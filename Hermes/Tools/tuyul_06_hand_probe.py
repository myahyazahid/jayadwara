"""Tuyul K1 — periksa geometri tangan/kaki + render close-up untuk menempatkan sendi.
  blender --background Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend \
      --python Hermes/Tools/tuyul_06_hand_probe.py -- <outdir>
"""
import sys
import math
from pathlib import Path

import numpy as np
import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else ROOT / "Hermes" / "Art" / "tuyul" / "Render" / "k1"
if not OUT.is_absolute():
    OUT = ROOT / OUT
OUT.mkdir(parents=True, exist_ok=True)

ob = bpy.data.objects["TY_Source"]
co = np.array([v.co[:] for v in ob.data.vertices])

print("== REGION TANGAN KIRI (x>0.15, z<0.32) per pita z 2cm ==")
for z in np.arange(0.30, 0.08, -0.02):
    m = (co[:, 2] >= z - 0.01) & (co[:, 2] < z + 0.01) & (co[:, 0] > 0.15)
    if m.any():
        s = co[m]
        print(f"  z={z:0.2f} x[{s[:,0].min():+.3f},{s[:,0].max():+.3f}] y[{s[:,1].min():+.3f},{s[:,1].max():+.3f}] n{len(s)}")
print("== REGION KAKI KIRI (0.02<x<0.20, z<0.25) ==")
for z in np.arange(0.24, 0.0, -0.02):
    m = (co[:, 2] >= z - 0.01) & (co[:, 2] < z + 0.01) & (co[:, 0] > 0.02) & (co[:, 0] < 0.20)
    if m.any():
        s = co[m]
        print(f"  z={z:0.2f} x[{s[:,0].min():+.3f},{s[:,0].max():+.3f}] y[{s[:,1].min():+.3f},{s[:,1].max():+.3f}] n{len(s)}")

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "FLAT"
sh.color_type = "TEXTURE"
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
sc.world.color = (0.55, 0.57, 0.6)
cam_d = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam


def shoot(name, loc, target, ortho, res=(800, 800)):
    cam.location = Vector(loc)
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam_d.type, cam_d.ortho_scale = "ORTHO", ortho
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = str(OUT / f"ty_{name}.png")
    bpy.ops.render.render(write_still=True)


# close-up tangan kiri (x~0.24, z~0.2)
shoot("hand_front", (0, -5, 0.20), (0.24, 0, 0.20), 0.36)
shoot("hand_side", (5, 0, 0.20), (0.24, 0, 0.20), 0.36)
shoot("hand_top", (0.24, 0, 5), (0.24, 0, 0.20), 0.36, res=(800, 800))
# close-up kaki kiri (x~0.12, z~0.08)
shoot("leg_front", (0, -5, 0.12), (0.12, 0, 0.12), 0.42)
shoot("leg_side", (5, 0, 0.12), (0.12, 0, 0.12), 0.42)
print("selesai ->", OUT)
