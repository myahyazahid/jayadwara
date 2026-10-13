"""Validasi paket FBX Jayadwara tanpa Unreal (docs/13 bagian 6.6).

Jalankan di Blender headless (proses terpisah, scene kosong):
  blender --background --factory-startup --python Art/Scripts/validate_jayadwara.py -- <file.fbx>
        [--max-tris N] [--materials N] [--height M] [--bones jd_skeleton]
Exit code 0 = semua PASS, 1 = ada FAIL.
"""
import argparse
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("fbx")
ap.add_argument("--max-tris", type=int, default=12000)
ap.add_argument("--materials", type=int, default=4)
ap.add_argument("--height", type=float, default=1.99, help="tinggi total termasuk tanduk (m)")
ap.add_argument("--tol", type=float, default=0.03)
ap.add_argument("--max-influence", type=int, default=4)
ap.add_argument("--no-zone", action="store_true", help="lewati cek JD_Zone (model bertekstur Tripo, Jayadwara2: tanpa atribut zona)")
ap.add_argument("--unit", type=float, default=0.01,
                help="meter per satuan data FBX; 0,01 = cm (kontrak Iterasi 6, 05_export_fbx.py)")
ap.add_argument("--export-scale", type=float, default=None,
                help="skala raksasa yang di-bake (default: export_scale di <mesh>_sockets.json, atau 1)")
args = ap.parse_args(argv)

import jd_skeleton as SK  # noqa: E402

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


# ---- scene kosong + import
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
fbx = os.path.abspath(args.fbx)
if hasattr(bpy.ops.import_scene, "fbx"):
    bpy.ops.import_scene.fbx(filepath=fbx)
else:
    bpy.ops.wm.fbx_import(filepath=fbx)
objs = list(bpy.data.objects)
arms = [o for o in objs if o.type == "ARMATURE"]
meshes = [o for o in objs if o.type == "MESH"]
empties = [o for o in objs if o.type == "EMPTY"]

check("tepat 1 armature", len(arms) == 1, f"{len(arms)} armature")
check("tepat 1 mesh (skeletal mesh tunggal)", len(meshes) == 1, f"{len(meshes)} mesh: {[m.name for m in meshes]}")
if len(arms) != 1 or len(meshes) != 1:
    for n, ok, d in results:
        print(("PASS" if ok else "FAIL"), "|", n, "|", d)
    sys.exit(1)
arm, mesh = arms[0], meshes[0]

# ---- tulang
expected = [b[0] for b in SK.build_bones()]
got = [b.name for b in arm.data.bones]
roots = [b.name for b in arm.data.bones if b.parent is None]
check("nama tulang = spesifikasi skeleton", set(got) == set(expected),
      f"kurang={sorted(set(expected) - set(got))[:6]} lebih={sorted(set(got) - set(expected))[:6]}")
check("jumlah tulang", len(got) == len(expected), f"{len(got)} (harapan {len(expected)})")
check("satu root bernama 'root'", roots == ["root"], str(roots))
check("nama tulang unik", len(set(got)) == len(got))

# ---- skala & ukuran
sc = [tuple(abs(v) for v in o.scale) for o in objs]
check("tidak ada skala negatif", all(v > 0 for o in objs for v in o.scale))
dg = bpy.context.evaluated_depsgraph_get()
ev = mesh.evaluated_get(dg)
corners = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
zmin, zmax = min(c.z for c in corners), max(c.z for c in corners)
import json as _json  # noqa: E402
import re as _re  # noqa: E402

_sj = _re.sub(r"_LOD\d+$", "", os.path.splitext(os.path.abspath(args.fbx))[0]) + "_sockets.json"
export_scale = args.export_scale
if export_scale is None:
    export_scale = _json.load(open(_sj, encoding="utf-8")).get("export_scale", 1.0) if os.path.exists(_sj) else 1.0
# ukuran dicek di skala authoring (1,90 m): data FBX = cm x export_scale
zmin, zmax = zmin * args.unit / export_scale, zmax * args.unit / export_scale
check(f"export_scale tercatat ({export_scale:.3f})", export_scale > 0)
check("telapak kaki di z≈0", abs(zmin) <= args.tol, f"zmin={zmin:.3f} m")
check(f"tinggi total ≈ {args.height} m", abs((zmax - zmin) - args.height) <= args.tol, f"{zmax - zmin:.3f} m")
check("objek armature bernama 'Armature' (UE tidak membuat tulang root tambahan)", arm.name == "Armature", arm.name)
check("skala armature seragam ≈ 1", all(abs(v - 1) < 1e-3 for v in arm.scale), f"scale={tuple(round(v, 4) for v in arm.scale)}")

# ---- topologi & material
me = mesh.data
tris = sum(len(p.vertices) - 2 for p in me.polygons)
check(f"tris ≤ {args.max_tris}", tris <= args.max_tris, f"{tris}")
check(f"slot material = {args.materials}", len(me.materials) == args.materials, str([m.name if m else None for m in me.materials]))
used_verts = set()
for e in me.edges:
    used_verts.update(e.vertices)
loose = sum(1 for v in me.vertices if v.index not in used_verts)
check("tidak ada vertex lepas", loose == 0, f"{loose}")
zero_area = sum(1 for p in me.polygons if p.area < 1e-9)
check("tidak ada face luas nol", zero_area == 0, f"{zero_area}")

# ---- UV (Iterasi 4): satu layer, semua koordinat di 0..1
import numpy as np  # noqa: E402

uvl = me.uv_layers.get("UVMap") or (me.uv_layers[0] if len(me.uv_layers) else None)
check("ada layer UV", uvl is not None, [l.name for l in me.uv_layers].__str__())
if uvl is not None:
    arr = np.empty(len(me.loops) * 2, dtype=np.float32)
    uvl.data.foreach_get("uv", arr)
    arr = arr.reshape(-1, 2)
    out = int(((arr < -0.001) | (arr > 1.001)).any(axis=1).sum())
    check("semua UV di dalam 0..1", out == 0, f"{out} loop di luar; rentang x[{arr[:, 0].min():.3f},{arr[:, 0].max():.3f}] y[{arr[:, 1].min():.3f},{arr[:, 1].max():.3f}]")
    check("hanya 1 layer UV", len(me.uv_layers) == 1, f"{len(me.uv_layers)}")

# ---- skin weight
names = {vg.index: vg.name for vg in mesh.vertex_groups}
bad_group = sorted({n for n in names.values() if n not in got})
check("semua vertex group = nama tulang", not bad_group, str(bad_group[:6]))
unw = over = off_norm = 0
mx = 0
for v in me.vertices:
    ws = [g.weight for g in v.groups if g.weight > 1e-4]
    if not ws:
        unw += 1
        continue
    mx = max(mx, len(ws))
    over += len(ws) > args.max_influence
    off_norm += abs(sum(ws) - 1.0) > 0.01
check("0 vertex tanpa weight", unw == 0, f"{unw}")
check(f"influence ≤ {args.max_influence} per vertex", over == 0, f"maks {mx}, melebihi: {over}")
check("weight ternormalisasi (jumlah=1±0,01)", off_norm == 0, f"{off_norm} vertex")
check("ada modifier/relasi armature", any(m.type == "ARMATURE" for m in mesh.modifiers) or mesh.parent == arm,
      f"modifier={[m.type for m in mesh.modifiers]} parent={mesh.parent.name if mesh.parent else None}")

# ---- socket: tidak di FBX (UE mengimpor empty sebagai tulang), tapi di <mesh>_sockets.json di sebelahnya
import json  # noqa: E402
import re  # noqa: E402

check("tidak ada empty di FBX (jadi tulang di UE)", not empties, str([o.name for o in empties][:6]))
exp_sockets = list(SK.build_sockets().keys())
sj = re.sub(r"_LOD\d+$", "", os.path.splitext(fbx)[0]) + "_sockets.json"
data = {}
if os.path.exists(sj):
    with open(sj, encoding="utf-8") as f:
        data = {s["name"]: s for s in json.load(f)["sockets"]}
missing = [s for s in exp_sockets if s not in data]
check("semua socket ada di _sockets.json", os.path.exists(sj) and not missing, f"hilang: {missing}" if os.path.exists(sj) else f"tidak ada: {sj}")
bad_parent = [s for s in exp_sockets if s in data and data[s]["bone"] not in got]
check("socket ter-parent ke tulang", not bad_parent, f"{bad_parent}")

# ---- atribut warna (info)
if not args.no_zone:
    check("atribut warna JD_Zone ada", "JD_Zone" in me.color_attributes)

# ---- laporan
w = max(len(n) for n, _, _ in results)
for n, ok, d in results:
    print(("PASS" if ok else "FAIL"), "|", n.ljust(w), "|", d)
fails = [n for n, ok, _ in results if not ok]
print(f"\nHASIL: {len(results) - len(fails)}/{len(results)} PASS" + (f" | GAGAL: {fails}" if fails else ""))
sys.exit(1 if fails else 0)
