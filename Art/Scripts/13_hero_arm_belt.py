"""Iterasi 2 — hero modeling: LENGAN (bracer, sarung tangan berjari), SABUK, KAIN (depan, belakang, selendang).

Mengganti JD_Arm_*, JD_Belt_*, JD_Cloth_* proxy. Kain = strip berbobot rantai tulang + garis tepi/tengah emas (strip terpisah,
rantai sama). Detail ukiran/batik tetap kerja tekstur (Iterasi 4).
"""
import importlib
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jd_common as C
import jd_hero as Hh
import jd_skeleton as SK
importlib.reload(C)
importlib.reload(Hh)
importlib.reload(SK)

S = SK.SIDES
seg = SK.bone_segments()
rad = math.radians


def P(name, bm, coll, zone, slot, **kw):
    return C.finish_part(name, bm, coll, zone, slot, smooth="angle", **kw)


for ob in list(bpy.data.objects):
    if ob.type == "MESH" and ob.name.startswith(("JD_Arm_", "JD_Belt_", "JD_Cloth_")):
        bpy.data.objects.remove(ob, do_unlink=True)
made = []


def axis_diamond(bm, c, A, B, N, h, w, out, back):
    pts = [c + A * h / 2, c - A * h / 2, c + B * w / 2, c - B * w / 2, c + N * out, c - N * back]
    Hh.hull(bm, pts)


# ================================================================ LENGAN
for sd, s in S.items():
    L = sd.upper()
    d = SK.arm_dir(s)
    el, wr = seg[f"lowerarm_{sd}"][0], seg[f"hand_{sd}"][0]
    outward = Vector((s * math.cos(SK.ARM_ANGLE), 0, math.sin(SK.ARM_ANGLE)))
    sh = seg[f"upperarm_{sd}"][0]
    UW = {f"upperarm_{sd}": 0.7, f"upperarm_twist_01_{sd}": 0.3}
    LWT = {f"lowerarm_{sd}": 0.6, f"lowerarm_twist_01_{sd}": 0.4}
    B = d.cross(outward).normalized()

    def radial_ribbon(bm_, fn, a0, a1, uv_pts, width, gap):
        """Pita emas di permukaan fn, digeser radial menjauhi sumbu lengan a0->a1 (selalu ke luar)."""
        uvs = Hh.catmull([(u, v, 0) for u, v in uv_pts], 6)
        pts, nrm = [], []
        ax = (a1 - a0)
        for u, v, _ in uvs:
            q = Vector(fn(min(max(u, 0), 1), min(max(v, 0), 1)))
            t = max(0.0, min(1.0, (q - a0).dot(ax) / ax.length_squared))
            rdir = (q - (a0 + ax * t)).normalized()
            pts.append(q + rdir * gap)
            nrm.append(rdir)
        Hh.ribbon(bm_, pts, nrm, width)

    def merge_into(dst, src):
        tmp = bpy.data.meshes.new("_rb")
        src.to_mesh(tmp)
        src.free()
        dst.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)

    # ---- (revisi) pelat merah lengan atas: HANYA sisi luar, ujung bawah runcing ke siku, tepi emas
    ua0, ua1 = sh + d * 0.085, el + d * 0.005

    def upper(u, v):
        k = (u - 0.5) * 2
        t = v * (1 - 0.32 * abs(k) ** 1.3)              # sisi berhenti lebih awal -> ujung runcing di tengah luar
        ang = k * rad(64)
        r = 0.079 - 0.010 * t
        return ua0 + (ua1 - ua0) * t + outward * (r * math.cos(ang)) + B * (r * math.sin(ang))

    bm = bmesh.new()
    Hh.grid_surface(bm, upper, 8, 7)
    bm = Hh.harden(bm, thick=0.013, bevel=0.003, segs=2)
    made.append(P(f"JD_Arm_UpperPlate_{L}", bm, "05_Arm", "red", "Armor", weights=UW))
    bm = bmesh.new()
    for uv, w in (([(0, 0), (0, 0.6), (0.5, 1.0)], 0.013), ([(1, 0), (1, 0.6), (0.5, 1.0)], 0.013),
                  ([(0, 0), (0.5, 0), (1, 0)], 0.011)):
        rb = bmesh.new()
        radial_ribbon(rb, upper, ua0, ua1, uv, w, 0.008)
        merge_into(bm, Hh.harden(rb, thick=0.006, bevel=0.0015, segs=1))
    made.append(P(f"JD_Arm_UpperTrim_{L}", bm, "05_Arm", "gold", "Armor", weights=UW))

    # ---- (revisi) gauntlet emas BERSUDUT: membungkus luar-depan lengan bawah, meruncing seperti bilah MELEWATI siku
    g0, g1 = el, wr + d * 0.010

    def gaunt(u, v):
        k = (u - 0.5) * 2
        ak = abs(k)
        ts = -0.22 * max(0.0, 1 - ak / 0.55) ** 1.4        # ekstensi runcing ke atas siku di sisi luar (dikurangi: bentrok lame saat siku ditekuk)
        t = ts + (1 - ts) * v
        ang = k * rad(105)
        r = 0.064 + 0.018 * max(t, 0.0) ** 1.2 + (0.10 * (-t) if t < 0 else 0.0)   # melebar ke pergelangan; sirip mencuat
        return g0 + (g1 - g0) * t + outward * (r * math.cos(ang)) + B * (r * math.sin(ang))

    bm = bmesh.new()
    Hh.grid_surface(bm, gaunt, 12, 9)
    bm = Hh.harden(bm, thick=0.014, bevel=0.003, segs=2)
    made.append(P(f"JD_Arm_Bracer_{L}", bm, "05_Arm", "gold", "Armor", weights=LWT))

    def inset(u, v):
        q = Vector(gaunt(0.5 + (u - 0.5) * 0.50, 0.18 + 0.64 * v))
        ax = g1 - g0
        t = max(0.0, min(1.0, (q - g0).dot(ax) / ax.length_squared))
        return q + (q - (g0 + ax * t)).normalized() * 0.009

    bm = bmesh.new()                                                                      # panel merah di sisi luar gauntlet
    Hh.grid_surface(bm, inset, 5, 6)
    bm = Hh.harden(bm, thick=0.006, bevel=0.0015, segs=1)
    made.append(P(f"JD_Arm_BracerInset_{L}", bm, "05_Arm", "red", "Armor", weights=LWT))

    bm = bmesh.new()                                                                      # berlian emas di panel merah
    c = Vector(inset(0.5, 0.5))
    rd = (c - (g0 + (g1 - g0) * 0.5)).normalized()
    axis_diamond(bm, c + rd * 0.006, d, B, rd, 0.080, 0.040, 0.014, 0.004)
    bm = Hh.harden(bm, thick=0.0, bevel=0.002, segs=1)
    made.append(P(f"JD_Arm_BracerGem_{L}", bm, "05_Arm", "gold", "Armor", weights=LWT))

    bm = bmesh.new()                                                                      # manset emas: pita di tepi ujung gauntlet (bukan cincin mengambang)
    for uv, w in (([(0.0, 1.0), (0.5, 1.0), (1.0, 1.0)], 0.022), ([(0.0, 0.04), (0.25, 0.02), (0.75, 0.02), (1.0, 0.04)], 0.012)):
        rb = bmesh.new()
        radial_ribbon(rb, gaunt, g0, g1, uv, w, 0.009)
        merge_into(bm, Hh.harden(rb, thick=0.007, bevel=0.0015, segs=1))
    made.append(P(f"JD_Arm_BracerRim_{L}", bm, "05_Arm", "gold", "Armor", weights=LWT))

    # sarung tangan (kepalan): telapak + 4 jari melengkung + ibu jari
    front = Vector((0, -1, 0)) - Vector((0, -1, 0)).project(d)
    front.normalize()
    inw = Vector((-s, 0, 0))
    inw = (inw - inw.project(d) - inw.project(front)).normalized()
    base = wr + d * 0.012

    def Lc(lf, iw, fw):
        return base + front * lf + inw * iw + d * fw

    bm = bmesh.new()
    k = SK.HAND_SCALE
    corners = [Lc(lf * k, iw * k, fw * k) for lf in (-0.046, 0.046) for iw in (-0.027, 0.027) for fw in (0.0, 0.095)]
    Hh.hull(bm, corners)
    bm = Hh.harden(bm, thick=0.0, bevel=0.010, segs=2)
    made.append(P(f"JD_Arm_Glove_{L}", bm, "05_Arm", "black", "Body", bone=f"hand_{sd}"))   # telapak (kaku)
    for fn in SK.FINGERS:                                              # jari: satu objek per jari, berbobot 3 tulang
        bm = bmesh.new()
        r0 = (0.0150 if fn == "thumb" else 0.0128) * k
        Hh.tube(bm, Hh.catmull(SK.finger_joints(sd, fn), 3), lambda t, r0=r0: r0 - 0.0028 * t, n=6, caps=(True, True), up=front, t_layer=True)
        made.append(P(f"JD_Arm_Finger_{fn.title()}_{L}", bm, "05_Arm", "black", "Body", kind="strip",
                      bones=[f"{fn}_{i}_{sd}" for i in ("01", "02", "03")]))

# ================================================================ SABUK (revisi atas feedback: "sabuk masih kurang")
# Konsep: ikat kain merah TEBAL berlapis (dua lilitan, sedikit miring), pita emas atas/bawah/sambungan, kancing emas
# di sekeliling, gesper emas besar berpermata merah + pelat kecil di kiri-kanan, dua ujung simpul menggantung.
BELT_W = {"spine_01": 0.6, "pelvis": 0.4}
BRX, BRY = 0.140, 0.106          # revisi: pas badan (undersuit di pinggang ±0,13 × ±0,093 m + tebal sabuk)


def belt_wrap(z0, z1, rs, tilt, bulge=0.06):
    def fn(u, v):
        a = 2 * math.pi * u
        k = rs * (1 + bulge * math.sin(math.pi * v))
        return Vector((BRX * k * math.cos(a), BRY * k * math.sin(a), z0 + (z1 - z0) * v + tilt * math.cos(a)))
    return fn


wraps = [belt_wrap(1.035, 1.098, 1.00, 0.008), belt_wrap(1.080, 1.142, 1.04, -0.008)]   # di pinggang, bukan perut
for n_, fn in zip(("JD_Belt_Band", "JD_Belt_Band2"), wraps):
    bm = bmesh.new()
    Hh.grid_surface(bm, fn, 36, 4, wrap_u=True)
    bm = Hh.harden(bm, thick=0.016, bevel=0.003, segs=2)
    made.append(P(n_, bm, "06_Belt_Cloth", "red", "Armor", weights=BELT_W))

bm = bmesh.new()                                                       # pita emas di tepi lilitan
for fn, v, grow in ((wraps[0], 0.0, 0.010), (wraps[1], 0.0, 0.012), (wraps[1], 1.0, 0.010)):
    ring = [Vector(fn(k / 44, v)) for k in range(44)]
    ring = [Vector((q.x * (1 + grow / BRX), q.y * (1 + grow / BRY), q.z)) for q in ring]
    Hh.closed_tube(bm, ring, 0.0068, n=6)
made.append(P("JD_Belt_Rings", bm, "06_Belt_Cloth", "gold", "Armor", weights=BELT_W))

bm = bmesh.new()                                                       # kancing emas di sekeliling sabuk (lewati depan)
for k in range(14):
    a = 2 * math.pi * k / 14
    if abs(math.sin(a) + 1) < 0.30:                                   # dekat depan (sin ≈ -1): ada gesper
        continue
    q = Vector(wraps[1](k / 14, 0.5))
    rdir = Vector((q.x, q.y, 0)).normalized()
    c = q + rdir * 0.014
    tang = Vector((-rdir.y, rdir.x, 0))
    Hh.hull(bm, [c + tang * dx + Vector((0, 0, dz)) + rdir * dr for dx in (-0.012, 0.012) for dz in (-0.016, 0.016) for dr in (-0.006, 0.004)])
bm = Hh.harden(bm, thick=0.0, bevel=0.002, segs=1)
made.append(P("JD_Belt_Emb", bm, "06_Belt_Cloth", "gold", "Armor", weights=BELT_W))

bm = bmesh.new()                                                       # gesper: bingkai berlian emas besar + pelat samping
bc = Vector((0, -(BRY * 1.04 * 1.06) - 0.020, 1.090))
frame = [bc + Vector((0, 0, 0.060)), bc + Vector((0.050, 0, 0)), bc + Vector((0, 0, -0.060)), bc + Vector((-0.050, 0, 0))]
Hh.closed_tube(bm, frame, 0.011, n=6)
for sx in (-1, 1):                                                     # pelat samping menempel di permukaan sabuk
    q = Vector(wraps[1]((1.5 * math.pi + sx * 0.55) / (2 * math.pi), 0.5))
    rdir = Vector((q.x, q.y, 0)).normalized()
    tang = Vector((-rdir.y, rdir.x, 0))
    pc = q + rdir * 0.014
    Hh.hull(bm, [pc + tang * dx + rdir * dy + Vector((0, 0, dz)) for dx in (-0.016, 0.016) for dy in (-0.007, 0.006) for dz in (-0.024, 0.024)])
bm = Hh.harden(bm, thick=0.0, bevel=0.002, segs=1)
made.append(P("JD_Belt_Buckle", bm, "06_Belt_Cloth", "gold", "Armor", weights=BELT_W))
bm = bmesh.new()
Hh.diamond(bm, bc + Vector((0, -0.004, 0)), 0.074, 0.090, 0.018, 0.008)
bm = Hh.harden(bm, thick=0.0, bevel=0.0018, segs=1)
made.append(P("JD_Belt_BuckleInset", bm, "06_Belt_Cloth", "red", "Armor", weights=BELT_W))

bm = bmesh.new()                                                       # dua ujung simpul menggantung di bawah gesper
for sx in (-1, 1):
    Hh.plate3d(bm, [(sx * 0.012, bc.y + 0.004, 1.050), (sx * 0.042, bc.y + 0.006, 1.050), (sx * 0.064, bc.y + 0.010, 0.968), (sx * 0.034, bc.y + 0.006, 0.955)])
bm = Hh.harden(bm, thick=0.009, bevel=0.002, segs=1)
made.append(P("JD_Belt_Knot", bm, "06_Belt_Cloth", "red", "Armor", weights={"pelvis": 0.6, "spine_01": 0.4}))


# ================================================================ KAIN
def resample(points, factor):
    out = []
    for a, b in zip(points[:-1], points[1:]):
        for k in range(factor):
            out.append(a.lerp(b, k / factor))
    out.append(points[-1])
    return out


def cloth(name, line, widths, sides, chain, face_dir, fold=0.0, phase=0.0):
    n = len(line)
    line = [Vector(p) for p in line]
    for i, p in enumerate(line):                                       # lipatan halus
        t = i / (n - 1)
        p.y += fold * math.sin(t * 9.0 + phase) * (0.3 + t)
    tans = []
    for i in range(n):
        a, b = line[max(i - 1, 0)], line[min(i + 1, n - 1)]
        tans.append((b - a).normalized())
    norms = []
    for t_, sv in zip(tans, sides):
        nn = t_.cross(sv).normalized()
        norms.append(nn if nn.dot(face_dir) > 0 else -nn)
    bm = bmesh.new()
    C.add_strip(bm, line, widths, sides)
    made.append(P(f"JD_Cloth_{name}", bm, "06_Belt_Cloth", "red", "Cloth", kind="strip", chain=chain))
    # garis tepi emas (kiri/kanan) + garis tengah, sedikit di depan permukaan
    bm = bmesh.new()
    for sign in (+1, -1):
        cl, wl, sl = [], [], []
        for p, w, sv, nn in zip(line, widths, sides, norms):
            cl.append(p + sv * sign * max(w / 2 - 0.009, 0) + nn * 0.0025)
            wl.append(0.013 if w > 0.035 else 0.0)
            sl.append(sv)
        C.add_strip(bm, cl, wl, sl)
    cl, wl, sl = [], [], []
    for i, (p, w, sv, nn) in enumerate(zip(line, widths, sides, norms)):
        t = i / (n - 1)
        cl.append(p + nn * 0.0025)
        wl.append(0.011 if 0.04 < t < 0.88 else 0.0)
        sl.append(sv)
    C.add_strip(bm, cl, wl, sl)
    made.append(P(f"JD_Cloth_{name}Trim", bm, "06_Belt_Cloth", "gold", "Cloth", kind="strip", chain=chain))


def panel_widths(n, w0=0.20, amp=0.02, tip_from=0.80):
    ws = []
    for i in range(n):
        t = i / (n - 1)
        w = (w0 + amp * math.sin(math.pi * t)) * (1.0 if t < tip_from else max(0.0, (1 - t) / (1 - tip_from)))
        ws.append(w)
    ws[-1] = 0.0
    return ws


X = Vector((1, 0, 0))
line = resample(SK.cloth_points(SK.CLOTH_FRONT_Z, SK.CLOTH_FRONT_Y, SK.CLOTH_FRONT_DY), 4)
cloth("Front", line, panel_widths(len(line)), [X] * len(line), "cloth_front", Vector((0, -1, 0)), fold=0.004)
line = resample(SK.cloth_points(SK.CLOTH_BACK_Z, SK.CLOTH_BACK_Y, SK.CLOTH_BACK_DY), 4)
cloth("Back", line, panel_widths(len(line), w0=0.20), [X] * len(line), "cloth_back", Vector((0, 1, 0)), fold=0.004, phase=1.7)

for sd, s in S.items():
    line = resample(SK.scarf_points(s), 4)
    n = len(line)
    face_n = Vector((s * 0.75, -0.66, 0.0)).normalized()          # revisi: bidang selendang menghadap depan-luar (lebar dari depan & samping)
    sides = [(line[min(i + 1, n - 1)] - line[max(i - 1, 0)]).normalized().cross(face_n).normalized() for i in range(n)]
    widths = [0.145 * (1 - (abs(i / (n - 1) - 0.2) / 0.8) ** 1.1) if i < n - 1 else 0.0 for i in range(n)]   # revisi: lebih ramping (konsep)
    cloth(f"Scarf_{sd.upper()}", line, widths, sides, f"scarf_{sd}", face_n, fold=0.003, phase=0.6 * s)

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
tot = 0
for ob in made:
    t = C.tri_count(ob, dg)
    tot += t
    print(f"{ob.name:26s} {t:6d}")
print("LENGAN+SABUK+KAIN tris:", tot)
