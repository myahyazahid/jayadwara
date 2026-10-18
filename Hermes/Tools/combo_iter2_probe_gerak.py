"""Peta gerak satu FBX Mixamo (combo iterasi 2): tinggi & posisi tulang per 0,1 s.

Dipakai sebelum memangkas klip: supaya rentang yang diambil berangka, bukan tebakan.
Hanya membaca FBX, tidak menulis apa pun ke aset.

Jalan:
  blender --background --factory-startup --python Hermes/Tools/combo_iter2_probe_gerak.py -- <file.fbx> <keluar.json>

Keluaran JSON: fps, frame_awal/akhir, panjang detik, dan sampel per frame:
  t, head_z, pelvis_z, pelvis_y, root_y, hand_r_z, hand_l_z, foot_r_z, foot_l_z
Semua satuan cm (skala impor FBX Mixamo sudah cm).
"""
import json
import os
import sys

import bpy

TULANG = {
    "head": "Head",
    "pelvis": "Hips",
    "root": "Hips",
    "hand_r": "RightHand",
    "hand_l": "LeftHand",
    "foot_r": "RightFoot",
    "foot_l": "LeftFoot",
}


def arg():
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    return []


def main():
    a = arg()
    if len(a) < 2:
        print("[probe] butuh 2 argumen: <file.fbx> <keluar.json>")
        return
    fbx, out = a[0], a[1]
    t_mulai = float(a[2]) if len(a) > 2 else None
    t_akhir = float(a[3]) if len(a) > 3 else None

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx)

    arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
    fps = bpy.context.scene.render.fps
    act = bpy.data.actions[0]
    f0, f1 = (int(round(x)) for x in act.frame_range)

    # prefix bisa 'mixamorig:' atau 'mixamorig1:'
    pre = ""
    for b in arm.data.bones:
        if b.name.endswith("Hips"):
            pre = b.name[: -len("Hips")]
            break

    nama = {k: pre + v for k, v in TULANG.items()}
    hilang = [k for k, v in nama.items() if v not in arm.pose.bones]
    if hilang:
        print(f"[probe] PERINGATAN tulang tidak ada: {hilang}")

    scn = bpy.context.scene
    sampel = []
    langkah = 3  # tiap 3 frame = 0,1 s
    awal, akhir = f0, f1
    if t_mulai is not None:
        langkah = 1
        awal = max(f0, int(round(f0 + t_mulai * fps)))
        akhir = min(f1, int(round(f0 + (t_akhir if t_akhir is not None else (f1 - f0) / float(fps)) * fps)))
    for f in range(awal, akhir + 1, langkah):
        scn.frame_set(f)
        bpy.context.view_layer.update()
        baris = {"frame": f, "t": round((f - f0) / float(fps), 3)}
        for k, v in nama.items():
            if v not in arm.pose.bones:
                continue
            w = arm.matrix_world @ arm.pose.bones[v].head
            if k in ("head", "pelvis", "hand_r", "hand_l", "foot_r", "foot_l"):
                baris[k + "_z"] = round(w.z * 100.0, 1)
            if k in ("pelvis", "root"):
                baris[k + "_y"] = round(w.y * 100.0, 1)
        sampel.append(baris)

    data = {
        "file": os.path.basename(fbx),
        "fps": fps,
        "frame_awal": f0,
        "frame_akhir": f1,
        "panjang_detik": round((f1 - f0) / float(fps), 3),
        "prefix": pre,
        "sampel": sampel,
    }

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)

    # tabel ringkas ke stdout
    print(f"[probe] {data['file']}  {data['panjang_detik']}s  {len(sampel)} sampel  fps {fps}")
    print("   t     head_z  pelv_z  pelv_y  handR_z handL_z footR_z footL_z")
    for s in sampel:
        print("  %5.2f  %6.1f  %6.1f  %6.1f  %6.1f  %6.1f  %6.1f  %6.1f" % (
            s["t"], s.get("head_z", 0), s.get("pelvis_z", 0), s.get("pelvis_y", 0),
            s.get("hand_r_z", 0), s.get("hand_l_z", 0), s.get("foot_r_z", 0), s.get("foot_l_z", 0)))
    print(f"[probe] json -> {out}")


main()
