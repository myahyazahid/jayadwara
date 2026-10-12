"""Jerangkong Iterasi 1 (jalur B, docs/20) — armature + potongan kaku dari mesh Tripo + bobot + socket.

Jalankan headless dari hasil impor:
  blender --background Art/Blender/jerangkong_v01_tripo.blend --python Art/Scripts/jerangkong_10_build.py
Hasil:
  Art/Blender/jerangkong_v02_rig.blend   JK_Armature (Mannequin + jaw + cloth_*), 17 objek JK_P_<Potongan> ber-Armature
                                         modifier, socket SOCKET_*; JK_Source disembunyikan (acuan)
  Art/Export/_jk_faces.npz               per segitiga JK_Source: label tulang + UV (input make_textures_jerangkong.py)

Aturan bobot (docs/20 6.5, disesuaikan): potongan yang bisa rontok = 1 tulang, bobot 1,0, dipisah tegas dari tetangga
dan lubang potongannya ditutup (cap, UV ke kotak warna tulang gelap CAP_UV). Potongan poros yang berisi >1 tulang
(Ribs: rusuk+selangka/belikat, Spine: lumbar+leher, Pelvis: panggul+kain) tidak dipisah di dalam; vertex di batas
antar-tulang dibagi rata menurut segitiga di sekitarnya. Kain: bobot halus sepanjang rantai cloth_* (+pelvis di atas).
Jari ikut hand_* (kaku, docs/23 S7). LOD0 dikurangi ke <= TRI_BUDGET (docs/20 J7).
"""
import importlib
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jk_segment as G  # noqa: E402
import jk_skeleton as SK  # noqa: E402

importlib.reload(SK)
importlib.reload(G)

ROOT = r"C:\repository\unreal_engine\jayadwara"
OUT = os.path.join(ROOT, "Art", "Blender", "jerangkong_v02_rig.blend")
FACES_NPZ = os.path.join(ROOT, "Art", "Export", "_jk_faces.npz")
ARM_NAME = "JK_Armature"
TRI_BUDGET = 34000
CAP_UV = (0.0015, 0.0015)          # kotak 8x8 px di pojok kiri-bawah atlas, diisi warna tulang gelap oleh make_textures

scene = bpy.context.scene
src = bpy.data.objects["JK_Source"]


def coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.data.collections["JK_Jerangkong"].children.link(c)
    return c


# ------------------------------------------------------------------ 0. bersihkan hasil lama
for ob in list(bpy.data.objects):
    if ob.name == ARM_NAME or ob.name.startswith(("JK_P_", "SOCKET_")):
        bpy.data.objects.remove(ob, do_unlink=True)
for ar in list(bpy.data.armatures):
    if ar.users == 0:
        bpy.data.armatures.remove(ar)

# ------------------------------------------------------------------ 1. armature
arm_data = bpy.data.armatures.new(ARM_NAME)
arm = bpy.data.objects.new(ARM_NAME, arm_data)
coll("09_Rig").objects.link(arm)
arm.show_in_front = True
arm_data.display_type = "STICK"
for o in bpy.context.view_layer.objects:
    o.select_set(False)
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_data.edit_bones
bones = SK.build_bones()
for name, parent, head, tail, connect in bones:
    b = eb.new(name)
    b.head, b.tail = head, tail
    b.roll = 0.0
    b.use_deform = name not in SK.IK_BONES
for name, parent, head, tail, connect in bones:
    if parent:
        eb[name].parent = eb[parent]
        eb[name].use_connect = connect
bpy.ops.object.mode_set(mode="OBJECT")
print("tulang:", len(arm_data.bones))

# ------------------------------------------------------------------ 2. segmentasi
me = src.data
nV = len(me.vertices)
Vco = np.zeros(nV * 3)
me.vertices.foreach_get("co", Vco)
Vco = Vco.reshape(-1, 3)
F = np.array([p.vertices[:] for p in me.polygons])
assert F.shape[1] == 3, "JK_Source harus segitiga"
lab = G.label_faces(Vco, F, SK.bone_segments())
uv = np.zeros(len(me.loops) * 2)
me.uv_layers[0].data.foreach_get("uv", uv)
uv = uv.reshape(-1, 2)
lt = np.array([p.loop_start for p in me.polygons])
fuv = np.stack([uv[lt], uv[lt + 1], uv[lt + 2]], 1)
os.makedirs(os.path.dirname(FACES_NPZ), exist_ok=True)
np.savez_compressed(FACES_NPZ, labels=lab.astype(str), fuv=fuv.astype(np.float32), centers=Vco[F].mean(1).astype(np.float32))

bone2piece = {b: p for p, bl in SK.PIECE_BONES.items() for b in bl}
bone2piece.update({"cloth_front": "Pelvis", "cloth_back": "Pelvis"})
piece_of = np.array([bone2piece[str(b)] for b in lab], dtype=object)
print("segitiga per potongan:", {p: int((piece_of == p).sum()) for p in SK.PIECES})


# ------------------------------------------------------------------ 3. bobot per vertex (dari label segitiga)
def chain_weights(z, chain_pts):
    """Bobot halus sepanjang rantai kain (tent per tulang) + pelvis di atas pangkal."""
    zs = [p[2] for p in chain_pts]
    s = np.interp(-z, [-zz for zz in zs], np.arange(len(zs)))     # 0 di pangkal .. 3 di ujung
    s = s - (z > zs[0]) * (z - zs[0]) * 4.0                         # di atas pangkal -> pelvis
    centers = [-0.5, 0.5, 1.5, 2.5]                                 # pelvis, _01, _02, _03
    w = np.array([max(0.0, 1.0 - abs(s - c)) for c in centers])
    w[0] = w[0] if s < 0.5 else 0.0
    if s <= -0.5:
        w[:] = 0
        w[0] = 1
    if s >= 2.5:
        w[:] = 0
        w[3] = 1
    return w / max(w.sum(), 1e-6)


vert_w = [dict() for _ in range(nV)]
for fi, f in enumerate(F):
    b = str(lab[fi])
    for v in f:
        vert_w[v][b] = vert_w[v].get(b, 0) + 1


def weights_for(vi, piece):
    cnt = {b: c for b, c in vert_w[vi].items() if bone2piece.get(b) == piece}
    if not cnt:
        return {SK.PIECE_BONES[piece][0]: 1.0}
    out = {}
    tot = sum(cnt.values())
    for b, c in cnt.items():
        if b in ("cloth_front", "cloth_back"):
            pts = SK.CLOTH_FRONT if b == "cloth_front" else SK.CLOTH_BACK
            w = chain_weights(Vco[vi][2], pts)
            for name, ww in zip(["pelvis", f"{b}_01", f"{b}_02", f"{b}_03"], w):
                if ww > 1e-3:
                    out[name] = out.get(name, 0) + ww * c / tot
        else:
            out[b] = out.get(b, 0) + c / tot
    top = sorted(out.items(), key=lambda kv: -kv[1])[:4]
    s = sum(w for _, w in top)
    return {k: w / s for k, w in top}


# ------------------------------------------------------------------ 4. potongan: pisah, tutup, objek
mat = src.data.materials[0]
mat.name = "M_Jerangkong"
pieces_coll = {"Skull": "01_Skull", "Jaw": "01_Skull", "Ribs": "02_SpineRibs", "Spine": "02_SpineRibs",
               "Pelvis": "03_PelvisCloth"}
stats = {}
for piece, (pivot_bone, detach) in SK.PIECES.items():
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    orig = bm.verts.layers.int.new("orig")
    for v in bm.verts:
        v[orig] = v.index
    keep = set(np.where(piece_of == piece)[0].tolist())
    cut_edges = set()
    for e in bm.edges:                                              # tepi yang dibagi dengan potongan lain = garis potong
        lf = e.link_faces
        if len(lf) >= 2 and any(f.index in keep for f in lf) and any(f.index not in keep for f in lf):
            cut_edges.add(e.index)
    cut_flag = bm.edges.layers.int.new("cut")
    for e in bm.edges:
        e[cut_flag] = 1 if e.index in cut_edges else 0
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
    bm.edges.ensure_lookup_table()
    boundary_cut = [e for e in bm.edges if e[cut_flag] and len(e.link_faces) == 1]
    capped = 0
    if boundary_cut:
        res = bmesh.ops.holes_fill(bm, edges=boundary_cut, sides=0)
        newf = res["faces"]
        if newf:
            tri = bmesh.ops.triangulate(bm, faces=newf)
            capf = tri["faces"]
            uvl = bm.loops.layers.uv.active
            for f in capf:
                f.smooth = False
                for lp in f.loops:
                    lp[uvl].uv = CAP_UV
            capped = len(capf)
    me_p = bpy.data.meshes.new(f"JK_P_{piece}")
    bm.to_mesh(me_p)
    origs = [v[orig] for v in bm.verts]
    bm.free()
    ob = bpy.data.objects.new(f"JK_P_{piece}", me_p)
    coll(pieces_coll.get(piece, "04_Arms" if "Arm" in piece else ("05_Hands" if "Hand" in piece else "06_LegsFeet"))).objects.link(ob)
    if not me_p.materials:
        me_p.materials.append(mat)
    ob["jk_piece"] = piece
    ob["jk_pivot_bone"] = pivot_bone
    ob["jk_detach"] = bool(detach)
    # bobot
    for vi, o in enumerate(origs):
        for b, w in weights_for(o, piece).items():
            vg = ob.vertex_groups.get(b) or ob.vertex_groups.new(name=b)
            vg.add([vi], w, "REPLACE")
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    ob.parent = arm
    stats[piece] = (sum(len(p.vertices) - 2 for p in me_p.polygons), capped, len(boundary_cut))

# cap = flat; sisanya halus
for ob in bpy.data.objects:
    if ob.name.startswith("JK_P_"):
        uvl = ob.data.uv_layers.active.data
        for p in ob.data.polygons:
            p.use_smooth = not all(abs(uvl[li].uv[0] - CAP_UV[0]) < 1e-6 and abs(uvl[li].uv[1] - CAP_UV[1]) < 1e-6
                                   for li in p.loop_indices)

# ------------------------------------------------------------------ 5. LOD0 ke anggaran tris
total = sum(t for t, _c, _b in stats.values())
if total > TRI_BUDGET:
    ratio = TRI_BUDGET / total
    for ob in [o for o in bpy.data.objects if o.name.startswith("JK_P_")]:
        dm = ob.modifiers.new("_dec", "DECIMATE")
        dm.decimate_type = "COLLAPSE"
        dm.ratio = ratio
        dm.use_collapse_triangulate = True
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
            bpy.ops.object.modifier_move_to_index(modifier="_dec", index=0)
            bpy.ops.object.modifier_apply(modifier="_dec")
total2 = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.name.startswith("JK_P_"))

# ------------------------------------------------------------------ 6. socket
seg = SK.bone_segments()
for name, (bone, pos) in SK.build_sockets().items():
    e = bpy.data.objects.new(f"SOCKET_{name}", None)
    e.empty_display_type = "SPHERE"
    e.empty_display_size = 0.03
    coll("10_Sockets").objects.link(e)
    e.parent = arm
    e.parent_type = "BONE"
    e.parent_bone = bone
    e.matrix_world = arm.matrix_world.copy()
    e.matrix_world.translation = pos
    bpy.context.view_layer.update()
    e.matrix_world.translation = pos

# ------------------------------------------------------------------ 7. sumber disembunyikan, simpan
src.hide_set(True)
src.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=OUT, relative_remap=True)
print(f"\n{'potongan':10s} {'tris':>6s} {'cap':>5s} {'tepi':>5s}")
for p, (t, c, b) in stats.items():
    print(f"{p:10s} {t:6d} {c:5d} {b:5d}")
print(f"total tris sebelum {total}, sesudah LOD0 {total2}  -> {OUT}")
