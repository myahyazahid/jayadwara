"""Iterasi 1 — export proxy ke FBX (skeletal mesh tunggal + armature + socket).

Jalankan di Blender setelah 01/02. Membuat salinan sementara dari semua bagian, menggabungkannya jadi satu mesh
`SK_Jayadwara_Proxy` (4 slot material), mengekspor, lalu membersihkan salinan. Scene asli tidak berubah.
Variabel opsional sebelum exec: FBX_OUT (path tujuan), MESH_NAME, PREP (LOD: fungsi(salinan) -> False untuk membuang
bagian; boleh mengubah mesh salinan, mis. decimate — lihat 16_make_lods.py).
Opsi FBX divalidasi terhadap properti operator di Blender yang sedang dipakai (tidak hardcode buta).
"""
import os

import bpy
from mathutils import Matrix

FBX_OUT = globals().get("FBX_OUT") or r"C:\repository\unreal_engine\jayadwara\Art\Export\SK_Jayadwara_Proxy.fbx"
MESH_NAME = globals().get("MESH_NAME") or "SK_Jayadwara_Proxy"     # hero: MESH_NAME="SK_Jayadwara", FBX_OUT=...\SK_Jayadwara.fbx
PREP = globals().get("PREP")
ARM_NAME = "JD_Armature"
# Iterasi 6 (diuji di UE 5.6.1 dengan 7 varian, lihat docs/13 Iterasi 6). Importer FBX UE:
#  - menjadikan objek armature tulang root tambahan, KECUALI namanya "Armature"; transform node itu lalu dibuang;
#  - menaruh faktor unit di header FBX (dan Import Uniform Scale) sebagai SKALA tulang root, bukan di posisi tulang;
#  - mengimpor empty SOCKET_* sebagai tulang.
# Maka: armature + mesh disalin, diskalakan BAKE_CM (100: m -> cm) dan skalanya di-apply, salinan armature diberi nama
# "Armature", diekspor dengan FBX_SCALE_ALL (header 1 cm, node skala 1), tanpa empty. Hasil di UE (skala import 1):
# 89 tulang, root skala 1, tinggi 199 cm — sama konvensinya dengan Mannequin. Override lewat globals untuk uji.
ARM_EXPORT_NAME = globals().get("ARM_EXPORT_NAME") or "Armature"
APPLY_SCALE = globals().get("APPLY_SCALE") or "FBX_SCALE_ALL"
BAKE_CM = float(globals().get("BAKE_CM", 100.0))
INCLUDE_SOCKETS = bool(globals().get("INCLUDE_SOCKETS", False))

scene = bpy.context.scene
arm = bpy.data.objects[ARM_NAME]
scene.frame_set(1)
prev_pose_pos = arm.data.pose_position
arm.data.pose_position = "REST"
bpy.context.view_layer.update()

# ---- 1. salinan sementara semua bagian -> satu mesh
tmp_coll = bpy.data.collections.new("_EXPORT_TMP")
scene.collection.children.link(tmp_coll)
dups = []
for ob in bpy.data.objects:
    if ob.type == "MESH" and ob.name.startswith("JD_") and "jd_kind" in ob:
        d = ob.copy()
        d.data = ob.data.copy()
        tmp_coll.objects.link(d)
        if PREP is not None and PREP(d) is False:
            bpy.data.objects.remove(d, do_unlink=True)
            continue
        dups.append(d)
act = max(dups, key=lambda o: len(o.data.vertices))        # undersuit (punya modifier Armature)
for o in bpy.context.view_layer.objects:
    o.select_set(False)
for d in dups:
    d.select_set(True)
bpy.context.view_layer.objects.active = act
with bpy.context.temp_override(active_object=act, object=act, selected_objects=dups, selected_editable_objects=dups):
    bpy.ops.object.join()
joined = bpy.context.view_layer.objects.active
joined.name = joined.data.name = MESH_NAME
if "JD_t" in joined.data.attributes:
    joined.data.attributes.remove(joined.data.attributes["JD_t"])
for k in list(joined.keys()):
    del joined[k]
print("mesh gabungan:", joined.name, "tris:", sum(len(p.vertices) - 2 for p in joined.data.polygons),
      "slot material:", [m.name for m in joined.data.materials], "modifier:", [m.type for m in joined.modifiers])

# ---- 2. salinan armature; skala cm di-bake ke data (tulang + vertex)
arm_x = arm.copy()
arm_x.data = arm.data.copy()
arm_x.animation_data_clear()
tmp_coll.objects.link(arm_x)
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

# ---- 3. pilih objek yang diekspor: armature, mesh gabungan, (socket hanya untuk uji)
for o in bpy.context.view_layer.objects:
    o.select_set(False)
export_objs = [arm_x, joined] + ([o for o in bpy.data.objects if o.name.startswith("SOCKET_")] if INCLUDE_SOCKETS else [])
for o in export_objs:
    o.select_set(True)

# ---- 4. opsi (hanya yang dikenal operator ini)
rna = bpy.ops.export_scene.fbx.get_rna_type().properties


def enum_ok(prop, value):
    p = rna.get(prop)
    return p is not None and value in [i.identifier for i in p.enum_items]


wanted = dict(
    filepath=FBX_OUT, use_selection=True, object_types={"ARMATURE", "MESH", "EMPTY"},
    use_mesh_modifiers=True, add_leaf_bones=False, use_armature_deform_only=False,   # tulang IK (non-deform) harus ikut terekspor
    bake_anim=False,                                                                   # aksi pose test JD_PoseTest tidak ikut
    use_triangles=True, global_scale=1.0, apply_unit_scale=True, use_custom_props=False,
    embed_textures=False, use_tspace=False,
)
if enum_ok("axis_forward", "-Y"):
    wanted["axis_forward"] = "-Y"
if enum_ok("axis_up", "Z"):
    wanted["axis_up"] = "Z"
if enum_ok("armature_nodetype", "NULL"):
    wanted["armature_nodetype"] = "NULL"
if enum_ok("mesh_smooth_type", "FACE"):
    wanted["mesh_smooth_type"] = "FACE"
if enum_ok("apply_scale_options", APPLY_SCALE):
    wanted["apply_scale_options"] = APPLY_SCALE
kwargs = {k: v for k, v in wanted.items() if k in rna}
print("opsi tidak dikenal (dilewati):", sorted(set(wanted) - set(kwargs)))
os.makedirs(os.path.dirname(FBX_OUT), exist_ok=True)
blocker = bpy.data.objects.get(ARM_EXPORT_NAME)
if blocker is not None:
    blocker.name = ARM_EXPORT_NAME + "_tmp"
arm_x.name = ARM_EXPORT_NAME
try:
    with bpy.context.temp_override(selected_objects=export_objs, selected_editable_objects=export_objs, active_object=arm_x):
        res = bpy.ops.export_scene.fbx(**kwargs)
    print("export:", res, "->", FBX_OUT, "|", os.path.getsize(FBX_OUT) // 1024, "KB")
finally:
    # ---- 5. bersihkan
    arm_data = arm_x.data
    bpy.data.objects.remove(joined, do_unlink=True)
    bpy.data.objects.remove(arm_x, do_unlink=True)
    bpy.data.armatures.remove(arm_data)
    if blocker is not None:
        blocker.name = ARM_EXPORT_NAME
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    bpy.data.collections.remove(tmp_coll)
    arm.data.pose_position = prev_pose_pos
