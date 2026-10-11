"""Iterasi 3 — pemeriksa deformasi numerik atas Action JD_PoseTest (frame 1 = rest).

1) Peregangan: rasio panjang tepi undersuit (pose / rest) per frame. Ditandai: <0,6 (runtuh) atau >1,6 (terentang).
2) Penetrasi: jumlah pasang segitiga yang saling berpotongan (BVH) antar kelompok armor, dikurangi jumlah di pose rest
   (pasangan yang memang bersentuhan di rest tidak dihitung sebagai masalah).
Hasil dicetak sebagai tabel; variabel DEFORM_RESULT (dict) berisi angka mentah.
"""
import bpy
from mathutils.bvhtree import BVHTree

scene = bpy.context.scene
POSE_NAMES = ["a_pose", "kuda_kuda", "pukul", "tendang", "injak", "jongkok", "tangan_atas", "raih_depan",
              "tendang_tinggi", "tangkis", "bungkuk", "putar_badan", "tengok"]
F0, F1 = scene.frame_start, scene.frame_end
ABS_LIMIT = 0.04            # m; batas perubahan panjang tepi (ditetapkan setelah melihat distribusi — lihat docs/13)

GROUPS = {
    "helm": ("JD_Head_Helm", "JD_Head_Fin_", "JD_Head_Cheek_", "JD_Head_Faceplate", "JD_Head_Chin", "JD_Head_NeckGuard"),
    "horn_L": ("JD_Head_Horn_L", "JD_Head_Brow_L"), "horn_R": ("JD_Head_Horn_R", "JD_Head_Brow_R"),
    "chest": ("JD_Torso_Chest", "JD_Torso_Chevron", "JD_Torso_Gem"), "back": ("JD_Torso_Back",), "collar": ("JD_Torso_Collar",),
    "pauldron_L": ("JD_Shoulder_Pauldron_L", "JD_Shoulder_Lame_L", "JD_Shoulder_Under_L", "JD_Shoulder_Spike_L"),
    "pauldron_R": ("JD_Shoulder_Pauldron_R", "JD_Shoulder_Lame_R", "JD_Shoulder_Under_R", "JD_Shoulder_Spike_R"),
    "bracer_L": ("JD_Arm_Bracer_L", "JD_Arm_BracerInset_L"), "bracer_R": ("JD_Arm_Bracer_R", "JD_Arm_BracerInset_R"),
    "belt": ("JD_Belt_Band",),
    "thigh_L": ("JD_Leg_ThighGuard_L",), "thigh_R": ("JD_Leg_ThighGuard_R",),
    "greave_L": ("JD_Leg_Greave_L", "JD_Leg_KneeGuard_L"), "greave_R": ("JD_Leg_Greave_R", "JD_Leg_KneeGuard_R"),
    "cloth_F": ("JD_Cloth_Front",), "cloth_B": ("JD_Cloth_Back",),
    "scarf_L": ("JD_Cloth_Scarf_L",), "scarf_R": ("JD_Cloth_Scarf_R",),
}
PAIRS = [("helm", "collar"), ("collar", "pauldron_L"), ("collar", "pauldron_R"), ("helm", "pauldron_L"), ("helm", "pauldron_R"), ("helm", "chest"), ("horn_L", "pauldron_L"), ("horn_R", "pauldron_R"),
         ("pauldron_L", "chest"), ("pauldron_R", "chest"), ("pauldron_L", "back"), ("pauldron_R", "back"),
         ("bracer_L", "pauldron_L"), ("bracer_R", "pauldron_R"), ("bracer_L", "belt"), ("bracer_R", "belt"),
         ("bracer_L", "chest"), ("bracer_R", "chest"), ("chest", "belt"), ("back", "belt"),
         ("thigh_L", "thigh_R"), ("greave_L", "greave_R"), ("thigh_L", "belt"), ("thigh_R", "belt"),
         ("thigh_L", "greave_L"), ("thigh_R", "greave_R"), ("thigh_L", "cloth_F"), ("thigh_R", "cloth_F"),
         ("greave_L", "cloth_F"), ("greave_R", "cloth_F"), ("greave_L", "scarf_L"), ("greave_R", "scarf_R"),
         ("thigh_L", "scarf_L"), ("thigh_R", "scarf_R"), ("greave_L", "cloth_B"), ("greave_R", "cloth_B")]
USED = sorted({g for pair in PAIRS for g in pair})


def members(prefixes):
    return [o for o in bpy.data.objects
            if o.type == "MESH" and o.name.startswith("JD_") and any(o.name.startswith(p) for p in prefixes)]


def group_bvh(objs, dg):
    verts, polys = [], []
    for ob in objs:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        off = len(verts)
        mw = ev.matrix_world
        verts += [mw @ v.co for v in me.vertices]
        polys += [tuple(off + i for i in lt.vertices) for lt in me.loop_triangles]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys, epsilon=1e-5)


body = bpy.data.objects["JD_Body_Undersuit"]
edges = [tuple(e.vertices) for e in body.data.edges]
gmem = {k: members(GROUPS[k]) for k in USED}
missing = [k for k, v in gmem.items() if not v]
if missing:
    print("! kelompok kosong:", missing)
rest_pos = None
stretch, overlaps = {}, {}
for f in range(F0, F1 + 1):
    scene.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    me = ev.to_mesh()
    pos = [ev.matrix_world @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    if f == F0:
        rest_pos = pos
    ratios, dabs = [], []
    for a, b in edges:
        r0 = (rest_pos[a] - rest_pos[b]).length
        r1 = (pos[a] - pos[b]).length
        ratios.append(r1 / r0 if r0 > 1e-9 else 1.0)
        dabs.append(abs(r1 - r0))
    # rasio saja menyesatkan di tepi sangat pendek (median tepi ±2,4 cm) -> pakai perubahan panjang ABSOLUT
    stretch[f] = (min(ratios), max(ratios), sum(1 for d in dabs if d > ABS_LIMIT), max(dabs))
    bv = {k: group_bvh(v, dg) for k, v in gmem.items() if v}
    for a, b in PAIRS:
        overlaps[(a, b, f)] = len(bv[a].overlap(bv[b])) if a in bv and b in bv else 0


def pname(f):
    return POSE_NAMES[f - F0] if f - F0 < len(POSE_NAMES) else f"f{f}"


print(f"== PEREGANGAN undersuit: perubahan panjang tepi absolut (batas {ABS_LIMIT * 100:.0f} cm ≈ 2% tinggi badan; median tepi 2,4 cm)")
print(f"{'pose':16s} {'rasio min':>9s} {'rasio maks':>10s} {'perubahan maks (cm)':>20s} {'tepi > batas':>13s}")
for f, (lo, hi, bad, dmax) in stretch.items():
    print(f"{pname(f):16s} {lo:9.2f} {hi:10.2f} {dmax * 100:20.1f} {bad:13d}")
print("\n== PENETRASI BARU antar armor (segitiga berpotongan dikurangi rest); hanya delta > 0")
rows = []
for a, b in PAIRS:
    base = overlaps[(a, b, F0)]
    worst = max(range(F0, F1 + 1), key=lambda f: overlaps[(a, b, f)])
    rows.append((overlaps[(a, b, worst)] - base, a, b, base, pname(worst)))
for d, a, b, base, wf in sorted(rows, reverse=True):
    if d > 0:
        print(f"  {a:11s} x {b:11s} rest={base:4d}  baru maks=+{d:4d}  pada pose '{wf}'")
print(f"  (tanpa penetrasi baru: {sum(1 for r in rows if r[0] <= 0)} dari {len(rows)} pasangan)")
DEFORM_RESULT = {"stretch": stretch, "rows": rows}
scene.frame_set(F0)
