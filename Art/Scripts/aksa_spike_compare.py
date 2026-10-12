"""Spike skeleton model Aksa, langkah S4b (docs/19 Iterasi 0): bandingkan pose referensi mesh hasil impor dengan Manny asli.

Headless: blender --background --factory-startup --python Art/Scripts/aksa_spike_compare.py
Membandingkan dua FBX yang sama-sama keluar dari UE dan masuk lewat importer Blender yang sama (konvensi sumbu
importer saling meniadakan):
  A = Art/Reference/manny/SKM_Manny_Simple.fbx          (Manny asli)
  B = Art/Export/_spike/SK_Aksa_Spike_UE.fbx            (mesh uji, diimpor ke SK_Mannequin lalu diekspor lagi dari UE)
Per tulang Manny: selisih posisi (mm) dan rotasi (derajat) di ruang dunia (meter). Lulus = semua < 1 mm dan < 0,5°.
Argumen opsional setelah `--`: <fbx A> <fbx B> (mis. SK_Aksa hasil ekspor UE: Art/Export/_spike/SK_Aksa_UE.fbx). Tulang yang hanya ada di B (sash_*, root) dilewati.
"""
import math
from pathlib import Path

import bpy
from mathutils import Matrix

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
import sys

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
FBX_A = Path(_argv[0]) if len(_argv) > 0 else ROOT / "Art" / "Reference" / "manny" / "SKM_Manny_Simple.fbx"
FBX_B = Path(_argv[1]) if len(_argv) > 1 else ROOT / "Art" / "Export" / "_spike" / "SK_Aksa_Spike_UE.fbx"


def load(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    arm = [o for o in bpy.data.objects if o not in before and o.type == "ARMATURE"][0]
    bones = {}
    for b in arm.data.bones:
        m = arm.matrix_world @ b.matrix_local
        s = m.to_scale()
        bones[b.name] = (m.translation.copy(), (m.to_3x3().normalized()), b.parent.name if b.parent else None)
    return arm, bones


for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
arm_a, A = load(FBX_A)
arm_b, B = load(FBX_B)
print("armature A:", arm_a.name, tuple(round(v, 3) for v in arm_a.rotation_euler), "| B:", arm_b.name, tuple(round(v, 3) for v in arm_b.rotation_euler))
print("tulang A:", len(A), "| B:", len(B), "| hanya di B:", sorted(set(B) - set(A)), "| hanya di A:", sorted(set(A) - set(B)))
worst_p = worst_r = 0.0
bad = []
for n, (ta, ra, pa) in A.items():
    if n not in B:
        continue
    tb, rb, pb = B[n]
    dp = (ta - tb).length * 1000
    rel = ra.inverted() @ rb
    ang = math.degrees(Matrix(rel).to_quaternion().angle)
    worst_p, worst_r = max(worst_p, dp), max(worst_r, ang)
    if dp > 1.0 or ang > 0.5 or pa != pb:
        bad.append((n, round(dp, 2), round(ang, 2), pa, pb))
print(f"selisih terburuk: posisi {worst_p:.3f} mm, rotasi {worst_r:.3f}°; tulang menyimpang: {len(bad)}")
for x in bad[:25]:
    print("  ", x)
print("LULUS" if not bad and not (set(A) - set(B)) else "TIDAK LULUS")
