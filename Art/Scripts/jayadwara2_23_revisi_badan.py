"""Jayadwara2 — revisi badan 14 Okt 2026 (feedback developer): kaki sedikit lebih pendek / badan lebih panjang (tinggi tetap),
dan satu helai kain tengah BELAKANG supaya bokong tidak terekspos.

  blender --background Art/Blender/jayadwara2_v05_rig_r3.blend --python Art/Scripts/jayadwara2_23_revisi_badan.py -- \
      [--out Art/Blender/jayadwara2_v06_revisi.blend] [--leg-cut 0.045] [--no-back]
File v05 tidak ditimpa. Sesudahnya: jayadwara2_14_export.py & jayadwara2_16_make_lods.py pada v06, lalu UE
(ue_import_jayadwara2.py, ue_setup_jayadwara2.py) dan jubah (jayadwara2_cape_01_intake --body v06 ... ).

1) Proporsi (remap tinggi rest): f(z) = z*k1 di bawah sendi pinggul Z1 (kaki memendek --leg-cut m), lalu segmen Z1..Z2
   (pinggul -> dada) memanjang k2 supaya Z2 tetap; di atas Z2 (dada, bahu, kepala) tidak berubah -> tinggi total sama.
   Vertex lengan (bobot upperarm/lowerarm/hand/jari) tidak ikut (digeser sebanding (1 - bobot lengan) supaya ketiak mulus);
   tulang lengan & clavicle tetap; tulang lain, socket, dan JD2_Source ikut di-remap.
2) Kain tengah belakang: lembar kain tengah DEPAN (|x| < 0,12, y < -0,19, z 0,30-1,05) diduplikasi di mesh yang sama
   (bobot ikut), dicerminkan ke belakang (y -> -y, normal dibalik), lalu tiap vertex didorong ke belakang sampai >= permukaan
   badan + CLEAR (raycast dari belakang) dan dibuat menggantung lurus (y tidak mengecil ke bawah).
"""
import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(ROOT / "Art" / "Blender" / "jayadwara2_v06_revisi.blend"))
ap.add_argument("--leg-cut", type=float, default=0.045, help="m, kaki memendek sebanyak ini (di sendi pinggul)")
ap.add_argument("--no-back", action="store_true")
args = ap.parse_args(argv)
assert "v05" not in Path(args.out).name

Z1, Z2 = 0.98, 1.40               # sendi pinggul (thigh head), dada (spine_04/05) — diukur dari skeleton v05
K1 = (Z1 - args.leg_cut) / Z1
K2 = (Z2 - Z1 * K1) / (Z2 - Z1)
ARM_KEYS = ("upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky")
CLEAR = 0.015
BACK_MIN_Y = -0.05                # sinar yang mengenai sesuatu di depan ini = lolos di antara kaki
TAB_X, TAB_Y, TAB_Z0, TAB_Z1 = 0.12, -0.19, 0.30, 1.05


def f(z):
    if z <= Z1:
        return z * K1
    if z < Z2:
        return Z1 * K1 + (z - Z1) * K2
    return z


body = bpy.data.objects["JD2_Body"]
arm = bpy.data.objects["JD2_Armature"]
if arm.animation_data:
    arm.animation_data.action = None
arm.data.pose_position = "REST"
gname = {g.index: g.name for g in body.vertex_groups}

# ------------------------------------------------------------------ 1) proporsi: mesh
me = body.data
mw = body.matrix_world
n_arm = 0
for v in me.vertices:
    wa = sum(g.weight for g in v.groups if any(k in gname[g.group] for k in ARM_KEYS))
    tot = sum(g.weight for g in v.groups) or 1.0
    wa = min(wa / tot, 1.0)
    p = mw @ v.co
    dz = (f(p.z) - p.z) * (1.0 - wa)
    if wa > 0.5:
        n_arm += 1
    v.co = mw.inverted() @ Vector((p.x, p.y, p.z + dz))
me.update()
src = bpy.data.objects.get("JD2_Source")
if src is not None:
    for v in src.data.vertices:
        p = src.matrix_world @ v.co
        v.co = src.matrix_world.inverted() @ Vector((p.x, p.y, f(p.z)))

# ------------------------------------------------------------------ 1) proporsi: skeleton & socket
bpy.context.view_layer.objects.active = arm
for o in bpy.context.view_layer.objects:
    o.select_set(o == arm)
bpy.ops.object.mode_set(mode="EDIT")
aw = arm.matrix_world
ai = aw.inverted()
n_b = 0
for eb in arm.data.edit_bones:
    if any(k in eb.name for k in ARM_KEYS) or eb.name.startswith("clavicle"):
        continue
    h, t = aw @ eb.head, aw @ eb.tail
    eb.head = ai @ Vector((h.x, h.y, f(h.z)))
    eb.tail = ai @ Vector((t.x, t.y, f(t.z)))
    n_b += 1
bpy.ops.object.mode_set(mode="OBJECT")
for s_ in (o for o in bpy.data.objects if o.name.startswith("SOCKET_") and "hand" not in o.name):
    p = s_.matrix_world.translation.copy()
    s_.matrix_world.translation = Vector((p.x, p.y, f(p.z)))
bones = arm.data.bones
print(f"proporsi: kaki x{K1:.3f} (memendek {args.leg_cut * 100:.1f} cm di pinggul), pinggul->dada x{K2:.3f}; {n_b} tulang & "
      f"mesh di-remap, {n_arm} vertex lengan tetap; pinggul {(aw @ bones['thigh_l'].head_local).z:.3f}, "
      f"lutut {(aw @ bones['calf_l'].head_local).z:.3f}, pelvis {(aw @ bones['pelvis'].head_local).z:.3f}")

# ------------------------------------------------------------------ 2) kain tengah belakang
if not args.no_back:
    bverts = [mw @ v.co for v in me.vertices]
    bvh_body = BVHTree.FromPolygons(bverts, [list(p.vertices) for p in me.polygons])
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    tab = [fc for fc in bm.faces if (lambda c: abs(c.x) < TAB_X and c.y < TAB_Y and TAB_Z0 < c.z < TAB_Z1)(fc.calc_center_median())]
    dup = bmesh.ops.duplicate(bm, geom=tab)
    nf = [g for g in dup["geom"] if isinstance(g, bmesh.types.BMFace)]
    nv = [g for g in dup["geom"] if isinstance(g, bmesh.types.BMVert)]
    for v in nv:
        v.co.y = -v.co.y                                   # cermin ke belakang (rest: ruang objek = dunia)
    bmesh.ops.reverse_faces(bm, faces=nf)
    # letakkan di permukaan bokong + CLEAR (sinar dari belakang di (x, z)); sinar yang lolos di antara kaki (mengenai kain
    # depan, y < BACK_MIN_Y) diabaikan. Per kolom (x, z) digeser sama -> tebal lembar terjaga. Lalu menggantung lurus:
    # dari atas ke bawah permukaan tidak boleh masuk lagi (kain jatuh dari titik terjauh bokong).
    cols = {}
    for v in nv:
        cols.setdefault((round(v.co.x / 0.01), round(v.co.z / 0.01)), []).append(v)
    target = {}
    for key, vs in cols.items():
        x, z = key[0] * 0.01, key[1] * 0.01
        hit, _, _, _ = bvh_body.ray_cast(Vector((x, 1.0, z)), Vector((0, -1, 0)), 2.0)
        target[key] = (hit.y + CLEAR) if (hit is not None and hit.y > BACK_MIN_Y) else None
    for x_key in sorted({k[0] for k in cols}):
        prev = None
        for z_key in sorted((k[1] for k in cols if k[0] == x_key), reverse=True):
            t = target[(x_key, z_key)]
            t = prev if t is None else (t if prev is None else max(t, prev))
            if t is None:
                continue
            vs = cols[(x_key, z_key)]
            inner = min(v.co.y for v in vs)
            for v in vs:
                v.co.y += t - inner
            prev = t
    bm.to_mesh(me)
    bm.free()
    me.update()
    print(f"kain tengah belakang: {len(nf)} muka dicerminkan dari kain tengah depan, jarak bebas {CLEAR * 100:.1f} cm")

body["jd2_revisi"] = f"14 Okt 2026: kaki -{args.leg_cut * 100:.1f} cm, badan x{K2:.3f}, kain tengah belakang"
bpy.ops.wm.save_as_mainfile(filepath=args.out, relative_remap=True)
print("disimpan ->", args.out)
