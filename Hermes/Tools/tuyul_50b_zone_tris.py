"""K5.1b - Probe tris per zona TY_Source (mencari kenapa LOD3 mentok 10.628 tris).

  blender --background Hermes/Art/tuyul/Blender/tuyul_v08_lod.blend --python Hermes/Tools/tuyul_50b_zone_tris.py

Mencetak: tris per zona anatomis + tris di beberapa kandidat zona lindung, supaya
lantai decimate LOD3 bisa dijelaskan dengan angka (bukan tebakan).
"""
import bpy

me = bpy.data.objects["TY_Source"].data


def zc(c):
    if c.z > 0.925 and abs(c.x) < 0.13 and abs(c.y) < 0.13:
        return "ubun_ubun"
    if c.z > 0.80 and c.y < -0.04:
        return "wajah"
    if c.z > 0.80:
        return "tempurung_belakang"
    if abs(c.x) > 0.20 and c.z < 0.32:
        return "tangan"
    if abs(c.x) > 0.18:
        return "lengan"
    if c.z < 0.20:
        return "kaki"
    return "badan_cawat"


zone, kandidat = {}, {"A: kepala z>0.78 + tangan": 0, "B: wajah z>0.80&y<-0.04 + tangan": 0,
                      "C: wajah + tangan + ubun": 0, "D: hanya wajah": 0}
for p in me.polygons:
    c = p.center
    t = len(p.vertices) - 2
    k = zc(c)
    zone[k] = zone.get(k, 0) + t
    kepala = c.z > 0.78
    wajah = c.z > 0.80 and c.y < -0.04
    ubun = c.z > 0.925 and abs(c.x) < 0.13 and abs(c.y) < 0.13
    tangan = abs(c.x) > 0.20 and c.z < 0.32
    if kepala or tangan:
        kandidat["A: kepala z>0.78 + tangan"] += t
    if wajah or tangan:
        kandidat["B: wajah z>0.80&y<-0.04 + tangan"] += t
    if wajah or ubun or tangan:
        kandidat["C: wajah + tangan + ubun"] += t
    if wajah:
        kandidat["D: hanya wajah"] += t

tot = sum(zone.values())
print(f"TOTAL {tot} tris, {len(me.vertices)} vertex")
for k, v in sorted(zone.items(), key=lambda kv: -kv[1]):
    print(f"  zona {k:<20} {v:6d} tris ({100.0 * v / tot:5.1f}%)")
print("lantai decimate (perkiraan = tris zona lindung):")
for k, v in kandidat.items():
    print(f"  {k:<42} {v:6d} tris ({100.0 * v / tot:5.1f}%)")
