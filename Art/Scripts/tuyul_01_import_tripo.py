"""Tuyul K0 (docs/27, Hermes/tuyul_hermes.md) — impor GLB Tripo developer sebagai basis intake.

Jalankan headless dari scene setup:
  blender --background Art/Blender/tuyul/tuyul_v00_setup.blend \
      --python Art/Scripts/tuyul_01_import_tripo.py -- [opsi]
Hasil: Art/Blender/tuyul/tuyul_v01_intake.blend (objek `TY_Source` di collection `01_Source`; tekstur di-pack).

Opsi:
  --src <glb>      sumber GLB (default Art/Source/tuyul_tripo_v01.glb)
  --out <blend>    keluaran (default Art/Blender/tuyul/tuyul_v01_intake.blend)
  --top-z <m>      tinggi puncak kepala (default 1.0; kartu model)
  --rot-z <deg>    putaran Z untuk menghadap -Y (coba 0/90/-90/180; default 0)
  --merge-dist <m> jarak gabung vertex kembar jahitan UV (default 0.0005)

Normalisasi: puncak kepala = TOP_Z, telapak di z=0, pusat X = rata-rata pusat kepala & telapak,
pusat Y = pusat pergelangan kaki. Sumber asli tidak diubah.
Salinan dari Art/Scripts/jerangkong_01_import_tripo.py; hanya path/nama/collection/argumen yang diubah.
"""
import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuyul_paths as P  # noqa: E402

ROOT = P.ROOT


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(P.SOURCE))
    ap.add_argument("--out", default=str(P.BLENDER / "tuyul_v01_intake.blend"))
    ap.add_argument("--top-z", type=float, default=1.0)
    ap.add_argument("--rot-z", type=float, default=0.0)
    ap.add_argument("--merge-dist", type=float, default=0.0005)
    return ap.parse_args(argv)


args = parse_args()
SRC = Path(args.src)
OUT = Path(args.out)
TOP_Z = args.top_z
ROT_Z = args.rot_z
MERGE_DIST = args.merge_dist

scene = bpy.context.scene
root_coll = bpy.data.collections.get("TY_Tuyul") or bpy.data.collections.new("TY_Tuyul")
if root_coll.name not in scene.collection.children:
    scene.collection.children.link(root_coll)
src_coll = bpy.data.collections.get("01_Source") or bpy.data.collections.new("01_Source")
if src_coll.name not in root_coll.children:
    root_coll.children.link(src_coll)

old = bpy.data.objects.get("TY_Source")
if old:
    bpy.data.objects.remove(old, do_unlink=True)

before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(SRC))
new = [o for o in bpy.data.objects if o not in before]

print("=== objek hasil impor ===")
for o in new:
    extra = ""
    if o.type == "MESH":
        me = o.data
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        extra = f" verts={len(me.vertices)} tris={tris} mats={[m.name for m in me.materials]}"
    print(f"  {o.type:9s} {o.name}{extra}")
print("=== image/tekstur ===")
for img in bpy.data.images:
    if img.users:
        print(f"  {img.name} size={tuple(img.size)} src={img.source}")

mesh_obs = [o for o in new if o.type == "MESH"]
assert mesh_obs, "GLB tidak berisi mesh"

# gabung semua mesh jadi satu objek TY_Source
for o in mesh_obs[1:]:
    o.select_set(True)
mesh_obs[0].select_set(True)
bpy.context.view_layer.objects.active = mesh_obs[0]
if len(mesh_obs) > 1:
    bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
for o in list(new):
    if o is not ob and o.name in bpy.data.objects:
        bpy.data.objects.remove(o, do_unlink=True)
ob.parent = None
ob.name = "TY_Source"
ob.data.name = "TY_Source"
for c in list(ob.users_collection):
    c.objects.unlink(ob)
src_coll.objects.link(ob)

# 1) bake transform impor, putar menghadap -Y, skala ke TOP_Z
me = ob.data
me.transform(ob.matrix_world)
ob.matrix_world = Matrix.Identity(4)
if ROT_Z:
    me.transform(Matrix.Rotation(math.radians(ROT_Z), 4, "Z"))
zs = [v.co.z for v in me.vertices]
z0, z1 = min(zs), max(zs)
me.transform(Matrix.Translation((0, 0, -z0)))
s = TOP_Z / (z1 - z0)
me.transform(Matrix.Scale(s, 4))


# 2) pusatkan (X: rata-rata pusat kepala & telapak; Y: pusat pergelangan kaki)
def band_center(zlo, zhi, axis):
    vals = [v.co[axis] for v in me.vertices if zlo <= v.co.z <= zhi]
    return (min(vals) + max(vals)) / 2.0 if vals else 0.0


head_x = band_center(TOP_Z - 0.12 * TOP_Z, TOP_Z, 0)
feet_x = band_center(0.0, 0.05 * TOP_Z, 0)
ankle_y = band_center(0.15 * TOP_Z, 0.25 * TOP_Z, 1)
me.transform(Matrix.Translation((-(head_x + feet_x) / 2.0, -ankle_y, 0)))

# 3) gabung vertex kembar di jahitan UV
bm = bmesh.new()
bm.from_mesh(me)
nv0 = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=MERGE_DIST)
nv1 = len(bm.verts)
bm.to_mesh(me)
bm.free()
me.update()

# 4) pack tekstur supaya .blend mandiri
for img in bpy.data.images:
    if img.source == "FILE" and not img.packed_file and img.users:
        try:
            img.pack()
        except RuntimeError as e:
            print("  ! gagal pack", img.name, e)

ob["ty_source"] = "Art/Source/tuyul_tripo_v01.glb (Tripo AI, developer)"
ob["ty_scale"] = s
ob["ty_rot_z"] = ROT_Z

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)

co = [v.co for v in me.vertices]
mn = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
mx = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print(f"Disimpan: {OUT}")
print(f"skala x{s:.4f} rot_z {ROT_Z}; vertex {nv0} -> {nv1} setelah merge; tris {tris}")
print(f"bbox min {tuple(round(v, 4) for v in mn)} max {tuple(round(v, 4) for v in mx)}")
print(f"tinggi = {mx.z - mn.z:.4f} m")
