"""V3b — Level v02: ganti GameMode Override ke Aksa2 (pawn Aksa versi BARU).

Latar: V3 memasang /Game/Jayadwara/Core/BP_JDGameMode (pawn = BP_Aksa lama) sesuai teks
panduan V3. Developer memutuskan (16 Okt 2026) level v02 memakai Aksa baru, sama seperti
preseden M7b v01: /Game/Jayadwara/Core/BP_JDGameMode_Aksa2 (pawn = BP_Aksa2; player
controller sama: BP_JDPlayerController). Tool ini HANYA mengganti referensi GameMode di
World Settings level (di dalam sandbox) — aset proyek tidak diubah.

Catatan: skrip V3 (maps_ep1_v02_30_level.py) sudah disetel ke Aksa2, jadi kalau V3
dijalankan ulang, tool ini tidak perlu lagi (tapi tetap aman dijalankan).

Uji (cetak): override sebelum -> sesudah + pawn/PC dari GameMode yang dipakai.

Pakai (dari WORKTREE, editor worktree terbuka, level v02 terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_32_gamemode.py
"""
import unreal

MAP = "/Game/Hermes/MapsEp1/Maps/Test_Hermes_MapsEp1_v02"
LEVEL_NAME = "Test_Hermes_MapsEp1_v02"
GAMEMODE_LAMA = "/Game/Jayadwara/Core/BP_JDGameMode"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode_Aksa2"

EAL = unreal.EditorAssetLibrary
problems = []


def log(m):
    unreal.log(f"[V3b] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[V3b] {m}")


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
    log(f"  pawn              = {d.get_editor_property('default_pawn_class')}")
    log(f"  player_controller = {d.get_editor_property('player_controller_class')}")

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

    log(f"CEK V3b: {'LULUS' if not problems else 'GAGAL'}")
    if problems:
        for p in problems:
            unreal.log_warning("  - " + p)


main()
