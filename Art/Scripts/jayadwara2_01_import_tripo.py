"""Jayadwara2 — impor & normalisasi model Tripo AI (GLB) developer, plus laporan kondisi mesh (docs/25 R0).

Jalankan headless (scene kosong):
  blender --background --factory-startup --python Art/Scripts/jayadwara2_01_import_tripo.py -- \
      [--src Art/Source/jayadwara_tripo_v01.glb] [--out Art/Blender/jayadwara2_v01_tripo.blend] \
      [--top-z 1.99] [--rot-z -90] [--no-merge]
Hasil: objek `JD2_Source` (semua mesh GLB digabung) di collection `JD2_Jayadwara/01_Source`, tekstur di-pack.

Normalisasi (sama dengan jerangkong_01_import_tripo.py):
- Rotasi --rot-z derajat di Z supaya menghadap -Y (kontrak Jayadwara/Aksa). GLB Tripo Jerangkong menghadap +X -> -90.
  CEK di render depan; laporan mencetak tebakan arah hadap dari telapak (jari kaki vs tumit).
- Skala: puncak bbox (TERMASUK tanduk) = --top-z. Model lama: 1,90 m tanpa tanduk, ±1,99 m dengan tanduk.
  Setelah R0, ganti --top-z supaya puncak helm (tanpa tanduk) = 1,90 (docs/25 R5).
- Telapak di z=0; x = rata-rata pusat kepala & pusat kedua telapak; y = pusat pergelangan kaki.
- Vertex kembar di jahitan UV digabung (glTF memecah vertex per UV; UV & normal per-loop tetap).
Sumber tidak diubah.
"""
import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--src", default=str(ROOT / "Art" / "Source" / "jayadwara_tripo_v01.glb"))
ap.add_argument("--out", default=str(ROOT / "Art" / "Blender" / "jayadwara2_v01_tripo.blend"))
ap.add_argument("--top-z", type=float, default=1.99)
ap.add_argument("--rot-z", type=float, default=-90.0)
ap.add_argument("--merge-dist", type=float, default=0.0005, help="m, setelah skala")
ap.add_argument("--no-merge", action="store_true")
args = ap.parse_args(argv)

SRC, OUT = Path(args.src), Path(args.out)
assert SRC.exists(), f"tidak ada: {SRC}"
assert OUT.resolve() != SRC.resolve()

# ------------------------------------------------------------------ scene bersih
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
root_coll = bpy.data.collections.new("JD2_Jayadwara")
scene.collection.children.link(root_coll)
src_coll = bpy.data.collections.new("01_Source")
root_coll.children.link(src_coll)

# ------------------------------------------------------------------ impor
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(SRC))
new = [o for o in bpy.data.objects if o not in before]
mesh_obs = [o for o in new if o.type == "MESH"]
assert mesh_obs, "GLB tanpa mesh"
n_mesh_src = len(mesh_obs)
n_armature_src = sum(o.type == "ARMATURE" for o in new)
n_anim_src = len(bpy.data.actions)

# bake transform dunia ke data tiap mesh, lalu gabung jadi satu
for o in mesh_obs:
    mw = o.matrix_world.copy()
    o.parent = None
    o.modifiers.clear()
    o.data.transform(mw)
    o.matrix_world = Matrix.Identity(4)
for o in new:
    if o not in mesh_obs:
        bpy.data.objects.remove(o, do_unlink=True)
ob = mesh_obs[0]
if len(mesh_obs) > 1:
    with bpy.context.temp_override(active_object=ob, selected_editable_objects=mesh_obs, selected_objects=mesh_obs):
        bpy.ops.object.join()
ob.name = ob.data.name = "JD2_Source"
for c in list(ob.users_collection):
    c.objects.unlink(ob)
src_coll.objects.link(ob)
me = ob.data

# ------------------------------------------------------------------ 1) putar, skala, telapak di z=0
me.transform(Matrix.Rotation(math.radians(args.rot_z), 4, "Z"))
zs = [v.co.z for v in me.vertices]
z0, z1 = min(zs), max(zs)
me.transform(Matrix.Translation((0, 0, -z0)))
s = args.top_z / (z1 - z0)
me.transform(Matrix.Scale(s, 4))
TOP = args.top_z


# ------------------------------------------------------------------ 2) pusatkan
def band(zlo, zhi, axis):
    vals = [v.co[axis] for v in me.vertices if zlo <= v.co.z <= zhi]
    return (min(vals), max(vals)) if vals else (0.0, 0.0)


def band_center(zlo, zhi, axis):
    lo, hi = band(zlo, zhi, axis)
    return (lo + hi) / 2.0


head_x = band_center(TOP * 0.88, TOP * 0.95, 0)          # di bawah tanduk
feet_x = band_center(0.0, 0.05, 0)
ankle_y = band_center(TOP * 0.04, TOP * 0.08, 1)
me.transform(Matrix.Translation((-(head_x + feet_x) / 2.0, -ankle_y, 0)))

# ------------------------------------------------------------------ 3) gabung vertex jahitan UV
nv0 = len(me.vertices)
if not args.no_merge:
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=args.merge_dist)
    bm.to_mesh(me)
    bm.free()
    me.update()
nv1 = len(me.vertices)

# ------------------------------------------------------------------ 4) pack tekstur
images = []
for img in bpy.data.images:
    if not img.users or img.type != "IMAGE":            # lewati Render Result / Viewer Node
        continue
    images.append((img.name, tuple(img.size)))
    if img.source == "FILE" and not img.packed_file:
        try:
            img.pack()
        except RuntimeError as e:
            print("  ! gagal pack", img.name, e)

ob["jd2_source"] = f"{SRC.name} (Tripo AI, model developer; docs/25)"
ob["jd2_scale"] = s
ob["jd2_rot_z"] = args.rot_z

# ------------------------------------------------------------------ laporan
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
boundary = sum(1 for e in bm.edges if e.is_boundary)
# pulau mesh (bagian terpisah)
seen, islands = set(), []
for v in bm.verts:
    if v.index in seen:
        continue
    stack, size = [v], 0
    seen.add(v.index)
    while stack:
        cur = stack.pop()
        size += 1
        for e in cur.link_edges:
            w = e.other_vert(cur)
            if w.index not in seen:
                seen.add(w.index)
                stack.append(w)
    islands.append(size)
bm.free()

co = [v.co.copy() for v in me.vertices]
mn = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
mx = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))

# simetri kiri-kanan: jarak vertex hasil cermin X ke vertex terdekat
kd = KDTree(len(co))
for i, c in enumerate(co):
    kd.insert(c, i)
kd.balance()
step = max(1, len(co) // 20000)
d = sorted(kd.find(Vector((-c.x, c.y, c.z)))[2] for c in co[::step])
sym_med, sym_p95 = d[len(d) // 2], d[int(len(d) * 0.95)]

# tebakan arah hadap: jari kaki menonjol lebih jauh dari pergelangan (y=0) daripada tumit
fy0, fy1 = band(0.0, TOP * 0.03, 1)
facing = "-Y (OK)" if -fy0 > fy1 else "+Y (PUTAR 180°: tambah 180 ke --rot-z)"

tris = sum(len(p.vertices) - 2 for p in me.polygons)
OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)

print("=" * 70)
print(f"Sumber   : {SRC}  ({SRC.stat().st_size / 1e6:.1f} MB)")
print(f"Disimpan : {OUT}")
print(f"GLB      : {n_mesh_src} mesh, {n_armature_src} armature, {n_anim_src} action")
print(f"Skala    : x{s:.4f} (tinggi asli {z1 - z0:.4f}) -> puncak {TOP} m; rot Z {args.rot_z}°")
print(f"Mesh     : {tris} tris, vertex {nv0} -> {nv1} setelah merge, {len(ob.material_slots)} material")
print(f"Tekstur  : " + ", ".join(f"{n} {w}x{h}" for n, (w, h) in images))
print(f"Topologi : {len(islands)} pulau (terbesar {sorted(islands, reverse=True)[:6]}), "
      f"{non_manifold} tepi non-manifold, {boundary} tepi terbuka")
print(f"Simetri X: median {sym_med * 100:.2f} cm, p95 {sym_p95 * 100:.2f} cm")
print(f"Hadap    : {facing}")
print(f"BBox     : min {tuple(round(v, 3) for v in mn)} max {tuple(round(v, 3) for v in mx)}")
print("=" * 70)
