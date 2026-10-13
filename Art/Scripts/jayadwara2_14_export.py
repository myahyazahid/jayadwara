"""Jayadwara2 R1/R5 — export paket UE: SK_Jayadwara2(.fbx) + socket JSON + tekstur PNG (kontrak sama dengan 05_export_fbx.py).

  blender --background Art/Blender/jayadwara2_v03_rig_r2.blend --python Art/Scripts/jayadwara2_14_export.py   (R1: jayadwara2_v02_rig_spike.blend)
  lalu: jayadwara2_15_dump_uv.py (blend yang sama) -> python -I make_textures_jayadwara2.py (menulis BC + Emit)
Variabel opsional (--python-expr + exec): OUT_DIR, MESH_NAME, GIANT_HEIGHT_M (default 45), FBX_NAME.
Kontrak (diuji di UE 5.6.1, docs/13 Iterasi 6): salinan armature bernama `Armature`; armature + mesh diskalakan
100 x (GIANT/1,90) lalu di-apply (data dalam cm, skala raksasa ter-bake); FBX_SCALE_ALL; tanpa empty; tanpa leaf bone.
Hanya LOD0 (37,7k tris; LOD1-3 di R5). Scene asli tidak berubah (rest pose dipakai saat export, dikembalikan).
"""
import json
import os

import bpy
from mathutils import Matrix, Vector

OUT_DIR = globals().get("OUT_DIR") or r"C:\repository\unreal_engine\jayadwara\Art\Export"
MESH_NAME = globals().get("MESH_NAME") or "SK_Jayadwara2"
BASE_HEIGHT_M = 1.90
GIANT_HEIGHT_M = float(globals().get("GIANT_HEIGHT_M") or 45.0)
SCALE = GIANT_HEIGHT_M / BASE_HEIGHT_M
BAKE_CM = 100.0 * SCALE
FBX_OUT = os.path.join(OUT_DIR, MESH_NAME + ".fbx")
TEX_DIR = os.path.join(OUT_DIR, "Textures_Jayadwara2")

scene = bpy.context.scene
arm = bpy.data.objects["JD2_Armature"]
body = bpy.data.objects["JD2_Body"]
scene.frame_set(1)
prev_pose = arm.data.pose_position
arm.data.pose_position = "REST"
bpy.context.view_layer.update()

# ---- sockets -> JSON (posisi Blender m & ruang komponen UE cm; konversi (x,-y,z) x100 x skala, docs/13 Iterasi 6)
socks = []
for o in sorted((o for o in bpy.data.objects if o.name.startswith("SOCKET_")), key=lambda o: o.name):
    p = o.matrix_world.translation
    socks.append({"name": o.name, "bone": o.parent_bone, "blender_m": [round(c, 4) for c in p],
                  "ue_component_cm": [round(p.x * 100 * SCALE, 3), round(-p.y * 100 * SCALE, 3), round(p.z * 100 * SCALE, 3)]})
json.dump({"mesh": MESH_NAME, "export_scale": round(SCALE, 6), "giant_height_m": GIANT_HEIGHT_M,
           "note": "posisi rest; ue_component_cm = (x, -y, z) x 100 x export_scale", "sockets": socks},
          open(os.path.join(OUT_DIR, MESH_NAME + "_sockets.json"), "w"), indent=2)

# ---- tekstur: PNG dari gambar ter-pack (Color/NormalGL/ORM)
os.makedirs(TEX_DIR, exist_ok=True)
scn = bpy.context.scene
for img in bpy.data.images:
    if img.type != "IMAGE" or not img.users:
        continue
    key = "BC" if img.name.startswith("Color") else "N" if img.name.startswith("Normal") else "ORM" if img.name.startswith("ORM") else None
    if not key:
        continue
    # BC asli Tripo ditulis sebagai _BC_src (sumber make_textures_jayadwara2.py); T_Jayadwara2_BC.png = hasil lukis (soket mata), JANGAN ditimpa
    path = os.path.join(TEX_DIR, f"T_Jayadwara2_{'BC_src' if key == 'BC' else key}.png")
    tmp = img.copy()
    tmp.filepath_raw = path
    tmp.file_format = "PNG"
    tmp.save()
    bpy.data.images.remove(tmp)
    print("tekstur:", path, tuple(img.size), "colorspace", img.colorspace_settings.name)

# ---- salinan sementara mesh + armature, skala di-bake
tmp = bpy.data.collections.new("_EXPORT_TMP")
scene.collection.children.link(tmp)
joined = body.copy()
joined.data = body.data.copy()
tmp.objects.link(joined)
joined.name = joined.data.name = MESH_NAME
for k in list(joined.keys()):
    del joined[k]
arm_x = arm.copy()
arm_x.data = arm.data.copy()
arm_x.animation_data_clear()
tmp.objects.link(arm_x)
mw = joined.matrix_world.copy()
joined.parent = None
joined.matrix_world = mw
for m in joined.modifiers:
    if m.type == "ARMATURE":
        m.object = arm_x
for o in (arm_x, joined):
    o.matrix_world = Matrix.Scale(BAKE_CM, 4) @ o.matrix_world
bpy.context.view_layer.update()
with bpy.context.temp_override(active_object=arm_x, selected_objects=[arm_x, joined], selected_editable_objects=[arm_x, joined]):
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
joined.parent = arm_x
joined.matrix_parent_inverse = arm_x.matrix_world.inverted()
for o in bpy.context.view_layer.objects:
    o.select_set(False)
export_objs = [arm_x, joined]
for o in export_objs:
    o.select_set(True)

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
          sum(len(p.vertices) - 2 for p in joined.data.polygons), "; skala bake", round(BAKE_CM, 2))
finally:
    d = arm_x.data
    bpy.data.objects.remove(joined, do_unlink=True)
    bpy.data.objects.remove(arm_x, do_unlink=True)
    bpy.data.armatures.remove(d)
    if blocker is not None:
        blocker.name = "Armature"
    arm.data.pose_position = prev_pose
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
