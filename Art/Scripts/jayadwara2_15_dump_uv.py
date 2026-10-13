"""Jayadwara2 R4 — simpan geometri (posisi rest per segitiga + UV) untuk make_textures_jayadwara2.py (Python luar Blender, ada PIL).
  blender --background Art/Blender/jayadwara2_v03_rig_r2.blend --python Art/Scripts/jayadwara2_15_dump_uv.py
Hasil: Art/Export/_jd2/_mesh_uv.npz  (tri_pos [N,3,3] meter, tri_uv [N,3,2])."""
import bpy
import numpy as np

ob = bpy.data.objects["JD2_Body"]
me = ob.data
me.calc_loop_triangles()
uv = me.uv_layers.active.data
pos = np.array([v.co[:] for v in me.vertices], np.float32)
tri_pos, tri_uv = [], []
for t in me.loop_triangles:
    tri_pos.append(pos[list(t.vertices)])
    tri_uv.append([uv[i].uv[:] for i in t.loops])
np.savez(r"C:\repository\unreal_engine\jayadwara\Art\Export\_jd2\_mesh_uv.npz", tri_pos=np.array(tri_pos, np.float32), tri_uv=np.array(tri_uv, np.float32))
print("ok", len(tri_pos), "segitiga")
