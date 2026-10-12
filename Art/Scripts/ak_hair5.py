"""Aksa — rambut gaya 5: LOW FADE + atas bertekstur (permintaan developer 12 Okt 2026, referensi foto potongan low fade).

  - Atas (di atas `top_line`, garis bobot membulat di sekeliling kepala; belakang TIDAK lancip): lapisan tipis + ±950 helai pita halus
    (1,2-2,6 mm) yang berangkat dari pusaran di ubun-ubun belakang, mengalir ke depan dan sedikit ke samping kanan karakter; helai depan
    menjulur jadi poni pendek di dahi; ujung helai sedikit terangkat acak (tekstur berantakan seperti foto).
  - Samping & belakang (antara garis rambut dan `top_line`): rambut cukur tipis -> bukan geometri, tetapi warna vertex kulit kepala
    (`paint_fade`): gelap di atas, memudar ke kulit di bawah (low fade). Masuk ke tekstur BC lewat make_textures_aksa.
Semua koordinat untuk kepala skala 1 (aksa_22 membangun di salinan kepala yang skalanya dibalik). Seed tetap -> deterministik.
"""
import bisect
import math
import random

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import ak_hair3 as H3
import ak_hair4 as H4

SEED = 53
N_STRANDS = 950
SEGS = 7
HI_FRAC = 0.05
WHORL = Vector((0.010, 0.040, 1.762))
STUBBLE = (0.016, 0.014, 0.014)            # warna rambut cukur (linear), dicampur ke kulit
FADE_H = 0.032                             # tinggi gradasi dari garis rambut ke atas (low fade)
smooth = H3.smooth


def top_line(p):
    """Batas bawah rambut panjang (z). Depan = garis rambut; samping di atas telinga; belakang membulat (tanpa ujung lancip)."""
    a = abs(math.degrees(H3._ang(p)))
    front = H3.hairline_z(0.0)
    if a < 45:
        return front
    side = 1.703
    if a < 85:
        return front + (side - front) * smooth(45, 85, a)
    back = 1.692
    return side + (back - side) * smooth(85, 180, a)          # kosinus halus: belakang rata, bukan V


def thick(p):
    """Tebal lapisan atas (dikurangi dari gaya 4): menipis ke 0,6 mm di garis bobot supaya menyatu dengan fade."""
    d = p.z - top_line(p)
    edge = smooth(-0.002, 0.020, d)
    top = smooth(1.70, 1.76, p.z)
    front = smooth(0.0, -0.07, p.y) * smooth(1.70, 1.74, p.z)
    return 0.0006 + (0.0025 + 0.0065 * top + 0.0030 * front) * edge


def stubble(p):
    """0..1 kepadatan rambut cukur di titik p (kulit kepala)."""
    hl = H3.hairline_at(p)
    if p.z < hl - 0.004:
        return 0.0
    s = smooth(hl - 0.004, hl + FADE_H, p.z)
    return 0.92 * s ** 0.8


def paint_fade(head_obj, to_unit):
    """Campur warna rambut cukur ke atribut AK_Zone kepala. to_unit(co) -> koordinat kepala skala 1."""
    ca = head_obj.data.color_attributes["AK_Zone"]
    n = 0
    for i, v in enumerate(head_obj.data.vertices):
        s = stubble(to_unit(v.co))
        if s > 0.01:
            c0 = tuple(ca.data[i].color)
            ca.data[i].color = tuple(c0[j] * (1 - s) + (STUBBLE[j] if j < 3 else 1.0) * s for j in range(4))
            n += 1
    return n


def _flow(p, n, rng_dir):
    r = p - WHORL
    r -= n * r.dot(n)
    r = r.normalized() if r.length > 1e-6 else Vector((0, -1, 0))
    wf = smooth(0.03, -0.04, p.y)
    wb = smooth(0.0, 0.05, p.y)
    ws = smooth(0.035, 0.062, abs(p.x)) * (1.0 - smooth(1.725, 1.760, p.z))
    F = Vector((-0.30, -1.0, -0.10))                          # depan: maju + sedikit ke kanan karakter (poni miring)
    S = Vector((0.0, -0.35, -1.0))
    B = Vector((0.15 * (1 if p.x > 0 else -1), 0.25, -1.0))
    d = r * 0.6 + F * wf + B * wb + S * ws + rng_dir
    d -= n * d.dot(n)
    return d.normalized()


def _snap(bvh, cand, n_prev):
    loc, nrm, _i, _d = bvh.find_nearest(cand)
    if loc is None:
        return None, None
    radial = (loc - H3.HEAD_C).normalized()
    return loc, (nrm + radial * 1.2 + n_prev).normalized()


def _strand(bm, bvh, p0, L, w0, rng, clump):
    swirl, phase, amp = clump
    jit = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.5, 0.5))) * 0.10
    tip_up = rng.random() ** 2 * 0.006                          # ujung terangkat acak (tekstur)
    base_lift = 0.0005 + rng.random() * 0.0018
    stop_front = 1.700 + rng.random() * 0.014                  # ujung poni & garis potong acak (tidak lurus seperti sisir)
    stop_back = 0.002 + rng.random() * 0.012
    loc, n = _snap(bvh, p0, Vector((0, 0, 1)))
    p = loc
    path, normals = [], []
    for k in range(SEGS + 1):
        t = k / SEGS
        lift = thick(p) + base_lift + tip_up * t * t
        path.append(p + n * lift)
        normals.append(n)
        d = _flow(p, n, jit)
        side = d.cross(n)
        d = (d + side * (swirl * 0.25 + math.sin(phase + k * 1.1) * 0.10 * amp)).normalized()
        q, nn = _snap(bvh, p + d * (L / SEGS), n)
        if q is None:
            break
        front = q.y < -0.055
        if (front and q.z < stop_front) or (not front and q.z < top_line(q) - stop_back):
            break                                             # poni berhenti di atas alis; samping/belakang berhenti di garis bobot
        p, n = q, nn
    m = len(path)
    if m < 3:
        return False
    widths = [w0 * (0.8 + 0.3 * math.sin(min(k / (m - 1) * 2.5, 1.0) * math.pi / 2)) * (1.0 - (k / (m - 1)) ** 1.8) if k < m - 1 else 0.0
              for k in range(m)]
    H4._ribbon(bm, path, normals, widths, 0.0, normals[0])
    return True


def build(head_mesh):
    """Mengembalikan (bm_shell, bm_strands, bm_hi, jumlah_helai)."""
    rng = random.Random(SEED)
    bvh = BVHTree.FromPolygons([tuple(v.co) for v in head_mesh.vertices], [tuple(p.vertices) for p in head_mesh.polygons])
    # lapisan atas (offset dari kulit kepala, tepi menipis ke garis bobot)
    bm_shell = bmesh.new()
    keep = [p for p in head_mesh.polygons if all(head_mesh.vertices[i].co.z > top_line(head_mesh.vertices[i].co) - 0.004 for i in p.vertices)]
    vmap = {}
    for p in keep:
        for i in p.vertices:
            if i not in vmap:
                v = head_mesh.vertices[i]
                vmap[i] = bm_shell.verts.new(v.co + v.normal * thick(v.co))
    for p in keep:
        try:
            bm_shell.faces.new([vmap[i] for i in p.vertices])
        except ValueError:
            pass
    for _ in range(3):
        new = {}
        for v in bm_shell.verts:
            nb = [e.other_vert(v).co for e in v.link_edges]
            if nb and not v.is_boundary:
                new[v] = v.co.lerp(sum(nb, Vector()) / len(nb), 0.4)
        for v, co in new.items():
            v.co = co
    bmesh.ops.recalc_face_normals(bm_shell, faces=list(bm_shell.faces))
    bmesh.ops.triangulate(bm_shell, faces=list(bm_shell.faces))
    # akar helai: area-weighted di daerah atas; 35% dekat tepi (garis bobot & garis rambut depan) supaya tepi tampak berhelai
    faces = [p for p in keep]
    areas = [p.area for p in faces]
    cum, acc = [], 0.0
    for a in areas:
        acc += a
        cum.append(acc)
    clumps = H4._clumps(rng)
    bm_str, bm_hi = bmesh.new(), bmesh.new()
    made = tries = 0
    while made < N_STRANDS and tries < N_STRANDS * 20:
        tries += 1
        f = faces[min(bisect.bisect_left(cum, rng.uniform(0, acc)), len(faces) - 1)]
        vs = [head_mesh.vertices[i].co for i in f.vertices]
        u, w = rng.random(), rng.random()
        if u + w > 1:
            u, w = 1 - u, 1 - w
        p = vs[0] + (vs[1] - vs[0]) * u + (vs[2] - vs[0]) * w
        near = p.z - top_line(p)
        if made < 0.35 * N_STRANDS and near > 0.02:
            continue
        frontal = smooth(0.0, -0.07, p.y)
        L = 0.034 + 0.030 * frontal + rng.uniform(-0.008, 0.012) * (1.0 + frontal)
        w0 = rng.uniform(0.0012, 0.0026)
        tgt = bm_hi if rng.random() < HI_FRAC else bm_str
        made += _strand(tgt, bvh, p, L, w0, rng, H4._clump_of(p, clumps))
    return bm_shell, bm_str, bm_hi, made
