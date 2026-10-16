"""K5.8 - uji penentu: apakah tepi seam bahu (vertex 100% clavicle_l <-> 100% upperarm_l)
ADA sebagai tepi di aset FBX? Banding SK_Tuyul.fbx (LOD0, audit 4,73 cm) vs LOD1 (34,73 cm).

  blender --background --factory-startup --python Hermes/Tools/tuyul_57_fbx_seam.py
"""
import bpy

OUT = r"C:\repository\unreal_engine\jayadwara_hermes_tuyul\Hermes\Art\tuyul\Export"
for nm in ("SK_Tuyul.fbx", "SK_Tuyul_LOD1.fbx", "SK_Tuyul_LOD2.fbx", "SK_Tuyul_LOD3.fbx"):
    bpy.ops.wm.read_homefile(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=OUT + "\\" + nm)
    obs = [o for o in bpy.data.objects if o.type == "MESH"]
    if not obs:
        print(nm, "TIDAK ADA MESH")
        continue
    ob = obs[0]
    me = ob.data
    gn = {vg.index: vg.name for vg in ob.vertex_groups}
    A = {v.index for v in me.vertices
         if any(gn[g.group] == "clavicle_l" and g.weight > 0.99 for g in v.groups)}
    B = {v.index for v in me.vertices
         if any(gn[g.group] == "upperarm_l" and g.weight > 0.99 for g in v.groups)}
    edges = {tuple(sorted(e.vertices)) for e in me.edges}
    zs = [v.co.z for v in me.vertices]
    hit = []
    for a in A:
        for b in B:
            if (a, b) in edges or (b, a) in edges:
                d = (me.vertices[a].co - me.vertices[b].co).length
                hit.append((d, a, b))
    hit.sort()
    print(f"{nm}: verts {len(me.vertices)} tris {sum(len(p.vertices) - 2 for p in me.polygons)} "
          f"z {min(zs):.3f}..{max(zs):.3f} | vertex clavicle_l-100% {len(A)}, upperarm_l-100% {len(B)} "
          f"| tepi penghubung: {len(hit)}")
    for d, a, b in hit[:3]:
        print(f"    panjang {1000 * d:6.2f} mm  v{a} {tuple(round(c, 3) for c in me.vertices[a].co)} "
              f"v{b} {tuple(round(c, 3) for c in me.vertices[b].co)}")
