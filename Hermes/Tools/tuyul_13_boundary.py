"""Tuyul K1 — cari tepi terbuka / non-manifold dan lokasinya (untuk menjelaskan uji 'di dalam').
  blender --background Hermes/Art/tuyul/Blender/tuyul_v02_skeleton.blend \
      --python Hermes/Tools/tuyul_13_boundary.py
"""
from collections import defaultdict

import bpy

me = bpy.data.objects["TY_Source"].data
cnt = defaultdict(int)
for p in me.polygons:
    vs = list(p.vertices)
    for i in range(len(vs)):
        a, b = vs[i], vs[(i + 1) % len(vs)]
        cnt[(a, b) if a < b else (b, a)] += 1

bnd = [(a, b) for (a, b), c in cnt.items() if c == 1]
nonman = [(a, b) for (a, b), c in cnt.items() if c > 2]
print(f"tepian: total={len(cnt)} terbuka(1 muka)={len(bnd)} non-manifold(>2 muka)={len(nonman)}")
V = me.vertices
for tag, lst in (("TERBUKA", bnd), ("NON-MANIFOLD", nonman)):
    if not lst:
        continue
    print(f"== {tag} ==")
    for a, b in lst[:40]:
        pa, pb = V[a].co, V[b].co
        print(f"   ({pa.x:+.3f},{pa.y:+.3f},{pa.z:+.3f}) - ({pb.x:+.3f},{pb.y:+.3f},{pb.z:+.3f})")
