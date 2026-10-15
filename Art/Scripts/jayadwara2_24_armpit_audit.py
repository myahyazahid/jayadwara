"""Jayadwara2 — audit ketiak (lengan terangkat). Laporan tepi terbuka di zona ketiak + render close-up per pose.

  blender --background Art/Blender/jayadwara2/jayadwara2_v06_revisi.blend --python Art/Scripts/jayadwara2_24_armpit_audit.py -- [outdir]
Temuan developer (13 Okt 2026, Play UE): saat memukul (lengan ke depan-atas, retarget MM_Attack_*) ketiak robek/bolong.
Pose didefinisikan lewat arah tulang (ruang dunia; karakter menghadap -Y, kiri karakter = +X), lengan kanan (-X).
Hasil: PNG per pose + `_sheet.png` di outdir (default Art/Export/_jd2/armpit), tabel celah di stdout.
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else Path(r"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2\armpit")
OUT.mkdir(parents=True, exist_ok=True)

arm = bpy.data.objects["JD2_Armature"]
body = bpy.data.objects["JD2_Body"]
scene = bpy.context.scene
if arm.animation_data:          # action uji pose (JD_PoseTest) menimpa pose manual
    arm.animation_data.action = None
arm.data.pose_position = "POSE"


def V(x, y, z):
    return Vector((x, y, z)).normalized()


def reset():
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def aim(bone, direction):
    pb = arm.pose.bones[bone]
    cur = (pb.tail - pb.head).normalized()
    R = cur.rotation_difference(direction).to_matrix().to_4x4()
    h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()


# (nama, arah lengan atas kanan, arah lengan bawah kanan) — kanan = -X, depan = -Y
POSES = [
    ("rest", None, None),
    ("depan_90", V(0, -1, 0), V(0, -1, 0)),               # pukulan lurus setinggi bahu
    ("depan_atas", V(-0.15, -0.7, 0.7), V(0.1, -0.5, 0.85)),   # seperti foto: siku di atas bahu
    ("samping_90", V(-1, 0, 0), V(-1, 0, 0)),             # T-pose
    ("atas", V(-0.2, -0.1, 1), V(0, 0, 1)),               # tangan ke atas
    ("guard", V(-0.3, -0.75, -0.2), V(0.3, -0.3, 0.9)),   # kepalan di depan dagu
]


def positions():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    me = ev.to_mesh()
    P = np.array([ev.matrix_world @ v.co for v in me.vertices], float)
    ev.to_mesh_clear()
    return P


# ------------------------------------------------------------------ tepi terbuka (boundary) & pasangan jahitan
me = body.data
E = np.array([e.vertices[:] for e in me.edges])
cnt = np.zeros(len(E), int)
key = {tuple(sorted(e)): i for i, e in enumerate(E)}
for p in me.polygons:
    vs = list(p.vertices)
    for a, b in zip(vs, vs[1:] + vs[:1]):
        cnt[key[tuple(sorted((a, b)))]] += 1
bnd = E[cnt == 1]
reset()
rest = positions()
bv = np.unique(bnd)
# jahitan split = vertex boundary yang punya kembar (posisi sama) di rest
from collections import defaultdict
grid = defaultdict(list)
for v in bv:
    grid[tuple(np.round(rest[v], 4))].append(v)
pairs = [g for g in grid.values() if len(g) >= 2]
print(f"tepi terbuka: {len(bnd)}, vertex boundary {len(bv)}, pasangan kembar (jahitan split) {len(pairs)}")
for side, sx in (("kanan", -1), ("kiri", 1)):
    sel = [g for g in pairs if np.sign(rest[g[0]][0]) == sx]
    zs = [rest[g[0]][2] for g in sel]
    if zs:
        print(f"  jahitan {side}: {len(sel)} pasangan, z {min(zs):.3f}..{max(zs):.3f}, |x| {np.mean([abs(rest[g[0]][0]) for g in sel]):.3f}")

# ------------------------------------------------------------------ pose + celah + render
seam_r = [g for g in pairs if rest[g[0]][0] < 0]
cam_data = bpy.data.cameras.new("AUD_cam")
cam = bpy.data.objects.new("AUD_cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.lens = 50
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "TEXTURE"
scene.display.shading.show_backface_culling = True     # lubang terlihat tembus, bukan sisi dalam
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.film_transparent = False
world = scene.world or bpy.data.worlds.new("W")
scene.world = world

shots = []
for name, ua, la in POSES:
    reset()
    if ua is not None:
        aim("upperarm_r", ua)
        aim("lowerarm_r", la)
    P = positions()
    gaps = [max(np.linalg.norm(P[a] - P[b]) for a in g for b in g) for g in seam_r]
    gaps = np.array(gaps) if gaps else np.zeros(1)
    print(f"{name:12s} celah jahitan kanan: maks {gaps.max() * 100:5.1f} cm, rerata {gaps.mean() * 100:4.1f} cm, >2 cm {int((gaps > 0.02).sum())}")
    # kamera: dari kanan-bawah-depan, mengarah ke ketiak kanan
    sh = arm.pose.bones["upperarm_r"].head
    target = Vector((sh.x * 0.85, sh.y, sh.z - 0.12))
    for tag, d in (("bawah", Vector((-0.9, -0.5, -0.55))), ("samping", Vector((-1.0, 0.25, 0.05)))):
        cam.location = target + d.normalized() * 0.9
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        f = OUT / f"{name}_{tag}.png"
        scene.render.filepath = str(f)
        bpy.ops.render.render(write_still=True)
        shots.append(f)

# lembar kontak
try:
    from PIL import Image
    ims = [Image.open(p) for p in shots]
    cols = 4
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * 640, rows * 640), "white")
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB"), ((i % cols) * 640, (i // cols) * 640))
    sheet.save(OUT / "_sheet.png")
    print("sheet", OUT / "_sheet.png")
except Exception as ex:   # PIL tidak ada di Python Blender
    print("tanpa sheet:", ex)
