"""K5.6 - dua uji angka (tanpa pose, tanpa render):
(a) apakah zona lindung benar-benar dilindungi -> hitung tris zona kepala/tangan per LOD;
(b) ketidakkontinuan bobot antar-tepi |dw|_1 per LOD -> sumber peregangan di bahu.

  blender --background Hermes/Art/tuyul/Blender/tuyul_v08_lod.blend --python Hermes/Tools/tuyul_55_seam_probe.py
"""
import bpy

Z_KEPALA = 0.78
X_TANGAN, Z_TANGAN = 0.20, 0.32


def tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def tris_zona(me, f):
    return sum(len(p.vertices) - 2 for p in me.polygons if all(f(me.vertices[i].co) for i in p.vertices))


def wdiff(ob):
    gname = {vg.index: vg.name for vg in ob.vertex_groups}
    W = [{gname[g.group]: g.weight for g in v.groups if g.weight > 1e-4} for v in ob.data.vertices]
    ds = []
    for e in ob.data.edges:
        a, b = W[e.vertices[0]], W[e.vertices[1]]
        ds.append(sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in set(a) | set(b)))
    ds.sort()
    return ds


kepala = lambda c: c.z > Z_KEPALA
tangan = lambda c: abs(c.x) > X_TANGAN and c.z < Z_TANGAN
for nm in ("TY_Source", "TY_Source_LOD1", "TY_Source_LOD2", "TY_Source_LOD3"):
    ob = bpy.data.objects.get(nm)
    if not ob:
        print(nm, "TIDAK ADA")
        continue
    me = ob.data
    t = tris(me)
    tk, tt = tris_zona(me, kepala), tris_zona(me, tangan)
    ds = wdiff(ob)
    n = len(ds)
    over = sum(1 for d in ds if d > 0.5)
    print(f"{nm}: tris {t} | tris kepala {tk} ({100.0 * tk / t:.1f}%) | tris tangan {tt} | "
          f"|dw| tepi median {ds[n // 2]:.3f} p99 {ds[int(0.99 * n)]:.3f} maks {ds[-1]:.3f} | "
          f"tepi |dw|>0.5: {over} ({100.0 * over / n:.2f}%)")
