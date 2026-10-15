"""Tuyul K1 — probe + render close-up tangan KANAN.
  blender --background Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend \
      --python Hermes/Tools/tuyul_09_probe_r.py -- <outdir>
"""
import sys
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
print("== TANGAN KANAN x<-0.18, pita 5mm ==")
for z in np.arange(0.30, 0.13, -0.005):
    m = (co[:, 2] >= z - 0.0025) & (co[:, 2] < z + 0.0025) & (co[:, 0] < -0.18)
    if m.any():
        s = co[m]
        print(f"  z={z:0.3f} x[{s[:,0].min():+.3f},{s[:,0].max():+.3f}] y[{s[:,1].min():+.3f},{s[:,1].max():+.3f}] n{len(s)}")
    else:
        print(f"  z={z:0.3f} -- kosong --")

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


def shoot(tag, loc, target, ortho, res=(900, 900)):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_d.type, cam_d.ortho_scale = "ORTHO", ortho
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = str(OUT / f"rhand_{tag}.png")
    bpy.ops.render.render(write_still=True)


shoot("front", (0, -5, 0.20), (-0.24, 0, 0.20), 0.34)
shoot("side", (-5, 0, 0.20), (-0.24, 0, 0.20), 0.34)
shoot("q34", (-3.5, -3.5, 1.0), (-0.24, 0, 0.20), 0.36)
print("selesai ->", OUT)
