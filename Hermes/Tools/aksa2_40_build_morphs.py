"""Aksa2 H3b — Pembuatan 8 Morph Target Wajah & Ekspor FBX Lengkap.
Input : Hermes/Art/aksa2/Blender/aksa2_v06_F4.blend
Output:
  - Hermes/Art/aksa2/Blender/aksa2_v07_morph.blend
  - Hermes/Art/aksa2/Export/SK_Aksa2.fbx (dengan 8 shape keys)
  - Hermes/Art/aksa2/Export/SK_Aksa2_sockets.json
"""
import json
import os
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v06_F4.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v07_morph.blend"
SOURCE_FBX = ROOT / "Art" / "Export" / "SK_Aksa.fbx"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"
SOCK_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2_sockets.json"

assert BLEND_IN.exists(), f"File input tidak ditemukan: {BLEND_IN}"
assert SOURCE_FBX.exists(), f"File pembanding tidak ditemukan: {SOURCE_FBX}"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
mesh_target = bpy.data.objects.get("AK2_Source")
arm_target = bpy.data.objects.get("AK2_Armature")
assert mesh_target is not None and arm_target is not None, "AK2_Source atau AK2_Armature tidak ditemukan"

# 1. Impor SK_Aksa sebagai Sumber Morph Target
print(f"Mengimpor sumber morph {SOURCE_FBX}...")
before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(SOURCE_FBX))
new_obs = [o for o in bpy.data.objects if o not in before]
mesh_source = next(o for o in new_obs if o.type == "MESH")
arm_source = next(o for o in new_obs if o.type == "ARMATURE")
bpy.data.objects.remove(arm_source, do_unlink=True)

# Terapkan skala cm ke m pada sumber
mesh_source.matrix_world = Matrix.Scale(0.01, 4) @ mesh_source.matrix_world
bpy.context.view_layer.update()
with bpy.context.temp_override(active_object=mesh_source, selected_objects=[mesh_source]):
    bpy.ops.object.transform_apply(scale=True)

# Sejajarkan kepala SK_Aksa ke Aksa2 (skala 0.88 + translasi hidung)
nose_t = Vector((0.0015, -0.0805, 1.6082))
nose_s = Vector((0.0000, -0.1304, 1.6553))
scale = 0.88
T = Matrix.Translation(nose_t) @ Matrix.Scale(scale, 4) @ Matrix.Translation(-nose_s)
mesh_source.matrix_world = T @ mesh_source.matrix_world
bpy.context.view_layer.update()
with bpy.context.temp_override(active_object=mesh_source, selected_objects=[mesh_source]):
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 2. Transfer 8 Morph Target via IDW
if not mesh_target.data.shape_keys:
    mesh_target.shape_key_add(name="Basis")

EXP_CONFIG = [
    # (nama_ekspresi, multiplier_kekuatan, radius_meter)
    ("ak_blink_L", 2.6, 0.045),
    ("ak_blink_R", 2.6, 0.045),
    ("ak_smile", 1.2, 0.045),
    ("ak_angry", 1.1, 0.045),
    ("ak_mouth_open", 1.0, 0.045),
    ("ak_brow_up", 1.2, 0.045),
    ("ak_wince", 1.1, 0.045),
    ("ak_sad", 1.1, 0.045),
]

skeys_s = mesh_source.data.shape_keys.key_blocks
basis_s = skeys_s["Basis"]

print("=== MEMULAI TRANSFER 8 MORPH TARGET ===")
morph_summary = {}
for name, mult, rad in EXP_CONFIG:
    kb_s = skeys_s.get(name)
    if not kb_s:
        print(f"PERINGATAN: Morph {name} tidak ditemukan di sumber!")
        continue

    moves = []
    for p0, p1 in zip(basis_s.data, kb_s.data):
        d = (p1.co - p0.co) * scale * mult
        if d.length > 0.0004:
            moves.append((p0.co, d))

    kd = KDTree(len(moves))
    for idx, (co, _) in enumerate(moves):
        kd.insert(co, idx)
    kd.balance()

    # Buat atau reset shape key pada target
    kb_t = mesh_target.data.shape_keys.key_blocks.get(name)
    if not kb_t:
        kb_t = mesh_target.shape_key_add(name=name)

    moved_t = []
    for idx, v in enumerate(mesh_target.data.vertices):
        # KONTRAK: Hanya vertex kepala dan wajah (Z >= 1.45 m, Y <= 0.02 m) yang boleh bergerak
        if v.co.z >= 1.45 and v.co.y <= 0.02:
            nb = kd.find_range(v.co, rad)
            if nb:
                tot_w = 0.0
                disp = Vector((0, 0, 0))
                for n_co, n_idx, dist in nb:
                    w = 1.0 / (dist * dist + 1e-4)
                    tot_w += w
                    disp += moves[n_idx][1] * w
                disp /= tot_w
                if disp.length > 0.0005:
                    kb_t.data[idx].co = v.co + disp
                    moved_t.append(disp.length)
        else:
            # Pastikan titik di bawah leher persis sama dengan Basis
            kb_t.data[idx].co = v.co

    max_d = max(moved_t) if moved_t else 0.0
    morph_summary[name] = {"count": len(moved_t), "max_mm": max_d * 1000}
    print(f"  {name:<15}: {len(moved_t):4d} verts moved | max displacement: {max_d*1000:5.2f} mm")

# Hapus mesh sumber dari scene
bpy.data.objects.remove(mesh_source, do_unlink=True)

# 3. Simpan Workfile Blender
BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT), relative_remap=True)
print(f"Workfile Blender tersimpan ke: {BLEND_OUT}")

# 4. Ekspor FBX dengan Shape Keys Aktif
print("Mengekspor FBX dengan shape keys...")
BAKE_CM = 100.0
ARM_EXPORT_NAME = "Armature"
MESH_NAME = "SK_Aksa2"

tmp_coll = bpy.data.collections.new("_EXPORT_TMP")
bpy.context.scene.collection.children.link(tmp_coll)

joined = mesh_target.copy()
joined.data = mesh_target.data.copy()
joined.name = joined.data.name = MESH_NAME
tmp_coll.objects.link(joined)

arm_x = arm_target.copy()
arm_x.data = arm_target.data.copy()
arm_x.animation_data_clear()
tmp_coll.objects.link(arm_x)

mod = joined.modifiers.new(name="Armature", type="ARMATURE")
mod.object = arm_x

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

arm_x.name = ARM_EXPORT_NAME
kwargs = dict(
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
    axis_forward="-Y",
    axis_up="Z",
    armature_nodetype="NULL",
    mesh_smooth_type="FACE",
    apply_scale_options="FBX_SCALE_ALL",
    colors_type="SRGB",
)

FBX_OUT.parent.mkdir(parents=True, exist_ok=True)
try:
    with bpy.context.temp_override(selected_objects=export_objs, selected_editable_objects=export_objs, active_object=arm_x):
        res = bpy.ops.export_scene.fbx(**kwargs)
    print("FBX Export status:", res, "->", FBX_OUT, f"({os.path.getsize(FBX_OUT) // 1024} KB)")
finally:
    arm_data = arm_x.data
    bpy.data.objects.remove(joined, do_unlink=True)
    bpy.data.objects.remove(arm_x, do_unlink=True)
    bpy.data.armatures.remove(arm_data)
    bpy.data.collections.remove(tmp_coll)

# 5. Ekspor 7 Socket JSON
def bone_head(arm_obj, bname):
    return arm_obj.matrix_world @ arm_obj.data.bones[bname].head_local


h = lambda n: bone_head(arm_target, n)
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
            "morph_targets": morph_summary,
        },
        f,
        indent=2,
    )
print(f"Socket JSON tersimpan: {len(sockets)} socket -> {SOCK_OUT}")
print("Selesai H3b Morph Targets & Export!")
