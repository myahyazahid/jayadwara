"""Modul bersama script Blender model Aksa (Iterasi 1+).

Koordinat: 1 unit = 1 m, karakter menghadap -Y, kiri karakter = +X (sisi `_l`), Z ke atas (sama dengan jd_common).
Armature = SKM_Manny_Simple asli (jalur (a), docs/19 Temuan Iterasi 0). Tinggi Aksa = tinggi Manny (A3 revisi):
H = 1,806 m (ujung rambut tertinggi). Ukuran dari konsep (docs/21, H = 1,75 m) dikali K.
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(r"C:\repository\unreal_engine\jayadwara")
ART = ROOT / "Art"
MANNY_FBX = ART / "Reference" / "manny" / "SKM_Manny_Simple.fbx"

H_CONCEPT = 1.75
H = 1.806
K = H / H_CONCEPT                                  # 1,032: konsep -> ukuran Manny
ARM_NAME = "AK_Armature"

if str(ART / "Scripts") not in sys.path:
    sys.path.insert(0, str(ART / "Scripts"))

# ---------------------------------------------------------------- warna (docs/21 bagian 3, kolom Usulan)
HEX = {
    "skin": "#C68965", "hair": "#1C1A1B", "eye": "#4A3426", "sclera": "#E8E4DC",
    "jacket": "#2B2E45", "shirt": "#1F1D1E", "pants": "#2F2C2E", "batik": "#5A3B2B",
    "gold": "#D6A33A", "boots": "#1A1817", "gloves": "#1F1D1E", "belt": "#1A1817", "stone": "#6B6B6E",
    "hair_hi": "#2E2420", "iris": "#5A3B27", "pupil": "#0E0B0A", "lip": "#B3735F", "sole": "#121010",
}


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def zone_rgba(zone):
    h = HEX[zone].lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)


# ---------------------------------------------------------------- material (5 slot, docs/19 6.3)
SLOTS = ["Skin", "Eyes", "Hair", "Cloth", "Gear"]
SLOT_ROUGHNESS = {"Skin": 0.55, "Eyes": 0.15, "Hair": 0.6, "Cloth": 0.85, "Gear": 0.6}


def get_material(slot):
    """`M_Aksa_<slot>`: warna dari atribut vertex `AK_Zone` (satu material per slot, banyak zona warna)."""
    name = f"M_Aksa_{slot}"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if mat.get("AK_TEX"):                            # sudah berbasis tekstur (Iterasi 5) -> jangan ditimpa
        return mat
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    attr = nt.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "AK_Zone"
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = SLOT_ROUGHNESS[slot]
    mat.use_backface_culling = False
    return mat


# ---------------------------------------------------------------- bagian (objek mesh)
def get_collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        raise RuntimeError(f"collection {name} tidak ada — jalankan aksa_00_setup_scene.py dulu")
    return c


def finish_part(name, bm, coll_name, zone, slot, kind="skin", bone=None, chain=None, smooth=True):
    """Ubah bmesh menjadi objek `AK_<name>`: warna zona + slot material + metadata rig.
    kind: skin (bobot dari jarak ke tulang) | rigid (satu tulang) | strip (sepanjang rantai tulang, atribut AK_t)."""
    loose = [v for v in bm.verts if not v.link_edges]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    ca = mesh.color_attributes.new("AK_Zone", "FLOAT_COLOR", "POINT")
    rgba = zone_rgba(zone)
    for d in ca.data:
        d.color = rgba
    mesh.materials.append(get_material(slot))
    obj = bpy.data.objects.new(name, mesh)
    get_collection(coll_name).objects.link(obj)
    obj["ak_kind"] = kind
    obj["ak_zone"] = zone
    obj["ak_slot"] = slot
    if bone:
        obj["ak_bone"] = bone
    if chain:
        obj["ak_chain"] = chain
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def remove_parts(prefix="AK_"):
    """Hapus mesh bagian AK_* (bukan referensi AK_REF_*) supaya proxy bisa dibuat ulang."""
    for ob in list(bpy.data.objects):
        if ob.type == "MESH" and ob.name.startswith(prefix) and not ob.name.startswith("AK_REF_"):
            bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)


def tri_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


# ---------------------------------------------------------------- rig
DEFORM = (["pelvis"] + [f"spine_0{i}" for i in range(1, 6)] + ["neck_01", "neck_02", "head"]
          + [f"{b}_{s}" for s in "lr" for b in ("clavicle", "upperarm", "lowerarm", "hand", "thigh", "calf", "foot", "ball")]
          + [f"sash_0{i}" for i in range(1, 7)])
SASH_N = 6
BODY_SHIFT_Y = 0.022       # badan (di bawah leher) digeser ke belakang agar cocok dengan sumbu konsep (hasil ukur siluet samping)


def sash_path():
    """7 titik pusat selendang (docs/21 D3): simpul di pinggul kiri-depan, jatuh di sisi depan-lateral paha kiri."""
    return [Vector((x, y + BODY_SHIFT_Y, z)) for x, y, z in [(0.09, -0.145, 1.05), (0.14, -0.145, 0.97), (0.175, -0.125, 0.85),
                                                              (0.185, -0.115, 0.75), (0.19, -0.11, 0.66), (0.19, -0.11, 0.59),
                                                              (0.19, -0.11, 0.55)]]


def get_arm():
    return bpy.data.objects[ARM_NAME]


def bone_head(arm, name):
    return arm.matrix_world @ arm.data.bones[name].head_local


def bone_segments(arm):
    """Segmen (awal, akhir) per tulang deform untuk bobot jarak."""
    h = lambda n: bone_head(arm, n)  # noqa: E731
    seg = {}
    chain = {"pelvis": "spine_01", "spine_01": "spine_02", "spine_02": "spine_03", "spine_03": "spine_04",
             "spine_04": "spine_05", "spine_05": "neck_01", "neck_01": "neck_02", "neck_02": "head"}
    for a, b in chain.items():
        seg[a] = (h(a), h(b))
    seg["head"] = (h("head"), h("head") + Vector((0, 0, 0.17)))
    for s in "lr":
        seg[f"clavicle_{s}"] = (h(f"clavicle_{s}"), h(f"upperarm_{s}"))
        seg[f"upperarm_{s}"] = (h(f"upperarm_{s}"), h(f"lowerarm_{s}"))
        seg[f"lowerarm_{s}"] = (h(f"lowerarm_{s}"), h(f"hand_{s}"))
        d = (h(f"hand_{s}") - h(f"lowerarm_{s}")).normalized()
        seg[f"hand_{s}"] = (h(f"hand_{s}"), h(f"hand_{s}") + d * 0.09)
        seg[f"thigh_{s}"] = (h(f"thigh_{s}"), h(f"calf_{s}"))
        seg[f"calf_{s}"] = (h(f"calf_{s}"), h(f"foot_{s}"))
        seg[f"foot_{s}"] = (h(f"foot_{s}"), h(f"ball_{s}"))
        seg[f"ball_{s}"] = (h(f"ball_{s}"), h(f"ball_{s}") + Vector((0, -0.07, 0)))
    pts = sash_path()
    for i in range(SASH_N):
        seg[f"sash_0{i + 1}"] = (pts[i], pts[i + 1])
    return seg


# ---------------------------------------------------------------- bobot
MAX_INFLUENCE = 4


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
    """Batasi influence per vertex dan normalisasi; kembalikan (maks influence, vertex tanpa bobot)."""
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
    mx = max((len([g for g in v.groups if g.weight > 1e-4]) for v in obj.data.vertices), default=0)
    return mx, unweighted


def smooth_weights(obj, iters=3, factor=0.5):
    """Haluskan bobot dengan rata-rata tetangga (hilangkan sambungan tajam)."""
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


def distance_weights(obj, seg, bone_names, k=3, power=4.0):
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


def mirror_x(bm, objs_names=None):
    """Salin geometri bm ke sisi -X (kiri -> kanan); kembalikan bmesh baru terpisah."""
    out = bm.copy()
    for v in out.verts:
        v.co.x = -v.co.x
    bmesh.ops.reverse_faces(out, faces=list(out.faces))
    return out
