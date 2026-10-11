"""Modul bersama untuk script Blender Jayadwara (Iterasi 1+).

Koordinat: 1 unit = 1 m. Karakter menghadap -Y; kiri karakter = +X (sisi `_l`). Z ke atas.
Dimensi mengikuti docs/14-model-sheet-jayadwara.md (H = 1,90 m).
"""
import json
import math

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

H = 1.90
SIDES = {"l": +1, "r": -1}

# ---------------------------------------------------------------- warna (docs/14, bagian 3)
HEX = {
    # revisi: warna dibuat sehidup konsep (nilai mid hasil ukur docs/14 tampak kusam di bawah pencahayaan render)
    "red": "#A8262B", "gold": "#D6A33A", "black": "#2A2626",
    "white": "#E2E0DE", "marun": "#5A1A1E",
    "gem": "#FFC86B", "eye": "#FFF1C8",
}
EMISSIVE = {"gem", "eye"}


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def zone_rgba(zone):
    h = HEX[zone].lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0 if zone in EMISSIVE else 0.0)


# ---------------------------------------------------------------- material (4 slot, docs/13 6.3)
SLOT_ROUGHNESS = {"Body": 0.65, "Armor": 0.40, "Cloth": 0.75, "Face": 0.30}


def get_material(slot):
    """Material `M_Jayadwara_<slot>`: warna dari atribut vertex `JD_Zone`; alpha atribut = emissive."""
    name = f"M_Jayadwara_{slot}"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if mat.get("JD_TEX"):                    # sudah dibangun ulang berbasis tekstur (08_materials.py) -> jangan ditimpa
        return mat
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    attr = nt.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "JD_Zone"
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 3.0
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(attr.outputs["Alpha"], mul.inputs[0])
    nt.links.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = SLOT_ROUGHNESS[slot]
    if slot == "Cloth":
        mat.use_backface_culling = False
    return mat


# ---------------------------------------------------------------- primitif bmesh
def _m(center=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    return (Matrix.Translation(center) @ Euler(rot, "XYZ").to_matrix().to_4x4()
            @ Matrix.Diagonal((*scale, 1.0)))


def add_box(bm, center, size, rot=(0, 0, 0)):
    bmesh.ops.create_cube(bm, size=1.0, matrix=_m(center, rot, size))


def add_ico(bm, center, radii, sub=1, rot=(0, 0, 0)):
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0, matrix=_m(center, rot, radii))


def add_cyl(bm, center, radii_xy, height, seg=8, rot=(0, 0, 0)):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=1.0, radius2=1.0, depth=1.0,
                          matrix=_m(center, rot, (radii_xy[0], radii_xy[1], height)))


def add_prism(bm, p0, p1, r0, r1, seg=6, cap=True, squash=(1.0, 1.0)):
    """Kerucut terpancung dari p0 ke p1 (radius r0 -> r1). `squash` = skala sumbu lokal X/Y (penampang elips)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    length = d.length
    quat = d.to_track_quat("Z", "Y")
    m = (Matrix.Translation((p0 + p1) / 2) @ quat.to_matrix().to_4x4()
         @ Matrix.Diagonal((squash[0], squash[1], 1.0, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=cap, segments=seg, radius1=r0, radius2=max(r1, 1e-4), depth=length, matrix=m)


def add_hull(bm, pts):
    """Padatan cembung dari titik-titik (bentuk bersudut)."""
    verts = [bm.verts.new(Vector(p)) for p in pts]
    bmesh.ops.convex_hull(bm, input=verts, use_existing_faces=False)
    # buang titik yang tidak terpakai oleh hull
    unused = [v for v in verts if v.is_valid and not v.link_faces]
    if unused:
        bmesh.ops.delete(bm, geom=unused, context="VERTS")


def add_strip(bm, centerline, widths, side_vecs, t_layer_name="JD_t"):
    """Strip kain: baris vertex kiri/kanan sepanjang `centerline`. Lebar 0 di ujung -> satu vertex (runcing).
    `side_vecs` = satu vektor arah-lebar per titik. Menyimpan parameter panjang t (0..1) di layer float `JD_t`."""
    layer = bm.verts.layers.float.get(t_layer_name) or bm.verts.layers.float.new(t_layer_name)
    n = len(centerline)
    rows = []
    for i, (p, w) in enumerate(zip(centerline, widths)):
        t = i / (n - 1)
        p = Vector(p)
        sv = Vector(side_vecs[i])
        if w <= 1e-6:
            v = bm.verts.new(p)
            v[layer] = t
            rows.append((v,))
        else:
            vl = bm.verts.new(p - sv * (w / 2))
            vr = bm.verts.new(p + sv * (w / 2))
            vl[layer] = t
            vr[layer] = t
            rows.append((vl, vr))
    for a, b in zip(rows[:-1], rows[1:]):
        if len(a) == 2 and len(b) == 2:
            bm.faces.new((a[0], a[1], b[1], b[0]))
        elif len(a) == 2 and len(b) == 1:
            bm.faces.new((a[0], a[1], b[0]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))


# ---------------------------------------------------------------- bagian (part)
def get_collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        raise RuntimeError(f"collection {name} tidak ada — jalankan setup scene dulu")
    return c


def finish_part(name, bm, coll_name, zone, slot, kind="rigid", bone=None, weights=None,
                chain=None, smooth=False, bones=None):
    """Ubah bmesh menjadi objek, beri warna zona + material slot + metadata rig."""
    loose = [v for v in bm.verts if not v.link_edges]      # higiene: buang vertex lepas (mis. artefak Skin modifier)
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    if smooth == "angle":                                   # hard-surface: muka smooth, tepi > 35° tetap tajam
        for f in bm.faces:
            f.smooth = True
        for e in bm.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(35):
                e.smooth = False
        smooth = False
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    ca = mesh.color_attributes.new("JD_Zone", "FLOAT_COLOR", "POINT")
    rgba = zone_rgba(zone)
    for d in ca.data:
        d.color = rgba
    mesh.materials.append(get_material(slot))
    obj = bpy.data.objects.new(name, mesh)
    get_collection(coll_name).objects.link(obj)
    obj["jd_kind"] = kind                    # rigid | skin | strip
    obj["jd_zone"] = zone
    if bone:
        obj["jd_bone"] = bone
    if weights:
        obj["jd_weights"] = json.dumps(weights)
    if chain:
        obj["jd_chain"] = chain              # nama dasar rantai tulang, mis. "scarf_l"
    if bones:
        obj["jd_bones"] = json.dumps(list(bones))   # daftar eksplisit tulang rantai (mis. 3 ruas jari), urut dari pangkal
    if smooth:
        try:
            mesh.shade_smooth()
        except AttributeError:
            for p in mesh.polygons:
                p.use_smooth = True
    return obj


def remove_existing(prefix="JD_"):
    """Hapus objek mesh bagian JD_* (bukan REF/LM/SOCKET) agar blockout bisa dibuat ulang."""
    for ob in list(bpy.data.objects):
        if ob.type == "MESH" and ob.name.startswith(prefix):
            bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)


def tri_count(obj, depsgraph=None):
    dg = depsgraph or bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    ev.to_mesh_clear()
    return n
