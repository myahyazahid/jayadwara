"""M7b — Level Ep01: ganti pawn ke Aksa versi BARU (Aksa2).

Latar: sampai M7 level memakai GameMode Override /Game/Jayadwara/Core/BP_JDGameMode
(pawn = BP_Aksa, Aksa versi lama). Proyek sudah menyediakan
/Game/Jayadwara/Core/BP_JDGameMode_Aksa2 (pawn = BP_Aksa2; player controller sama:
BP_JDPlayerController). Tool ini HANYA mengganti referensi GameMode di World Settings
level (di dalam sandbox) — aset proyek tidak diubah (tetap "hanya direferensikan").

Catatan: M3 tetap menyetel GameMode lama (sesuai spesifikasi M3). Kalau M3 dijalankan
ulang, jalankan juga tool ini.

Uji (cetak): override sebelum -> sesudah + pawn/PC dari GameMode yang dipakai.

Pakai (dari WORKTREE): python Tools/ue_remote.py Hermes/Tools/maps_ep1_75_aksa2.py
"""
import unreal

MAP = "/Game/Hermes/MapsEp1/Maps/Test_Hermes_MapsEp1"
LEVEL_NAME = "Test_Hermes_MapsEp1"
GAMEMODE_LAMA = "/Game/Jayadwara/Core/BP_JDGameMode"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode_Aksa2"

EAL = unreal.EditorAssetLibrary
problems = []


def log(m):
    unreal.log(f"[M7b] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[M7b] {m}")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        fail("Editor sedang Play (PIE) — hentikan dulu")
        return

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    log(f"level = {world.get_name()}  ({MAP})")
    if world.get_name() != LEVEL_NAME:
        fail(f"level salah: {world.get_name()} (harus {LEVEL_NAME})")
        return

    gm = EAL.load_asset(GAMEMODE)
    if gm is None:
        fail(f"GameMode {GAMEMODE} tidak ditemukan")
        return

    d = unreal.get_default_object(gm.generated_class())
    log(f"GameMode baru = {GAMEMODE}")
    log(f"  pawn                 = {d.get_editor_property('default_pawn_class')}")
    log(f"  player_controller    = {d.get_editor_property('player_controller_class')}")

    ws = world.get_world_settings()
    before = ws.get_editor_property("default_game_mode")
    ws.set_editor_property("default_game_mode", gm.generated_class())
    after = ws.get_editor_property("default_game_mode")
    log(f"override: {before}")
    log(f"       -> {after}")

    old = EAL.load_asset(GAMEMODE_LAMA)
    if old is not None and after == old.generated_class():
        fail("override masih GameMode lama")

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    ok = les.save_current_level()
    log(f"simpan level = {ok}")
    if not ok:
        fail("gagal menyimpan level")

    if problems:
        unreal.log_warning(f"[M7b] {len(problems)} masalah")
    else:
        log("selesai tanpa masalah")


main()
