"""Audit karakter ber-skeleton Manny dari FBX: kontrak orientasi/tinggi, uji pose, peregangan, tepi terbuka, render.

Headless (scene kosong, tidak menyimpan .blend apa pun):
  blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- <file.fbx> --out <dir>
        [--height 1.806] [--max-strain 40] [--res 480]
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
Pose: 13 pose uji Aksa (aksa_13_pose_tests.py) + 4 pose lengan untuk ketiak (jayadwara2_24_armpit_audit.py), diterapkan di
RUANG DUNIA dengan kontrak: karakter menghadap -Y, kiri karakter = +X, atas = +Z (dicek; kalau salah, audit GAGAL).
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
MAX_STRAIN = opt("--max-strain", 40.0, float)   # % ; batas kasar, pembanding sebenarnya = model lama (banding_karakter.py)
RES = opt("--res", 480, int)
OUT.mkdir(parents=True, exist_ok=True)

results = []


def check(name, ok, detail=""):
    results.append({"cek": name, "lulus": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


# ---------------------------------------------------------------- impor & satuan
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
need = ["pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head", "clavicle_l", "clavicle_r", "upperarm_l", "upperarm_r",
        "lowerarm_l", "lowerarm_r", "hand_l", "hand_r", "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l", "foot_r", "ball_l", "ball_r"]
missing = [n for n in need if n not in bones]
check("tulang utama Manny ada", not missing, f"hilang: {missing}" if missing else f"{len(arm.data.bones)} tulang")
if missing:
    (OUT / "audit.json").write_text(json.dumps({"fbx": str(FBX), "cek": results}, indent=1), encoding="utf-8")
    sys.exit(1)


def head_w(name):
    return arm.matrix_world @ bones[name].head


# kontrak orientasi: menghadap -Y (ujung kaki di depan tumit), kiri karakter = +X
fwd = ((head_w("ball_l") - head_w("foot_l")) + (head_w("ball_r") - head_w("foot_r"))) / 2
left = head_w("thigh_l") - head_w("thigh_r")
check("menghadap -Y (ball di depan foot)", fwd.y < -0.03 and abs(fwd.y) > abs(fwd.x), f"arah kaki {tuple(round(c, 3) for c in fwd)}")
check("kiri karakter = +X (thigh_l di +X)", left.x > 0.05, f"thigh_l - thigh_r = {left.x:.3f} m")
check("tegak (head di atas pelvis)", head_w("head").z - head_w("pelvis").z > 0.4, "")

# ---------------------------------------------------------------- pose uji
AX = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}
POSES = {   # = aksa_13_pose_tests.py (operasi tulang, sumbu dunia, derajat; "down" = turunkan pelvis, meter)
    "rest": [],
    "kuda_kuda": [("pelvis", "down", 0.20), ("thigh_l", "y", -48), ("thigh_r", "y", 48), ("calf_l", "y", 36), ("calf_r", "y", -36),
                  ("upperarm_l", "x", -55), ("upperarm_r", "x", -55), ("lowerarm_l", "x", -75), ("lowerarm_r", "x", -75),
                  ("foot_l", "y", 12), ("foot_r", "y", -12)],
    "pukul": [("spine_02", "z", 18), ("spine_03", "z", 14), ("upperarm_r", "x", -80), ("lowerarm_r", "x", -8),
              ("upperarm_l", "x", -60), ("lowerarm_l", "x", -95), ("thigh_l", "x", -20), ("calf_l", "x", 25), ("thigh_r", "x", 12)],
    "tendang_tinggi": [("spine_02", "x", 12), ("spine_03", "x", 10), ("thigh_r", "x", -105), ("calf_r", "x", 8), ("foot_r", "x", -25),
                       ("upperarm_l", "y", -30), ("upperarm_r", "y", 55), ("lowerarm_r", "x", -40), ("pelvis", "down", 0.05)],
    "dodge": [("spine_01", "x", 12), ("spine_02", "x", 14), ("spine_03", "x", 14), ("neck_01", "x", 8), ("pelvis", "down", 0.08),
              ("thigh_l", "x", -25), ("calf_l", "x", 35), ("thigh_r", "x", 18), ("upperarm_l", "x", -40), ("upperarm_r", "x", -40),
              ("lowerarm_l", "x", -70), ("lowerarm_r", "x", -70)],
    "jongkok": [("pelvis", "down", 0.46), ("spine_01", "x", -12), ("spine_02", "x", -14), ("thigh_l", "x", -100), ("thigh_r", "x", -100),
                ("calf_l", "x", 118), ("calf_r", "x", 118), ("foot_l", "x", -20), ("foot_r", "x", -20),
                ("upperarm_l", "x", -45), ("upperarm_r", "x", -45)],
    "lari": [("thigh_l", "x", -65), ("calf_l", "x", 75), ("foot_l", "x", -15), ("thigh_r", "x", 25), ("calf_r", "x", 30),
             ("upperarm_l", "x", 45), ("lowerarm_l", "x", -80), ("upperarm_r", "x", -55), ("lowerarm_r", "x", -85),
             ("spine_02", "z", -12), ("spine_03", "x", -8)],
    "lompat": [("pelvis", "down", 0.05), ("thigh_l", "x", -50), ("calf_l", "x", 70), ("thigh_r", "x", -35), ("calf_r", "x", 60),
               ("upperarm_l", "y", -110), ("upperarm_r", "y", 110)],
    "tendang_samping": [("spine_02", "y", -14), ("thigh_r", "y", 85), ("calf_r", "y", 5), ("upperarm_l", "y", -40), ("upperarm_r", "y", 60),
                        ("pelvis", "down", 0.04)],
    "tangkis": [("upperarm_l", "x", -70), ("lowerarm_l", "x", -105), ("upperarm_r", "x", -75), ("lowerarm_r", "x", -100), ("spine_02", "x", -8)],
    "putar_badan": [("spine_01", "z", 22), ("spine_02", "z", 22), ("spine_03", "z", 22), ("neck_01", "z", -25), ("upperarm_l", "x", -30),
                    ("upperarm_r", "x", -30)],
    "lunge": [("pelvis", "down", 0.22), ("thigh_l", "x", -75), ("calf_l", "x", 85), ("thigh_r", "x", 35), ("calf_r", "x", 5),
              ("spine_02", "x", -10), ("upperarm_l", "x", -50), ("lowerarm_l", "x", -70)],
    "bungkuk": [("spine_01", "x", -25), ("spine_02", "x", -25), ("spine_03", "x", -20), ("neck_01", "x", 20), ("upperarm_l", "x", -20),
                ("upperarm_r", "x", -20), ("thigh_l", "x", -15), ("thigh_r", "x", -15)],
    "tangan_terangkat": [("clavicle_l", "y", -12), ("clavicle_r", "y", 12), ("upperarm_l", "y", -150), ("upperarm_r", "y", 150),
                         ("lowerarm_l", "y", -10), ("lowerarm_r", "y", 10)],
}


def V(x, y, z):
    return Vector((x, y, z)).normalized()


AIM = {     # = jayadwara2_24_armpit_audit.py: arah lengan atas & bawah KANAN (dunia; kanan = -X, depan = -Y); kiri dicerminkan
    "lengan_depan_90": (V(0, -1, 0), V(0, -1, 0)),
    "lengan_depan_atas": (V(-0.15, -0.7, 0.7), V(0.1, -0.5, 0.85)),
    "lengan_samping_90": (V(-1, 0, 0), V(-1, 0, 0)),
    "lengan_guard": (V(-0.3, -0.75, -0.2), V(0.3, -0.3, 0.9)),
}
ORDER = ["pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "neck_02", "head", "clavicle_l", "clavicle_r",
         "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r", "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l",
         "foot_r", "ball_l", "ball_r"]


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
    for name, axis, val in sorted(ops, key=lambda o: ORDER.index(o[0])):
        pb = bones[name]
        W = arm.matrix_world @ pb.matrix
        if axis == "down":
            set_world(pb, Matrix.Translation((0, 0, -val)) @ W)
        else:
            h = W.translation.copy()
            set_world(pb, Matrix.Translation(h) @ Matrix.Rotation(math.radians(val), 4, AX[axis]) @ Matrix.Translation(-h) @ W)


def aim(name, direction):
    pb = bones[name]
    W = arm.matrix_world @ pb.matrix
    h = arm.matrix_world @ pb.head
    cur = (arm.matrix_world @ pb.tail - h).normalized()
    R = cur.rotation_difference(direction).to_matrix().to_4x4()
    set_world(pb, Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ W)


def apply_pose(pname):
    reset_pose()
    if pname in POSES:
        apply_ops(POSES[pname])
    else:
        up_r, low_r = AIM[pname]
        mirror = lambda d: Vector((-d.x, d.y, d.z))
        for side, up, low in (("r", up_r, low_r), ("l", mirror(up_r), mirror(low_r))):
            aim(f"upperarm_{side}", up)
            aim(f"lowerarm_{side}", low)


POSE_NAMES = list(POSES) + list(AIM)

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
PX_PER_M = 1000.0 / H
W_, H_ = 760, 1200
cam.data.type = "ORTHO"
cam.data.ortho_scale = H_ / PX_PER_M
cam.data.clip_start, cam.data.clip_end = 0.1, 50
cz = (1100 - H_ / 2) / PX_PER_M
ortho = {"front": ((0, -6, cz), (90, 0, 0)), "side": ((6, 0, cz), (90, 0, 90)), "back": ((0, 6, cz), (90, 0, 180))}
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
    chest = (head_w("spine_03") + head_w("neck_01")) / 2
    pel = head_w("pelvis")
    mid = (chest + pel) / 2
    look(mid + Vector((1.6, -3.4, 0.5)) * (H / 1.806), mid)                      # 3/4 depan, dari kiri-depan karakter
    render(OUT / f"pose_{pname}_depan.png", RES, int(RES * 4 / 3))
    pit = head_w("upperarm_r")
    cam.data.lens = 35
    look(pit + Vector((-0.75, -0.35, -0.75)) * (H / 1.806), pit + Vector((0.05, 0, -0.08)))   # ketiak kanan dari bawah-samping
    render(OUT / f"pose_{pname}_bawah.png", RES, RES)
    cam.data.lens = 50
reset_pose()

worst_pose = max((p for p in pose_data if p != "rest"), key=lambda p: pose_data[p]["regangan_p99_persen"])
wmax = pose_data[worst_pose]["regangan_p99_persen"]
check(f"regangan p99 <= {MAX_STRAIN}% di semua pose", wmax <= MAX_STRAIN, f"{wmax}% di {worst_pose}")

summary = {
    "fbx": str(FBX), "kanvas_tinggi_m": H, "tinggi_m": round(height, 4), "tris": sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes),
    "jumlah_tulang": len(arm.data.bones), "jumlah_mesh": len(meshes),
    "slot_material": [m.name for o in meshes for m in o.data.materials if m],
    "tepi_terbuka": open_total, "tepi_terbuka_per_tulang": top_open, "pose": pose_data, "cek": results,
}
(OUT / "audit.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
passed = sum(1 for r in results if r["lulus"])
print(f"\nHASIL AUDIT: {passed}/{len(results)} lulus — {FBX.name} -> {OUT}")
sys.exit(0 if passed == len(results) else 1)
