"""Animasi Mixamo hasil retarget: pangkas bagian yang tidak terpakai + ratakan geseran tulang root (Unreal Editor Python).

Jalankan SETELAH Tools/ue_import_mixamo.py dan SEBELUM Tools/ue_setup_light_combo.py (urutan di docs/12 bagian alur Mixamo).
Pakai: python Tools/ue_remote.py Tools/ue_mixamo_postproses.py
Boleh diulang, tapi import ulang (ue_import_mixamo.py) menimpa hasilnya, jadi selalu jalankan berdua.

Kenapa (temuan Hermes, Hermes/Laporan/2026-10-17-combo-iter2.md, temuan 8 + umpan balik 3–9):
  * Klip Mixamo membawa langkah maju / lompat di TRANSLASI tulang `root` (bukan root motion sequence). Kapsul diam, jadi
    mesh bergeser lalu menyentak balik (light_01 72 cm, air 204 cm, air_slam 370 cm). Diratakan per sumbu.
  * air_slam penuh 2,37 s -> dipangkas ke bagian sabetan + hantaman (0,65 s); hantaman udara kini berputar di tempat.
  * Pukulan 1–4 punya ancang-ancang 0,45 s dan ekor diam 0,5 s -> dipangkas supaya sambungan combo tidak berhenti di pose netral.
Jalan API yang berhasil: unreal.AnimSequencerController.set_bone_track_keys (UE 5.6). JANGAN pakai AnimDataController.set_model
(editor crash), enable_root_motion + force_root_lock (badan terbenam), atau AnimationLibrary.remove_bone_animation (animasi mati).
Kunci lama tidak bisa dibaca (internal_track_data kosong), jadi kunci dibangun ulang dari pose hasil sampel per frame.
"""
import unreal

MX = "/Game/Jayadwara/Characters/Aksa/Anims/Mixamo"
BONE = "root"
FPS = 30

# peran -> (mulai di klip asli, durasi) detik. Frame rate klip dipaksa 30 fps (air_slam asalnya 1770 fps).
PANGKAS = {
    # klip 18 Okt (2,37 s): ancang-ancang tangan (1,40) -> sabetan kaki kanan (1,63-1,90) -> hantaman (1,90) -> berdiri.
    # Mulai 1,40 (tangan masih di pose netral) supaya blend dari pose lompat tidak melompat ke pose sabetan.
    "air_slam": (1.40, 0.65),
    "air": (0.00, 0.90),          # tendangan saja; ekor diam 0,6 s dibuang agar montage selesai saat masih di udara
    "light_01": (0.10, 1.30),     # buang ancang-ancang yang menggeser kaki belakang 33 cm dan recovery yang menggesernya balik
    "light_02": (0.10, 1.35),
    "light_03": (0.45, 1.20),
    "light_04": (0.50, 1.05),
}
# peran -> sumbu (X, Y, Z) translasi root yang diratakan. Y = maju/mundur, X = samping, Z = tinggi.
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
    "air": (True, True, True),    # Z ikut: klip menambah lompatan 64 cm di atas lompatan kapsul -> "terlalu tinggi"
    "air_slam": (True, True, False),
}
# Posisi horizontal root dipaksa 0 (bukan ke frame pertama): hasil retarget air_slam menaruh pelvis 125 cm ke samping,
# jadi badan terseret saat blend masuk ("gerak ke samping kiri"). Yaw root TIDAK dikunci: putaran +187° berakhir menghadap depan.
NOL = {"air_slam"}

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
OPTS = unreal.AnimPoseEvaluationOptions()
LOCAL = unreal.AnimPoseSpaces.LOCAL
WORLD = unreal.AnimPoseSpaces.WORLD


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def controller(seq):
    model = seq.get_editor_property("data_model_interface")
    ctrl = unreal.new_object(unreal.AnimSequencerController, seq)
    ctrl.set_model(model)
    return model, ctrl


def pangkas(seq, t0, dur):
    """Tulis ulang SEMUA track tulang pada 30 fps untuk rentang [t0, t0+dur]. Urutan penting: sampel dulu, baru potong."""
    model, ctrl = controller(seq)
    n = int(round(dur * FPS)) + 1
    poses = [unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t0 + dur * i / float(n - 1), OPTS) for i in range(n)]
    ctrl.set_frame_rate(unreal.FrameRate(numerator=FPS, denominator=1))
    ctrl.set_play_length(dur)
    for b in list(model.get_bone_track_names()):
        trs = [unreal.AnimPoseExtensions.get_bone_pose(p, b, LOCAL) for p in poses]
        ctrl.set_bone_track_keys(b, [t.translation for t in trs], [t.rotation for t in trs], [t.scale3d for t in trs])


def ratakan(seq, sumbu, nol=False):
    """Translasi root sumbu terpilih dikunci ke nilai frame pertama; rotasi & skala disalin apa adanya."""
    model, ctrl = controller(seq)
    n = model.get_number_of_frames()
    length = AL.get_sequence_length(seq)
    trs = [unreal.AnimPoseExtensions.get_bone_pose(
        unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, min(length * i / float(max(n - 1, 1)), length), OPTS),
        BONE, LOCAL) for i in range(n)]
    base = unreal.Vector(0.0, 0.0, trs[0].translation.z) if nol else trs[0].translation
    pos = [unreal.Vector(base.x if sumbu[0] else t.translation.x,
                         base.y if sumbu[1] else t.translation.y,
                         base.z if sumbu[2] else t.translation.z) for t in trs]
    return ctrl.set_bone_track_keys(BONE, pos, [t.rotation for t in trs], [t.scale3d for t in trs])


def ukur(seq):
    """(rentang pelvis Y = maju/mundur cm, rentang pelvis X cm, rentang tinggi kepala) WORLD, 21 sampel."""
    length = AL.get_sequence_length(seq)
    px, py, hz = [], [], []
    for i in range(21):
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, length * i / 20.0, OPTS)
        p = unreal.AnimPoseExtensions.get_bone_pose(pose, "pelvis", WORLD).translation
        px.append(p.x)
        py.append(p.y)
        hz.append(unreal.AnimPoseExtensions.get_bone_pose(pose, "head", WORLD).translation.z)
    return round(max(py) - min(py), 1), round(max(px) - min(px), 1), (round(min(hz), 1), round(max(hz), 1))


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara] PIE sedang jalan — hentikan Play dulu")
        return
    done = 0
    for peran in sorted(set(PANGKAS) | set(RATAKAN)):
        path = f"{MX}/A_Aksa_Mx_{peran}"
        seq = unreal.load_asset(path)
        if not seq:
            log(f"{peran}: tidak ada ({path}), dilewati")
            continue
        awal = AL.get_sequence_length(seq)
        if peran in PANGKAS:
            t0, dur = PANGKAS[peran]
            if awal > dur + 0.05:                                 # sudah pendek = sudah dipangkas (aman diulang)
                pangkas(seq, t0, dur)
        if peran in RATAKAN:
            ratakan(seq, RATAKAN[peran], peran in NOL)
        EAL.save_loaded_asset(seq, only_if_is_dirty=False)
        geser, goyang_x, kepala = ukur(seq)
        log(f"{peran}: {awal:.2f} s -> {AL.get_sequence_length(seq):.2f} s | pinggul maju/mundur {geser} cm, samping {goyang_x} cm | kepala Z {kepala}")
        if geser > 3.0:
            unreal.log_warning(f"[Jayadwara] {peran}: pinggul masih bergeser {geser} cm (maju/mundur) > 3 cm")
        done += 1
    log(f"pasca-proses Mixamo selesai: {done} animasi — lanjut Tools/ue_setup_light_combo.py")


main()
