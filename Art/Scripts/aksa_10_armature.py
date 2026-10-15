"""Aksa Iterasi 1 — armature Manny asli + penyesuaian skala referensi. Hasil: aksa_v01_proxy.blend.

Jalankan di Blender (MCP: exec(open(path).read())) di atas aksa_v00_setup.blend. Langkah:
1. Skala reference plane, landmark, penggaris dari H=1,75 (konsep) ke H=1,806 (tinggi Manny; A3 revisi).
2. Impor Art/Reference/manny/SKM_Manny_Simple.fbx (hasil spike): empty berskala 0,01 dibuang, skala di-apply (meter),
   LOD2 Manny disimpan sebagai hantu referensi `AK_REF_MannyGhost` (wire, tidak ikut export).
3. Tulang `root` ditambahkan (induk 5 tulang akar Manny; importer Blender menjadikannya objek) dan rantai `sash_01..06`
   (daun baru di bawah pelvis; UE menggabungkannya ke SK_Mannequin). Tulang bantu (ik_*, twist, jari, dst.) use_deform=False
   supaya bobot otomatis hanya jatuh ke tulang utama; tetap ikut export.
4. Simpan sebagai aksa_v01_proxy.blend (v00 tidak berubah).
"""
import importlib
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C

importlib.reload(C)

scene = bpy.context.scene
assert "aksa_v00" in bpy.data.filepath or "aksa_v01" in bpy.data.filepath, "buka aksa_v00_setup.blend dulu"
OUT = C.ART / "Blender" / "aksa" / "aksa_v01_proxy.blend"

# ---- 1. skala referensi
for ob in bpy.data.objects:
    if ob.name.startswith("AK_REF_") and ob.type == "EMPTY" and ob.data is not None:
        ob.empty_display_size = C.H * 1.2
    elif ob.name.startswith("AK_LM_"):
        pass
if not scene.get("ak_scaled"):
    for ob in bpy.data.objects:
        if ob.name.startswith("AK_LM_"):
            ob.location.z *= C.K
        elif ob.name.startswith("AK_REF_ruler"):
            ob.empty_display_size = C.H
            ob.name = f"AK_REF_ruler_{C.H}m"
    scene["ak_scaled"] = True
root_coll = bpy.data.collections["AK_Aksa"]
root_coll["ak_height_m"] = C.H
root_coll["ak_armature"] = "SKM_Manny_Simple (asli)"

# ---- 2. impor Manny
for name in (C.ARM_NAME, "AK_REF_MannyGhost"):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(C.MANNY_FBX))
new = [o for o in bpy.data.objects if o not in before]
arm = next(o for o in new if o.type == "ARMATURE")
meshes = [o for o in new if o.type == "MESH"]
for o in [arm] + meshes:
    mw = o.matrix_world.copy()
    o.parent = None
    o.matrix_world = mw
for o in new:
    if o.type == "EMPTY":
        bpy.data.objects.remove(o, do_unlink=True)
ghost = next(m for m in meshes if m.name.endswith("LOD2"))
for m in meshes:
    if m is not ghost:
        bpy.data.objects.remove(m, do_unlink=True)
ghost.modifiers.clear()
ghost.vertex_groups.clear()
ghost.data.materials.clear()
ghost.name = ghost.data.name = "AK_REF_MannyGhost"
arm.name = arm.data.name = C.ARM_NAME
for o in (arm, ghost):
    for c in list(o.users_collection):
        c.objects.unlink(o)
bpy.context.scene.collection.objects.link(arm)
bpy.context.scene.collection.objects.link(ghost)
for o in bpy.context.view_layer.objects:
    o.select_set(False)
for o in (arm, ghost):
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)       # data -> meter, skala 1
for o in (arm, ghost):
    for c in list(o.users_collection):
        c.objects.unlink(o)
C.get_collection("08_Rig").objects.link(arm)
C.get_collection("00_REF").objects.link(ghost)
ghost.display_type = "WIRE"
ghost.hide_render = True
ghost.hide_select = True
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)
for mat in list(bpy.data.materials):
    if mat.users == 0:
        bpy.data.materials.remove(mat)

# ---- 3. root + sash_01..06
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.data.edit_bones
roots = [b for b in eb if b.parent is None and b.name != "root"]
rb = eb.get("root") or eb.new("root")
rb.head, rb.tail = (0.0, 0.0, 0.0), (0.0, 0.1, 0.0)
for b in roots:
    b.parent = rb
    b.use_connect = False
pts = C.sash_path()
prev = eb["pelvis"]
for i in range(C.SASH_N):
    b = eb.get(f"sash_0{i + 1}") or eb.new(f"sash_0{i + 1}")
    b.head, b.tail = pts[i], pts[i + 1]
    b.parent = prev
    b.use_connect = False
    prev = b
bpy.ops.object.mode_set(mode="OBJECT")
for b in arm.data.bones:
    b.use_deform = b.name in C.DEFORM
print("tulang:", len(arm.data.bones), "| deform:", sum(b.use_deform for b in arm.data.bones),
      "| root anak:", [b.name for b in arm.data.bones["root"].children])
h = [arm.matrix_world @ arm.data.bones[n].head_local for n in ("pelvis", "head")]
print("pelvis z", round(h[0].z, 3), "head z", round(h[1].z, 3), "| ghost tinggi:",
      round(max(v.co.z for v in ghost.data.vertices) - min(v.co.z for v in ghost.data.vertices), 3))

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
print("Disimpan:", bpy.data.filepath)
