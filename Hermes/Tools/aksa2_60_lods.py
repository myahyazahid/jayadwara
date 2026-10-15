"""Aksa2 H5 — Pembuatan & Ekspor LOD1, LOD2, dan LOD3 Ber-rig Tervalidasi.
Input : Hermes/Art/aksa2/Blender/aksa2_v06_F4.blend
Output:
  - Hermes/Art/aksa2/Export/SK_Aksa2_LOD1.fbx (pagu <= 25k tris)
  - Hermes/Art/aksa2/Export/SK_Aksa2_LOD2.fbx (pagu <= 10k tris)
  - Hermes/Art/aksa2/Export/SK_Aksa2_LOD3.fbx (pagu <= 4k tris)
"""
import os
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v06_F4.blend"
OUT_DIR = ROOT / "Hermes" / "Art" / "aksa2" / "Export"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
mesh = bpy.data.objects.get("AK2_Source")
arm = bpy.data.objects.get("AK2_Armature")
assert mesh is not None and arm is not None, "AK2_Source atau AK2_Armature tidak ditemukan"

BAKE_CM = 1.0
MAX_INF = 4

def get_tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)

def clean_weights(ob):
    for v in ob.data.vertices:
        gs = sorted(((g.group, g.weight) for g in v.groups), key=lambda x: -x[1])
        keep = {g: w for g, w in gs[:MAX_INF] if w > 1e-4} or ({gs[0][0]: 1.0} if gs else {})
        tot = sum(keep.values()) or 1.0
        for g, _w in gs:
            if g not in keep:
                ob.vertex_groups[g].remove([v.index])
        for g, w in keep.items():
            ob.vertex_groups[g].add([v.index], w / tot, "REPLACE")

def drop_loose(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=list(bm.edges))
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES_FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()

def export_fbx(mesh_obj, arm_obj, fbx_path):
    mesh_name = mesh_obj.name
    arm_name = "Armature"
    
    tmp_coll = bpy.data.collections.new("_EXPORT_TMP")
    bpy.context.scene.collection.children.link(tmp_coll)
    
    joined = mesh_obj.copy()
    joined.data = mesh_obj.data.copy()
    joined.name = joined.data.name = mesh_name
    tmp_coll.objects.link(joined)
    
    arm_x = arm_obj.copy()
    arm_x.data = arm_obj.data.copy()
    arm_x.animation_data_clear()
    tmp_coll.objects.link(arm_x)
    
    # Hapus mod armature lama lalu pasang ke arm_x
    for m in list(joined.modifiers):
        if m.type == "ARMATURE":
            joined.modifiers.remove(m)
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
    
    arm_x.name = arm_name
    kwargs = dict(
        filepath=str(fbx_path),
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
    
    try:
        with bpy.context.temp_override(selected_objects=export_objs, selected_editable_objects=export_objs, active_object=arm_x):
            bpy.ops.export_scene.fbx(**kwargs)
        print(f"Export selesai: {fbx_path.name} ({os.path.getsize(fbx_path)//1024} KB)")
    finally:
        arm_data = arm_x.data
        bpy.data.objects.remove(joined, do_unlink=True)
        bpy.data.objects.remove(arm_x, do_unlink=True)
        bpy.data.armatures.remove(arm_data)
        bpy.data.collections.remove(tmp_coll)

LOD_SPECS = [
    # (level, ratio, use_protect, vg_factor, max_tris)
    (1, 0.55, True, 0.60, 25000),
    (2, 0.22, True, 0.50, 10000),
    (3, 0.09, False, 0.0, 4000),
]

summary = [("LOD0", get_tris(mesh), 0)]

print("=== MEMULAI GENERASI LOD1, LOD2, LOD3 ===")
for lv, ratio, use_protect, vg_fac, max_tris in LOD_SPECS:
    ob = mesh.copy()
    ob.data = mesh.data.copy()
    ob.name = f"SK_Aksa2_LOD{lv}"
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    
    mod = ob.modifiers.new("Decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    
    if use_protect:
        vg = ob.vertex_groups.new(name="Protect_LOD")
        p_idx = [v.index for v in ob.data.vertices if (v.co.z >= 1.48 and abs(v.co.x) <= 0.12) or (abs(v.co.x) >= 0.40 and v.co.z <= 1.15) or (1.25 <= v.co.z <= 1.35 and abs(v.co.x) <= 0.05 and v.co.y <= -0.05)]
        vg.add(p_idx, 1.0, "REPLACE")
        mod.vertex_group = "Protect_LOD"
        mod.invert_vertex_group = True
        mod.vertex_group_factor = vg_fac
    
    bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    
    if use_protect:
        ob.vertex_groups.remove(ob.vertex_groups.get("Protect_LOD"))
    
    drop_loose(ob)
    clean_weights(ob)
    
    t_count = get_tris(ob)
    print(f"LOD{lv}: {t_count} tris (Pagu <= {max_tris}) -> LULUS? {t_count <= max_tris}")
    assert t_count <= max_tris, f"LOD{lv} melebihi pagu: {t_count} > {max_tris}"
    
    # Ekspor ke FBX
    fbx_out = OUT_DIR / f"SK_Aksa2_LOD{lv}.fbx"
    export_fbx(ob, arm, fbx_out)
    
    summary.append((f"LOD{lv}", t_count, 0))
    bpy.data.objects.remove(ob, do_unlink=True)

print(f"\n{'LOD':6s} {'tris':>8s} {'% LOD0':>8s}")
for nm, t, _ in summary:
    print(f"{nm:6s} {t:8d} {100 * t / summary[0][1]:7.1f}%")

print("Selesai H5 LODs!")
