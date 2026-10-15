"""K3.1 - Skinning Tuyul (bobot lunak) -> tuyul_v05_skin.blend.

  blender --background <blend_in> --python Hermes/Tools/tuyul_30_skin.py -- --out <blend_out>

Langkah: buang grup/modifier lama -> parent ARMATURE_AUTO (bobot otomatis, heat map)
-> haluskan (smooth 2x, factor 0,5) -> batasi 4 pengaruh -> normalisasi -> isi vertex tanpa bobot
(dengan tulang terdekat) -> normalisasi ulang. Cetak statistik + sebaran tulang dominan per zona
(cawat/punggung/perut) sebagai bukti ornamen terkunci ke tulang terdekat.
"""
import sys
import bpy
from mathutils import Vector

OBJ, ARM = "TY_Source", "TY_Armature"


def arg(name, default=None):
    a = sys.argv
    if "--" in a:
        a = a[a.index("--") + 1:]
        if name in a:
            return a[a.index(name) + 1]
    return default


def seg_dist(p, h, t):
    d = t - h
    L = d.length_squared
    if L < 1e-12:
        return (p - h).length
    u = max(0.0, min(1.0, (p - h).dot(d) / L))
    return (p - (h + d * u)).length


def zone(co):
    x, y, z = co
    if 0.18 <= z <= 0.44 and abs(x) < 0.28:
        return "cawat/pinggul"
    if y > 0.12 and 0.38 <= z <= 0.88:
        return "punggung/kantong"
    if y < -0.14 and 0.28 <= z <= 0.68:
        return "perut"
    return None


def main():
    out = arg("--out")
    ob, arm = bpy.data.objects[OBJ], bpy.data.objects[ARM]
    ob.vertex_groups.clear()
    for m in list(ob.modifiers):
        if m.type == "ARMATURE":
            ob.modifiers.remove(m)
    ob.parent = None
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.data.pose_position = "POSE"
    off = [n for n in (arg("--nodeform", "") or "").split(",") if n]
    if arg("--recalc"):
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bad = sum(1 for f in bm.faces if f.calc_area() < 1e-12)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(ob.data)
        bm.free()
        print(f"normal dihitung ulang (muka rusak/luas nol: {bad})")
    for n in off:
        if n in arm.data.bones:
            arm.data.bones[n].use_deform = False
    print("tulang dinonaktifkan dari deform:", off)

    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    # buka ketiak sementara: putar vertex lengan keluar supaya solver heat tidak bingung pada blob
    open_deg = float(arg("--tpose-open", "0"))
    co0 = None
    if open_deg > 0:
        import math
        from mathutils import Matrix, Vector
        xmin = float(arg("--tpose-x", "0.155"))
        co0 = [v.co.copy() for v in ob.data.vertices]
        piv = {"l": Vector((0.160, 0.0, 0.750)), "r": Vector((-0.160, 0.0, 0.750))}
        n = 0
        for v in ob.data.vertices:
            c = co0[v.index]
            if 0.20 < c.z < 0.82 and abs(c.x) > xmin:
                side = "l" if c.x > 0 else "r"
                t = min(1.0, (abs(c.x) - xmin) / 0.04)              # transisi halus
                ang = math.radians(-open_deg if side == "l" else open_deg) * t
                v.co = piv[side] + Matrix.Rotation(ang, 3, "Y") @ (c - piv[side])
                n += 1
        print(f"buka ketiak: {n} vertex diputar s/d {open_deg} derajat (xmin {xmin})")
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    if co0 is not None:
        for i, v in enumerate(ob.data.vertices):
            v.co = co0[i]
        bpy.context.view_layer.update()
    for n in off:
        if n in arm.data.bones:
            arm.data.bones[n].use_deform = True
    print("bobot otomatis: grup =", len(ob.vertex_groups), "| modifier =", [m.type for m in ob.modifiers])

    # --- pasca-proses bobot (Python murni; operator context tidak tersedia di background)
    me = ob.data
    names = {vg.index: vg.name for vg in ob.vertex_groups}
    nidx = {v: k for k, v in names.items()}
    nv = len(me.vertices)
    W = [dict() for _ in range(nv)]
    for v in me.vertices:
        for g in v.groups:
            if g.weight > 1e-5:
                W[v.index][g.group] = g.weight
    nbr = [[] for _ in range(nv)]
    for e in me.edges:
        a, b = e.vertices
        nbr[a].append(b)
        nbr[b].append(a)

    # buang bobot bocor: nilai kecil, dan tulang yang jauh dibanding tulang terdekat
    cull = float(arg("--cull", "0.0"))
    prox = float(arg("--prox", "0.0"))
    if cull > 0 or prox > 0:
        bseg = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones if b.use_deform}
        n_cull = n_prox = 0
        for i in range(nv):
            if not W[i]:
                continue
            if cull > 0:
                before = len(W[i])
                W[i] = {k: w for k, w in W[i].items() if w >= cull}
                n_cull += before - len(W[i])
            if prox > 0 and W[i]:
                ds = {k: seg_dist(me.vertices[i].co, *bseg[names[k]]) for k in W[i] if names[k] in bseg}
                if ds:
                    dmin = min(ds.values())
                    before = len(W[i])
                    W[i] = {k: w for k, w in W[i].items() if k not in ds or ds[k] <= (1.0 + prox) * dmin + 0.02}
                    n_prox += before - len(W[i])
        print(f"filter: cull<{cull} buang {n_cull} bobot | prox {prox} buang {n_prox} bobot")

    # prune radius per tulang: buang bobot tulang bila vertex lebih jauh dari radiusnya
    prunes = []
    for spec in (arg("--prune", "") or "").split(","):
        if ":" in spec:
            b, r = spec.split(":")
            prunes.append((b, float(r)))
    if prunes:
        bseg = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones}
        nidx = {v: k for k, v in names.items()}
        n_p = 0
        for i in range(nv):
            c = me.vertices[i].co
            for b, r in prunes:
                k = nidx.get(b)
                if k is not None and k in W[i] and b in bseg and seg_dist(c, *bseg[b]) > r:
                    del W[i][k]
                    n_p += 1
        print(f"prune {prunes}: buang {n_p} bobot")

    def normalize(d, lim=4):
        it = sorted(d.items(), key=lambda kv: -kv[1])[:lim]
        s = sum(w for _, w in it)
        return {k: w / s for k, w in it} if s > 0 else {}

    iters = int(arg("--smooth-iters", "1"))
    fac = float(arg("--smooth-factor", "0.5"))
    print(f"penghalusan: {iters} iterasi, faktor {fac}")
    for _ in range(iters):                                # haluskan: campur bobot diri dengan rata-rata tetangga
        NW = []
        for i in range(nv):
            acc = {k: (1.0 - fac) * w for k, w in W[i].items()}
            d = len(nbr[i])
            if d:
                for j in nbr[i]:
                    for k, w in W[j].items():
                        acc[k] = acc.get(k, 0.0) + fac * w / d
            NW.append(acc)
        W = NW
    cull2 = float(arg("--cull2", "0.0"))
    if cull2 > 0:
        W = [{k: w for k, w in d.items() if w >= cull2} or d for d in W]
        print(f"cull2<{cull2}: sisa bobot = {sum(len(d) for d in W)}")
    for i in range(nv):
        W[i] = normalize(W[i])                            # maks 4 pengaruh + normalisasi

    # vertex tanpa bobot -> tulang terdekat
    segs = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones
            if b.use_deform and b.name in nidx]
    fixed = 0
    for i in range(nv):
        if not W[i]:
            nm = min(segs, key=lambda s: seg_dist(me.vertices[i].co, s[1], s[2]))[0]
            W[i] = {nidx[nm]: 1.0}
            fixed += 1

    # tulis balik
    ob.vertex_groups.clear()
    cache = {}
    for i in range(nv):
        for gidx, w in W[i].items():
            nm = names[gidx]
            vg = cache.get(nm)
            if vg is None:
                vg = ob.vertex_groups.new(name=nm)
                cache[nm] = vg
            vg.add([i], w, "REPLACE")
    print("vertex tanpa bobot yang diperbaiki:", fixed)

    # statistik
    vgn = {vg.index: vg.name for vg in ob.vertex_groups}
    mx = unw = nonnorm = 0
    dom_count = {}
    zone_dom = {}
    for v in ob.data.vertices:
        gs = sorted(((g.group, g.weight) for g in v.groups if g.weight > 1e-4), key=lambda t: -t[1])
        mx = max(mx, len(gs))
        if not gs:
            unw += 1
            continue
        if abs(sum(w for _, w in gs) - 1.0) > 0.01:
            nonnorm += 1
        dn = vgn[gs[0][0]]
        dom_count[dn] = dom_count.get(dn, 0) + 1
        z = zone(v.co)
        if z:
            zone_dom.setdefault(z, {})
            zone_dom[z][dn] = zone_dom[z].get(dn, 0) + 1

    print(f"vertex={len(ob.data.vertices)}  maks pengaruh={mx}  tanpa bobot={unw}  tidak ternormalisasi={nonnorm}")
    print("tulang terpakai:", len(dom_count), "dari", len(ob.vertex_groups))
    top = sorted(dom_count.items(), key=lambda kv: -kv[1])[:10]
    print("tulang dominan (10 teratas):", [(n, c) for n, c in top])
    for z, d in zone_dom.items():
        t = sorted(d.items(), key=lambda kv: -kv[1])[:4]
        tot = sum(d.values())
        print(f"  zona {z}: {tot} vertex | dominan: " + ", ".join(f"{n} {100*c/tot:.0f}%" for n, c in t))

    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print("disimpan:", out)


main()
