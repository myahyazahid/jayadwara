"""Iterasi 2 — hero: UNDERSUIT hitam (Skin modifier + subdivisi level 2, topologi tabung bersih untuk deformasi)."""
import importlib
import sys

import bmesh
import bpy
from mathutils import Vector

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jd_common as C
import jd_skeleton as SK
importlib.reload(C)
importlib.reload(SK)

for ob in list(bpy.data.objects):
    if ob.type == "MESH" and ob.name == "JD_Body_Undersuit":
        bpy.data.objects.remove(ob, do_unlink=True)

seg = SK.bone_segments()
bm = bmesh.new()
skin = bm.verts.layers.skin.verify()


def sv(p, r, root=False):
    v = bm.verts.new(Vector(p))
    v[skin].radius = r
    v[skin].use_root = root
    return v


# Revisi (konsep: atletis-berotot). Radius (x, y) per sendi; titik tengah otot (bisep, lengan bawah, paha, betis).
P = sv((0, 0, 0.95), (0.158, 0.118), root=True)
Wst = sv((0, 0, 1.09), (0.145, 0.108))
C1 = sv((0, 0, 1.29), (0.188, 0.144))                       # revisi 2: lebih berisi (zirah tidak melayang)
C2 = sv((0, 0, 1.47), (0.206, 0.152))
N0 = sv((0, 0, 1.56), (0.068, 0.064))                        # trapezius/leher lebih tebal
N1 = sv((0, 0, 1.66), (0.055, 0.055))
for a, b in ((P, Wst), (Wst, C1), (C1, C2), (C2, N0), (N0, N1)):
    bm.edges.new((a, b))
for sd, s in SK.SIDES.items():
    sh, el, wr = seg[f"upperarm_{sd}"][0], seg[f"lowerarm_{sd}"][0], seg[f"hand_{sd}"][0]
    vs = sv(sh, (0.086, 0.084))                          # deltoid (mengisi pauldron)
    vb = sv(sh.lerp(el, 0.45), (0.079, 0.080))          # bisep
    ve = sv(el, (0.056, 0.056))
    vf = sv(el.lerp(wr, 0.35), (0.063, 0.061))          # otot lengan bawah
    vw = sv(wr, (0.046, 0.044))
    for a, b in ((C2, vs), (vs, vb), (vb, ve), (ve, vf), (vf, vw)):
        bm.edges.new((a, b))
    hip, knee, ankle = seg[f"thigh_{sd}"][0], seg[f"calf_{sd}"][0], seg[f"foot_{sd}"][0]
    vh = sv(hip, (0.098, 0.098))
    vt = sv(hip.lerp(knee, 0.45), (0.100, 0.102))       # paha
    vk = sv(knee, (0.078, 0.080))
    vc = sv(knee.lerp(ankle, 0.28), (0.080, 0.084))     # betis
    va = sv(ankle, (0.052, 0.054))
    for a, b in ((P, vh), (vh, vt), (vt, vk), (vk, vc), (vc, va)):
        bm.edges.new((a, b))

tmp_mesh = bpy.data.meshes.new("_tmp_skin")
bm.to_mesh(tmp_mesh)
bm.free()
tmp = bpy.data.objects.new("_tmp_skin", tmp_mesh)
bpy.context.scene.collection.objects.link(tmp)
mod = tmp.modifiers.new("Skin", "SKIN")
mod.use_smooth_shade = True
mod.branch_smoothing = 0.6
sub = tmp.modifiers.new("Subsurf", "SUBSURF")
sub.levels = sub.render_levels = 2
bpy.context.view_layer.update()
ev_mesh = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
bm = bmesh.new()
bm.from_mesh(ev_mesh)
bpy.data.objects.remove(tmp, do_unlink=True)
bpy.data.meshes.remove(tmp_mesh)
bpy.data.meshes.remove(ev_mesh)
ob = C.finish_part("JD_Body_Undersuit", bm, "01_Body", "black", "Body", kind="skin", smooth=True)
print("UNDERSUIT tris:", C.tri_count(ob))
