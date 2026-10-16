"""K5.5 - Diagnosa bobot LOD: bandingkan vektor bobot tiap vertex LOD1 dengan vertex
LOD0 terdekat (KD-tree). Vertex yang bobotnya jauh berbeda di posisi hampir sama =
bukti decimate COLLAPSE menyatukan vertex antar-bagian (lengan<->badan) di mesh blob.

  blender --background Hermes/Art/tuyul/Blender/tuyul_v08_lod.blend --python Hermes/Tools/tuyul_54_weight_diag.py
"""
import bpy
from mathutils import kdtree

l0 = bpy.data.objects["TY_Source"]
l1 = bpy.data.objects["TY_Source_LOD1"]
g0 = {vg.index: vg.name for vg in l0.vertex_groups}
g1 = {vg.index: vg.name for vg in l1.vertex_groups}


def wmap(ob, gm):
    out = []
    for v in ob.data.vertices:
        out.append({gm[g.group]: g.weight for g in v.groups if g.weight > 1e-4})
    return out


W0, W1 = wmap(l0, g0), wmap(l1, g1)
kd = kdtree.KDTree(len(l0.data.vertices))
for i, v in enumerate(l0.data.vertices):
    kd.insert(v.co, i)
kd.balance()

rows = []
for i, v in enumerate(l1.data.vertices):
    _co, idx, dist = kd.find(v.co)
    a, b = W0[idx], W1[i]
    d = sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in set(a) | set(b))
    rows.append((d, i, dist, v.co.copy(), a, b))
rows.sort(key=lambda t: -t[0])

n = len(rows)
for th in (0.2, 0.5, 0.9):
    k = sum(1 for r in rows if r[0] > th)
    print(f"  vertex LOD1 dengan |delta bobot| > {th:.1f} : {k} ({100.0 * k / n:.2f}%)")
print("  contoh terburuk (posisi, jarak ke vertex LOD0 terdekat, bobot LOD0 -> bobot LOD1):")
for d, i, dist, co, a, b in rows[:8]:
    fa = sorted(a.items(), key=lambda kv: -kv[1])[:3]
    fb = sorted(b.items(), key=lambda kv: -kv[1])[:3]
    print(f"    v{i:5d} ({co.x:+.3f},{co.y:+.3f},{co.z:+.3f}) jarak {dist * 1000:5.1f} mm delta {d:.2f} | "
          f"LOD0 {[(k, round(w, 2)) for k, w in fa]} -> LOD1 {[(k, round(w, 2)) for k, w in fb]}")
