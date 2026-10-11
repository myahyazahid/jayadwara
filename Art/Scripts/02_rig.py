"""Iterasi 1 — rig dasar: armature bergaya UE5 Mannequin, skin weight, socket.

Jalankan setelah 01_blockout.py. Aman dijalankan ulang (armature, vertex group, modifier, socket dibuat ulang).
- Bagian kaku: weight 1.0 ke satu tulang (atau campuran dari `jd_weights`).
- Undersuit: heat-map automatic weights (tulang kulit saja); jika gagal -> fallback jarak.
- Kain: weight sepanjang rantai tulang dari atribut vertex `JD_t`.
- Semua mesh: maks 4 influence, dinormalisasi.
"""
import importlib
import json
import sys

import bpy
from mathutils import Matrix, Vector

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jd_common as C
import jd_skeleton as SK
importlib.reload(C)
importlib.reload(SK)

ARM_NAME = "JD_Armature"
MAX_INFLUENCE = 4

# ------------------------------------------------------------------ bersihkan rig lama
for ob in list(bpy.data.objects):
    if ob.name == ARM_NAME or ob.name.startswith("SOCKET_"):
        bpy.data.objects.remove(ob, do_unlink=True)
for ob in bpy.data.objects:
    if ob.type == "MESH" and ob.name.startswith("JD_"):
        ob.parent = None
        ob.vertex_groups.clear()
        for m in list(ob.modifiers):
            ob.modifiers.remove(m)
for ar in list(bpy.data.armatures):
    if ar.users == 0:
        bpy.data.armatures.remove(ar)

parts = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("JD_") and "jd_kind" in o]

# ------------------------------------------------------------------ armature
arm_data = bpy.data.armatures.new(ARM_NAME)
arm = bpy.data.objects.new(ARM_NAME, arm_data)
C.get_collection("08_Rig").objects.link(arm)
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
    b.use_deform = name not in SK.IK_BONES      # tulang IK tidak men-deform; root ikut deform agar terekspor
for name, parent, head, tail, connect in bones:
    if parent:
        eb[name].parent = eb[parent]
        eb[name].use_connect = connect
bpy.ops.object.mode_set(mode="OBJECT")
print("tulang:", len(arm_data.bones))


# ------------------------------------------------------------------ util weight
def set_weights(obj, assign):
    """assign: {nama_grup: {vertex_index: bobot}}"""
    for gname, vmap in assign.items():
        vg = obj.vertex_groups.get(gname) or obj.vertex_groups.new(name=gname)
        by_w = {}
        for vi, w in vmap.items():
            by_w.setdefault(round(w, 5), []).append(vi)
        for w, idx in by_w.items():
            vg.add(idx, w, "REPLACE")


def clean_weights(obj, limit=MAX_INFLUENCE):
    """Batasi influence per vertex, normalisasi; kembalikan (maks influence, vertex tanpa weight)."""
    names = {vg.index: vg.name for vg in obj.vertex_groups}
    unweighted = 0
    for v in obj.data.vertices:
        gs = [(g.group, g.weight) for g in v.groups if g.weight > 1e-4]
        if not gs:
            unweighted += 1
            continue
        gs.sort(key=lambda x: -x[1])
        keep, drop = gs[:limit], gs[limit:]
        tot = sum(w for _, w in keep)
        for gi, _ in drop:
            obj.vertex_groups[gi].remove([v.index])
        for gi, w in keep:
            obj.vertex_groups[gi].add([v.index], w / tot, "REPLACE")
    mx = 0
    for v in obj.data.vertices:
        mx = max(mx, len([g for g in v.groups if g.weight > 1e-4]))
    return mx, unweighted


def smooth_weights(obj, iters=3, factor=0.5):
    """Haluskan bobot rata-rata dengan tetangga (hilangkan sambungan tajam hasil heat-map)."""
    me = obj.data
    n = len(me.vertices)
    adj = [set() for _ in range(n)]
    for e in me.edges:
        a, b = e.vertices
        adj[a].add(b)
        adj[b].add(a)
    W = [{g.group: g.weight for g in v.groups} for v in me.vertices]
    for _ in range(iters):
        new = []
        for i in range(n):
            nb = adj[i]
            acc = {}
            for j in nb:
                for g, w in W[j].items():
                    acc[g] = acc.get(g, 0.0) + w / len(nb)
            m = {}
            for g in set(W[i]) | set(acc):
                m[g] = (1 - factor) * W[i].get(g, 0.0) + factor * acc.get(g, 0.0)
            new.append(m)
        W = new
    for vi, m in enumerate(W):
        for g, w in m.items():
            if w > 1e-4:
                obj.vertex_groups[g].add([vi], w, "REPLACE")
            else:
                obj.vertex_groups[g].remove([vi])


def point_seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
    return (p - (a + ab * t)).length


def distance_weights(obj, bone_names, k=3, power=4.0):
    seg = SK.bone_segments()
    mw = obj.matrix_world
    assign = {n: {} for n in bone_names}
    for v in obj.data.vertices:
        p = mw @ v.co
        ds = sorted(((point_seg_dist(p, *seg[n]), n) for n in bone_names))[:k]
        ws = [1.0 / (d + 0.01) ** power for d, _ in ds]
        tot = sum(ws)
        for (d, n), w in zip(ds, ws):
            assign[n][v.index] = w / tot
    set_weights(obj, assign)


# ------------------------------------------------------------------ weight per bagian
report = []
for obj in parts:
    kind = obj["jd_kind"]
    n = len(obj.data.vertices)
    if kind == "rigid":
        wmap = json.loads(obj["jd_weights"]) if "jd_weights" in obj else {obj["jd_bone"]: 1.0}
        set_weights(obj, {b: {i: w for i in range(n)} for b, w in wmap.items()})
    elif kind == "strip":
        chain = json.loads(obj["jd_bones"]) if "jd_bones" in obj else SK.chain_bones(obj["jd_chain"])
        nb = len(chain)
        tl = obj.data.attributes["JD_t"].data
        assign = {b: {} for b in chain}
        for v in obj.data.vertices:
            u = tl[v.index].value * nb - 0.5
            if u <= 0:
                assign[chain[0]][v.index] = 1.0
            elif u >= nb - 1:
                assign[chain[-1]][v.index] = 1.0
            else:
                i0 = int(u)
                f = u - i0
                assign[chain[i0]][v.index] = 1.0 - f
                assign[chain[i0 + 1]][v.index] = f
        set_weights(obj, assign)
    # armature modifier + parent (armature di identitas -> parent inverse identitas)
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    mod.use_vertex_groups = True
    obj.parent = arm
    obj.parent_type = "OBJECT"

# ------------------------------------------------------------------ undersuit: heat-map auto weights
body = bpy.data.objects["JD_Body_Undersuit"]
body.modifiers.clear()
body.parent = None
saved = {b.name: b.use_deform for b in arm_data.bones}
for b in arm_data.bones:
    b.use_deform = b.name in SK.SKIN_BONES
ok_auto = True
try:
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    body.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    with bpy.context.temp_override(active_object=arm, object=arm, selected_objects=[body, arm],
                                   selected_editable_objects=[body, arm]):
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
except Exception as e:  # noqa
    ok_auto = False
    print("auto weights gagal:", e)
for b in arm_data.bones:
    b.use_deform = saved[b.name]
if ok_auto and body.vertex_groups:
    smooth_weights(body, iters=3, factor=0.5)
mx, unw = clean_weights(body)
if not ok_auto or unw > 0 or not body.vertex_groups:
    print(f"fallback jarak (auto={ok_auto}, tanpa weight={unw})")
    body.vertex_groups.clear()
    distance_weights(body, SK.SKIN_BONES)
    if not any(m.type == "ARMATURE" for m in body.modifiers):
        mod = body.modifiers.new("Armature", "ARMATURE")
        mod.object = arm
        mod.use_vertex_groups = True
    body.parent = arm
    body.parent_type = "OBJECT"
FOLLOW_FULL = 0.02                       # m; dorongan 15_body_fit >= ini -> badan 100% mengikuti bobot zirah di atasnya
if "JD_FitPush" in body.data.attributes and "jd_fit_src" in body:
    # otot yang ditempelkan ke zirah (15_body_fit) ikut bobot zirah itu -> bergerak bersama, tidak menembus keluar zirah
    src_names = json.loads(body["jd_fit_src"])
    pushv = [a.value for a in body.data.attributes["JD_FitPush"].data]
    srcv = [a.value for a in body.data.attributes["JD_FitSrc"].data]
    wmaps = []
    for n in src_names:
        o = bpy.data.objects.get(n)
        wmaps.append(json.loads(o["jd_weights"]) if o and "jd_weights" in o else {o["jd_bone"]: 1.0} if o and "jd_bone" in o else {})
    n_follow = 0
    for v in body.data.vertices:
        si = srcv[v.index]
        if si < 0 or not wmaps[si]:
            continue
        f = min(1.0, pushv[v.index] / FOLLOW_FULL)
        cur = {body.vertex_groups[g.group].name: g.weight for g in v.groups}
        for bn in set(cur) | set(wmaps[si]):
            w = (1 - f) * cur.get(bn, 0.0) + f * wmaps[si].get(bn, 0.0)
            vg = body.vertex_groups.get(bn) or body.vertex_groups.new(name=bn)
            if w > 1e-4:
                vg.add([v.index], w, "REPLACE")
            else:
                vg.remove([v.index])
        n_follow += 1
    smooth_weights(body, iters=2, factor=0.5)
    print(f"undersuit ikut zirah: {n_follow} vertex (penuh pada dorongan >= {FOLLOW_FULL * 100:.0f} cm)")
print("undersuit modifier:", [m.type for m in body.modifiers], "parent:", body.parent.name if body.parent else None)

# ------------------------------------------------------------------ bersihkan weight semua mesh
print(f"{'bagian':34s} grup  maks-influence  tanpa-weight")
for obj in parts:
    mx, unw = clean_weights(obj)
    report.append((obj.name, len(obj.vertex_groups), mx, unw))
    print(f"{obj.name:34s} {len(obj.vertex_groups):4d}  {mx:14d}  {unw:12d}")

# ------------------------------------------------------------------ socket
for name, (bone, pos) in SK.build_sockets().items():
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.05
    C.get_collection("09_Sockets").objects.link(e)
    e.parent = arm
    e.parent_type = "BONE"
    e.parent_bone = bone
    bpy.context.view_layer.update()
    e.matrix_world = Matrix.Translation(pos)
print("socket:", [o.name for o in bpy.data.objects if o.name.startswith("SOCKET_")])
print("selesai: parent semua bagian =", sorted({o.parent.name for o in parts if o.parent}))
