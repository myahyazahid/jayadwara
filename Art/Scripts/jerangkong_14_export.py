"""Jerangkong (jalur B) — paket export UE: SK boss & minion (LOD0–3), 14 SM potongan, parts.json, sockets.json.

Headless: blender --background Art/Blender/jerangkong/jerangkong_v02_rig.blend --python Art/Scripts/jerangkong_14_export.py
Scene tidak diubah (semua lewat salinan). Kontrak export = Jayadwara pasca-Iterasi 6 (docs/13): armature bernama
"Armature", data cm & skala di-bake lalu di-apply, FBX_SCALE_ALL, tanpa empty, tanpa animasi, LOD file terpisah.

Skala di-bake (Anim Dynamics kain tidak mendukung komponen berskala, docs/13 Iterasi 6b), jadi satu model -> dua aset:
  SK_Jerangkong  boss  x BOSS_SCALE   (puncak tengkorak 2,19 m -> ±30,7 m; docs/20 J2)
  SK_Kerangka    minion x MINION_SCALE (±1,86 m)
SM_Jerangkong_<Potongan> (14 potongan yang bisa rontok): geometri LOD1, skala boss, pivot = kepala tulang pivotnya di
pose rest, orientasi = sumbu komponen (identitas). Minion memakai SM yang sama dengan skala aktor MINION/BOSS.
Di C++: transform SM saat rontok = BoneWorld x inverse(BoneRef) x Translation(pivot) (lihat parts.json).
"""
import json
import os
import sys

import bpy
from mathutils import Matrix, Vector

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jk_skeleton as SK  # noqa: E402

OUT_DIR = globals().get("OUT_DIR") or r"C:\repository\unreal_engine\jayadwara\Art\Export"
BOSS_SCALE = 14.0
MINION_SCALE = 0.85
LOD_TARGET = {1: 14300, 2: 5700, 3: 2350}             # docs/20 J7
SKULL_BOOST = 1.6                                       # tengkorak dilindungi (rasio x1,6, maks 1)
ARM_NAME = "JK_Armature"

scene = bpy.context.scene
arm = bpy.data.objects[ARM_NAME]
pieces = sorted((o for o in bpy.data.objects if o.name.startswith("JK_P_")), key=lambda o: o.name)
arm.data.pose_position = "REST"
bpy.context.view_layer.update()
tmp = bpy.data.collections.new("_EXPORT_TMP")
scene.collection.children.link(tmp)


def tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


LOD0_TRIS = sum(tris(o.data) for o in pieces)


def ratio_for(level, piece_name):
    if level == 0:
        return 1.0
    r = LOD_TARGET[level] / LOD0_TRIS
    return min(1.0, r * SKULL_BOOST) if piece_name in ("Skull", "Jaw") else r


def dup(ob):
    d = ob.copy()
    d.data = ob.data.copy()
    tmp.objects.link(d)
    return d


def decimate(d, r):
    if r >= 0.999:
        return
    m = d.modifiers.new("_lod", "DECIMATE")
    m.decimate_type = "COLLAPSE"
    m.ratio = r
    m.use_collapse_triangulate = True
    with bpy.context.temp_override(object=d, active_object=d, selected_objects=[d], selected_editable_objects=[d]):
        bpy.ops.object.modifier_move_to_index(modifier="_lod", index=0)
        bpy.ops.object.modifier_apply(modifier="_lod")
    # bobot setelah collapse: maks 4, dinormalisasi
    for v in d.data.vertices:
        gs = sorted(((g.group, g.weight) for g in v.groups), key=lambda x: -x[1])
        keep = {g: w for g, w in gs[:4] if w > 1e-4} or ({gs[0][0]: 1.0} if gs else {})
        tot = sum(keep.values()) or 1.0
        for g, _w in gs:
            if g not in keep:
                d.vertex_groups[g].remove([v.index])
        for g, w in keep.items():
            d.vertex_groups[g].add([v.index], w / tot, "REPLACE")


rna = bpy.ops.export_scene.fbx.get_rna_type().properties


def fbx_kwargs(path, types):
    def ok(prop, value):
        p = rna.get(prop)
        return p is not None and value in [i.identifier for i in p.enum_items]

    w = dict(filepath=path, use_selection=True, object_types=types, use_mesh_modifiers=True, add_leaf_bones=False,
             use_armature_deform_only=False, bake_anim=False, use_triangles=True, global_scale=1.0,
             apply_unit_scale=True, use_custom_props=False, embed_textures=False, use_tspace=False)
    for prop, val in (("axis_forward", "-Y"), ("axis_up", "Z"), ("armature_nodetype", "NULL"),
                      ("mesh_smooth_type", "FACE"), ("apply_scale_options", "FBX_SCALE_ALL")):
        if ok(prop, val):
            w[prop] = val
    return {k: v for k, v in w.items() if k in rna}


def export_sk(path, mesh_name, scale, level):
    dups = []
    for o in pieces:
        d = dup(o)
        decimate(d, ratio_for(level, o["jk_piece"]))
        dups.append(d)
    with bpy.context.temp_override(active_object=dups[0], object=dups[0], selected_objects=dups, selected_editable_objects=dups):
        bpy.ops.object.join()
    j = dups[0]
    j.name = j.data.name = mesh_name
    for k in list(j.keys()):
        del j[k]
    n_tris = tris(j.data)
    ax = arm.copy()
    ax.data = arm.data.copy()
    ax.animation_data_clear()
    tmp.objects.link(ax)
    j.parent = None
    j.matrix_world = Matrix.Identity(4)
    for m in j.modifiers:
        if m.type == "ARMATURE":
            m.object = ax
    for o in (ax, j):
        o.matrix_world = Matrix.Scale(100.0 * scale, 4) @ o.matrix_world
    bpy.context.view_layer.update()
    with bpy.context.temp_override(active_object=ax, selected_objects=[ax, j], selected_editable_objects=[ax, j]):
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    j.parent = ax
    j.matrix_parent_inverse = ax.matrix_world.inverted()
    blocker = bpy.data.objects.get("Armature")
    if blocker is not None:
        blocker.name = "Armature_tmp"
    ax.name = "Armature"
    try:
        with bpy.context.temp_override(selected_objects=[ax, j], selected_editable_objects=[ax, j], active_object=ax):
            bpy.ops.export_scene.fbx(**fbx_kwargs(path, {"ARMATURE", "MESH"}))
    finally:
        ad = ax.data
        bpy.data.objects.remove(j, do_unlink=True)
        bpy.data.objects.remove(ax, do_unlink=True)
        bpy.data.armatures.remove(ad)
        if blocker is not None:
            blocker.name = "Armature"
    return n_tris


def export_sm(o, path, scale):
    piece = o["jk_piece"]
    pivot = arm.data.bones[o["jk_pivot_bone"]].head_local.copy()
    d = dup(o)
    decimate(d, ratio_for(1, piece))
    d.modifiers.clear()
    d.vertex_groups.clear()
    d.parent = None
    d.matrix_world = Matrix.Identity(4)
    d.data.transform(Matrix.Scale(100.0 * scale, 4) @ Matrix.Translation(-pivot))
    d.name = d.data.name = f"SM_Jerangkong_{piece}"
    for k in list(d.keys()):
        del d[k]
    n = tris(d.data)
    with bpy.context.temp_override(selected_objects=[d], selected_editable_objects=[d], active_object=d):
        bpy.ops.export_scene.fbx(**fbx_kwargs(path, {"MESH"}))
    bpy.data.objects.remove(d, do_unlink=True)
    return n, pivot


def ue_cm(p, scale):
    return [round(v * 100.0 * scale, 3) for v in (p.x, -p.y, p.z)]


os.makedirs(OUT_DIR, exist_ok=True)
report = []
for mesh_name, scale in (("SK_Jerangkong", BOSS_SCALE), ("SK_Kerangka", MINION_SCALE)):
    for lv in (0, 1, 2, 3):
        fn = f"{mesh_name}.fbx" if lv == 0 else f"{mesh_name}_LOD{lv}.fbx"
        report.append((fn, export_sk(os.path.join(OUT_DIR, fn), mesh_name, scale, lv)))
    # socket
    socks = []
    for o in sorted((o for o in bpy.data.objects if o.name.startswith("SOCKET_")), key=lambda o: o.name):
        p = o.matrix_world.translation
        socks.append({"name": o.name, "bone": o.parent_bone, "blender_m": [round(c, 5) for c in p], "ue_component_cm": ue_cm(p, scale)})
    with open(os.path.join(OUT_DIR, f"{mesh_name}_sockets.json"), "w", encoding="utf-8") as f:
        json.dump({"mesh": mesh_name, "export_scale": scale,
                   "note": "posisi rest; ue_component_cm = (x, -y, z) x 100 x export_scale (konvensi docs/13 Iterasi 6)",
                   "sockets": socks}, f, indent=2)

parts = []
sm_dir = os.path.join(OUT_DIR, "Jerangkong_Parts")
os.makedirs(sm_dir, exist_ok=True)
for o in pieces:
    piece, bone, detach = o["jk_piece"], o["jk_pivot_bone"], bool(o["jk_detach"])
    entry = {"piece": piece, "pivot_bone": bone, "detachable": detach, "bones": SK.PIECE_BONES[piece],
             "pivot_model_m": [round(c, 5) for c in arm.data.bones[bone].head_local],
             "pivot_ue_cm_boss": ue_cm(arm.data.bones[bone].head_local, BOSS_SCALE),
             "pivot_ue_cm_minion": ue_cm(arm.data.bones[bone].head_local, MINION_SCALE)}
    if detach:
        fn = f"SM_Jerangkong_{piece}.fbx"
        n, _pv = export_sm(o, os.path.join(sm_dir, fn), BOSS_SCALE)
        entry.update({"static_mesh": f"SM_Jerangkong_{piece}", "sm_tris": n})
        report.append((f"Jerangkong_Parts/{fn}", n))
    parts.append(entry)
with open(os.path.join(OUT_DIR, "SK_Jerangkong_parts.json"), "w", encoding="utf-8") as f:
    json.dump({"boss_scale": BOSS_SCALE, "minion_scale": MINION_SCALE, "sm_scale": BOSS_SCALE,
               "note": ("SM berskala boss, pivot = kepala pivot_bone di rest, orientasi identitas (sumbu komponen). "
                        "Transform SM saat rontok = BoneWorld * inverse(BoneRefComponent) * Translation(pivot_ue_cm). "
                        "Minion: skala aktor SM = minion_scale / boss_scale."),
               "parts": parts}, f, indent=2)

arm.data.pose_position = "POSE"
bpy.data.collections.remove(tmp)
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)
print(f"\nLOD0 kerja: {LOD0_TRIS} tris")
for fn, n in report:
    print(f"{fn:42s} {n:7d} tris")
