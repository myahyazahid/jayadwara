"""Aksa Iterasi 3 — pakaian hero + tangan, menggantikan proxy pakaian Iterasi 1.

Jalankan di Blender (MCP: exec(open(path).read())) dengan aksa_v03_mpfb.blend atau aksa_v04_outfit.blend terbuka.
Membangun (semua ter-skin ke armature Manny):
  tangan + lengan bawah (metaball mengikuti tulang jari Manny; tiap jari terpisah agar tidak menyatu), sarung tangan tanpa jari,
  kaos (leher bulat mengikuti leher MPFB), jaket terbuka (tebal, pita pinggang, kantong dada + kancing emas, pita emas bahu,
  ritsleting emas di tepi depan, emblem lengan & punggung), kerah berdiri (luar navy, lapisan dalam batik), lengan jaket + manset
  gulung, celana kargo (kerutan di atas boots) + kantong kargo bertutup + strap paha bergesper, sabuk + gesper berbingkai + tali
  sabuk, selendang batik (simpul + pita menempel paha), kalung (rantai + pecahan batu berbingkai), boots bertali (sol tebal + trim
  emas, kait emas, strap + gesper).
Lalu: dorong-keluar antar lapisan (tanpa tembus), bobot per bagian, simpan aksa_v04_outfit.blend.
Ukuran = proxy Iterasi 1 (sudah dicocokkan ke konsep, IoU badan 0,80–0,88) dengan detail konsep (docs/21 bagian 4).
"""
import importlib
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_cloth as K
import ak_common as C
import jd_common as JC
import jd_hero as HR

for m in (C, K, HR):
    importlib.reload(m)

assert any(k in bpy.data.filepath for k in ("aksa_v03", "aksa_v04")), "buka aksa_v03_mpfb.blend atau aksa_v04_outfit.blend"
OUT = C.ART / "Blender" / "aksa_v04_outfit.blend"
SY = C.BODY_SHIFT_Y
arm = C.get_arm()
bh = lambda n: C.bone_head(arm, n)  # noqa: E731
SIDES = {"L": 1, "R": -1}
FINGERS = ["index", "middle", "ring", "pinky"]

PROXY = ("AK_Shirt", "AK_Jacket", "AK_Collar", "AK_Sleeve", "AK_Forearm", "AK_Glove", "AK_Fingers", "AK_Pelvis", "AK_PantsLeg",
         "AK_Pocket", "AK_Belt", "AK_Buckle", "AK_Sash", "AK_Chain", "AK_Pendant", "AK_BootShaft", "AK_BootFoot")
NEW = ("AK_Hand", "AK_Finger", "AK_GloveNew", "AK_Tee", "AK_Coat", "AK_CoatDetail", "AK_CoatGold", "AK_CollarOut", "AK_CollarLining",
       "AK_CoatSleeve", "AK_Trousers", "AK_Cargo", "AK_Strap", "AK_BeltNew", "AK_BeltGold", "AK_SashNew", "AK_Necklace", "AK_Stone",
       "AK_Boot", "AK_Sole", "AK_BootGold", "AK_Lace")
for ob in list(bpy.data.objects):
    if ob.type == "MESH" and ob.name.startswith(PROXY + NEW):
        bpy.data.objects.remove(ob, do_unlink=True)
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)

# tulang jari ikut deform
for b in arm.data.bones:
    if any(f in b.name for f in FINGERS + ["thumb"]) and not b.name.startswith("ik_"):
        b.use_deform = True

parts = []


def part(name, bm, coll, zone, slot, bones=None, rigid=None, chain=None, smooth=True):
    o = C.finish_part(name, bm, coll, zone, slot, kind="rigid" if rigid else ("strip" if chain else "skin"), bone=rigid,
                      chain=chain, smooth=smooth)
    o["ak_bones"] = ",".join(bones) if bones else ""
    parts.append(o)
    return o


def spine(extra=()):
    return ["pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "clavicle_l", "clavicle_r"] + list(extra)


# ================================================================== segmen tulang (+ jari)
SEG = C.bone_segments(arm)
for s in "lr":
    for f in FINGERS:
        chain = [f"{f}_metacarpal_{s}", f"{f}_01_{s}", f"{f}_02_{s}", f"{f}_03_{s}"]
        for a, b in zip(chain[:-1], chain[1:]):
            SEG[a] = (bh(a), bh(b))
        d = bh(chain[-1]) - bh(chain[-2])
        SEG[chain[-1]] = (bh(chain[-1]), bh(chain[-1]) + d.normalized() * d.length * 0.85)
    th = [f"thumb_01_{s}", f"thumb_02_{s}", f"thumb_03_{s}"]
    for a, b in zip(th[:-1], th[1:]):
        SEG[a] = (bh(a), bh(b))
    d = bh(th[-1]) - bh(th[-2])
    SEG[th[-1]] = (bh(th[-1]), bh(th[-1]) + d.normalized() * d.length * 0.95)


def tip(s, f):
    return SEG[f"{f}_03_{s}"][1]


# ================================================================== 1. tangan + lengan bawah (metaball)
FR = {"index": (0.0080, 0.0074, 0.0068), "middle": (0.0083, 0.0076, 0.0070), "ring": (0.0079, 0.0072, 0.0066),
      "pinky": (0.0070, 0.0064, 0.0059), "thumb": (0.0105, 0.0092, 0.0085)}
for tag, sg in SIDES.items():
    s = tag.lower()
    la, hd = bh(f"lowerarm_{s}"), bh(f"hand_{s}")
    fa = hd - la
    els = [(la + fa * 0.45, fa, fa.length * 0.17, 0.037), (la + fa * 0.80, fa, fa.length * 0.15, 0.031), (hd, fa, 0.0, 0.025)]
    for f, r in (("index", 0.0105), ("middle", 0.0108), ("ring", 0.0100), ("pinky", 0.0090)):
        a, b = bh(f"{f}_metacarpal_{s}"), bh(f"{f}_01_{s}")
        els.append(((a + b) / 2, b - a, (b - a).length / 2, r))
    a, b = bh(f"thumb_01_{s}"), bh(f"thumb_02_{s}")
    els.append(((a + b) / 2, b - a, (b - a).length / 2, 0.0125))
    bm = bmesh.new()
    K.mesh_into_bm(bm, K.meta_mesh(f"hand_{s}", els, 0.0024, decimate=0.35))
    part(f"AK_Hand_{tag}", bm, "01_Body", "skin", "Skin",
         bones=[f"lowerarm_{s}", f"hand_{s}", f"thumb_01_{s}"] + [f"{f}_metacarpal_{s}" for f in FINGERS])
    for f in FINGERS + ["thumb"]:
        names = [f"{f}_01_{s}", f"{f}_02_{s}", f"{f}_03_{s}"] if f != "thumb" else [f"thumb_02_{s}", f"thumb_03_{s}"]
        rr = FR[f] if f != "thumb" else FR["thumb"][1:]
        els = []
        for n, r in zip(names, rr):
            a, b = SEG[n]
            els.append(((a + b) / 2, b - a, (b - a).length / 2, r))
        bm = bmesh.new()
        K.mesh_into_bm(bm, K.meta_mesh(f"fing_{f}_{s}", els, 0.0016, decimate=0.30))
        part(f"AK_Finger_{f}_{tag}", bm, "01_Body", "skin", "Skin", bones=[f"hand_{s}"] + names)

# ================================================================== 2. sarung tangan tanpa jari (metaball)
for tag, sg in SIDES.items():
    s = tag.lower()
    la, hd = bh(f"lowerarm_{s}"), bh(f"hand_{s}")
    fa = (hd - la).normalized()
    els = [(hd - fa * 0.012, fa, 0.016, 0.0285)]
    for f, r in (("index", 0.0136), ("middle", 0.0139), ("ring", 0.0131), ("pinky", 0.0120)):
        a, b, c = bh(f"{f}_metacarpal_{s}"), bh(f"{f}_01_{s}"), bh(f"{f}_02_{s}")
        els.append(((a + b) / 2, b - a, (b - a).length / 2, r))
        e = b + (c - b) * 0.42
        els.append(((b + e) / 2, e - b, (e - b).length / 2, FR[f][0] + 0.0026))
    a, b, c = bh(f"thumb_01_{s}"), bh(f"thumb_02_{s}"), bh(f"thumb_03_{s}")
    els.append(((a + b) / 2, b - a, (b - a).length / 2, 0.0145))
    e = b + (c - b) * 0.45
    els.append(((b + e) / 2, e - b, (e - b).length / 2, FR["thumb"][1] + 0.0020))
    bm = bmesh.new()
    K.mesh_into_bm(bm, K.meta_mesh(f"glove_{s}", els, 0.0026, decimate=0.30))
    HR.tube(bm, [hd - fa * 0.030, hd - fa * 0.016], [0.0335, 0.0335], n=16, caps=(True, True))          # strap pergelangan
    part(f"AK_GloveNew_{tag}", bm, "06_Accessory", "gloves", "Gear",
         bones=[f"lowerarm_{s}", f"hand_{s}", f"thumb_01_{s}", f"thumb_02_{s}"] + [f"{f}_metacarpal_{s}" for f in FINGERS] + [f"{f}_01_{s}" for f in FINGERS])

# ================================================================== 3. kaos (leher bulat mengikuti leher MPFB)
head = bpy.data.objects["AK_Head"]
neck_pts = [v.co for v in head.data.vertices if 1.505 < v.co.z < 1.520]
nc = sum(neck_pts, Vector()) / len(neck_pts)
n_hw = max(abs(p.x - nc.x) for p in neck_pts) + 0.004
n_hd = max(abs(p.y - nc.y) for p in neck_pts) + 0.004
SHIRT = [(0.99, -0.025, 0.178, 0.108, 2.6), (1.09, -0.028, 0.176, 0.108, 2.6), (1.20, -0.032, 0.180, 0.112, 2.6),
         (1.32, -0.034, 0.185, 0.128, 2.5), (1.40, -0.030, 0.188, 0.120, 2.4), (1.455, -0.015, 0.165, 0.098, 2.2),
         (1.492, 0.000, 0.105, 0.082, 2.1)]
secs = [(z, 0.0, cy + SY, hw, hd, p, None) for z, cy, hw, hd, p in SHIRT] + [(1.512, nc.x, nc.y, n_hw, n_hd, 2.0, None)]
bm = bmesh.new()
K.loft(bm, secs, n=40, caps=(True, False))
HR.closed_tube(bm, [Vector((nc.x + n_hw * math.cos(a), nc.y + n_hd * math.sin(a), 1.512)) for a in [2 * math.pi * k / 40 for k in range(40)]],
               0.0035, n=6)                                                                                   # rib leher
tee = part("AK_Tee", bm, "04_Top", "shirt", "Cloth", bones=spine(["neck_02"]))

# ================================================================== 4. jaket (terbuka, tebal)
JK = [(1.042, -0.028, 0.199, 0.125, 2.6, 0.062), (1.09, -0.030, 0.200, 0.126, 2.6, 0.057), (1.20, -0.033, 0.205, 0.138, 2.6, 0.052),
      (1.32, -0.035, 0.211, 0.146, 2.5, 0.050), (1.40, -0.031, 0.215, 0.137, 2.4, 0.050), (1.452, -0.016, 0.202, 0.112, 2.2, 0.048),
      (1.482, 0.000, 0.122, 0.092, 2.0, 0.046), (1.500, 0.008, 0.097, 0.087, 2.0, 0.045)]


def interp_secs(rows, sub=3):
    out = []
    for a, b in zip(rows[:-1], rows[1:]):
        for k in range(sub):
            t = k / sub
            out.append(tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a))))
    out.append(rows[-1])
    return out


secs = [(z, 0.0, cy + SY, hw, hd, p, ex) for z, cy, hw, hd, p, ex in interp_secs(JK, 3)]
bm = bmesh.new()
K.loft(bm, secs[1:], n=56, open_front=True)
K.solidify(bm, 0.0045)
coat = part("AK_Coat", bm, "04_Top", "jacket", "Cloth", bones=spine())                     # bahu ikut clavicle, bukan lengan atas
# pita pinggang
bm = bmesh.new()
K.loft(bm, [(z, 0.0, cy + SY, hw + 0.003, hd + 0.003, p, ex) for z, cy, hw, hd, p, ex in interp_secs(JK[:2], 2)[:2]], n=56, open_front=True)
K.solidify(bm, 0.006)
part("AK_CoatDetail_band", bm, "04_Top", "jacket", "Cloth", bones=spine())
coat_bvh = K.bvh_of(coat)
# kantong dada + tutup + kancing emas, emblem
bm_d, bm_g = bmesh.new(), bmesh.new()
for sg in (1, -1):
    c = Vector((sg * 0.098, 0, 1.305))
    K.patch_on(bm_d, coat_bvh, c, (1, 0, 0), (0, 0, 1), 0.060, 0.062, (0, 1, 0), 0.0055, 5, 5, thick=0.003)
    K.patch_on(bm_d, coat_bvh, c + Vector((0, 0, 0.037)), (1, 0, 0), (0, 0, 1), 0.066, 0.024, (0, 1, 0), 0.0090, 5, 2, thick=0.0035)
    for dx in (-0.018, 0.018):
        loc, nrm = K.ray(coat_bvh, (sg * 0.098 + dx, -0.4, 1.338), (0, 1, 0))
        if loc is not None:
            JC.add_prism(bm_g, loc + nrm * 0.008, loc + nrm * 0.0115, 0.0045, 0.0042, seg=10)
part("AK_CoatDetail_pockets", bm_d, "04_Top", "jacket", "Cloth", bones=spine())
# ritsleting emas di kedua tepi depan + pita emas bahu + emblem punggung
for sg in (1, -1):
    pts = [Vector((sg * (ex + 0.002), 0, z)) for z, cy, hw, hd, p, ex in interp_secs(JK, 3)[1:]]
    pts = K.curve_on(coat_bvh, pts, (0, 1, 0), 0.0)
    HR.tube(bm_g, pts, 0.0024, n=5, caps=(True, True))
    sh = [Vector((sg * x, 0, z)) for x, z in [(0.072, 1.494), (0.110, 1.478), (0.150, 1.462), (0.188, 1.448)]]
    sh = K.curve_on(coat_bvh, sh, lambda p: (0, 0, -1), 0.0028)
    HR.tube(bm_g, sh, 0.0018, n=5, caps=(True, True))
ec = Vector((0, 0.3, 1.385))
petals = []
for k in range(5):                                                     # teratau + sinar (bukan garuda, D6)
    a = math.radians(-50 + 25 * k)
    petals.append([ec + Vector((math.sin(a) * r, 0, math.cos(a) * r)) for r in (0.008, 0.026 if k == 2 else 0.020)])
for a_, b_ in petals:
    pa = K.curve_on(coat_bvh, [a_, b_], (0, -1, 0), 0.003)
    HR.tube(bm_g, pa, [0.0055, 0.0005], n=6, caps=(True, False))
pc = K.curve_on(coat_bvh, [ec + Vector((0, 0, -0.010)), ec + Vector((0, 0, 0.004))], (0, -1, 0), 0.003)
HR.tube(bm_g, pc, [0.009, 0.007], n=8, caps=(True, True))
part("AK_CoatGold", bm_g, "04_Top", "gold", "Gear", bones=spine(["upperarm_l", "upperarm_r"]))

# ================================================================== 5. kerah berdiri (luar navy, lapisan batik)
CL = [(1.488, 0.008, 0.094, 0.088, 2.0, 0.044), (1.540, 0.005, 0.100, 0.094, 2.0, 0.050), (1.600, 0.001, 0.112, 0.103, 2.0, 0.066)]
bm = bmesh.new()
K.loft(bm, [(z, 0.0, cy + SY, hw, hd, p, ex) for z, cy, hw, hd, p, ex in interp_secs(CL, 4)], n=48, open_front=True)
K.solidify(bm, 0.0035)
part("AK_CollarOut", bm, "04_Top", "jacket", "Cloth", bones=["spine_05", "neck_01", "clavicle_l", "clavicle_r"])
bm = bmesh.new()
K.loft(bm, [(z, 0.0, cy + SY, hw - 0.0042, hd - 0.0042, p, ex + 0.002) for z, cy, hw, hd, p, ex in interp_secs(CL, 4)], n=48, open_front=True)
bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
part("AK_CollarLining", bm, "04_Top", "batik", "Cloth", bones=["spine_05", "neck_01", "clavicle_l", "clavicle_r"])

# ================================================================== 6. lengan jaket + manset gulung
for tag, sg in SIDES.items():
    s = tag.lower()
    ua, la, hd = bh(f"upperarm_{s}"), bh(f"lowerarm_{s}"), bh(f"hand_{s}")
    fa = hd - la
    sh = Vector((sg * 0.160, ua.y, 1.398))
    cuff = la + fa * 0.30
    path = HR.catmull([sh, ua, ua.lerp(la, 0.5), la, cuff], spp=4)
    rad = lambda t: 0.054 + 0.008 * math.sin(math.pi * min(t * 1.6, 1.0)) - 0.002 * t   # noqa: E731
    bm = bmesh.new()
    HR.tube(bm, path, rad, n=18, caps=(False, False))
    K.solidify(bm, 0.003)
    fd = fa.normalized()
    for k, (t0, r) in enumerate([(-0.010, 0.0605), (0.004, 0.0640), (0.018, 0.0625)]):            # gulungan berlapis
        HR.tube(bm, [cuff + fd * t0, cuff + fd * (t0 + 0.013)], [r, r], n=18, caps=(True, True))
    part(f"AK_CoatSleeve_{tag}", bm, "04_Top", "jacket", "Cloth",
         bones=[f"clavicle_{s}", f"upperarm_{s}", f"lowerarm_{s}", "spine_05", "spine_04"])
    bm_g = bmesh.new()
    up = Vector((0, 0, 1))
    side = fd.cross(up).normalized()
    for a in (0.0, math.pi):                                                                      # batang jahit emas di manset
        c = cuff + fd * 0.011 + (side * math.cos(a) + up * math.sin(a)) * 0.066
        JC.add_box(bm_g, c, (0.004, 0.004, 0.018), rot=fd.to_track_quat("Z", "Y").to_euler())
    m = ua.lerp(la, 0.30)
    outw = Vector((sg, 0, 0))
    for k in range(3):                                                                            # emblem lengan atas (kuncup)
        a = math.radians(-30 + 30 * k)
        d = (up * math.cos(a) + fd * 0.0 + Vector((0, math.sin(a), 0))).normalized()
        HR.tube(bm_g, [m + outw * 0.060 + Vector((0, 0, -0.010)), m + outw * 0.061 + d * (0.020 if k == 1 else 0.015)], [0.005, 0.0004], n=6)
    part(f"AK_CoatGold_sleeve_{tag}", bm_g, "04_Top", "gold", "Gear", bones=[f"upperarm_{s}", f"lowerarm_{s}"])

# ================================================================== 7. celana kargo
bm = bmesh.new()
K.loft(bm, [(1.100, 0.0, -0.028 + SY, 0.180, 0.110, 2.6, None), (1.00, 0.0, -0.027 + SY, 0.186, 0.114, 2.6, None),
            (0.92, 0.0, -0.026 + SY, 0.190, 0.118, 2.5, None), (0.86, 0.0, -0.025 + SY, 0.172, 0.112, 2.3, None)], n=40, caps=(False, True))
part("AK_Trousers_pelvis", bm, "05_Bottom", "pants", "Cloth", bones=["pelvis", "spine_01", "spine_02", "thigh_l", "thigh_r"])
leg_objs = {}
for tag, sg in SIDES.items():
    s = tag.lower()
    th, ca, fo = bh(f"thigh_{s}"), bh(f"calf_{s}"), bh(f"foot_{s}")
    ctrl = [Vector((sg * 0.088, th.y, 0.99)), th, th.lerp(ca, 0.45), ca, ca.lerp(fo, 0.55), Vector((fo.x - sg * 0.001, fo.y + 0.008, 0.245))]
    ctrl = [p + Vector((0, SY, 0)) for p in ctrl]
    path = HR.catmull(ctrl, spp=5)
    base = [0.098, 0.097, 0.088, 0.073, 0.069, 0.069]

    def radius(t, base=base):
        x = t * (len(base) - 1)
        i = min(int(x), len(base) - 2)
        r = base[i] + (base[i + 1] - base[i]) * (x - i)
        r += 0.004 * math.exp(-((t - 0.62) / 0.05) ** 2)                                         # lutut sedikit longgar
        if t > 0.80:                                                                              # kerutan di atas boots
            r += 0.0045 * (0.5 + 0.5 * math.sin((t - 0.80) * 110)) * smooth01(t)
        return r

    smooth01 = lambda t: K.smooth(0.80, 0.86, t)  # noqa: E731
    bm = bmesh.new()
    HR.tube(bm, path, radius, n=22, squash=(1.0, 1.12), caps=(False, True))
    leg_objs[tag] = part(f"AK_Trousers_leg_{tag}", bm, "05_Bottom", "pants", "Cloth",
                         bones=["pelvis", "spine_01", f"thigh_{s}", f"calf_{s}", f"foot_{s}"])
# kantong kargo + strap paha
for tag, sg in SIDES.items():
    s = tag.lower()
    lbvh = K.bvh_of(leg_objs[tag])
    bm = bmesh.new()
    K.patch_on(bm, lbvh, Vector((sg * 0.25, -0.028 + SY, 0.650)), (0, 1, 0), (0, 0, 1), 0.110, 0.150, (-sg, 0, 0), 0.020, 6, 7, thick=0.017)
    K.patch_on(bm, lbvh, Vector((sg * 0.25, -0.028 + SY, 0.738)), (0, 1, 0), (0, 0, 1), 0.120, 0.034, (-sg, 0, 0), 0.0235, 6, 2, thick=0.004)
    part(f"AK_Cargo_{tag}", bm, "05_Bottom", "pants", "Cloth", bones=[f"thigh_{s}"])
    th, ca = bh(f"thigh_{s}"), bh(f"calf_{s}")
    zc = 0.705
    ctr = th.lerp(ca, (th.z - zc) / (th.z - ca.z)) + Vector((0, SY, 0))
    ring = []
    for k in range(28):
        a = 2 * math.pi * k / 28
        d = Vector((math.cos(a), math.sin(a), 0))
        loc, nrm = K.ray(lbvh, Vector((ctr.x, ctr.y, zc)) + d * 0.3, -d, 0.4)
        ring.append((loc + d * 0.0035) if loc is not None else Vector((ctr.x, ctr.y, zc)) + d * 0.095)
    bm = bmesh.new()
    rows = [[bm.verts.new(p + Vector((0, 0, dz))) for p in ring] for dz in (-0.011, 0.011)]
    for k in range(28):
        bm.faces.new((rows[0][k], rows[0][(k + 1) % 28], rows[1][(k + 1) % 28], rows[1][k]))
    K.solidify(bm, 0.003)
    part(f"AK_Strap_{tag}", bm, "05_Bottom", "belt", "Gear", bones=[f"thigh_{s}"])
    bm = bmesh.new()
    p_out = ring[0 if sg > 0 else 14]                                                        # sisi luar paha
    JC.add_box(bm, p_out + Vector((sg * 0.003, 0, 0)), (0.006, 0.026, 0.028))
    part(f"AK_BeltGold_strap_{tag}", bm, "05_Bottom", "gold", "Gear", rigid=f"thigh_{s}")

# ================================================================== 8. sabuk + gesper berbingkai + tali sabuk
bm = bmesh.new()
K.loft(bm, [(z, 0.0, -0.028 + SY, 0.189, 0.119, 2.7, None) for z in (1.070, 1.091, 1.112)], n=48)
K.solidify(bm, 0.004)
for a in (40, 100, 180, 260, 320):                                                                # tali sabuk
    t = math.radians(a)
    p = K.se_point(0.0, -0.028 + SY, 0.192, 0.122, 2.7, t, 1.091)
    nrm = Vector((p.x, p.y + 0.028 - SY, 0)).normalized()
    JC.add_box(bm, p + nrm * 0.0015, (0.012, 0.004, 0.050), rot=(0, 0, math.atan2(nrm.y, nrm.x) + math.pi / 2))
part("AK_BeltNew", bm, "05_Bottom", "belt", "Gear", bones=["pelvis", "spine_01", "spine_02"])
bm = bmesh.new()
fy = -0.028 + SY - 0.119 - 0.006
for (cx, cz, w, h) in [(0, 1.110, 0.054, 0.006), (0, 1.072, 0.054, 0.006), (-0.024, 1.091, 0.006, 0.044), (0.024, 1.091, 0.006, 0.044)]:
    JC.add_box(bm, (cx, fy, cz), (w, 0.006, h))
JC.add_box(bm, (-0.016, fy - 0.0015, 1.091), (0.004, 0.004, 0.030))                                # batang poros
JC.add_box(bm, (-0.002, fy - 0.0025, 1.091), (0.028, 0.003, 0.004))                                # lidah gesper
part("AK_BeltGold", bm, "05_Bottom", "gold", "Gear", rigid="spine_01")

# ================================================================== 9. selendang batik (simpul + pita menempel paha)
legL = K.bvh_of(leg_objs["L"])
sp = HR.catmull(C.sash_path(), spp=3)
pts, sides_ = [], []
for i, p in enumerate(sp):
    axis_c = Vector((0.105, -0.025 + SY, p.z))
    d = Vector((p.x - axis_c.x, p.y - axis_c.y, 0)).normalized()
    loc, nrm = K.ray(legL, Vector((axis_c.x, axis_c.y, p.z)) + d * 0.3, -d, 0.4)
    q = (loc + d * 0.0065) if (loc is not None and p.z < 1.0) else p
    pts.append(q)
for i, q in enumerate(pts):
    T = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
    d = Vector((q.x - 0.105, q.y - (-0.025 + SY), 0)).normalized()
    sides_.append(T.cross(d).normalized())
n = len(pts)
widths = [0.040 + 0.062 * K.smooth(0.0, 0.45, i / (n - 1)) * (1 - K.smooth(0.82, 1.0, i / (n - 1))) for i in range(n)]
widths[-1] = 0.0
bm = bmesh.new()
JC.add_strip(bm, pts, widths, sides_, t_layer_name="AK_t")
K.solidify(bm, 0.0022)
part("AK_SashNew", bm, "06_Accessory", "batik", "Cloth", chain="sash")
bm = bmesh.new()
JC.add_ico(bm, pts[0] + Vector((0, -0.006, 0.004)), (0.020, 0.013, 0.017), sub=2)                  # simpul
HR.tube(bm, [pts[0] + Vector((0.004, -0.010, 0.0)), pts[0] + Vector((0.020, -0.016, -0.034)), pts[0] + Vector((0.026, -0.016, -0.075))],
        [0.009, 0.007, 0.0], n=6, squash=(0.35, 1.0))                                              # ekor pendek simpul
part("AK_SashNew_knot", bm, "06_Accessory", "batik", "Cloth", rigid="pelvis")

# ================================================================== 10. kalung (rantai + pecahan batu berbingkai)
tee_bvh = K.bvh_of(tee)
head_bvh = K.bvh_of(head)
ctrl = [(0.046, -0.072 + SY, 1.515), (0.040, -0.110 + SY, 1.45), (0.022, -0.140 + SY, 1.38), (0.0, -0.150 + SY, 1.338),
        (-0.022, -0.140 + SY, 1.38), (-0.040, -0.110 + SY, 1.45), (-0.046, -0.072 + SY, 1.515)]
chain = HR.catmull(ctrl, spp=5)
proj = []
for p in chain:
    best = None
    for bv in (tee_bvh, head_bvh):
        loc, nrm, _i, d = bv.find_nearest(p)
        if loc is not None and (best is None or d < best[2]):
            best = (loc, nrm, d)
    proj.append(best[0] + best[1] * 0.0025 if best else p)
bm = bmesh.new()
HR.tube(bm, proj, 0.0016, n=6, caps=(True, True))
loc, nrm = K.ray(tee_bvh, (0, -0.4, 1.312), (0, 1, 0))
pc = loc + nrm * 0.006
outline = [pc + Vector((x, 0, z)) for x, z in [(0.0, 0.019), (0.008, 0.008), (0.010, -0.006), (0.004, -0.017), (-0.005, -0.014), (-0.010, -0.002), (-0.007, 0.010)]]
HR.closed_tube(bm, outline, 0.0013, n=6, up=Vector((0, -1, 0)))
part("AK_Necklace", bm, "06_Accessory", "gold", "Gear", rigid="spine_05")
bm = bmesh.new()
JC.add_hull(bm, [p + Vector((0, dy, 0)) for p in outline for dy in (-0.0032, 0.0028)] + [pc + Vector((0.002, -0.0045, 0.003))])
part("AK_Stone", bm, "06_Accessory", "stone", "Gear", rigid="spine_05", smooth=False)

# ================================================================== 11. boots
SOLE_T = 0.027
for tag, sg in SIDES.items():
    s = tag.lower()
    fo, bl = bh(f"foot_{s}"), bh(f"ball_{s}")
    ax = Vector((bl.x - fo.x, bl.y - fo.y, 0)).normalized()
    lat = Vector((-ax.y, ax.x, 0)).normalized()
    if lat.x * sg < 0:
        lat = -lat
    o = Vector((fo.x, fo.y + SY, 0))
    up = Vector((0, 0, 1))
    PROF = [(-0.098, 0.030, 0.090), (-0.088, 0.042, 0.110), (-0.050, 0.049, 0.125), (0.000, 0.051, 0.125), (0.050, 0.052, 0.104),
            (0.105, 0.051, 0.082), (0.155, 0.047, 0.066), (0.192, 0.040, 0.056), (0.214, 0.029, 0.048), (0.224, 0.012, 0.043)]

    def section(f, wl, zt, n=20, zb=SOLE_T - 0.002, p=2.6):
        zc, hz = (zb + zt) / 2, (zt - zb) / 2
        pts = []
        for k in range(n):
            a = 2 * math.pi * k / n
            c, sn = math.cos(a), math.sin(a)
            x = wl * K.sgn(c) * abs(c) ** (2 / p)
            z = zc + hz * K.sgn(sn) * abs(sn) ** (2 / p)
            pts.append(o + ax * f + lat * x + up * z)
        return pts

    bm = bmesh.new()
    rings = [[bm.verts.new(p) for p in section(f, wl, zt)] for f, wl, zt in PROF]
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(20):
            bm.faces.new((a[k], a[(k + 1) % 20], b[(k + 1) % 20], b[k]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    # batang boots
    sh0 = o + ax * (-0.008) + up * 0.05
    shaft = [sh0, sh0 + up * 0.10, sh0 + up * 0.212]
    HR.tube(bm, shaft, [0.052, 0.054, 0.059], n=20, squash=(1.0, 1.10), caps=(False, True))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    boot = part(f"AK_Boot_{tag}", bm, "07_Shoes", "boots", "Gear", bones=[f"calf_{s}", f"foot_{s}", f"ball_{s}"])
    # sol tebal + trim emas
    bm = bmesh.new()
    srings = []
    for f, wl, zt in [(-0.103, 0.032, 0), (-0.092, 0.046, 0), (-0.05, 0.053, 0), (0.00, 0.055, 0), (0.05, 0.056, 0), (0.105, 0.055, 0),
                      (0.155, 0.051, 0), (0.192, 0.044, 0), (0.216, 0.032, 0), (0.229, 0.013, 0)]:
        srings.append([bm.verts.new(p) for p in section(f, wl, SOLE_T, n=16, zb=0.0, p=5.0)])
    for a, b in zip(srings[:-1], srings[1:]):
        for k in range(16):
            bm.faces.new((a[k], a[(k + 1) % 16], b[(k + 1) % 16], b[k]))
    bm.faces.new(srings[0][::-1])
    bm.faces.new(srings[-1])
    for f in (-0.07, -0.03, 0.04, 0.09, 0.14, 0.18):                                                # gerigi sol
        JC.add_box(bm, o + ax * f + up * 0.004, (0.010, 0.10, 0.008), rot=(0, 0, math.atan2(ax.y, ax.x)))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    part(f"AK_Sole_{tag}", bm, "07_Shoes", "sole", "Gear", bones=[f"foot_{s}", f"ball_{s}"])
    bm_g = bmesh.new()
    outline = [o + ax * f + lat * w * sgn_ + up * (SOLE_T + 0.001) for sgn_ in (1, -1) for f, w, _ in
               ([(-0.101, 0.033, 0), (-0.05, 0.054, 0), (0.05, 0.057, 0), (0.155, 0.052, 0), (0.216, 0.033, 0)] if sgn_ > 0 else
                [(0.216, 0.033, 0), (0.155, 0.052, 0), (0.05, 0.057, 0), (-0.05, 0.054, 0), (-0.101, 0.033, 0)])]
    HR.closed_tube(bm_g, HR.catmull(outline + [outline[0]], spp=3)[:-1], 0.0017, n=5)
    # strap atas + gesper, kait tali
    top = sh0 + up * 0.192
    JC.add_box(bm_g, top + lat * 0.064 + up * 0.0, (0.004, 0.022, 0.024), rot=(0, 0, math.atan2(lat.y, lat.x)))
    for k in range(6):
        z = 0.105 + 0.022 * k
        for side in (-1, 1):
            p = sh0 + up * (z - 0.06) + ax * 0.054 + lat * side * 0.018
            JC.add_ico(bm_g, p, (0.0042, 0.0042, 0.0042), sub=1)
    part(f"AK_BootGold_{tag}", bm_g, "07_Shoes", "gold", "Gear", bones=[f"calf_{s}", f"foot_{s}", f"ball_{s}"])
    bm = bmesh.new()
    HR.tube(bm, [top - up * 0.010, top + up * 0.010], [0.0640, 0.0640], n=20, squash=(1.0, 1.06), caps=(True, True))
    for k in range(5):                                                                              # tali silang
        z0, z1 = 0.105 + 0.022 * k, 0.105 + 0.022 * (k + 1)
        for side in (-1, 1):
            a = sh0 + up * (z0 - 0.06) + ax * 0.057 + lat * side * 0.018
            b = sh0 + up * (z1 - 0.06) + ax * 0.057 + lat * -side * 0.018
            HR.tube(bm, [a, b], 0.0018, n=4, caps=(True, True))
    part(f"AK_Lace_{tag}", bm, "07_Shoes", "boots", "Gear", bones=[f"calf_{s}", f"foot_{s}"])

# ================================================================== 12. tanpa tembus antar lapisan
fit = {}
fit["tee"] = K.push_outside(tee, [head_bvh], 0.0025)
tee_bvh = K.bvh_of(tee)
fit["coat"] = K.push_outside(coat, [tee_bvh], 0.004)
for o in parts:
    if o.name.startswith("AK_CollarOut") or o.name.startswith("AK_CollarLining"):
        fit[o.name] = K.push_outside(o, [head_bvh], 0.006)
    if o.name.startswith("AK_GloveNew"):
        tag = o.name[-1]
        hb = [K.bvh_of(x) for x in parts if x.name.startswith(("AK_Hand_" + tag, "AK_Finger_")) and x.name.endswith("_" + tag)]
        fit[o.name] = K.push_outside(o, hb, 0.0022)
for tag in SIDES:
    boot = next(x for x in parts if x.name == f"AK_Boot_{tag}")
    fit["leg_" + tag] = K.push_outside(leg_objs[tag], [K.bvh_of(boot)], 0.003)
print("dorong-keluar (vertex):", fit)

# ================================================================== 13. bobot + modifier
for obj in parts:
    n_ = len(obj.data.vertices)
    if obj["ak_kind"] == "rigid":
        C.set_weights(obj, {obj["ak_bone"]: {i: 1.0 for i in range(n_)}})
    elif obj["ak_kind"] == "strip":
        chain_b = [f"sash_0{i}" for i in range(1, C.SASH_N + 1)]
        nb = len(chain_b)
        tl = obj.data.attributes["AK_t"].data
        assign = {b: {} for b in chain_b}
        for v in obj.data.vertices:
            u = tl[v.index].value * nb - 0.5
            if u <= 0:
                assign[chain_b[0]][v.index] = 1.0
            elif u >= nb - 1:
                assign[chain_b[-1]][v.index] = 1.0
            else:
                i0 = int(u)
                f = u - i0
                assign[chain_b[i0]][v.index] = 1.0 - f
                assign[chain_b[i0 + 1]][v.index] = f
        C.set_weights(obj, assign)
    else:
        bones = [b for b in obj["ak_bones"].split(",") if b in SEG]
        C.distance_weights(obj, SEG, bones, k=3, power=4.0)
        if not obj.name.startswith(("AK_Finger", "AK_Hand")):
            C.smooth_weights(obj, iters=2, factor=0.5)
    C.clean_weights(obj)
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    mod.use_vertex_groups = True
    obj.parent = arm

tot = 0
for o in parts:
    tot += C.tri_count(o)
print("bagian pakaian+tangan:", len(parts), "| tris:", tot)
print("TOTAL model tris:", sum(C.tri_count(o) for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("AK_") and not o.name.startswith("AK_REF")))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
print("Disimpan:", bpy.data.filepath)
