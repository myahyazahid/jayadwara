"""K2.1 - Audit topologi mesh Tuyul (angka 'sebelum').

Jalankan:
  blender --background <blend> --python Hermes/Tools/tuyul_20_audit_topology.py

Menghitung: tris, tepi terbuka (1 muka), non-manifold (>2 muka), vertex non-manifold,
vertex/tepi lepas, muka rusak (luas ~0), pulau mesh + ukurannya, dan
mengelompokkan tepi terbuka per zona (ketiak, selangkangan, leher, siku dalam, lain).
Juga volume mesh (m^3).
"""
import bpy, bmesh, sys
from mathutils import Vector

OBJ = "TY_Source"
GRID = 0.02  # m, jarak gabung cluster tepi terbuka


def get_bm(name=OBJ):
    ob = bpy.data.objects[name]
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return ob, bm


def zone(p):
    x, y, z = p
    ax = abs(x)
    if z >= 0.78 and ax < 0.12:
        return "leher"
    if 0.58 <= z <= 0.80 and 0.04 <= ax <= 0.22 and -0.12 <= y <= 0.12:
        return "ketiak"
    if 0.42 <= z <= 0.60 and 0.14 <= ax <= 0.30:
        return "siku_dalam"
    if 0.16 <= z <= 0.34 and ax < 0.16:
        return "selangkangan"
    return "lain"


def cluster(points, grid=GRID):
    """Gabung titik jadi cluster jarak < grid (union-find kasar via sort+proximity)."""
    pts = [Vector(p) for p in points]
    used = [False] * len(pts)
    clusters = []
    for i, p in enumerate(pts):
        if used[i]:
            continue
        stack = [i]
        used[i] = True
        members = []
        while stack:
            j = stack.pop()
            members.append(pts[j])
            for k in range(len(pts)):
                if not used[k] and (pts[k] - pts[j]).length < grid:
                    used[k] = True
                    stack.append(k)
        c = sum(members, Vector((0, 0, 0))) / len(members)
        clusters.append((c, len(members)))
    return clusters


def main():
    ob, bm = get_bm()
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    nv, ne, nf = len(bm.verts), len(bm.edges), len(bm.faces)
    tris = sum(len(f.verts) - 2 for f in bm.faces)

    open_e = [e for e in bm.edges if len(e.link_faces) == 1]
    nm_e = [e for e in bm.edges if len(e.link_faces) > 2]
    loose_e = [e for e in bm.edges if len(e.link_faces) == 0]
    loose_v = [v for v in bm.verts if len(v.link_edges) == 0]
    bad_f = [f for f in bm.faces if f.calc_area() < 1e-9]
    nm_v = [v for v in bm.verts if (not v.is_manifold) and (not v.is_boundary)]

    # pulau (komponen terhubung via vertex)
    seen = set()
    islands = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack = [v]
        seen.add(v.index)
        cnt = 0
        while stack:
            u = stack.pop()
            cnt += 1
            for e in u.link_edges:
                o = e.other_vert(u)
                if o.index not in seen:
                    seen.add(o.index)
                    stack.append(o)
        islands.append(cnt)
    islands.sort(reverse=True)

    vol = bm.calc_volume(signed=True)

    print("=== AUDIT TOPOLOGI ===")
    print(f"objek            : {ob.name}")
    print(f"vertex / edge / face : {nv} / {ne} / {nf}")
    print(f"tris             : {tris}")
    print(f"tepi terbuka (1) : {len(open_e)}")
    print(f"non-manifold (>2): {len(nm_e)}")
    print(f"vertex non-manifold: {len(nm_v)}")
    print(f"vertex lepas     : {len(loose_v)}")
    print(f"tepi lepas       : {len(loose_e)}")
    print(f"muka rusak (<1e-9 m2): {len(bad_f)}")
    print(f"pulau            : {len(islands)}  ukuran: {islands[:12]}{' ...' if len(islands) > 12 else ''}")
    print(f"volume           : {vol:.6f} m^3")

    # lokasi tepi terbuka per zona
    if open_e:
        pts = [tuple(e.verts[0].co) for e in open_e]
        cl = cluster(pts)
        print(f"--- tepi terbuka: {len(cl)} cluster ---")
        zcount = {}
        for c, n in sorted(cl, key=lambda t: -t[1]):
            z = zone(c)
            zcount[z] = zcount.get(z, 0) + n
            print(f"  zona={z:12s} n={n:4d} pusat=({c.x:+.4f},{c.y:+.4f},{c.z:+.4f})")
        print("  ringkas zona:", {k: v for k, v in sorted(zcount.items())})
    if nm_e:
        pts = [tuple((e.verts[0].co + e.verts[1].co) / 2) for e in nm_e]
        cl = cluster(pts)
        print(f"--- non-manifold: {len(cl)} cluster ---")
        for c, n in sorted(cl, key=lambda t: -t[1])[:12]:
            print(f"  zona={zone(c):12s} n={n:4d} pusat=({c.x:+.4f},{c.y:+.4f},{c.z:+.4f})")

    bm.free()


main()
