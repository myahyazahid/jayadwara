"""Aksa Iterasi 3 — library pakaian & tangan: loft terbuka, solidify, proyeksi ke permukaan, dorong-keluar antar lapisan, metaball.

Dipakai aksa_30_outfit.py. Koordinat dunia Blender (m), karakter menghadap -Y, kiri = +X.
"""
import math

import bmesh
import bpy
from mathutils import Quaternion, Vector
from mathutils.bvhtree import BVHTree


def sgn(x):
    return 1.0 if x >= 0 else -1.0


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def se_point(cx, cy, hw, hd, p, t, z):
    """Titik super-elips; t=0 depan (-Y), t=+pi/2 sisi +X."""
    s, c = math.sin(t), math.cos(t)
    x = cx + hw * sgn(s) * abs(s) ** (2 / p)
    y = cy - hd * sgn(c) * abs(c) ** (2 / p)
    return Vector((x, y, z))


def loft(bm, secs, n=32, open_front=False, caps=(False, False)):
    """secs: [(z, cx, cy, hw, hd, p, edge_x)]. open_front: cincin dari tepi depan kiri memutar lewat belakang ke tepi kanan
    (edge_x = setengah lebar bukaan depan). Mengembalikan daftar cincin."""
    rings = []
    for z, cx, cy, hw, hd, p, ex in secs:
        if open_front and ex:
            te = math.asin(min(0.999, (ex / hw) ** (p / 2)))
            ts = [te + (2 * math.pi - 2 * te) * k / (n - 1) for k in range(n)]
        else:
            ts = [2 * math.pi * k / n for k in range(n)]
        rings.append([bm.verts.new(se_point(cx, cy, hw, hd, p, t, z)) for t in ts])
    for a, b in zip(rings[:-1], rings[1:]):
        m = len(a)
        rng = range(m - 1) if open_front else range(m)
        for k in rng:
            bm.faces.new((a[k], a[(k + 1) % m], b[(k + 1) % m], b[k]))
    if caps[0] and not open_front:
        bm.faces.new(rings[0][::-1])
    if caps[1] and not open_front:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return rings


def solidify(bm, thickness):
    """Tebalkan permukaan terbuka (ke arah dalam)."""
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=thickness)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))


def bvh_of(obj_or_mesh):
    me = obj_or_mesh.data if hasattr(obj_or_mesh, "data") else obj_or_mesh
    return BVHTree.FromPolygons([tuple(v.co) for v in me.vertices], [tuple(p.vertices) for p in me.polygons])


def bvh_of_bm(bm):
    return BVHTree.FromBMesh(bm)


def ray(bvh, origin, direction, dist=1.0):
    hit = bvh.ray_cast(Vector(origin), Vector(direction).normalized(), dist)
    return (hit[0], hit[1]) if hit[0] is not None else (None, None)


def patch_on(bm, bvh, center, u_vec, v_vec, size_u, size_v, view_dir, offset, nu=6, nv=6, thick=0.0):
    """Pelat persegi yang menempel di permukaan: grid di bidang (u, v) sekitar center diproyeksikan sepanjang view_dir,
    lalu digeser `offset` sepanjang normal. thick > 0 -> ditebalkan. Mengembalikan daftar vertex baru."""
    u_vec, v_vec, view_dir = Vector(u_vec).normalized(), Vector(v_vec).normalized(), Vector(view_dir).normalized()
    grid = []
    for i in range(nu + 1):
        row = []
        for j in range(nv + 1):
            q = Vector(center) + u_vec * size_u * (i / nu - 0.5) + v_vec * size_v * (j / nv - 0.5)
            loc, nrm = ray(bvh, q - view_dir * 0.3, view_dir, 0.6)
            if loc is None:
                loc, nrm = q, -view_dir
            row.append(bm.verts.new(loc + nrm * offset))
        grid.append(row)
    new_faces = []
    for i in range(nu):
        for j in range(nv):
            new_faces.append(bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1])))
    if thick > 0:
        res = bmesh.ops.solidify(bm, geom=new_faces, thickness=thick)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return grid


def curve_on(bvh, pts, view_dir, offset):
    """Proyeksikan titik kurva ke permukaan sepanjang view_dir (atau arah per titik bila view_dir callable)."""
    out = []
    for p in pts:
        d = Vector(view_dir(p) if callable(view_dir) else view_dir).normalized()
        loc, nrm = ray(bvh, Vector(p) - d * 0.3, d, 0.6)
        out.append(loc + nrm * offset if loc is not None else Vector(p))
    return out


def push_outside(obj, inner_bvhs, gap=0.003):
    """Vertex obj yang berada di dalam / terlalu dekat permukaan lapisan dalam didorong keluar sepanjang normal lapisan dalam."""
    moved = 0
    for v in obj.data.vertices:
        p = obj.matrix_world @ v.co
        for bvh in inner_bvhs:
            loc, nrm, _i, d = bvh.find_nearest(p)
            if loc is None or d > 0.05:
                continue
            depth = (p - loc).dot(nrm)
            if depth < gap:
                p = loc + nrm * gap
                moved += 1
        v.co = obj.matrix_world.inverted() @ p
    return moved


# ---------------------------------------------------------------- metaball
META_K = 1.0 / 0.567          # radius elemen -> radius permukaan (threshold 0,6, stiffness 2; terkalibrasi)


def meta_mesh(name, elements, resolution=0.0025, decimate=None):
    """elements: [(co, dir, half_len, surface_radius)] kapsul (half_len 0 -> bola). Mengembalikan Mesh baru (modifier diterapkan)."""
    mb = bpy.data.metaballs.new(name + "_mb")
    mb.resolution = resolution
    mb.render_resolution = resolution
    mb.threshold = 0.6
    for co, d, half, rad in elements:
        e = mb.elements.new(type="CAPSULE" if half > 0 else "BALL")
        e.co = Vector(co)
        if half > 0:
            e.size_x = half
            e.rotation = Vector((1, 0, 0)).rotation_difference(Vector(d).normalized())
        e.radius = rad * META_K
        e.stiffness = 2.0
    ob = bpy.data.objects.new(name + "_mbo", mb)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.metaballs.remove(mb)
    if decimate:
        tmp = bpy.data.objects.new(name + "_dec", me)
        bpy.context.scene.collection.objects.link(tmp)
        mod = tmp.modifiers.new("dec", "DECIMATE")
        mod.ratio = decimate
        dg = bpy.context.evaluated_depsgraph_get()
        me2 = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
        bpy.data.objects.remove(tmp, do_unlink=True)
        bpy.data.meshes.remove(me)
        me = me2
    return me


def mesh_into_bm(bm, me):
    """Salin geometri Mesh ke bmesh bm."""
    off = len(bm.verts)
    vs = [bm.verts.new(v.co) for v in me.vertices]
    for p in me.polygons:
        try:
            bm.faces.new([vs[i] for i in p.vertices])
        except ValueError:
            pass
    return vs
