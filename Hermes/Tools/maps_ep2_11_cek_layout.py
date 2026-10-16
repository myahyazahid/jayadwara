"""MK1 - Cek data layout Ep02 (maps_ep2).

Baca Art/Level/ep02_layout_v02.json + impor Art/Level/ep02_medan_v02.py (untuk elev()).
Cetak:
  1) tabel 145 objek: id | jenis | pos (x,y) | alas (m) | selisih tanah di tapak (m)
  2) ringkasan 8 kelompok: jumlah item, alas min/maks
  3) cek angka kriteria MK1 (Hermes/maps_ep2_hermes.md).

Pakai: python -I Hermes/Tools/maps_ep2_11_cek_layout.py
Tidak menulis apa pun; hanya membaca file proyek (read-only).
"""
import collections
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # akar worktree
LEVEL = os.path.join(ROOT, "Art", "Level")
sys.path.insert(0, LEVEL)
import ep02_medan_v02 as M  # noqa: E402

JSON_PATH = os.path.join(LEVEL, "ep02_layout_v02.json")


def alas_min_max(pos, P, L, yaw=0.0):
    """Min/maks elev di tapak 5x5 setelah rotasi (sama dengan alas() generator)."""
    x, y = pos
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    zs = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            lx, ly = P / 2 * i / 2, L / 2 * j / 2
            zs.append(M.elev(x + lx * c - ly * s, y + lx * s + ly * c))
    return min(zs), max(zs)


def alas_dinding(o):
    """Alas dinding = elev terendah di sepanjang ruas dari->ke (sampel ~1 m)."""
    (x0, y0), (x1, y1) = o["dari"], o["ke"]
    n = max(2, int(math.hypot(x1 - x0, y1 - y0)) + 1)
    zs = [M.elev(x0 + (x1 - x0) * t / (n - 1), y0 + (y1 - y0) * t / (n - 1)) for t in range(n)]
    return min(zs), max(zs)


def objek_alas(o):
    """Kembalikan (alas, selisih_tanah, pos_tampil). alas = dasar bangunan (m)."""
    zdr = o.get("z_dasar_relatif", 0.0)
    if o.get("z") is not None:
        return o["z"] + zdr, None, o.get("pos")          # tinggi absolut
    if o["jenis"] == "dinding":
        lo, hi = alas_dinding(o)
        return lo + zdr, hi - lo, o["dari"]
    if "pos" in o:
        P, L = (list(o.get("ukuran", [4, 4])) + [4, 4])[:2]
        lo, hi = alas_min_max(o["pos"], P, L, o.get("yaw", 0))
        return lo + zdr, hi - lo, o["pos"]
    return None, None, None


def main():
    d = json.load(open(JSON_PATH, encoding="utf-8"))
    O, K = d["objek"], d["kelompok"]
    info = {o["id"]: objek_alas(o) for o in O}

    print("=" * 104)
    print("TABEL OBJEK (%d) - id | jenis | pos (x,y) | alas (m) | selisih tanah di tapak (m)" % len(O))
    print("=" * 104)
    for o in O:
        a, sl, pos = info[o["id"]]
        zs = "  z=%.2f" % o["z"] if o.get("z") is not None else ""
        zdr = "  zdr=%.1f" % o["z_dasar_relatif"] if "z_dasar_relatif" in o else ""
        sls = "%6.2f" % sl if sl is not None else "   -  "
        ps = "(%g,%g)" % (pos[0], pos[1]) if pos else "-"
        av = "%.2f" % a if a is not None else "  ?  "
        print("%-24s %-8s %-16s %8s %8s%s%s" % (o["id"], o["jenis"], ps, av, sls, zs, zdr))

    print()
    print("=" * 104)
    print("RINGKASAN KELOMPOK (%d)" % len(K))
    print("=" * 104)
    total = 0
    for k in K:
        zc = k.get("z")
        amin = amax = None
        for it in k["item"]:
            x, y, P, L = it[0], it[1], it[2], it[3]
            yaw = it[5] if len(it) > 5 else 0
            a = zc if zc is not None else alas_min_max((x, y), P, L, yaw)[0]
            amin = a if amin is None else min(amin, a)
            amax = a if amax is None else max(amax, a)
        total += len(k["item"])
        print("%-22s bentuk=%-6s n=%4d  alas %7.2f .. %7.2f%s" % (
            k["id"], k["bentuk"], len(k["item"]), amin, amax,
            "  (z=%.1f semua item)" % zc if zc is not None else ""))
    print("TOTAL item kelompok: %d" % total)

    print()
    print("=" * 104)
    print("CEK KRITERIA MK1")
    print("=" * 104)
    gagal = []

    def cek(label, got, want, tol=0.0):
        ok = abs(got - want) <= tol
        if not ok:
            gagal.append(label)
        print("%s %-48s = %-10s (harap %s%s)" % (
            "OK " if ok else "GAGAL", label, got, want, " +-%.2f" % tol if tol else ""))

    cek("jumlah objek", len(O), 145)
    cek("total item kelompok", total, 1817)
    pj = collections.Counter(p["jenis"] for p in d["penanda"])
    cek("penanda PlayerStart", pj.get("PlayerStart", 0), 1)
    cek("penanda titik", pj.get("titik", 0), 15)
    cek("penanda area", pj.get("area", 0), 7)
    pen = collections.Counter(o.get("penalti") for o in O)
    cek("tag penalti_tinggi", pen.get("tinggi", 0), 61)
    cek("tag penalti_normal", pen.get("normal", 0), 10)
    cek("tag tanpa_penalti", pen.get("tanpa", 0), 19)
    cek("tag adikara", sum(1 for o in O if o.get("milik") == "Adikara"), 11)
    cek("tag curian", sum(1 for o in O if o.get("curian")), 6)
    for i, want in (("KAMPUNG_PosRT", 7.85), ("KAMPUNG_Musala", 7.22), ("GUDANG_Gudang1", 6.00),
                    ("BANTARAN_Gubuk1", 3.50), ("SELATAN_SUTET1", 3.00)):
        cek("alas " + i, info[i][0], want, 0.02)

    naik = [(o["pos"][0], o["pos"][1], info[o["id"]][0] + 3.5) for o in O if o["id"].startswith("ATAP_Naik")]
    cek("ATAP_Naik n", len(naik), 27)
    cek("puncak ATAP_Naik terendah", round(min(t[2] for t in naik), 2), 9.97, 0.02)
    cek("puncak ATAP_Naik tertinggi", round(max(t[2] for t in naik), 2), 11.45, 0.02)

    print("  papan vs puncak ATAP_Naik terdekat (papan top = z + 0,15):")
    worst = 0.0
    for o in O:
        if o["id"].startswith("ATAP_Papan"):
            px, py = o["pos"]
            top = o["z"] + 0.15
            nx, ny, pk = min(naik, key=lambda t: math.hypot(px - t[0], py - t[1]))
            diff = abs(top - pk)
            worst = max(worst, diff)
            print("      %s top=%.2f  naik(%.0f,%.0f)=%.2f  jarak %.1f m  diff=%.2f" % (
                o["id"], top, nx, ny, pk, math.hypot(px - nx, py - ny), diff))
    cek("papan: selisih maks ke puncak naik", round(worst, 2), 0.0, 0.60)

    print()
    print("TEMUAN selisih tanah di tapak > 2 m (jenis != bidang):")
    ada = False
    for o in O:
        a, sl, _ = info[o["id"]]
        if sl is not None and sl > 2.0 and o["jenis"] != "bidang":
            ada = True
            print("      %-24s %.2f m" % (o["id"], sl))
    if not ada:
        print("      (tidak ada)")

    print()
    print("SEMUA LULUS" if not gagal else "ADA %d GAGAL: %s" % (len(gagal), ", ".join(gagal)))
    return len(gagal)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
