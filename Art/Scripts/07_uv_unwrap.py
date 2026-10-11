"""Iterasi 4 — UV unwrap terskrip untuk seluruh bagian (JD_*), dipack PER SLOT MATERIAL.

Cara: duplikat semua bagian -> satu mesh sementara; atribut muka `JD_part` menyimpan indeks bagian.
- Armor/Body/Face: smart_project (sudut 66°) lalu skala islands seragam (texel density sama) lalu pack (boleh rotasi).
- Cloth: unwrap berbasis sudut; tiap strip diputar agar panjangnya (JD_t) searah V (arah batik konsisten), pack TANPA rotasi.
UV hasil pack ditulis balik ke tiap bagian (UVMap) lewat atribut `JD_part`, dan data per-muka disimpan ke NPZ
untuk pembuat tekstur (make_textures.py). Aman dijalankan ulang (UVMap ditimpa).
Variabel opsional sebelum exec: UV_NPZ (path keluaran).
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector

UV_NPZ = globals().get("UV_NPZ") or r"C:\repository\unreal_engine\jayadwara\Art\Export\_uv_faces.npz"
UVNAME = "UVMap"
SLOTS = ["Body", "Armor", "Cloth", "Face"]
ZONES = ["red", "gold", "black", "white", "marun", "gem", "eye"]
MARGIN = {"Body": 0.004, "Armor": 0.003, "Cloth": 0.004, "Face": 0.006}
ANGLE_LIMIT = globals().get("ANGLE_LIMIT", 89)           # derajat; makin besar -> makin sedikit pecahan, tapi bisa melipat tabung
ANGLES = {"Body": 45}                                    # undersuit = tabung halus -> sudut kecil agar tidak tumpang-tindih
PACK_SHAPE = globals().get("PACK_SHAPE", "CONCAVE")       # CONCAVE | CONVEX | AABB
PACK_TIMES = globals().get("PACK_TIMES", 1)
SLOT_FILTER = globals().get("SLOT_FILTER", None)          # eksperimen: hanya slot ini


def call(op, **kw):
    """Panggil operator hanya dengan argumen yang dikenalnya (Blender 5.2 mengganti beberapa nama)."""
    props = op.get_rna_type().properties
    use = {k: v for k, v in kw.items() if k in props}
    skipped = sorted(set(kw) - set(use))
    if skipped:
        print(f"  (lewati argumen tak dikenal untuk {op.idname()}: {skipped})")
    return op(**use)


def enum_ok(op, prop, value):
    p = op.get_rna_type().properties.get(prop)
    return p is not None and value in [i.identifier for i in p.enum_items]


scene = bpy.context.scene
parts = sorted([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("JD_") and "jd_kind" in o], key=lambda o: o.name)
print("bagian:", len(parts))

# ---------------------------------------------------------------- 1. mesh gabungan sementara
tmp_coll = bpy.data.collections.new("_UV_TMP")
scene.collection.children.link(tmp_coll)
dups = []
for i, ob in enumerate(parts):
    d = ob.copy()
    d.data = ob.data.copy()
    d.modifiers.clear()
    d.parent = None
    d.matrix_world = ob.matrix_world.copy()
    for k in list(d.keys()):
        del d[k]
    me = d.data
    for layer in list(me.uv_layers):
        me.uv_layers.remove(layer)
    a = me.attributes.new("JD_part", "INT", "FACE")
    a.data.foreach_set("value", [i] * len(me.polygons))
    z = me.attributes.get("JD_zoneid") or me.attributes.new("JD_zoneid", "INT", "FACE")
    z.data.foreach_set("value", [ZONES.index(ob["jd_zone"])] * len(me.polygons))
    tmp_coll.objects.link(d)
    dups.append(d)
for o in bpy.context.view_layer.objects:
    o.select_set(False)
for d in dups:
    d.select_set(True)
act = dups[0]
bpy.context.view_layer.objects.active = act
with bpy.context.temp_override(active_object=act, object=act, selected_objects=dups, selected_editable_objects=dups):
    bpy.ops.object.join()
J = bpy.context.view_layer.objects.active
J.name = "_UV_JOINED"
me = J.data
if UVNAME not in me.uv_layers:
    me.uv_layers.new(name=UVNAME)
me.uv_layers.active = me.uv_layers[UVNAME]
slot_of_mat = {m.name.replace("M_Jayadwara_", ""): i for i, m in enumerate(me.materials)}
print("slot material:", slot_of_mat, "| muka:", len(me.polygons))

# ---------------------------------------------------------------- 2. unwrap per slot
bpy.context.tool_settings.use_uv_select_sync = True
bpy.ops.object.mode_set(mode="EDIT")


def select_slot(slot):
    bm = bmesh.from_edit_mesh(me)
    idx = slot_of_mat[slot]
    for f in bm.faces:
        f.select = f.material_index == idx
    bm.select_flush_mode()
    for e in bm.edges:
        e.select = all(f.select for f in e.link_faces) and bool(e.link_faces)
    for v in bm.verts:
        v.select = any(f.select for f in v.link_faces)
    bmesh.update_edit_mesh(me)


for slot in (SLOT_FILTER or SLOTS):
    select_slot(slot)
    if slot == "Cloth":
        call(bpy.ops.uv.unwrap, method="ANGLE_BASED", margin=MARGIN[slot], fill_holes=True)
    else:
        call(bpy.ops.uv.smart_project, angle_limit=math.radians(ANGLES.get(slot, ANGLE_LIMIT)), island_margin=0.0, margin_method="SCALED",
             area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
bpy.ops.object.mode_set(mode="OBJECT")

# ---------------------------------------------------------------- 3. kain: putar tiap strip agar panjang (t) searah -V
uv = me.uv_layers[UVNAME].data
tattr = me.attributes["JD_t"].data
cloth_idx = slot_of_mat["Cloth"]
parent = list(range(len(me.vertices)))


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


cloth_polys = [p for p in me.polygons if p.material_index == cloth_idx]
for p in cloth_polys:
    vs = list(p.vertices)
    for a in vs[1:]:
        ra, rb = find(vs[0]), find(a)
        if ra != rb:
            parent[ra] = rb
comp_loops = {}
for p in cloth_polys:
    comp_loops.setdefault(find(p.vertices[0]), []).extend(range(p.loop_start, p.loop_start + p.loop_total))
loop_vert = np.zeros(len(me.loops), dtype=np.int32)
me.loops.foreach_get("vertex_index", loop_vert)
for comp, loops in comp_loops.items():
    ts = np.array([tattr[loop_vert[l]].value for l in loops])
    uvs = np.array([uv[l].uv[:] for l in loops])
    top, bot = ts <= 0.25, ts >= 0.75
    if not top.any() or not bot.any():
        continue
    vec = uvs[bot].mean(axis=0) - uvs[top].mean(axis=0)
    ang = math.atan2(-1.0, 0.0) - math.atan2(vec[1], vec[0])        # arah target: (0,-1)
    c, s = math.cos(ang), math.sin(ang)
    cen = uvs.mean(axis=0)
    for l, p in zip(loops, uvs):
        q = p - cen
        uv[l].uv = (cen[0] + c * q[0] - s * q[1], cen[1] + s * q[0] + c * q[1])
print("strip kain diorientasi:", len(comp_loops))

# ---------------------------------------------------------------- 4. skala seragam + pack per slot
#   Packer bawaan Blender 5.2 tidak bisa disetel (cakupan tetap ±5%), jadi dipakai packer sendiri:
#   island = komponen loop yang berbagi vertex DAN koordinat UV; skala = 1 unit UV per meter (density seragam),
#   lalu shelf-packing + pencarian biner pada faktor skala global agar semua island muat di 0..1.
loop_poly_area = np.zeros(len(me.loops), dtype=np.float64)
for p in me.polygons:
    loop_poly_area[p.loop_start:p.loop_start + p.loop_total] = p.area / p.loop_total       # luas 3D dibagi rata ke loop
uvarr = np.zeros((len(me.loops), 2), dtype=np.float64)
uv.foreach_get("uv", uvarr.ravel())
loop_mat = np.zeros(len(me.loops), dtype=np.int32)
for p in me.polygons:
    loop_mat[p.loop_start:p.loop_start + p.loop_total] = p.material_index


def pack_slot(slot, size, margin_px, allow_rotate):
    idx = slot_of_mat[slot]
    loops = np.where(loop_mat == idx)[0]
    par = {int(l): int(l) for l in loops}

    def fnd(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    def uni(a, b):
        ra, rb = fnd(a), fnd(b)
        if ra != rb:
            par[ra] = rb

    for p in me.polygons:
        if p.material_index != idx:
            continue
        for k in range(1, p.loop_total):
            uni(p.loop_start, p.loop_start + k)
    seen = {}
    for l in loops:
        key = (int(loop_vert[l]), round(uvarr[l, 0], 5), round(uvarr[l, 1], 5))
        if key in seen:
            uni(int(l), seen[key])
        else:
            seen[key] = int(l)
    groups = {}
    for l in loops:
        groups.setdefault(fnd(int(l)), []).append(int(l))
    isl = []
    for g in groups.values():
        g = np.array(g)
        p = uvarr[g]
        a3 = loop_poly_area[g].sum()
        # luas UV island (shoelace per poligon) untuk skala ke meter
        # pendekatan: pakai lebar/tinggi bbox, skala dari rasio luas bbox terhadap luas 3D tidak akurat -> hitung dari poligon
        isl.append({"loops": g, "area3d": a3})
    # luas UV per island dari poligon
    loop_island = {}
    for i, it in enumerate(isl):
        for l in it["loops"]:
            loop_island[int(l)] = i
    uv_area = np.zeros(len(isl))
    for p in me.polygons:
        if p.material_index != idx:
            continue
        pts = uvarr[p.loop_start:p.loop_start + p.loop_total]
        x, y = pts[:, 0], pts[:, 1]
        uv_area[loop_island[p.loop_start]] += 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    for i, it in enumerate(isl):
        s = math.sqrt(it["area3d"] / uv_area[i]) if uv_area[i] > 1e-14 else 1.0      # -> 1 unit UV = 1 meter
        pts = uvarr[it["loops"]] * s
        mn = pts.min(axis=0)
        it["pts"] = pts - mn
        it["wh"] = it["pts"].max(axis=0)
    margin = margin_px / size

    def try_pack(f):
        rects = []
        for i, it in enumerate(isl):
            w, h = it["wh"] * f
            rot = False
            if allow_rotate and h > w:
                w, h, rot = h, w, True
            rects.append((h + margin, w + margin, i, rot))
        rects.sort(reverse=True)                              # tinggi menurun
        x = y = rowh = 0.0
        place = {}
        for rh, rw, i, rot in rects:
            if rw > 1.0:
                return None
            if x + rw > 1.0:
                y += rowh
                x, rowh = 0.0, 0.0
            if y + rh > 1.0:
                return None
            place[i] = (x, y, rot)
            x += rw
            rowh = max(rowh, rh)
        return place

    lo, hi = 1e-4, 1.0
    while try_pack(hi) is not None:
        hi *= 2
    for _ in range(40):
        mid = (lo + hi) / 2
        if try_pack(mid) is not None:
            lo = mid
        else:
            hi = mid
    f = lo
    place = try_pack(f)
    for i, it in enumerate(isl):
        x0, y0, rot = place[i]
        p = it["pts"] * f
        if rot:
            p = np.stack([p[:, 1], p[:, 0]], axis=1)
        uvarr[it["loops"]] = p + np.array([x0 + margin / 2, y0 + margin / 2])
    covered = sum(it["area3d"] for it in isl) * f * f
    print(f"  pack {slot}: {len(isl)} island, density {f * size:.0f} px/m, cakupan {covered * 100:.1f}%")


for slot in (SLOT_FILTER or SLOTS):
    pack_slot(slot, {"Armor": 2048, "Cloth": 2048, "Body": 1024, "Face": 1024}[slot], 8, slot != "Cloth")
uv.foreach_set("uv", uvarr.ravel())

# ---------------------------------------------------------------- 5. statistik + tulis balik ke bagian + NPZ
uv = me.uv_layers[UVNAME].data
nloop = len(me.loops)
uvarr = np.zeros((nloop, 2), dtype=np.float32)
uv.foreach_get("uv", uvarr.ravel())
for slot in SLOTS:
    idx = slot_of_mat[slot]
    ls = np.concatenate([np.arange(p.loop_start, p.loop_start + p.loop_total) for p in me.polygons if p.material_index == idx])
    sub = uvarr[ls]
    print(f"{slot:6s}: UV x[{sub[:, 0].min():.3f},{sub[:, 0].max():.3f}] y[{sub[:, 1].min():.3f},{sub[:, 1].max():.3f}] loops={len(ls)}")

pid = np.zeros(len(me.polygons), dtype=np.int32)
me.attributes["JD_part"].data.foreach_get("value", pid)
zid = np.zeros(len(me.polygons), dtype=np.int32)
me.attributes["JD_zoneid"].data.foreach_get("value", zid)
counter = [0] * len(parts)
rec_uv, rec_mat, rec_zone, rec_part, rec_area = [], [], [], [], []
vco = np.zeros((len(me.vertices), 3), dtype=np.float32)
me.vertices.foreach_get("co", vco.ravel())
for j, p in enumerate(me.polygons):
    k = pid[j]
    ob = parts[k]
    q = ob.data.polygons[counter[k]]
    counter[k] += 1
    assert q.loop_total == p.loop_total, f"muka tidak cocok pada {ob.name}"
    if "UVMap" not in ob.data.uv_layers:
        ob.data.uv_layers.new(name=UVNAME)
    tgt = ob.data.uv_layers[UVNAME].data
    for a in range(p.loop_total):
        tgt[q.loop_start + a].uv = tuple(uvarr[p.loop_start + a])
    uvs = uvarr[p.loop_start:p.loop_start + p.loop_total]
    for t in range(1, p.loop_total - 1):               # triangulasi kipas
        v0, v1, v2 = (vco[p.vertices[i]] for i in (0, t, t + 1))
        rec_area.append(0.5 * float(np.linalg.norm(np.cross(v1 - v0, v2 - v0))))
        rec_uv.append(np.stack([uvs[0], uvs[t], uvs[t + 1]]))
        rec_mat.append(p.material_index)
        rec_zone.append(zid[j])
        rec_part.append(k)
for ob in parts:
    ob.data.uv_layers.active = ob.data.uv_layers[UVNAME]
np.savez(UV_NPZ, uv=np.array(rec_uv, dtype=np.float32), mat=np.array(rec_mat, dtype=np.int8), zone=np.array(rec_zone, dtype=np.int8),
         part=np.array(rec_part, dtype=np.int16), part_names=np.array([o.name for o in parts]), area=np.array(rec_area, dtype=np.float32), slots=np.array([m.name.replace("M_Jayadwara_", "") for m in me.materials]),
         zones=np.array(ZONES))
print("NPZ:", UV_NPZ, "| segitiga:", len(rec_uv))

# ---------------------------------------------------------------- 6. bersihkan
bpy.data.objects.remove(J, do_unlink=True)
for m in list(bpy.data.meshes):
    if m.users == 0:
        bpy.data.meshes.remove(m)
bpy.data.collections.remove(tmp_coll)
