"""K5.7 - cari tepi teregang terburuk LANGSUNG di pose lengan (tanpa render, tanpa audit).

Pose `lengan_depan_atas` dari bagian "arah" profil: arahkan upperarm/lowerarm ke vektor dunia.
Untuk tiap LOD: laporkan tepi dengan regangan terbesar + posisi & bobot kedua ujungnya,
supaya jelas apakah penyebabnya bobot salah atau memang transisi bobot yang kasar.

  blender --background Hermes/Art/tuyul/Blender/tuyul_v08_lod.blend --python Hermes/Tools/tuyul_56_worst_edge.py
"""
import json

import bpy
from mathutils import Matrix, Vector

PROF = r"C:\repository\unreal_engine\jayadwara_hermes_tuyul\Hermes\Tools\pose_profil\tuyul.json"
POSE = "lengan_depan_atas"
arm = bpy.data.objects["TY_Armature"]
arah = json.load(open(PROF, encoding="utf-8"))["arah"][POSE]

for pb in arm.pose.bones:
    pb.matrix_basis.identity()
bpy.context.view_layer.update()


def aim(pb, d):
    d = (arm.matrix_world.inverted().to_3x3() @ Vector(d)).normalized()
    M = pb.matrix.copy()
    cur = (M.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
    head = M.translation.copy()
    pb.matrix = (Matrix.Translation(head) @ cur.rotation_difference(d).to_matrix().to_4x4()
                 @ Matrix.Translation(-head) @ M)
    bpy.context.view_layer.update()


for nm, d in arah.items():
    pb = arm.pose.bones.get(nm)
    if pb:
        aim(pb, d)
    else:
        print("  tulang tidak ada:", nm)

dg = bpy.context.evaluated_depsgraph_get()
for nm in ("TY_Source", "TY_Source_LOD1", "TY_Source_LOD2", "TY_Source_LOD3"):
    ob = bpy.data.objects.get(nm)
    if not ob:
        continue
    me = ob.data
    ev = ob.evaluated_get(dg)
    mev = ev.to_mesh()
    gname = {vg.index: vg.name for vg in ob.vertex_groups}
    W = [{gname[g.group]: round(g.weight, 2) for g in v.groups if g.weight > 0.05}
         for v in me.vertices]
    rows = []
    for e in me.edges:
        a, b = e.vertices
        l0 = (me.vertices[a].co - me.vertices[b].co).length
        if l0 <= 0.002:
            continue
        l1 = (mev.vertices[a].co - mev.vertices[b].co).length
        rows.append((abs(l1 - l0) / l0, a, b, l0, l1))
    rows.sort(key=lambda t: -t[0])
    print(f"== {nm} (pose {POSE}): {len(rows)} tepi diukur")
    for s, a, b, l0, l1 in rows[:4]:
        ca, cb = me.vertices[a].co, me.vertices[b].co
        print(f"   {100 * s:7.0f}%  rest {1000 * l0:6.2f} mm -> {100 * l1:6.1f} cm | "
              f"A ({ca.x:+.3f},{ca.y:+.3f},{ca.z:+.3f}) {W[a]} | "
              f"B ({cb.x:+.3f},{cb.y:+.3f},{cb.z:+.3f}) {W[b]}")
    ev.to_mesh_clear()
