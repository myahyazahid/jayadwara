"""Fase 1 Iterasi 2b — retarget animasi combat Aksa ke Jayadwara2 (Unreal Editor Python).

Tujuan (docs/23 §6 Iterasi 2b): Jayadwara memakai **jurus yang sama** dengan Aksa (keputusan developer 17 Okt 2026,
docs/07 "Daftar jurus Jayadwara (usulan)"). Montage hanya bisa memakai animasi yang skeleton-nya sama dengan mesh, jadi
animasi Aksa (skeleton Mannequin) harus di-retarget dulu ke `SKEL_Jayadwara2`.

Butuh:
  - hasil Tools/ue_import_mixamo.py + Tools/ue_mixamo_postproses.py + Tools/ue_setup_light_combo.py (A_Aksa_Mx_*),
  - hasil Tools/ue_setup_jayadwara2.py (SK_Jayadwara2, IK_Jayadwara2, RTG_Mannequin_To_Jayadwara2).
Pakai: python Tools/ue_remote.py Tools/ue_setup_giant_mixamo.py
Lalu WAJIB: python Tools/ue_remote.py Tools/ue_setup_giant_combo.py  (montage + profil memakai hasil skrip ini)

Membuat / mengisi ulang (aman diulang):
  Jayadwara2/Anims/Mixamo/A_JD2_Mx_light_01..04      dari A_Aksa_Mx_light_01..04
  Jayadwara2/Anims/Mixamo/A_JD2_Mx_back              dari A_Aksa_Mx_back
  Jayadwara2/Anims/Mixamo/A_JD2_Mx_finisher_01..03   dari A_Aksa_Mx_finisher_01..03
  Jayadwara2/Anims/Mixamo/A_JD2_Mx_air, _air_slam    dari A_Aksa_Mx_air, A_Aksa_Mx_air_slam
  Jayadwara2/Anims/Mixamo/A_JD2_Mx_lunge             hanya kalau A_Aksa_Mx_lunge ada (belum: lunge.fbx salah isi)
  Jayadwara2/Anims/Mixamo/A_JD2_Mx_dodge_*, _parry_* hanya kalau animasinya sudah ada di Aksa
  Jayadwara2/Anims/Mixamo/A_JD2_Src_attack_01        placeholder terjang (A_Aksa_Attack_01)
  Jayadwara2/Anims/Mixamo/A_JD2_Src_attack_02        placeholder berat & pose tangkis (A_Aksa_Attack_02)
  Jayadwara2/Anims/Mixamo/A_JD2_Src_stagger          placeholder stagger (A_Aksa_Stagger)

Catatan:
  - Tidak ada download Mixamo di sini: sumbernya animasi Aksa yang sudah lulus uji tangan 18 Okt 2026.
  - Folder tujuan hanya berisi hasil skrip ini (dihapus & dibuat ulang tiap jalan). Aset di luar
    `/Game/Jayadwara/Characters/Jayadwara2/Anims/Mixamo` tidak disentuh; RTG/IK Rig/skeleton hanya dibaca.
  - Panjang klip & tabel notify TIDAK diubah di sini. Notify dipasang di ue_setup_giant_combo.py dengan menyalin
    angka montage Aksa (paritas, docs/23 G2b-1).
"""
import warnings

import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary

J2 = "/Game/Jayadwara/Characters/Jayadwara2"
AKSA = "/Game/Jayadwara/Characters/Aksa"
DEST = f"{J2}/Anims/Mixamo"
MESH = f"{J2}/Mesh/SK_Jayadwara2"
RTG = f"{J2}/Rig/RTG_Mannequin_To_Jayadwara2"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
SUFFIX = "_JD2"                       # nama sementara dari helper retarget, diganti di bawah

# Sumber -> nama akhir. Urutan = urutan laporan. "wajib" = skrip berhenti kalau tidak ada.
ROLES = [
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_light_01",    "A_JD2_Mx_light_01",    True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_light_02",    "A_JD2_Mx_light_02",    True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_light_03",    "A_JD2_Mx_light_03",    True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_light_04",    "A_JD2_Mx_light_04",    True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_back",        "A_JD2_Mx_back",        True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_finisher_01", "A_JD2_Mx_finisher_01", True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_finisher_02", "A_JD2_Mx_finisher_02", True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_finisher_03", "A_JD2_Mx_finisher_03", True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_air",         "A_JD2_Mx_air",         True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_air_slam",    "A_JD2_Mx_air_slam",    True),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_lunge",       "A_JD2_Mx_lunge",       False),   # belum ada (lunge.fbx salah isi)
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_dodge_forward", "A_JD2_Mx_dodge_forward", False),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_dodge_back",  "A_JD2_Mx_dodge_back",  False),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_dodge_left",  "A_JD2_Mx_dodge_left",  False),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_dodge_right", "A_JD2_Mx_dodge_right", False),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_parry_01",    "A_JD2_Mx_parry_01",    False),
    (f"{AKSA}/Anims/Mixamo/A_Aksa_Mx_parry_02",    "A_JD2_Mx_parry_02",    False),
    # Placeholder Mannequin yang dipakai montage Aksa (berat, pose tangkis, stagger) — ikut disamakan.
    (f"{AKSA}/Anims/Attack/A_Aksa_Attack_01",      "A_JD2_Src_attack_01",  True),
    (f"{AKSA}/Anims/Attack/A_Aksa_Attack_02",      "A_JD2_Src_attack_02",  True),
    (f"{AKSA}/Anims/Attack/A_Aksa_Stagger",        "A_JD2_Src_stagger",    True),
]

problems = []


def log(msg):
    unreal.log(f"[Jayadwara2/2b] {msg}")


def fail(msg):
    problems.append(msg)
    unreal.log_error(f"[Jayadwara2/2b] {msg}")


def skeleton_of(asset):
    try:
        return asset.get_editor_property("skeleton")
    except Exception:
        return None


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara2/2b] PIE sedang jalan — hentikan Play dulu")
        return
    if not hasattr(unreal, "JDEditorToolsLibrary"):
        unreal.log_error("[Jayadwara2/2b] JDEditorToolsLibrary tidak ada (build C++ proyek belum jalan?)")
        return

    mesh = EAL.load_asset(MESH)
    rtg = EAL.load_asset(RTG)
    manny = EAL.load_asset(MANNY)
    if not mesh or not rtg or not manny:
        fail(f"aset dasar tidak lengkap: mesh={bool(mesh)} rtg={bool(rtg)} manny={bool(manny)} "
             f"(jalankan Tools/ue_setup_jayadwara2.py dulu)")
        return
    log(f"target {MESH} ({str(skeleton_of(mesh)).rsplit('.', 1)[-1]}), RTG {RTG.rsplit('/', 1)[-1]}")

    # ---- 1. kumpulkan sumber yang ada
    sources, planned = [], []
    for src, name, wajib in ROLES:
        if EAL.does_asset_exist(src):
            a = EAL.load_asset(src)
            sources.append(a)
            planned.append((src, name, a))
        elif wajib:
            fail(f"sumber wajib tidak ada: {src} (jalankan Tools/ue_import_mixamo.py + ue_setup_light_combo.py)")
        else:
            log(f"lewati {name}: {src.rsplit('/', 1)[-1]} belum ada (opsional)")
    if not sources:
        fail("tidak ada sumber yang bisa di-retarget")
        return

    # ---- 2. kosongkan folder tujuan (hanya milik skrip ini)
    if EAL.does_directory_exist(DEST):
        for p in EAL.list_assets(DEST, recursive=True):
            EAL.delete_asset(str(p).split(".")[0])
    left = EAL.list_assets(DEST, recursive=True) if EAL.does_directory_exist(DEST) else []
    if left:
        fail(f"gagal mengosongkan {DEST}: {left}")
        return

    # ---- 3. retarget sekali jalan (helper proyek: JDEditorToolsLibrary.retarget_assets_to_folder)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            unreal.JDEditorToolsLibrary.retarget_assets_to_folder(sources, manny, mesh, rtg, DEST, SUFFIX, True)
    except Exception as e:
        fail(f"retarget gagal: {e}")
        return
    EAL.save_directory(DEST, only_if_is_dirty=False, recursive=True)

    # ---- 4. ganti nama hasil retarget jadi A_JD2_*
    made = 0
    for src, name, source_asset in planned:
        temp = f"{DEST}/{source_asset.get_name()}{SUFFIX}"
        if not EAL.does_asset_exist(temp):
            fail(f"hasil retarget tidak ditemukan: {temp}")
            continue
        if EAL.does_asset_exist(f"{DEST}/{name}"):
            EAL.delete_asset(f"{DEST}/{name}")
        EAL.rename_asset(temp, f"{DEST}/{name}")
        a = EAL.load_asset(f"{DEST}/{name}")
        if not a:
            fail(f"gagal memuat hasil rename {name}")
            continue
        EAL.save_loaded_asset(a, only_if_is_dirty=False)

        skel = str(skeleton_of(a))
        panjang = AL.get_sequence_length(a)
        panjang_src = AL.get_sequence_length(source_asset)
        beda = abs(panjang - panjang_src)
        status = "OK" if beda <= 1.0 / 30.0 + 1e-4 else f"PANJANG BEDA {beda:.3f} s"
        if "Jayadwara2" not in skel:
            fail(f"{name}: skeleton bukan Jayadwara2 ({skel.rsplit('.', 1)[-1]})")
        if beda > 1.0 / 30.0 + 1e-4:
            fail(f"{name}: panjang {panjang:.3f} s vs sumber {panjang_src:.3f} s")
        log(f"{name:<22} <- {source_asset.get_name():<24} {panjang:5.2f} s  {status}")
        made += 1

    # ---- 5. ringkasan
    log(f"retarget selesai: {made}/{len(planned)} animasi di {DEST}")
    log("LANGKAH BERIKUTNYA: python Tools/ue_remote.py Tools/ue_setup_giant_combo.py "
        "(montage + notify paritas + DA_CombatProfile_Giant)")
    if problems:
        unreal.log_warning(f"[Jayadwara2/2b] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("tidak ada masalah")


main()
