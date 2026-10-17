"""K2.4 - Bersihkan 'merah basah' di tekstur warna (netralkan ke warna kulit).

  blender --background <blend_in> --python Art/Scripts/tuyul_28_tex_clean.py -- --out <blend_out>

Atlas Tripo dipertahankan; hanya warna merah dinetralkan:
  piksel "merah" = (R - max(G,B) > 0.06) dan R > 0.22  -> R diganti max(G,B)
  (pendar nanti lewat T_Tuyul_Emit di K4).
Simpan: T_Tuyul_Color_k2.png (bersih) + T_Tuyul_RedMask_k2.png (peta merah, bahan emissive K4),
lalu ganti tekstur di material dan simpan blend baru.
"""
import sys
from pathlib import Path
import numpy as np
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuyul_paths as P  # noqa: E402

ROOT = P.ROOT
TEX = P.WORK


def arg(name, default=None):
    a = sys.argv
    if "--" in a:
        a = a[a.index("--") + 1:]
        if name in a:
            return a[a.index(name) + 1]
    return default


def main():
    out = arg("--out")
    TEX.mkdir(parents=True, exist_ok=True)

    img = None
    for im in bpy.data.images:
        if im.name.startswith("Color") and im.size[0] > 0:
            img = im
            break
    if img is None:
        raise SystemExit("tekstur Color tidak ditemukan")
    w, h = img.size
    print(f"tekstur: {img.name} {w}x{h}")

    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    px = buf.reshape(h, w, 4)
    r = px[..., 0].copy()
    g = px[..., 1]
    b = px[..., 2]
    mx = np.maximum(g, b)
    red = (r - mx > 0.06) & (r > 0.22)
    n_red = int(red.sum())
    tot = w * h
    print(f"piksel merah (sebelum): {n_red} ({100*n_red/tot:.2f}%)")

    # netralkan: R -> max(G,B) (hue merah hilang, terang tetap)
    px[..., 0] = np.where(red, mx, r)
    print(f"rata-rata R sebelum={r.mean():.4f} sesudah={px[...,0].mean():.4f}")

    # gambar bersih
    clean = bpy.data.images.new("T_Tuyul_Color_k2", width=w, height=h, alpha=True)
    clean.pixels.foreach_set(buf)
    p = TEX / "T_Tuyul_Color_k2.png"
    clean.filepath_raw = str(p)
    clean.file_format = "PNG"
    clean.save()
    clean.pack()
    print("simpan:", p)

    # peta merah (putih=merah) untuk emissive K4
    m = np.zeros((h, w, 4), dtype=np.float32)
    m[..., 3] = 1.0
    m[..., 0] = red.astype(np.float32)
    m[..., 1] = red.astype(np.float32)
    m[..., 2] = red.astype(np.float32)
    mimg = bpy.data.images.new("T_Tuyul_RedMask_k2", width=w, height=h, alpha=True)
    mimg.pixels.foreach_set(m.reshape(-1))
    mp = TEX / "T_Tuyul_RedMask_k2.png"
    mimg.filepath_raw = str(mp)
    mimg.file_format = "PNG"
    mimg.save()
    print("simpan:", mp)

    # ganti tekstur di material
    n_swap = 0
    for mat in bpy.data.materials:
        if mat.use_nodes:
            for nd in mat.node_tree.nodes:
                if nd.type == "TEX_IMAGE" and nd.image is img:
                    nd.image = clean
                    n_swap += 1
                    print(f"material '{mat.name}': node '{nd.name}' -> T_Tuyul_Color_k2")
    if n_swap == 0:
        print("PERINGATAN: tidak ada node yang menunjuk tekstur Color")

    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print("disimpan:", out)


main()
