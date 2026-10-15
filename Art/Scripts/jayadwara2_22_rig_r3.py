"""Jayadwara2 R3 — rig final (R2 + bobot twist + sayap/kain ikut paha sebagian). [Dokumentasi R2:] Jayadwara2 R2 — rig: skeleton (jd2_skeleton) + lembar kain via KETEBALAN + pemisahan jahitan sentuh + bobot (zirah kaku) untuk mesh Tripo satu badan.

R2 vs spike R1 (jayadwara2_10_rig_spike.py, tetap disimpan): (1) lembar tipis (sayap kain, kain depan) dideteksi lewat ray cast ketebalan (< 3 cm), bukan kapsul tulang,
sehingga seluruh lembar menjadi satu makro WING/CLOTH dan tidak lagi sobek ketika kaki melebar; (2) bobot zirah dipertajam (terang pada atlas), bodysuit gelap tetap lunak.

[Dokumentasi spike R1:]

Jalankan headless dari hasil R0:
  blender --background Art/Blender/jayadwara2/jayadwara2_v01_tripo.blend --python Art/Scripts/jayadwara2_10_rig_spike.py
Hasil: Art/Blender/jayadwara2/jayadwara2_v05_rig_r3.blend  [R2: jayadwara2_v03_rig_r2.blend]  [R1: jayadwara2_v02_rig_spike.blend]  (objek `JD2_Body` ter-skin ke `JD2_Armature`, 9 socket; `JD2_Source` disembunyikan).

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

OUT = globals().get("RIG_OUT") or r"C:\repository\unreal_engine\jayadwara\Art\Blender\jayadwara2\jayadwara2_v05_rig_r3.blend"
ARM_NAME, BODY_NAME = "JD2_Armature", "JD2_Body"
MAX_INFLUENCE = 4
ISLAND_MIN_FACES = 0      # R3d: tidak lagi membuang pulau (membuat lubang); dulu 30
TWIST_FRAC = 0.6          # R3: bagian bobot segmen anggota badan yang dialihkan ke tulang twist di paruh distalnya
WING_THIGH = 0.55         # R3: sayap kain ikut paha hingga 55% di ujung (mengurangi tembus saat tendang/langkah lebar)
JOINT_R = {"hip": 0.17, "shoulder": 0.20, "knee": 0.09, "elbow": 0.09, "ankle": 0.08, "wrist": 0.08}   # R3: radius zona sendi tanpa penajaman zirah (m)
WING_FAR_THIGH = 0.55     # R3d: ujung bawah sayap ikut paha 55% (sisanya pinggul) — rok kinematik, tanpa simulasi
CLOTH_FAR_THIGH = 0.50    # R3d: ujung bawah kain depan ikut kedua paha 50% (dibagi rata)
WING_BLEND_R = 0.10      # R3c: jarak (m) dari permukaan paha tempat sayap berhenti ikut kaki
CLOTH_THIGH = 0.50       # kain depan ikut kedua paha (dibagi rata) hingga 50% di ujung bawah
ARMOR_LUM = 0.17          # luminans atlas per vertex; di atasnya = zirah (emas/merah/putih), di bawahnya = bodysuit hitam
ARMOR_POWER = 3.0         # penajaman bobot zirah anggota badan (w^p, dinormalisasi)

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
    # R3d: pemisahan (split) membuat tepi terbuka (440 vs 16 di sumber Tripo) yang merenggang jadi lubang/sobek saat bergerak.
    # Sekarang SEMUA sambungan dipertahankan (bobot kontinu menangani transisi), KECUALI kontak yang memang harus lepas:
    #  - lengan dengan apa pun selain torso di bahu (kepalan/lengan bawah menempel paha, sayap, kain, pinggang);
    #  - paha kiri <-> paha kanan, sayap kiri <-> sayap kanan (bagian simetris yang bersentuhan).
    if m0 == m1:
        return True
    k = {kind(m0), kind(m1)}
    if "ARM" in k:
        if k == {"ARM", "TORSO"}:
            return z > 1.40
        if k == {"ARM", "HEAD"}:
            return True
        return False
    if kind(m0) == kind(m1) and m0 != m1:          # LEG_l-LEG_r, WING_l-WING_r
        return False
    return True


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

# --- R2: ketebalan lokal per vertex (ray ke -normal & +normal, maks 15 cm) -> lembar tipis = sayap kain & kain depan
from mathutils.bvhtree import BVHTree
bm.verts.ensure_lookup_table()
bm.normal_update()
_tree = BVHTree.FromBMesh(bm)
thick = np.full(len(bm.verts), 0.15, np.float32)
for _v in bm.verts:
    for _sgn in (-1.0, 1.0):
        _hit = _tree.ray_cast(_v.co + _v.normal * (0.0015 * _sgn), _v.normal * _sgn, 0.15)   # mulai sedikit di luar permukaan sendiri
        if _hit[0] is not None:
            thick[_v.index] = min(thick[_v.index], _hit[3])
SHEET_MAX = 0.03
thin_v = thick < SHEET_MAX
print(f"lembar tipis: {int(thin_v.sum())} vertex (< {SHEET_MAX * 100:.0f} cm)")

# --- R2: warna atlas per vertex (rata-rata loop) -> zirah (terang) vs bodysuit (gelap)
_img = next(i for i in bpy.data.images if i.name.startswith("Color_") and i.type == "IMAGE")
_W, _H = _img.size
_buf = np.empty(_W * _H * 4, np.float32)
_img.pixels.foreach_get(_buf)
_buf = _buf.reshape(_H, _W, 4)[..., :3]
_uv = mesh.uv_layers.active.data
_acc = np.zeros((len(mesh.vertices), 3), np.float64)
_cnt = np.zeros(len(mesh.vertices))
for _l in mesh.loops:
    _u, _w = _uv[_l.index].uv
    _acc[_l.vertex_index] += _buf[min(_H - 1, max(0, int((1 - _w) * _H))), min(_W - 1, max(0, int(_u * _W)))]
    _cnt[_l.vertex_index] += 1
src_pos = np.array([v.co[:] for v in bm.verts], np.float32)
vcol_src = (_acc / np.maximum(_cnt, 1)[:, None]).astype(np.float32)          # per vertex SUMBER (sebelum split)
vlum_src = vcol_src.mean(axis=1)
print("luminans atlas per vertex: persentil", {p: round(float(np.percentile(vlum_src, p)), 3) for p in (5, 25, 50, 75, 95)})
fc = np.array([f.calc_center_median()[:] for f in bm.faces])
fmacro, _, _, _ = classify(fc)
# R2: sayap & kain depan = lembar tipis (>= 2 dari 3 vertex tipis) di zona pinggul-paha; menimpa hasil kapsul
_thin_face = np.array([sum(thin_v[v.index] for v in f.verts) >= 2 for f in bm.faces])
_cx, _cy, _cz = fc[:, 0], fc[:, 1], fc[:, 2]
_front = _thin_face & (np.abs(_cx) < 0.125) & (_cy < -0.185) & (_cz > 0.30) & (_cz < 1.06)
fmacro[_front] = "CLOTH"
for _sd, _sg in (("l", 1.0), ("r", -1.0)):
    _w = _thin_face & ~_front & (_sg * _cx > 0.12) & (_cz > 0.38) & (_cz < 1.16) & ((_cz > 0.72) | (_sg * _cx > 0.26))
    fmacro[_w] = f"WING_{_sd}"
print("makro lembar:", {k: int((fmacro == k).sum()) for k in ("CLOTH", "WING_l", "WING_r")})
# R3d: rapikan label sebelum split — komponen label kecil (mis. secuil sayap terlabel ARM di dekat kepalan) diberi label tetangga mayoritas.
# Tanpa ini potongan kecil itu terlepas jadi serpihan yang melayang ikut tangan.
LABEL_MIN_FACES = 40
for _pass in range(3):
    _seen = np.zeros(len(bm.faces), bool)
    _changed = 0
    for f0 in bm.faces:
        if _seen[f0.index]:
            continue
        lab0 = fmacro[f0.index]
        comp, stack, nb = [], [f0], {}
        _seen[f0.index] = True
        while stack:
            f = stack.pop()
            comp.append(f.index)
            for e in f.edges:
                for nf in e.link_faces:
                    if fmacro[nf.index] == lab0:
                        if not _seen[nf.index]:
                            _seen[nf.index] = True
                            stack.append(nf)
                    else:
                        nb[fmacro[nf.index]] = nb.get(fmacro[nf.index], 0) + 1
        if len(comp) < LABEL_MIN_FACES and nb:
            new = max(nb, key=nb.get)
            for fi in comp:
                fmacro[fi] = new
            _changed += 1
    print(f"rapikan label (lintasan {_pass + 1}): {_changed} komponen kecil dilabel ulang")
    if not _changed:
        break
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
_vm = {}
for v in bm.verts:
    cnt = {}
    for f in v.link_faces:
        m = fmacro[f.index]
        cnt[m] = cnt.get(m, 0) + 1
    _vm[v] = max(cnt, key=cnt.get) if cnt else "TORSO"
# R2: buang pulau mesh sangat kecil (sliver sisa split jahitan; tampil sebagai serpihan melayang saat pose)
_seen, _small = set(), []
for f0 in bm.faces:
    if f0 in _seen:
        continue
    comp, stack = [], [f0]
    _seen.add(f0)
    while stack:
        f = stack.pop()
        comp.append(f)
        for e in f.edges:
            for nf in e.link_faces:
                if nf not in _seen:
                    _seen.add(nf)
                    stack.append(nf)
    if len(comp) < ISLAND_MIN_FACES:
        _small.append(comp)
_nf = sum(len(c) for c in _small)
if _small:
    bmesh.ops.delete(bm, geom=[f for c in _small for f in c], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
print(f"pulau kecil dibuang: {len(_small)} pulau, {_nf} segitiga (< {ISLAND_MIN_FACES})")
bm.verts.ensure_lookup_table()
vmacro = [_vm[v] for v in bm.verts]
vmacro = np.array(vmacro, dtype=object)
bm.to_mesh(mesh)
bm.free()
mesh.update()
nV = len(mesh.vertices)
V = np.array([v.co[:] for v in mesh.vertices], float)
x, y, z = V[:, 0], V[:, 1], V[:, 2]
_key = lambda p_: (int(round(float(p_[0]) * 1e5)), int(round(float(p_[1]) * 1e5)), int(round(float(p_[2]) * 1e5)))
_lum_by_pos = {_key(p_): float(l_) for p_, l_ in zip(src_pos, vlum_src)}
vlum = np.array([_lum_by_pos.get(_key(p_), 0.0) for p_ in V])
is_armor = vlum > ARMOR_LUM
near_joint = np.zeros(len(V), bool)       # R3: zona sendi (zirah di sini tetap berbobot lunak agar sambungan tidak robek)
near_hipsh = np.zeros(len(V), bool)       # pinggul & bahu: pelat torso kaku juga dilunakkan
for _jn, _r in JOINT_R.items():
    for _sg in (1.0, -1.0):
        _d = np.linalg.norm(V - np.array(SK.P(_jn, _sg)), axis=1)
        near_joint |= _d < _r
        if _jn in ("hip", "shoulder"):
            near_hipsh |= _d < _r
print(f"zona sendi: {int(near_joint.sum())} vertex (zirah dilunakkan), pinggul/bahu: {int(near_hipsh.sum())}")
print(f"zirah (luminans > {ARMOR_LUM}): {int(is_armor.sum())} dari {nV} vertex")

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
        # R3d: KINEMATIK (tanpa rantai Anim Dynamics: sayap terlempar seperti ekor saat lompat di UE).
        # Bagian "jauh" = campuran pinggul -> paha yang naik ke bawah: atas (sabuk) 100% pelvis, ujung bawah KAIN_FAR_THIGH ikut paha.
        t_down = float(np.clip((u + 0.5) / len(names), 0.0, 1.0))
        if m.startswith("WING"):
            wm = {"pelvis": 1 - WING_FAR_THIGH * t_down, f"thigh_{m[-1]}": WING_FAR_THIGH * t_down}
        else:
            wm = {"pelvis": 1 - CLOTH_FAR_THIGH * t_down, "thigh_l": CLOTH_FAR_THIGH * t_down / 2, "thigh_r": CLOTH_FAR_THIGH * t_down / 2}
        if True:
            # R3c: bobot KONTINU: dekat kulit paha (s_leg <= 0) ikut kaki 100%, makin jauh ke luar (hingga WING_BLEND_R) makin ikut bagian "jauh"
            if m.startswith("WING"):
                sd_ = m[-1]
                cols = [SKINB.index(f"thigh_{sd_}"), SKINB.index(f"calf_{sd_}"), SKINB.index("pelvis")]
                s_leg = min(D[vi, cols[0]], D[vi, cols[1]])
            else:
                cols = [SKINB.index(f"thigh_{s_}") for s_ in ("l", "r")] + [SKINB.index("pelvis")]
                s_leg = min(D[vi, cols[0]], D[vi, cols[1]])
            f_leg = float(np.clip(1.0 - s_leg / WING_BLEND_R, 0.0, 1.0))
            dm = min(D[vi, c] for c in cols)
            wl = {SKINB[c]: float(np.exp(-(D[vi, c] - dm) / 0.03)) for c in cols}
            tot_ = sum(wl.values())
            wm = {bn: w * (1 - f_leg) for bn, w in wm.items()}
            for bn, w in wl.items():
                wm[bn] = wm.get(bn, 0.0) + f_leg * w / tot_
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
    if is_armor[vi] and (m.startswith("ARM") or m.startswith("LEG")) and not near_joint[vi]:          # R2: zirah anggota badan kaku (R3: kecuali zona sendi)
        w = w ** ARMOR_POWER
        w /= w.sum()
    elif is_armor[vi] and m == "TORSO" and not near_hipsh[vi]:                                       # R2: pelat dada/punggung/sabuk kaku (tak ikut lentur tulang belakang)
        zz = float(z[vi])
        if zz <= 1.12:
            rig = {"pelvis": 1.0}
        elif zz < 1.30:
            t_ = (zz - 1.12) / 0.18
            rig = {"pelvis": 1 - t_, "spine_04": t_}
        elif zz < 1.52:
            rig = {"spine_04": 1.0}
        else:
            rig = {"spine_05": 1.0}
        for bn, ww in rig.items():
            assign.setdefault(bn, {})[vi] = float(ww)
        continue
    elif m == "HEAD" and is_armor[vi] and float(z[vi]) > 1.70:                # helm & tanduk kaku ke `head`
        assign.setdefault("head", {})[vi] = 1.0
        continue
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


# ------------------------------------------------------------------ R3b: leher & dagu (perbaikan "wajah meleh" saat lompat)
# Temuan: leher/kerah (z 1,50-1,64) berbobot 100% spine_05 (makro TORSO; kapsul spine_05 r=0,24 menang atas neck_*), dan dagu depan z 1,64-1,68 setengahnya
# ke torso -> saat kepala berputar (lompat: head 25°) helm ikut `head`, dagu/leher tertinggal di torso dan wajah robek/meleh di sambungan.
# Perbaikan: (a) leher (|x|<0,12, y>-0,10, z 1,50-1,70) diinterpolasi spine_05 -> neck_01 -> neck_02 -> head menurut tinggi;
# (b) wajah depan/dagu (y<-0,09, |x|<0,13, z>=1,62) kaku ke `head`.
NECK_ANCHORS = [(1.50, "spine_05"), (1.56, "neck_01"), (1.61, "neck_02"), (1.66, "head")]
if "vw" not in globals():
    vw = {}
    for _bn, _d in assign.items():
        for _vi, _w in _d.items():
            vw.setdefault(_vi, {})[_bn] = _w
n_neck = n_chin = 0
for vi in range(nV):
    if vi in chain_vertices or vmacro[vi] not in ("TORSO", "HEAD"):
        continue
    zz, xx, yy = float(z[vi]), abs(float(x[vi])), float(y[vi])
    if zz < 1.50 or zz >= 1.70 or xx > 0.13:
        continue
    if yy < -0.09 and zz >= 1.62:                              # wajah depan / dagu
        vw[vi] = {"head": 1.0}
        n_chin += 1
    elif yy > -0.10 and xx < 0.12:                              # silinder leher
        if zz >= NECK_ANCHORS[-1][0]:
            vw[vi] = {"head": 1.0}
        else:
            for (z0, b0), (z1, b1) in zip(NECK_ANCHORS[:-1], NECK_ANCHORS[1:]):
                if z0 <= zz < z1:
                    t = (zz - z0) / (z1 - z0)
                    vw[vi] = {b0: 1 - t, b1: t}
                    break
        n_neck += 1
print(f"leher: {n_neck} vertex diinterpolasi spine_05>neck_01>neck_02>head; wajah/dagu kaku: {n_chin}")
assign = {}
for _vi, _wd in vw.items():
    for _bn, _w in _wd.items():
        if _w > 1e-5:
            assign.setdefault(_bn, {})[_vi] = float(_w)
# (blok twist di bawah membangun ulang vw dari assign; ia berjalan setelah perbaikan ini)

# ------------------------------------------------------------------ R3: bobot twist + sayap/kain ikut paha
vw = {}
for _bn, _d in assign.items():
    for _vi, _w in _d.items():
        vw.setdefault(_vi, {})[_bn] = _w
_TW = ("upperarm", "lowerarm", "thigh", "calf")
n_tw = 0
for vi, wd in vw.items():
    m = vmacro[vi]
    if vi in chain_vertices or is_armor[vi] or not (m.startswith("ARM") or m.startswith("LEG")):
        continue
    for bn in list(wd):
        base = bn.rsplit("_", 1)[0]
        if base in _TW and bn.endswith(("_l", "_r")):
            h_, t_ = SEG[bn]
            ab = np.array(t_[:]) - np.array(h_[:])
            tt = float(np.clip(((V[vi] - np.array(h_[:])) @ ab) / max(ab @ ab, 1e-12), 0.0, 1.0))
            k = float(np.clip((tt - 0.30) / 0.60, 0.0, 1.0)) * TWIST_FRAC
            if k > 1e-3:
                tw = f"{base}_twist_01_{bn[-1]}"
                wd[tw] = wd.get(tw, 0.0) + wd[bn] * k
                wd[bn] *= (1 - k)
                n_tw += 1
print(f"twist: {n_tw} vertex diberi bobot twist")
n_cp = 0
for vi, mm in chain_vertices.items():
    wd = vw[vi]
    if False:                                         # R3d: kain depan kini kinematik di blok bobot rantai (CLOTH_FAR_THIGH)
        f, parts = 0.0, {}
    else:
        continue                                      # R3c: sayap sudah berbobot kontinu menurut jarak ke paha (lihat blok bobot rantai)
    if f > 1e-3:
        for bn in list(wd):
            wd[bn] *= (1 - f)
        for bn, w in parts.items():
            wd[bn] = wd.get(bn, 0.0) + w
        n_cp += 1
print(f"kain/sayap ikut paha: {n_cp} vertex")
assign = {}
for _vi, _wd in vw.items():
    for _bn, _w in _wd.items():
        if _w > 1e-5:
            assign.setdefault(_bn, {})[_vi] = float(_w)


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
