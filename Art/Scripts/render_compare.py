"""Render ortografis depan/samping/belakang dengan skala SAMA dengan reference plane (760x1200, 1000 px = 1,9 m,
telapak kaki di y=1100), untuk dibandingkan berdampingan dengan konsep (compare_sheet.py).

Jalankan di Blender. Variabel opsional: RENDER_DIR (folder keluaran), VIEWS (front/side/back + close-up head34/belt/shoulder/boot/torso).
Scene dikembalikan seperti semula (kamera/lampu sementara dihapus, engine & setelan render dipulihkan).
"""
import math
import os

import bpy
from mathutils import Euler

OUT = globals().get("RENDER_DIR") or r"C:\repository\unreal_engine\jayadwara\Art\Export\_compare"
VIEWS = globals().get("VIEWS") or ["front", "side", "back", "head34"]       # + close-up opsional: belt, shoulder, boot, torso
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
r = sc.render
saved = dict(engine=r.engine, x=r.resolution_x, y=r.resolution_y, pct=r.resolution_percentage, film=r.film_transparent,
             cam=sc.camera, path=r.filepath, fmt=r.image_settings.file_format, mode=r.image_settings.color_mode)

# sembunyikan reference plane, landmark, socket, armature dari render
hidden = []
for o in bpy.data.objects:
    if o.type in {"EMPTY", "ARMATURE"} and not o.hide_render:
        o.hide_render = True
        hidden.append(o)

cam_data = bpy.data.cameras.new("_cmp_cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.28
cam = bpy.data.objects.new("_cmp_cam", cam_data)
sc.collection.objects.link(cam)
lights = []
for name, rot, energy in (("_cmp_key", (50, 0, -35), 3.2), ("_cmp_fill", (60, 0, 145), 1.0), ("_cmp_rim", (70, 0, 200), 1.8)):
    ld = bpy.data.lights.new(name, "SUN")
    ld.energy = energy
    lo = bpy.data.objects.new(name, ld)
    lo.rotation_euler = Euler(tuple(math.radians(a) for a in rot))
    sc.collection.objects.link(lo)
    lights.append(lo)

r.engine = "BLENDER_EEVEE"
r.resolution_x, r.resolution_y, r.resolution_percentage = 760, 1200, 100
r.film_transparent = True
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGBA"
sc.camera = cam
# langit terang sementara: permukaan metalik (emas) memantulkan lingkungan; dunia gelap membuat emas tampak zaitun
world_prev = sc.world
wtmp = bpy.data.worlds.new("_cmp_world")
wtmp.use_nodes = True
bg = next(n for n in wtmp.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (0.75, 0.78, 0.82, 1.0)
bg.inputs[1].default_value = 0.40
sc.world = wtmp
ZC = 1.14 - 0.19                      # tengah kanvas (tinggi 2,28 m; telapak kaki 0,19 m di atas tepi bawah)
POS = {"front": ((0, -6, ZC), (90, 0, 0)), "side": ((6, 0, ZC), (90, 0, 90)), "back": ((0, 6, ZC), (90, 0, 180))}
# close-up perspektif 3/4 (untuk dibanding panel detail konsep): nama -> (target, arah kamera, jarak)
CLOSE = {"head34": ((0, -0.02, 1.83), (0.32, -0.95, 0.02), 0.95),
         "belt": ((0, -0.06, 1.05), (0.25, -0.97, 0.10), 1.05),
         "shoulder": ((0.22, -0.02, 1.50), (0.50, -0.82, 0.28), 1.30),
         "boot": ((0.25, -0.12, 0.13), (0.45, -0.85, 0.35), 1.05),
         "torso": ((0, -0.02, 1.45), (0.35, -0.94, 0.12), 2.30)}
for v in VIEWS:
    if v in CLOSE:
        from mathutils import Vector
        cam_data.type, cam_data.lens = "PERSP", 85
        r.resolution_x = r.resolution_y = 900
        tgt, dv, dist = CLOSE[v]
        tgt = Vector(tgt)
        cam.location = tgt + Vector(dv).normalized() * dist
        cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    else:
        cam_data.type = "ORTHO"
        r.resolution_x, r.resolution_y = 760, 1200
        loc, rot = POS[v]
        cam.location = loc
        cam.rotation_euler = Euler(tuple(math.radians(a) for a in rot))
    r.filepath = os.path.join(OUT, f"render_{v}.png")
    bpy.ops.render.render(write_still=True)
    print("render:", r.filepath)

# pulihkan
sc.world = world_prev
bpy.data.worlds.remove(wtmp)
for o in hidden:
    o.hide_render = False
for o in [cam] + lights:
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.cameras.remove(cam_data)
for l in list(bpy.data.lights):
    if l.name.startswith("_cmp_") and l.users == 0:
        bpy.data.lights.remove(l)
r.engine, r.resolution_x, r.resolution_y, r.resolution_percentage = saved["engine"], saved["x"], saved["y"], saved["pct"]
r.film_transparent, sc.camera, r.filepath = saved["film"], saved["cam"], saved["path"]
r.image_settings.file_format, r.image_settings.color_mode = saved["fmt"], saved["mode"]
