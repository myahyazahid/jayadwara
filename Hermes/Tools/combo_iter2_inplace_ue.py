"""Ratakan geseran tulang `root` di animasi hasil retarget (combo iterasi 2).

Masalah (umpan balik developer): setelah memukul, karakter bergeser lalu balik ke belakang;
saat combo lompat, karakter terbang tinggi lalu menyentak mundur. Penyebabnya bukan root motion
sequence (sudah mati) melainkan kunci TRANSLASI pada tulang `root` di ruang lokal: klip Mixamo
membawa langkah maju (light_01 Y 71,9 cm) / lompat (air Y 203,8 cm) yang, karena kapsul diam,
dibaca sebagai geseran lalu balik.

Jalan yang berhasil: `unreal.AnimSequencerController.set_bone_track_keys` (UE 5.6).
  ctrl = unreal.new_object(unreal.AnimSequencerController, seq)
  ctrl.set_model(seq.data_model_interface)
  ctrl.set_bone_track_keys("root", pos, rot, scale)   # ganti seluruh track root
Catatan: `AnimDataController.set_model` (class lain) MENGHANCURKAN editor — jangan dipakai.
Membaca kunci lama lewat `internal_track_data` selalu kosong, jadi kunci dibangun ulang dengan
menyampel pose (AnimPoseExtensions.get_anim_pose_at_time) per frame, rotasi & skala ikut disalin
supaya tidak ada yang hilang.

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_inplace_ue.py
Log: Hermes/Art/combo-iter2/Log/inplace_ue.json
"""
import json
import os

import unreal

MX = "/Game/Hermes/ComboIter2/Mixamo"
LOG = unreal.Paths.convert_relative_path_to_full(
    unreal.Paths.project_dir() + "Hermes/Art/combo-iter2/Log/inplace_ue.json")
BONE = "root"

# peran -> sumbu yang diratakan (X, Y, Z) pada translasi root.
# Y = maju/mundur (yang dikeluhkan), X = samping, Z = tinggi (dibiarkan: busur lompatan asli).
RATAKAN = {
    "light_01": (False, True, False),
    "light_02": (False, True, False),
    "light_03": (False, True, False),
    "light_04": (True, True, False),
    "lunge": (False, True, False),
    "back": (False, True, False),
    "finisher_01": (False, True, False),
    "finisher_02": (False, True, False),
    "finisher_03": (False, True, False),
    "air": (True, True, True),      # Z ikut diratakan: klipnya menambah lompatan 64 cm -> "terlalu tinggi"
    "air_slam": (True, True, False),
}

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
hasil = []
HANYA = {"light_01", "light_02"}   # isi nama peran untuk menjalankan sebagian saja


def log(msg):
    unreal.log(f"[inplace_ue] {msg}")


def ukur(seq, sumbu_bone=BONE):
    """Rentang translasi lokal root + rentang WORLD pelvis/kepala (untuk verifikasi)."""
    o = unreal.AnimPoseEvaluationOptions()
    L = AL.get_sequence_length(seq)
    lx, ly, lz, py, pz, hz = [], [], [], [], [], []
    for i in range(0, 21):
        t = min(L * i / 20.0, L)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        v = unreal.AnimPoseExtensions.get_bone_pose(p, sumbu_bone, unreal.AnimPoseSpaces.LOCAL).translation
        pv = unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).translation
        hv = unreal.AnimPoseExtensions.get_bone_pose(p, "head", unreal.AnimPoseSpaces.WORLD).translation
        lx.append(v.x); ly.append(v.y); lz.append(v.z)
        py.append(pv.y); pz.append(pv.z); hz.append(hv.z)
    return {
        "root_x": [round(min(lx), 1), round(max(lx), 1)],
        "root_y": [round(min(ly), 1), round(max(ly), 1)],
        "root_z": [round(min(lz), 1), round(max(lz), 1)],
        "pelvis_y": [round(min(py), 1), round(max(py), 1)],
        "pelvis_z": [round(min(pz), 1), round(max(pz), 1)],
        "kepala_z": [round(min(hz), 1), round(max(hz), 1)],
    }


def ratakan(seq, sumbu):
    model = seq.get_editor_property("data_model_interface")
    n = model.get_number_of_frames()
    L = AL.get_sequence_length(seq)
    o = unreal.AnimPoseEvaluationOptions()
    ctrl = unreal.new_object(unreal.AnimSequencerController, seq)
    ctrl.set_model(model)

    pos, rot, scl = [], [], []
    for i in range(n):
        t = min(L * i / float(n - 1), L)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        tr = unreal.AnimPoseExtensions.get_bone_pose(p, BONE, unreal.AnimPoseSpaces.LOCAL)
        pos.append(tr.translation)
        rot.append(tr.rotation)
        scl.append(tr.scale3d)

    dasar = pos[0]
    baru = [unreal.Vector(
        dasar.x if sumbu[0] else k.x,
        dasar.y if sumbu[1] else k.y,
        dasar.z if sumbu[2] else k.z,
    ) for k in pos]
    ok = ctrl.set_bone_track_keys(BONE, baru, rot, scl)
    EAL.save_loaded_asset(seq, only_if_is_dirty=False)
    return ok, n


def main():
    for peran, sumbu in RATAKAN.items():
        if HANYA and peran not in HANYA:
            continue
        path = f"{MX}/A_Aksa_Mx_{peran}"
        seq = unreal.load_asset(path)   # load_asset EAL bergantung registry yang bisa belum siap
        if not seq:
            log(f"LEWAT {peran}: aset tidak ada")
            continue
        sebelum = ukur(seq)
        ok, n = ratakan(seq, sumbu)
        sesudah = ukur(seq)
        baris = {
            "peran": peran,
            "sumbu_diratakan": "".join(a for a, v in zip("XYZ", sumbu) if v) or "-",
            "kunci": n,
            "ok": bool(ok),
            "sebelum": sebelum,
            "sesudah": sesudah,
        }
        hasil.append(baris)
        log(f"{peran:12s} [{baris['sumbu_diratakan']}] root Y {sebelum['root_y']} -> {sesudah['root_y']} "
            f"| pelvis Y {sebelum['pelvis_y']} -> {sesudah['pelvis_y']} "
            f"| kepala Z {sesudah['kepala_z']} | ok={ok}")

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(hasil, f, indent=1)
    log(f"selesai: {len(hasil)} animasi -> {LOG}")


main()
