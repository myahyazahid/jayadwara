"""Jayadwara2 — revisi badan 14 Okt 2026 (feedback developer): kaki sedikit lebih pendek / badan lebih panjang (tinggi tetap),
dan satu helai kain tengah BELAKANG supaya bokong tidak terekspos.

  blender --background Art/Blender/jayadwara2/jayadwara2_v05_rig_r3.blend --python Art/Scripts/jayadwara2_23_revisi_badan.py -- \
      [--out Art/Blender/jayadwara2/jayadwara2_v06_revisi.blend] [--leg-cut 0.045] [--no-back]
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
ap.add_argument("--out", default=str(ROOT / "Art" / "Blender" / "jayadwara2" / "jayadwara2_v06_revisi.blend"))
ap.add_argument("--leg-cut", type=float, default=0.045, help="m, kaki memendek sebanyak ini (di sendi pinggul)")
ap.add_argument("--no-back", action="store_true")
args = ap.parse_args(argv)
assert "v05" not in Path(args.out).name

Z1, Z2 = 0.98, 1.40               # sendi pinggul (thigh head), dada (spine_04/05) — diukur dari skeleton v05
K1 = (Z1 - args.leg_cut) / Z1
K2 = (Z2 - Z1 * K1) / (Z2 - Z1)
ARM_KEYS = ("upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky")
CLEAR = 0.015
PANEL_WIDEN = 1.25               # R7b: helai belakang sedikit lebih lebar (tepi menyelip di bawah helai samping)
PANEL_RED_UV = (0.0249, 0.9847)   # R7b: texel merah atlas badan = median warna helai samping belakang (0,48/0,07/0,11)
TOP_Z0, PANEL_TOP_Z = 0.93, 1.12   # R7b: tepi atas helai di atas TOP_Z0 diratakan ke PANEL_TOP_Z (balik sabuk)
BELT_Z = 1.07                     # R7b: di atas ini pangkal helai menyelip di belakang permukaan sabuk
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
    # R7b (feedback developer): helai harus SEBARIS dengan helai samping belakang, bukan terbenam di bokong & berdiri sendiri.
    # (a) serpihan kecil ikut terduplikasi dari kain depan -> hanya pulau terbesar dipakai
    nvset = set(nv)
    seen, isl = set(), []
    for v in nv:
        if v in seen:
            continue
        st, grp = [v], [v]
        seen.add(v)
        while st:
            c_ = st.pop()
            for e in c_.link_edges:
                w = e.other_vert(c_)
                if w in nvset and w not in seen:
                    seen.add(w)
                    st.append(w)
                    grp.append(w)
        isl.append(grp)
    isl.sort(key=len, reverse=True)
    junk = [v for g in isl[1:] for v in g]
    bmesh.ops.delete(bm, geom=junk, context="VERTS")
    nv = isl[0]
    # (b) sedikit lebih lebar supaya tepinya menyelip di bawah helai samping
    for v in nv:
        v.co.x *= PANEL_WIDEN
    # (c) kedalaman = permukaan luar helai samping belakang pada tinggi yang sama (+4 mm), minimal bokong + CLEAR;
    #     di bawah sabuk menyelip di belakang permukaan sabuk; di bawahnya menggantung lurus.
    B = np.array([tuple(p_) for p_ in bverts])
    flap = (B[:, 1] > 0.05) & (np.abs(B[:, 0]) > 0.08) & (np.abs(B[:, 0]) < 0.22)
    zs = np.arange(0.30, 1.10, 0.02)
    yf = np.array([np.percentile(B[flap & (np.abs(B[:, 2] - z) < 0.02), 1], 90) if (flap & (np.abs(B[:, 2] - z) < 0.02)).sum() > 5 else np.nan
                   for z in zs])
    ok = ~np.isnan(yf)
    yf = np.interp(zs, zs[ok], yf[ok])
    for _ in range(3):
        yf[1:-1] = 0.25 * yf[:-2] + 0.5 * yf[1:-1] + 0.25 * yf[2:]
    cols = {}
    for v in nv:
        cols.setdefault((round(v.co.x / 0.01), round(v.co.z / 0.01)), []).append(v)
    target = {}
    for key in cols:
        x, z = key[0] * 0.01, key[1] * 0.01
        hit, _, _, _ = bvh_body.ray_cast(Vector((x, 1.0, z)), Vector((0, -1, 0)), 2.0)
        body_y = hit.y if (hit is not None and hit.y > BACK_MIN_Y) else None
        t = float(np.interp(z, zs, yf)) + 0.004
        if body_y is not None:
            t = max(t, body_y + CLEAR)
            if z > BELT_Z:                                  # pangkal di bawah sabuk: di belakang permukaan sabuk
                k = min((z - BELT_Z) / 0.06, 1.0)
                t = t * (1 - k) + (body_y - 0.004) * k
        target[key] = t
    for x_key in sorted({k[0] for k in cols}):
        prev = None
        for z_key in sorted((k[1] for k in cols if k[0] == x_key), reverse=True):
            t = target[(x_key, z_key)]
            if prev is not None and z_key * 0.01 < BELT_Z:
                t = max(t, prev)
            vs = cols[(x_key, z_key)]
            inner = min(v.co.y for v in vs)
            for v in vs:
                v.co.y += t - inner
            prev = t
    # (c2) tepi atas rata: vertex tepi terbuka di atas TOP_Z0 diangkat ke PANEL_TOP_Z (di balik sabuk), pita di bawahnya
    #     ditarik sebagian -> tanpa celah hitam di antara sabuk dan pangkal helai.
    nvs = set(nv)
    top_edge = {v for v in nv if v.co.z > TOP_Z0 and any(e.is_boundary for e in v.link_edges)}
    for v in nv:
        if v in top_edge:
            v.co.z = max(v.co.z, PANEL_TOP_Z)
        elif v.co.z > TOP_Z0 - 0.05:
            k = (v.co.z - (TOP_Z0 - 0.05)) / (PANEL_TOP_Z - (TOP_Z0 - 0.05))
            v.co.z += max(0.0, PANEL_TOP_Z - 0.03 - v.co.z) * min(max(k, 0.0), 1.0) * 0.5
    # (d) tekstur: interior helai (merah bernoda / gelap dari atlas kain depan) dipetakan ke titik merah bersih yang sama dengan
    #     helai samping belakang; muka emas (list tepi & ornamen) tetap -> menyatu dengan helai lain.
    uvl = bm.loops.layers.uv.active
    img = next(n.image for n in me.materials[0].node_tree.nodes if n.type == "TEX_IMAGE" and n.image.name.startswith("Color"))
    W_, H_ = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(H_, W_, 4)
    faces = {f_ for v in nv for f_ in v.link_faces}
    n_red = 0
    for f_ in faces:
        u = sum(l[uvl].uv[0] for l in f_.loops) / len(f_.loops)
        w = sum(l[uvl].uv[1] for l in f_.loops) / len(f_.loops)
        c = px[int(w * (H_ - 1)), int(u * (W_ - 1)), :3]
        gold = c[0] > 0.45 and c[1] > 0.28 and c[1] > c[2] * 1.4            # emas: merah & hijau tinggi, biru rendah
        if not gold:
            for k, l in enumerate(f_.loops):
                l[uvl].uv = (PANEL_RED_UV[0] + 0.001 * (k % 2), PANEL_RED_UV[1] + 0.001 * ((k // 2) % 2))
            n_red += 1
    print(f"helai belakang: {n_red}/{len(faces)} muka interior -> merah bersih (sama dengan helai samping), emas tetap")
    print(f"helai belakang: {len(junk)} vertex serpihan dibuang, lebar x{PANEL_WIDEN}, kedalaman = helai samping "
          f"(y {yf.min():.3f}-{yf.max():.3f} m)")
    # tepi atas yang diratakan bisa membuat muka gepeng (luas nol): larutkan
    degen = [e for e in bm.edges if e.calc_length() < 1e-5]
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=list(bm.edges))
    bmesh.ops.delete(bm, geom=[f_ for f_ in bm.faces if f_.calc_area() < 1e-10], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    me.update()
    print(f"kain tengah belakang: {len(nf)} muka dicerminkan dari kain tengah depan, jarak bebas {CLEAR * 100:.1f} cm")

body["jd2_revisi"] = f"14 Okt 2026: kaki -{args.leg_cut * 100:.1f} cm, badan x{K2:.3f}, kain tengah belakang"
bpy.ops.wm.save_as_mainfile(filepath=args.out, relative_remap=True)
print("disimpan ->", args.out)
