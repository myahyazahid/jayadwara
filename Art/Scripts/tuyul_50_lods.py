"""K5.1 - LOD1-3 Tuyul dari TY_Source (LOD0 = 38.101 tris).

  blender --background Art/Blender/tuyul/tuyul_v07_material.blend --python Art/Scripts/tuyul_50_lods.py

Pola `Art/Scripts/jayadwara2_16_make_lods.py`: salinan mesh, grup `LODPROTECT`
(kepala+wajah+mata, tangan) dilindungi, Decimate COLLAPSE, buang vertex/edge lepas,
bobot dibersihkan (<= 4 influence, dinormalisasi), modifier Armature dipasang lagi.
Rasio decimate dicari otomatis: tris <= anggaran kartu, sedekat mungkin ke anggaran.
Anggaran (kartu K5): LOD1 30k, LOD2 14k, LOD3 6k. Scene asli tidak diubah.
Keluaran: Art/Blender/tuyul/tuyul_v08_lod.blend + Art/Export/Textures_Tuyul/_work/render_k5/_lod_tris.json
"""
import json
import sys
from pathlib import Path

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuyul_paths as P  # noqa: E402

ROOT = P.ROOT
OBJ, ARM = "TY_Source", "TY_Armature"
BUDGET = {1: 30000, 2: 14000, 3: 6000}
MAX_INF = 4
# zona lindung (angka dari laporan K0/K4: kepala z>0,80; wajah y<-0,04; ubun-ubun z>0,925)
# Zona menyesuaikan anggaran -- lantai decimate diukur di tuyul_50b_zone_tris.py:
#   kepala+tangan 9.848 tris (25,9%) -> LOD1 (30k) aman, tapi anggaran LOD3 (6k) TIDAK mungkin
#   wajah+tangan 4.413 tris (11,6%) -> LOD2 (14k)
#   wajah 3.072 tris (8,1%)         -> LOD3 (6k)
Z_KEPALA = 0.78
Z_WAJAH, Y_WAJAH = 0.80, -0.04
Z_TANGAN, X_TANGAN = 0.32, 0.20


def tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def drop_loose(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()


def clean_weights(ob):
    vgs = {vg.index: vg for vg in ob.vertex_groups}
    for v in ob.data.vertices:
        gs = sorted(((g.group, g.weight) for g in v.groups
                     if vgs[g.group].name != "LODPROTECT" and g.weight > 1e-4), key=lambda t: -t[1])
        keep, drop = gs[:MAX_INF], gs[MAX_INF:]
        tot = sum(w for _, w in keep) or 1.0
        for gi, _ in drop:
            vgs[gi].remove([v.index])
        for gi, w in keep:
            vgs[gi].add([v.index], w / tot, "REPLACE")


def transfer_weights(d, src):
    """Kembalikan bobot tiap vertex LOD dari bobot LOD0 di titik permukaan terdekat.

    Decimate COLLAPSE mengaduk transisi bobot yang tadinya tajam (mis. di bahu:
    vertex `upperarm_r` 1,0 jadi `clavicle_r` 0,62 + `upperarm_r` 0,38) sehingga
    bahu teregang 14-35 cm saat pose. Diagnosa: tuyul_54_weight_diag.py (0,18% vertex
    menyimpang, semua di clavicle). Data Transfer = cara standar memindahkan bobot
    antar-LOD: interpolasi di atas muka LOD0 terdekat, bukan rata-rata vertex tetangga.
    """
    mod = d.modifiers.new("_xfer", "DATA_TRANSFER")
    mod.object = src
    mod.use_vert_data = True
    mod.data_types_verts = {"VGROUP_WEIGHTS"}
    mod.vert_mapping = "POLYINTERP_NEAREST"
    mod.layers_vgroup_select_src = "ALL"
    mod.layers_vgroup_select_dst = "NAME"
    mod.mix_mode = "REPLACE"
    mod.mix_factor = 1.0
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    d.select_set(True)
    bpy.context.view_layer.objects.active = d
    bpy.ops.object.modifier_apply(modifier="_xfer")


def protect(ob, level):
    """Zona lindung menyesuaikan anggaran: LOD1 kepala+tangan, LOD2 wajah+tangan, LOD3 wajah."""
    kepala = lambda c: c.z > Z_KEPALA
    wajah = lambda c: c.z > Z_WAJAH and c.y < Y_WAJAH
    tangan = lambda c: abs(c.x) > X_TANGAN and c.z < Z_TANGAN
    aturan = {1: lambda c: kepala(c) or tangan(c),
              2: lambda c: wajah(c) or tangan(c),
              3: wajah}[level]
    vg = ob.vertex_groups.new(name="LODPROTECT")
    n = 0
    for v in ob.data.vertices:
        if aturan(v.co):
            vg.add([v.index], 1.0, "REPLACE")
            n += 1
    return n


def apply_decimate(d, ratio):
    mod = d.modifiers.new("Decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    mod.vertex_group = "LODPROTECT"
    mod.invert_vertex_group = True   # bobot 1 = didecimate -> dibalik: LODPROTECT = dilindungi
    mod.vertex_group_factor = 1.0
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    d.select_set(True)
    bpy.context.view_layer.objects.active = d
    bpy.ops.object.modifier_apply(modifier="Decimate")


src = bpy.data.objects[OBJ]
arm = bpy.data.objects[ARM]
t0 = tris(src.data)
xs = [v.co.x for v in src.data.vertices]
zs = [v.co.z for v in src.data.vertices]
print(f"LOD0 TY_Source: {t0} tris | x {min(xs):+.3f}..{max(xs):+.3f} | z {min(zs):+.3f}..{max(zs):+.3f}")
print(f"matrix_world TY_Source = {[round(v, 4) for v in src.matrix_world.translation]} "
      f"parent={src.parent.name if src.parent else None}")
nprot0 = sum(1 for v in src.data.vertices if v.co.z > Z_KEPALA or (abs(v.co.x) > X_TANGAN and v.co.z < Z_TANGAN))
print(f"zona lindung: {nprot0} vertex ({100.0 * nprot0 / len(src.data.vertices):.2f}% vertex) "
      f"[kepala z>{Z_KEPALA}, tangan |x|>{X_TANGAN} & z<{Z_TANGAN}]")

report = {"LOD0": t0, "zona_lindung_vertex": nprot0}
for level in sorted(BUDGET):
    budget = BUDGET[level]
    ratio = budget / t0
    for attempt in range(1, 9):
        d = src.copy()
        d.data = src.data.copy()
        d.name = d.data.name = f"TY_Source_LOD{level}"
        bpy.context.scene.collection.objects.link(d)
        d.modifiers.clear()
        d.parent = None
        nprot = protect(d, level)
        apply_decimate(d, ratio)
        drop_loose(d)
        d.vertex_groups.remove(d.vertex_groups["LODPROTECT"])
        transfer_weights(d, src)   # bobot dari LOD0 (interpolasi muka) -- perbaiki adukan decimate
        clean_weights(d)
        t = tris(d.data)
        print(f"  LOD{level} coba {attempt}: rasio {ratio:.3f} -> {t} tris (anggaran {budget})")
        if t <= budget:
            am = d.modifiers.new("Armature", "ARMATURE")
            am.object = arm
            am.use_vertex_groups = True
            d.parent = arm
            d.parent_type = "OBJECT"
            report[f"LOD{level}"] = t
            report[f"LOD{level}_rasio"] = round(ratio, 4)
            print(f"LOD{level}: {t} tris (rasio {ratio:.3f}, anggaran {budget}) OK "
                  f"| {100.0 * t / t0:.1f}% dari LOD0 | lindung {nprot} vertex")
            break
        ratio = max(0.02, ratio * budget / t * 0.97)
        bpy.data.objects.remove(d, do_unlink=True)
    else:
        print(f"LOD{level}: GAGAL mencapai anggaran {budget} - lantai {t} tris (dilaporkan, bukan dipaksa)")
        report[f"LOD{level}"] = None
        report[f"LOD{level}_lantai"] = t

out = P.WORK / "render_k5"
out.mkdir(parents=True, exist_ok=True)
(out / "_lod_tris.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(P.BLENDER / "tuyul_v08_lod.blend"))
print("simpan tuyul_v08_lod.blend")
print("ringkasan:", report)
