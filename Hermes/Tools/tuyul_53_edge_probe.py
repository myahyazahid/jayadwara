"""K5.4 - Probe panjang tepi TY_Source (LOD0) & LOD1-3: membuktikan filter derau
"tepi < 2 mm" di Art/Scripts/audit_karakter.py bersifat ABSOLUT, sehingga
regangan p99 tidak bisa dibandingkan antar-skala (model 27 m / 45 m).

  blender --background Hermes/Art/tuyul/Blender/tuyul_v08_lod.blend --python Hermes/Tools/tuyul_53_edge_probe.py
"""
import bpy

for name in ("TY_Source", "TY_Source_LOD1", "TY_Source_LOD2", "TY_Source_LOD3"):
    ob = bpy.data.objects[name]
    me = ob.data
    L = []
    for e in me.edges:
        a, b = me.vertices[e.vertices[0]].co, me.vertices[e.vertices[1]].co
        L.append((a - b).length)
    L.sort()
    n = len(L)
    lt2 = sum(1 for x in L if x < 0.002)
    print(f"{name:16s} {n:6d} tepi | min {L[0] * 1000:6.2f} mm | p25 {L[n // 4] * 1000:6.2f} | "
          f"median {L[n // 2] * 1000:6.2f} | p99 {L[int(0.99 * n)] * 1000:7.2f} | "
          f"tepi<2mm {lt2:5d} ({100.0 * lt2 / n:4.1f}%)")
