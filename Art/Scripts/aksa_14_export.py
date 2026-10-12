"""Aksa Iterasi 1 — export proxy ke FBX (skeletal mesh tunggal, 5 slot material, armature Manny + root + sash) + socket JSON.

Jalankan di Blender (aksa_v01_proxy.blend, setelah aksa_11). Kontrak export = Jayadwara (docs/13 Iterasi 6) + spike Aksa
(docs/19 Iterasi 0): salinan armature + mesh x100 lalu di-apply (data cm), objek armature bernama `Armature` (dibuang UE;
`root` ada sebagai TULANG sungguhan), FBX_SCALE_ALL, tanpa empty, tanpa animasi. Tulang bantu Manny ikut (use_armature_deform_only=False).
Variabel opsional (globals): FBX_OUT, MESH_NAME, PREP (fungsi(salinan) -> False untuk membuang bagian; untuk LOD).
Slot material diurutkan tetap: Skin, Eyes, Hair, Cloth, Gear.
"""
import importlib
import json
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C

importlib.reload(C)

FBX_OUT = globals().get("FBX_OUT") or str(C.ART / "Export" / "SK_Aksa_Proxy.fbx")
MESH_NAME = globals().get("MESH_NAME") or "SK_Aksa_Proxy"
PREP = globals().get("PREP")
BAKE_CM = 100.0
ARM_EXPORT_NAME = "Armature"

scene = bpy.context.scene
arm = C.get_arm()
if arm.animation_data:
    scene.frame_set(1)
prev_pose_pos = arm.data.pose_position
arm.data.pose_position = "REST"
bpy.context.view_layer.update()

# ---- 1. salinan semua bagian -> satu mesh
tmp_coll = bpy.data.collections.new("_EXPORT_TMP")
scene.collection.children.link(tmp_coll)
dups = []
for ob in bpy.data.objects:
    if ob.type == "MESH" and ob.name.startswith("AK_") and "ak_kind" in ob:
        d = ob.copy()
        d.data = ob.data.copy()
        tmp_coll.objects.link(d)
        if PREP is not None and PREP(d) is False:
            bpy.data.objects.remove(d, do_unlink=True)
            continue
        dups.append(d)
act = max(dups, key=lambda o: len(o.data.vertices))
for o in bpy.context.view_layer.objects:
    o.select_set(False)
for d in dups:
    d.select_set(True)
bpy.context.view_layer.objects.active = act
with bpy.context.temp_override(active_object=act, object=act, selected_objects=dups, selected_editable_objects=dups):
    bpy.ops.object.join()
joined = bpy.context.view_layer.objects.active
joined.name = joined.data.name = MESH_NAME
if "AK_t" in joined.data.attributes:
    joined.data.attributes.remove(joined.data.attributes["AK_t"])
for k in list(joined.keys()):
    del joined[k]

# urutan slot tetap
me = joined.data
old_names = [m.name for m in me.materials]
remap = {i: C.SLOTS.index(n.replace("M_Aksa_", "")) for i, n in enumerate(old_names)}
idx = [remap[p.material_index] for p in me.polygons]
me.materials.clear()
for slot in C.SLOTS:
    me.materials.append(C.get_material(slot))
for p, i in zip(me.polygons, idx):
    p.material_index = i
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print("mesh gabungan:", joined.name, "tris:", tris, "slot:", [m.name for m in me.materials], "modifier:", [m.type for m in joined.modifiers])

# ---- 2. salinan armature; skala cm di-bake ke data
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

# ---- 3. pilih + opsi
for o in bpy.context.view_layer.objects:
    o.select_set(False)
export_objs = [arm_x, joined]
for o in export_objs:
    o.select_set(True)
rna = bpy.ops.export_scene.fbx.get_rna_type().properties


def enum_ok(prop, value):
    p = rna.get(prop)
    return p is not None and value in [i.identifier for i in p.enum_items]


wanted = dict(filepath=FBX_OUT, use_selection=True, object_types={"ARMATURE", "MESH"}, use_mesh_modifiers=True, add_leaf_bones=False,
              use_armature_deform_only=False, bake_anim=False, use_triangles=True, global_scale=1.0, apply_unit_scale=True,
              use_custom_props=False, embed_textures=False, use_tspace=False)
for prop, val in (("axis_forward", "-Y"), ("axis_up", "Z"), ("armature_nodetype", "NULL"), ("mesh_smooth_type", "FACE"),
                  ("apply_scale_options", "FBX_SCALE_ALL"), ("colors_type", "SRGB")):
    if enum_ok(prop, val):
        wanted[prop] = val
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
    arm_data = arm_x.data
    bpy.data.objects.remove(joined, do_unlink=True)
    bpy.data.objects.remove(arm_x, do_unlink=True)
    bpy.data.armatures.remove(arm_data)
    if blocker is not None:
        blocker.name = ARM_EXPORT_NAME
    for m_ in list(bpy.data.meshes):
        if m_.users == 0:
            bpy.data.meshes.remove(m_)
    bpy.data.collections.remove(tmp_coll)
    arm.data.pose_position = prev_pose_pos

# ---- 4. socket (posisi rest, ruang dunia Blender m -> ruang komponen UE cm = (x, -y, z) x 100; skala 1)
h = lambda n: C.bone_head(arm, n)  # noqa: E731
hand_dir = {s: (h(f"hand_{s}") - h(f"lowerarm_{s}")).normalized() for s in "lr"}
SOCK = {
    "hand_r_hit": ("hand_r", h("hand_r") + hand_dir["r"] * 0.11),
    "hand_l_hit": ("hand_l", h("hand_l") + hand_dir["l"] * 0.11),
    "foot_r_hit": ("ball_r", h("ball_r") + Vector((0, -0.05, 0.02))),
    "foot_l_hit": ("ball_l", h("ball_l") + Vector((0, -0.05, 0.02))),
    "pendant": ("spine_05", Vector((0.0, -0.158 + C.BODY_SHIFT_Y, 1.312))),
    "head_fx": ("head", Vector((0.0, 0.0, 1.80))),
    "back_fx": ("spine_04", Vector((0.0, 0.105, 1.26))),
}
sockets = [{"name": n, "bone": b, "blender_m": [round(p.x, 5), round(p.y, 5), round(p.z, 5)],
            "ue_component_cm": [round(p.x * 100, 3), round(-p.y * 100, 3), round(p.z * 100, 3)]} for n, (b, p) in SOCK.items()]
sock_path = os.path.join(os.path.dirname(FBX_OUT), f"{MESH_NAME}_sockets.json")
with open(sock_path, "w", encoding="utf-8") as f:
    json.dump({"mesh": MESH_NAME, "export_scale": 1.0, "note": "posisi rest; ue_component_cm = (x, -y, z) x 100 (skala 1, tinggi 180,6 cm = Manny)",
               "sockets": sockets}, f, indent=2)
print("socket:", len(sockets), "->", sock_path)
