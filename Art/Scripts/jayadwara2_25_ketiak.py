"""Jayadwara2 R8 — tutup lubang ketiak (temuan developer 13 Okt 2026: ketiak robek/bolong saat memukul di UE).

  blender --background Art/Blender/jayadwara2/jayadwara2_v06_revisi.blend --python Art/Scripts/jayadwara2_25_ketiak.py -- [--out PATH] [--rows N]
Hasil: Art/Blender/jayadwara2/jayadwara2_v07_ketiak.blend (v06 tidak ditimpa). Ukur/render: jayadwara2_24_armpit_audit.py di file hasil.

Penyebab: tiap ketiak punya SATU lubang tertutup (±5 x 13 x 11 cm, z 1,28–1,41) yang setengah tepinya makro ARM, setengah
TORSO — sisa pemisahan jahitan lengan–rusuk (R1–R3, docs/25). Di pose rest tersembunyi; lengan terangkat menarik tepi lengan
menjauh dari tepi badan sehingga lubang terbuka lebar (langit terlihat menembus).
Perbaikan: isi lubang dengan grid (grid fill: rel tepi lengan ↔ rel tepi badan) lalu bagi sisi silangnya jadi ROWS baris.
Vertex baru: bobot = interpolasi linier sisi lengan ↔ sisi badan (kulit ketiak melar merata, bukan lubang/selaput kaku);
UV = satu texel bodysuit tergelap dari tepi lubang (warna polos gelap, bukan atlas tercampur). Lalu bobot cincin sekitar
lubang (±RING cm) dihaluskan beberapa iterasi supaya regangan tersebar.
"""
import json
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


OUT = arg("--out", r"C:\repository\unreal_engine\jayadwara\Art\Blender\jayadwara2\jayadwara2_v07_ketiak.blend")
ROWS = arg("--rows", 4)           # baris di antara rel lengan dan rel badan
RING = arg("--ring", 0.05)        # m, radius cincin bobot yang dihaluskan di sekitar lubang
SMOOTH_IT = arg("--smooth", 6)
MIN_LOOP = 20                     # loop tepi lebih kecil dari ini bukan lubang ketiak (serpihan 3 vertex)

body = bpy.data.objects["JD2_Body"]
me = body.data
macro = json.loads(body["jd2_macro"])

bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
deform = bm.verts.layers.deform.verify()
uv_layer = bm.loops.layers.uv.active


# ------------------------------------------------------------------ cari loop lubang ketiak
def boundary_loops():
    adj = {}
    for e in bm.edges:
        if e.is_boundary:
            a, b = e.verts
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    seen, loops = set(), []
    for s in adj:
        if s in seen:
            continue
        comp, st = [], [s]
        while st:
            v = st.pop()
            if v in seen:
                continue
            seen.add(v)
            comp.append(v)
            st += adj[v]
        if len(comp) >= MIN_LOOP and all(len(adj[v]) == 2 for v in comp):
            loops.append(comp)
    return loops


loops = boundary_loops()
print(f"loop lubang: {[len(l) for l in loops]}")
if not loops:
    raise SystemExit("tidak ada lubang ketiak (sudah ditutup?)")

# texel bodysuit tergelap dari tepi lubang -> UV patch
img = next((n.image for m in me.materials if m and m.use_nodes for n in m.node_tree.nodes
            if n.type == "TEX_IMAGE" and n.image), None)
px = np.array(img.pixels[:], np.float32).reshape(img.size[1], img.size[0], -1) if img else None


def lum_at(uv):
    if px is None:
        return 0.0
    x = int(np.clip(uv.x, 0, 0.9999) * px.shape[1])
    y = int(np.clip(uv.y, 0, 0.9999) * px.shape[0])
    r, g, b = px[y, x, :3]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


# penanda elemen lama (wrapper Python BMVert tidak stabil setelah operator bmesh -> pakai layer data)
old_v = bm.verts.layers.int.new("jd2_old")
old_f = bm.faces.layers.int.new("jd2_old")
for v in bm.verts:
    v[old_v] = 1
for f in bm.faces:
    f[old_f] = 1
ring_seed = []
for _k in range(len(loops)):
    loop = boundary_loops()[0]
    loop_set = set(loop)
    edges = [e for e in bm.edges if e.is_boundary and e.verts[0] in loop_set and e.verts[1] in loop_set]
    n_arm = sum(1 for v in loop if str(macro[v.index]).startswith("ARM"))
    uvs = [l[uv_layer].uv.copy() for v in loop for l in v.link_loops]
    dark_uv = min(uvs, key=lum_at)
    mat_nr = next(iter(loop[0].link_faces)).material_index
    seed_co = [v.co.copy() for v in loop]

    # urutkan loop & taruh sudut grid di peralihan lengan->badan supaya rel = sisi lengan dan sisi badan
    order = [loop[0]]
    prev = None
    while len(order) < len(loop):
        cur = order[-1]
        nxt = next(o for e in cur.link_edges if e.is_boundary for o in e.verts
                   if o is not cur and o in loop_set and o is not prev)
        prev = cur
        order.append(nxt)
    is_arm = [str(macro[v.index]).startswith("ARM") for v in order]
    start = next(i for i in range(len(order)) if is_arm[i] and not is_arm[i - 1])
    order = order[start - 1:] + order[:start - 1]          # mulai di vertex badan terakhir sebelum lengan
    is_arm = is_arm[start - 1:] + is_arm[:start - 1]
    n = len(order)
    if n % 2:
        raise SystemExit(f"loop {n} vertex ganjil: grid fill butuh jumlah tepi genap")
    # rel lengan A (a1..ak) dan rel badan T (dibalik supaya T[0] bersebelahan dengan a1); dijahit "ritsleting" segitiga
    # menurut panjang busur ternormalisasi, lalu sisi silang lengan<->badan dibagi ROWS baris.
    A = [v for v, arm_ in zip(order, is_arm) if arm_]
    T = [v for v, arm_ in zip(order, is_arm) if not arm_]
    T = T[:1] + T[1:][::-1]                     # order[0] = badan sebelum a1; sisanya badan sesudah ak (dibalik)

    def arclen(chain):
        d = [0.0]
        for p, q in zip(chain, chain[1:]):
            d.append(d[-1] + (q.co - p.co).length)
        return [x / (d[-1] or 1.0) for x in d]

    ua, ut = arclen(A), arclen(T)
    new_faces, i, j = [], 0, 0
    while i < len(A) - 1 or j < len(T) - 1:
        if j == len(T) - 1 or (i < len(A) - 1 and ua[i + 1] <= ut[j + 1]):
            new_faces.append(bm.faces.new((A[i], A[i + 1], T[j])))
            i += 1
        else:
            new_faces.append(bm.faces.new((A[i], T[j + 1], T[j])))
            j += 1
    res = {"faces": new_faces}
    side = {v: a for v, a in zip(order, is_arm)}
    loop_edges = {e for e in bm.edges if e.verts[0] in loop_set and e.verts[1] in loop_set
                  and side.get(e.verts[0]) == side.get(e.verts[1])}
    cross = list({e for f in new_faces for e in f.edges if e not in loop_edges
                  and side.get(e.verts[0]) != side.get(e.verts[1])})
    bmesh.ops.subdivide_edges(bm, edges=cross, cuts=ROWS - 1, use_grid_fill=True, smooth=0.0)
    bm.verts.ensure_lookup_table()
    new_verts = [v for v in bm.verts if not v[old_v]]
    patch_faces = [f for f in bm.faces if not f[old_f]]
    for f in patch_faces:
        f.smooth = True
        f.material_index = mat_nr
        for l in f.loops:
            l[uv_layer].uv = dark_uv
    for v in new_verts:
        v[old_v] = 1
    for f in patch_faces:
        f[old_f] = 2                    # 2 = tambalan ketiak
    ring_seed += seed_co
    print(f"lubang {n} vertex (lengan {n_arm}): jahitan {len(res['faces'])} segitiga, +{len(new_verts)} vertex, "
          f"{len(patch_faces)} face patch, UV gelap lum {lum_at(dark_uv):.3f}")

patch = [f for f in bm.faces if f[old_f] == 2]
bmesh.ops.recalc_face_normals(bm, faces=patch)
new_verts_all = list({v for f in patch for v in f.verts})

# ------------------------------------------------------------------ bobot: vertex baru (sudah diinterpolasi subdivide) + halus cincin
co = np.array([v.co for v in bm.verts])
seed = np.array([tuple(c) for c in ring_seed])
dist = np.min(np.linalg.norm(co[:, None, :] - seed[None, :, :], axis=2), axis=1)
ring = [bm.verts[i] for i in np.nonzero(dist < RING)[0]]
ring_set = set(ring) | set(new_verts_all)
print(f"cincin halus: {len(ring_set)} vertex (radius {RING * 100:.0f} cm, {SMOOTH_IT} iterasi)")
for _ in range(SMOOTH_IT):
    upd = {}
    for v in ring_set:
        nb = [e.other_vert(v) for e in v.link_edges]
        acc = {}
        for u in [v] + nb:
            for g, w in u[deform].items():
                acc[g] = acc.get(g, 0.0) + w / (len(nb) + 1)
        upd[v] = acc
    for v, acc in upd.items():
        top = sorted(acc.items(), key=lambda kv: -kv[1])[:4]
        s = sum(w for _, w in top) or 1.0
        v[deform].clear()
        for g, w in top:
            if w / s > 0.01:
                v[deform][g] = w / s

bm.verts.layers.int.remove(old_v)
bm.faces.layers.int.remove(old_f)
bm.to_mesh(me)
me.update()
# makro vertex baru: ikut TORSO (dipakai skrip audit/pose untuk memisah badan vs kain)
macro += ["TORSO"] * (len(me.vertices) - len(macro))
body["jd2_macro"] = json.dumps(macro)
bm.free()
print(f"vertex {len(me.vertices)}, face {len(me.polygons)}")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("disimpan", OUT)
