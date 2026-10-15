"""K3.2 - Socket + export LOD0 SK_Tuyul.fbx (kontrak Jayadwara pasca-Iterasi 6).

  blender --background <blend_in> --python Hermes/Tools/tuyul_31_export.py -- --outdir <dir> [--scale 1.0] [--name SK_Tuyul]

Kontrak (docs/13/20, pola jerangkong_14_export.py): armature bernama "Armature", data cm & skala di-bake
lalu di-apply, FBX_SCALE_ALL, tanpa empty, tanpa animasi, axis -Y/Z, tanpa leaf bone.
Keluaran: <name>.fbx + <name>_sockets.json (8 socket) + blend ber-socket (v06).
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
OBJ = "TY_Source"


def arg(name, default=None):
    a = sys.argv
    if "--" in a:
        a = a[a.index("--") + 1:]
        if name in a:
            return a[a.index(name) + 1]
    return default


def tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def ue_cm(p, scale):
    return [round(v * 100.0 * scale, 3) for v in (p.x, -p.y, p.z)]


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


def main():
    outdir = Path(arg("--outdir", str(ROOT / "Hermes" / "Art" / "tuyul" / "Export")))
    scale = float(arg("--scale", "1.0"))
    name = arg("--name", "SK_Tuyul")
    outdir.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    arm = bpy.data.objects[ARM_NAME]
    src = bpy.data.objects[OBJ]
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()

    # ---- socket: empty di collection 10_Sockets, induk tulang
    col = bpy.data.collections.get("10_Sockets") or bpy.data.collections.new("10_Sockets")
    if col.name not in bpy.data.collections["TY_Tuyul"].children:
        bpy.data.collections["TY_Tuyul"].children.link(col)
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    sockets = SK.build_sockets()
    for sn, (bone, pos) in sockets.items():
        e = bpy.data.objects.new(f"SOCKET_{sn}", None)
        e.empty_display_type = "SPHERE"
        e.empty_display_size = 0.02
        col.objects.link(e)
        e.parent = arm
        e.parent_type = "BONE"
        e.parent_bone = bone
        e.matrix_world = arm.matrix_world.copy()
        e.matrix_world.translation = pos
        bpy.context.view_layer.update()
        e.matrix_world.translation = pos
    print("socket:", len(sockets), sorted(sockets))

    # ---- salinan untuk export
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
    j.name = j.data.name = name
    for mt in j.data.materials:
        mt.name = "M_Tuyul"
    blocker = bpy.data.objects.get("Armature")
    if blocker is not None:
        blocker.name = "Armature_tmp"
    ax.name = "Armature"
    n_tris = tris(j.data)
    fbx = outdir / f"{name}.fbx"
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
    print(f"export: {fbx}  tris={n_tris}  scale={scale}")

    # ---- sockets json
    socks = [{"name": f"SOCKET_{sn}", "bone": bone, "blender_m": [round(c, 5) for c in pos],
              "ue_component_cm": ue_cm(pos, scale)} for sn, (bone, pos) in sockets.items()]
    js = outdir / f"{name}_sockets.json"
    js.write_text(json.dumps({"mesh": name, "export_scale": scale,
                              "note": "posisi rest; ue_component_cm = (x, -y, z) x 100 x export_scale (konvensi docs/13 Iterasi 6)",
                              "sockets": socks}, indent=2), encoding="utf-8")
    print("socket json:", js)

    arm.data.pose_position = "POSE"
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "Hermes" / "Art" / "tuyul" / "Blender" / "tuyul_v06_export.blend"))
    print("blend ber-socket: tuyul_v06_export.blend")


main()
