"""Jubah Jayadwara2 J1 — uji pose: jubah mengikuti JD2_Armature (constraint Copy Transforms = Copy Pose From Mesh di UE).

  blender --background Art/Blender/jayadwara2/jayadwara2_cape_v01_rig.blend --python Art/Scripts/jayadwara2_cape_11_pose_tests.py -- [tag]
Pose: rest, jalan kiri/kanan (sama dengan jayadwara2_17: paha ±28°/18°, lutut 30°), lari (paha 45°/-30°, lutut 70°),
tendang depan 90°, jongkok/lompat, badan berputar 25°, lengan terangkat depan, kepala miring.
Ukur: vertex jubah di dalam kapsul paha/betis (radius = p80 jarak kulit kaki ke tulang) dan regangan tepi jubah (maks/p99).
Keluaran: Art/Export/_jd2c/poses/<tag>_<pose>.png (samping | belakang 3/4 | depan 3/4) + tabel di stdout.
Catatan: ini KINEMATIK (J1). Kain bergerak & tabrakan sebenarnya di J3 (Chaos Cloth).
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
TAG = argv[0] if argv else "j1"
OUT = Path(r"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2c\poses")
OUT.mkdir(parents=True, exist_ok=True)

sc = bpy.context.scene
arm = bpy.data.objects["JD2_Armature"]
body = bpy.data.objects["JD2_Body"]
cape = bpy.data.objects["JD2_Cape"]
sc.frame_set(1)
if arm.animation_data:          # action uji R3 (JD_PoseTest) menimpa pose manual saat render; file tidak disimpan
    arm.animation_data.action = None

POSES = {
    "rest": [],
    "jalan_kiri": [("thigh_l", "X", -28), ("calf_l", "X", 6), ("thigh_r", "X", 18), ("calf_r", "X", 30),
                   ("upperarm_l", "X", 22), ("upperarm_r", "X", -22)],
    "jalan_kanan": [("thigh_r", "X", -28), ("calf_r", "X", 6), ("thigh_l", "X", 18), ("calf_l", "X", 30),
                    ("upperarm_r", "X", 22), ("upperarm_l", "X", -22)],
    "lari": [("thigh_l", "X", -45), ("calf_l", "X", 25), ("thigh_r", "X", 30), ("calf_r", "X", 70),
             ("spine_01", "X", -8), ("upperarm_l", "X", 40), ("upperarm_r", "X", -40)],
    "tendang": [("thigh_l", "X", -90), ("calf_l", "X", 10)],
    "jongkok": [("pelvis", "Z", 0), ("thigh_l", "X", -60), ("calf_l", "X", 90), ("thigh_r", "X", -60), ("calf_r", "X", 90)],
    "putar_badan": [("spine_03", "Z", 25), ("spine_05", "Z", 10)],
    "lengan_depan": [("upperarm_l", "X", -80), ("upperarm_r", "X", -80)],
    "kepala_miring": [("neck_01", "X", 8), ("neck_02", "X", 6), ("head", "X", 22), ("head", "Y", 20)],
}


def rot(bone, axis, deg):
    pb = arm.pose.bones[bone]
    h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()


def reset():
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


# kapsul kaki dari rest (kulit berbobot dominan ke tulang kaki)
gname = {g.index: g.name for g in body.vertex_groups}
bones = arm.data.bones
LEG = {"thigh": ("thigh", "calf"), "calf": ("calf", "foot")}


def seg_dist(P, a, b):
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


caps = []
for sd in "lr":
    for key, (b0, b1) in LEG.items():
        a = np.array(arm.matrix_world @ bones[f"{b0}_{sd}"].head_local)
        b = np.array(arm.matrix_world @ bones[f"{b1}_{sd}"].head_local)
        pts = []
        for v in body.data.vertices:
            g = max(v.groups, key=lambda g: g.weight, default=None)
            if g is not None and gname[g.group].startswith(f"{key}") and gname[g.group].endswith(f"_{sd}"):
                pts.append(tuple(body.matrix_world @ v.co))
        r = float(np.percentile(seg_dist(np.array(pts), a, b), 80))
        caps.append((f"{key}_{sd}", b0 + "_" + sd, b1 + "_" + sd, r))
print("kapsul kaki (radius cm):", {n: round(r * 100, 1) for n, _, _, r in caps})


def evaluated(o):
    dg = bpy.context.evaluated_depsgraph_get()
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    P = np.array([o.matrix_world @ v.co for v in m.vertices])
    e.to_mesh_clear()
    return P


edges = np.array([tuple(e.vertices) for e in cape.data.edges])
rest_len = None

# render
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"
sh.color_type = "TEXTURE"
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
sc.world.color = (0.45, 0.5, 0.55)
for o in bpy.data.objects:
    o.hide_render = o not in (body, cape)
cd = bpy.data.cameras.new("c_pose")
cam = bpy.data.objects.new("c_pose", cd)
sc.collection.objects.link(cam)
sc.camera = cam
cd.type, cd.ortho_scale = "ORTHO", 2.2
sc.render.resolution_x, sc.render.resolution_y = 640, 760

rows = []
for name, ops in POSES.items():
    reset()
    for b, ax, d in ops:
        if d:
            rot(b, ax, d)
    if name == "jongkok":                                   # pinggul turun supaya telapak tetap di lantai (perkiraan)
        arm.pose.bones["pelvis"].location = (0, 0, 0)
        pb = arm.pose.bones["pelvis"]
        pb.matrix = Matrix.Translation((0, 0.05, -0.32)) @ pb.matrix
        bpy.context.view_layer.update()
    C = evaluated(cape)
    L = np.linalg.norm(C[edges[:, 0]] - C[edges[:, 1]], axis=1)
    if rest_len is None:
        rest_len = np.maximum(L, 1e-5)
        C0 = C.copy()
    strain = L / rest_len - 1
    inside = {}
    pbm = {pb.name: pb for pb in arm.pose.bones}
    for n, b0, b1, r in caps:
        a = np.array(arm.matrix_world @ pbm[b0].head)
        b = np.array(arm.matrix_world @ pbm[b1].head)
        inside[n] = int((seg_dist(C, a, b) < r - 0.005).sum())
    rows.append((name, inside, float(np.percentile(strain, 99)), float(strain.max())))
    hot = strain > 0.3
    if hot.any():
        mid = (C0[edges[hot, 0]] + C0[edges[hot, 1]]) / 2
        print(f"  {name}: {int(hot.sum())} tepi >30% di z p5/50/95 {np.round(np.percentile(mid[:, 2], [5, 50, 95]), 2)}, "
              f"|x| {np.round(np.percentile(np.abs(mid[:, 0]), [5, 50, 95]), 2)}, y {np.round(np.percentile(mid[:, 1], [5, 50, 95]), 2)}")
    imgs = []
    for view, loc in (("samping", (6, 0, 0.95)), ("belakang34", (3.4, 4.6, 1.2)), ("depan34", (-3.4, -4.6, 1.2))):
        cam.location = Vector(loc)
        cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        f = OUT / f"_{TAG}_{name}_{view}.png"
        sc.render.filepath = str(f)
        bpy.ops.render.render(write_still=True)
        imgs.append(f)
    # gabung 3 view jadi satu PNG
    ims = [bpy.data.images.load(str(f)) for f in imgs]
    w, h = ims[0].size
    big = bpy.data.images.new(f"{name}_sheet", w * 3, h)
    px = np.zeros((h, w * 3, 4), dtype=np.float32)
    for k, im in enumerate(ims):
        px[:, k * w:(k + 1) * w] = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        bpy.data.images.remove(im)
    big.pixels = px.ravel()
    big.filepath_raw = str(OUT / f"{TAG}_{name}.png")
    big.file_format = "PNG"
    big.save()
    for f in imgs:
        f.unlink()
reset()

print("=" * 70)
print(f"{'pose':14s} {'tembus kapsul kaki (vertex)':52s} regangan p99 / maks")
for name, inside, p99, mx in rows:
    print(f"{name:14s} {str(inside):52s} {p99 * 100:5.1f}% / {mx * 100:5.1f}%")
print("=" * 70)
