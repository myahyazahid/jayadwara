"""Spike skeleton model Aksa, langkah S3 (docs/19 Iterasi 0): armature Manny -> FBX sesuai kontrak export.

Headless: blender --background --factory-startup --python Art/Scripts/aksa_spike_roundtrip.py
Variabel opsional (globals sebelum exec / edit di bawah): LEAF (tulang daun sash_01..06; default False supaya skeleton
SK_Mannequin di UE tidak berubah selama spike), ROOT_TAIL (arah tulang `root`).
1. Impor Art/Reference/manny/SKM_Manny_Simple.fbx (hasil Tools/ue_export_manny.py). Importer menaruh data dalam cm di bawah
   empty berskala 0,01 dan menjadikan node `root` sebagai OBJEK armature: empty dibuang, skala di-apply (data jadi meter),
   lalu `root` dibuat sebagai TULANG (induk pelvis, ik_foot_root, ik_hand_root, interaction, center_of_mass).
2. Mesh uji kaku (kapsul per segmen, bobot 1.0 ke satu tulang) (+ tulang daun bila LEAF).
3. Ekspor memakai kontrak yang sama dengan Jayadwara (docs/13 Iterasi 6): salinan armature + mesh x100 lalu di-apply,
   objek armature bernama `Armature` (dibuang UE), FBX_SCALE_ALL, tanpa empty, tanpa animasi.
Hasil: Art/Export/_spike/SK_Aksa_Spike.fbx. Lanjut: Tools/ue_spike_aksa_import.py, lalu aksa_spike_compare.py.
"""
import math
import os
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
FBX_IN = ROOT / "Art" / "Reference" / "manny" / "SKM_Manny_Simple.fbx"
FBX_OUT = ROOT / "Art" / "Export" / "_spike" / "SK_Aksa_Spike.fbx"
APPLY_SCALE = "FBX_SCALE_ALL"
BAKE_CM = 100.0


def clear():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def import_manny(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    new = [o for o in bpy.data.objects if o not in before]
    return [o for o in new if o.type == "ARMATURE"][0], [o for o in new if o.type == "MESH"]


def bone_head(arm, name):
    return arm.matrix_world @ arm.data.bones[name].head_local


LEAF = bool(globals().get("LEAF", False))
ROOT_TAIL = globals().get("ROOT_TAIL") or (0.0, 0.1, 0.0)

clear()
arm, meshes = import_manny(FBX_IN)
for m in meshes:
    bpy.data.objects.remove(m, do_unlink=True)
holder = arm.parent
mw = arm.matrix_world.copy()
arm.parent = None
arm.matrix_world = mw
if holder is not None:
    for ch in list(holder.children_recursive):
        if ch.type == "EMPTY":
            bpy.data.objects.remove(ch, do_unlink=True)
    bpy.data.objects.remove(holder, do_unlink=True)
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)       # data dalam meter, skala 1

bpy.ops.object.mode_set(mode="EDIT")
eb = arm.data.edit_bones
roots = [b for b in eb if b.parent is None]
root_names = [b.name for b in roots]
rb = eb.new("root")
rb.head = (0.0, 0.0, 0.0)
rb.tail = ROOT_TAIL
for b in roots:
    b.parent = rb
    b.use_connect = False
if LEAF:
    start = Vector((0.13, -0.05, 0.95))
    prev = eb["pelvis"]
    for i in range(1, 7):
        b = eb.new(f"sash_{i:02d}")
        b.head = start + Vector((0.02 * i, 0.0, -0.08 * (i - 1)))
        b.tail = start + Vector((0.02 * i, 0.0, -0.08 * i))
        b.parent = prev
        b.use_connect = False
        prev = b
bpy.ops.object.mode_set(mode="OBJECT")
print("root bone dibuat; induk dari:", root_names, "| LEAF:", LEAF, "| tulang:", len(arm.data.bones))

# ---- mesh uji kaku
SEG = [("pelvis", "spine_02", 0.17), ("spine_02", "spine_05", 0.18), ("spine_05", "neck_01", 0.14),
       ("neck_01", "head", 0.055), ("head", None, 0.10),
       ("upperarm_l", "lowerarm_l", 0.05), ("lowerarm_l", "hand_l", 0.04), ("hand_l", None, 0.04),
       ("upperarm_r", "lowerarm_r", 0.05), ("lowerarm_r", "hand_r", 0.04), ("hand_r", None, 0.04),
       ("thigh_l", "calf_l", 0.08), ("calf_l", "foot_l", 0.06), ("foot_l", "ball_l", 0.05),
       ("thigh_r", "calf_r", 0.08), ("calf_r", "foot_r", 0.06), ("foot_r", "ball_r", 0.05)]
bm = bmesh.new()
groups = {}
for a, b, r in SEG:
    p0 = bone_head(arm, a)
    if b is None:                                   # kepala / tangan: ujung = +dorong kecil
        p1 = p0 + (Vector((0, 0, 0.18)) if a == "head" else (bone_head(arm, a) - bone_head(arm, a.replace("hand", "lowerarm"))).normalized() * 0.09)
    else:
        p1 = bone_head(arm, b)
    d = p1 - p0
    mat = Matrix.Translation((p0 + p1) / 2) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=r, radius2=r * 0.9, depth=d.length, matrix=mat)
    groups[a] = groups.get(a, []) + list(res["verts"])
if LEAF:
    sash_pts = [Vector((0.13 + 0.02 * i, -0.05, 0.95 - 0.08 * i)) for i in range(7)]
    sash_rows = []
    for p in sash_pts:
        sash_rows.append((bm.verts.new(p + Vector((-0.04, 0, 0))), bm.verts.new(p + Vector((0.04, 0, 0)))))
    for (a0, b0), (a1, b1) in zip(sash_rows, sash_rows[1:]):
        bm.faces.new((a0, b0, b1, a1))
    for i, (va, vb) in enumerate(sash_rows):
        groups.setdefault(f"sash_{min(i + 1, 6):02d}", []).extend([va, vb])
bm.verts.ensure_lookup_table()
bm.verts.index_update()
groups = {k: [v.index for v in vs] for k, vs in groups.items()}
me = bpy.data.meshes.new("SK_Aksa_Spike")
bm.to_mesh(me)
bm.free()
mesh = bpy.data.objects.new("SK_Aksa_Spike", me)
bpy.context.scene.collection.objects.link(mesh)
for name, idx in groups.items():
    vg = mesh.vertex_groups.new(name=name)
    vg.add(idx, 1.0, "REPLACE")
mod = mesh.modifiers.new("Armature", "ARMATURE")
mod.object = arm
mesh.parent = arm
mat = bpy.data.materials.new("M_Aksa_Spike")
me.materials.append(mat)
print("mesh uji:", len(me.vertices), "vert,", len(me.polygons), "poly; tulang:", len(arm.data.bones))

# ---- ekspor sesuai kontrak (salinan armature bernama `root`, cm, skala di-apply)
arm.name = "Arm_src"
arm_x = arm.copy()
arm_x.data = arm.data.copy()
bpy.context.scene.collection.objects.link(arm_x)
mesh_x = mesh.copy()
mesh_x.data = mesh.data.copy()
bpy.context.scene.collection.objects.link(mesh_x)
mesh_x.parent = None
for m in mesh_x.modifiers:
    if m.type == "ARMATURE":
        m.object = arm_x
for o in (arm_x, mesh_x):
    o.matrix_world = Matrix.Scale(BAKE_CM, 4) @ o.matrix_world
bpy.context.view_layer.update()
with bpy.context.temp_override(active_object=arm_x, selected_objects=[arm_x, mesh_x], selected_editable_objects=[arm_x, mesh_x]):
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
mesh_x.parent = arm_x
mesh_x.matrix_parent_inverse = arm_x.matrix_world.inverted()
arm_x.name = "Armature"
for o in bpy.context.view_layer.objects:
    o.select_set(False)
for o in (arm_x, mesh_x):
    o.select_set(True)
rna = bpy.ops.export_scene.fbx.get_rna_type().properties
wanted = dict(filepath=str(FBX_OUT), use_selection=True, object_types={"ARMATURE", "MESH"}, use_mesh_modifiers=True,
              add_leaf_bones=False, use_armature_deform_only=False, bake_anim=False, use_triangles=True,
              global_scale=1.0, apply_unit_scale=True, use_custom_props=False, embed_textures=False,
              axis_forward="-Y", axis_up="Z", armature_nodetype="NULL", mesh_smooth_type="FACE",
              apply_scale_options=APPLY_SCALE)
kw = {k: v for k, v in wanted.items() if k in rna}
print("opsi dilewati:", sorted(set(wanted) - set(kw)))
os.makedirs(FBX_OUT.parent, exist_ok=True)
with bpy.context.temp_override(selected_objects=[arm_x, mesh_x], selected_editable_objects=[arm_x, mesh_x], active_object=arm_x):
    print("export:", bpy.ops.export_scene.fbx(**kw), FBX_OUT, os.path.getsize(FBX_OUT) // 1024, "KB")
