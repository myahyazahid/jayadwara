"""
Hermes/Tools/aksa2_155_clamp_clavicle.py
Menyelaraskan bobot clavicle di bawah ketiak (Z <= 1.32m) sesuai model asli SK_Aksa:
- Di bawah Z < 1.26m: clavicle dihapus total (100% spine_03/04).
- Antara 1.26m <= Z <= 1.32m: clavicle dibatasi maksimal 20% (transisi halus), sisanya ke spine_04.
- Menghilangkan 1-2 helai poligon ketiak yang masih tertarik saat lompat.
"""
import bpy
from pathlib import Path
from mathutils import Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v26_clean_topology.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v27_flawless_armpit.blend"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

mesh_obj = next((o for o in bpy.data.objects if o.type == "MESH"), None)
arm_obj = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

vg_map = {vg.name: vg for vg in mesh_obj.vertex_groups}

clamped_count = 0
for v in mesh_obj.data.vertices:
    abs_x = abs(v.co.x)
    z = v.co.z

    # Area torso ketiak (|X| <= 0.27m, Z <= 1.32m)
    if abs_x <= 0.27 and z <= 1.32:
        for clav_name in ['clavicle_l', 'clavicle_r']:
            if clav_name in vg_map:
                try:
                    w = vg_map[clav_name].weight(v.index)
                except RuntimeError:
                    w = 0.0
                
                if w > 0.01:
                    if z < 1.26:
                        # Hapus total
                        vg_map[clav_name].remove([v.index])
                        vg_map['spine_03'].add([v.index], w * 0.5, 'ADD')
                        vg_map['spine_04'].add([v.index], w * 0.5, 'ADD')
                        clamped_count += 1
                    else:
                        # Gradien halus: max 0.20 di Z=1.32m
                        max_w = (z - 1.26) / (1.32 - 1.26) * 0.20
                        if w > max_w:
                            diff = w - max_w
                            vg_map[clav_name].add([v.index], -diff, 'ADD')
                            vg_map['spine_04'].add([v.index], diff, 'ADD')
                            clamped_count += 1

print(f"Total verteks dengan bobot clavicle yang diredam di ketiak: {clamped_count} verteks")

# Normalisasi 4 influences
bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
print(f"Tersimpan di: {BLEND_OUT}")

# Ekspor FBX standar proyek
tmp_coll = bpy.data.collections.new("ExportTemp")
bpy.context.scene.collection.children.link(tmp_coll)

body_dup = mesh_obj.copy()
body_dup.data = mesh_obj.data.copy()
body_dup.name = body_dup.data.name = "SK_Aksa2"
tmp_coll.objects.link(body_dup)

arm_dup = arm_obj.copy()
arm_dup.data = arm_obj.data.copy()
arm_dup.animation_data_clear()
arm_dup.name = "Armature"
tmp_coll.objects.link(arm_dup)

mw = body_dup.matrix_world.copy()
body_dup.parent = None
body_dup.matrix_world = mw
for m in body_dup.modifiers:
    if m.type == "ARMATURE":
        m.object = arm_dup

BAKE_CM = 100.0
for o in (arm_dup, body_dup):
    o.matrix_world = Matrix.Scale(BAKE_CM, 4) @ o.matrix_world
bpy.context.view_layer.update()

with bpy.context.temp_override(active_object=arm_dup, selected_objects=[arm_dup, body_dup], selected_editable_objects=[arm_dup, body_dup]):
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

body_dup.parent = arm_dup
body_dup.matrix_parent_inverse = arm_dup.matrix_world.inverted()

for o in bpy.context.view_layer.objects:
    o.select_set(False)
export_objs = [arm_dup, body_dup]
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
for prop, val in (("axis_forward", "-Y"), ("axis_up", "Z"),
                  ("armature_nodetype", "NULL"), ("mesh_smooth_type", "FACE"),
                  ("apply_scale_options", "FBX_SCALE_ALL"), ("colors_type", "SRGB")):
    if enum_ok(prop, val):
        wanted[prop] = val

kwargs = {k: v for k, v in wanted.items() if k in rna}
with bpy.context.temp_override(selected_objects=export_objs, selected_editable_objects=export_objs, active_object=arm_dup):
    res = bpy.ops.export_scene.fbx(**kwargs)

print(f"SK_Aksa2.fbx v27 (Flawless Armpit) berhasil diekspor: {res} -> {FBX_OUT}")
bpy.ops.wm.quit_blender()
