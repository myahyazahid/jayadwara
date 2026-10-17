"""Buat versi IN-PLACE dari 3 FBX Mixamo yang pinggulnya bergeser (combo iterasi 2).

Masalah (umpan balik developer M6): "Space + LMB, animasinya terbang tinggi banget,
nendang maju lalu tiba-tiba mundur di udara".

Sebab: klip Mixamo itu membawa geseran pinggul (root motion) yang tidak diinginkan:
  air       210,7 cm (Y 0,8 -> 203,8 | Z 74,3 -> 138,8)
  air_slam  383,4 cm (Y 0,4 -> 369,5 | Z 35,8 -> 188,3)
  light_04   51,3 cm (X -45,5 -> -0,1 | Z 84,5 -> 102,9)
Di UE root motion sequence sudah dimatikan, jadi geseran itu tetap dipakai sebagai animasi
tulang: mesh bergerak, kapsul tidak -> karakter tampak melayang lalu mundur.

JANGAN DIPAKAI — PERCOBAAN INI GAGAL (lihat laporan temuan 8).
FBX hasil ekspor Blender masuk UE dengan basis tulang berbeda; karena skeleton SK_Mixamo_YBot
dipakai bersama, animasi jadi terotasi 90 derajat dan hasil retarget rebah (kepala 33,8 cm,
seharusnya 136 cm). Round-trip di Blender sendiri identik, jadi koreksi geserannya benar —
yang salah jalur ekspor/impor. Perbaikan yang benar: unduh ulang klip "In Place" dari Mixamo.

Skrip ini TIDAK menyentuh file asli. Hasil ditulis ke Mixamo/inplace/<peran>.fbx
(namun tidak dipakai lagi; peta INPLACE di combo_iter2_import_mixamo.py sudah dikosongkan).

Jalan: "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --python Hermes/Tools/combo_iter2_inplace_fbx.py
"""

import os

import bpy
import mathutils

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../Hermes
SRC = os.path.join(HERE, "Art", "combo-iter2", "Mixamo")
OUT = os.path.join(SRC, "inplace")
HIPS = "mixamorig:Hips"

# peran -> sumbu yang diratakan (True = dibuat konstan di nilai frame pertama)
RATAKAN = {
    "air": (True, True, True),        # terbang: semua sumbu, tinggi datang dari lompatan pemain
    "air_slam": (True, True, True),   # menukik: semua sumbu, gerak turun datang dari LaunchCharacter (AirSlamSpeed)
    "light_04": (True, True, False),  # tendangan putar di tanah: X/Y rata, Z (tekuk) dipertahankan
}


def fcurves_of(ob):
    ad = ob.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "layers") and len(act.layers):      # Blender 5.x: action berlapis
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for cb in getattr(strip, "channelbags", []):
                    out.extend(cb.fcurves)
        return out
    return list(getattr(act, "fcurves", []))


def rentang(arm):
    """Rentang frame dari action (scene.frame_start/end tidak selalu ikut action)."""
    fr = [fc.range() for fc in fcurves_of(arm)]
    awal = int(min(r[0] for r in fr))
    akhir = int(max(r[1] for r in fr))
    return awal, akhir


def ukur(arm, hips):
    """Kembalikan daftar (frame, posisi dunia pinggul, lokasi lokal pinggul)."""
    scene = bpy.context.scene
    f0, f1 = rentang(arm)
    hasil = []
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        hasil.append((f, (arm.matrix_world @ hips.matrix).translation.copy(), hips.location.copy()))
    return hasil


def ratakan(role):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    path = os.path.join(SRC, f"{role}.fbx")
    bpy.ops.import_scene.fbx(filepath=path)
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    hips = arm.pose.bones[HIPS]
    scene = bpy.context.scene
    rata = RATAKAN[role]

    awal = ukur(arm, hips)
    p0 = awal[0][1]
    xs = [p.x for _, p, _ in awal]
    ys = [p.y for _, p, _ in awal]
    zs = [p.z for _, p, _ in awal]
    print(f"[inplace] {role}: SEBELUM dunia X {min(xs):7.1f}..{max(xs):7.1f} | "
          f"Y {min(ys):7.1f}..{max(ys):7.1f} | Z {min(zs):7.1f}..{max(zs):7.1f}")

    # dunia -> ruang-tulang: M = skala objek armature (0,01) x matriks istirahat tulang.
    # Tanpa matriks objek, koreksinya mengecil 100x (sempat gagal senyap).
    M_inv = (arm.matrix_world.to_3x3() @ hips.bone.matrix_local.to_3x3()).inverted()

    for f, pos, loc in awal:
        delta_world = mathutils.Vector((
            pos.x - p0.x if rata[0] else 0.0,
            pos.y - p0.y if rata[1] else 0.0,
            pos.z - p0.z if rata[2] else 0.0,
        ))
        hips.location = loc - (M_inv @ delta_world)
        hips.keyframe_insert("location", frame=f)

    # simpan hanya kurva lokasi yang baru (rotasi/scale tidak disentuh)
    scene.frame_set(int(scene.frame_start))

    os.makedirs(OUT, exist_ok=True)
    keluar = os.path.join(OUT, f"{role}.fbx")
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.fbx(
        filepath=keluar,
        use_selection=True,
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True,
        add_leaf_bones=False,
        axis_forward="-Z",
        axis_up="Y",
    )
    print(f"[inplace] {role}: ditulis {keluar}")

    # verifikasi: baca ulang file hasil
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=keluar)
    arm2 = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    hips2 = arm2.pose.bones[HIPS]
    akhir = ukur(arm2, hips2)
    xs2 = [p.x for _, p, _ in akhir]
    ys2 = [p.y for _, p, _ in akhir]
    zs2 = [p.z for _, p, _ in akhir]
    print(f"[inplace] {role}: SESUDAH dunia X {min(xs2):7.1f}..{max(xs2):7.1f} | "
          f"Y {min(ys2):7.1f}..{max(ys2):7.1f} | Z {min(zs2):7.1f}..{max(zs2):7.1f}")


for peran in RATAKAN:
    ratakan(peran)
print("[inplace] selesai")
