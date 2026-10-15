"""K2 — zoom ketat punggung/bahu/perut untuk melokalisasi unsur gore.

  blender --background Hermes/Art/tuyul/Blender/tuyul_v03_clean.blend \
      --python Hermes/Tools/tuyul_23_back_zoom.py -- <outdir>
"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else ROOT / "Hermes" / "Art" / "tuyul" / "Render" / "k2"
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


def shoot(tag, loc, target, ortho, res=(1200, 1200)):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_d.type, cam_d.ortho_scale = "ORTHO", ortho
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = str(OUT / f"zz_{tag}.png")
    bpy.ops.render.render(write_still=True)


# punggung = +Y. Zoom ketat per area.
shoot("back_sh", (0, 5, 0.80), (0, 0.06, 0.80), 0.30)      # bahu/punggung atas
shoot("back_mid", (0, 5, 0.62), (0, 0.10, 0.62), 0.30)     # punggung tengah
shoot("back_low", (0, 5, 0.42), (0, 0.08, 0.42), 0.30)     # punggung bawah
shoot("back_l_q34", (2.0, 4.5, 0.80), (0.08, 0.06, 0.78), 0.28)
shoot("back_r_q34", (-2.0, 4.5, 0.80), (-0.08, 0.06, 0.78), 0.28)
shoot("belly", (0, -5, 0.45), (0, -0.14, 0.45), 0.30)
print("selesai ->", OUT)
