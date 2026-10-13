"""Iterasi 5 — paket export final: LOD0–LOD3 (FBX terpisah) + data socket untuk Unreal.

Jalankan di Blender pada scene hero yang sudah di-rig (setelah 02/03/07/08). Scene asli tidak berubah:
tiap LOD dibuat dari SALINAN bagian lewat hook PREP di 05_export_fbx.py.

Keluaran (OUT_DIR, default Art/Export):
  SK_Jayadwara.fbx          LOD0 (penuh)
  SK_Jayadwara_LOD1..3.fbx  LOD1–3, skeleton sama (diimpor ke slot LOD di UE: Tools/ue_import_jayadwara.py)
  SK_Jayadwara_sockets.json socket: tulang induk + posisi (Blender m & ruang komponen UE cm) — UE tidak membuat
                            socket skeletal mesh dari empty FBX, jadi skrip UE membacanya dari sini.
Per LOD, per bagian: decimate COLLAPSE (rasio, dengan minimal tris per bagian) lalu bersihkan bobot (≤4 influence,
dinormalisasi) + buang vertex/edge tanpa muka; bagian yang lebih kecil dari ambang (diagonal bbox) dibuang, kecuali bagian yang dilindungi.
"""
import json
import os

import bmesh
import bpy
from mathutils import Vector

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
OUT_DIR = globals().get("OUT_DIR") or r"C:\repository\unreal_engine\jayadwara\Art\Export"
MESH_NAME = "SK_Jayadwara"
# docs/13 D4 (revisi Iterasi 6b): skala raksasa di-BAKE ke FBX supaya komponen mesh di UE berskala 1 (Anim Dynamics tidak
# mendukung komponen berskala). Model dibuat 1,90 m; tinggi game 45 m = PLACEHOLDER. Ganti GIANT_HEIGHT_M -> jalankan
# ulang skrip ini, Tools/ue_import_jayadwara.py, ue_setup_retarget.py, ue_setup_giant.py; samakan
# AJDGiantCharacter::MeshHeightCm.
BASE_HEIGHT_M = 1.90
GIANT_HEIGHT_M = globals().get("GIANT_HEIGHT_M") or 45.0
EXPORT_SCALE = GIANT_HEIGHT_M / BASE_HEIGHT_M                   # ≈ 23,68
# level: (rasio decimate, minimal tris per bagian, buang bagian dengan diagonal bbox < m)
LODS = globals().get("LODS") or {
    1: (0.50, 24, 0.0),
    2: (0.22, 16, 0.035),
    3: (0.09, 12, 0.080),
}
PROTECT = ("JD_Body_Undersuit", "JD_Head_Eye", "JD_Torso_Gem", "JD_Head_Faceplate")   # tidak pernah dibuang
# bagian berfaset tajam yang pecah jadi bidang abu-abu (terbaca "silver", aturan IP) bila didecimate terlalu jauh
MIN_RATIO = {"JD_Leg_KneeGuard_": 0.45, "JD_Head_Horn_": 0.40}
MAX_INF = 4


def tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def clean_weights(ob):
    """Decimate menggabungkan vertex -> himpunan tulang bisa > 4. Batasi 4 terbesar lalu normalisasi."""
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
    """Decimate agresif bisa menyisakan vertex/edge tanpa muka -> buang (validator: 0 vertex lepas)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES_FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()


def make_prep(level, stats):
    ratio, min_tris, min_diag = LODS[level]

    def prep(d):
        name = d.name.rsplit(".", 1)[0]
        bb = [d.matrix_world @ Vector(c) for c in d.bound_box]
        diag = (Vector((max(p.x for p in bb), max(p.y for p in bb), max(p.z for p in bb)))
                - Vector((min(p.x for p in bb), min(p.y for p in bb), min(p.z for p in bb)))).length
        if min_diag and diag < min_diag and not name.startswith(PROTECT):
            stats["removed"].append(name)
            return False
        n = tris(d.data)
        r = min(1.0, max(ratio, min_tris / max(n, 1), max([v for k, v in MIN_RATIO.items() if name.startswith(k)], default=0.0)))
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
    ns = {"__name__": "__jd_export__", "FBX_OUT": fbx_out, "MESH_NAME": MESH_NAME, "PREP": prep, "BAKE_CM": 100.0 * EXPORT_SCALE}
    exec(compile(open(os.path.join(SCRIPTS, "05_export_fbx.py"), encoding="utf-8").read(), "05_export_fbx.py", "exec"), ns)


summary = []
lod0_tris = sum(tris(o.data) for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("JD_") and "jd_kind" in o)
run_export(os.path.join(OUT_DIR, f"{MESH_NAME}.fbx"), None)
summary.append(("LOD0", lod0_tris, 0))
for lv in sorted(LODS):
    st = {"removed": [], "tris": 0}
    run_export(os.path.join(OUT_DIR, f"{MESH_NAME}_LOD{lv}.fbx"), make_prep(lv, st))
    summary.append((f"LOD{lv}", st["tris"], len(st["removed"])))
    print(f"LOD{lv}: dibuang {len(st['removed'])} bagian kecil:", sorted(st["removed"]))

# ---- socket: posisi rest (ruang dunia Blender, m) + perkiraan ruang komponen UE (cm; Blender -Y depan -> UE +Y)
arm = bpy.data.objects["JD_Armature"]
prev = arm.data.pose_position
arm.data.pose_position = "REST"
bpy.context.view_layer.update()
sockets = []
for o in sorted((o for o in bpy.data.objects if o.name.startswith("SOCKET_")), key=lambda o: o.name):
    p = o.matrix_world.translation
    sockets.append({"name": o.name, "bone": o.parent_bone, "blender_m": [round(p.x, 5), round(p.y, 5), round(p.z, 5)],
                    "ue_component_cm": [round(v * 100 * EXPORT_SCALE, 3) for v in (p.x, -p.y, p.z)]})
arm.data.pose_position = prev
with open(os.path.join(OUT_DIR, f"{MESH_NAME}_sockets.json"), "w", encoding="utf-8") as f:
    json.dump({"mesh": MESH_NAME, "export_scale": round(EXPORT_SCALE, 6), "giant_height_m": GIANT_HEIGHT_M,
               "note": "posisi rest; ue_component_cm = (x, -y, z) x 100 x export_scale (konversi terverifikasi di UE 5.6.1, Iterasi 6)",
               "sockets": sockets}, f, indent=2)

print(f"\n{'LOD':6s} {'tris':>8s} {'% LOD0':>7s} {'bagian dibuang':>15s}")
for nm, t, rm in summary:
    print(f"{nm:6s} {t:8d} {100 * t / lod0_tris:6.1f}% {rm:15d}")
print("socket:", len(sockets), "->", os.path.join(OUT_DIR, f"{MESH_NAME}_sockets.json"))
