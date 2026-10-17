"""K4.1 - Ekstrak atlas Tripo ke Textures/ + ukur hex per zona + audit bayangan terpanggang.

  blender --background <blend> --python Art/Scripts/tuyul_40_tex_extract.py -- --outdir <Textures dir>

Menulis T_Tuyul_Color.png, T_Tuyul_N.png, T_Tuyul_ORM.png (dari image di blend) dan mencetak
hex rata-rata/median per zona mesh (via UV) supaya bisa dibandingkan dengan palet kartu model.
"""
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuyul_paths as P  # noqa: E402

ROOT = P.ROOT
OBJ = "TY_Source"
PALET = {"kulit": "#8E9A8B", "kulit bayangan": "#6F7A6D", "cawat": "#5A4A3A", "mata": "#0B0B0B", "pendar Kala": "#8B1A1A"}


def arg(name, default=None):
    a = sys.argv
    if "--" in a:
        a = a[a.index("--") + 1:]
        if name in a:
            return a[a.index(name) + 1]
    return default


def lin2srgb(c):
    c = np.clip(np.asarray(c, dtype=np.float64), 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def hexof(rgb):
    return "#" + "".join(f"{max(0, min(255, int(round(c * 255)))):02X}" for c in rgb)


def zones(co):
    x, y, z = co
    out = []
    if z > 0.80:
        out.append("kepala")
    if z > 0.925 and abs(x) < 0.13 and abs(y) < 0.13:
        out.append("ubun-ubun")
    if z > 0.80 and y < -0.04:
        out.append("wajah")
    if 0.45 < z < 0.74 and y < -0.06 and abs(x) < 0.16:
        out.append("dada")
    if abs(x) > 0.18 and 0.28 < z < 0.74:
        out.append("lengan")
    if 0.18 < z < 0.46 and abs(x) < 0.22:
        out.append("pinggul/cawat")
    if z < 0.20:
        out.append("kaki")
    return out


def main():
    outdir = Path(arg("--outdir", str(P.TEX)))
    outdir.mkdir(parents=True, exist_ok=True)
    ob = bpy.data.objects[OBJ]
    me = ob.data

    # ---- 1. ekstrak peta
    rename = {}
    for img in bpy.data.images:
        n = img.name
        if n == "T_Tuyul_Color" or (n.startswith("T_Tuyul_Color") and "T_Tuyul_Color.png" not in rename):
            rename["T_Tuyul_Color.png"] = img        # nama tepat menang atas T_Tuyul_Color_k2 dst.
        elif n.startswith("NormalGL"):
            rename["T_Tuyul_N.png"] = img
        elif n.startswith("ORM"):
            rename["T_Tuyul_ORM.png"] = img
    for fn, img in rename.items():
        if (outdir / fn).exists() and "--force" not in sys.argv:
            print(f"LEWATI {fn}: sudah ada di {outdir} (tambah --force untuk menimpa tekstur final)")
            continue
        img.filepath_raw = str(outdir / fn)
        img.file_format = "PNG"
        img.save()
        p = outdir / fn
        print(f"simpan {fn}: {p.stat().st_size if p.exists() else 'GAGAL'} byte  {img.size[:]}  colorspace={img.colorspace_settings.name}")

    # ---- 2. UV per vertex
    uvl = me.uv_layers.active.data
    vuv = {}
    for p in me.polygons:
        for li in p.loop_indices:
            vuv.setdefault(me.loops[li].vertex_index, []).append(uvl[li].uv.copy())
    uv = {i: (sum(u.x for u in l) / len(l), sum(u.y for u in l) / len(l)) for i, l in vuv.items()}

    # ---- 3. baca peta warna ke numpy
    cimg = rename["T_Tuyul_Color.png"]
    W, H = cimg.size
    buf = np.empty(W * H * 4, dtype=np.float32)
    cimg.pixels.foreach_get(buf)
    px = buf.reshape(H, W, 4)
    srgb = np.zeros((H, W, 4), dtype=np.float64)
    srgb[:, :, :3] = lin2srgb(px[:, :, :3])
    srgb[:, :, 3] = px[:, :, 3]

    def sample(us):
        vals = []
        for u, v in us:
            xi = min(W - 1, max(0, int(u * W)))
            yi = min(H - 1, max(0, int(v * H)))
            vals.append(srgb[yi, xi, :3])
        return np.array(vals) if vals else np.zeros((0, 3))

    print("\n== hex sRGB per zona (median) vs palet kartu ==")
    print("palet:", PALET)
    for z in ["kepala", "ubun-ubun", "wajah", "dada", "lengan", "pinggul/cawat", "kaki"]:
        us = [uv[i] for i in uv if z in zones(me.vertices[i].co)]
        a = sample(us)
        if len(a) == 0:
            print(f"  {z:14s} 0 vertex")
            continue
        med = np.median(a, axis=0)
        mean = a.mean(axis=0)
        print(f"  {z:14s} n={len(a):5d}  median {hexof(med)}  rata2 {hexof(mean)}  V={med.max():.3f}")

    # ---- 4. audit bayangan terpanggang + area gelap (mata)
    rgb = srgb[:, :, :3]
    V = rgb.max(axis=2)
    tot = W * H
    for th, lab in ((0.10, "sangat gelap V<0,10 (mata/bayangan)"), (0.22, "gelap V<0,22 (bayangan terpanggang?)")):
        m = V < th
        n = int(m.sum())
        if n:
            ys, xs = np.nonzero(m)
            print(f"  {lab}: {n} px ({100*n/tot:.2f}%)  u {xs.min()/W:.2f}-{xs.max()/W:.2f}  v {ys.min()/H:.2f}-{ys.max()/H:.2f}")
    m = V > 0.85
    print(f"  terang V>0,85: {int(m.sum())} px ({100*m.sum()/tot:.2f}%)")
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-6), 0)
    kuning = (sat > 0.25) & (rgb[:, :, 0] > rgb[:, :, 2]) & (rgb[:, :, 1] > rgb[:, :, 2]) & (mx > 0.35)
    merah = (sat > 0.30) & (rgb[:, :, 0] > 1.35 * rgb[:, :, 1]) & (rgb[:, :, 0] > 1.35 * rgb[:, :, 2]) & (mx > 0.25)
    print(f"  kekuningan/keemasan (koin?) : {int(kuning.sum())} px ({100*kuning.sum()/tot:.2f}%)")
    print(f"  kemerahan (urat Kala?)      : {int(merah.sum())} px ({100*merah.sum()/tot:.2f}%)")


main()
