"""Jerangkong — impor model awal developer (Tripo AI, GLB) ke scene setup, sebagai basis Iterasi 1 (docs/20 jalur B).

Jalankan headless dari scene setup:
  blender --background Art/Blender/jerangkong_v00_setup.blend --python Art/Scripts/jerangkong_01_import_tripo.py
Hasil: Art/Blender/jerangkong_v01_tripo.blend (objek `JK_Source` di collection `01_Source`; tekstur di-pack).

Normalisasi:
- GLB Tripo: tinggi 1,0, menghadap +X (Blender) -> diputar -90° di Z supaya menghadap -Y (kontrak Jayadwara/Aksa).
- Skala: puncak tengkorak = TOP_Z (setinggi konsep; docs/24 S1/S2).
- Posisi: telapak di z=0; x = rata-rata pusat tengkorak & pusat kedua telapak (sama dengan reference plane depan);
  y = pusat pergelangan kaki (sama dengan reference plane samping).
- Vertex kembar di jahitan UV digabung (glTF memecah vertex per UV; UV & normal per-loop tetap).
Sumber asli tidak diubah: Art/Source/jerangkong_tripo_v01.glb (salinan yahya_design/rKHD3GD0eELe7BHA74wR.glb).
"""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
SRC = ROOT / "Art" / "Source" / "jerangkong_tripo_v01.glb"
OUT = ROOT / "Art" / "Blender" / "jerangkong_v01_tripo.blend"
TOP_Z = 2.19
MERGE_DIST = 0.0005            # m (setelah skala)

scene = bpy.context.scene
root_coll = bpy.data.collections["JK_Jerangkong"]
src_coll = bpy.data.collections.get("01_Source") or bpy.data.collections.new("01_Source")
if src_coll.name not in root_coll.children:
    root_coll.children.link(src_coll)

old = bpy.data.objects.get("JK_Source")
if old:
    bpy.data.objects.remove(old, do_unlink=True)

before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(SRC))
new = [o for o in bpy.data.objects if o not in before]
mesh_obs = [o for o in new if o.type == "MESH"]
assert len(mesh_obs) == 1, f"GLB berisi {len(mesh_obs)} mesh, diharapkan 1"
ob = mesh_obs[0]
for o in new:
    if o is not ob:
        bpy.data.objects.remove(o, do_unlink=True)
ob.parent = None
ob.name = "JK_Source"
ob.data.name = "JK_Source"
for c in list(ob.users_collection):
    c.objects.unlink(ob)
src_coll.objects.link(ob)

# 1) bake transform impor, putar menghadap -Y, skala
me = ob.data
me.transform(ob.matrix_world)
ob.matrix_world = Matrix.Identity(4)
me.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))
zs = [v.co.z for v in me.vertices]
z0, z1 = min(zs), max(zs)
me.transform(Matrix.Translation((0, 0, -z0)))
s = TOP_Z / (z1 - z0)
me.transform(Matrix.Scale(s, 4))


# 2) pusatkan
def band_center(zlo, zhi, axis):
    vals = [v.co[axis] for v in me.vertices if zlo <= v.co.z <= zhi]
    return (min(vals) + max(vals)) / 2.0


skull_x = band_center(TOP_Z - 0.12, TOP_Z, 0)
feet_x = band_center(0.0, 0.05, 0)
ankle_y = band_center(0.15, 0.25, 1)
me.transform(Matrix.Translation((-(skull_x + feet_x) / 2.0, -ankle_y, 0)))

# 3) gabung vertex kembar di jahitan UV
bm = bmesh.new()
bm.from_mesh(me)
nv0 = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=MERGE_DIST)
nv1 = len(bm.verts)
bm.to_mesh(me)
bm.free()
me.update()

# 4) pack tekstur supaya file .blend mandiri
for img in bpy.data.images:
    if img.source == "FILE" and not img.packed_file and img.users:
        try:
            img.pack()
        except RuntimeError as e:
            print("  ! gagal pack", img.name, e)

ob["jk_source"] = "Art/Source/jerangkong_tripo_v01.glb (Tripo AI, model awal developer)"
ob["jk_scale"] = s

bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
co = [v.co for v in me.vertices]
mn = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
mx = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print(f"Disimpan: {OUT}")
print(f"skala x{s:.4f}; vertex {nv0} -> {nv1} setelah merge; tris {tris}")
print(f"bbox min {tuple(round(v, 3) for v in mn)} max {tuple(round(v, 3) for v in mx)}")
