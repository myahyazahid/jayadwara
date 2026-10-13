"""Transformasi manusia <-> Jayadwara (Unreal Editor Python): aset input + isi BP_JDPlayerController.

Membuat / mengisi ulang (aman diulang):
  /Game/Input/Actions/IA_Transform       Input Action boolean
  /Game/Input/IMC_Default                + pemetaan tombol T -> IA_Transform
  /Game/Jayadwara/Core/BP_JDPlayerController   transform_action, giant_pawn_class = model raksasa AKTIF (butuh build C++ terbaru)
  /Game/Jayadwara/Core/BP_JDGameMode_Giant     default_pawn_class = model raksasa AKTIF (level Test_GiantScale)
Model aktif dipilih lewat ACTIVE_GIANT (docs/25 R6, 13 Okt 2026: developer memilih Jayadwara2). Kembali ke model lama:
  ubah ACTIVE_GIANT = "Jayadwara" lalu jalankan ulang skrip ini (aset kedua model tetap ada).
Pakai: python Tools/ue_remote.py Tools/ue_setup_transform.py
"""
import unreal

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

IA_PATH = "/Game/Input/Actions/IA_Transform"
IMC_PATH = "/Game/Input/IMC_Default"
PC_PATH = "/Game/Jayadwara/Core/BP_JDPlayerController"
GIANTS = {"Jayadwara": "/Game/Jayadwara/Characters/Jayadwara/BP_Jayadwara",          # model lama (stylized, skrip) — cadangan
          "Jayadwara2": "/Game/Jayadwara/Characters/Jayadwara2/BP_Jayadwara2"}     # model Tripo (docs/25) — AKTIF sejak R6
ACTIVE_GIANT = globals().get("ACTIVE_GIANT", "Jayadwara2")
GIANT_PATH = GIANTS[ACTIVE_GIANT]
GM_GIANT_PATH = "/Game/Jayadwara/Core/BP_JDGameMode_Giant"
KEY = "T"


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def ensure_action():
    if EAL.does_asset_exist(IA_PATH):
        return EAL.load_asset(IA_PATH)
    action = asset_tools.create_asset("IA_Transform", "/Game/Input/Actions", unreal.InputAction, unreal.InputAction_Factory())
    EAL.save_loaded_asset(action, only_if_is_dirty=False)
    log("IA_Transform dibuat")
    return action


def map_key(imc, action):
    for m in imc.get_editor_property("mappings"):
        if m.get_editor_property("action") == action and m.get_editor_property("key").get_editor_property("key_name") == KEY:
            log(f"IMC_Default sudah memetakan {KEY}")
            return
    key = unreal.Key()
    key.set_editor_property("key_name", KEY)
    imc.map_key(action, key)
    EAL.save_loaded_asset(imc, only_if_is_dirty=False)
    log(f"IMC_Default: {KEY} -> IA_Transform")


def fill_controller(action):
    giant = EAL.load_asset(GIANT_PATH)
    pc = EAL.load_asset(PC_PATH)
    d = unreal.get_default_object(pc.generated_class())
    d.set_editor_property("transform_action", action)
    d.set_editor_property("giant_pawn_class", giant.generated_class())
    unreal.BlueprintEditorLibrary.compile_blueprint(pc)
    EAL.save_loaded_asset(pc, only_if_is_dirty=False)
    log(f"BP_JDPlayerController: transform_action & giant_pawn_class = {giant.get_name()}")
    if EAL.does_asset_exist(GM_GIANT_PATH):
        gm = EAL.load_asset(GM_GIANT_PATH)
        unreal.get_default_object(gm.generated_class()).set_editor_property("default_pawn_class", giant.generated_class())
        unreal.BlueprintEditorLibrary.compile_blueprint(gm)
        EAL.save_loaded_asset(gm, only_if_is_dirty=False)
        log(f"BP_JDGameMode_Giant: default_pawn_class = {giant.get_name()}")


def main():
    action = ensure_action()
    map_key(EAL.load_asset(IMC_PATH), action)
    if hasattr(unreal.JDPlayerController, "ToggleTransformation") or hasattr(unreal.JDPlayerController, "toggle_transformation"):
        fill_controller(action)
    else:
        log("C++ belum ter-build dengan transformasi: BP_JDPlayerController belum diisi (jalankan ulang setelah build)")


main()
