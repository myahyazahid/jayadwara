"""Aksa Iterasi 6 — paket export final: SK_Aksa.fbx (LOD0, morph target) + SK_Aksa_LOD1..3.fbx + socket JSON.

Jalankan di Blender (MCP: exec(open(path).read())) dengan aksa_v05_tex.blend terbuka (setelah aksa_50/51). Scene tidak berubah:
tiap LOD dibuat dari SALINAN bagian lewat hook PREP di aksa_14_export.py.
Anggaran (docs/19 A8): LOD0 <= 60k, LOD1 <= 25k, LOD2 <= 10k, LOD3 <= 4k tris.
Per LOD, per bagian: shape key dibuang (morph hanya di LOD0), decimate COLLAPSE (rasio per kelompok, minimal tris per bagian),
bobot dibersihkan (<= 4 influence, ternormalisasi), vertex/edge lepas dibuang. Bagian kecil (diagonal bbox < ambang) dibuang kecuali
yang dilindungi (mata, kepala, tangan, kalung+batu). Helai rambut: dikurangi di LOD1, dibuang di LOD2+ (lapisan rambut tetap).
"""
import os

import bmesh
import bpy
from mathutils import Vector

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
OUT_DIR = globals().get("OUT_DIR") or r"C:\repository\unreal_engine\jayadwara\Art\Export"
MESH_NAME = "SK_Aksa"
# level: (rasio dasar, minimal tris per bagian, buang bagian dengan diagonal bbox < m)
LODS = globals().get("LODS") or {1: (0.42, 24, 0.0), 2: (0.16, 12, 0.045), 3: (0.055, 8, 0.09)}
# pengali rasio per awalan nama (kepala/mata dijaga, rambut helai dipangkas keras)
RATIO_MUL = {"AK_Head": 1.5, "AK_EyeIris": 2.0, "AK_EyePupil": 2.0, "AK_EyeSclera": 1.3, "AK_HairShell": 1.2, "AK_Hand_": 1.2, "AK_Hair": 0.55,
             "AK_HairHi": 0.55, "AK_Brows": 1.5}
DROP_FROM = {"AK_Hair": 2, "AK_HairHi": 2, "AK_Lace_": 2, "AK_EyePupil": 3, "AK_Finger_": 3}   # bagian dibuang mulai LOD ini
PROTECT = ("AK_Head", "AK_EyeSclera", "AK_EyeIris", "AK_Hand_", "AK_Necklace", "AK_Stone", "AK_HairShell", "AK_Brows")
MAX_INF = 4


def tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def clean_weights(ob):
    for v in ob.data.vertices:
        gs = sorted(((g.group, g.weight) for g in v.groups), key=lambda x: -x[1])
        keep = {g: w for g, w in gs[:MAX_INF] if w > 1e-4} or ({gs[0][0]: 1.0} if gs else {})
        tot = sum(keep.values()) or 1.0
        for g, _w in gs:
            if g not in keep:
                ob.vertex_groups[g].remove([v.index])
        for g, w in keep.items():
            ob.vertex_groups[g].add([v.index], w / tot, "REPLACE")


def drop_loose(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=list(bm.edges))   # muka luas nol (sisa dinding tipis / decimate)
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES_FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()


def _pref(name, table, default):
    """Kunci berakhiran '_' = awalan (AK_Finger_ -> semua jari); selain itu nama persis (AK_Hair != AK_HairShell)."""
    return next((v for k, v in table.items() if (name.startswith(k) if k.endswith("_") else name == k)), default)


def make_prep(level, stats):
    ratio, min_tris, min_diag = LODS[level]

    def prep(d):
        name = d.name.rsplit(".", 1)[0]
        if level >= _pref(name, DROP_FROM, 99):
            stats["removed"].append(name)
            return False
        bb = [d.matrix_world @ Vector(c) for c in d.bound_box]
        diag = (Vector((max(p.x for p in bb), max(p.y for p in bb), max(p.z for p in bb)))
                - Vector((min(p.x for p in bb), min(p.y for p in bb), min(p.z for p in bb)))).length
        if min_diag and diag < min_diag and not name.startswith(PROTECT):
            stats["removed"].append(name)
            return False
        if d.data.shape_keys:
            d.shape_key_clear()                                   # morph target hanya di LOD0
        n = tris(d.data)
        r = min(1.0, max(ratio * _pref(name, RATIO_MUL, 1.0), min_tris / max(n, 1)))
        if r < 0.999:
            mod = d.modifiers.new("_lod", "DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = r
            mod.use_collapse_triangulate = True
            with bpy.context.temp_override(object=d, active_object=d, selected_objects=[d], selected_editable_objects=[d]):
                bpy.ops.object.modifier_move_to_index(modifier="_lod", index=0)
                bpy.ops.object.modifier_apply(modifier="_lod")
            drop_loose(d)
            clean_weights(d)
        stats["tris"] += tris(d.data)
        return True

    return prep


def run_export(fbx_out, prep):
    ns = {"__name__": "__ak_export__", "FBX_OUT": fbx_out, "MESH_NAME": MESH_NAME, "PREP": prep}
    exec(compile(open(os.path.join(SCRIPTS, "aksa_14_export.py"), encoding="utf-8").read(), "aksa_14_export.py", "exec"), ns)


lod0 = sum(tris(o.data) for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("AK_") and "ak_kind" in o)
summary = [("LOD0", lod0, 0)]
run_export(os.path.join(OUT_DIR, f"{MESH_NAME}.fbx"), None)
for lv in sorted(LODS):
    st = {"removed": [], "tris": 0}
    run_export(os.path.join(OUT_DIR, f"{MESH_NAME}_LOD{lv}.fbx"), make_prep(lv, st))
    summary.append((f"LOD{lv}", st["tris"], len(st["removed"])))
    print(f"LOD{lv}: dibuang {len(st['removed'])}:", sorted(st["removed"]))
print(f"\n{'LOD':6s} {'tris':>8s} {'% LOD0':>7s} {'dibuang':>8s}")
for nm, t, rm in summary:
    print(f"{nm:6s} {t:8d} {100 * t / lod0:6.1f}% {rm:8d}")
