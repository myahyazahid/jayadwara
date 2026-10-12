"""Transformasi manusia <-> Jayadwara (Unreal Editor Python): aset input + isi BP_JDPlayerController.

Membuat / mengisi ulang (aman diulang):
  /Game/Input/Actions/IA_Transform       Input Action boolean
  /Game/Input/IMC_Default                + pemetaan tombol T -> IA_Transform
  /Game/Jayadwara/Core/BP_JDPlayerController   transform_action, giant_pawn_class = BP_Jayadwara (butuh build C++ terbaru)
Pakai: python Tools/ue_remote.py Tools/ue_setup_transform.py
"""
import unreal

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

IA_PATH = "/Game/Input/Actions/IA_Transform"
IMC_PATH = "/Game/Input/IMC_Default"
PC_PATH = "/Game/Jayadwara/Core/BP_JDPlayerController"
GIANT_PATH = "/Game/Jayadwara/Characters/Jayadwara/BP_Jayadwara"
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
    log("BP_JDPlayerController: transform_action & giant_pawn_class terisi")


def main():
    action = ensure_action()
    map_key(EAL.load_asset(IMC_PATH), action)
    if hasattr(unreal.JDPlayerController, "ToggleTransformation") or hasattr(unreal.JDPlayerController, "toggle_transformation"):
        fill_controller(action)
    else:
        log("C++ belum ter-build dengan transformasi: BP_JDPlayerController belum diisi (jalankan ulang setelah build)")


main()
