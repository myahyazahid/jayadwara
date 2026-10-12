"""Aksa Iterasi 2 — rambut: tudung kulit kepala + gumpalan (blade) pipih runcing berlapis, berdasarkan ak_head_front/side.png.

Dipakai oleh aksa_20_head.py. Seed tetap -> hasil deterministik; ubah SEED/COUNTS/parameter lalu jalankan ulang untuk iterasi.
Konsep: hitam pendek berantakan; poni jatuh sampai garis alis dan menyapu ke kiri karakter; volume di puncak dengan beberapa jambul;
sisi menipis di depan telinga lalu menggantung di belakang telinga; belakang berlapis sampai tengkuk. Highlight coklat samar.
"""
import math
import random

import bmesh
from mathutils import Vector

import jd_hero as HR

SEED = 11
CENTER = Vector((0.0, 0.004, 1.69))
UP = Vector((0, 0, 1))
COUNTS = {"fringe": 20, "fringe2": 18, "crownfront": 26, "top": 190, "tuft": 50, "spike": 8, "side": 40, "sideburn": 6, "back": 40}      # side & sideburn per sisi
CAP_OFFSET = 0.009


def hairline_z(t, x_abs):
    """Batas bawah kulit kepala berambut (z) menurut sudut cincin t (0 = depan)."""
    a = abs(math.degrees(t))
    if a < 42:
        return 1.711 + 0.004 * (a / 42.0)                                # garis rambut depan
    if a < 78:
        return 1.715 - (a - 42) / 36.0 * 0.048                           # turun ke pelipis / depan telinga
    if a < 115:
        return 1.667 - (a - 78) / 37.0 * 0.020                           # di sekitar telinga
    return 1.647 - (min(a, 180) - 115) / 65.0 * 0.030                    # belakang sampai tengkuk


def scalp_cap(bm, rings_pts, ts, offset=CAP_OFFSET):
    """Tudung = cincin kepala di atas garis rambut, digeser ke luar sepanjang normal; tepi dihaluskan, bidang datar disederhanakan."""
    n = len(ts)
    L = len(rings_pts)
    vmap = {}
    for i in range(L):
        for k in range(n):
            p, nrm = rings_pts[i][k]
            if p.z >= hairline_z(ts[k], abs(p.x)):
                vmap[(i, k)] = bm.verts.new(p + nrm * offset)
    for i in range(L - 1):
        for k in range(n):
            quad = [(i, k), (i, (k + 1) % n), (i + 1, (k + 1) % n), (i + 1, k)]
            if all(q in vmap for q in quad):
                bm.faces.new([vmap[q] for q in quad])
    top = [vmap[(L - 1, k)] for k in range(n) if (L - 1, k) in vmap]
    if len(top) > 2:
        bm.faces.new(top)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.verts.ensure_lookup_table()
    # haluskan tepi (hilangkan efek tangga grid)
    bnd = [v for v in bm.verts if v.is_boundary]
    for _ in range(8):
        new = {}
        for v in bnd:
            nb = [e.other_vert(v) for e in v.link_edges if e.other_vert(v).is_boundary]
            if len(nb) >= 2:
                avg = sum((u.co for u in nb), Vector()) / len(nb)
                new[v] = v.co.lerp(avg, 0.5)
        for v, co in new.items():
            v.co = co
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(4.0), verts=list(bm.verts), edges=list(bm.edges))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    return bm


def scalp_cap_mesh(bm_out, mesh, center_y=-0.02, offset=CAP_OFFSET):
    """Tudung dari mesh kepala sembarang (mis. MPFB): muka di atas garis rambut, digeser ke luar sepanjang normal vertex."""
    keep = {}
    for p in mesh.polygons:
        ok = True
        for vi in p.vertices:
            co = mesh.vertices[vi].co
            t = math.atan2(co.x, -(co.y - center_y))
            if co.z < hairline_z(t, abs(co.x)):
                ok = False
                break
        if ok:
            keep[p.index] = p
    vmap = {}
    for p in keep.values():
        vs = []
        for vi in p.vertices:
            if vi not in vmap:
                v = mesh.vertices[vi]
                vmap[vi] = bm_out.verts.new(v.co + v.normal * offset)
            vs.append(vmap[vi])
        try:
            bm_out.faces.new(vs)
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm_out, faces=list(bm_out.faces))
    bnd = [v for v in bm_out.verts if v.is_boundary]
    for _ in range(6):
        new = {}
        for v in bnd:
            nb = [e.other_vert(v) for e in v.link_edges if e.other_vert(v).is_boundary]
            if len(nb) >= 2:
                new[v] = v.co.lerp(sum((u.co for u in nb), Vector()) / len(nb), 0.5)
        for v, co in new.items():
            v.co = co
    bmesh.ops.triangulate(bm_out, faces=list(bm_out.faces))
    return bm_out


def _blade(bm, p, nrm, d0, length, r0, rng, grav=0.18, curl=None, up_vec=None, segs=3, flat=0.38):
    """Satu gumpalan: tabung pipih runcing dari titik akar p (sedikit di bawah permukaan) searah d0."""
    path = [p - nrm * 0.004]
    d = d0.normalized()
    curl = curl if curl is not None else Vector()
    for _k in range(segs):
        path.append(path[-1] + d * (length / segs))
        d = (d + Vector((0, 0, -1)) * grav + curl / segs).normalized()
    f = [0.8, 1.0, 0.82, 0.46, 0.0][: segs + 1] if segs == 4 else [0.9, 1.0, 0.7, 0.0]
    radii = [r0 * x for x in f]
    HR.tube(bm, path, radii, n=4, squash=(flat, 1.0), caps=(False, False), up=up_vec if up_vec is not None else nrm)


def _ray(bvh, d, origin=CENTER, dist=0.25):
    hit = bvh.ray_cast(origin, d, dist)
    return (hit[0], hit[1]) if hit[0] is not None else (None, None)


def make_clumps(bm_out, bvh, hi_bm=None):
    """Tambahkan gumpalan ke bm_out (sebagian kecil ke hi_bm sebagai highlight). Mengembalikan jumlah gumpalan."""
    rng = random.Random(SEED)
    made = 0

    def target():
        return hi_bm if (hi_bm is not None and rng.random() < 0.12) else bm_out

    # ---- poni: akar di sepanjang garis rambut depan, jatuh ke garis alis, menyapu ke +X
    N = COUNTS["fringe"]
    for i in range(N):
        x = -0.052 + 0.104 * (i + rng.uniform(-0.35, 0.35)) / (N - 1)
        z = 1.718 + rng.uniform(-0.003, 0.006)
        hit = bvh.ray_cast(Vector((x, -0.3, z)), Vector((0, 1, 0)))
        if hit[0] is None:
            continue
        p, nrm = hit[0] + hit[1] * CAP_OFFSET, hit[1]
        sweep = 0.30 + x * 7.0 + rng.uniform(-0.25, 0.25)
        d0 = Vector((max(-0.9, min(0.9, sweep)), -0.42 - rng.uniform(0, 0.25), -1.0))
        _blade(target(), p, nrm, d0, rng.uniform(0.026, 0.056), rng.uniform(0.0100, 0.0165), rng, grav=0.12,
               curl=Vector((0, -0.35, 0)), up_vec=Vector((0, -1, 0)))
        made += 1

    N2 = COUNTS["fringe2"]
    for i in range(N2):
        x = -0.050 + 0.100 * (i + rng.uniform(-0.35, 0.35)) / (N2 - 1)
        z = 1.738 + rng.uniform(-0.004, 0.004)
        hit = bvh.ray_cast(Vector((x, -0.3, z)), Vector((0, 1, 0)))
        if hit[0] is None:
            continue
        p, nrm = hit[0] + hit[1] * CAP_OFFSET, hit[1]
        d0 = Vector((max(-0.8, min(0.8, 0.25 + x * 6.0 + rng.uniform(-0.3, 0.3))), -0.55 - rng.uniform(0, 0.3), -0.8))
        _blade(target(), p, nrm, d0, rng.uniform(0.036, 0.060), rng.uniform(0.0105, 0.0165), rng, grav=0.1,
               curl=Vector((0, -0.4, 0)), up_vec=Vector((0, -1, 0)))
        made += 1

    # ---- puncak depan: menyapu ke depan-bawah menutup kulit kepala di atas poni
    for i in range(COUNTS["crownfront"]):
        x = rng.uniform(-0.045, 0.045)
        z = rng.uniform(1.748, 1.772)
        hit = bvh.ray_cast(Vector((x, -0.3, z)), Vector((0, 1, 0)))
        if hit[0] is None:
            continue
        p, nrm = hit[0] + hit[1] * CAP_OFFSET, hit[1]
        d0 = Vector((0.25 + x * 5.0 + rng.uniform(-0.3, 0.3), -1.0, rng.uniform(-0.1, 0.45)))
        _blade(target(), p, nrm, d0, rng.uniform(0.045, 0.068), rng.uniform(0.0115, 0.0170), rng, grav=0.22,
               curl=Vector((0, -0.2, -0.3)), up_vec=Vector((0, 0, 1)))
        made += 1

    # ---- volume puncak: bilah lebar berlapis, melengkung keluar-atas
    for i in range(COUNTS["top"]):
        for _try in range(30):
            ang = rng.uniform(0, 2 * math.pi)
            el = math.acos(rng.uniform(math.cos(1.05), 0.995))                            # seragam per luas permukaan
            d = Vector((math.cos(ang) * math.sin(el), math.sin(ang) * math.sin(el), math.cos(el)))
            p, nrm = _ray(bvh, d)
            if p is not None and p.z > 1.722 and not (p.y < -0.05 and p.z < 1.735):
                break
        else:
            continue
        out = Vector((p.x, p.y - CENTER.y, 0)).normalized()
        if p.y < -0.03:
            out = (out + Vector((0.2, -0.4, 0))).normalized()                         # bagian depan puncak ke depan-bawah
        d0 = out * rng.uniform(0.35, 0.75) + UP * rng.uniform(0.5, 0.95)
        _blade(target(), p + nrm * CAP_OFFSET, nrm, d0, rng.uniform(0.040, 0.062), rng.uniform(0.0095, 0.0145), rng, grav=0.26,
               curl=out * 0.25)
        made += 1
    # ---- tuft berlapis keliling kepala (melebarkan siluet setinggi telinga)
    for i in range(COUNTS["tuft"]):
        for _try in range(30):
            ang = rng.uniform(0, 2 * math.pi)
            el = rng.uniform(0.95, 1.35)
            d = Vector((math.cos(ang) * math.sin(el), math.sin(ang) * math.sin(el), math.cos(el)))
            p, nrm = _ray(bvh, d)
            if p is not None and 1.69 < p.z < 1.745 and not (p.y < -0.045):
                break
        else:
            continue
        out = Vector((p.x, p.y - CENTER.y, 0)).normalized()
        d0 = out * rng.uniform(0.5, 0.9) + Vector((0, 0, -rng.uniform(0.3, 0.8)))
        _blade(target(), p + nrm * CAP_OFFSET, nrm, d0, rng.uniform(0.036, 0.056), rng.uniform(0.0105, 0.0155), rng, grav=0.2,
               curl=out * 0.1)
        made += 1

    # ---- beberapa jambul menjulang
    for i in range(COUNTS["spike"]):
        ang = rng.uniform(0, 2 * math.pi)
        d = Vector((math.cos(ang) * 0.18, math.sin(ang) * 0.18, 1.0)).normalized()
        p, nrm = _ray(bvh, d)
        if p is None:
            continue
        d0 = Vector((math.cos(ang) * rng.uniform(0.15, 0.4), math.sin(ang) * rng.uniform(0.15, 0.4) - 0.1, 1.0))
        _blade(target(), p + nrm * CAP_OFFSET, nrm, d0, rng.uniform(0.026, 0.036), rng.uniform(0.0075, 0.010), rng, grav=0.05,
               curl=Vector((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.2), 0)))
        made += 1

    # ---- sisi: menggantung di belakang telinga (+ cambang pendek di depan telinga)
    for s in (1, -1):
        for i in range(COUNTS["side"]):
            for _try in range(30):
                base = math.radians(rng.uniform(-10, 70))
                ang = base if s > 0 else math.pi - base
                el = rng.uniform(0.75, 1.45)
                d = Vector((math.cos(ang) * math.sin(el), math.sin(ang) * math.sin(el), math.cos(el)))
                p, nrm = _ray(bvh, d)
                if p is not None and p.x * s > 0.030 and 1.665 < p.z < 1.750:
                    break
            else:
                continue
            out = Vector((p.x, 0, 0)).normalized()
            d0 = out * rng.uniform(0.2, 0.5) + Vector((0, rng.uniform(0.0, 0.35), -1.0))
            _blade(target(), p + nrm * CAP_OFFSET, nrm, d0, rng.uniform(0.040, 0.066), rng.uniform(0.0085, 0.013), rng, grav=0.16,
                   curl=Vector((s * 0.15, 0.2, 0)))
            made += 1
        for i in range(COUNTS["sideburn"]):                                              # cambang di depan telinga
            z = rng.uniform(1.668, 1.702)
            hit = bvh.ray_cast(Vector((s * 0.2, rng.uniform(-0.035, -0.012), z)), Vector((-s, 0, 0)), 0.3)
            if hit[0] is None:
                continue
            p, nrm = hit[0], hit[1]
            d0 = Vector((s * 0.1, -0.1, -1.0))
            _blade(target(), p + nrm * CAP_OFFSET, nrm, d0, rng.uniform(0.022, 0.032), rng.uniform(0.0065, 0.0085), rng, grav=0.1)
            made += 1

    # ---- belakang: berlapis sampai tengkuk
    for i in range(COUNTS["back"]):
        for _try in range(30):
            ang = math.radians(rng.uniform(55, 125))
            el = rng.uniform(0.55, 1.75)
            d = Vector((math.cos(ang) * math.sin(el) * (1 if rng.random() < 0.5 else -1), math.sin(ang) * math.sin(el), math.cos(el)))
            p, nrm = _ray(bvh, d)
            if p is not None and p.y > 0.025 and 1.625 < p.z < 1.75:
                break
        else:
            continue
        out = Vector((p.x, p.y - CENTER.y, 0)).normalized()
        d0 = out * rng.uniform(0.25, 0.55) + Vector((0, 0.1, -1.0))
        _blade(target(), p + nrm * CAP_OFFSET, nrm, d0, rng.uniform(0.050, 0.082), rng.uniform(0.0095, 0.0145), rng, grav=0.15,
               curl=out * 0.2)
        made += 1
    return made
