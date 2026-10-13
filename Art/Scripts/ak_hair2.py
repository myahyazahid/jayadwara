"""Aksa — rambut gaya 2 (stylized game, rapi): volume pendek bertekstur + gumpalan tebal yang menempel mengikuti aliran.

Developer (12 Okt 2026): rambut tidak harus sama dengan konsep, yang penting bagus dan cocok. Gaya: textured crop —
atas tebal menyapu ke depan dan sedikit ke kiri karakter (+X), poni pendek jatuh di dahi atas, sisi dan tengkuk tipis rapi.
Struktur:
  1. Cangkang (shell): kulit kepala di atas garis rambut digeser sepanjang normal dengan ketebalan bervariasi (thick()),
     dihaluskan, tepinya ditutup dinding ke kulit kepala (tidak tampak setipis kertas).
  2. Gumpalan (lock): pita berpenampang lensa yang berjalan DI ATAS cangkang mengikuti medan aliran (flow()), meruncing di ujung.
     Gumpalan poni keluar dari tepi depan dan berlanjut di atas dahi.
Seed tetap -> deterministik. Ubah parameter lalu jalankan ulang aksa_22_mpfb_head.py.
"""
import math
import random

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SEED = 21
WHORL = Vector((0.0, 0.035, 1.772))            # pusaran di puncak belakang
CENTER_Y = -0.02
N_LOCKS = {"top": 70, "front": 22, "side": 22, "back": 34}      # side per sisi
HI_FRAC = 0.06


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def hairline_z(t):
    """Garis rambut (z) per sudut t (0 = depan)."""
    a = abs(math.degrees(t))
    if a < 40:
        return 1.722 + 0.003 * (a / 40.0)
    if a < 80:
        return 1.725 - (a - 40) / 40.0 * 0.050                 # pelipis turun ke atas telinga
    if a < 115:
        return 1.675 - (a - 80) / 35.0 * 0.020
    return 1.655 - (min(a, 180) - 115) / 65.0 * 0.035          # tengkuk


def thick(p):
    """Ketebalan cangkang: tebal di atas & depan (volume), tipis di sisi & tengkuk."""
    top = smooth(1.700, 1.770, p.z)
    front = smooth(0.0, -0.075, p.y)
    side = smooth(0.035, 0.060, abs(p.x)) * (1 - top)
    t = 0.0055 + 0.0250 * top + 0.0080 * front * smooth(1.715, 1.76, p.z)
    return t * (1 - 0.35 * side)


def _ang(co):
    return math.atan2(co.x, -(co.y - CENTER_Y))


def build_shell(bm_out, mesh):
    """Cangkang + dinding tepi. Mengembalikan BVH cangkang."""
    def ok(co):
        if co.z < hairline_z(_ang(co)):
            return False
        if abs(co.x) > 0.0600 and co.z < 1.705:          # telinga
            return False
        return True

    keep = [p for p in mesh.polygons if all(ok(mesh.vertices[i].co) for i in p.vertices)]
    vmap, base = {}, {}
    for p in keep:
        for i in p.vertices:
            if i not in vmap:
                v = mesh.vertices[i]
                vmap[i] = bm_out.verts.new(v.co + v.normal * thick(v.co))
                base[vmap[i]] = (v.co.copy(), v.normal.copy())
    for p in keep:
        try:
            bm_out.faces.new([vmap[i] for i in p.vertices])
        except ValueError:
            pass
    bm_out.verts.ensure_lookup_table()
    # haluskan permukaan luar (ketebalan bervariasi + tonjolan tengkorak)
    for _ in range(3):
        new = {}
        for v in bm_out.verts:
            nb = [e.other_vert(v).co for e in v.link_edges]
            if nb and not v.is_boundary:
                new[v] = v.co.lerp(sum(nb, Vector()) / len(nb), 0.5)
        for v, co in new.items():
            v.co = co
    # tepi: haluskan lalu tutup dinding ke kulit kepala
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
    inner = {}
    for v in bnd:
        co, n = base[v]
        inner[v] = bm_out.verts.new(co + n * 0.0012)
    for e in bnd_edges:
        a, b = e.verts
        try:
            bm_out.faces.new((a, b, inner[b], inner[a]))
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm_out, faces=list(bm_out.faces))
    bmesh.ops.dissolve_limit(bm_out, angle_limit=math.radians(3.0), verts=list(bm_out.verts), edges=list(bm_out.edges))
    bmesh.ops.triangulate(bm_out, faces=list(bm_out.faces))
    return BVHTree.FromBMesh(bm_out)


def flow(p, n, rng_j):
    """Arah aliran di permukaan."""
    d = p - WHORL
    d -= n * d.dot(n)
    d = d.normalized() if d.length > 1e-6 else Vector((0, -1, 0))
    if p.y < 0.01 and p.z > 1.725:                     # atas-depan: menyapu ke depan dan ke +X
        d += Vector((0.35, -0.55, 0.0))
    if p.z < 1.735 and p.y > -0.03:                    # sisi & belakang: turun, sedikit ke belakang
        d += Vector((0.0, 0.25, -0.9))
    d += rng_j
    d -= n * d.dot(n)
    return d.normalized()


def _lock(bm, path, normals, widths, heights):
    """Pita berpenampang lensa: kiri, atas, kanan, bawah; ujung meruncing ke satu titik."""
    rows = []
    m = len(path)
    for k in range(m):
        p, n = path[k], normals[k]
        T = (path[min(k + 1, m - 1)] - path[max(k - 1, 0)]).normalized()
        b = T.cross(n).normalized()
        w, h = widths[k], heights[k]
        if w < 1e-5:
            rows.append([bm.verts.new(p)])
            continue
        rows.append([bm.verts.new(p - b * w / 2), bm.verts.new(p + n * h), bm.verts.new(p + b * w / 2),
                     bm.verts.new(p - n * h * 0.25)])
    for a, c in zip(rows[:-1], rows[1:]):
        if len(c) == 1:
            for k in range(4):
                bm.faces.new((a[k], a[(k + 1) % 4], c[0]))
        else:
            for k in range(4):
                bm.faces.new((a[k], a[(k + 1) % 4], c[(k + 1) % 4], c[k]))
    bm.faces.new(rows[0][::-1])


def _sample_on(bm_shell, rng, n, pred):
    faces = [f for f in bm_shell.faces if pred(f.calc_center_median(), f.normal)]
    if not faces:
        return []
    areas = [f.calc_area() for f in faces]
    tot = sum(areas)
    out = []
    for _ in range(n):
        r = rng.uniform(0, tot)
        acc = 0.0
        for f, a in zip(faces, areas):
            acc += a
            if acc >= r:
                vs = [v.co for v in f.verts]
                u, w_ = rng.random(), rng.random()
                if u + w_ > 1:
                    u, w_ = 1 - u, 1 - w_
                out.append((vs[0] + (vs[1] - vs[0]) * u + (vs[2] - vs[0]) * w_, f.normal.copy()))
                break
    return out


def make_locks(bm_out, bm_hi, bm_shell, bvh_shell, bvh_head):
    rng = random.Random(SEED)
    made = 0
    jobs = []
    jobs += [("top", p, n) for p, n in _sample_on(bm_shell, rng, N_LOCKS["top"], lambda c, n: c.z > 1.735 and n.z > 0.2)]
    jobs += [("back", p, n) for p, n in _sample_on(bm_shell, rng, N_LOCKS["back"], lambda c, n: c.y > 0.02 and 1.66 < c.z < 1.75)]
    for s in (1, -1):
        jobs += [("side", p, n) for p, n in _sample_on(bm_shell, rng, N_LOCKS["side"],
                                                       lambda c, n, s=s: c.x * s > 0.03 and -0.04 < c.y < 0.03 and 1.68 < c.z < 1.745)]
    for i in range(N_LOCKS["front"]):                      # poni: akar di tepi depan atas
        x = -0.05 + 0.10 * (i + rng.uniform(-0.4, 0.4)) / (N_LOCKS["front"] - 1)
        hit = bvh_shell.ray_cast(Vector((x, -0.3, rng.uniform(1.738, 1.752))), Vector((0, 1, 0)))
        if hit[0] is not None:
            jobs.append(("front", hit[0], hit[1]))
    for region, p0, n0 in jobs:
        if region == "top":
            L, w0, h0, lift = rng.uniform(0.055, 0.085), rng.uniform(0.022, 0.032), rng.uniform(0.0050, 0.0075), 0.0018
        elif region == "front":
            L, w0, h0, lift = rng.uniform(0.028, 0.044), rng.uniform(0.016, 0.024), rng.uniform(0.0040, 0.0060), 0.0022
        elif region == "side":
            L, w0, h0, lift = rng.uniform(0.032, 0.050), rng.uniform(0.015, 0.022), rng.uniform(0.0025, 0.0040), 0.0010
        else:
            L, w0, h0, lift = rng.uniform(0.040, 0.065), rng.uniform(0.018, 0.028), rng.uniform(0.0035, 0.0055), 0.0012
        jit = Vector((rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), rng.uniform(-0.15, 0.15)))
        segs = 5
        path, normals = [], []
        p, n = Vector(p0), Vector(n0)
        for k in range(segs + 1):
            path.append(p + n * (lift + (0.0030 if region == 'top' else 0.0015) * k / segs))
            normals.append(n)
            d = flow(p, n, jit)
            if region == "front":
                d = (d + Vector((0.55, -0.35, -0.6))).normalized()
            cand = p + d * (L / segs)
            loc, nrm, _i, _d = bvh_shell.find_nearest(cand)
            if loc is None or cand.z < hairline_z(_ang(cand)) + 0.002 or (loc - cand).length > 0.006:
                hl, hn, _i2, _d2 = bvh_head.find_nearest(cand)       # keluar dari cangkang: lanjut di atas kulit
                if hl is None:
                    break
                loc, nrm = hl + hn * 0.0045, hn
            p, n = loc, nrm
            if region == "front" and p.z < 1.700:              # ujung poni berhenti di atas alis
                path.append(p + n * lift)
                normals.append(n)
                break
        m = len(path)
        if m < 3:
            continue
        prof = [0.75, 1.0, 0.95, 0.80, 0.50, 0.0]                   # profil lebar, diregangkan ke m titik
        f = []
        for k in range(m):
            x = k / (m - 1) * (len(prof) - 1)
            i0 = min(int(x), len(prof) - 2)
            f.append(prof[i0] + (prof[i0 + 1] - prof[i0]) * (x - i0))
        target = bm_hi if (bm_hi is not None and rng.random() < HI_FRAC) else bm_out
        _lock(target, path, normals, [w0 * x for x in f], [h0 * max(x, 0.0) for x in f])
        made += 1
    return made
