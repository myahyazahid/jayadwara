#!/usr/bin/env python3
"""MK2 - Medan Ep02_KampungKali (v02) di Blender (headless).

Bangun mesh SM_Ep02_Medan: grid x -700..700, y -600..400, sel 2,5 m -> 561 x 401 = 224.961 vertex,
tinggi = elev(x,y). Tiap muka diberi slot material dari ep02_medan_v02.zona_material(x, y) di titik
tengah muka. Slot (8): Air, Rel, Jalan, Gudang, Paving, Kampung, Bantaran, Sawah.

Simpan maps_ep2_medan_v02.blend, ekspor Export/SM_Ep02_Medan.fbx (meter; UE baca x100 -> cm),
render 2 PNG (Eevee): MK2_atas (orto dari atas, utara di atas) + MK2_miring (dari barat daya, ~35 deg).

Jalankan (dari WORKTREE):
  blender --background --factory-startup --python Hermes/Tools/maps_ep2_20_medan_blender.py -- --out Hermes/Art/maps_ep2
"""
import json
import math
import os
import sys

import bpy
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
    out_dir = os.path.join(WORKTREE, "Hermes", "Art", "maps_ep2")
out_dir = os.path.abspath(out_dir)
exp_dir = os.path.join(out_dir, "Export")
ren_dir = os.path.join(out_dir, "Render")
for d in (out_dir, exp_dir, ren_dir):
    os.makedirs(d, exist_ok=True)

sys.path.insert(0, os.path.join(WORKTREE, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402  (elev, zona_material, TITIK_UJI)

with open(os.path.join(WORKTREE, "Art", "Level", "ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
MEDAN = DATA["medan"]
X0, X1 = MEDAN["x_min"], MEDAN["x_max"]
Y0, Y1 = MEDAN["y_min"], MEDAN["y_max"]
SEL = MEDAN["sel"]
NX = int(round((X1 - X0) / SEL)) + 1
NY = int(round((Y1 - Y0) / SEL)) + 1
CX_MEDAN = (X0 + X1) / 2.0
CY_MEDAN = (Y0 + Y1) / 2.0
print("[MK2] grid medan: x %g..%g, y %g..%g, sel %g -> %d x %d = %d vertex"
      % (X0, X1, Y0, Y1, SEL, NX, NY, NX * NY))


# ------------------------------------------------------------------ warna
def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


WARNA = {k: tuple(v) for k, v in DATA["mi_warna"].items()}   # sRGB 0-255 dari JSON
SLOT = ["Air", "Rel", "Jalan", "Gudang", "Paving", "Kampung", "Bantaran", "Sawah"]
for _s in SLOT:
    assert _s in WARNA, "slot medan tidak ada di mi_warna: %s" % _s


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


MAT = {name: make_mat(name, WARNA[name]) for name in SLOT}

# ------------------------------------------------------------------ scene bersih
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

scene = bpy.context.scene
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
    try:
        scene.render.engine = eng
        break
    except Exception:
        pass
print("[MK2] render engine:", scene.render.engine)
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.render.image_settings.file_format = "PNG"
try:
    scene.view_settings.view_transform = "Standard"
except Exception as e:
    print("[MK2] view_transform Standard gagal:", e)
for attr in ("taa_render_samples", "taa_samples"):
    try:
        setattr(scene.eevee, attr, 32)
        break
    except Exception:
        pass

world = bpy.data.worlds.new("W_MK2")
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

medan_mesh = bpy.data.meshes.new("SM_Ep02_Medan")
medan_mesh.from_pydata(verts, [], faces)
medan_mesh.update()
for name in SLOT:
    medan_mesh.materials.append(MAT[name])
slot_index = {name: k for k, name in enumerate(SLOT)}

zona_count = {name: 0 for name in SLOT}
luar = 0
for j in range(NY - 1):
    row = j * (NX - 1)
    for i in range(NX - 1):
        cx = X0 + (i + 0.5) * SEL
        cy = Y0 + (j + 0.5) * SEL
        zn = M.zona_material(cx, cy)
        if zn not in slot_index:
            luar += 1
            zn = "Bantaran"
        medan_mesh.polygons[row + i].material_index = slot_index[zn]
        zona_count[zn] += 1
medan_mesh.validate()
medan_obj = bpy.data.objects.new("SM_Ep02_Medan", medan_mesh)
bpy.context.collection.objects.link(medan_obj)

n_vertex = len(medan_mesh.vertices)
n_face = len(medan_mesh.polygons)
print("[MK2] mesh medan: %d vertex, %d muka" % (n_vertex, n_face))
print("[MK2] jumlah muka per zona:", {k: zona_count[k] for k in SLOT})
if luar:
    print("[MK2] PERINGATAN muka di luar 8 slot (dipetakan ke Bantaran):", luar)

# ------------------------------------------------------------------ kamera
cam_atas_data = bpy.data.cameras.new("Cam_Atas")
cam_atas_data.type = "ORTHO"
cam_atas_data.ortho_scale = 1900.0            # medan 1400 x 1000 -> 16:9 butuh >= 1778
cam_atas_data.clip_start = 1.0
cam_atas_data.clip_end = 8000.0
cam_atas = bpy.data.objects.new("C_MK2_Atas", cam_atas_data)
cam_atas.location = (CX_MEDAN, CY_MEDAN, 2000.0)
cam_atas.rotation_euler = (0.0, 0.0, 0.0)     # lihat -Z, atas = +Y (utara di atas)
bpy.context.collection.objects.link(cam_atas)

cam_mir_data = bpy.data.cameras.new("Cam_Miring")
cam_mir_data.type = "PERSP"
cam_mir_data.lens = 40.0
cam_mir_data.clip_start = 1.0
cam_mir_data.clip_end = 40000.0
cam_mir = bpy.data.objects.new("C_MK2_Miring", cam_mir_data)
az = math.radians(225.0)                       # dari BARAT DAYA
D = 2200.0
h = D * math.tan(math.radians(35.0))
target = Vector((CX_MEDAN, CY_MEDAN, 5.0))
cam_mir.location = Vector((CX_MEDAN + math.cos(az) * D, CY_MEDAN + math.sin(az) * D, h))
arah = target - cam_mir.location
cam_mir.rotation_euler = arah.to_track_quat("-Z", "Y").to_euler()
bpy.context.collection.objects.link(cam_mir)
print("[MK2] kamera miring di (%.0f, %.0f, %.0f), elevasi 35 deg, lens %.0f"
      % (cam_mir.location.x, cam_mir.location.y, cam_mir.location.z, cam_mir_data.lens))

# ------------------------------------------------------------------ matahari
sun_data = bpy.data.lights.new("Sun_MK2", type="SUN")
sun_data.energy = 0.6
sun = bpy.data.objects.new("Sun_MK2", sun_data)
sun.rotation_euler = (0.0, 0.0, 0.0)
bpy.context.collection.objects.link(sun)

# ------------------------------------------------------------------ render
def render_ke(cam, sun_rot_deg, path):
    scene.camera = cam
    sun.rotation_euler = tuple(math.radians(a) for a in sun_rot_deg)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("[MK2] render ->", path)


render_ke(cam_atas, (0.0, 0.0, 0.0), os.path.join(ren_dir, "MK2_atas.png"))
render_ke(cam_mir, (52.0, 0.0, -38.0), os.path.join(ren_dir, "MK2_miring.png"))

# ------------------------------------------------------------------ simpan .blend
blend_path = os.path.join(out_dir, "maps_ep2_medan_v02.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("[MK2] simpan blend ->", blend_path)

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
        print("[MK2] export kwargs penuh gagal (%s), coba minimal" % e)
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"})
    print("[MK2] ekspor FBX ->", path, "|", os.path.getsize(path) // 1024, "KB")


export_fbx(medan_obj, os.path.join(exp_dir, "SM_Ep02_Medan.fbx"))

# ------------------------------------------------------------------ uji 14 titik
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


print("\n[MK2] UJI 14 TITIK: tinggi mesh (bilinear) vs elev (target |d| <= 0.05 m)")
print("%-28s %8s %10s %8s" % ("titik", "elev", "mesh_bil", "d"))
max_d = 0.0
n_lulus = 0
for label, ((x, y), tgt, tol) in M.TITIK_UJI.items():
    e = M.elev(x, y)
    mb = mesh_z(x, y)
    d = mb - e
    max_d = max(max_d, abs(d))
    if abs(d) <= 0.05:
        n_lulus += 1
    print("%-28s %8.2f %10.2f %8.3f" % (label, e, mb, d))
print("[MK2] max |mesh - elev| = %.3f m ; lulus <=0.05: %d/%d" % (max_d, n_lulus, len(M.TITIK_UJI)))

# ------------------------------------------------------------------ verdict
print("\n[MK2] vertex medan = %d (target 224961): %s"
      % (n_vertex, "OK" if n_vertex == 224961 else "GAGAL"))
print("[MK2] PNG: %s , %s" % (
    os.path.exists(os.path.join(ren_dir, "MK2_atas.png")),
    os.path.exists(os.path.join(ren_dir, "MK2_miring.png"))))
print("[MK2] FBX: %s" % os.path.exists(os.path.join(exp_dir, "SM_Ep02_Medan.fbx")))
print("[MK2] SELESAI")
