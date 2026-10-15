"""Tuyul K0 — laporan kondisi mesh (angka): tris, tepi terbuka/non-manifold, pulau, simetri, kepala.

  blender --background Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend \
      --python Hermes/Tools/tuyul_03_analyze.py
Tidak mengubah apa pun; hanya mencetak angka untuk laporan K0.
"""
import bpy
import bmesh
from mathutils import Vector

ob = bpy.data.objects["TY_Source"]
me = ob.data

tris = sum(len(p.vertices) - 2 for p in me.polygons)
print(f"objek        : {ob.name} (mesh)")
print(f"vertex/tris  : {len(me.vertices)} / {tris}")
print(f"material     : {[m.name for m in me.materials]}")
print(f"uv layers    : {[u.name for u in me.uv_layers]}")

bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
boundary = [e for e in bm.edges if len(e.link_faces) == 1]
nonmani = [e for e in bm.edges if len(e.link_faces) > 2]
loose_v = [v for v in bm.verts if not v.link_edges]
print(f"tepi terbuka (1 face)   : {len(boundary)}")
print(f"tepi non-manifold (>2)  : {len(nonmani)}")
print(f"vertex lepas            : {len(loose_v)}")

# pulau mesh (connected components)
seen = set()
islands = []
for v in bm.verts:
    if v.index in seen:
        continue
    stack = [v]
    comp = []
    seen.add(v.index)
    while stack:
        cur = stack.pop()
        comp.append(cur)
        for e in cur.link_edges:
            o = e.other_vert(cur)
            if o.index not in seen:
                seen.add(o.index)
                stack.append(o)
    islands.append(comp)
islands.sort(key=len, reverse=True)
print(f"pulau mesh              : {len(islands)} (ukuran 5 terbesar: {[len(c) for c in islands[:5]]})")

co = [v.co for v in me.vertices]
mn = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
mx = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
print(f"bbox min {tuple(round(v, 4) for v in mn)} max {tuple(round(v, 4) for v in mx)}")
print(f"tinggi {mx.z - mn.z:.4f} m; lebar(x) {mx.x - mn.x:.4f}; dalam(y) {mx.y - mn.y:.4f}")

head = [c for c in co if c.z >= 0.8]
print(f"vertex kepala (z>=0.8)  : {len(head)}")

# simetri terhadap X=0: cari pasangan cermin terdekat
cell = {}
for c in co:
    key = (round(c.x, 2), round(c.y, 2), round(c.z, 2))
    cell.setdefault(key, []).append(c)
miss = 0
worst = 0.0
for c in co:
    m = Vector((-c.x, c.y, c.z))
    found = None
    for dx in (-0.01, 0.0, 0.01):
        for dy in (-0.01, 0.0, 0.01):
            for dz in (-0.01, 0.0, 0.01):
                key = (round(m.x + dx, 2), round(m.y + dy, 2), round(m.z + dz, 2))
                for q in cell.get(key, []):
                    d = (q - m).length
                    if found is None or d < found:
                        found = d
    if found is None or found > 0.02:
        miss += 1
    elif found > worst:
        worst = found
print(f"simetri X=0: {len(co) - miss}/{len(co)} vertex punya pasangan cermin <=2 cm; simpangan terbesar {worst*1000:.1f} mm")
bm.free()
