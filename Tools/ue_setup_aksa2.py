"""Aksa2 — pasang SK_Aksa2 di game SECARA PARALEL, Aksa lama tidak diubah (pola Jayadwara2, docs/25 R6) (Unreal Editor Python).

Butuh: hasil Tools/ue_import_aksa2.py, serta BP_Aksa + ABP_Aksa + BP_JDGameMode dari setup Aksa lama (TIDAK diubah).
Membuat / mengisi ulang (idempoten):
  Aksa2/BP_Aksa2                      salinan BP_Aksa (kamera/input/kombo sama), mesh = SK_Aksa2, anim = ABP_Aksa (dipakai bersama)
  Core/BP_JDGameMode_Aksa2            salinan BP_JDGameMode, default pawn = BP_Aksa2
  Maps/Test_Combat_Aksa2              salinan Test_Combat, game mode override = BP_JDGameMode_Aksa2  (Play = Aksa2)
BP_Aksa, SK_Aksa, ABP_Aksa, BP_JDGameMode, Test_Combat tidak disentuh: Aksa lama tetap model aktif di level lain.
Ganti model aktif secara global (nanti, setelah developer memutuskan):
  python Tools/ue_remote.py -c "ACTIVE_AKSA='Aksa2'; exec(open(r'Tools/ue_setup_aksa2.py').read())"   -> BP_JDGameMode memakai BP_Aksa2
  ACTIVE_AKSA='Aksa'  -> kembali ke BP_Aksa (aset kedua model tetap ada)
Default (tanpa ACTIVE_AKSA) = tidak mengubah BP_JDGameMode.
Pakai: python Tools/ue_remote.py Tools/ue_setup_aksa2.py   (editor terbuka, TIDAK sedang Play)
"""
import unreal

EAL = unreal.EditorAssetLibrary
A1, A2 = "/Game/Jayadwara/Characters/Aksa", "/Game/Jayadwara/Characters/Aksa2"
GM_SRC, GM2 = "/Game/Jayadwara/Core/BP_JDGameMode", "/Game/Jayadwara/Core/BP_JDGameMode_Aksa2"
MAP_SRC, MAP2 = "/Game/Jayadwara/Maps/Test_Combat", "/Game/Jayadwara/Maps/Test_Combat_Aksa2"
ACTIVE_AKSA = globals().get("ACTIVE_AKSA", None)           # None = jangan ubah BP_JDGameMode


def log(msg):
    unreal.log(f"[Aksa2] {msg}")


def dup(src, dst):
    if EAL.does_asset_exist(dst):
        return EAL.load_asset(dst)
    a = EAL.duplicate_asset(src, dst)
    assert a is not None, f"duplikat {src} gagal"
    log(f"{dst.split('/')[-1]} = salinan {src.split('/')[-1]}")
    return a


def make_pawn(mesh):
    bp = dup(f"{A1}/BP_Aksa", f"{A2}/BP_Aksa2")
    d = unreal.get_default_object(bp.generated_class())
    m = d.get_editor_property("mesh")
    m.set_editor_property("skeletal_mesh_asset", mesh)
    m.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    m.set_editor_property("anim_class", EAL.load_asset(f"{A1}/Anims/ABP_Aksa").generated_class())
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, False)
    log("BP_Aksa2: mesh = SK_Aksa2, anim = ABP_Aksa")
    return bp


def set_pawn(gm_path, bp):
    gm = EAL.load_asset(gm_path)
    unreal.get_default_object(gm.generated_class()).set_editor_property("default_pawn_class", bp.generated_class())
    unreal.BlueprintEditorLibrary.compile_blueprint(gm)
    EAL.save_loaded_asset(gm, False)
    log(f"{gm_path.split('/')[-1]}: default pawn = {bp.get_name()}")


def make_level(gm):
    # JANGAN duplicate_asset untuk level: world salinan tertahan di memori dan load_level berikutnya membuat editor crash.
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if EAL.does_asset_exist(MAP2):
        les.load_level(MAP2)
    else:
        les.new_level_from_template(MAP2, MAP_SRC)
        log("Test_Combat_Aksa2 dibuat dari Test_Combat")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", gm.generated_class())
    les.save_current_level()
    log("Test_Combat_Aksa2 siap: Play = Aksa2")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        raise RuntimeError("Editor sedang Play (PIE), hentikan dulu")
    mesh = EAL.load_asset(f"{A2}/Mesh/SK_Aksa2")
    if mesh is None:
        unreal.log_error("[Aksa2] SK_Aksa2 belum ada: jalankan Tools/ue_import_aksa2.py")
        return
    bp = make_pawn(mesh)
    dup(GM_SRC, GM2)
    set_pawn(GM2, bp)
    gm2 = EAL.load_asset(GM2)
    if ACTIVE_AKSA in ("Aksa", "Aksa2"):
        set_pawn(GM_SRC, EAL.load_asset(f"{A1}/BP_Aksa") if ACTIVE_AKSA == "Aksa" else bp)
    make_level(gm2)


main()
