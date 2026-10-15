"""Jubah Jayadwara2 J1 — export SK_Jayadwara2_Cape(.fbx) + tekstur + JSON skala (kontrak sama dengan jayadwara2_14_export.py).

  blender --background Art/Blender/jayadwara2/jayadwara2_cape_v01_rig.blend --python Art/Scripts/jayadwara2_cape_14_export.py
lalu validasi:
  blender --background --factory-startup --python Art/Scripts/validate_jayadwara.py -- Art/Export/SK_Jayadwara2_Cape.fbx \
      --materials 1 --no-zone --max-tris 60000 --height 1.50 --zmin 0.10 --extra-bone-prefix cape_ --no-sockets
Kontrak: salinan armature bernama `Armature` (tanpa constraint), armature + mesh diskalakan 100 x (45/1,90) lalu di-apply,
FBX_SCALE_ALL, tanpa empty, tanpa leaf bone. Skeleton = 89 tulang Jayadwara2 (nama sama -> Copy Pose From Mesh) + rantai cape_*.
Tekstur Tripo (BC/N/ORM) -> Export/Textures_Jayadwara2_Cape/. Scene asli tidak berubah.
"""
import json
import os

import bpy
from mathutils import Matrix

OUT_DIR = globals().get("OUT_DIR") or r"C:\repository\unreal_engine\jayadwara\Art\Export"
MESH_NAME = globals().get("MESH_NAME") or "SK_Jayadwara2_Cape"
SRC_MESH = globals().get("SRC_MESH") or "JD2_Cape"
BASE_HEIGHT_M = 1.90
GIANT_HEIGHT_M = 45.0
SCALE = GIANT_HEIGHT_M / BASE_HEIGHT_M
BAKE_CM = 100.0 * SCALE
FBX_OUT = os.path.join(OUT_DIR, MESH_NAME + ".fbx")
TEX_DIR = os.path.join(OUT_DIR, "Textures_Jayadwara2_Cape")

scene = bpy.context.scene
arm = bpy.data.objects["JD2C_Armature"]
cape = bpy.data.objects[SRC_MESH]
scene.frame_set(1)
prev_pose = arm.data.pose_position
arm.data.pose_position = "REST"
bpy.context.view_layer.update()

# JSON skala (validator membaca export_scale dari sini; jubah tanpa socket)
if MESH_NAME == "SK_Jayadwara2_Cape":
    json.dump({"mesh": MESH_NAME, "export_scale": round(SCALE, 6), "giant_height_m": GIANT_HEIGHT_M,
               "note": "jubah (docs/26): tanpa socket; mengikuti SK_Jayadwara2 lewat Copy Pose From Mesh", "sockets": []},
              open(os.path.join(OUT_DIR, MESH_NAME + "_sockets.json"), "w"), indent=2)

# tekstur: gambar yang dipakai material jubah
os.makedirs(TEX_DIR, exist_ok=True)
imgs = {n.image for m in cape.data.materials if m and m.node_tree for n in m.node_tree.nodes
        if n.type == "TEX_IMAGE" and n.image}
for img in imgs:
    key = "BC" if img.name.startswith("Color") else "N" if img.name.startswith("Normal") else "ORM" if img.name.startswith("ORM") else None
    if not key:
        continue
    path = os.path.join(TEX_DIR, f"T_Jayadwara2_Cape_{key}.png")
    tmp = img.copy()
    tmp.filepath_raw = path
    tmp.file_format = "PNG"
    tmp.save()
    bpy.data.images.remove(tmp)
    print("tekstur:", path, tuple(img.size))
# Material induk butuh Emit & Mask zona. Emit datar hitam (jubah tanpa bagian menyala). Mask zona (J2) dibuat
# make_textures_jayadwara2_cape.py dari BC; mask datar "merah penuh" hanya ditulis kalau belum ada.
flats = [("Emit", (0.0, 0.0, 0.0, 1.0))]
if not os.path.exists(os.path.join(TEX_DIR, "T_Jayadwara2_Cape_Mask.png")):
    flats.append(("Mask", (1.0, 0.0, 0.0, 0.0)))
for key, rgba in flats:
    flat = bpy.data.images.new(f"_flat_{key}", 4, 4, alpha=True)
    flat.pixels = list(rgba) * 16
    flat.filepath_raw = os.path.join(TEX_DIR, f"T_Jayadwara2_Cape_{key}.png")
    flat.file_format = "PNG"
    flat.save()
    bpy.data.images.remove(flat)

# salinan sementara, skala di-bake
tmp = bpy.data.collections.new("_EXPORT_TMP")
scene.collection.children.link(tmp)
mesh = cape.copy()
mesh.data = cape.data.copy()
tmp.objects.link(mesh)
mesh.name = mesh.data.name = MESH_NAME
for k in list(mesh.keys()):
    del mesh[k]
if mesh.data.materials:
    mesh.data.materials[0].name = "M_Jayadwara2_Cape"
arm_x = arm.copy()
arm_x.data = arm.data.copy()
arm_x.animation_data_clear()
for pb in arm_x.pose.bones:
    for c in list(pb.constraints):
        pb.constraints.remove(c)
tmp.objects.link(arm_x)
mw = mesh.matrix_world.copy()
mesh.parent = None
mesh.matrix_world = mw
for m in mesh.modifiers:
    if m.type == "ARMATURE":
        m.object = arm_x
for o in (arm_x, mesh):
    o.matrix_world = Matrix.Scale(BAKE_CM, 4) @ o.matrix_world
bpy.context.view_layer.update()
with bpy.context.temp_override(active_object=arm_x, selected_objects=[arm_x, mesh], selected_editable_objects=[arm_x, mesh]):
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
mesh.parent = arm_x
mesh.matrix_parent_inverse = arm_x.matrix_world.inverted()
export_objs = [arm_x, mesh]
for o in bpy.context.view_layer.objects:
    o.select_set(o in export_objs)

rna = bpy.ops.export_scene.fbx.get_rna_type().properties


def enum_ok(prop, value):
    p = rna.get(prop)
    return p is not None and value in [i.identifier for i in p.enum_items]


wanted = dict(filepath=FBX_OUT, use_selection=True, object_types={"ARMATURE", "MESH"}, use_mesh_modifiers=True,
              add_leaf_bones=False, use_armature_deform_only=False, bake_anim=False, use_triangles=True,
              global_scale=1.0, apply_unit_scale=True, use_custom_props=False, embed_textures=False, use_tspace=False)
for prop, val in (("axis_forward", "-Y"), ("axis_up", "Z"), ("armature_nodetype", "NULL"), ("mesh_smooth_type", "FACE"),
                  ("apply_scale_options", "FBX_SCALE_ALL")):
    if enum_ok(prop, val):
        wanted[prop] = val
kwargs = {k: v for k, v in wanted.items() if k in rna}
blocker = bpy.data.objects.get("Armature")
if blocker is not None:
    blocker.name = "Armature_tmp"
arm_x.name = "Armature"
try:
    with bpy.context.temp_override(selected_objects=export_objs, selected_editable_objects=export_objs, active_object=arm_x):
        res = bpy.ops.export_scene.fbx(**kwargs)
    print("export:", res, "->", FBX_OUT, "|", os.path.getsize(FBX_OUT) // 1024, "KB; tris",
          sum(len(p.vertices) - 2 for p in mesh.data.polygons), "; tulang", len(arm_x.data.bones), "; skala bake", round(BAKE_CM, 2))
finally:
    d = arm_x.data
    bpy.data.objects.remove(mesh, do_unlink=True)
    bpy.data.objects.remove(arm_x, do_unlink=True)
    bpy.data.armatures.remove(d)
    bpy.data.collections.remove(tmp)
    if blocker is not None:
        blocker.name = "Armature"
    arm.data.pose_position = prev_pose
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
