"""Validasi FBX Tuyul (K3) — Blender headless.

  blender --background --factory-startup --python Hermes/Tools/validate_tuyul.py -- <fbx> [--scale 1.0]

Salinan validate_jerangkong.py dengan profil Tuyul: bobot **lunak** (tidak ada cek potongan kaku),
satu tulang per vertex tidak wajib, tulang bernama Mannequin + jaw + 3 jari + IK, tinggi 1,0 m x skala.
Skala dibaca dari <mesh>_sockets.json (export_scale). Keluar kode 1 kalau ada yang gagal.
"""
import json
import re
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
sys.path.insert(0, str(ROOT / "Hermes" / "Tools"))
import tuyul_skeleton as SK  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
fbx = Path(argv[0])
m = re.search(r"_LOD(\d)$", fbx.stem)
level = int(m.group(1)) if m else 0
BUDGET = {0: 100000, 1: 30000, 2: 14000, 3: 6000}[level]
base = re.sub(r"_LOD\d+$", "", fbx.stem)
sock_json = json.loads(fbx.with_name(base + "_sockets.json").read_text(encoding="utf-8"))
SCALE = float(sock_json["export_scale"])
TINGGI = 1.0 * SCALE                                   # model sumber 1,0000 m (K0)

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def import_fbx(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    return [o for o in bpy.data.objects if o not in before]


for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
new = import_fbx(fbx)
arm = next(o for o in new if o.type == "ARMATURE")
meshes = [o for o in new if o.type == "MESH"]
U = 0.01                                                     # data dalam cm (kontrak export)
wscale = arm.matrix_world.to_scale().x
UNIT = U if wscale > 0.5 else 1.0
B = {b.name: ((arm.matrix_world @ b.matrix_local).translation * UNIT / SCALE, b.parent.name if b.parent else None)
     for b in arm.data.bones}                                # ruang model (m)

# ---- tulang
spec = {n: (h, p) for n, p, h, _t, _c in SK.build_bones()}
missing = sorted(set(spec) - set(B))
check(f"{len(spec)} tulang tuyul_skeleton ada", not missing, f"hilang: {missing[:5]}" if missing else "")
extra = sorted(set(B) - set(spec))
check("tidak ada tulang tambahan", not extra, f"{extra[:5]}")
roots = [n for n, v in B.items() if v[1] is None]
check("satu akar bernama root", roots == ["root"], f"{roots}")
bad_par = [n for n in spec if n in B and B[n][1] != spec[n][1]]
check("hierarki sama dengan tuyul_skeleton", not bad_par, f"{bad_par[:5]}")
worst = max(((B[n][0] - Vector(spec[n][0])).length * 1000 for n in spec if n in B), default=0)
check("posisi tulang = tuyul_skeleton (<= 1 mm, ruang model)", worst <= 1.0, f"terburuk {worst:.3f} mm")
check("tidak ada empty", not [o for o in new if o.type == "EMPTY"], "")

# ---- mesh
check("tepat 1 objek mesh", len(meshes) == 1, f"{len(meshes)}")
mesh = meshes[0]
me = mesh.data
tris = sum(len(p.vertices) - 2 for p in me.polygons)
check(f"tris LOD{level} <= {BUDGET}", tris <= BUDGET, f"{tris}")
mats = [mt.name.split(".")[0] for mt in me.materials]
check("1-2 slot material (atlas Tripo)", 1 <= len(mats) <= 2, f"{mats}")
vgn = {vg.index: vg.name for vg in mesh.vertex_groups}
check("grup vertex hanya ke tulang yang ada", all(n in B for n in vgn.values()), "")
mx = unw = nonnorm = 0
for v in me.vertices:
    gs = [(vgn[g.group], g.weight) for g in v.groups if g.weight > 1e-4]
    mx = max(mx, len(gs))
    if not gs:
        unw += 1
        continue
    if abs(sum(w for _, w in gs) - 1.0) > 0.01:
        nonnorm += 1
check("<= 4 influence per vertex", mx <= 4, f"maks {mx}")
check("0 vertex tanpa bobot", unw == 0, f"{unw}")
check("bobot ternormalisasi (±0,01)", nonnorm == 0, f"{nonnorm}")
check("bobot lunak: tidak ada vertex 1-tulang-kaku wajib", True, "profil Tuyul tidak memakai cek potongan kaku")
mw = mesh.matrix_world
zs = [(mw @ v.co).z * UNIT for v in me.vertices]
h = (max(zs) - min(zs)) / SCALE
check(f"tinggi model 1,00 m x skala {SCALE:.0f} = {TINGGI:.2f} m (±1%)", abs(h - 1.0) <= 0.01,
      f"{h:.3f} m x skala {SCALE} = {h * SCALE:.2f} m")
check("telapak di z≈0", abs(min(zs)) / SCALE <= 0.01, f"{min(zs):.4f} m")
uv = me.uv_layers.active
check("UV 0-1", uv is not None and all(-0.001 <= c <= 1.001 for d in uv.data for c in d.uv), "")
bad_s = [s["name"] for s in sock_json["sockets"] if s["bone"] not in B]
check("socket JSON: tulang induk ada (>= 8)", not bad_s and len(sock_json["sockets"]) >= 8,
      f"{len(sock_json['sockets'])} socket" + (f" rusak: {bad_s}" if bad_s else ""))

passed = sum(1 for r in results if r[1])
print(f"\nHASIL: {passed}/{len(results)} lulus — {fbx.name}")
sys.exit(0 if passed == len(results) else 1)
