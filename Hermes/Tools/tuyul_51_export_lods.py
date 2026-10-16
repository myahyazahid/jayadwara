"""K5.2 - Export 4 LOD x 3 skala Tuyul (kontrak sama dengan tuyul_31_export.py).

  blender --background Hermes/Art/tuyul/Blender/tuyul_v08_lod.blend --python Hermes/Tools/tuyul_51_export_lods.py

Kontrak docs/20 6.5 / Jayadwara pasca-Iterasi 6: armature bernama "Armature", data cm &
skala di-bake lalu di-apply, FBX_SCALE_ALL, tanpa empty/animasi, axis -Y/Z, tanpa leaf bone.
SK_Tuyul (LOD0 x1) TIDAK ditimpa (artefak K3); socket JSON hanya untuk LOD0 tiap skala
(pola jayadwara2_16_make_lods.py membuang socket json LOD). Scene tidak disimpan.
"""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
sys.path.insert(0, str(ROOT / "Hermes" / "Tools"))
import tuyul_skeleton as SK  # noqa: E402

ARM_NAME = "TY_Armature"
OUT = ROOT / "Hermes" / "Art" / "tuyul" / "Export"
# (nama aset dasar, skala, LOD yang diekspor, tulis sockets json)
PLAN = [
    ("SK_Tuyul", 1.0, [1, 2, 3], False),          # LOD0 x1 sudah ada dari K3
    ("SK_TuyulBesar", 27.0, [0, 1, 2, 3], True),
    ("SK_TuyulRaksasa", 45.0, [0, 1, 2, 3], True),
]
rna = bpy.ops.export_scene.fbx.get_rna_type().properties


def tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def ue_cm(p, scale):
    return [round(v * 100.0 * scale, 3) for v in (p.x, -p.y, p.z)]


def fbx_kwargs(path, types):
    def ok(prop, value):
        p = rna.get(prop)
        return p is not None and value in [i.identifier for i in p.enum_items]

    w = dict(filepath=path, use_selection=True, object_types=types, use_mesh_modifiers=True,
             add_leaf_bones=False, use_armature_deform_only=False, bake_anim=False, use_triangles=True,
             global_scale=1.0, apply_unit_scale=True, use_custom_props=False, embed_textures=False, use_tspace=False)
    for prop, val in (("axis_forward", "-Y"), ("axis_up", "Z"), ("armature_nodetype", "NULL"),
                      ("mesh_smooth_type", "FACE"), ("apply_scale_options", "FBX_SCALE_ALL")):
        if ok(prop, val):
            w[prop] = val
    return {k: v for k, v in w.items() if k in rna}


def export_one(mesh_name, asset, scale):
    scene = bpy.context.scene
    arm = bpy.data.objects[ARM_NAME]
    src = bpy.data.objects[mesh_name]
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    tmp = bpy.data.collections.new("_EXPORT_TMP")
    scene.collection.children.link(tmp)
    j = src.copy()
    j.data = src.data.copy()
    tmp.objects.link(j)
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
    j.name = j.data.name = asset
    for mt in j.data.materials:
        mt.name = "M_Tuyul"
    blocker = bpy.data.objects.get("Armature")
    if blocker is not None:
        blocker.name = "Armature_tmp"
    ax.name = "Armature"
    t = tris(j.data)
    fbx = OUT / f"{asset}.fbx"
    try:
        with bpy.context.temp_override(selected_objects=[ax, j], selected_editable_objects=[ax, j], active_object=ax):
            bpy.ops.export_scene.fbx(**fbx_kwargs(str(fbx), {"ARMATURE", "MESH"}))
    finally:
        ad = ax.data
        bpy.data.objects.remove(j, do_unlink=True)
        bpy.data.objects.remove(ax, do_unlink=True)
        bpy.data.armatures.remove(ad)
        if blocker is not None:
            blocker.name = "Armature"
        bpy.data.collections.remove(tmp)
    print(f"export {fbx.name}: {t} tris, skala {scale}, tinggi {1.0 * scale:.1f} m")
    return t


def write_sockets(asset, scale):
    sockets = SK.build_sockets()
    socks = [{"name": f"SOCKET_{sn}", "bone": bone, "blender_m": [round(c, 5) for c in pos],
              "ue_component_cm": ue_cm(pos, scale)} for sn, (bone, pos) in sockets.items()]
    js = OUT / f"{asset}_sockets.json"
    js.write_text(json.dumps({"mesh": asset, "export_scale": scale,
                              "note": "posisi rest; ue_component_cm = (x, -y, z) x 100 x export_scale (konvensi docs/13 Iterasi 6)",
                              "sockets": socks}, indent=2), encoding="utf-8")
    print(f"socket json {js.name}: {len(socks)} socket, skala {scale}")
    return len(socks)


report = {}
for base, scale, lods, sock in PLAN:
    for n in lods:
        mesh = "TY_Source" if n == 0 else f"TY_Source_LOD{n}"
        asset = base if n == 0 else f"{base}_LOD{n}"
        report[asset] = export_one(mesh, asset, scale)
    if sock:
        report[f"{base}_sockets"] = write_sockets(base, scale)

(OUT / "_lod_export.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("ringkasan export:", json.dumps(report, indent=None))
