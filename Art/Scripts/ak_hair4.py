"""Aksa — rambut gaya 4: HELAI. Cangkang gaya 3 (volume + belahan, `ak_hair3.build_shell`) tetap sebagai lapisan dasar yang tidak
terlihat bolong, tetapi permukaannya ditutup ratusan helai pita tipis yang meruncing ke ujung (bukan gumpalan tebal).

Permintaan developer (12 Okt 2026): rambut gaya 3 terlalu kasar/bergumpal, minta helai yang lebih realistis.
  - Akar helai: diambil acak (seed tetap) dari permukaan cangkang; 40% dekat garis rambut supaya garis rambut tampak tumbuh helai demi helai.
  - Jalur: mengikuti medan aliran gaya 3 (`ak_hair3.flow`: disisir ke belakang, menjauhi belahan, belakang turun) + arah gerombol
    (60 gerombol, tiap gerombol punya sapuan arah + gelombang halus) + jitter kecil per helai -> helai bertetangga sejajar seperti rambut sungguhan.
  - Penampang: pita datar 2 titik (kiri, kanan) lebar 1,6-3 mm, meruncing ke satu titik di ujung; tiap helai diangkat dari
    permukaan 1-4 mm menurut lapisan (acak) supaya saling menumpuk.
  - ~5% helai berwarna `hair_hi` (nyaris hitam, highlight sangat halus).
  Revisi 2 (developer: masih menggumpal): helai lebih tipis, lebih jarang (520), rambut hitam pekat; cangkang menjadi 'kulit kepala gelap' yang tampak di sela helai.
Anggaran: ±8k segitiga (N_STRANDS x SEGS x 2). Seed tetap -> deterministik.
"""
import math
import random

import bmesh
from mathutils import Vector

import ak_hair3 as H3

SEED = 47
N_STRANDS = 520
SEGS = 8
N_CLUMPS = 60
HI_FRAC = 0.05
HEAD_C = H3.HEAD_C


def _sample_roots(bm_shell, rng, n):
    """Titik akar pada cangkang (area-weighted) di atas garis rambut; 40% dibatasi dekat garis rambut."""
    faces = [f for f in bm_shell.faces if f.calc_center_median().z > H3.hairline_at(f.calc_center_median()) - 0.002]
    areas = [f.calc_area() for f in faces]
    tot = sum(areas)
    cum, acc = [], 0.0
    for a in areas:
        acc += a
        cum.append(acc)
    import bisect
    out = []
    tries = 0
    while len(out) < n and tries < n * 30:
        tries += 1
        f = faces[min(bisect.bisect_left(cum, rng.uniform(0, tot)), len(faces) - 1)]
        vs = [v.co for v in f.verts]
        i = rng.randrange(1, len(vs) - 1)
        u, w = rng.random(), rng.random()
        if u + w > 1:
            u, w = 1 - u, 1 - w
        p = vs[0] + (vs[i] - vs[0]) * u + (vs[i + 1] - vs[0]) * w
        near = p.z - H3.hairline_at(p)
        if len(out) < 0.4 * n and near > 0.03:
            continue
        out.append((p, f.normal.copy()))
    return out


def _clumps(rng):
    return [(rng.uniform(-1, 1), rng.uniform(0, 6.28), rng.uniform(0.6, 1.4)) for _ in range(N_CLUMPS)]


def _clump_of(p, clumps):
    """Gerombol menurut posisi: bagi permukaan kepala jadi sel sehingga helai bertetangga berbagi gerombol."""
    h = int((p.x + 0.1) * 160) * 73856093 ^ int((p.y + 0.1) * 160) * 19349663 ^ int((p.z - 1.6) * 160) * 83492791
    return clumps[h % len(clumps)]


def _ribbon(bm, path, normals, widths, camber, flip_ref):
    m = len(path)
    rows = []
    for k in range(m):
        p, n = path[k], normals[k]
        T = (path[min(k + 1, m - 1)] - path[max(k - 1, 0)]).normalized()
        b = T.cross(n)
        if b.length < 1e-6:
            rows.append([bm.verts.new(p)])
            continue
        b.normalize()
        w = widths[k]
        if w < 1e-5:
            rows.append([bm.verts.new(p)])
            continue
        rows.append([bm.verts.new(p - b * w / 2), bm.verts.new(p + b * w / 2)])
    faces = []
    for a, c in zip(rows[:-1], rows[1:]):
        try:
            if len(a) == 1:
                continue
            if len(c) == 1:
                faces.append(bm.faces.new((a[0], a[1], c[0])))
            else:
                faces.append(bm.faces.new((a[0], a[1], c[1], c[0])))
        except ValueError:
            pass
    for f in faces:                                               # normal menghadap luar (searah normal permukaan)
        f.normal_update()
        if f.normal.dot(flip_ref) < 0:
            f.normal_flip()


def _strand(bm, bvh_shell, p0, n0, L, w0, lift, rng, clump, segs=SEGS):
    swirl, phase, amp = clump
    path, normals = [], []
    p, n = Vector(p0), Vector(n0)
    own = Vector((rng.uniform(-1, 1), rng.uniform(-0.4, 0.4), rng.uniform(-0.3, 0.3))) * 0.04      # jitter kecil per helai
    for k in range(segs + 1):
        path.append(p + n * lift)
        normals.append(n)
        d = H3.flow(p, n, Vector())
        wave = math.sin(phase + k * 0.9) * 0.07 * amp
        side = d.cross(n)
        d = d + side * (swirl * 0.14 * (1.0 - 0.5 * k / segs) + wave) + own
        d -= n * d.dot(n)
        d.normalize()
        q, nn = H3._snap(bvh_shell, p + d * (L / segs), n)
        if q is None:
            break
        p, n = q, nn
    m = len(path)
    if m < 3:
        return False
    widths = []
    for k in range(m):
        t = k / (m - 1)
        widths.append(w0 * (0.75 + 0.4 * math.sin(min(t * 2.2, 1.0) * math.pi / 2)) * (1.0 - t ** 2.2) if k < m - 1 else 0.0)
    _ribbon(bm, path, normals, widths, 0.0007, normals[0])
    return True


def build(head_mesh):
    """Mengembalikan (bm_shell, bm_strands, bm_hi, jumlah_helai). Pemanggil menyelesaikan objek (finish_part)."""
    rng = random.Random(SEED)
    bm_shell, bm_strands, bm_hi = bmesh.new(), bmesh.new(), bmesh.new()
    bvh_shell = H3.build_shell(bm_shell, head_mesh)
    bm_shell.faces.ensure_lookup_table()
    clumps = _clumps(rng)
    made = 0
    for p, n in _sample_roots(bm_shell, rng, N_STRANDS):
        top = H3.smooth(1.70, 1.76, p.z)
        front = H3.smooth(0.0, -0.07, p.y)
        L = 0.095 + 0.050 * front * top + rng.uniform(-0.012, 0.020) + 0.020 * top
        w0 = rng.uniform(0.0016, 0.0030)
        lift = 0.0010 + rng.random() ** 1.5 * 0.0030
        tgt = bm_hi if rng.random() < HI_FRAC else bm_strands
        if _strand(tgt, bvh_shell, p, n, L, w0, lift, rng, _clump_of(p, clumps)):
            made += 1
    return bm_shell, bm_strands, bm_hi, made
