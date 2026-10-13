"""Aksa — ganti rambut menjadi gaya 4 (helai, `ak_hair4.py`) pada file kerja yang sedang terbuka (v04/v05) TANPA mengulang kepala/pakaian/rig.

Jalankan di Blender (MCP: exec(open(path).read())). Menghapus AK_HairShell/AK_Hair/AK_HairHi lalu membangun ulang dari AK_Head
(koordinat basis), memasang modifier Armature + bobot 1.0 ke tulang `head`, simpan. Setelah ini ulangi: aksa_50_uv -> make_textures_aksa
-> aksa_51_materials -> aksa_14_export (UV & tekstur rambut berubah; jangan jalankan bila developer sudah mengecat rambut).
"""
import importlib
import sys

import bpy

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C
import ak_hair3 as H3
import ak_hair4 as H4

for m in (C, H3, H4):
    importlib.reload(m)
arm = C.get_arm()
head = bpy.data.objects["AK_Head"]
for n in ("AK_HairShell", "AK_Hair", "AK_HairHi"):
    ob = bpy.data.objects.get(n)
    if ob is not None:
        bpy.data.objects.remove(ob, do_unlink=True)
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)
HEAD_K, HEAD_PIVOT_Z, NECK_CY = 1.16, 1.535, 0.010      # HARUS sama dengan aksa_22 (kepala diperbesar; konstanta rambut untuk skala 1)
from mathutils import Vector  # noqa: E402


def _hk(co, inv):
    k = 1.0 / HEAD_K if inv else HEAD_K
    return Vector((co.x * k, NECK_CY + (co.y - NECK_CY) * k, HEAD_PIVOT_Z + (co.z - HEAD_PIVOT_Z) * k))


_tmp = head.data.copy()
for v in _tmp.vertices:
    v.co = _hk(v.co, True)
bm_shell, bm_str, bm_hi, made = H4.build(_tmp)
bpy.data.meshes.remove(_tmp)
for _bm in (bm_shell, bm_str, bm_hi):
    for v in _bm.verts:
        v.co = _hk(v.co, False)
parts = [C.finish_part("AK_HairShell", bm_shell, "03_Hair", "hair", "Hair", kind="rigid", bone="head"),
         C.finish_part("AK_Hair", bm_str, "03_Hair", "hair", "Hair", kind="rigid", bone="head"),
         C.finish_part("AK_HairHi", bm_hi, "03_Hair", "hair_hi", "Hair", kind="rigid", bone="head")]
for obj in parts:
    C.set_weights(obj, {"head": {i: 1.0 for i in range(len(obj.data.vertices))}})
    C.clean_weights(obj)
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    mod.use_vertex_groups = True
    obj.parent = arm
hz = max(v.co.z for o in parts for v in o.data.vertices)
print("helai:", made, "| tris:", {o.name: C.tri_count(o) for o in parts}, "| rambut z maks %.3f" % hz)
bpy.ops.wm.save_mainfile()
