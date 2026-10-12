"""Aksa Iterasi 1 — proxy pakaian + badan dari primitif (5 slot material), ter-skin ke armature Manny.

Jalankan di Blender setelah aksa_10_armature.py (aksa_v01_proxy.blend terbuka). Ukuran = konsep (docs/21) x K, dicocokkan
ke posisi tulang Manny (pose rest Manny, bukan pose konsep). Bagian: kepala/mata/rambut (kaku ke `head`), leher, lengan bawah
(kulit), kaos, jaket (depan terbuka) + lengan + kerah, celana + kantong kargo, sabuk + gesper, selendang (rantai sash_01..06),
kalung + liontin, sarung tangan + jari, boots. Nama objek: AK_<Bagian>[_L|_R]. Bobot: jarak ke segmen tulang (+ haluskan).
"""
import importlib
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C
import jd_common as JC
import jd_hero as HR

importlib.reload(C)
importlib.reload(HR)

arm = C.get_arm()
C.remove_parts()
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
_pts = C.sash_path()
for _i in range(C.SASH_N):
    _b = arm.data.edit_bones[f"sash_0{_i + 1}"]
    _b.head, _b.tail = _pts[_i], _pts[_i + 1]
bpy.ops.object.mode_set(mode="OBJECT")
SEG = C.bone_segments(arm)
bh = lambda n: C.bone_head(arm, n)  # noqa: E731
SIDES = {"L": +1, "R": -1}
parts = []


def sgn(x):
    return 1.0 if x >= 0 else -1.0


def loft(bm, secs, n=20, caps=(True, True)):
    """Loft penampang super-elips. secs = [(z, cx, cy, hw, hd, p)]; p=2 elips, >2 lebih kotak."""
    rings = []
    for z, cx, cy, hw, hd, p in secs:
        ring = []
        for k in range(n):
            a = 2 * math.pi * k / n
            c, s = math.cos(a), math.sin(a)
            ring.append(bm.verts.new((cx + hw * sgn(c) * abs(c) ** (2 / p), cy + hd * sgn(s) * abs(s) ** (2 / p), z)))
        rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    if caps[0]:
        bm.faces.new(rings[0][::-1])
    if caps[1]:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def new_bm():
    return bmesh.new()


NO_SHIFT = ("Head", "Eyes", "Hair", "Brows", "Neck", "Sleeve", "Forearm", "Glove", "Fingers", "Sash")   # ikut tulang / sudah bergeser


def part(name, bm, coll, zone, slot, kind="skin", bone=None, chain=None):
    o = C.finish_part("AK_" + name, bm, coll, zone, slot, kind=kind, bone=bone, chain=chain)
    if not name.startswith(NO_SHIFT):
        o.data.transform(Matrix.Translation((0.0, C.BODY_SHIFT_Y, 0.0)))
    parts.append(o)
    return o


def both(name, builder, coll, zone, slot, kind="skin", bone=None):
    """Bangun sisi kiri (s=+1) dan kanan (s=-1) dengan builder(s) -> bmesh."""
    for tag, s in SIDES.items():
        part(f"{name}_{tag}", builder(s), coll, zone, slot, kind, bone=(bone.format(s=tag.lower()) if bone else None))


# ================================================================== kepala (kaku ke `head`)
HC = Vector((0.0, -0.004, 1.667))
bm = new_bm()
JC.add_ico(bm, HC, (0.078, 0.098, 0.093), sub=3)
JC.add_prism(bm, (0, -0.092, 1.652), (0, -0.114, 1.638), 0.013, 0.006, seg=4)           # hidung (penanda arah)
for s in (1, -1):
    JC.add_ico(bm, (s * 0.077, 0.004, 1.664), (0.009, 0.017, 0.024), sub=1)              # telinga
part("Head", bm, "02_Head", "skin", "Skin", "rigid", bone="head")

bm = new_bm()
for s in (1, -1):
    JC.add_ico(bm, (s * 0.033, -0.0925, 1.673), (0.0105, 0.0105, 0.0105), sub=2)
part("Eyes", bm, "02_Head", "eye", "Eyes", "rigid", bone="head")

bm = new_bm()                                                                            # rambut: kubah + jambul
JC.add_ico(bm, (0.0, 0.012, 1.705), (0.0985, 0.112, 0.0985), sub=3)
cut = [v for v in bm.verts if v.co.z < 1.655 + 0.062 * min(max((-v.co.y + 0.01) / 0.09, 0.0), 1.0)]      # garis rambut miring
bmesh.ops.delete(bm, geom=cut, context="VERTS")
for ang, r, tilt in [(0, 0.0, 0.0), (45, 0.045, 0.3), (110, 0.05, 0.3), (170, 0.05, 0.3), (230, 0.05, 0.3), (290, 0.045, 0.3),
                     (340, 0.04, 0.3)]:
    a = math.radians(ang)
    base = Vector((r * math.cos(a), 0.012 + r * math.sin(a) * 1.1, 1.745 - r * 0.2))
    JC.add_prism(bm, base, base + Vector((math.cos(a) * tilt * 0.05, math.sin(a) * tilt * 0.05, 0.045)), 0.019, 0.004, seg=5)
part("Hair", bm, "03_Hair", "hair", "Hair", "rigid", bone="head")

bm = new_bm()                                                                            # alis
for s in (1, -1):
    JC.add_box(bm, (s * 0.034, -0.0935, 1.694), (0.042, 0.008, 0.009), rot=(0, 0, 0.12 * s))
part("Brows", bm, "03_Hair", "hair", "Hair", "rigid", bone="head")

# ================================================================== leher
bm = new_bm()
HR.tube(bm, [Vector(p) for p in [(0, 0.014, 1.50), (0, 0.008, 1.56), (0, 0.0, 1.625)]], 0.056, n=12, squash=(1.0, 0.95),
        caps=(False, False))
part("Neck", bm, "01_Body", "skin", "Skin", "skin")

# ================================================================== torso: kaos + jaket + kerah + sabuk
SHIRT = [(0.99, -0.03, -0.025, 0.178, 0.108, 2.6), (1.09, -0.03, -0.028, 0.176, 0.108, 2.6), (1.20, -0.03, -0.032, 0.180, 0.112, 2.6),
         (1.32, -0.03, -0.034, 0.185, 0.128, 2.5), (1.40, -0.03, -0.030, 0.188, 0.120, 2.4), (1.455, -0.03, -0.015, 0.165, 0.098, 2.2),
         (1.50, -0.03, 0.005, 0.085, 0.075, 2.0)]
SHIRT = [(z, cy, hw, hd, p) for z, _, cy, hw, hd, p in SHIRT]
bm = new_bm()
loft(bm, [(z, 0.0, cy, hw, hd, p) for z, cy, hw, hd, p in SHIRT])
part("Shirt", bm, "04_Top", "shirt", "Cloth", "skin")

JACKET = [(1.042, -0.028, 0.197, 0.123, 2.6), (1.09, -0.030, 0.198, 0.124, 2.6), (1.20, -0.033, 0.203, 0.136, 2.6),
          (1.32, -0.035, 0.209, 0.144, 2.5), (1.40, -0.031, 0.213, 0.135, 2.4), (1.452, -0.016, 0.200, 0.110, 2.2),
          (1.482, 0.000, 0.120, 0.090, 2.0), (1.50, 0.008, 0.095, 0.085, 2.0)]
bm = new_bm()
loft(bm, [(z, 0.0, cy, hw, hd, p) for z, cy, hw, hd, p in JACKET], caps=(False, False))
bm.faces.ensure_lookup_table()
drop = [f for f in bm.faces if f.calc_center_median().y < -0.10 and abs(f.calc_center_median().x) < 0.055
        and f.calc_center_median().z < 1.46]
bmesh.ops.delete(bm, geom=drop, context="FACES")
part("Jacket", bm, "04_Top", "jacket", "Cloth", "skin")

bm = new_bm()                                                                            # kerah berdiri (depan terbuka)
loft(bm, [(1.49, 0.0, 0.006, 0.090, 0.086, 2.0), (1.54, 0.0, 0.004, 0.096, 0.092, 2.0), (1.60, 0.0, 0.0, 0.108, 0.100, 2.0)],
     n=20, caps=(False, False))
bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().y < -0.05 and abs(f.calc_center_median().x) < 0.06],
                 context="FACES")
part("Collar", bm, "04_Top", "jacket", "Cloth", "skin")

bm = new_bm()                                                                            # sabuk
loft(bm, [(1.070, 0.0, -0.028, 0.188, 0.118, 2.7), (1.112, 0.0, -0.028, 0.188, 0.118, 2.7)])
JC.add_box(bm, (0, -0.1475, 1.091), (0.050, 0.014, 0.040))
part("Belt", bm, "05_Bottom", "belt", "Gear", "skin")
bm = new_bm()
JC.add_box(bm, (0, -0.1565, 1.091), (0.046, 0.006, 0.034))
part("Buckle", bm, "05_Bottom", "gold", "Gear", "skin")

# ================================================================== lengan: lengan jaket + manset, lengan bawah (kulit)
def sleeve(s):
    ua, la, hd_ = bh(f"upperarm_{'l' if s > 0 else 'r'}"), bh(f"lowerarm_{'l' if s > 0 else 'r'}"), bh(f"hand_{'l' if s > 0 else 'r'}")
    sh = Vector((s * 0.165, ua.y, 1.415))
    fa = (hd_ - la)
    cuff = la + fa * 0.30
    bm = new_bm()
    HR.tube(bm, [sh, ua, ua.lerp(la, 0.5), la, cuff], [0.060, 0.063, 0.059, 0.055, 0.057], n=12, caps=(False, False))
    HR.tube(bm, [cuff - fa.normalized() * 0.012, cuff + fa.normalized() * 0.026], [0.064, 0.064], n=12, caps=(True, True))     # gulungan manset
    return bm


def forearm(s):
    la, hd_ = bh(f"lowerarm_{'l' if s > 0 else 'r'}"), bh(f"hand_{'l' if s > 0 else 'r'}")
    fa = hd_ - la
    bm = new_bm()
    HR.tube(bm, [la + fa * 0.32, la + fa * 0.65, hd_ + fa.normalized() * 0.01], [0.044, 0.038, 0.034], n=10, caps=(False, False))
    return bm


both("Sleeve", sleeve, "04_Top", "jacket", "Cloth", "skin")
both("Forearm", forearm, "01_Body", "skin", "Skin", "skin")


def hand_frame(s):
    side = "l" if s > 0 else "r"
    la, hd_ = bh(f"lowerarm_{side}"), bh(f"hand_{side}")
    d = (hd_ - la).normalized()
    inw = Vector((-s, 0, 0))
    n_p = (inw - inw.project(d)).normalized()                  # normal telapak (menghadap paha)
    w = n_p.cross(d).normalized()                              # lebar tangan (d, w, n_p) tangan-kanan
    return hd_, d, n_p, w


def box_along(bm, p0, d, w, n_p, length, width, thick):
    """Balok dari p0 sepanjang d (panjang), lebar sepanjang w, tebal sepanjang n_p."""
    m = Matrix((d, w, n_p)).transposed().to_4x4()
    c = p0 + d * length / 2
    JC.add_box(bm, c, (length, width, thick), rot=m.to_euler())


def glove(s):
    hd_, d, n_p, w = hand_frame(s)
    bm = new_bm()
    box_along(bm, hd_ - d * 0.035, d, w, n_p, 0.115, 0.088, 0.044)                # manset + telapak
    JC.add_prism(bm, hd_ - d * 0.035, hd_ + d * 0.005, 0.047, 0.047, seg=10)       # manset bulat di pergelangan
    return bm


def fingers(s):
    hd_, d, n_p, w = hand_frame(s)
    bm = new_bm()
    box_along(bm, hd_ + d * 0.075, d, w, n_p, 0.075, 0.080, 0.026)
    th = (hd_ + d * 0.03 + Vector((0, -0.045, 0)) - n_p * 0.01)
    JC.add_prism(bm, th, th + (d * 0.8 + Vector((0, -0.55, 0))).normalized() * 0.075, 0.015, 0.011, seg=6)
    return bm


both("Glove", glove, "06_Accessory", "gloves", "Gear", "rigid", bone="hand_{s}")
both("Fingers", fingers, "01_Body", "skin", "Skin", "rigid", bone="hand_{s}")

# ================================================================== celana + kantong kargo
bm = new_bm()
loft(bm, [(1.100, 0.0, -0.028, 0.180, 0.110, 2.6), (1.00, 0.0, -0.027, 0.186, 0.114, 2.6), (0.92, 0.0, -0.026, 0.190, 0.118, 2.5),
          (0.86, 0.0, -0.025, 0.172, 0.112, 2.3)], caps=(False, True))
part("Pelvis", bm, "05_Bottom", "pants", "Cloth", "skin")


def pants_leg(s):
    side = "l" if s > 0 else "r"
    th, ca, fo = bh(f"thigh_{side}"), bh(f"calf_{side}"), bh(f"foot_{side}")
    path = [Vector((s * 0.088, th.y, 0.99)), th, th.lerp(ca, 0.45), ca, ca.lerp(fo, 0.55), Vector((fo.x - s * 0.002, fo.y + 0.004, 0.245))]
    bm = new_bm()
    HR.tube(bm, path, [0.098, 0.097, 0.088, 0.073, 0.069, 0.068], n=14, squash=(1.0, 1.12), caps=(False, True))
    return bm


def pocket(s):
    bm = new_bm()
    JC.add_box(bm, (s * 0.214, -0.028, 0.655), (0.052, 0.125, 0.17))
    JC.add_box(bm, (s * 0.214, -0.028, 0.745), (0.058, 0.130, 0.018))                # tutup kantong
    return bm


both("PantsLeg", pants_leg, "05_Bottom", "pants", "Cloth", "skin")
both("Pocket", pocket, "05_Bottom", "pants", "Cloth", "rigid", bone="thigh_{s}")

# ================================================================== selendang (rantai sash_01..06)
sp = C.sash_path()
widths = [0.045, 0.060, 0.085, 0.095, 0.098, 0.090, 0.0]
sides = []
for i, p in enumerate(sp):
    T = (sp[min(i + 1, len(sp) - 1)] - sp[max(i - 1, 0)]).normalized()
    nrm = Vector((p.x - 0.105, p.y - (C.BODY_SHIFT_Y - 0.025), 0)).normalized()
    sides.append(T.cross(nrm).normalized())
bm = new_bm()
JC.add_strip(bm, sp, widths, sides, t_layer_name="AK_t")
part("Sash", bm, "06_Accessory", "batik", "Cloth", "strip", chain="sash")

# ================================================================== kalung
bm = new_bm()
chain_pts = HR.catmull([(0.052, -0.092, 1.512), (0.034, -0.128, 1.435), (0.0, -0.1545, 1.335), (-0.034, -0.128, 1.435),
                        (-0.052, -0.092, 1.512)], spp=4)
HR.tube(bm, chain_pts, 0.0024, n=4, caps=(True, True))
part("Chain", bm, "06_Accessory", "gold", "Gear", "rigid", bone="spine_05")
bm = new_bm()
JC.add_box(bm, (0, -0.1585, 1.312), (0.024, 0.009, 0.044), rot=(0, 0, 0))
part("Pendant", bm, "06_Accessory", "stone", "Gear", "rigid", bone="spine_05")

# ================================================================== boots
def boot_shaft(s):
    side = "l" if s > 0 else "r"
    fo = bh(f"foot_{side}")
    bm = new_bm()
    HR.tube(bm, [Vector((fo.x, fo.y + 0.004, 0.06)), Vector((fo.x, fo.y + 0.002, 0.16)), Vector((fo.x - s * 0.002, fo.y + 0.004, 0.272))],
            [0.060, 0.058, 0.058], n=14, squash=(1.0, 1.0), caps=(False, True))
    HR.tube(bm, [Vector((fo.x - s * 0.002, fo.y + 0.004, 0.246)), Vector((fo.x - s * 0.002, fo.y + 0.004, 0.272))], [0.066, 0.066], n=14,
            caps=(True, True))                                                     # strap + gesper di bibir
    return bm


def boot_foot(s):
    side = "l" if s > 0 else "r"
    fo, bl = bh(f"foot_{side}"), bh(f"ball_{side}")
    ax = Vector((bl.x - fo.x, bl.y - fo.y, 0)).normalized()                       # arah telapak (sedikit keluar)
    lat = Vector((-ax.y, ax.x, 0)).normalized()
    if lat.x * s < 0:
        lat = -lat
    o = Vector((fo.x, fo.y, 0))

    def P(f, l, z):                                                                # f: maju dari tumit-poros, l: lateral
        return o + ax * f + lat * l + Vector((0, 0, z))

    pts = []
    for f, wl, zt in [(-0.095, 0.050, 0.075), (-0.02, 0.058, 0.098), (0.06, 0.060, 0.085), (0.12, 0.056, 0.070), (0.20, 0.044, 0.050),
                      (0.225, 0.030, 0.034)]:
        pts += [P(f, wl, 0.0), P(f, -wl, 0.0), P(f, wl * 0.92, zt), P(f, -wl * 0.92, zt)]
    bm = new_bm()
    JC.add_hull(bm, pts)
    return bm


both("BootShaft", boot_shaft, "07_Shoes", "boots", "Gear", "skin")
both("BootFoot", boot_foot, "07_Shoes", "boots", "Gear", "rigid", bone="foot_{s}")

# ================================================================== bobot + modifier
def weights_for(obj):
    kind = obj["ak_kind"]
    n = len(obj.data.vertices)
    if kind == "rigid":
        set_ = {obj["ak_bone"]: {i: 1.0 for i in range(n)}}
        C.set_weights(obj, set_)
        return
    if kind == "strip":
        chain = [f"{obj['ak_chain']}_0{i}" for i in range(1, C.SASH_N + 1)]
        nb = len(chain)
        tl = obj.data.attributes["AK_t"].data
        assign = {b: {} for b in chain}
        for v in obj.data.vertices:
            u = tl[v.index].value * nb - 0.5
            if u <= 0:
                assign[chain[0]][v.index] = 1.0
            elif u >= nb - 1:
                assign[chain[-1]][v.index] = 1.0
            else:
                i0 = int(u)
                f = u - i0
                assign[chain[i0]][v.index] = 1.0 - f
                assign[chain[i0 + 1]][v.index] = f
        C.set_weights(obj, assign)
        return
    name = obj.name
    spine = ["pelvis"] + [f"spine_0{i}" for i in range(1, 6)]
    if "Neck" in name:
        bones = ["spine_05", "neck_01", "neck_02", "head"]
    elif any(k in name for k in ("Shirt", "Jacket", "Collar", "Belt", "Buckle")):
        bones = spine + ["neck_01", "neck_02", "clavicle_l", "clavicle_r"]
    elif "Sleeve" in name or "Forearm" in name:
        s = "l" if name.endswith("_L") else "r"
        bones = [f"clavicle_{s}", f"upperarm_{s}", f"lowerarm_{s}", f"hand_{s}", "spine_05", "spine_04"]
    elif "Pelvis" in name:
        bones = ["pelvis", "spine_01", "spine_02", "thigh_l", "thigh_r"]
    elif "PantsLeg" in name:
        s = "l" if name.endswith("_L") else "r"
        bones = ["pelvis", "spine_01", f"thigh_{s}", f"calf_{s}", f"foot_{s}"]
    elif "BootShaft" in name:
        s = "l" if name.endswith("_L") else "r"
        bones = [f"calf_{s}", f"foot_{s}", f"ball_{s}"]
    else:
        raise RuntimeError(f"tidak ada aturan bobot untuk {name}")
    C.distance_weights(obj, SEG, bones, k=3, power=4.0)
    C.smooth_weights(obj, iters=2, factor=0.5)


report = []
for obj in parts:
    weights_for(obj)
    mx, unw = C.clean_weights(obj)
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    mod.use_vertex_groups = True
    obj.parent = arm
    report.append((obj.name, C.tri_count(obj), mx, unw))
tot = sum(r[1] for r in report)
for r in report:
    print(f"  {r[0]:18s} tris {r[1]:5d}  influence maks {r[2]}  tanpa bobot {r[3]}")
print("TOTAL tris:", tot, "| bagian:", len(parts), "| slot:", sorted({o['ak_slot'] for o in parts}))

bpy.ops.wm.save_mainfile()
print("Disimpan:", bpy.data.filepath)
