"""Tuyul K1 — buat armature (skeleton sendiri, nama Mannequin + jaw) dari mesh intake.

  blender --background Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend \
      --python Hermes/Tools/tuyul_10_rig.py
Hasil: Hermes/Art/tuyul/Blender/tuyul_v02_skeleton.blend (objek `TY_Armature`, collection 09_Rig).
Belum ada skinning (itu K3). Pola: Art/Scripts/jerangkong_10_build.py (bagian armature).
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import tuyul_skeleton as SK  # noqa: E402

ROOT = r"C:\repository\unreal_engine\jayadwara_hermes_tuyul"
OUT = os.path.join(ROOT, "Hermes", "Art", "tuyul", "Blender", "tuyul_v02_skeleton.blend")
ARM_NAME = "TY_Armature"

scene = bpy.context.scene
root_coll = bpy.data.collections["TY_Tuyul"]
rig_coll = bpy.data.collections.get("09_Rig") or bpy.data.collections.new("09_Rig")
if rig_coll.name not in root_coll.children:
    root_coll.children.link(rig_coll)

# bersihkan hasil lama
for ob in list(bpy.data.objects):
    if ob.name == ARM_NAME:
        bpy.data.objects.remove(ob, do_unlink=True)

arm_data = bpy.data.armatures.new(ARM_NAME)
arm = bpy.data.objects.new(ARM_NAME, arm_data)
rig_coll.objects.link(arm)
arm.show_in_front = True
arm_data.display_type = "OCTAHEDRAL"

for o in bpy.context.view_layer.objects:
    o.select_set(False)
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_data.edit_bones
bones = SK.build_bones()
for name, parent, head, tail, connect in bones:
    b = eb.new(name)
    b.head, b.tail = head, tail
    b.roll = 0.0
    b.use_deform = name not in SK.IK_BONES
for name, parent, head, tail, connect in bones:
    if parent:
        eb[name].parent = eb[parent]
        eb[name].use_connect = connect
bpy.ops.object.mode_set(mode="OBJECT")
print("tulang:", len(arm_data.bones))

# tabel sendi (head tiap tulang deform) untuk laporan
print("== TABEL SENDI (head, m) ==")
for name, parent, head, tail, connect in bones:
    if name not in SK.IK_BONES and name != "root":
        print(f"  {name:16s} ({head.x:+.3f}, {head.y:+.3f}, {head.z:+.3f})")

bpy.ops.wm.save_as_mainfile(filepath=OUT, relative_remap=True)
print("Disimpan:", OUT)
