#!/usr/bin/env python3
"""M2 — Medan + tangga Ep01_LawangSapta di Blender (headless).

Bangun:
1. Mesh medan SM_Ep01_Medan: grid x -340..460, y -420..280, sel 2 m -> 401 x 351 = 140.751 vertex,
   tinggi = elev(x,y). Tiap muka diberi slot material menurut aturan material_zona (di titik tengah muka,
   urutan dari atas; yang pertama cocok menang). Slot: Air, Galian, Jalan, Plato, Sawah, Desa, Hutan.
2. Mesh SM_Ep01_Tangga: 28 balok dari (0,87.5,28) ke (0,112.5,35), lebar 10 m, origin (0,0,0).

Simpan .blend, ekspor 2 FBX (meter), render 2 PNG (Eevee): M2_atas (orto dari atas, utara di atas)
dan M2_miring (perspektif dari selatan-barat daya, ~35 derajat ke bawah).

Jalankan (dari WORKTREE):
  blender --background --factory-startup --python Hermes/Tools/maps_ep1_20_medan_blender.py -- --out Hermes/Art/maps_ep1
"""
import sys
import os
import json
import math

import bpy
import bmesh
from mathutils import Vector

# ------------------------------------------------------------------ argumen
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
out_dir = None
for i, a in enumerate(argv):
    if a == "--out" and i + 1 < len(argv):
        out_dir = argv[i + 1]

HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = os.path.abspath(os.path.join(HERE, "..", ".."))
if out_dir is None:
    out_dir = os.path.join(WORKTREE, "Hermes", "Art", "maps_ep1")
out_dir = os.path.abspath(out_dir)
exp_dir = os.path.join(out_dir, "Export")
ren_dir = os.path.join(out_dir, "Render")
for d in (out_dir, exp_dir, ren_dir):
    os.makedirs(d, exist_ok=True)

sys.path.insert(0, os.path.join(WORKTREE, "Art", "Level"))
import ep01_medan as M  # noqa: E402  (elev, TITIK_UJI, JALAN_AKSES, JALAN_PROYEK, dist_poly)

with open(os.path.join(WORKTREE, "Art", "Level", "ep01_layout_v01.json"), encoding="utf-8") as f:
    DATA = json.load(f)
MEDAN = DATA["medan"]
X0, X1 = MEDAN["x_min"], MEDAN["x_max"]
Y0, Y1 = MEDAN["y_min"], MEDAN["y_max"]
SEL = MEDAN["sel"]
NX = int(round((X1 - X0) / SEL)) + 1
NY = int(round((Y1 - Y0) / SEL)) + 1

print("[M2] grid medan: x %g..%g, y %g..%g, sel %g -> %d x %d = %d vertex"
      % (X0, X1, Y0, Y1, SEL, NX, NY, NX * NY))

# ------------------------------------------------------------------ warna
def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


# warna sRGB dari tabel MI (instruksi §2)
WARNA = {
    "Air":     (91, 143, 176),
    "Galian":  (181, 88, 47),
    "Jalan":   (150, 120, 90),
    "Plato":   (128, 132, 118),
    "Sawah":   (126, 162, 89),
    "Desa":    (199, 166, 121),
    "Hutan":   (79, 107, 74),
    "Andesit": (108, 120, 113),
}
SLOT = ["Air", "Galian", "Jalan", "Plato", "Sawah", "Desa", "Hutan"]


def make_mat(name, srgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    r, g, b = [srgb_to_linear(v) for v in srgb]
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (r, g, b, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.4
    m.diffuse_color = (r, g, b, 1.0)
    return m


MAT = {name: make_mat(name, WARNA[name]) for name in WARNA}

# ------------------------------------------------------------------ aturan zona
def zona(x, y, z):
    if z < -1.0:
        return "Air"
    if (x / 70.0) ** 2 + (y / 60.0) ** 2 < 1.0:
        return "Galian"
    if abs(x) < 25.0 and -110.0 <= y <= -27.0:
        return "Galian"
    d_proyek, _ = M.dist_poly(x, y, M.JALAN_PROYEK)
    if d_proyek <= 4.0:
        return "Jalan"
    if x > 120.0:
        d_akses, _ = M.dist_poly(x, y, M.JALAN_AKSES)
        if d_akses <= 4.0:
            return "Jalan"
    if -60.0 <= x <= 60.0 and 120.0 <= y <= 220.0:
        return "Plato"
    if -90.0 <= x <= 210.0 and -270.0 <= y <= -110.0:
        return "Sawah"
    if -260.0 <= x <= -80.0 and -325.0 <= y <= -200.0:
        return "Desa"
    return "Hutan"


# ------------------------------------------------------------------ scene bersih
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.render.image_settings.file_format = "PNG"
try:
    scene.view_settings.view_transform = "Standard"
except Exception as e:
    print("[M2] view_transform Standard gagal:", e)
try:
    scene.eevee.taa_render_samples = 32
except Exception:
    pass

world = bpy.data.worlds.new("W_M2")
world.use_nodes = True
bgnode = world.node_tree.nodes.get("Background")
if bgnode:
    bgnode.inputs[0].default_value = (0.5, 0.5, 0.5, 1.0)
    bgnode.inputs[1].default_value = 0.15
scene.world = world

# ------------------------------------------------------------------ mesh medan
Z = [[0.0] * NX for _ in range(NY)]
verts = []
for j in range(NY):
    y = Y0 + j * SEL
    for i in range(NX):
        x = X0 + i * SEL
        z = M.elev(x, y)
        Z[j][i] = z
        verts.append((x, y, z))

faces = []
for j in range(NY - 1):
    for i in range(NX - 1):
        a = j * NX + i
        b = a + 1
        c = (j + 1) * NX + i + 1
        d = (j + 1) * NX + i
        faces.append((a, b, c, d))

medan_mesh = bpy.data.meshes.new("SM_Ep01_Medan")
medan_mesh.from_pydata(verts, [], faces)
medan_mesh.update()
for name in SLOT:
    medan_mesh.materials.append(MAT[name])
slot_index = {name: k for k, name in enumerate(SLOT)}

zona_count = {name: 0 for name in SLOT}
for j in range(NY - 1):
    row = j * (NX - 1)
    for i in range(NX - 1):
        cx = X0 + (i + 0.5) * SEL
        cy = Y0 + (j + 0.5) * SEL
        cz = 0.25 * (Z[j][i] + Z[j][i + 1] + Z[j + 1][i] + Z[j + 1][i + 1])
        zn = zona(cx, cy, cz)
        medan_mesh.polygons[row + i].material_index = slot_index[zn]
        zona_count[zn] += 1
medan_mesh.validate()
medan_obj = bpy.data.objects.new("SM_Ep01_Medan", medan_mesh)
bpy.context.collection.objects.link(medan_obj)

n_vertex = len(medan_mesh.vertices)
n_face = len(medan_mesh.polygons)
print("[M2] mesh medan: %d vertex, %d muka" % (n_vertex, n_face))
print("[M2] jumlah muka per zona:", {k: zona_count[k] for k in SLOT})

# ------------------------------------------------------------------ mesh tangga
n_step = 28
ys, ye = 87.5, 112.5
zs, ze = 28.0, 35.0
dy = (ye - ys) / n_step
dz = (ze - zs) / n_step
lebar = 10.0
bm = bmesh.new()
for k in range(n_step):
    y0 = ys + k * dy
    y1 = y0 + dy
    ztop = zs + (k + 1) * dz
    x0b, x1b = -lebar / 2.0, lebar / 2.0
    z0b = zs
    vs = [bm.verts.new((x0b, y0, z0b)), bm.verts.new((x1b, y0, z0b)),
          bm.verts.new((x1b, y1, z0b)), bm.verts.new((x0b, y1, z0b)),
          bm.verts.new((x0b, y0, ztop)), bm.verts.new((x1b, y0, ztop)),
          bm.verts.new((x1b, y1, ztop)), bm.verts.new((x0b, y1, ztop))]
    for quad in ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
                 (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[q] for q in quad])
bm.normal_update()
tangga_mesh = bpy.data.meshes.new("SM_Ep01_Tangga")
bm.to_mesh(tangga_mesh)
bm.free()
tangga_mesh.materials.append(MAT["Andesit"])
tangga_obj = bpy.data.objects.new("SM_Ep01_Tangga", tangga_mesh)
bpy.context.collection.objects.link(tangga_obj)
print("[M2] mesh tangga: %d vertex, %d muka (%d balok)" %
      (len(tangga_mesh.vertices), len(tangga_mesh.polygons), n_step))

# ------------------------------------------------------------------ kamera
cam_atas_data = bpy.data.cameras.new("Cam_Atas")
cam_atas_data.type = "ORTHO"
cam_atas_data.ortho_scale = 1300.0
cam_atas_data.clip_start = 1.0
cam_atas_data.clip_end = 6000.0
cam_atas = bpy.data.objects.new("C_M2_Atas", cam_atas_data)
cam_atas.location = (60.0, -70.0, 500.0)
cam_atas.rotation_euler = (0.0, 0.0, 0.0)  # lihat -Z, atas = +Y (utara di atas)
bpy.context.collection.objects.link(cam_atas)

cam_mir_data = bpy.data.cameras.new("Cam_Miring")
cam_mir_data.type = "PERSP"
cam_mir_data.lens = 42.0
cam_mir_data.clip_start = 1.0
cam_mir_data.clip_end = 30000.0
cam_mir = bpy.data.objects.new("C_M2_Miring", cam_mir_data)
az = math.radians(210.0)          # selatan-barat daya
D = 1150.0
h = D * math.tan(math.radians(35.0))
cam_mir.location = Vector((60.0 + math.cos(az) * D, -70.0 + math.sin(az) * D, h))
arah = Vector((60.0, -70.0, 5.0)) - cam_mir.location
cam_mir.rotation_euler = arah.to_track_quat("-Z", "Y").to_euler()
bpy.context.collection.objects.link(cam_mir)
print("[M2] kamera miring di (%.0f, %.0f, %.0f), elevasi 35 deg, lens %.0f" %
      (cam_mir.location.x, cam_mir.location.y, cam_mir.location.z, cam_mir_data.lens))

# ------------------------------------------------------------------ matahari
sun_data = bpy.data.lights.new("Sun_M2", type="SUN")
sun_data.energy = 0.6
sun = bpy.data.objects.new("Sun_M2", sun_data)
sun.rotation_euler = (0.0, 0.0, 0.0)
bpy.context.collection.objects.link(sun)

# ------------------------------------------------------------------ render
def render_ke(cam, sun_rot_deg, path):
    scene.camera = cam
    sun.rotation_euler = tuple(math.radians(a) for a in sun_rot_deg)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("[M2] render ->", path)


render_ke(cam_atas, (0.0, 0.0, 0.0), os.path.join(ren_dir, "M2_atas.png"))
render_ke(cam_mir, (52.0, 0.0, -38.0), os.path.join(ren_dir, "M2_miring.png"))

# ------------------------------------------------------------------ simpan .blend
blend_path = os.path.join(out_dir, "maps_ep1_medan_v01.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("[M2] simpan blend ->", blend_path)

# ------------------------------------------------------------------ ekspor FBX
def export_fbx(obj, path):
    for o in bpy.data.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    kwargs = dict(filepath=path, use_selection=True, object_types={"MESH"},
                  global_scale=1.0, apply_unit_scale=True,
                  axis_forward="X", axis_up="Z", mesh_smooth_type="FACE")
    try:
        bpy.ops.export_scene.fbx(**kwargs)
    except TypeError as e:
        print("[M2] export kwargs penuh gagal (%s), coba minimal" % e)
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"})
    print("[M2] ekspor FBX ->", path)


export_fbx(medan_obj, os.path.join(exp_dir, "SM_Ep01_Medan.fbx"))
export_fbx(tangga_obj, os.path.join(exp_dir, "SM_Ep01_Tangga.fbx"))

# ------------------------------------------------------------------ uji 12 titik
def mesh_z(x, y):
    fx = (x - X0) / SEL
    fy = (y - Y0) / SEL
    i0 = max(0, min(NX - 2, int(math.floor(fx))))
    j0 = max(0, min(NY - 2, int(math.floor(fy))))
    tx = fx - i0
    ty = fy - j0
    z00 = Z[j0][i0]
    z10 = Z[j0][i0 + 1]
    z01 = Z[j0 + 1][i0]
    z11 = Z[j0 + 1][i0 + 1]
    return (z00 * (1 - tx) + z10 * tx) * (1 - ty) + (z01 * (1 - tx) + z11 * tx) * ty


def nearest_z(x, y):
    i = max(0, min(NX - 1, int(round((x - X0) / SEL))))
    j = max(0, min(NY - 1, int(round((y - Y0) / SEL))))
    return Z[j][i]


print("\n[M2] UJI 12 TITIK: tinggi mesh vs elev")
print("%-26s %8s %10s %8s %10s %8s" % ("titik", "elev", "mesh_bil", "d_bil", "mesh_near", "d_near"))
max_d = 0.0
max_d_near = 0.0
for label, ((x, y), tgt, tol) in M.TITIK_UJI.items():
    e = M.elev(x, y)
    mb = mesh_z(x, y)
    mn = nearest_z(x, y)
    db = mb - e
    dn = mn - e
    max_d = max(max_d, abs(db))
    max_d_near = max(max_d_near, abs(dn))
    print("%-26s %8.2f %10.2f %8.3f %10.2f %8.3f" % (label, e, mb, db, mn, dn))
print("[M2] max |mesh_bilinear - elev| = %.3f m ; max |mesh_nearest - elev| = %.3f m" % (max_d, max_d_near))

# ------------------------------------------------------------------ verdict
print("\n[M2] vertex medan = %d (target 140751): %s" % (n_vertex, "OK" if n_vertex == 140751 else "GAGAL"))
print("[M2] PNG: %s , %s" % (
    os.path.exists(os.path.join(ren_dir, "M2_atas.png")),
    os.path.exists(os.path.join(ren_dir, "M2_miring.png"))))
print("[M2] FBX: %s , %s" % (
    os.path.exists(os.path.join(exp_dir, "SM_Ep01_Medan.fbx")),
    os.path.exists(os.path.join(exp_dir, "SM_Ep01_Tangga.fbx"))))
print("[M2] SELESAI")
