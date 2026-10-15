"""Audit karakter ber-skeleton Manny dari FBX: kontrak orientasi/tinggi, uji pose, peregangan, tepi terbuka, render.

Headless (scene kosong, tidak menyimpan .blend apa pun):
  blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- <file.fbx> --out <dir>
        [--height 1.806] [--max-strain 40] [--res 480] [--profil Art/Scripts/pose_profil/manny.json] [--kanvas M]
Contoh (model lama sebagai pembanding, lalu model baru):
  ... audit_karakter.py -- Art/Export/SK_Aksa.fbx --out Hermes/Art/aksa2/Audit/lama
  ... audit_karakter.py -- Hermes/Art/aksa2/Export/SK_Aksa2.fbx --out Hermes/Art/aksa2/Audit/baru
Lanjut: python -I Art/Scripts/banding_karakter.py --lama <dir lama> --baru <dir baru> --out <dir>

Hasil di <dir>:
  front/side/back_color.png + _mask.png  ortografis pose rest, kanvas sama dengan Art/Reference/ak_ref_*.png
                                         (760x1200, 1000 px = --height, telapak y=1100, tengah x=380) -> aksa_12_compare_sheet.py
  pose_<nama>_depan.png / _bawah.png     tiap pose: 3/4 depan, dan dari bawah-samping ke ketiak kanan (backface culling NYALA,
                                         jadi lubang terlihat tembus; pelajaran docs/25 R8)
  audit.json                             angka + PASS/FAIL tiap cek (dibaca banding_karakter.py)
Pose & tulang wajib dari --profil (JSON, default pose_profil/manny.json: 13 pose uji Aksa + 4 pose lengan untuk ketiak).
Skeleton lain (monster non-Manny) = profil sendiri dengan nama tulangnya; format dijelaskan di "catatan" manny.json.
Pose diterapkan di RUANG DUNIA dengan kontrak: menghadap -Y, kiri = +X, atas = +Z (dicek lewat "orientasi"; salah = GAGAL).
--kanvas: lebar/tinggi kanvas ortografis dalam m per 1000 px (default --height; naikkan untuk badan panjang/sayap lebar,
konsep lalu harus dibuat dengan kanvas yang sama). Raksasa: --height = tinggi di FBX (mis. 45 untuk boss yang di-bake 45 m); pose "down" & kamera ikut diskalakan.
Regangan (dasar vonis) = |panjang tepi pose - rest| / rest, persentil 99 semua tepi (%, tidak bergantung kerapatan mesh).
Peregangan = selisih panjang tepi terbesar vs rest (cm), per tulang berbobot terbesar (untuk menunjuk LOKASI masalah).
Exit code 0 = semua PASS, 1 = ada FAIL.
"""
import json
import math
import os
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not argv:
    print(__doc__)
    sys.exit(2)


def opt(name, default, cast=str):
    return cast(argv[argv.index(name) + 1]) if name in argv else default


FBX = Path(argv[0]).resolve()
OUT = Path(opt("--out", str(FBX.parent / ("audit_" + FBX.stem)))).resolve()
H = opt("--height", 1.806, float)
KANVAS = opt("--kanvas", H, float)               # m per 1000 px di render ortografis; > H untuk badan panjang/sayap lebar
MAX_STRAIN = opt("--max-strain", 40.0, float)   # % ; batas kasar, pembanding sebenarnya = model lama (banding_karakter.py)
RES = opt("--res", 480, int)
PROFIL_PATH = opt("--profil", str(Path(__file__).resolve().parent / "pose_profil" / "manny.json"))
OUT.mkdir(parents=True, exist_ok=True)

results = []


def check(name, ok, detail=""):
    results.append({"cek": name, "lulus": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


# ---------------------------------------------------------------- impor & satuan
if FBX.is_file() and FBX.stat().st_size < 1024 and FBX.read_bytes().startswith(b"version https://git-lfs"):
    print(f"GAGAL: {FBX} masih pointer Git LFS (file asli belum diunduh). Jalankan: git lfs pull --include=\"{FBX.name}\"")
    sys.exit(2)
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=str(FBX))
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
meshes = [o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers)]
if arm is None or not meshes:
    check("FBX berisi armature + mesh ter-skin", False, f"armature={arm is not None}, mesh ter-skin={len(meshes)}")
    (OUT / "audit.json").write_text(json.dumps({"fbx": str(FBX), "cek": results}, indent=1), encoding="utf-8")
    sys.exit(1)
scene = bpy.context.scene
bpy.context.view_layer.update()


def world_z_range():
    zs = [(o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices]
    return min(zs), max(zs)


z0, z1 = world_z_range()
if z1 - z0 > 20:                                   # data FBX dalam cm (kontrak export) -> skala objek akar 0,01 supaya meter
    for o in bpy.data.objects:
        if o.parent is None:
            o.scale = o.scale * 0.01
    bpy.context.view_layer.update()
    z0, z1 = world_z_range()
height = z1 - z0
check(f"tinggi {H:.3f} m -6/+2 cm", -0.06 <= height - H <= 0.02, f"{height:.3f} m")
check("telapak di z≈0 (±1 cm)", abs(z0) <= 0.01, f"{z0:.4f} m")

bones = arm.pose.bones
PROFIL = json.loads(Path(PROFIL_PATH).read_text(encoding="utf-8"))
SC = H / 1.806                                     # skala jarak (pose "down", kamera) relatif ke manusia 1,806 m
_pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
EXT = max(max(p[i] for p in _pts) - min(p[i] for p in _pts) for i in range(3))
SCK = max(EXT, H) / 1.806                          # skala jarak kamera: dimensi terbesar (badan panjang, sayap lebar)
need = PROFIL["tulang_wajib"]
missing = [n for n in need if n not in bones]
check(f"tulang wajib profil '{PROFIL['nama']}' ada", not missing, f"hilang: {missing}" if missing else f"{len(arm.data.bones)} tulang")
used = {o[0] for ops in PROFIL.get("pose", {}).values() for o in ops} | {t for d in PROFIL.get("arah", {}).values() for t in d}
undef = sorted(n for n in used if n not in bones)
check("semua tulang di pose profil ada", not undef, f"tidak ada: {undef}" if undef else "")
if missing or undef:
    (OUT / "audit.json").write_text(json.dumps({"fbx": str(FBX), "cek": results}, indent=1), encoding="utf-8")
    sys.exit(1)


def head_w(name):
    return arm.matrix_world @ bones[name].head


# kontrak orientasi: menghadap -Y, kiri karakter = +X, atas = +Z (pasangan tulang [dari, ke] di profil)
ori = PROFIL.get("orientasi", {})
for key, axis, sign, label in (("depan", 1, -1, "menghadap -Y"), ("kiri", 0, 1, "kiri karakter = +X"), ("atas", 2, 1, "atas = +Z")):
    for a_, b_ in ori.get(key, []):
        d = head_w(b_) - head_w(a_)
        ok = d[axis] * sign > 0.015 * SC and abs(d[axis]) >= max(abs(d[i]) for i in range(3) if i != axis) * (1.0 if key != "depan" else 0.5)
        check(f"{label} ({a_} -> {b_})", ok, f"vektor {tuple(round(c, 3) for c in d)}")

# ---------------------------------------------------------------- pose uji (dari profil)
AX = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}
POSES = {"rest": []}
POSES.update({k: v for k, v in PROFIL.get("pose", {}).items() if k != "rest"})
ARAH = PROFIL.get("arah", {})


def depth(name):
    n, b_ = 0, arm.data.bones[name]
    while b_.parent:
        n, b_ = n + 1, b_.parent
    return n


def reset_pose():
    if arm.animation_data:
        arm.animation_data.action = None
    arm.data.pose_position = "POSE"
    for pb in bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def set_world(pb, W):
    pb.matrix = arm.matrix_world.inverted() @ W
    bpy.context.view_layer.update()


def apply_ops(ops):
    for name, axis, val in sorted(ops, key=lambda o: depth(o[0])):     # induk dulu, lalu anak
        pb = bones[name]
        W = arm.matrix_world @ pb.matrix
        if axis == "down":
            set_world(pb, Matrix.Translation((0, 0, -val * SC)) @ W)
        else:
            h = W.translation.copy()
            set_world(pb, Matrix.Translation(h) @ Matrix.Rotation(math.radians(val), 4, AX[axis]) @ Matrix.Translation(-h) @ W)


def ujung(pb):
    """Ujung anatomis tulang (dunia): kepala anak utama (bukan twist/ik), kalau ada; selain itu ekor. Ekor tulang hasil impor
    FBX tidak sejajar anggota badan (mis. lowerarm Manny), jadi tidak dipakai untuk arah."""
    anak = [c for c in pb.children if "twist" not in c.name and not c.name.startswith("ik_")]
    if anak:
        c = max(anak, key=lambda c: (c.head - pb.head).length)
        if (c.head - pb.head).length > 1e-6:
            return arm.matrix_world @ c.head
    return arm.matrix_world @ pb.tail


def aim(name, direction):
    pb = bones[name]
    W = arm.matrix_world @ pb.matrix
    h = arm.matrix_world @ pb.head
    cur = (ujung(pb) - h).normalized()
    R = cur.rotation_difference(Vector(direction).normalized()).to_matrix().to_4x4()
    set_world(pb, Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ W)


def apply_pose(pname):
    reset_pose()
    if pname in POSES:
        apply_ops(POSES[pname])
    else:
        for name in sorted(ARAH[pname], key=depth):
            aim(name, ARAH[pname][name])


POSE_NAMES = list(POSES) + [k for k in ARAH if k not in POSES]

# ---------------------------------------------------------------- tulang dominan per vertex, tepi terbuka
dominant = {}
for o in meshes:
    names = {vg.index: vg.name for vg in o.vertex_groups}
    dom = []
    for v in o.data.vertices:
        g = max(v.groups, key=lambda g: g.weight, default=None)
        dom.append(names.get(g.group, "?") if g else "(tanpa bobot)")
    dominant[o.name] = dom

open_by_bone = {}
open_total = 0
for o in meshes:
    bm = bmesh.new()
    bm.from_mesh(o.data)
    for e in bm.edges:
        if e.is_boundary:
            open_total += 1
            b = dominant[o.name][e.verts[0].index]
            open_by_bone[b] = open_by_bone.get(b, 0) + 1
    bm.free()
top_open = sorted(open_by_bone.items(), key=lambda kv: -kv[1])[:8]
print(f"tepi terbuka (boundary): {open_total} | terbanyak per tulang: {top_open}")
unweighted = sum(1 for d in dominant.values() for b in d if b == "(tanpa bobot)")
check("0 vertex tanpa bobot", unweighted == 0, f"{unweighted}")


def edge_lengths():
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    for o in meshes:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        co = [mw @ v.co for v in me.vertices]
        out[o.name] = [(co[e.vertices[0]] - co[e.vertices[1]]).length for e in me.edges]
        ev.to_mesh_clear()
    return out


edges_v0 = {o.name: [e.vertices[0] for e in o.data.edges] for o in meshes}
reset_pose()
rest_len = edge_lengths()

# ---------------------------------------------------------------- render
try:
    scene.render.engine = "BLENDER_WORKBENCH"
except TypeError as e:
    print("engine:", e)
    raise
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
sh = scene.display.shading
sh.light = "STUDIO"
sh.show_backface_culling = True
sh.show_object_outline = False
sh.background_type = "WORLD"
imgs = [n.image for o in meshes for m in o.data.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]
def img_ok(i):          # tertanam, atau file ada dan bukan pointer Git LFS (±130 byte)
    f = bpy.path.abspath(i.filepath)
    return bool(i.packed_file) or (os.path.isfile(f) and os.path.getsize(f) > 1024)


tex_ok = bool(imgs) and all(img_ok(i) for i in imgs)
sh.color_type = "TEXTURE" if tex_ok else "MATERIAL"
print("warna render:", sh.color_type, f"({len(imgs)} tekstur" + ("" if tex_ok or not imgs else ", ada yang GAGAL dimuat -> pakai warna material") + ")")
if scene.world is None:
    scene.world = bpy.data.worlds.new("Audit")
arm.hide_render = True
for o in bpy.data.objects:
    if o.type == "EMPTY":
        o.hide_render = True

cam = bpy.data.objects.new("AuditCam", bpy.data.cameras.new("AuditCam"))
scene.collection.objects.link(cam)
scene.camera = cam


def look(loc, target):
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def render(path, w, h):
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


# ortografis rest (kanvas Art/Reference/ak_ref_*.png)
PX_PER_M = 1000.0 / KANVAS
W_, H_ = 760, 1200
cam.data.type = "ORTHO"
cam.data.ortho_scale = H_ / PX_PER_M
cam.data.clip_start, cam.data.clip_end = 0.05 * SC, 100 * SCK
cz = (1100 - H_ / 2) / PX_PER_M
ortho = {"front": ((0, -6 * SCK, cz), (90, 0, 0)), "side": ((6 * SCK, 0, cz), (90, 0, 90)), "back": ((0, 6 * SCK, cz), (90, 0, 180))}
for vname, (loc, rot) in ortho.items():
    cam.location = loc
    cam.rotation_euler = tuple(math.radians(a) for a in rot)
    scene.world.color = (0.82, 0.82, 0.82)
    color_type = sh.color_type
    sh.light = "STUDIO"
    render(OUT / f"{vname}_color.png", W_, H_)
    scene.world.color = (0, 0, 0)
    sh.light = "FLAT"
    sh.color_type = "SINGLE"
    sh.single_color = (1, 1, 1)
    render(OUT / f"{vname}_mask.png", W_, H_)
    sh.color_type = color_type

# perspektif per pose
sh.light = "STUDIO"
scene.world.color = (0.55, 0.6, 0.66)
cam.data.type = "PERSP"
cam.data.lens = 50
pose_data = {}
for pname in POSE_NAMES:
    apply_pose(pname)
    cur = edge_lengths()
    worst, strain = {}, []
    for oname, rl in rest_len.items():
        dom, v0 = dominant[oname], edges_v0[oname]
        for i, (a, b) in enumerate(zip(rl, cur[oname])):
            d = abs(a - b) * 100
            bone = dom[v0[i]]
            if d > worst.get(bone, 0.0):
                worst[bone] = d
            if a > 0.002:                              # regangan relatif; tepi < 2 mm diabaikan (derau)
                strain.append(abs(b - a) / a)
    top = sorted(worst.items(), key=lambda kv: -kv[1])[:3]
    mx = top[0][1] if top else 0.0
    strain.sort()
    p99 = 100 * strain[int(0.99 * (len(strain) - 1))] if strain else 0.0
    smax = 100 * strain[-1] if strain else 0.0
    pose_data[pname] = {"peregangan_maks_cm": round(mx, 2), "regangan_p99_persen": round(p99, 1), "regangan_maks_persen": round(smax, 1),
                        "terburuk": [[b, round(d, 2)] for b, d in top]}
    print(f"  {pname:18s} regangan p99 {p99:5.1f}% maks {smax:6.1f}% | peregangan maks {mx:5.2f} cm  "
          + " | ".join(f"{b} {d:.2f}" for b, d in top))
    kam = PROFIL.get("kamera", {})
    t_ = kam.get("tengah")
    if t_:
        mid = sum((head_w(n) for n in t_), Vector()) / len(t_)
    else:                                                                       # tanpa profil kamera: pusat bbox
        pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
        mid = sum(pts, Vector()) / len(pts)
    look(mid + Vector((1.8, -3.9, 0.5)) * SCK, mid)                              # 3/4 depan, dari kiri-depan karakter
    render(OUT / f"pose_{pname}_depan.png", RES, int(RES * 4 / 3))
    dk = kam.get("dekat")
    if dk:
        pit = head_w(dk["tulang"])
        cam.data.lens = 35
        look(pit + Vector(dk.get("offset", (-0.75, -0.35, -0.75))) * SC, pit + Vector(dk.get("bidik", (0.05, 0, -0.08))) * SC)
        render(OUT / f"pose_{pname}_{dk.get('nama', 'dekat')}.png", RES, RES)
        cam.data.lens = 50
reset_pose()

worst_pose = max((p for p in pose_data if p != "rest"), key=lambda p: pose_data[p]["regangan_p99_persen"])
wmax = pose_data[worst_pose]["regangan_p99_persen"]
check(f"regangan p99 <= {MAX_STRAIN}% di semua pose", wmax <= MAX_STRAIN, f"{wmax}% di {worst_pose}")

summary = {
    "fbx": str(FBX), "profil": PROFIL["nama"], "kamera_dekat": (PROFIL.get("kamera", {}).get("dekat") or {}).get("nama"),
    "kanvas_tinggi_m": KANVAS, "tinggi_m": round(height, 4), "tris": sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes),
    "jumlah_tulang": len(arm.data.bones), "jumlah_mesh": len(meshes),
    "slot_material": [m.name for o in meshes for m in o.data.materials if m],
    "tepi_terbuka": open_total, "tepi_terbuka_per_tulang": top_open, "pose": pose_data, "cek": results,
}
(OUT / "audit.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
passed = sum(1 for r in results if r["lulus"])
print(f"\nHASIL AUDIT: {passed}/{len(results)} lulus — {FBX.name} -> {OUT}")
sys.exit(0 if passed == len(results) else 1)
