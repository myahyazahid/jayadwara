"""Validasi FBX Aksa (Iterasi 1+) — Blender headless.

  blender --background --factory-startup --python Art/Scripts/validate_aksa.py -- Art/Export/SK_Aksa_Proxy.fbx [--max-tris 60000] [--require-uv] [--require-morph 8]

Dasar: Art/Reference/manny/SKM_Manny_Simple.fbx (impor yang sama) dan manny_rest.json. Cek:
 tulang: semua 88 tulang Manny ada, induknya sama, posisi <=1 mm dan orientasi <=0,5° (ruang dunia, meter); tulang tambahan hanya
 yang diizinkan (sash_*, jacket_*); tulang `root` ada dan satu-satunya akar; tinggi mesh 1,806 m ±2 cm, telapak di z≈0;
 mesh: 1 objek, tris <= batas, tepat 5 slot material berurutan (Skin, Eyes, Hair, Cloth, Gear), <=4 influence, bobot ternormalisasi,
 0 vertex tanpa bobot, grup vertex hanya ke tulang yang ada, UV 0-1 (jika --require-uv); socket JSON valid.
Keluar dengan kode 1 kalau ada yang gagal.
"""
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
MANNY = ROOT / "Art" / "Reference" / "manny" / "SKM_Manny_Simple.fbx"
MANNY_JSON = ROOT / "Art" / "Reference" / "manny" / "manny_rest.json"
ALLOWED_EXTRA = ("sash_", "jacket_")
SLOTS = ["M_Aksa_Skin", "M_Aksa_Eyes", "M_Aksa_Hair", "M_Aksa_Cloth", "M_Aksa_Gear"]

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
fbx = Path(argv[0])
max_tris = int(argv[argv.index("--max-tris") + 1]) if "--max-tris" in argv else 60000
require_uv = "--require-uv" in argv

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def load(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == "ARMATURE" and len(o.data.bones) > 10)
    meshes = [o for o in new if o.type == "MESH"]
    bones = {}
    for b in arm.data.bones:
        m = arm.matrix_world @ b.matrix_local
        bones[b.name] = (m.translation.copy(), m.to_3x3().normalized(), b.parent.name if b.parent else None)
    return arm, meshes, bones, new


for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
arm_a, meshes_a, A, _ = load(MANNY)
arm_b, meshes_b, B, new_b = load(fbx)
UNIT_B = 0.01 if max(v[0].z for v in B.values()) > 50 else 1.0     # FBX Aksa: data dalam cm (kontrak export), skala objek 1
B = {n: (t * UNIT_B, r, p) for n, (t, r, p) in B.items()}
manny_h = json.loads(MANNY_JSON.read_text(encoding="utf-8"))["height_m"]

# ---- tulang
missing = sorted(set(A) - set(B))
check("88 tulang Manny ada di FBX", not missing, f"hilang: {missing[:5]}" if missing else f"{len(A)} tulang")
extra = sorted(n for n in B if n not in A and n != "root")
bad_extra = [n for n in extra if not n.startswith(ALLOWED_EXTRA)]
check("tulang tambahan hanya sash_*/jacket_*", not bad_extra, f"tambahan: {len(extra)}" + (f", tidak diizinkan: {bad_extra}" if bad_extra else ""))
roots = [n for n, v in B.items() if v[2] is None]
check("satu akar bernama root", roots == ["root"], f"akar: {roots}")
bad_parent = [n for n in A if n in B and A[n][2] not in (B[n][2], None) and not (A[n][2] is None and B[n][2] == "root")]
bad_parent += [n for n in A if n in B and A[n][2] is None and B[n][2] != "root"]
check("hierarki sama dengan Manny (akar Manny di bawah root)", not bad_parent, f"menyimpang: {bad_parent[:5]}" if bad_parent else "")
worst_p = worst_r = 0.0
off = []
for n, (ta, ra, _) in A.items():
    if n not in B:
        continue
    tb, rb, _ = B[n]
    dp = (ta - tb).length * 1000
    ang = math.degrees(Matrix(ra.inverted() @ rb).to_quaternion().angle)
    worst_p, worst_r = max(worst_p, dp), max(worst_r, ang)
    if dp > 1.0 or ang > 0.5:
        off.append((n, round(dp, 2), round(ang, 2)))
check("posisi tulang = Manny (<=1 mm)", worst_p <= 1.0, f"terburuk {worst_p:.3f} mm")
check("orientasi tulang = Manny (<=0,5°)", worst_r <= 0.5, f"terburuk {worst_r:.3f}°" + (f" | {off[:4]}" if off else ""))
check("tidak ada empty di FBX", not [o for o in new_b if o.type == "EMPTY" and o.name != "Armature"], "")

# ---- mesh
check("tepat 1 objek mesh", len(meshes_b) == 1, f"{len(meshes_b)}")
mesh = meshes_b[0]
me = mesh.data
tris = sum(len(p.vertices) - 2 for p in me.polygons)
check(f"tris <= {max_tris}", tris <= max_tris, f"{tris}")
mats = [m.name for m in me.materials]
check("5 slot material berurutan", [m.split(".")[0] for m in mats] == SLOTS or [m.split(".")[0] for m in mats] == [s.replace("M_", "MI_") for s in SLOTS], f"{mats}")
vg_names = {vg.index: vg.name for vg in mesh.vertex_groups}
bad_groups = [n for n in vg_names.values() if n not in B]
check("grup vertex hanya ke tulang yang ada", not bad_groups, f"{bad_groups[:5]}")
mx = 0
unweighted = 0
nonnorm = 0
for v in me.vertices:
    gs = [g.weight for g in v.groups if g.weight > 1e-4]
    mx = max(mx, len(gs))
    if not gs:
        unweighted += 1
    elif abs(sum(gs) - 1.0) > 0.01:
        nonnorm += 1
check("<=4 influence per vertex", mx <= 4, f"maks {mx}")
check("0 vertex tanpa bobot", unweighted == 0, f"{unweighted}")
check("bobot ternormalisasi (±0,01)", nonnorm == 0, f"{nonnorm} vertex")
mw = mesh.matrix_world
zs = [(mw @ v.co).z for v in me.vertices]
height = (max(zs) - min(zs)) * (0.01 if max(zs) - min(zs) > 20 else 1.0)
check(f"tinggi mesh {manny_h:.3f} m -6/+2 cm (rambut boleh lebih rendah)", -0.06 <= height - manny_h <= 0.02, f"{height:.3f} m")
foot_z = min(zs) * (0.01 if max(zs) - min(zs) > 20 else 1.0)
check("telapak di z≈0 (±1 cm)", abs(foot_z) <= 0.01, f"{foot_z:.4f} m")
if require_uv:
    uv = me.uv_layers.active
    ok = uv is not None and all(-0.001 <= c <= 1.001 for d in uv.data for c in d.uv)
    check("UV 0-1", ok, "tidak ada UV" if uv is None else "")
    if uv is not None:
        degen = 0
        for p_ in me.polygons:
            pts = [uv.data[i].uv for i in range(p_.loop_start, p_.loop_start + p_.loop_total)]
            a2 = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
            if abs(a2) < 1e-10:
                degen += 1
        check("UV: segitiga degenerate <2% (dinding tipis trim/tali)", degen <= len(me.polygons) // 50, f"{degen} poligon")

# ---- morph target (--require-morph N)
if "--require-morph" in argv:
    need = int(argv[argv.index("--require-morph") + 1])
    keys = list(me.shape_keys.key_blocks) if me.shape_keys else []
    names = [k.name for k in keys[1:]]
    check(f">= {need} morph target", len(names) >= need, f"{len(names)}: {names}")
    unit_m = 0.01 if max(zs) - min(zs) > 20 else 1.0
    leak, empty = [], []
    if keys:
        basis = keys[0]
        for k in keys[1:]:
            moved = bad = 0
            for i, v in enumerate(me.vertices):
                d = (k.data[i].co - basis.data[i].co).length * unit_m
                if d > 1e-4:
                    moved += 1
                    if basis.data[i].co.z * unit_m < 1.45:
                        bad += 1
            if moved == 0:
                empty.append(k.name)
            if bad:
                leak.append((k.name, bad))
    check("morph target tidak menggeser vertex di bawah leher (z<1,45)", not leak, f"{leak}")
    check("tiap morph target menggeser vertex", not empty, f"kosong: {empty}")

# ---- socket
sj = fbx.with_name(fbx.stem + "_sockets.json")
if sj.exists():
    data = json.loads(sj.read_text(encoding="utf-8"))
    bad = [s["name"] for s in data["sockets"] if s["bone"] not in B]
    check("socket JSON: tulang induk ada", not bad and len(data["sockets"]) >= 7, f"{len(data['sockets'])} socket" + (f", salah: {bad}" if bad else ""))
else:
    check("socket JSON ada", False, str(sj))

passed = sum(1 for r in results if r[1])
print(f"\nHASIL: {passed}/{len(results)} lulus — {fbx.name}")
sys.exit(0 if passed == len(results) else 1)
