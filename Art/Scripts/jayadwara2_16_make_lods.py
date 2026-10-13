"""Jayadwara2 R5 — LOD1–3 (FBX terpisah, skeleton sama) dari `JD2_Body` (LOD0 = hasil R3, 37,4k tris).

  blender --background Art/Blender/jayadwara2_v05_rig_r3.blend --python Art/Scripts/jayadwara2_16_make_lods.py
Per LOD: salinan JD2_Body, Armature dilepas, Decimate COLLAPSE (rasio LODS) dengan grup `LODPROTECT` (kepala depan: helm/wajah/mata, dan zona permata dada)
dilindungi, lalu bobot dibersihkan (<= 4 influence, dinormalisasi), buang vertex/edge lepas; Armature dipasang lagi; diekspor lewat jayadwara2_14_export.py
(kontrak sama: Armature, cm, skala raksasa ter-bake) sebagai SK_Jayadwara2_LOD<n>.fbx. Scene asli tidak berubah (tidak disimpan).
Anggaran docs/25 R9: LOD1 <= 30k, LOD2 <= 14k, LOD3 <= 6k tris. Ringkasan di Art/Export/_jd2/_lod_report.json."""
import json
import os

import bmesh
import bpy
import numpy as np

ROOT = r"C:\repository\unreal_engine\jayadwara"
EXPORT_PY = os.path.join(ROOT, "Art", "Scripts", "jayadwara2_14_export.py")
LODS = globals().get("LODS") or {1: 0.50, 2: 0.23, 3: 0.10}
BUDGET = {1: 30000, 2: 14000, 3: 6000}
MAX_INF = 4

body0 = bpy.data.objects["JD2_Body"]
arm = bpy.data.objects["JD2_Armature"]
tris = lambda me: sum(len(p.vertices) - 2 for p in me.polygons)
report = {"LOD0": tris(body0.data)}


def protect_group(ob):
    vg = ob.vertex_groups.get("LODPROTECT") or ob.vertex_groups.new(name="LODPROTECT")
    n = 0
    for v in ob.data.vertices:
        c = v.co
        head = c.z > 1.70 and c.y < -0.03                                   # helm, wajah, mata (tampak depan)
        gem = abs(c.x) < 0.06 and 1.38 < c.z < 1.52 and c.y < -0.12          # permata dada
        if head or gem:
            vg.add([v.index], 1.0, "REPLACE")
            n += 1
    return n


def clean_weights(ob):
    vgs = {vg.index: vg for vg in ob.vertex_groups}
    for v in ob.data.vertices:
        gs = sorted(((g.group, g.weight) for g in v.groups if vgs[g.group].name != "LODPROTECT" and g.weight > 1e-4), key=lambda t: -t[1])
        keep, drop = gs[:MAX_INF], gs[MAX_INF:]
        tot = sum(w for _, w in keep) or 1.0
        for gi, _ in drop:
            vgs[gi].remove([v.index])
        for gi, w in keep:
            vgs[gi].add([v.index], w / tot, "REPLACE")


def drop_loose(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()


src_code = compile(open(EXPORT_PY, encoding="utf-8").read(), EXPORT_PY, "exec")
for lod, ratio in LODS.items():
    d = body0.copy()
    d.data = body0.data.copy()
    d.name = d.data.name = f"JD2_Body_LOD{lod}"
    bpy.context.scene.collection.objects.link(d)
    d.modifiers.clear()
    d.parent = None
    nprot = protect_group(d)
    mod = d.modifiers.new("Decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    mod.vertex_group = "LODPROTECT"
    mod.invert_vertex_group = True            # bobot 1 = didecimate: dibalik supaya grup LODPROTECT = dilindungi, sisanya didecimate
    mod.vertex_group_factor = 1.0
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    d.select_set(True)
    bpy.context.view_layer.objects.active = d
    bpy.ops.object.modifier_apply(modifier="Decimate")
    drop_loose(d)
    clean_weights(d)
    d.vertex_groups.remove(d.vertex_groups["LODPROTECT"])
    am = d.modifiers.new("Armature", "ARMATURE")
    am.object = arm
    am.use_vertex_groups = True
    d.parent = arm
    d.parent_type = "OBJECT"
    t = tris(d.data)
    report[f"LOD{lod}"] = t
    print(f"LOD{lod}: {t} tris (rasio {ratio}, anggaran {BUDGET[lod]}, terlindungi {nprot} vertex) {'OK' if t <= BUDGET[lod] else 'MELEBIHI'}")
    # ekspor: JD2_Body sementara = LOD ini
    body0.name = "JD2_Body_LOD0"
    d.name = "JD2_Body"
    g = {"__name__": "lod_export", "MESH_NAME": f"SK_Jayadwara2_LOD{lod}", "OUT_DIR": os.path.join(ROOT, "Art", "Export")}
    exec(src_code, g)
    d.name = f"JD2_Body_LOD{lod}"
    body0.name = "JD2_Body"
    for extra in (f"SK_Jayadwara2_LOD{lod}_sockets.json",):
        pth = os.path.join(ROOT, "Art", "Export", extra)
        if os.path.exists(pth):
            os.remove(pth)
json.dump(report, open(os.path.join(ROOT, "Art", "Export", "_jd2", "_lod_report.json"), "w"), indent=2)
print("laporan:", report)

# ---- perbandingan visual (Workbench, tekstur apa adanya): depan & kepala per LOD -> Art/Export/_jd2/_lod_<n>_{depan,kepala}.png
if globals().get("RENDER_COMPARE", True):
    from mathutils import Vector
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light, sh.color_type, sh.show_cavity = "FLAT", "TEXTURE", False
    sc.view_settings.view_transform = "Standard"
    sc.world = sc.world or bpy.data.worlds.new("w")
    sc.world.color = (0.45, 0.5, 0.55)
    for o in bpy.data.objects:
        if o.type in {"ARMATURE", "EMPTY"}:
            o.hide_render = True
    cd = bpy.data.cameras.new("c")
    cam = bpy.data.objects.new("c", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cd.type = "ORTHO"
    objs = {0: body0, **{n: bpy.data.objects[f"JD2_Body_LOD{n}"] for n in LODS}}
    src = bpy.data.objects.get("JD2_Source")
    if src:
        src.hide_render = True
    for n, ob in objs.items():
        for k, o in objs.items():
            o.hide_render = (k != n)
        for name, loc, orth, res in (("depan", (0, -10, 1.055), 2.28, (760, 1200)), ("kepala", (0, -10, 1.76), 0.34, (1000, 1000))):
            cd.ortho_scale = orth
            cam.location = Vector(loc)
            cam.rotation_euler = (np.radians(90), 0, 0)
            sc.render.resolution_x, sc.render.resolution_y = res
            sc.render.filepath = os.path.join(ROOT, "Art", "Export", "_jd2", f"_lod_{n}_{name}.png")
            bpy.ops.render.render(write_still=True)
