"""Aksa2 — Ekspor SK_Aksa2.fbx dari file blend hasil perbaikan.
Default input: Art/Blender/aksa2_v06_F4.blend
Default output: Art/Export/SK_Aksa2.fbx
"""
import json
import os
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1].parent
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
BLEND_IN = Path(argv[0]) if argv else ROOT / "Art" / "Blender" / "aksa2_v06_F4.blend"
FBX_OUT = ROOT / "Art" / "Export" / "SK_Aksa2.fbx"
SOCK_OUT = ROOT / "Art" / "Export" / "SK_Aksa2_sockets.json"

assert BLEND_IN.exists(), f"File input tidak ditemukan: {BLEND_IN}"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
mesh = bpy.data.objects.get("AK2_Source")
arm = bpy.data.objects.get("AK2_Armature")
assert mesh is not None and arm is not None, "AK2_Source atau AK2_Armature tidak ditemukan"

# Standardisasi nama material
if mesh.data.materials:
    mesh.data.materials[0].name = "M_Aksa2_Body"

# Ekspor FBX
BAKE_CM = 100.0  # kontrak docs/19 §6.4: data dalam cm, skala di-apply (sama dengan aksa_14_export.py)
ARM_EXPORT_NAME = "Armature"
MESH_NAME = "SK_Aksa2"

tmp_coll = bpy.data.collections.new("_EXPORT_TMP")
bpy.context.scene.collection.children.link(tmp_coll)

joined = mesh.copy()
joined.data = mesh.data.copy()
joined.name = joined.data.name = MESH_NAME
tmp_coll.objects.link(joined)

arm_x = arm.copy()
arm_x.data = arm.data.copy()
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

# Socket JSON
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
