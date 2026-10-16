"""K5.9 - Haluskan (Laplacian) bobot tepi bahu LOD1-3 supaya regangan LOD tidak jauh
lebih buruk dari LOD0. Pola smoothing bobot Aksa2 (v31-v32).

Latar (diagnosa K5): tepi rest ~4,5 mm di bahu-belakang (z~0,71) menghubungkan satu
vertex 100% `clavicle_l` dengan satu vertex 100% `upperarm_l`; saat lengan diangkat
tepi itu teregang 34 cm (regangan p99 LOD1 352% vs LOD0 73%). Decimate COLLAPSE
menghapus vertex transisi sehingga dua ujung ekstrem jadi bertetangga langsung.
Smoothing menularkan bobot ke tetangga tepi (hanya vertex di zona bahu yang menyentuh
tepi |dw|>0,5) sampai gradiennya mulus. LOD0 (TY_Source) TIDAK diubah.

  blender --background Hermes/Art/tuyul/Blender/tuyul_v08_lod.blend \
      --python Hermes/Tools/tuyul_58_smooth_lod.py -- <iterasi> <faktor> <ring>

Keluaran: Hermes/Art/tuyul/Blender/tuyul_v09_smooth.blend
"""
import sys
from pathlib import Path

import bpy

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
ART = ROOT / "Hermes" / "Art" / "tuyul"
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ITER = int(argv[0]) if len(argv) > 0 else 20
FACTOR = float(argv[1]) if len(argv) > 1 else 0.5
RINGS = int(argv[2]) if len(argv) > 2 else 10
LODS = ["TY_Source_LOD1", "TY_Source_LOD2", "TY_Source_LOD3"]
Z_LO, Z_HI, DW_SEAM = 0.45, 0.95, 0.5   # zona bahu/dada atas + lengan atas


def weights_of(ob):
    gname = {vg.index: vg.name for vg in ob.vertex_groups}
    return [{gname[g.group]: g.weight for g in v.groups if g.weight > 1e-4}
            for v in ob.data.vertices]


def smooth(ob):
    me = ob.data
    W = weights_of(ob)
    adj = [set() for _ in me.vertices]
    for e in me.edges:
        a, b = e.vertices
        adj[a].add(b)
        adj[b].add(a)
    seam = set()
    for e in me.edges:
        a, b = e.vertices
        wa, wb = W[a], W[b]
        d = sum(abs(wa.get(k, 0.0) - wb.get(k, 0.0)) for k in set(wa) | set(wb))
        if d > DW_SEAM:
            seam.add(a)
            seam.add(b)
    mask = set(seam)
    frontier = set(seam)
    for _ in range(RINGS):
        nxt = set()
        for i in frontier:
            for j in adj[i]:
                if j not in mask:
                    nxt.add(j)
        mask |= nxt
        frontier = nxt
    mask = {i for i in mask if Z_LO < me.vertices[i].co.z < Z_HI}
    for _ in range(ITER):
        NW = []
        for i in range(len(W)):
            if i not in mask or not adj[i]:
                NW.append(W[i])
                continue
            acc = {}
            for k, v in W[i].items():
                acc[k] = acc.get(k, 0.0) + (1.0 - FACTOR) * v
            n = len(adj[i])
            for j in adj[i]:
                for k, v in W[j].items():
                    acc[k] = acc.get(k, 0.0) + FACTOR * v / n
            NW.append(acc)
        W = NW
    names = sorted({k for w in W for k in w})
    for vg in list(ob.vertex_groups):
        ob.vertex_groups.remove(vg)
    vgs = {nm: ob.vertex_groups.new(name=nm) for nm in names}
    for i, w in enumerate(W):
        top = sorted(w.items(), key=lambda kv: -kv[1])[:4]
        tot = sum(v for _, v in top) or 1.0
        for k, v in top:
            vgs[k].add([i], v / tot, "REPLACE")
    return len(mask)


for nm in LODS:
    ob = bpy.data.objects.get(nm)
    if not ob:
        print("TIDAK ADA", nm)
        continue
    n = smooth(ob)
    print(f"{nm}: smoothing {ITER}x faktor {FACTOR}, band {RINGS} ring -> {n} vertex")

bpy.ops.wm.save_as_mainfile(filepath=str(ART / "Blender" / "tuyul_v09_smooth.blend"))
print("simpan tuyul_v09_smooth.blend")
