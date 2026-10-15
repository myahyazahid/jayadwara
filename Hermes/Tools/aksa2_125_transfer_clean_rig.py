"""
Hermes/Tools/aksa2_125_transfer_clean_rig.py
Transfer pembobotan 100% bersih dari SK_Aksa.fbx (yang 10/10 PASS tanpa ketiak melar)
ke mesh SK_Aksa2 menggunakan Data Transfer (Nearest Face Interpolated).
"""
import bpy
from pathlib import Path
from mathutils import Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v18_clean_armpit.blend"
SOURCE_FBX = Path(r"C:\repository\unreal_engine\jayadwara\Art\Export\SK_Aksa.fbx")
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v21_datatransfer_clean.blend"
FBX_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Export" / "SK_Aksa2.fbx"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))

target_mesh = next((o for o in bpy.data.objects if o.type == "MESH"), None)
target_arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# Import SK_Aksa sebagai source
bpy.ops.import_scene.fbx(filepath=str(SOURCE_FBX))
# Temukan objek-objek baru yang diimpor
new_arm = None
new_mesh = None
for o in bpy.context.selected_objects:
    if o.type == "ARMATURE" and o != target_arm:
        new_arm = o
    elif o.type == "MESH" and o != target_mesh:
        new_mesh = o

print("Source mesh:", new_mesh.name, "Source arm:", new_arm.name)

# Samakan skala: SK_Aksa dalam cm (tinggi ~180), target dalam meter (tinggi ~1.8)
# Skala new_arm dan new_mesh dengan 0.01
for o in [new_arm, new_mesh]:
    o.matrix_world = Matrix.Scale(0.01, 4) @ o.matrix_world
bpy.context.view_layer.update()

with bpy.context.temp_override(active_object=new_arm, selected_objects=[new_arm, new_mesh], selected_editable_objects=[new_arm, new_mesh]):
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

print("Bounding box target mesh:", target_mesh.dimensions)
print("Bounding box source mesh:", new_mesh.dimensions)

# Hapus vertex groups lama di target_mesh dan buat yang baru sesuai source
target_mesh.vertex_groups.clear()

# Pasang modifier DataTransfer pada target_mesh
dt = target_mesh.modifiers.new(name="WeightTransfer", type='DATA_TRANSFER')
dt.object = new_mesh
dt.use_vert_data = True
dt.data_types_verts = {'VGROUP_WEIGHTS'}
dt.vert_mapping = 'POLYINTERP_NEAREST' # Nearest Face Interpolated (sangat halus)

bpy.context.view_layer.objects.active = target_mesh
with bpy.context.temp_override(active_object=target_mesh, selected_objects=[target_mesh]):
    bpy.ops.object.datalayout_transfer(modifier=dt.name)
    bpy.ops.object.modifier_apply(modifier=dt.name)

# Hapus source mesh dan source armature
bpy.data.objects.remove(new_mesh, do_unlink=True)
bpy.data.objects.remove(new_arm, do_unlink=True)

# Batasi 4 pengaruh per vertex & normalisasi
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

# Simpan blend
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
print(f"Tersimpan di: {BLEND_OUT}")

# Ekspor FBX standar proyek (scale 100cm, -Y, Z, NULL)
tmp_coll = bpy.data.collections.new("ExportTemp")
bpy.context.scene.collection.children.link(tmp_coll)

body_dup = target_mesh.copy()
body_dup.data = target_mesh.data.copy()
body_dup.name = body_dup.data.name = "SK_Aksa2"
tmp_coll.objects.link(body_dup)

arm_dup = target_arm.copy()
arm_dup.data = target_arm.data.copy()
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

print(f"SK_Aksa2.fbx v21 (DataTransfer Clean) berhasil diekspor: {res} -> {FBX_OUT}")
bpy.ops.wm.quit_blender()
