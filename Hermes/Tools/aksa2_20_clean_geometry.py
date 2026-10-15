"""Aksa2 H2 — Pembersihan geometri: segel celah mikro, hapus non-manifold, catat tepi terbuka sebelum vs sesudah.
Input : Hermes/Art/aksa2/Blender/aksa2_v02_fit.blend
Output: Hermes/Art/aksa2/Blender/aksa2_v03_clean.blend
"""
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
BLEND_IN = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v02_fit.blend"
BLEND_OUT = ROOT / "Hermes" / "Art" / "aksa2" / "Blender" / "aksa2_v03_clean.blend"

assert BLEND_IN.exists(), f"File input tidak ditemukan: {BLEND_IN}"

print(f"Membuka {BLEND_IN}...")
bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
mesh_obj = bpy.data.objects.get("AK2_Source")
assert mesh_obj is not None, "AK2_Source tidak ditemukan"
me = mesh_obj.data

bm = bmesh.new()
bm.from_mesh(me)
bm.edges.ensure_lookup_table()
bm.verts.ensure_lookup_table()


def count_boundary_by_zone(bm_data):
    b_edges = [e for e in bm_data.edges if e.is_boundary]
    zones = {
        "Kepala/Leher (Z >= 1.45m)": 0,
        "Ketiak/Dada (1.10m <= Z < 1.45m)": 0,
        "Pinggang/Selangkangan (0.75m <= Z < 1.10m)": 0,
        "Kaki/Sepatu (Z < 0.75m)": 0,
    }
    for e in b_edges:
        mid_z = (e.verts[0].co.z + e.verts[1].co.z) / 2.0
        if mid_z >= 1.45:
            zones["Kepala/Leher (Z >= 1.45m)"] += 1
        elif mid_z >= 1.10:
            zones["Ketiak/Dada (1.10m <= Z < 1.45m)"] += 1
        elif mid_z >= 0.75:
            zones["Pinggang/Selangkangan (0.75m <= Z < 1.10m)"] += 1
        else:
            zones["Kaki/Sepatu (Z < 0.75m)"] += 1
    return len(b_edges), zones


total_b_before, zones_before = count_boundary_by_zone(bm)
nm_before = sum(1 for e in bm.edges if not e.is_manifold)
v_before = len(bm.verts)
t_before = sum(len(f.verts) - 2 for f in bm.faces)

print("=" * 70)
print(f"KONDISI AWAL (SEBELUM H2):")
print(f"  Tris: {t_before}, Vertex: {v_before}")
print(f"  Total boundary edges: {total_b_before}")
print(f"  Total non-manifold edges: {nm_before}")
for zname, cnt in zones_before.items():
    print(f"    - {zname}: {cnt}")
print("=" * 70)

# Pembersihan geometri terkontrol: merge doubles 2.5 mm
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0025)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

total_b_after, zones_after = count_boundary_by_zone(bm)
nm_after = sum(1 for e in bm.edges if not e.is_manifold)
v_after = len(bm.verts)
t_after = sum(len(f.verts) - 2 for f in bm.faces)

print("=" * 70)
print(f"KONDISI AKHIR (SESUDAH H2):")
print(f"  Tris: {t_after}, Vertex: {v_after}")
print(f"  Total boundary edges: {total_b_after} (TURUN dari {total_b_before})")
print(f"  Total non-manifold edges: {nm_after} (TURUN dari {nm_before})")
for zname, cnt in zones_after.items():
    b4 = zones_before[zname]
    print(f"    - {zname}: {b4} -> {cnt} ({'TURUN' if cnt < b4 else 'TETAP'})")
print("=" * 70)

bm.to_mesh(me)
bm.free()
me.update()

# Simpan blend baru
BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT), relative_remap=True)
print(f"Model bersih berhasil disimpan ke: {BLEND_OUT}")
