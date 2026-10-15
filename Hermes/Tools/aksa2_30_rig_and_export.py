"""Aksa2 H3 — Rigging, Skinning Spike, Anatomi Refinements, dan Ekspor FBX Kontrak Proyek.
Input : Hermes/Art/aksa2/Blender/aksa2_v03_clean.blend
Output:
  - Hermes/Art/aksa2/Blender/aksa2_v04_rig.blend
  - Hermes/Art/aksa2/Export/SK_Aksa2.fbx
  - Hermes/Art/aksa2/Export/SK_Aksa2_sockets.json
"""
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import bpy
import mathutils
from mathutils import Matrix, Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v03_clean.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v04_rig.blend"
SOURCE_FBX = ROOT / "Art" / "Export" / "SK_Aksa.fbx"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"
SOCK_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2_sockets.json"

assert BLEND_IN.exists(), f"File input tidak ditemukan: {BLEND_IN}"
assert SOURCE_FBX.exists(), f"File pembanding tidak ditemukan: {SOURCE_FBX}"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
mesh = bpy.data.objects.get("AK2_Source")
arm = bpy.data.objects.get("AK2_Armature")
assert mesh is not None and arm is not None, "AK2_Source atau AK2_Armature tidak ditemukan"

# ------------------------------------------------------------------ 1) Standardisasi Nama Material
if mesh.data.materials:
    mesh.data.materials[0].name = "M_Aksa2_Body"
print("Material slot:", [m.name for m in mesh.data.materials])

# ------------------------------------------------------------------ 2) Transfer Bobot dari SK_Aksa.fbx
print(f"Mengimpor sumber bobot {SOURCE_FBX}...")
before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(SOURCE_FBX))
new_obs = [o for o in bpy.data.objects if o not in before]
new_arm = next(o for o in new_obs if o.type == "ARMATURE")
new_mesh = next(o for o in new_obs if o.type == "MESH")

# Skala 0.01 (cm -> meter) agar sejajar dengan target mesh
for o in [new_arm, new_mesh]:
    o.matrix_world = Matrix.Scale(0.01, 4) @ o.matrix_world
bpy.context.view_layer.update()

with bpy.context.temp_override(active_object=new_arm, selected_objects=[new_arm, new_mesh], selected_editable_objects=[new_arm, new_mesh]):
    bpy.ops.object.transform_apply(scale=True)

# DataTransfer
mesh.vertex_groups.clear()
dt = mesh.modifiers.new(name="WeightTransfer", type="DATA_TRANSFER")
dt.object = new_mesh
dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"

bpy.context.view_layer.objects.active = mesh
with bpy.context.temp_override(active_object=mesh, selected_objects=[mesh]):
    bpy.ops.object.datalayout_transfer(modifier=dt.name)
    bpy.ops.object.modifier_apply(modifier=dt.name)

bpy.data.objects.remove(new_mesh, do_unlink=True)
bpy.data.objects.remove(new_arm, do_unlink=True)
print(f"DataTransfer selesai, total vertex groups: {len(mesh.vertex_groups)}")

# ------------------------------------------------------------------ 3) Kunci Bagian Kaku (docs/21 D8 & aksa_hermes.md H3)
vg_by_name = {vg.name: vg for vg in mesh.vertex_groups}
vg_by_idx = {vg.index: vg.name for vg in mesh.vertex_groups}

locked_verts = set()
for v in mesh.data.vertices:
    ax = abs(v.co.x)
    cz = v.co.z
    cy = v.co.y
    side = "_l" if v.co.x > 0 else "_r"

    # Rambut & Kepala -> head 100%
    if cz >= 1.58:
        for g in list(v.groups):
            mesh.vertex_groups[g.group].remove([v.index])
        if "head" in vg_by_name:
            vg_by_name["head"].add([v.index], 1.0, "REPLACE")
        locked_verts.add(v.index)

    # Liontin dada -> spine_05 100%
    elif 1.25 <= cz <= 1.35 and ax <= 0.05 and cy <= -0.05:
        for g in list(v.groups):
            mesh.vertex_groups[g.group].remove([v.index])
        if "spine_05" in vg_by_name:
            vg_by_name["spine_05"].add([v.index], 1.0, "REPLACE")
        locked_verts.add(v.index)

    # Gesper sabuk pinggang -> pelvis 100%
    elif 0.93 <= cz <= 1.05 and ax <= 0.08 and cy <= -0.06:
        for g in list(v.groups):
            mesh.vertex_groups[g.group].remove([v.index])
        if "pelvis" in vg_by_name:
            vg_by_name["pelvis"].add([v.index], 1.0, "REPLACE")
        locked_verts.add(v.index)

    # Sol sepatu -> foot / ball 100%
    elif cz <= 0.035:
        for g in list(v.groups):
            bname = vg_by_idx.get(g.group, "")
            if not ("foot" in bname or "ball" in bname):
                mesh.vertex_groups[g.group].remove([v.index])
        target_b = f"ball{side}" if cy < -0.05 else f"foot{side}"
        if target_b in vg_by_name:
            vg_by_name[target_b].add([v.index], 1.0, "ADD")
        locked_verts.add(v.index)

print(f"Bagian kaku dikunci: {len(locked_verts)} vertex.")

# ------------------------------------------------------------------ 4) Laplacian Weight Smoothing pada Sendi Fleksibel
print("Menjalankan Laplacian weight smoothing pada zona sendi...")
neighbors = defaultdict(list)
for e in mesh.data.edges:
    neighbors[e.vertices[0]].append(e.vertices[1])
    neighbors[e.vertices[1]].append(e.vertices[0])

alpha = 0.35
# Smooth 3 pass pada sendi bahu, siku, dan paha
for pass_num in range(3):
    cur_weights = {v.index: {g.group: g.weight for g in v.groups} for v in mesh.data.vertices}
    for v in mesh.data.vertices:
        if v.index in locked_verts:
            continue
        ax = abs(v.co.x)
        cz = v.co.z
        is_joint = (
            (1.10 <= cz <= 1.50 and ax >= 0.10)
            or (0.95 <= cz <= 1.25 and ax >= 0.25)
            or (0.75 <= cz <= 1.00 and ax >= 0.05)
        )
        if is_joint:
            nb = neighbors[v.index]
            if not nb:
                continue
            all_groups = set(cur_weights[v.index].keys())
            for n_idx in nb:
                all_groups.update(cur_weights[n_idx].keys())
            new_w = {}
            for g in all_groups:
                w_self = cur_weights[v.index].get(g, 0.0)
                w_nb = sum(cur_weights[n_idx].get(g, 0.0) for n_idx in nb) / len(nb)
                val = (1.0 - alpha) * w_self + alpha * w_nb
                if val > 0.005:
                    new_w[g] = val
            for g in list(v.groups):
                mesh.vertex_groups[g.group].remove([v.index])
            for g, w in new_w.items():
                mesh.vertex_groups[g].add([v.index], w, "REPLACE")

# ------------------------------------------------------------------ 5) Limit 4 Eksplisit & Normalisasi
print("Membatasi maksimal 4 pengaruh bobot per vertex dan normalisasi...")
for v in mesh.data.vertices:
    if len(v.groups) > 4:
        sorted_groups = sorted(v.groups, key=lambda g: g.weight, reverse=True)
        for g in sorted_groups[4:]:
            mesh.vertex_groups[g.group].remove([v.index])

# Normalisasi manual presisi
for v in mesh.data.vertices:
    total_w = sum(g.weight for g in v.groups)
    if total_w > 1e-6:
        for g in v.groups:
            mesh.vertex_groups[g.group].add([v.index], g.weight / total_w, "REPLACE")
    else:
        vg_by_name["pelvis"].add([v.index], 1.0, "REPLACE")

# Penyesuaian telapak di z=0 dan tinggi 1.806 m
zs = [v.co.z for v in mesh.data.vertices]
z_min = min(zs)
print(f"Telapak Z minimum saat ini: {z_min:.4f} m, mengangkat sebesar {-z_min:.4f} m...")
mesh.data.transform(Matrix.Translation((0, 0, -z_min)))

# Sesuaikan puncak ke tepat 1.806 m
zs_now = [v.co.z for v in mesh.data.vertices]
z_max = max(zs_now)
scale_z = 1.806 / z_max
print(f"Puncak Z saat ini: {z_max:.4f} m, menyesuaikan skala Z: x{scale_z:.4f}...")
mesh.data.transform(Matrix.Scale(scale_z, 4, Vector((0, 0, 1))))
mesh.data.update()

# Pasang modifier Armature pada mesh
for m in list(mesh.modifiers):
    if m.type == "ARMATURE":
        bpy.data.objects.remove(m, do_unlink=True)
mod_arm = mesh.modifiers.new(name="Armature", type="ARMATURE")
mod_arm.object = arm

# Simpan blend kerja
BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT), relative_remap=True)
print(f"Workfile Blender tersimpan ke: {BLEND_OUT}")

# ------------------------------------------------------------------ 6) Ekspor FBX Kontrak Proyek (docs/19 §6.4)
BAKE_CM = 100.0
ARM_EXPORT_NAME = "Armature"
MESH_NAME = "SK_Aksa2"

tmp_coll = bpy.data.collections.new("_EXPORT_TMP")
bpy.context.scene.collection.children.link(tmp_coll)

# Duplikat mesh
joined = mesh.copy()
joined.data = mesh.data.copy()
joined.name = joined.data.name = MESH_NAME
tmp_coll.objects.link(joined)

# Duplikat armature
arm_x = arm.copy()
arm_x.data = arm.data.copy()
arm_x.animation_data_clear()
tmp_coll.objects.link(arm_x)

# Bind modifier ke arm_x
for m in joined.modifiers:
    if m.type == "ARMATURE":
        m.object = arm_x

# Bake cm (skala 100)
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


wanted = dict(
    filepath=str(FBX_OUT),
    use_selection=True,
    object_types={"ARMATURE", "MESH"},
    use_mesh_modifiers=True,
    add_leaf_bones=False,
    use_armature_deform_only=False,
    bake_anim=False,
    use_triangles=True,
    global_scale=1.0,
    apply_unit_scale=True,
    use_custom_props=False,
    embed_textures=False,
    use_tspace=False,
)
for prop, val in (
    ("axis_forward", "-Y"),
    ("axis_up", "Z"),
    ("armature_nodetype", "NULL"),
    ("mesh_smooth_type", "FACE"),
    ("apply_scale_options", "FBX_SCALE_ALL"),
    ("colors_type", "SRGB"),
):
    if enum_ok(prop, val):
        wanted[prop] = val
kwargs = {k: v for k, v in wanted.items() if k in rna}

FBX_OUT.parent.mkdir(parents=True, exist_ok=True)
blocker = bpy.data.objects.get(ARM_EXPORT_NAME)
if blocker is not None:
    blocker.name = ARM_EXPORT_NAME + "_tmp"
arm_x.name = ARM_EXPORT_NAME

try:
    with bpy.context.temp_override(selected_objects=export_objs, selected_editable_objects=export_objs, active_object=arm_x):
        res = bpy.ops.export_scene.fbx(**kwargs)
    print("FBX Export status:", res, "->", FBX_OUT, f"({os.path.getsize(FBX_OUT) // 1024} KB)")
finally:
    arm_data = arm_x.data
    bpy.data.objects.remove(joined, do_unlink=True)
    bpy.data.objects.remove(arm_x, do_unlink=True)
    bpy.data.armatures.remove(arm_data)
    if blocker is not None:
        blocker.name = ARM_EXPORT_NAME
    bpy.data.collections.remove(tmp_coll)

# ------------------------------------------------------------------ 7) Ekspor 7 Socket JSON Standar Proyek
def bone_head(arm_obj, bname):
    return arm_obj.matrix_world @ arm_obj.data.bones[bname].head_local


h = lambda n: bone_head(arm, n)
hand_dir = {s: (h(f"hand_{s}") - h(f"lowerarm_{s}")).normalized() for s in "lr"}

SOCK = {
    "hand_r_hit": ("hand_r", h("hand_r") + hand_dir["r"] * 0.11),
    "hand_l_hit": ("hand_l", h("hand_l") + hand_dir["l"] * 0.11),
    "foot_r_hit": ("ball_r", h("ball_r") + Vector((0, -0.05, 0.02))),
    "foot_l_hit": ("ball_l", h("ball_l") + Vector((0, -0.05, 0.02))),
    "pendant": ("spine_05", Vector((0.0, -0.136, 1.312))),
    "head_fx": ("head", Vector((0.0, 0.0, 1.80))),
    "back_fx": ("spine_04", Vector((0.0, 0.105, 1.26))),
}

sockets = [
    {
        "name": n,
        "bone": b,
        "blender_m": [round(p.x, 5), round(p.y, 5), round(p.z, 5)],
        "ue_component_cm": [round(p.x * 100, 3), round(-p.y * 100, 3), round(p.z * 100, 3)],
    }
    for n, (b, p) in SOCK.items()
]

SOCK_OUT.parent.mkdir(parents=True, exist_ok=True)
with open(SOCK_OUT, "w", encoding="utf-8") as f:
    json.dump(
        {
            "mesh": MESH_NAME,
            "export_scale": 1.0,
            "note": "posisi rest; ue_component_cm = (x, -y, z) x 100 (skala 1, tinggi 180,6 cm = Manny)",
            "sockets": sockets,
        },
        f,
        indent=2,
    )
print(f"Socket JSON tersimpan: {len(sockets)} socket -> {SOCK_OUT}")
print("Selesai H3 Rig & Export!")
