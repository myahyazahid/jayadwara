"""Validasi FBX Jerangkong (jalur B, docs/20 6.5) — Blender headless.

  blender --background --factory-startup --python Art/Scripts/validate_jerangkong.py -- Art/Export/SK_Jerangkong.fbx [--parts]

Skala dibaca dari <mesh>_sockets.json (export_scale). Cek:
 tulang: semua tulang jk_skeleton ada (nama Mannequin + jaw + cloth_* + IK), induk sama, posisi <= 1 mm x skala, satu akar `root`,
 tanpa empty; mesh: 1 objek, tris <= anggaran LOD (docs/20 J7), tepat 1 slot material M_Jerangkong, <= 4 influence, bobot
 ternormalisasi, 0 vertex tanpa bobot, vertex tulang potongan kaku (lengan, tangan, kaki, tengkorak, rahang) tepat 1 tulang
 bobot 1,0, tinggi = 2,19 m x skala (±1%), telapak z≈0, UV 0-1; socket JSON valid.
 --parts: parts.json (17 potongan, 14 bisa rontok, file SM ada) dan pivot SM: bbox SM + pivot = bbox vertex SK tulang-tulang potongan
 (toleransi 3% ukuran potongan; SM memakai geometri LOD1).
Keluar dengan kode 1 kalau ada yang gagal.
"""
import json
import re
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jk_skeleton as SK  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
fbx = Path(argv[0])
check_parts = "--parts" in argv
m = re.search(r"_LOD(\d)$", fbx.stem)
level = int(m.group(1)) if m else 0
BUDGET = {0: 35000, 1: 15000, 2: 6000, 3: 2500}[level]
base = re.sub(r"_LOD\d+$", "", fbx.stem)
sock_json = json.loads(fbx.with_name(base + "_sockets.json").read_text(encoding="utf-8"))
SCALE = float(sock_json["export_scale"])
RIGID = [b for p, bl in SK.PIECE_BONES.items() if p not in ("Ribs", "Spine", "Pelvis") for b in bl]

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
wscale = arm.matrix_world.to_scale().x                       # importer Blender bisa menaruh skala 0,01 di objek
UNIT = U if wscale > 0.5 else 1.0
B = {b.name: ((arm.matrix_world @ b.matrix_local).translation * UNIT / SCALE, b.parent.name if b.parent else None)
     for b in arm.data.bones}                                # ruang model (m)

# ---- tulang
spec = {n: (h, p) for n, p, h, _t, _c in SK.build_bones()}
missing = sorted(set(spec) - set(B))
check(f"{len(spec)} tulang jk_skeleton ada", not missing, f"hilang: {missing[:5]}" if missing else "")
extra = sorted(set(B) - set(spec))
check("tidak ada tulang tambahan", not extra, f"{extra[:5]}")
roots = [n for n, v in B.items() if v[1] is None]
check("satu akar bernama root", roots == ["root"], f"{roots}")
bad_par = [n for n in spec if n in B and B[n][1] != spec[n][1]]
check("hierarki sama dengan jk_skeleton", not bad_par, f"{bad_par[:5]}")
worst = max(((B[n][0] - Vector(spec[n][0])).length * 1000 for n in spec if n in B), default=0)
check("posisi tulang = jk_skeleton (<= 1 mm, ruang model)", worst <= 1.0, f"terburuk {worst:.3f} mm")
check("tidak ada empty", not [o for o in new if o.type == "EMPTY"], "")

# ---- mesh
check("tepat 1 objek mesh", len(meshes) == 1, f"{len(meshes)}")
mesh = meshes[0]
me = mesh.data
tris = sum(len(p.vertices) - 2 for p in me.polygons)
check(f"tris LOD{level} <= {BUDGET}", tris <= BUDGET, f"{tris}")
mats = [mt.name.split(".")[0] for mt in me.materials]
check("1 slot material M_Jerangkong", mats == ["M_Jerangkong"], f"{mats}")
vgn = {vg.index: vg.name for vg in mesh.vertex_groups}
check("grup vertex hanya ke tulang yang ada", all(n in B for n in vgn.values()), "")
mx = unw = nonnorm = rigid_bad = 0
for v in me.vertices:
    gs = [(vgn[g.group], g.weight) for g in v.groups if g.weight > 1e-4]
    mx = max(mx, len(gs))
    if not gs:
        unw += 1
        continue
    if abs(sum(w for _, w in gs) - 1.0) > 0.01:
        nonnorm += 1
    if any(n in RIGID for n, _ in gs) and not (len(gs) == 1 and gs[0][1] > 0.999):
        rigid_bad += 1
check("<= 4 influence per vertex", mx <= 4, f"maks {mx}")
check("0 vertex tanpa bobot", unw == 0, f"{unw}")
check("bobot ternormalisasi (±0,01)", nonnorm == 0, f"{nonnorm}")
check("potongan kaku: tepat 1 tulang bobot 1,0", rigid_bad == 0, f"{rigid_bad} vertex")
mw = mesh.matrix_world
zs = [(mw @ v.co).z * UNIT for v in me.vertices]
h = (max(zs) - min(zs)) / SCALE
check("tinggi model 2,19 m (±1%) setelah dibagi skala", abs(h - 2.19) <= 0.022, f"{h:.3f} m x {SCALE} = {h * SCALE:.2f} m")
check("telapak di z≈0", abs(min(zs)) / SCALE <= 0.01, f"{min(zs):.4f} m")
uv = me.uv_layers.active
check("UV 0-1", uv is not None and all(-0.001 <= c <= 1.001 for d in uv.data for c in d.uv), "")
bad_s = [s["name"] for s in sock_json["sockets"] if s["bone"] not in B]
check("socket JSON: tulang induk ada (>= 8)", not bad_s and len(sock_json["sockets"]) >= 8, f"{len(sock_json['sockets'])} socket")

# ---- potongan & pivot SM
if check_parts:
    pj = json.loads(fbx.with_name("SK_Jerangkong_parts.json").read_text(encoding="utf-8"))
    parts = pj["parts"]
    det = [p for p in parts if p["detachable"]]
    check("17 potongan, 14 bisa rontok", len(parts) == 17 and len(det) == 14, f"{len(parts)}/{len(det)}")
    sm_scale = pj["sm_scale"]
    worst_rel, worst_name, missing_sm = 0.0, "", []
    for p in det:
        f = fbx.parent / "Jerangkong_Parts" / (p["static_mesh"] + ".fbx")
        if not f.exists():
            missing_sm.append(p["static_mesh"])
            continue
        objs = import_fbx(f)
        sm = next(o for o in objs if o.type == "MESH")
        smw = sm.matrix_world
        s_u = U if smw.to_scale().x > 0.5 else 1.0
        pts = [(smw @ v.co) * s_u / sm_scale + Vector(p["pivot_model_m"]) for v in sm.data.vertices]
        # vertex SK milik tulang-tulang potongan (ruang model)
        gis = {mesh.vertex_groups[b].index for b in p["bones"] if b in mesh.vertex_groups}
        sk_pts = [(mw @ v.co) * UNIT / SCALE for v in me.vertices
                  if sum(g.weight for g in v.groups if g.group in gis) > 0.5]
        lo1 = Vector([min(q[i] for q in pts) for i in range(3)])
        hi1 = Vector([max(q[i] for q in pts) for i in range(3)])
        lo2 = Vector([min(q[i] for q in sk_pts) for i in range(3)])
        hi2 = Vector([max(q[i] for q in sk_pts) for i in range(3)])
        size = (hi2 - lo2).length
        rel = max((lo1 - lo2).length, (hi1 - hi2).length) / max(size, 1e-6)
        if rel > worst_rel:
            worst_rel, worst_name = rel, p["piece"]
        for o in objs:
            bpy.data.objects.remove(o, do_unlink=True)
    check("file SM ada untuk 14 potongan", not missing_sm, f"{missing_sm}")
    check("pivot SM cocok dengan potongan di SK (<= 3% ukuran)", worst_rel <= 0.03, f"terburuk {worst_name} {worst_rel * 100:.2f}%")

passed = sum(1 for r in results if r[1])
print(f"\nHASIL: {passed}/{len(results)} lulus — {fbx.name}")
sys.exit(0 if passed == len(results) else 1)
