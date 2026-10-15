"""K2.3 - IoU badan + simpangan permukaan (ray-parity, deterministik).

  blender --background --factory-startup --python Hermes/Tools/tuyul_27_iou.py -- <blend_A> <blend_B>

- IoU voxel: grid 5 mm, titik "di dalam" diuji dengan ray-parity (BVHTree) -> hasil
  konsisten antara dua mesh (tidak ada derau normal permukaan).
- Simpangan permukaan: closest_point_on_mesh, maks + rata-rata + jumlah > 1 mm.
"""
import sys
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OBJ = "TY_Source"
STEP = 0.005
DIR = Vector((0.0, 0.0, 1.0))  # sinar +Z


def arg(i):
    a = sys.argv
    if "--" in a:
        a = a[a.index("--") + 1:]
        if len(a) > i:
            return a[i]
    return None


def load_mesh(path, name):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [OBJ]
    ob = [o for o in dst.objects if o and o.type == "MESH"][0]
    bpy.context.scene.collection.objects.link(ob)
    ob.name = name
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    return ob


def inside(bvh, p, maxhit=256):
    o = p.copy()
    n = 0
    while n < maxhit:
        loc, nor, idx, dist = bvh.ray_cast(o, DIR, 50.0)
        if loc is None:
            break
        n += 1
        o = loc + DIR * 1e-5
    return (n % 2) == 1


def deviation(ob_from, ob_to):
    ds = []
    for v in ob_from.data.vertices:
        ok, loc, nor, _ = ob_to.closest_point_on_mesh(v.co)
        if ok:
            ds.append((v.co - loc).length)
    ds = np.array(ds)
    return ds.max(), ds.mean(), int((ds > 0.001).sum()), len(ds)


def main():
    pa, pb = arg(0), arg(1)
    bpy.ops.wm.open_mainfile(filepath=pb)
    obj_b = bpy.data.objects[OBJ]
    obj_a = load_mesh(pa, "TY_A")
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()

    print(f"A = {pa.split('/')[-1]} (v={len(obj_a.data.vertices)})")
    print(f"B = {pb.split('/')[-1]} (v={len(obj_b.data.vertices)})")

    for tag, o in (("A->B", (obj_a, obj_b)), ("B->A", (obj_b, obj_a))):
        mx, mn, n1, tot = deviation(o[0], o[1])
        print(f"simpangan {tag}: maks={mx*1000:.3f} mm  rata={mn*1000:.3f} mm  >1mm={n1}/{tot}")

    co = np.array([v.co[:] for v in obj_b.data.vertices])
    lo, hi = co.min(0) - STEP, co.max(0) + STEP
    xs = np.arange(lo[0], hi[0], STEP)
    ys = np.arange(lo[1], hi[1], STEP)
    zs = np.arange(lo[2], hi[2], STEP)
    print(f"grid {len(xs)}x{len(ys)}x{len(zs)} = {len(xs)*len(ys)*len(zs)} titik (step {STEP*1000:.0f} mm)")

    bvh_a = BVHTree.FromObject(obj_a, dg)
    bvh_b = BVHTree.FromObject(obj_b, dg)

    occ_a = np.zeros((len(xs), len(ys), len(zs)), dtype=bool)
    occ_b = np.zeros_like(occ_a)
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            for k, z in enumerate(zs):
                p = Vector((x, y, z))
                occ_a[i, j, k] = inside(bvh_a, p)
                occ_b[i, j, k] = inside(bvh_b, p)

    vox = STEP ** 3
    inter = int(np.logical_and(occ_a, occ_b).sum())
    union = int(np.logical_or(occ_a, occ_b).sum())
    iou = inter / union if union else 0.0
    sym = (union - inter) * vox
    print(f"voxel A_dalam={int(occ_a.sum())} B_dalam={int(occ_b.sum())}")
    print(f"irisan={inter}  gabung={union}  beda={union-inter} voxel")
    print(f"volume selisih simetris = {sym:.8f} m^3")
    print(f"IoU = {iou:.6f}   1-IoU = {1-iou:.6f}")
    print(f"LULUS bila 1-IoU <= 0.02 -> {'LULUS' if (1-iou) <= 0.02 else 'GAGAL'}")


main()
