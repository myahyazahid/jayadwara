"""K2.2 - Pembersihan geometri Tuyul.

Jalankan:
  blender --background <in.blend> --python Art/Scripts/tuyul_21_clean_geom.py -- --out <out.blend>

Kerja:
  1. Buang serpihan: vertex/tepi lepas, muka rusak (luas ~0).
  2. Perbaiki cacat di ketiak kiri (1 tepi terbuka + 2 non-manifold):
     hapus muka di radius kecil sekitar cacat, tutup lubang, hitung ulang normal.
  3. Jangan memotong badan jadi potongan (tidak ada pemisahan badan).
Mesh tidak dipindah/diubah bentuk di luar zona cacat.
"""
import bpy, bmesh, sys
from mathutils import Vector

OBJ = "TY_Source"
DEFECT = Vector((0.1519, 0.0970, 0.7550))  # pusat cacat ketiak kiri (dari audit)
R_DEL = 0.007                              # radius hapus muka (m)


def arg(name, default=None):
    a = sys.argv
    if "--" in a:
        a = a[a.index("--") + 1:]
        if name in a:
            return a[a.index(name) + 1]
    return default


def counts(bm):
    oe = sum(1 for e in bm.edges if len(e.link_faces) == 1)
    nm = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    lv = sum(1 for v in bm.verts if len(v.link_edges) == 0)
    le = sum(1 for e in bm.edges if len(e.link_faces) == 0)
    return oe, nm, lv, le


def main():
    out = arg("--out")
    ob = bpy.data.objects[OBJ]
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    vol0 = bm.calc_volume(signed=True)
    c0 = counts(bm)
    print(f"SEBELUM  tepi_terbuka={c0[0]} non_manifold={c0[1]} v_lepas={c0[2]} e_lepas={c0[3]} vol={vol0:.6f}")

    # 1. serpihan
    le = [e for e in bm.edges if len(e.link_faces) == 0]
    if le:
        bmesh.ops.delete(bm, geom=le, context='EDGES')
    lv = [v for v in bm.verts if len(v.link_edges) == 0]
    if lv:
        bmesh.ops.delete(bm, geom=lv, context='VERTS')
    bad = [f for f in bm.faces if f.calc_area() < 1e-9]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context='FACES_ONLY')
    print(f"serpihan dibuang: tepi_lepas={len(le)} v_lepas={len(lv)} muka_rusak={len(bad)}")

    # 2. perbaiki cacat ketiak kiri
    bm.verts.ensure_lookup_table()
    fdel = [f for f in bm.faces if any((v.co - DEFECT).length < R_DEL for v in f.verts)]
    print(f"muka dihapus di zona cacat (r={R_DEL*1000:.0f} mm): {len(fdel)}")
    if fdel:
        bmesh.ops.delete(bm, geom=fdel, context='FACES')
    # buang vertex yang jadi lepas
    lv2 = [v for v in bm.verts if len(v.link_edges) == 0]
    if lv2:
        bmesh.ops.delete(bm, geom=lv2, context='VERTS')
    # tutup lubang
    be = [e for e in bm.edges if len(e.link_faces) == 1]
    if be:
        res = bmesh.ops.holes_fill(bm, edges=be, sides=0)
        print(f"tutup lubang: tepi batas={len(be)} muka baru={len(res.get('faces', []))}")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.verts.ensure_lookup_table()
    vol1 = bm.calc_volume(signed=True)
    c1 = counts(bm)
    print(f"SESUDAH  tepi_terbuka={c1[0]} non_manifold={c1[1]} v_lepas={c1[2]} e_lepas={c1[3]} vol={vol1:.6f}")
    print(f"vertex/edge/face: {len(bm.verts)}/{len(bm.edges)}/{len(bm.faces)}  tris={sum(len(f.verts)-2 for f in bm.faces)}")

    bm.to_mesh(ob.data)
    ob.data.update()
    bm.free()

    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"disimpan: {out}")


main()
