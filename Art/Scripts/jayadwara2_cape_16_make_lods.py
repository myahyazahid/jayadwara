"""Jubah Jayadwara2 J2 — LOD1–2 (FBX terpisah, skeleton sama) dari `JD2_Cape` (pola jayadwara2_16_make_lods.py).

  blender --background Art/Blender/jayadwara2/jayadwara2_cape_v01_rig.blend --python Art/Scripts/jayadwara2_cape_16_make_lods.py
Per LOD: salinan JD2_Cape, Armature dilepas, Decimate COLLAPSE (rasio LODS), bobot dibersihkan (<= 4 influence,
dinormalisasi), vertex lepas dibuang, Armature dipasang lagi; diekspor lewat jayadwara2_cape_14_export.py (kontrak sama)
sebagai SK_Jayadwara2_Cape_LOD<n>.fbx. Scene asli tidak disimpan. Anggaran (docs/26 J2): LOD1 <= 16k, LOD2 <= 8k tris.
Ringkasan: Art/Export/_jd2c/_lod_report.json + render pembanding _lod_<n>_belakang.png.
"""
import json
import math
import os

import bmesh
import bpy
from mathutils import Vector

ROOT = r"C:\repository\unreal_engine\jayadwara"
EXPORT_PY = os.path.join(ROOT, "Art", "Scripts", "jayadwara2_cape_14_export.py")
OUT = os.path.join(ROOT, "Art", "Export")
LODS = globals().get("LODS") or {1: 0.50, 2: 0.24}
BUDGET = {1: 16000, 2: 8000}
MAX_INF = 4

cape0 = bpy.data.objects["JD2_Cape"]
arm = bpy.data.objects["JD2C_Armature"]
tris = lambda me: sum(len(p.vertices) - 2 for p in me.polygons)
report = {"LOD0": tris(cape0.data)}


def clean_weights(ob):
    vgs = {vg.index: vg for vg in ob.vertex_groups}
    for v in ob.data.vertices:
        gs = sorted(((g.group, g.weight) for g in v.groups if g.weight > 1e-4), key=lambda t: -t[1])
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
objs = {0: cape0}
for lod, ratio in LODS.items():
    d = cape0.copy()
    d.data = cape0.data.copy()
    d.name = d.data.name = f"JD2_Cape_LOD{lod}"
    bpy.context.scene.collection.objects.link(d)
    d.modifiers.clear()
    d.parent = None
    mod = d.modifiers.new("Decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    d.select_set(True)
    bpy.context.view_layer.objects.active = d
    bpy.ops.object.modifier_apply(modifier="Decimate")
    drop_loose(d)
    clean_weights(d)
    am = d.modifiers.new("Armature", "ARMATURE")
    am.object = arm
    d.parent = arm
    t = tris(d.data)
    report[f"LOD{lod}"] = t
    print(f"LOD{lod}: {t} tris (rasio {ratio}, anggaran {BUDGET[lod]}) {'OK' if t <= BUDGET[lod] else 'MELEBIHI'}")
    exec(src_code, {"__name__": "lod_export", "MESH_NAME": f"SK_Jayadwara2_Cape_LOD{lod}", "SRC_MESH": d.name, "OUT_DIR": OUT})
    objs[lod] = d
json.dump(report, open(os.path.join(OUT, "_jd2c", "_lod_report.json"), "w"), indent=2)
print("laporan:", report)

# perbandingan visual (belakang)
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light, sh.color_type = "STUDIO", "TEXTURE"
sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
sc.world.color = (0.5, 0.52, 0.55)
cd = bpy.data.cameras.new("c_lod")
cam = bpy.data.objects.new("c_lod", cd)
sc.collection.objects.link(cam)
sc.camera = cam
cd.type, cd.ortho_scale = "ORTHO", 1.9
sc.render.resolution_x, sc.render.resolution_y = 600, 760
cam.location = Vector((0, 5, 0.9))
cam.rotation_euler = (Vector((0, 0, 0.9)) - cam.location).to_track_quat("-Z", "Y").to_euler()
for n, ob in objs.items():
    for o in bpy.data.objects:
        o.hide_render = o is not ob
    sc.render.filepath = os.path.join(OUT, "_jd2c", f"_lod_{n}_belakang.png")
    bpy.ops.render.render(write_still=True)
