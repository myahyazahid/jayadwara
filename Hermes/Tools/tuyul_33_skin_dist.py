"""K3.1b - Skinning berbasis jarak tulang (alternatif bobot heat) -> blend.

  blender --background <blend_in> --python Hermes/Tools/tuyul_33_skin_dist.py -- --out <blend_out>
        [--power 4] [--k 4] [--smooth-iters 2] [--smooth-factor 0.5] [--cull 0.0]

Bobot awal = 1/(jarak ke segmen tulang)^power untuk K tulang terdekat (root & IK dikecualikan),
lalu dihaluskan di permukaan, dibatasi 4 pengaruh, dinormalisasi. Bidang bobot mulus by design,
untuk mesh blob Tripo yang bobot heat-nya berisik (lihat laporan K3).
"""
import sys

import bpy

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
    power = float(arg("--power", "4"))
    K = int(arg("--k", "4"))
    iters = int(arg("--smooth-iters", "2"))
    fac = float(arg("--smooth-factor", "0.5"))
    cull = float(arg("--cull", "0.0"))
    ob, arm = bpy.data.objects[OBJ], bpy.data.objects[ARM]
    ob.vertex_groups.clear()
    for m in list(ob.modifiers):
        if m.type == "ARMATURE":
            ob.modifiers.remove(m)
    ob.parent = None
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.data.pose_position = "POSE"
    ob.parent = arm
    ob.matrix_parent_inverse = arm.matrix_world.inverted()
    md = ob.modifiers.new("Armature", "ARMATURE")
    md.object = arm

    me = ob.data
    nv = len(me.vertices)
    segs = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones
            if b.use_deform and b.name != "root" and not b.name.startswith("ik_")]
    print(f"tulang kandidat: {len(segs)}  power={power} k={K} halus={iters}x{fac} cull={cull}")

    W = []
    for v in me.vertices:
        ds = sorted(((seg_dist(v.co, h, t), nm) for nm, h, t in segs), key=lambda x: x[0])[:K]
        ws = {nm: 1.0 / (d + 1e-4) ** power for d, nm in ds}
        s = sum(ws.values())
        W.append({nm: w / s for nm, w in ws.items()})

    nbr = [[] for _ in range(nv)]
    for e in me.edges:
        a, b = e.vertices
        nbr[a].append(b)
        nbr[b].append(a)

    for _ in range(iters):
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

    if cull > 0:
        W = [{k: w for k, w in d.items() if w >= cull} or d for d in W]
    for i in range(nv):
        it = sorted(W[i].items(), key=lambda kv: -kv[1])[:4]
        s = sum(w for _, w in it) or 1.0
        W[i] = {k: w / s for k, w in it}

    cache = {}
    for i in range(nv):
        for nm, w in W[i].items():
            vg = cache.get(nm)
            if vg is None:
                vg = ob.vertex_groups.new(name=nm)
                cache[nm] = vg
            vg.add([i], w, "REPLACE")

    mx = unw = nonnorm = 0
    dom = {}
    zd = {}
    for v in me.vertices:
        gs = sorted(((g.group, g.weight) for g in v.groups if g.weight > 1e-4), key=lambda t: -t[1])
        mx = max(mx, len(gs))
        if not gs:
            unw += 1
            continue
        if abs(sum(w for _, w in gs) - 1.0) > 0.01:
            nonnorm += 1
        nm = ob.vertex_groups[gs[0][0]].name
        dom[nm] = dom.get(nm, 0) + 1
        z = zone(v.co)
        if z:
            zd.setdefault(z, {})
            zd[z][nm] = zd[z].get(nm, 0) + 1
    print(f"vertex={nv} maks pengaruh={mx} tanpa bobot={unw} tidak ternormalisasi={nonnorm} grup={len(ob.vertex_groups)}")
    print("dominan 10:", sorted(dom.items(), key=lambda kv: -kv[1])[:10])
    for z, d in zd.items():
        t = sorted(d.items(), key=lambda kv: -kv[1])[:4]
        tot = sum(d.values())
        print(f"  zona {z}: {tot} | " + ", ".join(f"{n} {100*c/tot:.0f}%" for n, c in t))
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print("disimpan:", out)


main()
