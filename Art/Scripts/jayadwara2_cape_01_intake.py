"""Jubah Jayadwara2 J0 — impor jubah Tripo, normalisasi, fit kasar ke badan, ukur titik kait (docs/26 J0).

Jalankan headless di atas file rig final (file itu TIDAK ditimpa):
  blender --background Art/Blender/jayadwara2_v05_rig_r3.blend --python Art/Scripts/jayadwara2_cape_01_intake.py -- \
      [--src Art/Source/jayadwara2_cape_tripo_v01.glb] [--out Art/Blender/jayadwara2_cape_v00_intake.blend] \
      [--collar-z 1.60] [--hem-z 0.10] [--rot-z 90] [--clear 0.02]
Hasil: collection `10_Cape` berisi `JD2_Cape_Source` (jubah ter-fit) + empty `JD2C_ANCHOR_*` (titik kait).

Normalisasi:
- GLB Tripo jubah (cap02) menghadap -X (bagian depan terbuka di -X) -> --rot-z 90 supaya menghadap -Y.
- Skala tinggi: puncak kerah = --collar-z (K9: kerah <= dagu, dagu Jayadwara2 ±1,64 m), ujung runcing terbawah = --hem-z (mata kaki).
- Depan dibuka (--open-deg): Tripo membuat mantel tertutup, konsep terbuka memperlihatkan zirah dada.
- Skala lebar/kedalaman & geser Y: --fit (default 1.1,1.25,0.02 dipilih visual di J0 dari 3 kandidat). Fit global
  TIDAK bisa membebaskan jubah dari badan (puncak jubah tenggelam di pelat punggung/pauldron) -> fit lokal di J1.
  Laporan jarak mengecualikan lengan; tanda jarak tidak andal di lembar kain tipis badan (sayap).
Sumber tidak diubah.
"""
import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--src", default=str(ROOT / "Art" / "Source" / "jayadwara2_cape_tripo_v01.glb"))
ap.add_argument("--out", default=str(ROOT / "Art" / "Blender" / "jayadwara2_cape_v00_intake.blend"))
ap.add_argument("--collar-z", type=float, default=1.60)
ap.add_argument("--hem-z", type=float, default=0.10)
ap.add_argument("--rot-z", type=float, default=90.0)
ap.add_argument("--clear", type=float, default=0.02, help="m, jarak bebas minimal jubah ke badan (di bawah kerah)")
ap.add_argument("--merge-dist", type=float, default=0.0005)
ap.add_argument("--fit", default="1.1,1.25,0.02",
                help="sx,sy,dy (relatif skala tinggi, geser Y m); 'search' = cari grid jarak bebas. Default dipilih visual di J0")
ap.add_argument("--open-deg", type=float, default=55.0, help="setengah sudut bukaan depan (0 = jubah tertutup apa adanya)")
ap.add_argument("--collar-band", type=float, default=0.07, help="m di bawah puncak kerah yang tidak dipotong (pita kerah)")
args = ap.parse_args(argv)

SRC, OUT = Path(args.src), Path(args.out)
assert SRC.exists(), f"tidak ada: {SRC}"
assert "jayadwara2_v05_rig_r3" not in OUT.name, "jangan menimpa file rig final"
body = bpy.data.objects["JD2_Body"]
arm = bpy.data.objects["JD2_Armature"]

# ------------------------------------------------------------------ impor & gabung
coll = bpy.data.collections.get("10_Cape") or bpy.data.collections.new("10_Cape")
if coll.name not in bpy.context.scene.collection.children:
    (bpy.data.collections.get("JD2_Jayadwara") or bpy.context.scene.collection).children.link(coll)
for o in list(coll.objects):
    bpy.data.objects.remove(o, do_unlink=True)
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(SRC))
new = [o for o in bpy.data.objects if o not in before]
mesh_obs = [o for o in new if o.type == "MESH"]
assert mesh_obs, "GLB tanpa mesh"
for o in mesh_obs:
    mw = o.matrix_world.copy()
    o.parent = None
    o.modifiers.clear()
    o.data.transform(mw)
    o.matrix_world = Matrix.Identity(4)
for o in new:
    if o not in mesh_obs:
        bpy.data.objects.remove(o, do_unlink=True)
cape = mesh_obs[0]
if len(mesh_obs) > 1:
    with bpy.context.temp_override(active_object=cape, selected_editable_objects=mesh_obs, selected_objects=mesh_obs):
        bpy.ops.object.join()
cape.name = cape.data.name = "JD2_Cape_Source"
for c in list(cape.users_collection):
    c.objects.unlink(cape)
coll.objects.link(cape)
me = cape.data

# ------------------------------------------------------------------ putar, tinggi, gabung jahitan UV
me.transform(Matrix.Rotation(math.radians(args.rot_z), 4, "Z"))
zs = [v.co.z for v in me.vertices]
z0, z1 = min(zs), max(zs)
sz = (args.collar_z - args.hem_z) / (z1 - z0)
me.transform(Matrix.Translation((0, 0, -z0)))
me.transform(Matrix.Scale(sz, 4))
me.transform(Matrix.Translation((0, 0, args.hem_z)))
xs = [v.co.x for v in me.vertices]
me.transform(Matrix.Translation((-(min(xs) + max(xs)) / 2, 0, 0)))
nv0 = len(me.vertices)
bm = bmesh.new()
bm.from_mesh(me)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=args.merge_dist)

# Buka depan: jubah Tripo berupa mantel tertutup (panel depan sampai lutut), konsep terbuka di depan.
# Buang muka yang sudut horizontalnya (dari sumbu jubah, 0° = -Y) < --open-deg, di bawah pita kerah.
n_cut = 0
if args.open_deg > 0:
    mid = [v.co.y for v in bm.verts if 0.95 < v.co.z < 1.3]
    yc = (min(mid) + max(mid)) / 2
    z_keep = args.collar_z - args.collar_band
    dead = []
    for f in bm.faces:
        c = f.calc_center_median()
        if c.z >= z_keep:
            continue
        ang = math.degrees(math.atan2(abs(c.x), -(c.y - yc)))     # 0 = tepat di depan
        if ang < args.open_deg:
            dead.append(f)
    n_cut = len(dead)
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    # buang serpihan (potongan rantai/ornamen yang terlepas dari lembar utama)
    seen, isl = set(), []
    for v in bm.verts:
        if v in seen:
            continue
        st, grp = [v], [v]
        seen.add(v)
        while st:
            cur = st.pop()
            for e in cur.link_edges:
                w = e.other_vert(cur)
                if w not in seen:
                    seen.add(w)
                    st.append(w)
                    grp.append(w)
        isl.append(grp)
    big = max(len(g) for g in isl)
    loose = [v for g in isl if len(g) < max(200, big * 0.02) for v in g]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
bm.to_mesh(me)
bm.free()
me.update()
for img in bpy.data.images:
    if img.users and img.type == "IMAGE" and img.source == "FILE" and not img.packed_file:
        try:
            img.pack()
        except RuntimeError as e:
            print("  ! gagal pack", img.name, e)

# ------------------------------------------------------------------ BVH badan tanpa lengan
ARM_KEYS = ("upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky")
gname = {g.index: g.name for g in body.vertex_groups}
bme = body.data
is_arm = []
for v in bme.vertices:
    best = max(v.groups, key=lambda g: g.weight, default=None)
    is_arm.append(best is not None and any(k in gname[best.group] for k in ARM_KEYS))
bw = body.matrix_world
bverts = [bw @ v.co for v in bme.vertices]
polys = [list(p.vertices) for p in bme.polygons if sum(is_arm[i] for i in p.vertices) * 2 < len(p.vertices)]
bvh = BVHTree.FromPolygons(bverts, polys)
bvh_full = BVHTree.FromPolygons(bverts, [list(p.vertices) for p in bme.polygons])

base = [v.co.copy() for v in me.vertices]
COLLAR_Z = args.collar_z - 0.10     # di atas ini = kerah; jarak bebas cukup >= 0


def signed(bv, p):
    hit, nrm, _, d = bv.find_nearest(p)
    if hit is None:
        return 9.0
    return d if (p - hit).dot(nrm) >= 0 else -d


def evaluate(sx, sy, dy, step=1):
    bad = worst = 0
    worst = 9.0
    for i in range(0, len(base), step):
        c = base[i]
        p = Vector((c.x * sx, c.y * sy + dy, c.z))
        d = signed(bvh, p)
        need = 0.0 if c.z > COLLAR_Z else args.clear
        if d < need:
            bad += 1
        worst = min(worst, d)
    return bad, worst


# Skala lebar/kedalaman: tetap (--fit) atau grid kasar lalu halus, relatif terhadap skala tinggi (1 = seragam).
def search():
    best = None
    for sx in (1.0, 1.1, 1.2, 1.3):
        for sy in (1.0, 1.1, 1.2, 1.35, 1.5):
            for dy in (-0.02, 0.0, 0.02, 0.04, 0.06):
                bad, _ = evaluate(sx, sy, dy, step=6)
                score = (bad, abs(sx - 1) + abs(sy - 1) + abs(dy))
                if best is None or score < best[0]:
                    best = (score, sx, sy, dy)
    _, sx0, sy0, dy0 = best
    for sx in (sx0 - 0.05, sx0, sx0 + 0.05):
        for sy in (sy0 - 0.05, sy0, sy0 + 0.05):
            for dy in (dy0 - 0.01, dy0, dy0 + 0.01):
                if sx < 0.95 or sy < 0.95:
                    continue
                bad, _ = evaluate(sx, sy, dy, step=3)
                score = (bad, abs(sx - 1) + abs(sy - 1) + abs(dy))
                if score < best[0]:
                    best = (score, sx, sy, dy)
    return best[1:]


SX, SY, DY = search() if args.fit == "search" else (float(t) for t in args.fit.split(","))
for v, c in zip(me.vertices, base):
    v.co = Vector((c.x * SX, c.y * SY + DY, c.z))
me.update()

# ------------------------------------------------------------------ laporan jarak per zona (semua vertex)
zones = {"kerah (>%.2f)" % COLLAR_Z: [], "punggung 1,0-%.2f" % COLLAR_Z: [], "pinggul/sayap 0,5-1,0": [], "kaki <0,5": []}
zk = list(zones)
d_arm = []
for v in me.vertices:
    p = v.co
    d = signed(bvh, p)
    k = zk[0] if p.z > COLLAR_Z else zk[1] if p.z > 1.0 else zk[2] if p.z > 0.5 else zk[3]
    zones[k].append(d)
    d_arm.append(signed(bvh_full, p))

# ------------------------------------------------------------------ titik kait (diukur di badan rest)
for o in [o for o in bpy.data.objects if o.name.startswith("JD2C_ANCHOR_")]:
    bpy.data.objects.remove(o, do_unlink=True)


def back_surface(x, z):
    """Titik permukaan punggung (ray dari belakang ke depan)."""
    hit, *_ = bvh.ray_cast(Vector((x, 1.0, z)), Vector((0, -1, 0)))
    return hit


def anchor(name, loc):
    e = bpy.data.objects.new(f"JD2C_ANCHOR_{name}", None)
    e.empty_display_type, e.empty_display_size = "SPHERE", 0.025
    e.location = loc
    coll.objects.link(e)
    return e


# chin: titik terdepan-terbawah wajah (kepala, |x|<0.04, y paling depan) di 1,60-1,72
face = [p for p in bverts if abs(p.x) < 0.04 and 1.60 < p.z < 1.72 and p.y < -0.08]
chin = min(face, key=lambda p: p.z) if face else Vector((0, -0.12, 1.64))
anchors = {
    "nape": back_surface(0.0, 1.57),            # tengkuk
    "upper_back": back_surface(0.0, 1.45),      # punggung atas (pusat rantai)
}
eb = {b.name: b for b in arm.data.bones}
for sd in "lr":
    t = arm.matrix_world @ eb[f"clavicle_{sd}"].tail_local     # sendi bahu
    anchors[f"shoulder_{sd}"] = back_surface(t.x * 0.8, t.z - 0.03)   # di balik/bawah pauldron
anchors["chin"] = chin
for k, p in anchors.items():
    if p is not None:
        anchor(k, p)

cape["jd2_source"] = f"{SRC.name} (Tripo AI, developer, yahya_design/cap02.glb; docs/26)"
cape["jd2_fit"] = f"rotZ {args.rot_z} sz {sz:.4f} sx {SX:.3f} sy {SY:.3f} dy {DY:.3f}"
OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)

# topologi
bm = bmesh.new()
bm.from_mesh(me)
nonman = sum(1 for e in bm.edges if not e.is_manifold)
boundary = sum(1 for e in bm.edges if e.is_boundary)
seen, isl = set(), []
for v in bm.verts:
    if v.index in seen:
        continue
    st, n = [v], 0
    seen.add(v.index)
    while st:
        cur = st.pop()
        n += 1
        for e in cur.link_edges:
            w = e.other_vert(cur)
            if w.index not in seen:
                seen.add(w.index)
                st.append(w)
    isl.append(n)
bm.free()
co = [v.co for v in me.vertices]
mn = Vector([min(c[i] for c in co) for i in range(3)])
mx = Vector([max(c[i] for c in co) for i in range(3)])
tris = sum(len(p.vertices) - 2 for p in me.polygons)

print("=" * 70)
print(f"Sumber   : {SRC} ({SRC.stat().st_size / 1e6:.1f} MB)  ->  {OUT}")
print(f"Mesh     : {tris} tris, vertex {nv0} -> {len(me.vertices)} setelah merge+buka depan ({n_cut} muka dibuang, {args.open_deg:.0f}°), {len(cape.material_slots)} material")
print(f"Topologi : {len(isl)} pulau (terbesar {sorted(isl, reverse=True)[:8]}), {nonman} tepi non-manifold, {boundary} tepi terbuka")
print(f"Fit      : rotZ {args.rot_z}, tinggi x{sz:.4f} (kerah {args.collar_z} m, ujung {args.hem_z} m), "
      f"lebar x{SX:.3f}, kedalaman x{SY:.3f} (relatif), geser Y {DY * 100:+.1f} cm")
print(f"BBox     : min {tuple(round(v, 3) for v in mn)} max {tuple(round(v, 3) for v in mx)}")
for k, ds in zones.items():
    if ds:
        ds.sort()
        print(f"Jarak {k:24s}: n={len(ds):6d} min {ds[0] * 100:+6.1f} cm, p5 {ds[len(ds) // 20] * 100:+6.1f} cm, "
              f"<{args.clear * 100:.0f}cm {sum(d < args.clear for d in ds)}, tembus {sum(d < 0 for d in ds)}")
print(f"Tembus termasuk lengan (pose rest): {sum(d < 0 for d in d_arm)} vertex")
for k, p in anchors.items():
    print(f"Kait {k:12s}: {tuple(round(v, 3) for v in p) if p else 'TIDAK KENA'}")
print("=" * 70)
