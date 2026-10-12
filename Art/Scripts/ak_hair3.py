"""Aksa — rambut gaya 3: disisir ke belakang dengan belahan samping + jambul depan (permintaan developer, 12 Okt 2026,
referensi gambar karakter stylized dengan rambut swept-back).

Struktur sama dengan ak_hair2 (cangkang + gumpalan menempel mengikuti aliran), tapi:
  - cangkang: jambul depan tebal yang naik lalu melengkung ke belakang; ketebalan menipis halus ke garis rambut (tanpa dinding tegak);
    alur belahan dangkal di x = PART_X; sisi tipis disisir ke belakang;
  - gumpalan: helai panjang halus berpenampang lensa yang berangkat dari garis rambut depan/sisi dan mengalir ke belakang,
    menyebar menjauhi belahan; belakang turun ke tengkuk.
Warna mengikuti Aksa (hitam + highlight coklat halus). Seed tetap -> deterministik.
"""
import math
import random

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import ak_hair2 as H2

SEED = 31
CENTER_Y = -0.02
PART_X = -0.024                   # belahan di sisi kanan karakter (seperti referensi: kiri gambar)
HI_FRAC = 0.06


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def hairline_z(t):
    a = abs(math.degrees(t))
    if a < 38:
        return 1.714 + 0.004 * (a / 38.0)                       # garis rambut depan
    if a < 80:
        return 1.718 - (a - 38) / 42.0 * 0.042
    if a < 115:
        return 1.676 - (a - 80) / 35.0 * 0.020
    return 1.656 - (min(a, 180) - 115) / 65.0 * 0.034


def _ang(co):
    return math.atan2(co.x, -(co.y - CENTER_Y))


def thick(p):
    t_edge = smooth(0.0, 0.022, p.z - hairline_z(_ang(p)))                       # menipis ke garis rambut
    top = smooth(1.700, 1.770, p.z)
    front = smooth(0.005, -0.070, p.y) * smooth(1.712, 1.745, p.z)             # jambul depan
    side = smooth(0.035, 0.062, abs(p.x)) * (1 - top)
    part = math.exp(-((p.x - PART_X) / 0.006) ** 2) * smooth(0.02, -0.05, p.y) * top
    temple = smooth(0.030, 0.055, abs(p.x)) * smooth(1.69, 1.73, p.z)
    t = 0.007 + 0.027 * top + 0.016 * front + 0.010 * temple - 0.006 * part
    t *= (1 - 0.30 * side)
    return max(0.0015, t * (0.25 + 0.75 * t_edge))


def build_shell(bm_out, mesh):
    def ok(co):
        if co.z < hairline_z(_ang(co)):
            return False
        if abs(co.x) > 0.0600 and co.z < 1.705:
            return False
        return True

    keep = [p for p in mesh.polygons if all(ok(mesh.vertices[i].co) for i in p.vertices)]
    vmap, base = {}, {}
    for p in keep:
        for i in p.vertices:
            if i not in vmap:
                v = mesh.vertices[i]
                off = thick(v.co)
                lift = Vector((0.15, -0.45, 0.35)) * (0.007 * smooth(0.0, -0.07, v.co.y) * smooth(1.72, 1.75, v.co.z))  # jambul condong ke depan-atas
                vmap[i] = bm_out.verts.new(v.co + v.normal * off + lift)
                base[vmap[i]] = (v.co.copy(), v.normal.copy())
    for p in keep:
        try:
            bm_out.faces.new([vmap[i] for i in p.vertices])
        except ValueError:
            pass
    bm_out.verts.ensure_lookup_table()
    for _ in range(4):
        new = {}
        for v in bm_out.verts:
            nb = [e.other_vert(v).co for e in v.link_edges]
            if nb and not v.is_boundary:
                new[v] = v.co.lerp(sum(nb, Vector()) / len(nb), 0.5)
        for v, co in new.items():
            v.co = co
    bnd_edges = [e for e in bm_out.edges if e.is_boundary]
    bnd = list({v for e in bnd_edges for v in e.verts})
    for _ in range(5):
        new = {}
        for v in bnd:
            nb = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if len(nb) == 2:
                new[v] = v.co.lerp((nb[0].co + nb[1].co) / 2, 0.5)
        for v, co in new.items():
            v.co = co
    # tempel tepi tepat di kurva garis rambut (mulus, tidak ikut grid mesh kepala)
    head_bvh = BVHTree.FromPolygons([tuple(v.co) for v in mesh.vertices], [tuple(p.vertices) for p in mesh.polygons])
    snapped = {}
    for v in bnd:
        co = v.co
        tgt = Vector((co.x, co.y, hairline_z(_ang(co))))
        loc, nrm, _i, _d = head_bvh.find_nearest(tgt)
        if loc is not None:
            snapped[v] = (loc, nrm)
    for _ in range(4):                                             # haluskan titik tempel sepanjang tepi
        new = {}
        for v in bnd:
            nb = [e.other_vert(v) for e in v.link_edges if e.is_boundary and e.other_vert(v) in snapped]
            if v in snapped and len(nb) == 2:
                loc = snapped[v][0].lerp((snapped[nb[0]][0] + snapped[nb[1]][0]) / 2, 0.5)
                new[v] = (loc, snapped[v][1])
        snapped.update(new)
    for v, (loc, nrm) in snapped.items():
        v.co = loc + nrm * 0.0018
        base[v] = (loc, nrm)
    inner = {v: bm_out.verts.new(base[v][0] + base[v][1] * 0.0006) for v in bnd}
    for e in bnd_edges:
        a, b = e.verts
        try:
            bm_out.faces.new((a, b, inner[b], inner[a]))
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm_out, faces=list(bm_out.faces))
    bmesh.ops.dissolve_limit(bm_out, angle_limit=math.radians(2.5), verts=list(bm_out.verts), edges=list(bm_out.edges))
    bmesh.ops.triangulate(bm_out, faces=list(bm_out.faces))
    return BVHTree.FromBMesh(bm_out)


def flow(p, n, jit):
    """Ke belakang (+Y), menyebar menjauhi belahan; sisi ke belakang; belakang turun."""
    if p.y < 0.03 and p.z > 1.70:
        side = 1.0 if p.x >= PART_X else -1.0
        spread = side * (0.25 + 1.2 * min(abs(p.x - PART_X), 0.06))
        d = Vector((spread, 1.0, 0.25 if p.y < -0.03 else -0.05))
    elif p.y < 0.03:
        d = Vector((0.0, 1.0, 0.05))                              # sisi: disisir lurus ke belakang
    else:
        d = Vector((0.15 * (1 if p.x > 0 else -1), 0.45, -1.0))   # belakang: turun
    d += jit
    d -= n * d.dot(n)
    return d.normalized()


HEAD_C = Vector((0.0, -0.005, 1.69))


def _snap(bvh_shell, cand, n_prev):
    loc, nrm, _i, _d = bvh_shell.find_nearest(cand)
    if loc is None:
        return None, None
    radial = (loc - HEAD_C).normalized()
    n = (nrm + radial * 1.5 + n_prev * 1.0).normalized()          # normal dihaluskan: tidak ikut faset cangkang
    return loc, n


def _strand(bm, bvh_shell, p0, n0, L, w0, h0, lift, segs=12, prof=None):
    path, normals = [], []
    p, n = Vector(p0), Vector(n0)
    for _k in range(segs + 1):
        path.append(p + n * lift)
        normals.append(n)
        d = flow(p, n, Vector())
        q, nn = _snap(bvh_shell, p + d * (L / segs), n)
        if q is None:
            break
        p, n = q, nn
    m = len(path)
    if m < 3:
        return False
    prof = prof or [0.55, 0.85, 1.0, 1.08, 1.1, 1.05, 0.95, 0.8, 0.55, 0.0]
    f = []
    for k in range(m):
        x = k / (m - 1) * (len(prof) - 1)
        i0 = min(int(x), len(prof) - 2)
        f.append(prof[i0] + (prof[i0 + 1] - prof[i0]) * (x - i0))
    H2._lock(bm, path, normals, [w0 * x for x in f], [h0 * x for x in f])
    return True


def make_locks(bm_out, bm_hi, bm_shell, bvh_shell, bvh_head):
    """Helai teratur dan sejajar (tanpa acak arah): 2 baris atas berselang, sisi, belakang."""
    rng = random.Random(SEED)
    made = 0

    def tgt():
        return bm_hi if (bm_hi is not None and rng.random() < HI_FRAC) else bm_out

    for row, (zr, n, x0) in enumerate([(1.727, 13, 0.0), (1.750, 12, 0.5)]):
        for i in range(n):
            x = -0.056 + 0.112 * (i + x0) / (n - 1 + x0)
            hit = bvh_shell.ray_cast(Vector((x, -0.3, zr)), Vector((0, 1, 0)))
            if hit[0] is None:
                continue
            centre = 1.0 - min(abs(x - 0.008) / 0.06, 1.0)
            L = 0.11 + 0.06 * centre
            made += _strand(tgt(), bvh_shell, hit[0], hit[1], L, 0.0125 + 0.0025 * centre, 0.0042, 0.0016 + 0.0012 * row)
    for s in (1, -1):
        for i in range(7):
            z = 1.693 + 0.040 * i / 6
            hit = bvh_shell.ray_cast(Vector((s * 0.2, -0.040 + 0.006 * i, z)), Vector((-s, 0, 0)), 0.3)
            if hit[0] is None:
                continue
            made += _strand(tgt(), bvh_shell, hit[0], hit[1], 0.075, 0.0115, 0.0028, 0.0012, segs=9)
    for i in range(14):
        az = math.radians(25 + 130 * i / 13)                       # sudut di belakang (+Y)
        d = Vector((math.cos(az), math.sin(az), 0.55)).normalized()
        hit = bvh_shell.ray_cast(HEAD_C, d, 0.3)
        if hit[0] is None:
            continue
        made += _strand(tgt(), bvh_shell, hit[0], hit[1], 0.085, 0.0150, 0.0034, 0.0014, segs=10)
    return made
