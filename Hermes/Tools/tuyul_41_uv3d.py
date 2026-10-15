"""K4.2 - Rasterisasi atlas: tiap texel diberi posisi 3D (pola docs/25 make_textures_jayadwara2.py).

  blender --background <blend> --python Hermes/Tools/tuyul_41_uv3d.py -- --outdir <dir>

Keluaran: uv_zone.png (peta zona), uv_pos_z.png (kedalaman), dan cetakan silang:
  texel per zona, silang peta MERAH (dari K2) vs zona, histogram metalik ORM vs zona.
Dipakai untuk menentukan zona pendar T_Tuyul_Emit (mata, urat dada/lengan, ubun-ubun, ornamen).
"""
import sys
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(r"C:\repository\unreal_engine\jayadwara_hermes_tuyul")
OBJ = "TY_Source"
W = H = 4096
BAND = 256  # baris per potong supaya hemat memori


def arg(name, default=None):
    a = sys.argv
    if "--" in a:
        a = a[a.index("--") + 1:]
        if name in a:
            return a[a.index(name) + 1]
    return default


def load_img(path):
    img = bpy.data.images.load(str(path), check_existing=False)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    return buf.reshape(h, w, 4), img


def save_rgb(name, arr, path, colorspace="Non-Color"):
    """arr: (H,W,4) float 0..1"""
    img = bpy.data.images.new(name, width=arr.shape[1], height=arr.shape[0], alpha=True, float_buffer=False)
    img.colorspace_settings.name = colorspace
    img.pixels.foreach_set(np.ascontiguousarray(arr, dtype=np.float32).ravel())
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()
    print("simpan", path.name, arr.shape[1], "x", arr.shape[0])


def main():
    outdir = Path(arg("--outdir", str(ROOT / "Hermes" / "Art" / "tuyul" / "Render" / "k4")))
    outdir.mkdir(parents=True, exist_ok=True)
    me = bpy.data.objects[OBJ].data
    me.calc_loop_triangles()
    uvl = me.uv_layers.active.data
    co = np.array([v.co[:] for v in me.vertices], dtype=np.float32)

    pos = np.full((H, W, 3), np.nan, dtype=np.float32)
    nt = len(me.loop_triangles)
    print("trianggel:", nt)
    for k, t in enumerate(me.loop_triangles):
        li = t.loops
        uvs = np.array([[uvl[i].uv[0], uvl[i].uv[1]] for i in li], dtype=np.float64)
        p = np.array([co[me.loops[i].vertex_index] for i in li], dtype=np.float32)
        px, py = uvs[:, 0] * W, uvs[:, 1] * H
        x0 = max(0, int(np.floor(px.min())))
        x1 = min(W - 1, int(np.ceil(px.max())))
        y0 = max(0, int(np.floor(py.min())))
        y1 = min(H - 1, int(np.ceil(py.max())))
        if x1 < x0 or y1 < y0:
            continue
        d = (py[1] - py[2]) * (px[0] - px[2]) + (px[2] - px[1]) * (py[0] - py[2])
        if abs(d) < 1e-12:
            continue
        xs = np.arange(x0, x1 + 1) + 0.5
        for ya in range(y0, y1 + 1, BAND):
            yb = min(y1, ya + BAND - 1)
            gx, gy = np.meshgrid(xs, np.arange(ya, yb + 1) + 0.5)
            w0 = ((py[1] - py[2]) * (gx - px[2]) + (px[2] - px[1]) * (gy - py[2])) / d
            w1 = ((py[2] - py[0]) * (gx - px[2]) + (px[0] - px[2]) * (gy - py[2])) / d
            w2 = 1.0 - w0 - w1
            m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not m.any():
                continue
            P = (w0[..., None] * p[0] + w1[..., None] * p[1] + w2[..., None] * p[2]).astype(np.float32)
            sub = pos[ya:yb + 1, x0:x1 + 1]
            sub[m] = P[m]
        if k % 8000 == 0:
            print("  tri", k)

    x, y, z = pos[:, :, 0], pos[:, :, 1], pos[:, :, 2]
    valid = ~np.isnan(z)
    print("texel terisi:", int(valid.sum()), f"({100*valid.sum()/(W*H):.2f}% atlas)")

    Z = {
        "ubun-ubun": valid & (z > 0.925) & (np.abs(x) < 0.13) & (np.abs(y) < 0.13),
        "kepala": valid & (z > 0.80),
        "wajah": valid & (z > 0.80) & (y < -0.04),
        "dada": valid & (z > 0.45) & (z < 0.74) & (y < -0.06) & (np.abs(x) < 0.16),
        "lengan": valid & (np.abs(x) > 0.18) & (z > 0.28) & (z < 0.74),
        "pinggul": valid & (z > 0.18) & (z < 0.46) & (np.abs(x) < 0.22),
        "kaki": valid & (z < 0.20),
    }
    print("\n== texel per zona ==")
    for k, m in Z.items():
        print(f"  {k:10s} {int(m.sum()):9d}")

    # peta merah dari K2 (dari atlas ASLI sebelum netralisasi)
    rp = ROOT / "Hermes" / "Art" / "tuyul" / "Texture" / "T_Tuyul_RedMask_k2.png"
    red = np.zeros((H, W), dtype=bool)
    if rp.exists():
        rimg, _ = load_img(rp)
        red = rimg[:, :, 0] > 0.5
    print(f"\npeta merah K2: {int(red.sum())} texel ({100*red.sum()/(W*H):.3f}%)")
    print("== silang merah vs zona ==")
    for k, m in Z.items():
        print(f"  merah di {k:10s}: {int((red & m).sum()):8d}")
    luar = red & ~(Z["wajah"] | Z["dada"] | Z["lengan"] | Z["ubun-ubun"])
    print(f"  merah di LUAR zona konsep: {int(luar.sum())}")

    # metalik dari ORM (B)
    op = ROOT / "Hermes" / "Art" / "tuyul" / "Textures" / "T_Tuyul_ORM.png"
    orm = None
    if op.exists():
        oimg, _ = load_img(op)
        orm = oimg
        met = oimg[:, :, 2]
        print("\n== metalik (ORM.B) histogram ==")
        for th in (0.1, 0.3, 0.5, 0.7, 0.9):
            print(f"  >{th}: {int((met > th).sum())} texel ({100*(met>th).sum()/(W*H):.3f}%)")
        mm = met > 0.5
        print("== metalik>0,5 vs zona ==")
        for k, m in Z.items():
            print(f"  metalik di {k:10s}: {int((mm & m).sum()):8d}")
        print(f"  metalik di luar semua zona: {int((mm & ~valid).sum())} (tak terpetakan)")

    # gambar peta zona + kedalaman
    zone_col = np.zeros((H, W, 4), dtype=np.float32)
    zone_col[:, :, 3] = 1.0
    warna = {
        "kepala": (0.15, 0.15, 0.15), "wajah": (0.9, 0.2, 0.2), "ubun-ubun": (1.0, 1.0, 0.1),
        "dada": (0.2, 0.9, 0.2), "lengan": (0.2, 0.5, 1.0), "pinggul": (1.0, 0.5, 0.0), "kaki": (0.6, 0.2, 0.9),
    }
    for k, m in Z.items():
        zone_col[m, :3] = warna[k]
    save_rgb("zone", zone_col, outdir / "uv_zone.png")
    zz = np.nan_to_num(z, nan=0.0)
    zc = np.zeros((H, W, 4), dtype=np.float32)
    zc[:, :, 0] = zc[:, :, 1] = zc[:, :, 2] = zz
    zc[:, :, 3] = valid.astype(np.float32)
    save_rgb("posz", zc, outdir / "uv_pos_z.png")
    rm = np.zeros((H, W, 4), dtype=np.float32)
    rm[:, :, 0] = rm[:, :, 1] = rm[:, :, 2] = red.astype(np.float32)
    rm[:, :, 3] = 1.0
    save_rgb("red", rm, outdir / "uv_red_mask.png")
    np.save(outdir / "uv_pos.npy", pos)


main()
