"""Aksa Iterasi 5 — UV terskrip per slot material (5 slot) + data per-segitiga untuk pembuat tekstur.

Jalankan di Blender (MCP: exec(open(path).read())) dengan aksa_v04_outfit.blend (atau v05_tex) terbuka, setelah pipeline Iterasi 4
(aksa_22 → aksa_30 → aksa_40). Cara:
  - Kepala (AK_Head): jika objek punya properti `ak_native_uv` UV-nya dipertahankan; kalau tidak, smart_project seperti bagian lain.
  - Mata: proyeksi planar depan per mata (kiri sel kiri, kanan sel kanan) di slot Eyes 512²: iris/pupil/sklera tumpang di tempat yang sama.
  - Bagian lain: smart_project (ANGLE, default 85°) per slot, lalu skala per-island ke texel density seragam x bobot (kepala 2,2x, tangan/jari 1,5x,
    sarung tangan 1,3x, kerah/selendang 1,2x), lalu packer sendiri (shelf + pencarian biner pada faktor skala; rotasi diizinkan).
  - UV ditulis balik ke tiap bagian (layer `UVMap`); NPZ per-segitiga (UV, warna vertex linear, posisi dunia, zona, bagian, luas) ke
    Art/Export/_uv_faces_aksa.npz untuk make_textures_aksa.py.
Ukuran per slot: Skin 2048, Eyes 512, Hair 1024, Cloth 2048, Gear 1024 (docs/19 6.3). Aman diulang (UV ditimpa), tapi JANGAN ulang setelah
developer mulai mengecat tekstur (tata letak berubah).
"""
import math
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, r"C:\repository\unreal_engine\jayadwara\Art\Scripts")
import ak_common as C

UVNAME = "UVMap"
ANGLE = globals().get("ANGLE") or 85
NPZ = C.ART / "Export" / "_uv_faces_aksa.npz"
SIZE = {"Skin": 2048, "Eyes": 512, "Hair": 1024, "Cloth": 2048, "Gear": 1024}
MARGIN_PX = {"Skin": 8, "Eyes": 4, "Hair": 6, "Cloth": 8, "Gear": 6}
DENS = [("AK_Head", 2.2), ("AK_Hand", 1.5), ("AK_Finger", 1.5), ("AK_GloveNew", 1.3), ("AK_CollarLining", 1.2), ("AK_CollarOut", 1.1),
        ("AK_SashNew", 1.2), ("AK_Necklace", 1.4), ("AK_Stone", 1.4), ("AK_Brows", 1.4)]
ZONES = list(C.HEX.keys())
arm_names = {o.name for o in bpy.data.objects if o.type == "ARMATURE"}
parts = sorted([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("AK_") and not o.name.startswith("AK_REF") and "ak_kind" in o],
               key=lambda o: o.name)
print("bagian:", len(parts), "| slot:", sorted({o["ak_slot"] for o in parts}))
scene = bpy.context.scene


def dens_of(name):
    for pre, w in DENS:
        if name.startswith(pre):
            return w
    return 1.0


def call(op, **kw):
    props = op.get_rna_type().properties
    return op(**{k: v for k, v in kw.items() if k in props})


# ---------------------------------------------------------------- UV mata (planar)
def eye_uv(ps):
    cen = {}
    for o in ps:
        if o.name.startswith("AK_EyeSclera"):
            for sg in (1, -1):
                pts = [v.co for v in o.data.vertices if v.co.x * sg > 0]
                cen[sg] = sum(pts, Vector()) / len(pts)
    R = 0.0145                                                  # radius bola mata (m) -> 0,23 UV
    for o in ps:
        uv = o.data.uv_layers.get(UVNAME) or o.data.uv_layers.new(name=UVNAME)
        for p in o.data.polygons:
            for li in range(p.loop_start, p.loop_start + p.loop_total):
                co = o.data.vertices[o.data.loops[li].vertex_index].co
                sg = 1 if co.x > 0 else -1
                c = cen[sg]
                u0 = 0.0 if sg > 0 else 0.5
                uv.data[li].uv = (u0 + 0.25 + (co.x - c.x) * sg / R * 0.23, 0.5 + (co.z - c.z) / R * 0.23)
        o.data.uv_layers.active = uv


# ---------------------------------------------------------------- unwrap + pack per slot
def process_slot(slot):
    ps = [o for o in parts if o["ak_slot"] == slot]
    if slot == "Eyes":
        eye_uv(ps)
        return ps
    tmp = bpy.data.collections.new("_UV_TMP")
    scene.collection.children.link(tmp)
    dups = []
    for i, ob in enumerate(ps):
        d = ob.copy()
        d.data = ob.data.copy()
        d.modifiers.clear()
        d.parent = None
        d.matrix_world = ob.matrix_world.copy()
        for k in list(d.keys()):
            del d[k]
        me = d.data
        if me.shape_keys:
            d.shape_key_clear()
        native = bool(ob.get("ak_native_uv")) and UVNAME in ob.data.uv_layers
        if not native:
            for layer in list(me.uv_layers):
                me.uv_layers.remove(layer)
        a = me.attributes.new("AK_part", "INT", "FACE")
        a.data.foreach_set("value", [i] * len(me.polygons))
        n = me.attributes.new("AK_nat", "INT", "FACE")
        n.data.foreach_set("value", [1 if native else 0] * len(me.polygons))
        tmp.objects.link(d)
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
    me = J.data
    if UVNAME not in me.uv_layers:
        me.uv_layers.new(name=UVNAME)
    me.uv_layers.active = me.uv_layers[UVNAME]
    bpy.context.tool_settings.use_uv_select_sync = True
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(me)
    nat = bm.faces.layers.int["AK_nat"]
    for f in bm.faces:
        f.select = f[nat] == 0
    bm.select_flush_mode()
    for e in bm.edges:
        e.select = bool(e.link_faces) and all(f.select for f in e.link_faces)
    for v in bm.verts:
        v.select = any(f.select for f in v.link_faces)
    bmesh.update_edit_mesh(me)
    if any(f.select for f in bm.faces):
        call(bpy.ops.uv.smart_project, angle_limit=math.radians(ANGLE), island_margin=0.0, margin_method="SCALED", area_weight=0.0,
             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    uv = me.uv_layers[UVNAME].data
    nl = len(me.loops)
    loop_vert = np.zeros(nl, dtype=np.int32)
    me.loops.foreach_get("vertex_index", loop_vert)
    uvarr = np.zeros((nl, 2), dtype=np.float64)
    uv.foreach_get("uv", uvarr.ravel())
    pid = np.zeros(len(me.polygons), dtype=np.int32)
    me.attributes["AK_part"].data.foreach_get("value", pid)
    loop_part = np.zeros(nl, dtype=np.int32)
    loop_area = np.zeros(nl, dtype=np.float64)
    for j, p in enumerate(me.polygons):
        loop_part[p.loop_start:p.loop_start + p.loop_total] = pid[j]
        loop_area[p.loop_start:p.loop_start + p.loop_total] = p.area / p.loop_total
    par = list(range(nl))

    def fnd(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for p in me.polygons:
        for k in range(1, p.loop_total):
            a, b = fnd(p.loop_start), fnd(p.loop_start + k)
            if a != b:
                par[a] = b
    seen = {}
    for l in range(nl):
        key = (int(loop_vert[l]), round(uvarr[l, 0], 5), round(uvarr[l, 1], 5))
        if key in seen:
            a, b = fnd(l), fnd(seen[key])
            if a != b:
                par[a] = b
        else:
            seen[key] = l
    groups = {}
    for l in range(nl):
        groups.setdefault(fnd(l), []).append(l)
    isl = []
    loop_isl = np.zeros(nl, dtype=np.int32)
    for gi, g in enumerate(groups.values()):
        g = np.array(g)
        loop_isl[g] = gi
        isl.append({"loops": g, "area3d": loop_area[g].sum(), "w": dens_of(ps[loop_part[g[0]]].name)})
    uv_area = np.zeros(len(isl))
    for p in me.polygons:
        pts = uvarr[p.loop_start:p.loop_start + p.loop_total]
        x, y = pts[:, 0], pts[:, 1]
        uv_area[loop_isl[p.loop_start]] += 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    for i, it in enumerate(isl):
        s = math.sqrt(it["area3d"] / uv_area[i]) if uv_area[i] > 1e-14 else 1.0
        pts = uvarr[it["loops"]] * s * it["w"]
        mn = pts.min(axis=0)
        it["pts"] = pts - mn
        it["wh"] = it["pts"].max(axis=0)
    size = SIZE[slot]
    margin = MARGIN_PX[slot] / size

    def try_pack(f):
        rects = []
        for i, it in enumerate(isl):
            w, h = it["wh"] * f
            rot = False
            if h > w:
                w, h, rot = h, w, True
            rects.append((h + margin, w + margin, i, rot))
        rects.sort(reverse=True)
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
    covered = sum(it["area3d"] * it["w"] ** 2 for it in isl) * f * f
    print(f"  {slot}: {len(isl)} island, density dasar {f * size:.0f} px/m, cakupan {covered * 100:.1f}%")
    uv.foreach_set("uv", uvarr.ravel())

    # tulis balik ke bagian asli
    counter = [0] * len(ps)
    for j, p in enumerate(me.polygons):
        k = pid[j]
        ob = ps[k]
        q = ob.data.polygons[counter[k]]
        counter[k] += 1
        assert q.loop_total == p.loop_total, f"muka tidak cocok: {ob.name}"
        tgt = ob.data.uv_layers.get(UVNAME) or ob.data.uv_layers.new(name=UVNAME)
        for a in range(p.loop_total):
            tgt.data[q.loop_start + a].uv = tuple(uvarr[p.loop_start + a])
        ob.data.uv_layers.active = tgt
    bpy.data.objects.remove(J, do_unlink=True)
    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)
    bpy.data.collections.remove(tmp)
    return ps


for slot in C.SLOTS:
    process_slot(slot)

# ---------------------------------------------------------------- NPZ per-segitiga
rec = {k: [] for k in ("uv", "col", "pos", "mat", "zone", "part", "area")}
part_names = []
for k, ob in enumerate(parts):
    part_names.append(ob.name)
    me = ob.data
    ca = me.color_attributes["AK_Zone"]
    cols = np.zeros((len(me.vertices), 4), dtype=np.float32)
    # POINT domain: satu warna per vertex
    for i, d in enumerate(ca.data):
        cols[i] = d.color
    uvl = me.uv_layers[UVNAME].data
    mw = ob.matrix_world
    zid = ZONES.index(ob["ak_zone"])
    mi = C.SLOTS.index(ob["ak_slot"])
    for p in me.polygons:
        vs = list(p.vertices)
        ls = list(range(p.loop_start, p.loop_start + p.loop_total))
        for t in range(1, len(vs) - 1):
            idx = (0, t, t + 1)
            tri_v = [vs[i] for i in idx]
            tri_l = [ls[i] for i in idx]
            rec["uv"].append([tuple(uvl[l].uv) for l in tri_l])
            rec["col"].append([cols[v][:3] for v in tri_v])
            rec["pos"].append([tuple(mw @ me.vertices[v].co) for v in tri_v])
            rec["mat"].append(mi)
            rec["zone"].append(zid)
            rec["part"].append(k)
            a_ = (me.vertices[tri_v[1]].co - me.vertices[tri_v[0]].co).cross(me.vertices[tri_v[2]].co - me.vertices[tri_v[0]].co).length * 0.5
            rec["area"].append(a_)
np.savez(NPZ, uv=np.array(rec["uv"], np.float32), col=np.array(rec["col"], np.float32), pos=np.array(rec["pos"], np.float32),
         mat=np.array(rec["mat"], np.int8), zone=np.array(rec["zone"], np.int8), part=np.array(rec["part"], np.int16),
         area=np.array(rec["area"], np.float32), part_names=np.array(part_names), slots=np.array(C.SLOTS), zones=np.array(ZONES))
print("NPZ:", NPZ, "| segitiga:", len(rec["uv"]))
bpy.ops.wm.save_as_mainfile(filepath=str(C.ART / "Blender" / "aksa_v05_tex.blend"), relative_remap=True)
print("Disimpan:", bpy.data.filepath)
