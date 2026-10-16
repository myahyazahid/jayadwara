"""K5.3 - Render banding LOD0-3 Tuyul (Workbench TEXTURE, ortografis, tanpa lampu).

  blender --background Hermes/Art/tuyul/Blender/tuyul_v08_lod.blend --python Hermes/Tools/tuyul_52_lod_render.py

Keluaran: Hermes/Art/tuyul/Render/k5/lod{n}_{depan,kepala}.png (n = 0..3)
Model 1,0 m; kanvas sama untuk semua LOD supaya bisa dibandingkan piksel-per-piksel.
"""
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
OUT = ROOT / "Hermes" / "Art" / "tuyul" / "Render" / "k5"
OUT.mkdir(parents=True, exist_ok=True)
OBJS = {0: "TY_Source", 1: "TY_Source_LOD1", 2: "TY_Source_LOD2", 3: "TY_Source_LOD3"}

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light, sh.color_type, sh.show_cavity = "FLAT", "TEXTURE", False
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
sc.world.color = (0.78, 0.79, 0.80)
for o in bpy.data.objects:
    if o.type in {"ARMATURE", "EMPTY"}:
        o.hide_render = True

cd = bpy.data.cameras.new("c_k5")
cam = bpy.data.objects.new("c_k5", cd)
sc.collection.objects.link(cam)
sc.camera = cam
cd.type = "ORTHO"

VIEWS = (("depan", (0.0, -3.0, 0.50), 1.20, (600, 900)),
         ("kepala", (0.0, -3.0, 0.90), 0.45, (800, 800)))

tris = lambda me: sum(len(p.vertices) - 2 for p in me.polygons)
for n, name in OBJS.items():
    ob = bpy.data.objects[name]
    for k, o in OBJS.items():
        bpy.data.objects[o].hide_render = (k != n)
    t = tris(ob.data)
    for vname, loc, orth, res in VIEWS:
        cd.ortho_scale = orth
        cam.location = Vector(loc)
        cam.rotation_euler = (1.5707963, 0.0, 0.0)
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.filepath = str(OUT / f"lod{n}_{vname}.png")
        bpy.ops.render.render(write_still=True)
    print(f"LOD{n} ({name}): {t} tris -> lod{n}_depan.png, lod{n}_kepala.png")
