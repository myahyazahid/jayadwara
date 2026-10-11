"""Library bentuk hard-surface untuk Iterasi 2 (hero modeling mid-poly).

Dipakai oleh 11_hero_head.py ... 14_hero_leg.py. Semua fungsi bekerja pada bmesh dan mengembalikan bmesh.
Konvensi koordinat sama dengan jd_common (karakter menghadap -Y, kiri = +X, 1 unit = 1 m).
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

rad = math.radians


# ------------------------------------------------------------------ kurva & frame
def catmull(pts, spp=6):
    """Catmull-Rom seragam; hasil melewati semua titik kontrol."""
    P = [Vector(p) for p in pts]
    if len(P) < 3:
        return [P[0].lerp(P[-1], i / spp) for i in range(spp + 1)]
    ext = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1:i + 3]
        for k in range(spp):
            t = k / spp
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1])
    return out


def frames(path, up=None):
    """Frame paralel (T, N, B) di tiap titik path."""
    n = len(path)
    T = []
    for i in range(n):
        a, b = path[max(i - 1, 0)], path[min(i + 1, n - 1)]
        T.append((b - a).normalized())
    up = Vector(up) if up is not None else Vector((0, 0, 1))
    if abs(T[0].dot(up.normalized())) > 0.95:
        up = Vector((1, 0, 0)) if abs(T[0].x) < 0.9 else Vector((0, 1, 0))
    N0 = (up - up.project(T[0])).normalized()
    out = [(T[0], N0, T[0].cross(N0))]
    for i in range(1, n):
        q = T[i - 1].rotation_difference(T[i])
        N = (q @ out[-1][1]).normalized()
        out.append((T[i], N, T[i].cross(N)))
    return out


def _radius_list(radii, n):
    if callable(radii):
        return [radii(i / (n - 1)) for i in range(n)]
    if isinstance(radii, (int, float)):
        return [float(radii)] * n
    return list(radii)


# ------------------------------------------------------------------ primitif bentuk
def tube(bm, path, radii, n=8, squash=(1.0, 1.0), caps=(True, True), up=None, rot=0.0, t_layer=False):
    """Tabung sepanjang `path` dengan radius berubah; radius ≈ 0 di ujung -> runcing.
    t_layer=True: simpan parameter panjang t (0..1) per vertex di layer `JD_t` (untuk bobot rantai tulang, mis. jari)."""
    path = [Vector(p) for p in path]
    rl = _radius_list(radii, len(path))
    Fr = frames(path, up)
    layer = (bm.verts.layers.float.get("JD_t") or bm.verts.layers.float.new("JD_t")) if t_layer else None
    rings = []
    for i, (p, (T, N, B), r) in enumerate(zip(path, Fr, rl)):
        tt = i / max(len(path) - 1, 1)
        if r < 5e-4:
            v = bm.verts.new(p)
            if layer:
                v[layer] = tt
            rings.append([v])
            continue
        ring = []
        for k in range(n):
            a = rot + 2 * math.pi * k / n
            v = bm.verts.new(p + N * (r * squash[0] * math.cos(a)) + B * (r * squash[1] * math.sin(a)))
            if layer:
                v[layer] = tt
            ring.append(v)
        rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(b) == 1:
            for k in range(n):
                bm.faces.new((a[k], a[(k + 1) % n], b[0]))
        elif len(a) == 1:
            for k in range(n):
                bm.faces.new((a[0], b[(k + 1) % n], b[k]))
        else:
            for k in range(n):
                bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    if caps[0] and len(rings[0]) > 2:
        bm.faces.new(rings[0][::-1])
    if caps[1] and len(rings[-1]) > 2:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def closed_tube(bm, loop_pts, radius, n=6, squash=(1.0, 1.0), up=None):
    """Tabung mengikuti kurva TERTUTUP (mis. bingkai permata). loop_pts tanpa duplikasi titik awal."""
    P = [Vector(p) for p in loop_pts]
    m = len(P)
    Fr = []
    prev_N = None
    for i in range(m):
        T = (P[(i + 1) % m] - P[(i - 1) % m]).normalized()
        ref = Vector(up) if up is not None else Vector((0, 0, 1))
        if abs(T.dot(ref)) > 0.95:
            ref = Vector((1, 0, 0))
        N = (ref - ref.project(T)).normalized()
        Fr.append((T, N, T.cross(N)))
    rings = []
    for p, (T, N, B) in zip(P, Fr):
        rings.append([bm.verts.new(p + N * (radius * squash[0] * math.cos(2 * math.pi * k / n))
                                   + B * (radius * squash[1] * math.sin(2 * math.pi * k / n))) for k in range(n)])
    for i in range(m):
        a, b = rings[i], rings[(i + 1) % m]
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def grid_surface(bm, fn, nu, nv, wrap_u=False):
    """Permukaan parametrik: fn(u, v) -> Vector, u,v ∈ [0,1]. Hasil: bidang terbuka (dapat di-solidify)."""
    cols = nu if wrap_u else nu + 1
    V = [[bm.verts.new(Vector(fn(i / nu, j / nv))) for j in range(nv + 1)] for i in range(cols)]
    for i in range(nu if not wrap_u else nu):
        i2 = (i + 1) % cols if wrap_u else i + 1
        for j in range(nv):
            bm.faces.new((V[i][j], V[i2][j], V[i2][j + 1], V[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return V


def plate3d(bm, pts):
    """Satu muka dari titik 3D (outline plat); ketebalan diberikan lewat harden()."""
    f = bm.faces.new([bm.verts.new(Vector(p)) for p in pts])
    return f


def hull(bm, pts):
    verts = [bm.verts.new(Vector(p)) for p in pts]
    bmesh.ops.convex_hull(bm, input=verts, use_existing_faces=False)
    unused = [v for v in verts if v.is_valid and not v.link_faces]
    if unused:
        bmesh.ops.delete(bm, geom=unused, context="VERTS")
    return bm


def ellipsoid_patch(bm, center, radii, th0, th1, ph0=0.0, ph1=2 * math.pi, nu=12, nv=8, rot=None, wrap=False):
    """Bagian elipsoid: polar θ∈[th0,th1] (0 = kutub atas +Z), azimut φ∈[ph0,ph1]. `rot` = Matrix 3x3 pemutar."""
    R = rot if rot is not None else Matrix.Identity(3)
    c = Vector(center)

    def fn(u, v):
        ph = ph0 + (ph1 - ph0) * u
        th = th0 + (th1 - th0) * v
        p = Vector((radii[0] * math.sin(th) * math.cos(ph), radii[1] * math.sin(th) * math.sin(ph), radii[2] * math.cos(th)))
        return c + R @ p

    return grid_surface(bm, fn, nu, nv, wrap_u=wrap)


def axis_patch_fn(p0, p1, r0, r1, center_dir, span, v0=0.0, v1=1.0, squash=(1.0, 1.0), off=0.0):
    """Fungsi permukaan (u,v) untuk plat yang membungkus sumbu p0->p1 (silinder lancip/elips).
    center_dir: arah (dunia) tengah plat; span: sudut bungkus (rad); u melintang sudut, v sepanjang sumbu.
    Normal du×dv bisa menghadap ke dalam atau luar tergantung orientasi — periksa visual."""
    p0, p1 = Vector(p0), Vector(p1)
    a = (p1 - p0).normalized()
    e1 = Vector(center_dir) - Vector(center_dir).project(a)
    e1.normalize()
    e2 = a.cross(e1)

    def fn(u, v):
        t = v0 + (v1 - v0) * v
        ang = (u - 0.5) * span
        c = p0 + (p1 - p0) * t
        r = (r0(t) if callable(r0) else r0 + (r1 - r0) * t) + off      # r0 boleh fungsi profil r(t)
        return c + e1 * (r * squash[0] * math.cos(ang)) + e2 * (r * squash[1] * math.sin(ang))
    return fn


def ring_around_axis(p0, p1, r0, r1, t, n=18, squash=(1.0, 1.0), center_dir=(0, -1, 0)):
    """Titik cincin elips mengelilingi sumbu pada posisi t∈[0,1] (untuk closed_tube)."""
    p0, p1 = Vector(p0), Vector(p1)
    a = (p1 - p0).normalized()
    e1 = Vector(center_dir) - Vector(center_dir).project(a)
    e1.normalize()
    e2 = a.cross(e1)
    c = p0 + (p1 - p0) * t
    r = r0 + (r1 - r0) * t
    return [c + e1 * (r * squash[0] * math.cos(2 * math.pi * k / n)) + e2 * (r * squash[1] * math.sin(2 * math.pi * k / n))
            for k in range(n)]


def surf_normal(fn, u, v, eps=1e-3, wrap_u=False):
    cl = (lambda x: x) if wrap_u else (lambda x: min(max(x, 0.0), 1.0))
    du = Vector(fn(cl(u + eps), v)) - Vector(fn(cl(u - eps), v))
    dv = Vector(fn(u, min(v + eps, 1))) - Vector(fn(u, max(v - eps, 0)))
    n = du.cross(dv)
    return n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))


def curve_on_surface(fn, uv_pts, offset=0.0, spp=6, wrap_u=False):
    """Jalur 3D yang menempel di permukaan fn (dengan offset sepanjang normal).
    wrap_u=True: u periodik (permukaan mengelilingi sumbu), jadi u tidak dijepit ke [0,1]."""
    uvs = catmull([(u, v, 0) for u, v in uv_pts], spp)
    out = []
    for u, v, _ in uvs:
        v = min(max(v, 0), 1)
        if not wrap_u:
            u = min(max(u, 0), 1)
        out.append(Vector(fn(u, v)) + surf_normal(fn, u, v, wrap_u=wrap_u) * offset)
    return out


def ribbon(bm, path, normals, widths):
    """Pita pipih sepanjang path; lebar tegak lurus path di bidang yang normalnya `normals` (ketebalan lewat harden)."""
    path = [Vector(p) for p in path]
    n = len(path)
    wl = _radius_list(widths, n)
    rows = []
    for i, p in enumerate(path):
        T = (path[min(i + 1, n - 1)] - path[max(i - 1, 0)]).normalized()
        side = T.cross(Vector(normals[i])).normalized()
        rows.append((bm.verts.new(p - side * wl[i] / 2), bm.verts.new(p + side * wl[i] / 2)))
    for a, b in zip(rows[:-1], rows[1:]):
        bm.faces.new((a[0], a[1], b[1], b[0]))
    return bm


def ribbon_on_surface(bm, fn, uv_pts, widths, offset=0.0, spp=6, wrap_u=False):
    """Pita emas pipih yang menempel di permukaan fn (ornamen konsep = pita pipih, bukan tabung bulat)."""
    uvs = catmull([(u, v, 0) for u, v in uv_pts], spp)
    pts, nrm = [], []
    for u, v, _ in uvs:
        v = min(max(v, 0), 1)
        if not wrap_u:
            u = min(max(u, 0), 1)
        nn = surf_normal(fn, u, v, wrap_u=wrap_u)
        pts.append(Vector(fn(u, v)) + nn * offset)
        nrm.append(nn)
    return ribbon(bm, pts, nrm, widths)


def quad_region_fn(fn, c00, c10, c11, c01):
    """Fungsi permukaan baru untuk daerah segiempat (bilinear) di ruang uv permukaan fn (mis. pelat emas di dada)."""
    def g(u, v):
        a = (c00[0] * (1 - u) + c10[0] * u, c00[1] * (1 - u) + c10[1] * u)
        b = (c01[0] * (1 - u) + c11[0] * u, c01[1] * (1 - u) + c11[1] * u)
        uu, vv = a[0] * (1 - v) + b[0] * v, a[1] * (1 - v) + b[1] * v
        return fn(min(max(uu, 0), 1), min(max(vv, 0), 1))
    return g


def offset_fn(fn, d):
    """Permukaan fn digeser sepanjang normalnya sejauh d."""
    def g(u, v):
        return Vector(fn(u, v)) + surf_normal(fn, u, v) * d
    return g


def spiral_uv(center, r0, turns=1.4, start=0.0, n=14, direction=1, r1=0.015):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        a = start + direction * 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        pts.append((center[0] + r * math.cos(a), center[1] + r * math.sin(a)))
    return pts


# ------------------------------------------------------------------ modifier -> bmesh
def eval_mods(bm, mods):
    """Terapkan daftar modifier [(tipe, {prop: nilai})] lewat evaluasi objek sementara; kembalikan bmesh baru."""
    me = bpy.data.meshes.new("_hero_tmp")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("_hero_tmp", me)
    bpy.context.scene.collection.objects.link(ob)
    for typ, props in mods:
        m = ob.modifiers.new(typ.title(), typ)
        for k, v in props.items():
            try:
                setattr(m, k, v)
            except (AttributeError, TypeError) as e:
                print(f"  ! modifier {typ}.{k}: {e}")
    bpy.context.view_layer.update()
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me2 = bpy.data.meshes.new_from_object(ev)
    out = bmesh.new()
    out.from_mesh(me2)
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(me)
    bpy.data.meshes.remove(me2)
    return out


def harden(bm, thick=0.010, offset=0.0, bevel=0.003, segs=2, angle=40, subsurf=0):
    """Beri ketebalan (solidify) lalu bevel tepi tajam. thick=0 -> hanya bevel."""
    mods = []
    if thick:
        mods.append(("SOLIDIFY", dict(thickness=thick, offset=offset, use_even_offset=True)))
    if subsurf:
        mods.append(("SUBSURF", dict(levels=subsurf, render_levels=subsurf)))
    if bevel:
        mods.append(("BEVEL", dict(width=bevel, segments=segs, limit_method="ANGLE", angle_limit=rad(angle))))
    return eval_mods(bm, mods) if mods else bm


def sharp_by_angle(bm, angle=35):
    """Tandai tepi tajam (> angle) sebagai sharp dan muka smooth -> tampilan hard-surface tanpa jaringan tris tambahan."""
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > rad(angle):
            e.smooth = False
    return bm


# ------------------------------------------------------------------ bentuk turunan yang sering dipakai
def lens(bm, center, size_x, size_z, thick, rot=(0, 0, 0), pts=8, bevel=0.002):
    """Plat berbentuk wajik/lensa kecil (mata, permata kecil, ornamen)."""
    cx = Vector(center)
    R = Matrix.Rotation(rot[2], 3, "Z") @ Matrix.Rotation(rot[1], 3, "Y") @ Matrix.Rotation(rot[0], 3, "X")
    ring = [cx + R @ Vector((size_x * math.cos(2 * math.pi * k / pts) / 2, 0, size_z * math.sin(2 * math.pi * k / pts) / 2))
            for k in range(pts)]
    plate3d(bm, ring)
    return harden(bm, thick=thick, bevel=bevel, segs=1)


def diamond(bm, c, w, h, d_front, d_back, z_off=0.0):
    """Berlian runcing depan-belakang (hull 6 titik): lebar w, tinggi h, tonjolan depan d_front (ke -Y)."""
    c = Vector(c)
    pts = [c + Vector((0, 0, h / 2)), c + Vector((0, 0, -h / 2)), c + Vector((-w / 2, 0, 0)), c + Vector((w / 2, 0, 0)),
           c + Vector((0, -d_front, 0)), c + Vector((0, d_back, 0))]
    return hull(bm, pts)


def count_tris(bm):
    return sum(len(f.verts) - 2 for f in bm.faces)
