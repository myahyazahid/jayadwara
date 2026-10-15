"""Resep perbaikan mesh ter-skin di satu wilayah, pasangan diagnosa_mesh.py. Bekerja pada .blend, hasil ke file BARU.

Headless:
  blender --background <masuk.blend> --python Art/Scripts/perbaiki_mesh.py -- <resep> --objek <mesh> --tulang a,b
        --out <keluar.blend> [--radius 0.12] [--iterasi 4] [--gabung]
Resep (kode sama dengan diagnosa.md & Hermes/panduan_kerja_claude.md):
  F1 tutup-lubang     isi HANYA loop yang ditunjuk: --pusat "x,y,z[;x,y,z]" (m, dari tabel loop diagnosa.md) [--toleransi 0.03]
                      [--maks-tepi 200]; tanpa --pusat mencetak daftar loop lalu berhenti. Bobot & UV dari tepi loop
  F2 samakan-jahitan  vertex kembar (posisi sama) di wilayah diberi bobot rata-rata yang SAMA; --gabung = sekalian digabung (UV tetap)
  F3 bobot-tetangga   bobot salah tulang. Tiga mode:
                        --sumber <model sehat .fbx/.blend> [--sumber-objek nama]  transfer bobot seluruh wilayah dari permukaan
                                 terdekat model sehat bernama tulang sama (TERBAIK untuk kerusakan luas; pola docs/25 R1)
                        --mode jarak     hitung ulang bobot wilayah dari jarak ke tulang wilayah/induk/anak, lalu dihaluskan
                        (default) tetangga  hanya vertex yang ditandai diganti rata-rata tetangga sehat (kerusakan kecil <= 30 vertex)
  F4 haluskan-bobot   haluskan bobot di wilayah (Laplacian sepanjang tepi) --iterasi kali; tulang di --kunci tidak disentuh
  F7 balik-normal     muka wilayah yang normalnya menghadap ke tulang dibalik
Setiap resep mencetak angka sebelum/sesudah. Bobot selalu dibersihkan: <= 4 influence, dinormalisasi.
Wilayah = vertex yang secara fisik dekat ruas --tulang (radius 0,12 m pada tinggi 1,806, ikut tinggi model di file).
File masuk TIDAK ditimpa (--out wajib dan harus beda).
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line
from mathutils.kdtree import KDTree

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RESEP = {"F1": "tutup-lubang", "F2": "samakan-jahitan", "F3": "bobot-tetangga", "F4": "haluskan-bobot", "F7": "balik-normal"}
if not argv or argv[0] not in list(RESEP) + list(RESEP.values()):
    print(__doc__)
    sys.exit(2)


def opt(name, default, cast=str):
    return cast(argv[argv.index(name) + 1]) if name in argv else default


resep = argv[0] if argv[0] in RESEP else {v: k for k, v in RESEP.items()}[argv[0]]
OBJ = opt("--objek", "")
TULANG = [t for t in opt("--tulang", "").split(",") if t]
OUT = opt("--out", "")
src = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
if not OUT or (src and Path(OUT).resolve() == src):
    print("GAGAL: --out wajib dan harus file baru (file masuk tidak boleh ditimpa)")
    sys.exit(2)
obj = bpy.data.objects.get(OBJ)
if obj is None or obj.type != "MESH":
    print(f"GAGAL: objek mesh '{OBJ}' tidak ada. Mesh di file: {[o.name for o in bpy.data.objects if o.type == 'MESH']}")
    sys.exit(2)
mod = next((m for m in obj.modifiers if m.type == "ARMATURE" and m.object), None)
if mod is None:
    print("GAGAL: objek tidak punya modifier Armature")
    sys.exit(2)
arm = mod.object
bad = [t for t in TULANG if t not in arm.data.bones]
if bad or not TULANG:
    print(f"GAGAL: --tulang tidak ada: {bad or '(kosong)'}")
    sys.exit(2)

MWo, MWa = obj.matrix_world, arm.matrix_world
me = obj.data
CO = [MWo @ v.co for v in me.vertices]
H_W = max(c.z for c in CO) - min(c.z for c in CO)
SCW = H_W / 1.806                                   # satuan dunia per "meter manusia"
RADIUS = opt("--radius", 0.12, float) * SCW
ITER = opt("--iterasi", 4, int)
KUNCI = [t for t in opt("--kunci", "").split(",") if t]


def ujung(b):                                       # sama dengan diagnosa_mesh.py: kepala anak utama, bukan ekor
    anak = [c for c in b.children if "twist" not in c.name and not c.name.startswith("ik_")]
    if anak:
        c = max(anak, key=lambda c: (c.head_local - b.head_local).length)
        if (c.head_local - b.head_local).length > 1e-9:
            return MWa @ c.head_local
    return MWa @ b.tail_local


SEG = {b.name: (MWa @ b.head_local, ujung(b)) for b in arm.data.bones if b.use_deform}


def dist_seg(p, a, b):
    t = min(max(intersect_point_line(p, a, b)[1], 0.0), 1.0)
    return (p - (a + (b - a) * t)).length


reg_seg = [SEG[t] if t in SEG else (MWa @ arm.data.bones[t].head_local, ujung(arm.data.bones[t])) for t in TULANG]
REG = {i for i, p in enumerate(CO) if min(dist_seg(p, a, b) for a, b in reg_seg) <= RADIUS}
names = {g.index: g.name for g in obj.vertex_groups}
print(f"resep {resep} ({RESEP[resep]}) objek {OBJ}, wilayah {TULANG}: {len(REG)} vertex, radius {RADIUS:.4f}")


def get_w(i):
    return {names[g.group]: g.weight for g in me.vertices[i].groups if g.weight > 1e-4 and g.group in names}


def set_w(i, w):
    # JEBAKAN BLENDER: ambil indeks grup dulu; menghapus sambil membaca v.groups menggeser elemen -> bobot lama tertinggal
    for gi in [g.group for g in me.vertices[i].groups]:
        obj.vertex_groups[gi].remove([i])
    w = {k: v for k, v in w.items() if math.isfinite(v) and v > 1e-6}
    top = sorted(w.items(), key=lambda kv: -kv[1])[:4]
    s = sum(v for _, v in top) or 1.0
    for bone, val in top:
        vg = obj.vertex_groups.get(bone) or obj.vertex_groups.new(name=bone)
        vg.add([i], val / s, "REPLACE")


def avg(ws):
    out = {}
    for w in ws:
        for k, v in w.items():
            out[k] = out.get(k, 0) + v / len(ws)
    return out


def neighbors():
    nb = {i: set() for i in range(len(me.vertices))}
    for e in me.edges:
        a, b = e.vertices
        nb[a].add(b)
        nb[b].add(a)
    return nb


dipakai = {max(w, key=w.get) for w in (get_w(i) for i in range(len(me.vertices))) if w}


def jauh(i):                                        # aturan sama dengan diagnosa_mesh.py
    w = get_w(i)
    if not w:
        return True
    dom = max(w, key=w.get)
    if dom not in SEG:
        return False
    p = CO[i]
    d_dom = dist_seg(p, *SEG[dom])
    d_near = min(dist_seg(p, *SEG[n]) for n in SEG if n in dipakai or n in TULANG)
    return d_dom > d_near + 0.25 * SCW and d_dom > 3 * max(d_near, 0.01 * SCW)


if resep == "F3":
    MODE = opt("--mode", "tetangga")
    SUMBER = opt("--sumber", "")
    if SUMBER:
        MODE = "sumber"
    bad_v = {i for i in REG if jauh(i)}
    print(f"sebelum: {len(bad_v)} vertex bobot ke tulang jauh (mode {MODE})")
    REG15 = {i for i, p in enumerate(CO) if min(dist_seg(p, a, b) for a, b in reg_seg) <= RADIUS * 1.5}
    luar = sum(1 for i in REG15 - REG if jauh(i))
    if luar:
        print(f"PERINGATAN: {luar} vertex rusak lagi di LUAR wilayah (radius x1,5). Kerusakan lebih luas dari wilayah; vertex rusak di "
              f"luar akan tetap menarik tepi. Ulangi dengan --radius {RADIUS / SCW * 1.5:.2f} (naikkan sampai peringatan ini hilang).")
    if MODE == "tetangga" and len(bad_v) > 30:
        print("PERINGATAN: > 30 vertex rusak = kerusakan luas; tetangganya kemungkinan ikut rusak. Pakai --sumber <model sehat> "
              "(terbaik) atau --mode jarak.")
    if MODE == "sumber":
        # transfer bobot dari permukaan terdekat model sehat (skeleton bernama sama): seluruh wilayah, bukan hanya yang ditandai
        from mathutils.bvhtree import BVHTree
        from mathutils.geometry import barycentric_transform
        sudah = set(bpy.data.objects)
        if SUMBER.lower().endswith(".fbx"):
            bpy.ops.import_scene.fbx(filepath=SUMBER)
        else:
            with bpy.data.libraries.load(SUMBER) as (src_d, dst_d):
                dst_d.objects = [n for n in src_d.objects]
            for o in dst_d.objects:
                if o is not None:
                    bpy.context.scene.collection.objects.link(o)
        baru = [o for o in bpy.data.objects if o not in sudah]
        obj = bpy.data.objects[OBJ]                 # impor membuat datablock baru: rujukan Python lama bisa basi -> ambil ulang
        me = obj.data
        arm = next(m for m in obj.modifiers if m.type == "ARMATURE").object
        src_o = next((o for o in baru if o.type == "MESH" and (not opt("--sumber-objek", "") or o.name == opt("--sumber-objek", ""))
                      and o.vertex_groups), None)
        if src_o is None:
            print("GAGAL: mesh ber-bobot tidak ditemukan di --sumber")
            sys.exit(2)
        bpy.context.view_layer.update()
        sco = [src_o.matrix_world @ v.co for v in src_o.data.vertices]
        sh = max(c.z for c in sco) - min(c.z for c in sco)
        k = H_W / sh                                # samakan tinggi sumber dengan model ini (tinggi dunia)
        sco = [Vector((c.x * k, c.y * k, c.z * k)) for c in sco]
        snames = {g.index: g.name for g in src_o.vertex_groups}
        sw = [{snames[g.group]: g.weight for g in v.groups if g.weight > 1e-4} for v in src_o.data.vertices]
        tris = []
        for f in src_o.data.polygons:
            vs = list(f.vertices)
            for j in range(1, len(vs) - 1):
                tris.append((vs[0], vs[j], vs[j + 1]))
        bvh = BVHTree.FromPolygons(sco, tris, all_triangles=True)
        hilang = set()
        for i in REG:
            loc, nrm, ti, dist = bvh.find_nearest(CO[i])
            if ti is None:
                continue
            a_, b_, c_ = tris[ti]
            bc = barycentric_transform(loc, sco[a_], sco[b_], sco[c_], Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
            if not all(math.isfinite(x) for x in bc) or sum(max(x, 0) for x in bc) <= 1e-9:
                # JEBAKAN: segitiga luas nol (umum di model Tripo/hasil decimate) -> barisentrik NaN -> bobot NaN -> vertex kosong.
                # Pakai vertex sumber terdekat saja.
                near_v = min((a_, b_, c_), key=lambda vi: (sco[vi] - loc).length)
                bc = [1.0 if vi == near_v else 0.0 for vi in (a_, b_, c_)]
            w = {}
            for vi, bw in zip((a_, b_, c_), bc):
                for bone, val in sw[vi].items():
                    if bone in arm.data.bones:
                        w[bone] = w.get(bone, 0) + max(bw, 0) * val
                    else:
                        hilang.add(bone)
            if w:
                set_w(i, w)
        for o in baru:
            bpy.data.objects.remove(o, do_unlink=True)
        obj = bpy.data.objects[OBJ]
        me = obj.data
        arm = next(m for m in obj.modifiers if m.type == "ARMATURE").object
        if hilang:
            print(f"tulang sumber yang tidak ada di model ini (dilewati): {sorted(hilang)[:10]}")
    elif MODE == "jarak":
        # bobot dihitung ulang dari jarak ke ruas tulang kandidat (tulang wilayah + induk + anak yang dipakai), 2 terdekat, lalu dihaluskan
        cand = set(TULANG)
        for t in TULANG:
            bn = arm.data.bones[t]
            if bn.parent:
                cand.add(bn.parent.name)
            cand.update(c.name for c in bn.children)
        cand = [c for c in cand if c in SEG and (c in dipakai or c in TULANG)]   # tulang wilayah selalu ikut (bisa saja tak dipakai krn rusak)
        print(f"tulang kandidat: {sorted(cand)}")
        for i in REG:
            d = sorted((dist_seg(CO[i], *SEG[c]), c) for c in cand)[:2]
            w = {c: 1 / max(dd, 0.005 * SCW) ** 4 for dd, c in d}
            set_w(i, w)
        nb = neighbors()
        for _ in range(3):
            cur = {i: get_w(i) for i in REG}
            for i in REG:
                ws = [cur.get(n) or get_w(n) for n in nb[i]]
                if ws:
                    set_w(i, avg([cur[i], avg(ws)]))
    else:
        nb = neighbors()
        sehat = [i for i in REG if i not in bad_v]
        kd = KDTree(len(sehat))
        for j, i in enumerate(sehat):
            kd.insert(CO[i], j)
        kd.balance()
        todo = set(bad_v)
        for _ in range(50):                         # rambatkan dari tepi area rusak ke dalam (tetangga sehat lebih dulu)
            if not todo:
                break
            nxt = set()
            for i in todo:
                ok = [n for n in nb[i] if n not in todo]
                if ok:
                    set_w(i, avg([get_w(n) for n in ok]))
                else:
                    nxt.add(i)
            if nxt == todo:                          # pulau tanpa tetangga sehat: pakai sehat terdekat (KD)
                for i in nxt:
                    set_w(i, avg([get_w(sehat[j]) for _, j, _ in kd.find_n(CO[i], 6)]))
                nxt = set()
            todo = nxt
    print(f"sesudah: {sum(jauh(i) for i in REG)} vertex bobot ke tulang jauh")

elif resep == "F2":
    idx = sorted(REG)
    kd = KDTree(len(idx))
    for j, i in enumerate(idx):
        kd.insert(CO[i], j)
    kd.balance()
    seen, groups = set(), []
    for i in idx:
        if i in seen:
            continue
        g = [idx[j] for _, j, _ in kd.find_range(CO[i], 0.0002 * SCW)]
        seen.update(g)
        if len(g) > 1:
            groups.append(g)
    beda = sum(1 for g in groups if len({tuple(sorted(get_w(i).items())) for i in g}) > 1)
    print(f"sebelum: {len(groups)} kelompok vertex kembar, {beda} berbobot beda")
    for g in groups:
        w = avg([get_w(i) for i in g])
        for i in g:
            set_w(i, w)
    if "--gabung" in argv:
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.ensure_lookup_table()
        vs = [bm.verts[i] for g in groups for i in g]
        n0 = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=vs, dist=0.0002 * SCW / max(obj.scale.x, 1e-9))
        bm.to_mesh(me)
        bm.free()
        print(f"digabung: {n0 - len(me.vertices)} vertex")
    if "--gabung" not in argv:                      # setelah digabung indeks bergeser; cek ulang lewat diagnosa_mesh.py
        print(f"sesudah: {sum(1 for g in groups if len({tuple(sorted(get_w(i).items())) for i in g}) > 1)} kelompok berbobot beda")

elif resep == "F4":
    nb = neighbors()

    def tajam():
        n = 0
        for e in me.edges:
            a, b = e.vertices
            if a in REG or b in REG:
                wa, wb = get_w(a), get_w(b)
                if any(abs(wa.get(k, 0) - wb.get(k, 0)) > 0.6 for k in set(wa) | set(wb)):
                    n += 1
        return n

    print(f"sebelum: {tajam()} tepi lompatan bobot > 0,6")
    for _ in range(ITER):
        cur = {i: get_w(i) for i in REG}
        for i in REG:
            if KUNCI and any(k in cur[i] and cur[i][k] > 0.99 for k in KUNCI):
                continue                            # bagian kaku (mis. gesper ke pelvis) tidak dilunakkan
            ws = [cur.get(n) or get_w(n) for n in nb[i]]
            if ws:
                w = avg([cur[i]] + [avg(ws)])         # 50% diri, 50% rata-rata tetangga
                set_w(i, w)
    print(f"sesudah: {tajam()} tepi lompatan bobot > 0,6 ({ITER} iterasi)")

elif resep == "F1":
    MAKS = opt("--maks-tepi", 200, int)
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bnd = [e for e in bm.edges if e.is_boundary and (e.verts[0].index in REG or e.verts[1].index in REG)]
    adj = {}
    for e in bnd:
        a, b = e.verts
        adj.setdefault(a, []).append(e)
        adj.setdefault(b, []).append(e)
    seen, loops = set(), []
    for e0 in bnd:
        if e0 in seen:
            continue
        comp, stack = [], [e0]
        seen.add(e0)
        while stack:
            e = stack.pop()
            comp.append(e)
            for v in e.verts:
                for e2 in adj[v]:
                    if e2 not in seen:
                        seen.add(e2)
                        stack.append(e2)
        loops.append(comp)
    print(f"sebelum: {len(loops)} loop tepi terbuka di wilayah, ukuran (tepi): {sorted((len(c) for c in loops), reverse=True)[:10]}")
    # WAJIB menunjuk loop: --pusat "x,y,z;x,y,z" (meter, dari tabel loop di diagnosa.md) --toleransi 0.03 (m). Tanpa itu tidak ada
    # yang diisi: tepi kerah/lengan baju/kantong juga loop terbuka, dan menutupnya merusak desain.
    pusat_arg = opt("--pusat", "")
    if not pusat_arg:
        print("GAGAL: F1 butuh --pusat \"x,y,z\" (salin dari kolom 'pusat (m)' tabel loop di diagnosa.md, hanya loop yang DIKELUHKAN "
              "dan bertanda merah di gambar). Daftar loop di wilayah ini:")
        for c in sorted(loops, key=len, reverse=True)[:12]:
            vs = {v for e in c for v in e.verts}
            cen = sum((MWo @ v.co for v in vs), Vector()) / len(vs) / (100.0 if H_W > 20 else 1.0)
            print(f"   {len(c):4d} tepi, pusat {tuple(round(x, 3) for x in cen)}")
        sys.exit(2)
    UNIT = 100.0 if H_W > 20 else 1.0             # file dari impor FBX = cm; file kerja Blender = m
    targets = [Vector(tuple(float(x) for x in t.split(","))) * UNIT for t in pusat_arg.split(";") if t.strip()]
    tol = opt("--toleransi", 0.03, float) * UNIT

    def pusat(c):
        vs = {v for e in c for v in e.verts}
        return sum((MWo @ v.co for v in vs), Vector()) / len(vs)

    isi = [c for c in loops if any((pusat(c) - t).length <= tol for t in targets) and len(c) <= MAKS]
    lewat = [len(c) for c in loops if any((pusat(c) - t).length <= tol for t in targets) and len(c) > MAKS]
    tak_ketemu = [tuple(round(x / UNIT, 3) for x in t) for t in targets if not any((pusat(c) - t).length <= tol for c in loops)]
    if tak_ketemu:
        print(f"PERINGATAN: tidak ada loop di dekat {tak_ketemu} (toleransi {tol / UNIT} m)")
    nf0 = len(bm.faces)
    for c in isi:
        bmesh.ops.holes_fill(bm, edges=c, sides=0)
    bm.faces.ensure_lookup_table()
    baru = [bm.faces[i] for i in range(nf0, len(bm.faces))]
    if baru:
        baru = bmesh.ops.triangulate(bm, faces=baru)["faces"]
        uv = bm.loops.layers.uv.active
        for f in baru:
            tet = [lf for e in f.edges for lf in e.link_faces if lf is not f and lf not in baru]
            if tet:
                f.material_index = tet[0].material_index
            if uv:                                  # UV tambalan = UV loop lama di vertex yang sama (tanpa atlas tercampur)
                for lp in f.loops:
                    lk = next((l2 for l2 in lp.vert.link_loops if l2.face not in baru), None)
                    if lk:
                        lp[uv].uv = lk[uv].uv
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.update()
    print(f"sesudah: {len(isi)} loop diisi ({len(baru)} segitiga baru); dilewati (> --maks-tepi {MAKS} tepi, kemungkinan tepi "
          f"baju/lengan baju yang disengaja): {lewat}")
    print("CATATAN: lubang lebar di antara dua bagian yang bergerak beda (ketiak lengan-badan) lebih baik dijahit 'ritsleting' "
          "dengan baris tambahan (lihat Art/Scripts/jayadwara2_25_ketiak.py); holes_fill tidak menambah vertex, jadi tambalan "
          "besar akan melar kaku. Selalu jalankan F4 setelah F1.")

elif resep == "F7":
    n = 0
    bm = bmesh.new()
    bm.from_mesh(me)
    for f in bm.faces:
        if not all(v.index in REG for v in f.verts):
            continue
        w = get_w(f.verts[0].index)
        if not w:
            continue
        dom = max(w, key=w.get)
        if dom not in SEG:
            continue
        c = MWo @ f.calc_center_median()
        a, b = SEG[dom]
        t = min(max(intersect_point_line(c, a, b)[1], 0.0), 1.0)
        out = c - (a + (b - a) * t)
        if out.length < 0.01 * SCW:
            continue
        nrm = (MWo.to_3x3() @ f.normal).normalized()
        if nrm.dot(out.normalized()) < -0.3:
            f.normal_flip()
            n += 1
    bm.to_mesh(me)
    bm.free()
    print(f"dibalik: {n} muka. PERIKSA gambar: kantong/tali/lapisan dalam boleh menghadap ke dalam; kalau yang terbalik justru "
          "itu, kembali ke file sebelumnya.")

# bersihkan bobot di wilayah
for i in REG:
    if i < len(me.vertices):
        w = get_w(i)
        if w:
            set_w(i, w)
bpy.ops.wm.save_as_mainfile(filepath=str(Path(OUT).resolve()), copy=False)
print(f"disimpan: {OUT}. Lanjut: export FBX lalu diagnosa_mesh.py --sebelum <dir diagnosa lama> (+ audit & banding untuk regresi)")
