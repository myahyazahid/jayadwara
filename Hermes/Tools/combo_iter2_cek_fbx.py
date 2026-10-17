"""Cek FBX Mixamo hasil download developer (M3, Hermes/combo_iter2_hermes.md §4).

Jalan:
  blender --background --factory-startup --python Hermes/Tools/combo_iter2_cek_fbx.py -- <folder_result> <folder_log>

Untuk tiap *.fbx: impor ke scene kosong, catat ke <folder_log>/cek_fbx.json:
  nama file ada di tabel M1, 1 armature mixamorig*, ada Hips/Spine/LeftHand/RightFoot,
  ybot punya mesh berskin + tinggi 160-200 cm, animasi punya action >= 10 frame + fps,
  geser pinggul awal->akhir (In Place < 30 cm; lebih = catatan, bukan gagal),
  semua file harus pakai skeleton yang sama dengan ybot (nama tulang identik).

Skrip hanya membaca folder result dan menulis JSON di folder log. Tidak memindahkan file;
pemindahan dilakukan terpisah setelah hasil dibaca.
"""
import bpy
import json
import math
import os
import sys

# Tabel M1 (mixamo/asset/DAFTAR_ANIMASI.md) + finisher_03 (PR #41, docs/07 17 Okt 2026).
PERAN = {
    "ybot.fbx": {"jurus": "karakter sumber retarget", "kena": None, "prioritas": 1},
    "light_04.fbx": {"jurus": "tendangan putar belakang", "kena": "kaki", "prioritas": 1},
    "finisher_01.fbx": {"jurus": "tendangan belakang", "kena": "kaki", "prioritas": 1},
    "finisher_02.fbx": {"jurus": "tendangan ganda melompat", "kena": "kaki", "prioritas": 1},
    "finisher_03.fbx": {"jurus": "finisher 3 (ringan x3 -> berat)", "kena": None, "prioritas": 1},
    "air.fbx": {"jurus": "tendangan terbang memutar", "kena": "kaki", "prioritas": 1},
    "dodge_back.fbx": {"jurus": "salto belakang", "kena": None, "prioritas": 1},
    "dodge_left.fbx": {"jurus": "guling kiri", "kena": None, "prioritas": 1},
    "dodge_right.fbx": {"jurus": "guling kanan", "kena": None, "prioritas": 1},
    "dodge_forward.fbx": {"jurus": "langkah cepat menunduk", "kena": None, "prioritas": 1},
    "light_01.fbx": {"jurus": "jab", "kena": "tangan", "prioritas": 2},
    "light_02.fbx": {"jurus": "cross", "kena": "tangan", "prioritas": 2},
    "light_03.fbx": {"jurus": "hook", "kena": "tangan", "prioritas": 2},
    "lunge.fbx": {"jurus": "terjang", "kena": "tangan", "prioritas": 2},
    "back.fbx": {"jurus": "pukul mundur", "kena": "tangan", "prioritas": 2},
    "heavy.fbx": {"jurus": "pukulan putar", "kena": "tangan", "prioritas": 2},
    "air_slam.fbx": {"jurus": "hantaman ke bawah", "kena": None, "prioritas": 2},
    "parry_01.fbx": {"jurus": "tepis luar", "kena": None, "prioritas": 2},
    "parry_02.fbx": {"jurus": "tepis dalam", "kena": None, "prioritas": 2},
}

WAJIB_TULANG = ("Hips", "Spine", "LeftHand", "RightFoot")


def argv_after_dashdash():
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    return []


def bersihkan():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def prefix_dari(bone_names):
    """'mixamorig:Hips' -> 'mixamorig:' ; 'mixamorig1:Hips' -> 'mixamorig1:' ; tanpa ':' -> ''."""
    for n in bone_names:
        if n.endswith("Hips"):
            head = n[: -len("Hips")]
            if head.startswith("mixamorig"):
                return head
    return None


def tinggi_mesh_cm(objek_mesh, depsgraph):
    zs = []
    for ob in objek_mesh:
        ev = ob.evaluated_get(depsgraph)
        me = ev.to_mesh()
        mw = ob.matrix_world
        for v in me.vertices:
            zs.append((mw @ v.co).z)
        ev.to_mesh_clear()
    if not zs:
        return None
    return (max(zs) - min(zs)) * 100.0


def punya_skin(objek_mesh):
    for ob in objek_mesh:
        if ob.vertex_groups and any(m.type == "ARMATURE" for m in ob.modifiers):
            return True
    return False


def posisi_pinggul(arm, nama_tulang, frame):
    bpy.context.scene.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm.evaluated_get(dg)
    pb = ev.pose.bones.get(nama_tulang)
    if pb is None:
        return None
    return arm.matrix_world @ pb.head


def cek_satu(path, nama, info):
    bersihkan()
    bpy.ops.import_scene.fbx(filepath=path)
    hasil = {
        "file": nama,
        "jurus": info["jurus"],
        "prioritas": info["prioritas"],
        "kena": info["kena"],
        "gagal": [],
        "catatan": [],
    }

    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    hasil["armature_count"] = len(arms)
    hasil["mesh_count"] = len(meshes)
    if len(arms) != 1:
        hasil["gagal"].append(f"armature harus tepat 1, ada {len(arms)}")
        hasil["lulus"] = False
        return hasil

    arm = arms[0]
    bones = [b.name for b in arm.data.bones]
    hasil["tulang_jumlah"] = len(bones)
    hasil["tulang_contoh"] = bones[:6]

    prefix = prefix_dari(bones)
    hasil["prefix"] = prefix
    if prefix is None:
        hasil["gagal"].append("tidak ada tulang diawali 'mixamorig' / tidak ada Hips")
    else:
        bukan = [b for b in bones if not b.startswith("mixamorig")]
        hasil["tulang_tanpa_prefix"] = bukan[:10]
        if bukan:
            hasil["gagal"].append(f"{len(bukan)} tulang tidak diawali 'mixamorig'")
        hilang = [t for t in WAJIB_TULANG if (prefix + t) not in bones]
        hasil["tulang_hilang"] = hilang
        if hilang:
            hasil["gagal"].append("tulang wajib hilang: " + ", ".join(hilang))

    hasil["tulang"] = sorted(bones)

    # fps scene (nilai asli dari file)
    hasil["fps"] = bpy.context.scene.render.fps

    # action
    actions = [a for a in bpy.data.actions]
    hasil["action_jumlah"] = len(actions)
    if actions:
        act = actions[0]
        f0, f1 = act.frame_range
        hasil["action_nama"] = act.name
        hasil["frame_awal"] = round(float(f0), 3)
        hasil["frame_akhir"] = round(float(f1), 3)
        hasil["frame_jumlah"] = int(round(float(f1) - float(f0))) + 1
        hasil["detik"] = round((float(f1) - float(f0)) / max(hasil["fps"], 1), 3)
    else:
        hasil["action_nama"] = None
        hasil["frame_jumlah"] = 0

    if nama == "ybot.fbx":
        hasil["punya_skin"] = punya_skin(meshes)
        if not hasil["punya_skin"]:
            hasil["gagal"].append("ybot tidak punya mesh berskin (impor 'With Skin'?)")
        dg = bpy.context.evaluated_depsgraph_get()
        tinggi = tinggi_mesh_cm(meshes, dg)
        hasil["tinggi_cm"] = round(tinggi, 2) if tinggi else None
        if tinggi is None:
            hasil["gagal"].append("tidak ada mesh untuk diukur")
        elif not (160.0 <= tinggi <= 200.0):
            hasil["gagal"].append(f"tinggi {tinggi:.1f} cm di luar 160-200 cm")
    else:
        if not actions:
            hasil["gagal"].append("tidak ada action (animasi kosong)")
        elif hasil["frame_jumlah"] < 10:
            hasil["gagal"].append(f"animasi hanya {hasil['frame_jumlah']} frame (< 10)")
        if hasil["fps"] != 30:
            hasil["catatan"].append(f"fps scene {hasil['fps']} (daftar minta 30)")

    # In Place: geser pinggul horizontal awal -> akhir
    if prefix and actions:
        nama_hips = prefix + "Hips"
        p0 = posisi_pinggul(arm, nama_hips, int(round(hasil["frame_awal"])))
        p1 = posisi_pinggul(arm, nama_hips, int(round(hasil["frame_akhir"])))
        if p0 and p1:
            dx = (p1.x - p0.x) * 100.0
            dy = (p1.y - p0.y) * 100.0
            jarak = math.hypot(dx, dy)
            hasil["geser_pinggul_cm"] = round(jarak, 2)
            hasil["geser_xy_cm"] = [round(dx, 2), round(dy, 2)]
            hasil["in_place"] = jarak < 30.0
            if not hasil["in_place"]:
                hasil["catatan"].append(
                    f"tidak In Place: pinggul geser {jarak:.1f} cm (dx {dx:.1f}, dy {dy:.1f})"
                )

    hasil["lulus"] = not hasil["gagal"]
    return hasil


def main():
    args = argv_after_dashdash()
    if len(args) < 2:
        print("PAKAI: blender -b --factory-startup --python combo_iter2_cek_fbx.py -- <folder_result> <folder_log>")
        sys.exit(2)
    folder_result, folder_log = args[0], args[1]
    os.makedirs(folder_log, exist_ok=True)

    files = sorted(f for f in os.listdir(folder_result) if f.lower().endswith(".fbx"))
    print(f"[cek_fbx] {len(files)} file di {folder_result}")

    hasil_semua = []
    for f in files:
        path = os.path.join(folder_result, f)
        nama = f
        info = PERAN.get(nama)
        if info is None:
            hasil_semua.append({
                "file": nama,
                "gagal": ["nama file tidak ada di tabel M1"],
                "catatan": [],
                "lulus": False,
            })
            print(f"[cek_fbx] {nama}: GAGAL nama tidak dikenal")
            continue
        h = cek_satu(path, nama, info)
        hasil_semua.append(h)
        status = "LULUS" if h["lulus"] else "GAGAL"
        print(
            f"[cek_fbx] {nama}: {status} "
            f"tulang={h.get('tulang_jumlah')} frame={h.get('frame_jumlah')} "
            f"fps={h.get('fps')} geser={h.get('geser_pinggul_cm')} cm "
            f"gagal={h['gagal']} catatan={h['catatan']}"
        )

    # skeleton harus sama dengan ybot
    ybot = next((h for h in hasil_semua if h["file"] == "ybot.fbx" and h.get("tulang")), None)
    if ybot:
        acuan = set(ybot["tulang"])
        for h in hasil_semua:
            if h["file"] == "ybot.fbx" or not h.get("tulang"):
                continue
            beda = set(h["tulang"]) ^ acuan
            h["tulang_beda_vs_ybot"] = len(beda)
            if beda:
                h["gagal"].append(
                    f"{len(beda)} nama tulang beda dari ybot (contoh: {sorted(beda)[:3]})"
                )
                h["lulus"] = False
                print(f"[cek_fbx] {h['file']}: GAGAL skeleton beda dari ybot ({len(beda)} tulang)")
    else:
        print("[cek_fbx] PERINGATAN: ybot.fbx tidak ada/lulus, perbandingan skeleton dilewati")

    # peran yang belum ada filenya
    ada = {h["file"] for h in hasil_semua}
    belum = [n for n in PERAN if n not in ada]

    out = {
        "folder_result": os.path.abspath(folder_result),
        "jumlah_file": len(files),
        "lulus": sum(1 for h in hasil_semua if h["lulus"]),
        "gagal": sum(1 for h in hasil_semua if not h["lulus"]),
        "file": hasil_semua,
        "peran_belum_ada": belum,
    }
    out_path = os.path.join(folder_log, "cek_fbx.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    print(f"[cek_fbx] lulus {out['lulus']} / gagal {out['gagal']} -> {out_path}")
    if belum:
        print("[cek_fbx] belum ada file untuk: " + ", ".join(belum))
    for h in hasil_semua:
        if not h["lulus"]:
            print(f"[cek_fbx] GAGAL {h['file']}: " + "; ".join(h["gagal"]))


main()
