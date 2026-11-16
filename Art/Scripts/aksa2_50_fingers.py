"""Aksa2 — perbaikan jari tangan yang menyatu (opsi A, docs/19 Aksa2).

Masalah (diukur 17 Okt 2026): mesh SK_Aksa2 hasil Tripo punya jari yang melebur jadi satu
balok (area tangan hanya 927 vertex; v1 SK_Aksa 4.623). Tulang jari tetap ada dan berbobot,
jadi saat animasi mengepal jari, "selaput" antar jari tertarik sampai 4,91x (v1: 2,03x) ->
tangan terlihat pipih/gepih. Tulang ujung jari (index_03_l) bahkan 0 vertex berbobot.

Perbaikan:
  1. Potong balok jari yang menyatu di bidang buku jari (bisect + fill) per sisi.
  2. Bangun ulang 4 jari (telunjuk, tengah, manis, kelingking) sebagai tabung tertutup
     mengikuti tulang jari Manny, dengan UV diambil dari vertex telapak terdekat dan
     bobot skinning per ruas tulang (blend di sendi).
  3. Join ke AK2_Source (shape key wajah tetap utuh: vertex baru delta 0 di semua key).
  4. Simpan ke Art/Blender/aksa2/aksa2_v08_fingers.blend (v07 tidak diubah).

Pakai:
  blender --background --factory-startup --python Art/Scripts/aksa2_50_fingers.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector, kdtree

ROOT = Path(__file__).resolve().parents[1].parent
BLEND_IN = ROOT / "Art" / "Blender" / "aksa2" / "aksa2_v07_morph.blend"
BLEND_OUT = ROOT / "Art" / "Blender" / "aksa2" / "aksa2_v08_fingers.blend"

SIDES = ("l", "r")
FINGERS = ("index", "middle", "ring", "pinky")
# radius pangkal tiap jari (meter) — diukur dari lebar buku jari Manny
RADIUS = {"index": 0.0082, "middle": 0.0086, "ring": 0.0080, "pinky": 0.0068}
RING_SEG = 12            # segmen keliling tabung
CUT_OFFSET = -0.006      # potong 0,6 cm di BELAKANG buku jari: tepi sarung menutup pangkal jari
THUMB_EXCLUDE = 0.018    # vertex lebih dekat dari 1,8 cm ke tulang jempol tidak ikut dipotong
BASE_EMBED = 0.014       # pangkal jari masuk 1,4 cm ke dalam telapak (biar tidak bolong)
RIM_DEPTH = 0.0035       # ketebalan tepi sarung tangan (3,5 mm)
RIM_SCALE = 0.93         # tepi dikecilkan 7% saat masuk
DOME = 0.007             # tonjolan bantalan buku jari (7 mm) di bekas potongan
UV_NAME = None           # diisi dari mesh


def log(msg):
    print(f"[jari] {msg}")


def open_blend():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND_IN))
    mesh = bpy.data.objects["AK2_Source"]
    arm = bpy.data.objects["AK2_Armature"]
    return mesh, arm


def bone_points(arm):
    """Kembalikan dict tulang -> (head, tail) di ruang mesh (meter)."""
    out = {}
    for b in arm.data.bones:
        out[b.name] = (b.head_local.copy(), b.tail_local.copy())
    return out


def seg_dist(p, a, b):
    ab = b - a
    if ab.length_squared < 1e-12:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab * t)).length


def thumb_dist(p, bones, side):
    d = 1e9
    j = finger_joints(bones, "thumb", side)
    for i in range(3):
        d = min(d, seg_dist(p, j[i], j[i + 1]))
    return d


def finger_joints(bones, finger, side):
    """Sendi jari sebenarnya ada di head tiap tulang.

    Rig Aksa2 punya celah antara tail dan head tulang berikutnya (5-9 cm), jadi
    tail TIDAK boleh dipakai sebagai sendi berikutnya.
    """
    return [bones[f"{finger}_01_{side}"][0],
            bones[f"{finger}_02_{side}"][0],
            bones[f"{finger}_03_{side}"][0],
            bones[f"{finger}_03_{side}"][1]]


def knuckle_plane(bones, side):
    """Bidang buku jari: pusat = rata-rata sendi pangkal jari, normal = arah jari rata-rata."""
    pts = [finger_joints(bones, f, side)[0] for f in FINGERS]
    center = sum(pts, Vector()) / len(pts)
    dirs = []
    for f in FINGERS:
        j = finger_joints(bones, f, side)
        dirs.append((j[-1] - j[0]).normalized())
    normal = sum(dirs, Vector()) / len(dirs)
    normal.normalize()
    return center + normal * CUT_OFFSET, normal, pts


def cut_fused_fingers(mesh, arm, side):
    """Potong balok jari yang menyatu pada satu sisi, isi lubangnya.

    Kembalikan daftar (posisi, uv) vertex blok jari asli — dipakai untuk transfer UV
    supaya warna jari baru sama dengan jari di tekstur aslinya.
    """
    bones = bone_points(arm)
    center, normal, knuckles = knuckle_plane(bones, side)

    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='DESELECT')

    me = mesh.data

    def side_of_hand(p):
        return p.x > 0 if side == "l" else p.x < 0

    def hand_region(p):
        return side_of_hand(p) and abs(p.x) >= 0.40 and 0.85 < p.z < 1.10

    bm = bmesh.from_edit_mesh(me)
    bm.verts.ensure_lookup_table()
    cand = [v for v in bm.verts if hand_region(v.co)]
    for v in cand:
        v.select = True
    for f in bm.faces:
        if any(v.select for v in f.verts):
            f.select = True
    bmesh.update_edit_mesh(me)

    # 1) potong bersih sepanjang bidang buku jari (tanpa menghapus apa pun)
    bpy.ops.mesh.bisect(plane_co=center, plane_no=normal,
                        clear_outer=False, clear_inner=False, use_fill=False, threshold=1e-06)

    # 2) kumpulkan blok jari asli (di luar bidang, bukan jempol) + UV-nya
    bm = bmesh.from_edit_mesh(me)
    bm.verts.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.active
    block = []
    kill = []
    for v in bm.verts:
        if not hand_region(v.co):
            continue
        if (v.co - center).dot(normal) <= 1e-5:
            continue
        if thumb_dist(v.co, bones, side) < THUMB_EXCLUDE:
            continue
        kill.append(v)
        uv = None
        for f in v.link_faces:
            for loop in f.loops:
                if loop.vert is v and uv_layer is not None:
                    uv = loop[uv_layer].uv.copy()
                    break
            if uv:
                break
        if uv is not None:
            block.append((v.co.copy(), uv))

    if not kill:
        bpy.ops.object.mode_set(mode='OBJECT')
        log(f"sisi {side}: tidak ada blok jari, dilewati")
        return block

    # 3) hapus blok jari, lalu beri ketebalan tepi + isi lubangnya
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    # PENTING: hanya tepi di sekitar potongan tangan yang boleh dijahit.
    # Kalau semua tepi terbuka mesh diambil, lubang mata/rambut ikut tertutup
    # dan muncul bidang hitam di wajah.
    def near_cut(e):
        m = (e.verts[0].co + e.verts[1].co) * 0.5
        return (m - center).length < 0.13 and abs(m.x) > 0.38

    boundary = [e for e in bm.edges if e.is_boundary and near_cut(e)]
    if boundary:
        # Tepi sarung tangan diberi ketebalan (ditarik masuk 3,5 mm lalu dikecilkan
        # 7%) supaya tidak terlihat seperti potongan kertas yang sobek.
        ret = bmesh.ops.extrude_edge_only(bm, edges=boundary)
        new_verts = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMVert)]
        if new_verts:
            ctr = sum((v.co for v in new_verts), Vector()) / len(new_verts)
            for v in new_verts:
                v.co = ctr + (v.co - ctr) * RIM_SCALE - normal * RIM_DEPTH
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        inner = [e for e in bm.edges if e.is_boundary and near_cut(e)]
        if inner:
            # simpan UV di tepi potongan (warna sarung tangan) sebagai acuan
            uv_ref = []
            if uv_layer is not None:
                for v in {v for e in inner for v in e.verts}:
                    for f in v.link_faces:
                        hit = None
                        for lp in f.loops:
                            if lp.vert is v:
                                hit = lp[uv_layer].uv.copy()
                                break
                        if hit is not None:
                            uv_ref.append((v.co.copy(), hit))
                            break
            before = set(bm.faces)
            bmesh.ops.holes_fill(bm, edges=inner, sides=0)
            new_faces = [f for f in bm.faces if f not in before]
            if new_faces:
                # bekas potongan jangan datar: tonjolkan sedikit (bantalan buku jari)
                res = bmesh.ops.poke(bm, faces=new_faces)
                for v in res['verts']:
                    v.co = v.co + normal * DOME
            # semua face baru wajib berwarna sarung tangan, bukan kulit
            if uv_ref and uv_layer is not None:
                for f in [f for f in bm.faces if f not in before]:
                    for lp in f.loops:
                        co = lp.vert.co
                        best = min(uv_ref, key=lambda t: (t[0] - co).length)
                        lp[uv_layer].uv = best[1]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.update_edit_mesh(me)
    log(f"sisi {side}: hapus {len(kill)} vertex blok jari, rim {len(boundary)} edge batas")

    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    log(f"sisi {side}: total vertex sekarang {len(me.vertices)}")
    return block


def find_base_color_image(me):
    """Cari tekstur yang masuk ke Base Color Principled BSDF."""
    for m in me.materials:
        if not m or not m.node_tree:
            continue
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                for link in n.inputs["Base Color"].links:
                    src = link.from_node
                    if src.type == 'TEX_IMAGE' and src.image:
                        return src.image
    return None


def pick_glove_uv(me, vert_uv, img, side="r"):
    """Pilih titik UV di sarung tangan yang benar-benar hitam dan rata.

    Kalau dipakai titik di batas tekstur, jendela UV kecil di pangkal jari bisa
    menyentuh piksel kulit dan muncul garis cokelat di atas sarung hitam.
    """
    import numpy as np
    W, H = img.size
    buf = np.empty(W * H * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    buf = buf.reshape(H, W, 4)

    HALF = 20          # jendela lebih lebar dari lebar patch UV jari (±0,012)
    best_score, best_uv, best_rgb = -1e9, None, None
    for v in me.vertices:
        if (v.co.x > 0) != (side == "l"):
            continue
        if not (0.20 < abs(v.co.x) < 0.45 and 0.85 < v.co.z < 1.25):
            continue
        uv = vert_uv.get(v.index)
        if uv is None:
            continue
        x = int(min(max(uv.x, 0.02), 0.98) * W)
        y = int(min(max(uv.y, 0.02), 0.98) * H)
        if x - HALF < 0 or y - HALF < 0 or x + HALF >= W or y + HALF >= H:
            continue
        win = buf[y - HALF:y + HALF + 1, x - HALF:x + HALF + 1, :3]
        mean = win.reshape(-1, 3).mean(axis=0)
        std = float(win.reshape(-1, 3).std(axis=0).max())
        lum = float(0.2126 * mean[0] + 0.7152 * mean[1] + 0.0722 * mean[2])
        if lum > 0.16:                                # harus gelap (sarung hitam)
            continue
        score = -std * 6.0 - lum
        if score > best_score:
            best_score, best_uv, best_rgb = score, uv.copy(), mean
    if best_uv is None:
        best_uv, best_rgb = Vector((0.5, 0.5)), (0, 0, 0)
    log("UV sarung jari (%s): (%.3f, %.3f) warna %.2f/%.2f/%.2f skor %.3f" % (
        side, best_uv.x, best_uv.y, best_rgb[0], best_rgb[1], best_rgb[2], best_score))
    return best_uv


def pick_skin_uv(me, vert_uv, img, side="r"):
    """Pilih satu titik UV di kulit lengan yang areanya rata, untuk seluruh jari.

    UV hasil transfer dari blok jari asli jatuh di area metal/kain sehingga jari
    belang-belang. Dipilih titik yang lingkungan 11x11 px-nya seragam (standar
    deviasi rendah) dan warnanya seperti kulit, supaya jari berwarna rata.
    """
    import numpy as np
    W, H = img.size
    buf = np.empty(W * H * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    buf = buf.reshape(H, W, 4)

    HALF = 5
    best_score, best_uv, best_rgb = -1e9, None, None
    for v in me.vertices:
        if (v.co.x > 0) != (side == "l"):
            continue
        if not (0.20 < abs(v.co.x) < 0.42 and 0.98 < v.co.z < 1.22):
            continue
        uv = vert_uv.get(v.index)
        if uv is None:
            continue
        x = int(min(max(uv.x, 0.02), 0.98) * W)
        y = int(min(max(uv.y, 0.02), 0.98) * H)
        if x - HALF < 0 or y - HALF < 0 or x + HALF >= W or y + HALF >= H:
            continue
        win = buf[y - HALF:y + HALF + 1, x - HALF:x + HALF + 1, :3]
        mean = win.reshape(-1, 3).mean(axis=0)
        std = float(win.reshape(-1, 3).std(axis=0).max())
        lum = float(0.2126 * mean[0] + 0.7152 * mean[1] + 0.0722 * mean[2])
        if not (0.18 < lum < 0.65):
            continue
        if not (mean[0] >= mean[1] >= mean[2]):      # kulit: merah >= hijau >= biru
            continue
        score = (mean[0] - mean[2]) * 2.0 - std * 4.0 - abs(lum - 0.42)
        if score > best_score:
            best_score, best_uv, best_rgb = score, uv.copy(), mean
    if best_uv is None:
        best_uv, best_rgb = Vector((0.5, 0.5)), (0, 0, 0)
    log("UV kulit jari (%s): (%.3f, %.3f) warna %.2f/%.2f/%.2f skor %.3f" % (
        side, best_uv.x, best_uv.y, best_rgb[0], best_rgb[1], best_rgb[2], best_score))
    return best_uv


def make_finger_obj(name, bones, side, finger, uv_layer_name, skin_uv, glove_uv=None):
    """Bangun satu jari sebagai objek tabung tertutup mengikuti tulang.

    Tiap ruas dibagi 3 ring (bukan 1) supaya lekukannya halus, ditambah ujung membulat
    (3 ring mengecil + titik kutub) supaya tidak terlihat seperti cakar.
    """
    chain_bones = [f"{finger}_01_{side}", f"{finger}_02_{side}", f"{finger}_03_{side}"]
    joints = finger_joints(bones, finger, side)
    knuckle = joints[0]
    frames = []
    for i in range(3):
        a, b = joints[i], joints[i + 1]
        frames.append((a, b, (b - a).normalized()))

    r0 = RADIUS[finger]
    d0 = frames[0][2]

    # ---- daftar ring: (posisi, radius, bobot) ----
    # pangkal: masuk ke dalam telapak, bobotnya hampir seluruhnya ikut tangan
    # (bantalan buku jari), lalu pindah bertahap ke tulang jari supaya tidak
    # terjadi regangan besar saat jari menekuk
    rings = []
    rings.append((knuckle - d0 * BASE_EMBED, r0 * 1.00,
                  [(f"hand_{side}", 1.0)]))
    rings.append((knuckle - d0 * 0.005, r0 * 1.06,
                  [(f"hand_{side}", 0.75), (chain_bones[0], 0.25)]))
    rings.append((knuckle + d0 * max(CUT_OFFSET, 0.004), r0 * 1.14,
                  [(f"hand_{side}", 0.50), (chain_bones[0], 0.50)]))

    SUB = 3                      # ring per ruas
    total = sum((b - a).length for a, b, _d in frames)
    travelled = 0.0
    for i, (a, b, d) in enumerate(frames):
        seg = (b - a).length
        for k in range(1, SUB + 1):
            t = k / SUB
            pos = a + (b - a) * t
            travelled += seg / SUB
            s = travelled / total                     # 0..1 sepanjang jari
            r = r0 * (1.0 - 0.30 * s)                 # mengecil ke ujung
            if k < SUB:
                r *= 1.02                              # sedikit menggembung di tengah ruas
            # bobot: campur ke tulang berikutnya secara bertahap di dekat sendi
            cur = chain_bones[i]
            nxt = chain_bones[i + 1] if i + 1 < len(chain_bones) else None
            if i == 0 and t <= 0.34:
                w = [(f"hand_{side}", 0.20), (cur, 0.80)]
            elif nxt and t >= 0.99:
                w = [(cur, 0.55), (nxt, 0.45)]
            elif nxt and t >= 0.85:
                w = [(cur, 0.75), (nxt, 0.25)]
            elif nxt and t >= 0.5:
                w = [(cur, 0.90), (nxt, 0.10)]
            else:
                w = [(cur, 1.0)]
            rings.append((pos, r, w))

    # ujung membulat: belahan bola (3 ring mengecil + titik kutub)
    tip_pos = frames[-1][1]
    tip_dir = frames[-1][2]
    r_tip = rings[-1][1]
    for ang in (32.0, 56.0, 76.0):
        a_rad = math.radians(ang)
        rings.append((tip_pos + tip_dir * (r_tip * math.sin(a_rad)),
                      r_tip * math.cos(a_rad),
                      [(chain_bones[2], 1.0)]))

    # frame keliling: pakai sumbu tulang pertama, konsisten sepanjang jari
    ref = frames[0][2]
    up = Vector((0, 0, 1))
    if abs(ref.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    xa = ref.cross(up).normalized()
    ya = ref.cross(xa).normalized()

    verts = []
    ring_idx = []
    for pos, r, _w in rings:
        idx = []
        for k in range(RING_SEG):
            a = 2 * math.pi * k / RING_SEG
            verts.append(pos + xa * (math.cos(a) * r) + ya * (math.sin(a) * r))
            idx.append(len(verts) - 1)
        ring_idx.append(idx)

    # titik kutub ujung jari
    verts.append(tip_pos + tip_dir * r_tip)
    tip_i = len(verts) - 1

    faces = []
    for i in range(len(ring_idx) - 1):
        a, b = ring_idx[i], ring_idx[i + 1]
        for k in range(RING_SEG):
            k2 = (k + 1) % RING_SEG
            faces.append((a[k], a[k2], b[k2], b[k]))
    for k in range(RING_SEG):
        k2 = (k + 1) % RING_SEG
        faces.append((ring_idx[-1][k], ring_idx[-1][k2], tip_i))
    faces.append(tuple(reversed(ring_idx[0])))   # tutup pangkal (di dalam telapak)

    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)

    # UV: satu area kulit yang rata, dipetakan mengikuti tabung jari
    uv = me.uv_layers.new(name=uv_layer_name)
    PATCH = 0.012
    vmap = {}
    for ri, ring in enumerate(ring_idx):
        # dua ring pertama ada di dalam sarung tangan -> warnanya ikut sarung
        base = glove_uv if (glove_uv is not None and ri <= 1) else skin_uv
        for k, vi in enumerate(ring):
            vmap[vi] = (base.x + PATCH * (k / RING_SEG),
                        base.y + PATCH * (ri / max(1, len(ring_idx) - 1)))
    vmap[tip_i] = (skin_uv.x + PATCH * 0.5, skin_uv.y + PATCH)
    for poly in me.polygons:
        for li in poly.loop_indices:
            uv.data[li].uv = vmap[me.loops[li].vertex_index]
        poly.use_smooth = True

    # bobot skinning
    groups = {}
    for gname, _ in [(f"hand_{side}", 0), (chain_bones[0], 0), (chain_bones[1], 0), (chain_bones[2], 0)]:
        groups[gname] = ob.vertex_groups.get(gname) or ob.vertex_groups.new(name=gname)
    for ri, (_pos, _r, w) in enumerate(rings):
        for vi in ring_idx[ri]:
            for gname, weight in w:
                groups[gname].add([vi], weight, 'REPLACE')
    for gname, weight in [(chain_bones[2], 1.0)]:
        groups[gname].add([tip_i], weight, 'REPLACE')
    return ob


def fix_zero_uv(mesh, kd, uv_by_vert):
    """Permukaan hasil potong (holes_fill) punya UV 0,0 — ganti dengan UV vertex terdekat."""
    me = mesh.data
    uv_layer = me.uv_layers[0]
    fixed = 0
    for poly in me.polygons:
        loops = list(poly.loop_indices)
        if not loops:
            continue
        if any(uv_layer.data[li].uv.length > 1e-6 for li in loops):
            continue
        # UV semua loop nol -> face baru dari fill
        center = sum((me.vertices[me.loops[li].vertex_index].co for li in loops), Vector()) / len(loops)
        _co, ki, _d = kd.find(center)
        uv = uv_by_vert[ki]
        for li in loops:
            uv_layer.data[li].uv = uv
        fixed += 1
    if fixed:
        log(f"  UV permukaan potongan diperbaiki: {fixed} face")


def build_fingers(mesh, arm, blocks):
    global UV_NAME
    bones = bone_points(arm)
    me = mesh.data
    UV_NAME = me.uv_layers[0].name if me.uv_layers else "UVMap"
    log(f"UV layer: {UV_NAME}")

    uv_layer = me.uv_layers[0]
    vert_uv = {}
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            vert_uv.setdefault(vi, uv_layer.data[li].uv.copy())

    new_objs = []
    for side in SIDES:
        center, normal, _k = knuckle_plane(bones, side)
        palm_verts = []
        for v in me.vertices:
            if (v.co.x > 0) != (side == "l"):
                continue
            if abs(v.co.x) < 0.40:
                continue
            if not (0.85 < v.co.z < 1.10):
                continue
            if (v.co - center).dot(normal) > 0.0:
                continue          # di depan bidang potong
            if thumb_dist(v.co, bones, side) < THUMB_EXCLUDE:
                continue
            palm_verts.append(v.index)
        log(f"sisi {side}: {len(palm_verts)} vertex telapak untuk transfer UV")

        # Telapak di dekat buku jari masih berbobot tulang jari (sisa rig lama).
        # Kalau dibiarkan, telapak ikut terarik saat jari menekuk -> regangan besar.
        # Pindahkan bobot tulang jari (kecuali jempol) ke tulang tangan.
        FB = tuple(f"{f}_{seg}_{side}" for f in ("index", "middle", "ring", "pinky")
                   for seg in ("01", "02", "03"))
        hand_g = mesh.vertex_groups.get(f"hand_{side}")
        if hand_g is None:
            hand_g = mesh.vertex_groups.new(name=f"hand_{side}")
        moved = 0
        for v in me.vertices:
            vi = v.index
            take = []
            total = 0.0
            for g in v.groups:
                gname = mesh.vertex_groups[g.group].name
                if any(gname.startswith(b) for b in FB):
                    take.append(g.group)
                    total += g.weight
            if not take:
                continue
            for gi in take:
                mesh.vertex_groups[gi].remove([vi])
            hand_g.add([vi], total, 'ADD')
            moved += 1
        log(f"sisi {side}: {moved} vertex telapak dipindah dari tulang jari ke hand_{side}")

        kd = kdtree.KDTree(len(palm_verts))
        uv_by_vert = []
        for i, vi in enumerate(palm_verts):
            kd.insert(me.vertices[vi].co, i)
            uv_by_vert.append(vert_uv.get(vi, (0.5, 0.5)))
        kd.balance()
        fix_zero_uv(mesh, kd, uv_by_vert)

        # UV jari baru: pakai satu area kulit lengan supaya warnanya seragam
        img = find_base_color_image(me)
        skin_uv = pick_skin_uv(me, vert_uv, img, side) if img else Vector((0.5, 0.5))
        log(f"sisi {side}: UV kulit dipakai untuk semua jari")

        # UV sarung tangan (hitam rata) untuk pangkal jari
        glove_uv = pick_glove_uv(me, vert_uv, img, side) if img else Vector((0.0, 0.0))

        for f in FINGERS:
            ob = make_finger_obj(f"JD_FINGER_{f}_{side}", bones, side, f, UV_NAME, skin_uv, glove_uv)
            # pakai material body (slot 0) supaya saat join tidak jadi slot kosong
            for m in mesh.data.materials:
                ob.data.materials.append(m)
            new_objs.append(ob)
            log(f"  jari {f}_{side}: {len(ob.data.vertices)} vertex, {len(ob.data.polygons)} face")

    # join ke AK2_Source
    bpy.ops.object.select_all(action='DESELECT')
    for o in new_objs:
        o.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.join()
    log(f"join selesai: AK2_Source = {len(mesh.data.vertices)} vertex, {len(mesh.data.polygons)} face")

    # buang slot material kosong sisa join, arahkan face-nya ke slot 0
    me2 = mesh.data
    empty = [i for i, m in enumerate(me2.materials) if m is None]
    if empty:
        for p in me2.polygons:
            if p.material_index in empty:
                p.material_index = 0
        for i in reversed(empty):
            me2.materials.pop(index=i)
        log(f"slot material kosong dibuang: {empty}")
    keys = [k.name for k in mesh.data.shape_keys.key_blocks] if mesh.data.shape_keys else []
    log(f"shape key: {len(keys)} {keys}")


def main():
    mesh, arm = open_blend()
    log(f"mulai: {len(mesh.data.vertices)} vertex, {len(mesh.data.polygons)} face")

    blocks = {}
    for side in SIDES:
        blocks[side] = cut_fused_fingers(mesh, arm, side)

    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    build_fingers(mesh, arm, blocks)

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    log(f"disimpan: {BLEND_OUT}")


main()
