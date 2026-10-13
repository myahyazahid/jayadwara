"""Jayadwara2 R1/R2 — pulau UV atlas Tripo sebagai petunjuk segmentasi bagian (headless).
  blender --background Art/Blender/jayadwara2_v01_tripo.blend --python Art/Scripts/jayadwara2_04_uv_islands.py
Mencetak jumlah pulau & statistik (tris, bbox 3D) dan menyimpan Art/Export/_jd2/_uv_islands.npz (label per segitiga)."""
import numpy as np
import bmesh
import bpy

ob = bpy.data.objects["JD2_Source"]
bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table()
uv = bm.loops.layers.uv.active
tri = bmesh.ops.triangulate(bm, faces=bm.faces[:])
F = [f for f in bm.faces]
# faces yang berbagi tepi DAN berbagi UV di kedua ujung tepi = satu pulau
def key(l):  # UV dibulatkan
    return (round(l[uv].uv.x, 4), round(l[uv].uv.y, 4))
parent = list(range(len(F)))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
for e in bm.edges:
    if len(e.link_faces) != 2: continue
    f0, f1 = e.link_faces
    def uvs(f):
        d = {}
        for l in f.loops:
            if l.edge == e: d[l.vert.index] = key(l)
            # loop's vert at start of edge
        return d
    # kunci UV tiap vertex tepi pada tiap face
    def evuv(f):
        out = {}
        for l in f.loops:
            if l.vert in e.verts: out[l.vert.index] = key(l)
        return out
    a, b = evuv(f0), evuv(f1)
    if a == b:
        parent[find(f0.index)] = find(f1.index)
lab = np.array([find(f.index) for f in F])
uniq, inv = np.unique(lab, return_inverse=True)
cent = np.array([f.calc_center_median()[:] for f in F]); area = np.array([f.calc_area() for f in F])
print("pulau UV:", len(uniq), "dari", len(F), "segitiga")
order = np.argsort(-np.bincount(inv, weights=area))
for k in order[:40]:
    m = inv == k; c = cent[m]
    print(f"  #{k:3d} tris={m.sum():5d} luas={area[m].sum()*1e4:7.0f}cm2  bbox X[{c[:,0].min():+.2f},{c[:,0].max():+.2f}] Y[{c[:,1].min():+.2f},{c[:,1].max():+.2f}] Z[{c[:,2].min():.2f},{c[:,2].max():.2f}]")
small = (np.bincount(inv) < 20).sum()
print("pulau < 20 segitiga:", small)
np.savez(r"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2\_uv_islands.npz", label=inv, cent=cent)
