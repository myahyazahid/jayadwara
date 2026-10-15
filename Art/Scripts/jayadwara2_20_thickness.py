"""Jayadwara2 R2 — ketebalan lokal mesh (deteksi lembar tipis: sayap kain, kain depan) lewat ray cast ke arah -normal.

  blender --background Art/Blender/jayadwara2/jayadwara2_v01_tripo.blend --python Art/Scripts/jayadwara2_20_thickness.py
Per vertex: jarak ke permukaan berikutnya di sisi dalam (maks 0,15 m); tak kena = volume/terbuka. Lembar tipis = ketebalan < SHEET_MAX.
Hasil: Art/Export/_jd2/_thickness.npz (vertex, thick) + render peta warna depan/samping/belakang (_thick_*.png)."""
import numpy as np
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ob = bpy.data.objects["JD2_Source"]
me = ob.data
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.normal_update()
tree = BVHTree.FromBMesh(bm)
th = np.full(len(bm.verts), 0.15, np.float32)
for v in bm.verts:
    n = v.normal
    for sgn in (-1.0, 1.0):          # dalam (-n) dan luar (+n): lembar dua sisi berarti salah satu hit dekat
        o = v.co + n * (-sgn) * 0.0015 * -1  # sedikit digeser keluar dari permukaan sendiri
        hit = tree.ray_cast(v.co - n * 0.0015 * sgn * -1, n * sgn, 0.15)
        if hit[0] is not None:
            th[v.index] = min(th[v.index], hit[3])
V = np.array([v.co[:] for v in bm.verts], np.float32)
np.savez(r"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2\_thickness.npz", V=V, thick=th)
print("ketebalan: persentil", {p: round(float(np.percentile(th, p)) * 100, 2) for p in (5, 25, 50, 75, 95)}, "cm")
print("vertex < 2 cm:", int((th < 0.02).sum()), "| < 3 cm:", int((th < 0.03).sum()), "| tak kena:", int((th >= 0.15).sum()))
# warna: merah = tipis (<3 cm), biru = tebal
ca = me.color_attributes.get("thick") or me.color_attributes.new("thick", "FLOAT_COLOR", "POINT")
for i, t in enumerate(th):
    k = float(np.clip(t / 0.06, 0, 1))
    ca.data[i].color = (1 - k, 0.15, k, 1)
me.color_attributes.active_color = ca
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading
sh.light, sh.color_type, sh.show_cavity = "FLAT", "VERTEX", False
sc.view_settings.view_transform = "Standard"; sc.world = sc.world or bpy.data.worlds.new("w"); sc.world.color = (0.25, 0.25, 0.25)
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type, cd.ortho_scale = "ORTHO", 2.28
sc.render.resolution_x, sc.render.resolution_y = 760, 1200
for name, loc in (("front", (0, -10, 1.055)), ("side", (10, 0, 1.055)), ("back", (0, 10, 1.055))):
    cam.location = Vector(loc); cam.rotation_euler = (Vector((0, 0, 1.055)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = rf"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2\_thick_{name}.png"; bpy.ops.render.render(write_still=True)
