"""Jayadwara2 R1 — spike rig: skeleton (jd2_skeleton) + pemisahan jahitan sentuh + bobot kulit untuk mesh Tripo satu badan.

Jalankan headless dari hasil R0:
  blender --background Art/Blender/jayadwara2/jayadwara2_v01_tripo.blend --python Art/Scripts/jayadwara2_10_rig_spike.py
Hasil: Art/Blender/jayadwara2/jayadwara2_v02_rig_spike.blend  (objek `JD2_Body` ter-skin ke `JD2_Armature`, 9 socket; `JD2_Source` disembunyikan).

Temuan R1: mesh Tripo satu pulau; kepalan menyentuh/menyatu dengan sayap kain & paha, lengan dengan rusuk. Bobot apa pun
menarik "jembatan" antar bagian jadi balok panjang saat pose. Jadi:
  1. Tiap segitiga diberi MAKRO (HEAD/TORSO/ARM_x/LEG_x/WING_x/CLOTH) dari kapsul tulang terdekat + aturan kain/sayap.
  2. Tepi antar dua makro yang tidak seharusnya tersambung (mis. kepalan-sayap) dipisah (split edge): vertex diduplikasi,
     permukaan tetap ada tapi tidak saling menarik. Sambungan sah (bahu, pinggul, leher, sabuk) dipertahankan.
  3. Bobot per vertex: kandidat dibatasi ke tulang makronya (+ makro bertetangga di sambungan sah), kapsul bertetangga.
  4. Kain depan & sayap: bobot sepanjang rantai tulang. Pauldron: 50% clavicle / 50% upperarm.
Mesh sumber tidak diubah. Variabel opsional: RIG_OUT.
"""
import json
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jd2_skeleton as SK

OUT = globals().get("RIG_OUT") or r"C:\repository\unreal_engine\jayadwara\Art\Blender\jayadwara2\jayadwara2_v02_rig_spike.blend"
ARM_NAME, BODY_NAME = "JD2_Armature", "JD2_Body"
MAX_INFLUENCE = 4

src = bpy.data.objects["JD2_Source"]
for n in (ARM_NAME, BODY_NAME):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
for o in list(bpy.data.objects):
    if o.name.startswith("SOCKET_"):
        bpy.data.objects.remove(o, do_unlink=True)
root_coll = bpy.data.collections["JD2_Jayadwara"]


def sub(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in root_coll.children:
        root_coll.children.link(c)
    return c


body = src.copy()
body.data = src.data.copy()
body.name = body.data.name = BODY_NAME
sub("02_Body").objects.link(body)
src.hide_viewport = src.hide_render = True
mesh = body.data

# ------------------------------------------------------------------ armature
arm_data = bpy.data.armatures.new(ARM_NAME)
arm = bpy.data.objects.new(ARM_NAME, arm_data)
sub("08_Rig").objects.link(arm)
arm.show_in_front = True
arm_data.display_type = "STICK"
bpy.context.view_layer.objects.active = arm
for o in bpy.context.view_layer.objects:
    o.select_set(False)
arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_data.edit_bones
bones = SK.build_bones()
for name, parent, head, tail, connect in bones:
    b = eb.new(name)
    b.head, b.tail = head, tail
    b.use_deform = name not in SK.IK_BONES
for name, parent, head, tail, connect in bones:
    if parent:
        eb[name].parent = eb[parent]
        eb[name].use_connect = connect
bpy.ops.object.mode_set(mode="OBJECT")
print("tulang:", len(arm_data.bones))

# ------------------------------------------------------------------ geometri bantu
SEG = SK.bone_segments()


def seg_dist(P, a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-12), 0.0, 1.0)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1), t


def chain_project(P, names):
    best_d = np.full(len(P), np.inf)
    best_u = np.zeros(len(P))
    for i, n in enumerate(names):
        h, t = SEG[n]
        d, tt = seg_dist(P, h[:], t[:])
        m = d < best_d
        best_d[m] = d[m]
        best_u[m] = i + tt[m]
    return best_u, best_d


RADII = {"pelvis": 0.19, "spine_01": 0.17, "spine_02": 0.18, "spine_03": 0.20, "spine_04": 0.22, "spine_05": 0.24,
         "neck_01": 0.075, "neck_02": 0.075, "head": 0.16, "clavicle": 0.07, "upperarm": 0.085, "lowerarm": 0.085,
         "hand": 0.095, "thigh": 0.12, "calf": 0.10, "foot": 0.10, "ball": 0.08}
EXTRA = {"pelvis": ((0, 0, 0.88), (0, 0, 1.0))}        # kapsul panggul dipanjangkan ke bawah (selangkangan)
# SKIN_BONES model lama tidak memuat head/foot/ball (bagian kaku) -> di mesh satu badan ketiganya wajib ikut
SKINB = [n for n in SK.SKIN_BONES if "twist" not in n] + ["head"] + [f"{b}_{sd}" for sd in ("l", "r") for b in ("foot", "ball")]
SCARF_BONES = {sd: [f"scarf_{sd}_{i + 1:02d}" for i in range(SK.SCARF_N)] for sd in ("l", "r")}
FRONT_BONES = SK.chain_bones("cloth_front")
WING_R = 0.14                                          # setengah lebar sayap sisi (lembar melebar ke dalam, menempel paha)


def rad(n):
    return RADII[n.rsplit("_", 1)[0] if n[-2:] in ("_l", "_r") else n]


def macro_of_bone(n):
    if n in ("head", "neck_01", "neck_02"):
        return "HEAD"
    if n == "pelvis" or n.startswith("spine_"):
        return "TORSO"
    sd = n[-1]
    if n.split("_")[0] in ("clavicle", "upperarm", "lowerarm", "hand"):
        return f"ARM_{sd}"
    return f"LEG_{sd}"


def kind(m):
    return m.split("_")[0]


def allowed_join(m0, m1, z):
    """Apakah dua makro boleh tetap tersambung pada ketinggian z (sambungan anatomis/pakaian yang sah)?"""
    if m0 == m1:
        return True
    k = {kind(m0), kind(m1)}
    if k == {"HEAD", "TORSO"}:
        return True
    if k == {"ARM", "TORSO"}:
        return z > 1.40
    if k == {"LEG", "TORSO"}:
        return z > 0.80
    if k == {"WING", "TORSO"}:
        return z > 0.98
    if k == {"CLOTH", "TORSO"}:
        return z > 0.98
    if k == {"CLOTH", "LEG"}:
        return z > 1.0
    if k == {"WING", "CLOTH"}:
        return True
    return False


def classify(P):
    """(makro per titik, matriks skor kapsul D, posisi rantai sayap, posisi rantai kain depan)."""
    n = len(P)
    D = np.zeros((n, len(SKINB)))
    for j, b in enumerate(SKINB):
        h, t = EXTRA.get(b, SEG[b])
        D[:, j] = seg_dist(P, h[:], t[:])[0] - rad(b)
    best = D.argmin(axis=1)
    macro = np.array([macro_of_bone(SKINB[i]) for i in best], dtype=object)
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    s_arm = np.min([D[:, j] for j, b in enumerate(SKINB) if kind(macro_of_bone(b)) == "ARM"], axis=0)
    s_leg = np.min([D[:, j] for j, b in enumerate(SKINB) if kind(macro_of_bone(b)) == "LEG"], axis=0)
    front = (np.abs(x) < 0.115) & (y < -0.198) & (z < 1.04) & (z > 0.30)
    macro[front] = "CLOTH"
    u_chain = {}
    for sd, sg in (("l", 1.0), ("r", -1.0)):
        u_w, d_w = chain_project(P, SCARF_BONES[sd])
        sc = d_w - WING_R
        cand = (sc < 0) & (z < 1.14) & (z > 0.30) & (sg * x > np.where(z < 0.75, 0.285, 0.20)) & (s_arm > 0.0) & (sc < s_leg) & ~front
        macro[cand] = f"WING_{sd}"
        u_chain[sd] = u_w
    u_front, _ = chain_project(P, FRONT_BONES)
    return macro, D, u_chain, u_front


# ------------------------------------------------------------------ 1) makro per segitiga -> split jahitan sentuh
bm = bmesh.new()
bm.from_mesh(mesh)
bm.faces.ensure_lookup_table()
fc = np.array([f.calc_center_median()[:] for f in bm.faces])
fmacro, _, _, _ = classify(fc)
to_split = []
by_pair = {}
for e in bm.edges:
    if len(e.link_faces) != 2:
        continue
    f0, f1 = e.link_faces
    m0, m1 = fmacro[f0.index], fmacro[f1.index]
    if m0 == m1:
        continue
    z = (e.verts[0].co.z + e.verts[1].co.z) / 2
    if not allowed_join(m0, m1, z):
        to_split.append(e)
        key = tuple(sorted((m0, m1)))
        by_pair[key] = by_pair.get(key, 0) + 1
print(f"tepi dipisah: {len(to_split)} dari {len(bm.edges)}; pasangan:", dict(sorted(by_pair.items(), key=lambda kv: -kv[1])[:10]))
nv0 = len(bm.verts)
bmesh.ops.split_edges(bm, edges=to_split)
print(f"vertex {nv0} -> {len(bm.verts)} setelah split")
bm.faces.ensure_lookup_table()
bm.verts.ensure_lookup_table()
vmacro = []
for v in bm.verts:
    cnt = {}
    for f in v.link_faces:
        m = fmacro[f.index]
        cnt[m] = cnt.get(m, 0) + 1
    vmacro.append(max(cnt, key=cnt.get) if cnt else "TORSO")
vmacro = np.array(vmacro, dtype=object)
bm.to_mesh(mesh)
bm.free()
mesh.update()
nV = len(mesh.vertices)
V = np.array([v.co[:] for v in mesh.vertices], float)
x, y, z = V[:, 0], V[:, 1], V[:, 2]

# ------------------------------------------------------------------ 2) bobot
_, D, u_chain, u_front = classify(V)
adj = {n: set() for n in SKINB}
par = {n: p for n, p, *_ in bones}
for n in SKINB:
    q = par.get(n)
    while q and q not in SKINB:
        q = par.get(q)
    if q in adj:
        adj[n].add(q)
        adj[q].add(n)
bone_macro = {b: macro_of_bone(b) for b in SKINB}
MARGIN, TAU = 0.05, 0.02
assign = {}
chain_vertices = {}
for vi in range(nV):
    m = vmacro[vi]
    names = None
    if m == "CLOTH":
        names, u = FRONT_BONES, u_front[vi]
    elif m.startswith("WING"):
        names, u = SCARF_BONES[m[-1]], u_chain[m[-1]][vi]
    if names:
        u -= 0.5
        wm = {names[0]: 1.0} if u <= 0 else {names[-1]: 1.0} if u >= len(names) - 1 else \
            {names[int(u)]: 1 - (u - int(u)), names[int(u) + 1]: u - int(u)}
        for bn, w in wm.items():
            assign.setdefault(bn, {})[vi] = float(w)
        chain_vertices[vi] = m
        continue
    ok = [j for j, b in enumerate(SKINB) if allowed_join(m, bone_macro[b], z[vi])]
    j0 = min(ok, key=lambda j: D[vi, j])
    cand = [j0] + [SKINB.index(q) for q in adj[SKINB[j0]]
                   if SKINB.index(q) in ok and D[vi, SKINB.index(q)] <= D[vi, j0] + MARGIN]
    w = np.exp(-(D[vi, cand] - D[vi, j0]) / TAU)
    w /= w.sum()
    pauldron = False
    if m.startswith("ARM"):
        sd, sg = m[-1], (1.0 if m[-1] == "l" else -1.0)
        pauldron = (np.linalg.norm(V[vi] - np.array(SK.P("shoulder", sg))) < 0.17 and z[vi] > 1.44 and sg * x[vi] > 0.15)
    if pauldron:
        assign.setdefault(f"clavicle_{sd}", {})[vi] = 0.5
        assign.setdefault(f"upperarm_{sd}", {})[vi] = 0.5
    else:
        for c, ww in zip(cand, w):
            assign.setdefault(SKINB[c], {})[vi] = float(ww)


def set_weights(obj, assign):
    for gname, vmap in assign.items():
        vg = obj.vertex_groups.get(gname) or obj.vertex_groups.new(name=gname)
        by_w = {}
        for vi, w in vmap.items():
            if w > 1e-4:
                by_w.setdefault(round(w, 5), []).append(int(vi))
        for w, idx in by_w.items():
            vg.add(idx, w, "REPLACE")


body.vertex_groups.clear()
set_weights(body, assign)


def unweighted():
    return sum(1 for v in mesh.vertices if not [g for g in v.groups if g.weight > 1e-4])


def smooth_weights(iters=1, factor=0.4, skip=frozenset()):
    ad = [set() for _ in range(nV)]
    for e in mesh.edges:
        a, b = e.vertices
        ad[a].add(b)
        ad[b].add(a)
    W = [{g.group: g.weight for g in v.groups} for v in mesh.vertices]
    names = {vg.index: vg.name for vg in body.vertex_groups}
    for _ in range(iters):
        new = []
        for i in range(nV):
            if i in skip or not ad[i]:
                new.append(W[i])
                continue
            acc = {}
            for j in ad[i]:
                for g, w in W[j].items():
                    acc[g] = acc.get(g, 0.0) + w / len(ad[i])
            new.append({g: (1 - factor) * W[i].get(g, 0.0) + factor * acc.get(g, 0.0) for g in set(W[i]) | set(acc)})
        W = new
    for vi, m in enumerate(W):
        if vi in skip:
            continue
        for g, w in m.items():
            vg = body.vertex_groups[g]
            if w > 1e-4:
                vg.add([vi], w, "REPLACE")
            else:
                vg.remove([vi])


def clean_weights(limit=MAX_INFLUENCE):
    vgs = {vg.index: vg for vg in body.vertex_groups}
    for v in mesh.vertices:
        gs = sorted(((g.group, g.weight) for g in v.groups if g.weight > 1e-4), key=lambda t: -t[1])
        keep, drop = gs[:limit], gs[limit:]
        tot = sum(w for _, w in keep) or 1.0
        for gi, _ in drop:
            vgs[gi].remove([v.index])
        for gi, w in keep:
            vgs[gi].add([v.index], w / tot, "REPLACE")


smooth_weights(iters=1, factor=0.4, skip=frozenset(chain_vertices))
clean_weights()
mx = max(len([g for g in v.groups if g.weight > 1e-4]) for v in mesh.vertices)
print(f"bobot: grup={len(body.vertex_groups)}, influence maks={mx}, tanpa bobot={unweighted()}")
cnt = {}
for m in vmacro:
    cnt[m] = cnt.get(m, 0) + 1
print("vertex per makro:", dict(sorted(cnt.items())))

mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
mod.use_vertex_groups = True
body.parent = arm
body.parent_type = "OBJECT"
body["jd2_macro"] = json.dumps([str(m) for m in vmacro])

# ------------------------------------------------------------------ socket
for name, (bone, pos) in SK.build_sockets().items():
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.05
    sub("09_Sockets").objects.link(e)
    e.parent = arm
    e.parent_type = "BONE"
    e.parent_bone = bone
    bpy.context.view_layer.update()
    e.matrix_world = Matrix.Translation(pos)

bpy.ops.wm.save_as_mainfile(filepath=OUT, relative_remap=True)
print("disimpan:", OUT)
