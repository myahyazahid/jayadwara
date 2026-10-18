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
HANYA = {"air_slam"}   # isi nama peran untuk menjalankan sebagian saja

# peran -> kunci yaw tulang root (putaran badan ke samping).
# Dulu air_slam dikunci di sini karena "gerak ke samping kiri". Ternyata geseran itu
# berasal dari translasi pelvis (NOL), sedangkan mengunci yaw membuat badan BERHENTI
# menyamping sepanjang montage -> umpan balik berikutnya: "tendangannya memutar selesai
# di samping". Jadi kunci yaw tidak dipakai lagi untuk air_slam.
KUNCI_YAW = {}

# peran -> total putaran badan yang diinginkan (derajat), mulai menghadap depan.
# air_slam: kurva asli root 106,7 -> 293,3 derajat (monoton, +186,6). Kalau dibiarkan,
# badan mulai membelakangi pemain lalu berhenti di 0 (menghadap depan) tetapi masuknya
# menyentak 186 derajat dalam 0,15 s blend. Kalau dikunci, badan menyamping terus.
# Jalan tengah: skalakan kurvanya jadi tepat 360 derajat -> mulai depan, satu putaran
# penuh, berakhir depan. Bentuk (percepatan/perlambatan) putaran tetap seperti aslinya.
PUTAR = {}

# peran -> paksa posisi horizontal root ke 0 (bukan ke frame pertama).
# air_slam: hasil retarget menaruh pelvis di X 125,7 cm padahal klip lain ~0 cm
# (light_01 0,2 / air -0,9). Offset 1,25 m ini membuat badan terseret ke samping
# saat blend masuk dari pose lompat -> "gerakan seperti ke samping kiri".
NOL = {"air_slam": True}


def log(msg):
    unreal.log(f"[inplace_ue] {msg}")


def ukur(seq, sumbu_bone=BONE):
    """Rentang translasi lokal root + rentang WORLD pelvis/kepala + yaw root (untuk verifikasi)."""
    o = unreal.AnimPoseEvaluationOptions()
    L = AL.get_sequence_length(seq)
    lx, ly, lz, py, pz, hz, hx, yaw = [], [], [], [], [], [], [], []
    for i in range(0, 21):
        t = min(L * i / 20.0, L)
        p = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, o)
        v = unreal.AnimPoseExtensions.get_bone_pose(p, sumbu_bone, unreal.AnimPoseSpaces.LOCAL).translation
        r = unreal.AnimPoseExtensions.get_bone_pose(p, sumbu_bone, unreal.AnimPoseSpaces.LOCAL).rotation
        pv = unreal.AnimPoseExtensions.get_bone_pose(p, "pelvis", unreal.AnimPoseSpaces.WORLD).translation
        hv = unreal.AnimPoseExtensions.get_bone_pose(p, "head", unreal.AnimPoseSpaces.WORLD).translation
        lx.append(v.x); ly.append(v.y); lz.append(v.z)
        py.append(pv.y); pz.append(pv.z)
        hz.append(hv.z); hx.append(hv.x)
        yaw.append(r.rotator().yaw)
    return {
        "root_x": [round(min(lx), 1), round(max(lx), 1)],
        "root_y": [round(min(ly), 1), round(max(ly), 1)],
        "root_z": [round(min(lz), 1), round(max(lz), 1)],
        "root_yaw": [round(min(yaw), 1), round(max(yaw), 1)],
        "pelvis_y": [round(min(py), 1), round(max(py), 1)],
        "pelvis_z": [round(min(pz), 1), round(max(pz), 1)],
        "kepala_x": [round(min(hx), 1), round(max(hx), 1)],
        "kepala_z": [round(min(hz), 1), round(max(hz), 1)],
    }


def ratakan(seq, sumbu, kunci_yaw=False, nol=False, putar=None):
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

    dasar = unreal.Vector(0.0, 0.0, pos[0].z) if nol else pos[0]
    baru = [unreal.Vector(
        dasar.x if sumbu[0] else k.x,
        dasar.y if sumbu[1] else k.y,
        dasar.z if sumbu[2] else k.z,
    ) for k in pos]

    if putar:
        # Putaran badan diskalakan: yaw_0 -> yaw_0 + putar, mengikuti bentuk kurva asli.
        # Yaw dibuka dulu (unwrap) karena kurva melewati +-180 derajat di tengah klip.
        mentah = [q.rotator().yaw for q in rot]
        buka = [mentah[0]]
        for y in mentah[1:]:
            buka.append(buka[-1] + ((y - buka[-1] + 180.0) % 360.0 - 180.0))
        rentang = buka[-1] - buka[0]
        baru_rot = []
        for i, q in enumerate(rot):
            r = q.rotator()
            y = buka[0] + (putar * ((buka[i] - buka[0]) / rentang) if rentang else 0.0)
            baru_rot.append(unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=y).quaternion())
        rot = baru_rot
        log(f"putaran badan {rentang:.1f} -> {putar:.1f} derajat")
    elif kunci_yaw:
        # Badan tidak boleh berputar: yaw root dibekukan di frame pertama,
        # pitch & roll dibiarkan supaya badan tetap bisa melipat/menunduk.
        y0 = rot[0].rotator().yaw
        baru_rot = []
        for q in rot:
            r = q.rotator()
            baru_rot.append(unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=y0).quaternion())
        rot = baru_rot

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
        kunci = KUNCI_YAW.get(peran, False)
        nol = NOL.get(peran, False)
        ok, n = ratakan(seq, sumbu, kunci, nol, PUTAR.get(peran))
        sesudah = ukur(seq)
        baris = {
            "peran": peran,
            "sumbu_diratakan": "".join(a for a, v in zip("XYZ", sumbu) if v) or "-",
            "yaw_dikunci": kunci,
            "putaran_penuh": PUTAR.get(peran),
            "horizontal_dinolkan": nol,
            "kunci": n,
            "ok": bool(ok),
            "sebelum": sebelum,
            "sesudah": sesudah,
        }
        hasil.append(baris)
        log(f"{peran:12s} [{baris['sumbu_diratakan']}{' + yaw' if kunci else ''}] "
            f"root Y {sebelum['root_y']} -> {sesudah['root_y']} "
            f"| pelvis Y {sebelum['pelvis_y']} -> {sesudah['pelvis_y']} "
            f"| yaw {sebelum['root_yaw']} -> {sesudah['root_yaw']} "
            f"| kepala X {sebelum['kepala_x']} -> {sesudah['kepala_x']} "
            f"| kepala Z {sesudah['kepala_z']} | ok={ok}")

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(hasil, f, indent=1)
    log(f"selesai: {len(hasil)} animasi -> {LOG}")


main()
