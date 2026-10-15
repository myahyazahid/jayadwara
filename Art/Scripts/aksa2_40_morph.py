"""Aksa2 — 8 morph target wajah di atas model Tripo (docs/19 A4; pengganti percobaan Hermes H3b yang dihentikan).

  blender --background --factory-startup --python Art/Scripts/aksa2_40_morph.py
Input : Art/Blender/aksa2/aksa2_v06_F4.blend   (TIDAK diubah)
Output: Art/Blender/aksa2/aksa2_v07_morph.blend

Kenapa tidak transfer dari SK_Aksa (cara Hermes): wajah Tripo = satu permukaan segitiga ±9 mm, mata dilukis di tekstur,
bibir menyatu. Morph hasil transfer merusak dahi/rambut. Di sini:
  1. area mata & mulut dirapatkan (subdivide lokal, bobot tulang & UV ikut terinterpolasi),
  2. garis bibir DIPISAH (split edge) + dibuat kantong rongga mulut gelap (UV titik gelap atlas), tertutup rapat di netral,
  3. tiap morph = medan perpindahan lokal berbobot halus di sekitar landmark (diukur dari render berkisi 5 mm, 15 Okt 2026).
Landmark (m, Blender, +X = kiri karakter, wajah menghadap -Y): mata R/L (-0,032 / +0,031; z 1,645), alis z 1,658 (x ±0,014..0,048),
garis bibir z 1,580 (sudut x ±0,0255), dasar hidung z 1,600, dagu z 1,545.
Nama shape key = SK_Aksa: ak_blink_L, ak_blink_R, ak_smile, ak_angry, ak_mouth_open, ak_brow_up, ak_wince, ak_sad.
Tidak ada vertex di bawah z 1,45 m yang bergeser (validate_aksa.py --require-morph 8).
"""
import heapq
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1].parent
BLEND_IN = ROOT / "Art" / "Blender" / "aksa2" / "aksa2_v06_F4.blend"
BLEND_OUT = ROOT / "Art" / "Blender" / "aksa2" / "aksa2_v07_morph.blend"

EYE = {"R": (-0.032, 1.645), "L": (0.031, 1.646)}
BROW_Z, BROW_IN, BROW_OUT = 1.658, 0.014, 0.048
LIP_Z, LIP_HALF = 1.580, 0.0255
POCKET_DEPTH = 0.024
LIP_CURVE = []            # [(x, z)] jalur belah bibir (diisi build_topology)
JAW_OPEN = 0.014          # m, bibir bawah turun saat ak_mouth_open = 1


def sm(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ell(P, cx, cz, rx, rz_up, rz_dn=None):
    """Bobot elips halus (1 di pusat, 0 di tepi); rz_up di atas pusat, rz_dn di bawah."""
    rz_dn = rz_up if rz_dn is None else rz_dn
    dz = P[:, 2] - cz
    rz = np.where(dz >= 0, rz_up, rz_dn)
    r = np.sqrt(((P[:, 0] - cx) / rx) ** 2 + (dz / rz) ** 2)
    return sm(1.0 - r)


# ---------------------------------------------------------------- topologi
def front_face_in(cx, cz, rx, rz):
    def fn(c, n):
        return n.y < -0.15 and c.y < -0.03 and ((c.x - cx) / rx) ** 2 + ((c.z - cz) / rz) ** 2 <= 1.0
    return fn


def subdivide(bm, fn, cuts=1):
    faces = [f for f in bm.faces if fn(f.calc_center_median(), f.normal)]
    edges = list({e for f in faces for e in f.edges})
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=cuts, use_grid_fill=True, smooth=0.0)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    return len(faces)


def darkest_uv(me):
    """UV sebuah texel gelap pada atlas (isi rongga mulut)."""
    img = None
    for n in me.materials[0].node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            lk = n.inputs["Base Color"].links
            if lk and getattr(lk[0].from_node, "image", None):
                img = lk[0].from_node.image
    assert img is not None, "tekstur Base Color tidak ditemukan"
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[:, :, :3]
    lum = px.mean(axis=2)
    sat = px.max(axis=2) - px.min(axis=2)
    orm = bpy.data.images.load(str(ROOT / "Art" / "Export" / "Textures_Aksa2" / "T_Aksa2_ORM.png"))
    assert tuple(orm.size) == (w, h), "ORM harus seukuran Base Color"
    op = np.array(orm.pixels[:], dtype=np.float32).reshape(h, w, 4)[:, :, :3]
    ok = (sat < 0.08) & (lum > 0.012) & (op[:, :, 1] >= 0.66) & (op[:, :, 2] < 0.12)   # netral gelap, KASAR (roughness>=0,66), non-metal
    k = 5
    from numpy.lib.stride_tricks import sliding_window_view
    okw = sliding_window_view(ok, (k, k)).all(axis=(2, 3))
    avg = np.where(okw, sliding_window_view(lum, (k, k)).mean(axis=(2, 3)), 9.0)
    y, x = np.unravel_index(np.argmin(avg), avg.shape)
    print("texel gelap:", (int(x) + k // 2, int(y) + k // 2), "lum", float(avg[y, x]), "rgb", px[y + k // 2, x + k // 2])
    return ((x + k // 2 + 0.5) / w, (y + k // 2 + 0.5) / h)


def build_topology(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    mk = bm.verts.layers.int.new("mk")           # 1 = bibir bawah / kantong bawah, 2 = bibir atas / kantong atas
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    n0 = len(bm.faces)
    for s, (ex, ez) in EYE.items():
        subdivide(bm, front_face_in(ex, ez, 0.032, 0.017))
        subdivide(bm, front_face_in(ex, ez, 0.026, 0.012))
    subdivide(bm, front_face_in(0.0, LIP_Z, 0.040, 0.024))
    subdivide(bm, front_face_in(0.0, LIP_Z, 0.034, 0.011))
    print("segitiga setelah rapatkan:", len(bm.faces), "(sebelum", n0, ")")

    # --- jalur garis bibir (Dijkstra, ikuti z = LIP_Z)
    cand = [v for v in bm.verts if v.normal.y < -0.2 and v.co.y < -0.03 and abs(v.co.x) <= LIP_HALF + 0.003
            and abs(v.co.z - LIP_Z) < 0.007]
    cset = set(cand)
    a = min(cand, key=lambda v: (v.co.x - LIP_HALF) ** 2 + (v.co.z - LIP_Z) ** 2)
    b = min(cand, key=lambda v: (v.co.x + LIP_HALF) ** 2 + (v.co.z - LIP_Z) ** 2)
    dist, prev, pq = {a: 0.0}, {}, [(0.0, 0, a)]
    cnt = 1
    while pq:
        d, _, v = heapq.heappop(pq)
        if v is b:
            break
        if d > dist.get(v, 1e9):
            continue
        for e in v.link_edges:
            w = e.other_vert(v)
            if w not in cset:
                continue
            c = d + e.calc_length() * (1.0 + 400.0 * abs(w.co.z - LIP_Z))
            if c < dist.get(w, 1e9):
                dist[w], prev[w] = c, v
                heapq.heappush(pq, (c, cnt, w))
                cnt += 1
    assert b in prev, "jalur garis bibir tidak ditemukan"
    chain = [b]
    while chain[-1] is not a:
        chain.append(prev[chain[-1]])
    chain.reverse()                                  # dari sudut +X ke sudut -X
    print("rantai bibir:", len(chain), "vertex, x", round(chain[0].co.x, 4), "->", round(chain[-1].co.x, 4))
    LIP_CURVE.clear()
    LIP_CURVE.extend(sorted((v.co.x, v.co.z) for v in chain))            # z garis bibir sebenarnya, per x
    dev = [abs(v.co.z - LIP_Z) * 1000 for v in chain]
    print("simpangan z jalur bibir (mm): maks %.2f rata %.2f" % (max(dev), sum(dev) / len(dev)))
    positions = [tuple(round(c, 7) for c in v.co) for v in chain]
    edges = [bm.edges.get((chain[i], chain[i + 1])) for i in range(len(chain) - 1)]
    assert all(edges)
    bmesh.ops.split_edges(bm, edges=edges)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.normal_update()

    # --- klasifikasi atas/bawah per posisi
    by_pos = {}
    for v in bm.verts:
        key = tuple(round(c, 7) for c in v.co)
        if key in set(positions):
            by_pos.setdefault(key, []).append(v)
    U, Lw = [], []
    for p in positions:
        vs = by_pos[p]
        if len(vs) == 1:
            U.append(vs[0])
            Lw.append(vs[0])
            continue
        def mz(v):
            return np.mean([f.calc_center_median().z for f in v.link_faces])
        vs.sort(key=mz)
        Lw.append(vs[0])
        U.append(vs[1])
    n = len(chain) - 1
    assert U[0] is Lw[0] and U[n] is Lw[n], "ujung celah harus tidak terbelah"

    # --- kantong rongga mulut (manual), cincin belakang
    dl = bm.verts.layers.deform.active
    uvl = bm.loops.layers.uv.active
    uv = darkest_uv(me)

    def new_back(src, x, y, z):
        v = bm.verts.new((x, y, z))
        if dl:
            for g, w in src[dl].items():
                v[dl][g] = w
        return v

    BA = new_back(U[0], U[0].co.x * 0.85, U[0].co.y + 0.006, LIP_Z)
    BB = new_back(U[n], U[n].co.x * 0.85, U[n].co.y + 0.006, LIP_Z)
    BU, BL = [BA], [BA]
    for i in range(1, n):
        t = U[i].co.x / LIP_HALF
        depth = 0.004 + (POCKET_DEPTH - 0.004) * max(0.0, 1.0 - t * t)
        BU.append(new_back(U[i], U[i].co.x * 0.88, U[i].co.y + depth, LIP_Z + 0.0025))
        BL.append(new_back(Lw[i], Lw[i].co.x * 0.88, Lw[i].co.y + depth, LIP_Z - 0.0025))
    BU.append(BB)
    BL.append(BB)
    for v in BL[1:n]:
        v[mk] = 3
    for v in BU[1:n]:
        v[mk] = 2
    for v in Lw[1:n]:
        v[mk] = 1
    for v in U[1:n]:
        v[mk] = 2

    roof, floor = [], []
    for i in range(n):
        roof.append([U[i], U[i + 1], BU[i + 1], BU[i]])
        floor.append([Lw[i], BL[i], BL[i + 1], Lw[i + 1]])
    ring = BU[:-1] + [BB] + BL[-2::-1]
    ring = [v for k, v in enumerate(ring) if v not in ring[:k]]

    def mk_faces(quads):
        out = []
        for vs in quads:
            vs = [v for k, v in enumerate(vs) if v not in vs[:k]]      # buang vertex ganda di ujung (jadi segitiga)
            if len(vs) >= 3:
                out.append(bm.faces.new(vs))
        return out

    f_roof, f_floor, f_cap = mk_faces(roof), mk_faces(floor), [bm.faces.new(ring)]
    bm.normal_update()
    # orientasi eksplisit: atap menghadap bawah (-Z), lantai menghadap atas (+Z), dinding belakang menghadap depan (-Y)
    for fs, ax, sign in ((f_roof, "z", -1), (f_floor, "z", 1), (f_cap, "y", -1)):
        for f in fs:
            if getattr(f.normal, ax) * sign < 0:
                f.normal_flip()
    faces = f_roof + f_floor + f_cap
    bm.normal_update()
    for f in faces:
        f.smooth = False                                 # kantong flat; tepi rim tajam supaya normal bibir tidak tercemar
        for e in f.edges:
            if len(e.link_faces) > 1 and any(lf not in faces for lf in e.link_faces):
                e.smooth = False
        for lp in f.loops:
            lp[uvl].uv = uv
    bm.normal_update()
    print("kantong mulut:", len(faces), "poligon, kedalaman", POCKET_DEPTH)
    bm.to_mesh(me)
    me.update()
    bm.free()


def snapshot_normals(me):
    """Posisi + normal rata-rata per vertex dari mesh ASLI (custom normals Tripo), sebelum topologi diubah."""
    from mathutils.kdtree import KDTree
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    lv = np.empty(len(me.loops), dtype=np.int32)
    me.loops.foreach_get("vertex_index", lv)
    cn = np.array([c.vector[:] for c in me.corner_normals], dtype=np.float64)
    acc = np.zeros_like(co)
    np.add.at(acc, lv, cn)
    acc /= np.maximum(np.linalg.norm(acc, axis=1, keepdims=True), 1e-8)
    kd = KDTree(len(co))
    for i, c in enumerate(co):
        kd.insert(tuple(c), i)
    kd.balance()
    return kd, acc


def fix_normals(ob, snap):
    """Mesh Tripo punya custom split normals; loop baru hasil subdivisi mewarisi normal ngawur (bibir berbintik).
    Di blok wajah (|x|<0,07, z 1,50-1,675, depan) tiap loop memakai normal vertex ASLI terdekat (karakter shading Tripo
    tetap, kedua sisi celah bibir sama); kantong mulut (poligon flat) memakai normal hasil hitung. Luar blok tidak disentuh."""
    kd, vn = snap
    me = ob.data
    tmp = ob.copy()
    tmp.data = me.copy()
    bpy.context.scene.collection.objects.link(tmp)
    bpy.context.view_layer.objects.active = tmp
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.customdata_custom_splitnormals_clear()
    bpy.ops.object.mode_set(mode="OBJECT")
    auto = np.array([c.vector[:] for c in tmp.data.corner_normals], dtype=np.float64)
    bpy.data.objects.remove(tmp, do_unlink=True)
    cur = np.array([c.vector[:] for c in me.corner_normals], dtype=np.float64)
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    lv = np.empty(len(me.loops), dtype=np.int32)
    me.loops.foreach_get("vertex_index", lv)
    lp = np.empty(len(me.loops), dtype=np.int32)
    me.loops.foreach_get("vertex_index", lp)
    smooth = np.zeros(len(me.polygons), dtype=bool)
    me.polygons.foreach_get("use_smooth", smooth)
    poly_of_loop = np.empty(len(me.loops), dtype=np.int32)
    for p in me.polygons:
        poly_of_loop[p.loop_start:p.loop_start + p.loop_total] = p.index
    P = co[lv]
    block = (np.abs(P[:, 0]) < 0.07) & (P[:, 2] > 1.50) & (P[:, 2] < 1.675) & (P[:, 1] < 0.0)
    out = cur.copy()
    for li in np.where(block)[0]:
        if smooth[poly_of_loop[li]]:
            hits = kd.find_n(tuple(P[li]), 4)                       # campuran 4 vertex asli terdekat (tanpa batas sel)
            wts = np.array([1.0 / (h[2] + 1e-4) ** 2 for h in hits])
            out[li] = (vn[[h[1] for h in hits]] * wts[:, None]).sum(axis=0) / wts.sum()
        else:
            out[li] = auto[li]
    n = np.linalg.norm(out, axis=1, keepdims=True)
    out = out / np.where(n < 1e-8, 1.0, n)
    me.normals_split_custom_set(out.tolist())
    bpy.context.view_layer.objects.active = ob
    print("normal wajah disetel ulang untuk", int(block.sum()), "loop dari", len(block))


# ---------------------------------------------------------------- morph
def displacements(P, mk):
    """Kembalikan {nama: array Nx3 perpindahan (m)}."""
    N = len(P)
    D = {}
    x, z = P[:, 0], P[:, 2]
    gate = (P[:, 2] > 1.45) & (P[:, 1] < 0.03) & (np.abs(P[:, 0]) < 0.075)      # hanya wajah depan
    lower_rim = mk == 1                                  # bibir bawah (rim celah)
    lower_back = mk == 3                                 # dinding belakang kantong bawah
    lower_pocket = lower_rim | lower_back
    upper_pocket = mk == 2

    def zero():
        return np.zeros((N, 3))

    def blink(sd, amount=0.92):
        ex, ez = EYE[sd]
        d = zero()
        zp = ez - 0.0015
        w = ell(P, ex, ez, 0.026, 0.015, 0.011) * gate
        up = z > zp
        d[:, 2] = np.where(up, -(z - zp) * amount * w, (zp - z) * 0.28 * w)
        d[:, 1] = -0.0008 * w
        return d

    def eye_squint(sd, up_mm, lo_mm):
        ex, ez = EYE[sd]
        d = zero()
        w = ell(P, ex, ez, 0.026, 0.012, 0.010) * gate
        d[:, 2] = np.where(z > ez - 0.0015, -up_mm * w, lo_mm * w)
        return d

    def brow_inner_outer(sd, inner_dz, outer_dz, inner_dx):
        s = 1.0 if sd == "L" else -1.0
        d = zero()
        g = sm((z - 1.650) / 0.007) * gate * sm((1.700 - z) / 0.020 + 0.0)
        wi = ell(P, s * 0.022, BROW_Z + 0.001, 0.020, 0.016, 0.012) * g
        wo = ell(P, s * 0.043, BROW_Z + 0.002, 0.018, 0.015, 0.012) * g
        d[:, 2] = inner_dz * wi + outer_dz * wo
        d[:, 0] = -s * inner_dx * wi
        d[:, 1] = -0.0009 * (np.abs(inner_dz) > 0) * (wi + wo) * 0.5
        return d

    def corner(sd, dz, dx, dy):
        s = 1.0 if sd == "L" else -1.0
        d = zero()
        w = ell(P, s * LIP_HALF, LIP_Z, 0.020, 0.013, 0.015) * gate
        d[:, 2] = dz * w
        d[:, 0] = s * dx * w
        d[:, 1] = dy * w
        return d

    def cheek(sd, dz, dy):
        s = 1.0 if sd == "L" else -1.0
        d = zero()
        w = ell(P, s * 0.034, 1.619, 0.030, 0.020, 0.022) * gate
        d[:, 2] = dz * w
        d[:, 1] = dy * w
        return d

    # ---- ak_blink_L / R
    D["ak_blink_L"] = blink("L")
    D["ak_blink_R"] = blink("R")

    # ---- ak_brow_up
    d = zero()
    g = sm((z - 1.652) / 0.006) * sm((1.708 - z) / 0.030) * gate
    wb = ell(P, 0.0, BROW_Z + 0.004, 0.058, 0.026, 0.012) * g
    d[:, 2] = 0.0105 * wb
    d[:, 1] = -0.0010 * wb
    D["ak_brow_up"] = d

    # ---- ak_angry: alis turun & merapat, kelopak atas turun, sudut mulut turun
    d = zero()
    for sd in "LR":
        d += brow_inner_outer(sd, -0.0058, 0.0008, 0.0030)
        d += eye_squint(sd, 0.0022, 0.0008)
        d += corner(sd, -0.0030, -0.0008, 0.0005)
    d[:, 1] += -0.0006 * ell(P, 0.0, 1.640, 0.020, 0.012, 0.010) * gate     # glabela maju
    D["ak_angry"] = d

    # ---- ak_sad: ujung dalam alis naik, luar turun, sudut mulut turun, dagu naik
    d = zero()
    for sd in "LR":
        d += brow_inner_outer(sd, 0.0055, -0.0020, -0.0004)
        d += eye_squint(sd, 0.0016, 0.0)
        d += corner(sd, -0.0042, 0.0004, 0.0008)
    d[:, 2] += 0.0020 * ell(P, 0.0, 1.553, 0.022, 0.012, 0.014) * gate
    d[:, 1] += -0.0010 * ell(P, 0.0, 1.553, 0.022, 0.012, 0.014) * gate
    D["ak_sad"] = d

    # ---- ak_smile
    d = zero()
    for sd in "LR":
        d += corner(sd, 0.0075, 0.0070, 0.0035)
        d += cheek(sd, 0.0045, -0.0030)
        d += eye_squint(sd, 0.0, -0.0022)
    wl = ell(P, 0.0, LIP_Z, 0.034, 0.011, 0.012) * gate
    d[:, 0] += np.sign(P[:, 0]) * 0.0030 * wl
    D["ak_smile"] = d

    # ---- ak_mouth_open: rahang & bibir bawah turun; kantong ikut
    d = zero()
    wx = sm(1.0 - (np.abs(x) / 0.032) ** 1.4)
    wz = sm((z - 1.520) / 0.030)
    cx_, cz_ = zip(*LIP_CURVE)
    curve_z = np.interp(x, cx_, cz_)                       # z garis bibir di x tiap vertex
    below = (z < curve_z - 1e-5)                            # kulit di bawah garis bibir (bukan rim)
    wj = np.where(below & ~upper_pocket & ~lower_pocket, wx * wz, 0.0)
    wj = np.where(lower_rim, wx, wj)                        # rim bawah ikut kulit di bawahnya (tanpa selisih)
    wj = np.where(lower_back, wx * 0.85, wj) * gate
    d[:, 2] = -JAW_OPEN * wj
    d[:, 1] = 0.0035 * wj * sm((LIP_Z - z) / 0.020)
    d[:, 2] += 0.0008 * ell(P, 0.0, 1.592, 0.020, 0.008, 0.004) * gate * (~below & ~lower_pocket)      # bibir atas naik sedikit
    D["ak_mouth_open"] = d

    if "--debug" in sys.argv:
        for i in np.where(mk > 0)[0]:
            print("  celah mk=%d x=%+.4f z=%.4f  dz_open=%+.2fmm wj=%.2f" % (mk[i], P[i, 0], P[i, 2], d[i, 2] * 1000, wj[i]))
    # ---- ak_wince: mata terpejam kuat, alis turun, hidung berkerut, bibir atas naik, sudut ditarik
    d = zero()
    for sd in "LR":
        d += blink(sd, 0.80) * 0.9
        d += brow_inner_outer(sd, -0.0040, -0.0020, 0.0025)
        d += corner(sd, -0.0010, 0.0030, 0.0)
        d += cheek(sd, 0.0035, -0.0015)
    d[:, 2] += 0.0022 * ell(P, 0.0, 1.592, 0.022, 0.010, 0.004) * gate
    D["ak_wince"] = d

    for k, v in D.items():
        v[~gate] = 0.0
        v[P[:, 2] < 1.46] = 0.0
    return D


def main():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
    ob = bpy.data.objects["AK2_Source"]
    me = ob.data
    assert me.shape_keys is None, "v06 harus tanpa shape key"
    assert ob.matrix_world == ob.matrix_world.Identity(4), "AK2_Source harus identitas"
    snap = snapshot_normals(me)
    build_topology(me)
    fix_normals(ob, snap)

    mkv = np.zeros(len(me.vertices), dtype=np.int32)
    me.attributes["mk"].data.foreach_get("value", mkv)
    P = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", P)
    P = P.reshape(-1, 3)
    D = displacements(P, mkv)

    ob.shape_key_add(name="Basis", from_mix=False)
    for name in ("ak_blink_L", "ak_blink_R", "ak_smile", "ak_angry", "ak_mouth_open", "ak_brow_up", "ak_wince", "ak_sad"):
        kb = ob.shape_key_add(name=name, from_mix=False)
        tgt = (P + D[name]).astype(np.float32).ravel()
        kb.data.foreach_set("co", tgt)
        kb.value = 0.0
        mx = np.abs(D[name]).max() * 1000
        print(f"  {name:14s} verts>0.1mm: {int((np.abs(D[name]).max(axis=1) > 1e-4).sum()):5d}  maks {mx:.1f} mm")
    me.attributes.remove(me.attributes["mk"])
    me.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    print("Tersimpan:", BLEND_OUT, "| vertex", len(me.vertices), "| tris", sum(len(p.vertices) - 2 for p in me.polygons))


main()
