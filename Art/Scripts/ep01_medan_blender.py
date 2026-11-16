"""Mesh medan + tangga Ep01_LawangSapta (greybox) di Blender, headless.

Sumber data: Art/Level/ep01_medan_v02.py (elev, zona_material, TITIK_UJI) dan ep01_layout_v02.json (batas medan, tangga).
Dipindah dari Hermes/Tools/maps_ep1_v02_20_medan_blender.py (hermes/maps_ep1_v02), jalur keluaran disesuaikan struktur proyek.

Hasil:
  Art/Export/Level/SM_Ep01_Medan.fbx    grid sel 2,5 m, tinggi = elev(x, y), slot material per zona (Air, Galian, Jalan, Plato, Sawah, Desa, Hutan)
  Art/Export/Level/SM_Ep01_Tangga.fbx   28 balok dari CANDI_Tangga, origin (0, 0, 0)
  Art/Blender/ep01/ep01_medan.blend
Uji: tinggi mesh vs elev di semua TITIK_UJI (|d| <= 0,05 m); keluar dengan kode 1 kalau gagal.

Jalankan:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" --background --factory-startup --python Art/Scripts/ep01_medan_blender.py
"""
import json
import math
import os
import sys

import bmesh
import bpy

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EXPORT = os.path.join(REPO, "Art", "Export", "Level")
BLEND = os.path.join(REPO, "Art", "Blender", "ep01", "ep01_medan.blend")
for d in (EXPORT, os.path.dirname(BLEND)):
    os.makedirs(d, exist_ok=True)

sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep01_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
MEDAN = DATA["medan"]
X0, X1, Y0, Y1, SEL = MEDAN["x_min"], MEDAN["x_max"], MEDAN["y_min"], MEDAN["y_max"], MEDAN["sel"]
NX = int(round((X1 - X0) / SEL)) + 1
NY = int(round((Y1 - Y0) / SEL)) + 1
print(f"[medan] grid x {X0}..{X1}, y {Y0}..{Y1}, sel {SEL} -> {NX} x {NY} = {NX * NY} vertex")

# warna sRGB hanya untuk material pratinjau Blender; material UE dibuat oleh Tools/ue_greybox_ep01.py
WARNA = {"Air": (91, 143, 176), "Galian": (181, 88, 47), "Jalan": (150, 120, 90), "Plato": (128, 132, 118),
         "Sawah": (126, 162, 89), "Desa": (199, 166, 121), "Hutan": (79, 107, 74), "Andesit": (108, 120, 113)}
SLOT = ["Air", "Galian", "Jalan", "Plato", "Sawah", "Desa", "Hutan"]


def linear(v):
    c = v / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def make_mat(name, srgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    r, g, b = [linear(v) for v in srgb]
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
    m.diffuse_color = (r, g, b, 1.0)
    return m


MAT = {n: make_mat(n, c) for n, c in WARNA.items()}
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

# ------------------------------------------------------------------ medan
Z = [[0.0] * NX for _ in range(NY)]
verts = []
for j in range(NY):
    y = Y0 + j * SEL
    for i in range(NX):
        x = X0 + i * SEL
        Z[j][i] = M.elev(x, y)
        verts.append((x, y, Z[j][i]))
faces = []
for j in range(NY - 1):
    for i in range(NX - 1):
        a = j * NX + i
        faces.append((a, a + 1, (j + 1) * NX + i + 1, (j + 1) * NX + i))
mesh = bpy.data.meshes.new("SM_Ep01_Medan")
mesh.from_pydata(verts, [], faces)
mesh.update()
for n in SLOT:
    mesh.materials.append(MAT[n])
idx = {n: k for k, n in enumerate(SLOT)}
per_zona = dict.fromkeys(SLOT, 0)
for j in range(NY - 1):
    for i in range(NX - 1):
        zn = M.zona_material(X0 + (i + 0.5) * SEL, Y0 + (j + 0.5) * SEL)
        mesh.polygons[j * (NX - 1) + i].material_index = idx[zn]
        per_zona[zn] += 1
mesh.validate()
medan = bpy.data.objects.new("SM_Ep01_Medan", mesh)
bpy.context.collection.objects.link(medan)
print(f"[medan] {len(mesh.vertices)} vertex, {len(mesh.polygons)} muka; muka per zona: {per_zona}")

# ------------------------------------------------------------------ tangga (CANDI_Tangga)
T = next(o for o in DATA["objek"] if o["id"] == "CANDI_Tangga")
(xs, ys, zs), (xe, ye, ze) = T["dari"], T["ke"]
n_step, lebar = T["anak_tangga"], T["lebar"]
dy, dz = (ye - ys) / n_step, (ze - zs) / n_step
bm = bmesh.new()
for k in range(n_step):
    y0, y1, ztop = ys + k * dy, ys + (k + 1) * dy, zs + (k + 1) * dz
    xa, xb = -lebar / 2.0, lebar / 2.0
    vs = [bm.verts.new(p) for p in ((xa, y0, zs), (xb, y0, zs), (xb, y1, zs), (xa, y1, zs),
                                    (xa, y0, ztop), (xb, y0, ztop), (xb, y1, ztop), (xa, y1, ztop))]
    for q in ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in q])
bm.normal_update()
tmesh = bpy.data.meshes.new("SM_Ep01_Tangga")
bm.to_mesh(tmesh)
bm.free()
tmesh.materials.append(MAT["Andesit"])
tangga = bpy.data.objects.new("SM_Ep01_Tangga", tmesh)
bpy.context.collection.objects.link(tangga)
print(f"[tangga] {len(tmesh.vertices)} vertex, {n_step} balok dari ({xs},{ys},{zs}) ke ({xe},{ye},{ze})")

# ------------------------------------------------------------------ simpan + ekspor
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("[simpan]", BLEND)


def export_fbx(obj, path):
    for o in bpy.data.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, global_scale=1.0,
                             apply_unit_scale=True, axis_forward="X", axis_up="Z", mesh_smooth_type="FACE")
    print("[ekspor]", path)


export_fbx(medan, os.path.join(EXPORT, "SM_Ep01_Medan.fbx"))
export_fbx(tangga, os.path.join(EXPORT, "SM_Ep01_Tangga.fbx"))

# ------------------------------------------------------------------ uji titik
def mesh_z(x, y):
    fx, fy = (x - X0) / SEL, (y - Y0) / SEL
    i0 = max(0, min(NX - 2, int(math.floor(fx))))
    j0 = max(0, min(NY - 2, int(math.floor(fy))))
    tx, ty = fx - i0, fy - j0
    return ((Z[j0][i0] * (1 - tx) + Z[j0][i0 + 1] * tx) * (1 - ty) + (Z[j0 + 1][i0] * (1 - tx) + Z[j0 + 1][i0 + 1] * tx) * ty)


print("[uji] tinggi mesh vs elev (target |d| <= 0.05 m)")
gagal = 0
for label, ((x, y), tgt, tol) in M.TITIK_UJI.items():
    d = mesh_z(x, y) - M.elev(x, y)
    ok = abs(d) <= 0.05
    gagal += not ok
    print(f"  {'OK ' if ok else 'GAGAL'} {label:26s} elev={M.elev(x, y):7.2f} mesh={mesh_z(x, y):7.2f} d={d:+.3f}")

print("[medan] SELESAI" if gagal == 0 else f"[medan] ADA {gagal} TITIK GAGAL")
sys.exit(1 if gagal else 0)
