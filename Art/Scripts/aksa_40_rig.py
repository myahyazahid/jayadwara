"""Aksa Iterasi 4 — rig final: tulang twist Manny ikut deform, rantai ujung jaket `jacket_*`, bobot ulang lengan/kaki/tangan.

Jalankan di Blender (MCP: exec(open(path).read())) dengan aksa_v04_outfit.blend terbuka, SETELAH aksa_22 (kepala + morph) dan aksa_30
(pakaian). Idempotent (aman diulang):
  1. Tulang twist Manny (upperarm/lowerarm/thigh/calf `_twist_01/02`) use_deform = True; segmen bobot dipecah sepanjang anggota badan
     (sendi -> twist terdekat -> twist jauh -> sendi berikutnya) sehingga puntiran lengan/kaki yang digerakkan ABP/Control Rig Mannequin
     tersebar halus.
  2. Rantai `jacket_l_01..02` dan `jacket_r_01..02` (induk spine_03, daun baru): dua ujung depan jaket berayun (Anim Dynamics di UE).
  3. Bobot dihitung ulang untuk lengan jaket, tangan, celana (kaki), kantong kargo dengan daftar tulang yang menyertakan twist; ujung depan
     jaket (badan jaket, pita pinggang, ritsleting emas) dicampur ke rantai `jacket_*` menurut tinggi dan kedekatan ke tepi depan.
Simpan ke file yang sedang terbuka.
"""
import importlib
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C

importlib.reload(C)
assert "aksa_v04" in bpy.data.filepath, "buka aksa_v04_outfit.blend"
arm = C.get_arm()
SY = C.BODY_SHIFT_Y
bh = lambda n: C.bone_head(arm, n)  # noqa: E731

# ---------------------------------------------------------------- 1. tulang jacket_* (daun baru)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.data.edit_bones
JK = {}
for sd, sg in (("l", 1), ("r", -1)):
    pts = [Vector((sg * 0.100, -0.148 + SY, 1.150)), Vector((sg * 0.112, -0.158 + SY, 1.092)), Vector((sg * 0.118, -0.164 + SY, 1.036))]
    prev = eb["spine_03"]
    for k in (1, 2):
        b = eb.get(f"jacket_{sd}_0{k}") or eb.new(f"jacket_{sd}_0{k}")
        b.head, b.tail = pts[k - 1], pts[k]
        b.parent = prev
        b.use_connect = False
        prev = b
    JK[sd] = [(pts[0], pts[1]), (pts[1], pts[2])]
bpy.ops.object.mode_set(mode="OBJECT")
for b in arm.data.bones:
    if b.name.startswith("jacket_") or "_twist_" in b.name:
        b.use_deform = True

# ---------------------------------------------------------------- 2. segmen bobot (twist + jacket)
SEG = C.bone_segments(arm)
for s in "lr":
    for f in ["index", "middle", "ring", "pinky"]:
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
LIMBS = {"upperarm": ("lowerarm", None), "lowerarm": ("hand", None), "thigh": ("calf", None), "calf": ("foot", None)}
TWISTS = {}
for s in "lr":
    for a, (b, _) in LIMBS.items():
        t = [n for n in (f"{a}_twist_01_{s}", f"{a}_twist_02_{s}") if n in arm.data.bones]
        if not t:
            continue
        A, B = bh(f"{a}_{s}"), bh(f"{b}_{s}")
        ax = (B - A)
        t.sort(key=lambda n: (bh(n) - A).dot(ax))
        chain = [f"{a}_{s}"] + t
        ends = [bh(n) for n in chain[1:]] + [B]
        for n, e in zip(chain, ends):
            SEG[n] = (bh(n), e)
        TWISTS[f"{a}_{s}"] = t
print("twist:", {k: v for k, v in TWISTS.items() if k.endswith("_l")})
for sd in "lr":
    for k in (1, 2):
        SEG[f"jacket_{sd}_0{k}"] = JK[sd][k - 1]


def with_twist(names):
    out = []
    for n in names:
        out.append(n)
        out += TWISTS.get(n, [])
    return out


# ---------------------------------------------------------------- 3. bobot ulang
def reweight(obj, bones, smooth=True):
    obj.vertex_groups.clear()
    C.distance_weights(obj, SEG, bones, k=3, power=4.0)
    if smooth:
        C.smooth_weights(obj, iters=2, factor=0.5)
    C.clean_weights(obj)


redone = []
for tag in ("L", "R"):
    s = tag.lower()
    spine = ["spine_04", "spine_05", f"clavicle_{s}"]
    reweight(bpy.data.objects[f"AK_CoatSleeve_{tag}"], with_twist([f"upperarm_{s}", f"lowerarm_{s}"]) + [f"hand_{s}"] + spine)
    hand_bones = with_twist([f"lowerarm_{s}"]) + [f"hand_{s}", f"thumb_01_{s}"] + [f"{f}_metacarpal_{s}" for f in ("index", "middle", "ring", "pinky")]
    reweight(bpy.data.objects[f"AK_Hand_{tag}"], hand_bones, smooth=False)
    leg = ["pelvis", "spine_01"] + with_twist([f"thigh_{s}", f"calf_{s}"]) + [f"foot_{s}"]
    reweight(bpy.data.objects[f"AK_Trousers_leg_{tag}"], leg)
    reweight(bpy.data.objects[f"AK_Cargo_{tag}"], with_twist([f"thigh_{s}"]) + ["pelvis"])
    redone += [f"AK_CoatSleeve_{tag}", f"AK_Hand_{tag}", f"AK_Trousers_leg_{tag}", f"AK_Cargo_{tag}"]
print("bobot ulang:", redone)


# ---------------------------------------------------------------- 4. ujung depan jaket -> rantai jacket_*
def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def flap_blend(obj):
    """Campur bobot ke jacket_l/r_01..02: aktif di depan-bawah (z < 1,16) dan makin dekat tepi depan (|x| kecil, y depan)."""
    gi = {vg.name: vg for vg in obj.vertex_groups}
    for n in ("jacket_l_01", "jacket_l_02", "jacket_r_01", "jacket_r_02"):
        if n not in gi:
            gi[n] = obj.vertex_groups.new(name=n)
    moved = 0
    for v in obj.data.vertices:
        p = obj.matrix_world @ v.co
        front = smooth(-0.02 + SY, -0.075 + SY, p.y)
        low = smooth(1.165, 1.060, p.z)
        edge = 1.0 - smooth(0.05, 0.13, abs(p.x))
        f = front * low * (0.35 + 0.65 * edge)
        if f < 0.02:
            continue
        sd = "l" if p.x >= 0 else "r"
        u = smooth(1.12, 1.045, p.z)                                          # 0 = jacket_01, 1 = jacket_02
        old = {g.group: g.weight for g in v.groups}
        for gidx, w in old.items():
            obj.vertex_groups[gidx].add([v.index], w * (1 - f), "REPLACE")
        gi[f"jacket_{sd}_01"].add([v.index], f * (1 - u), "ADD")
        gi[f"jacket_{sd}_02"].add([v.index], f * u, "ADD")
        moved += 1
    C.clean_weights(obj)
    return moved


for name in ("AK_Coat", "AK_CoatDetail_band", "AK_CoatGold"):
    print(name, "ujung jaket:", flap_blend(bpy.data.objects[name]))

bpy.ops.wm.save_mainfile()
print("rig final: tulang", len(arm.data.bones), "| deform", sum(b.use_deform for b in arm.data.bones))
