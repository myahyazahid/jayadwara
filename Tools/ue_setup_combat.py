"""Fase 1 Iterasi 1 — fondasi GAS: input combat, DataAsset, BP, level Test_Combat (Unreal Editor Python).

Butuh build C++ Iterasi 1 (UJDInputConfig, UJDAbilitySet, UJDEditorToolsLibrary.make_gameplay_tag).
Pakai: python Tools/ue_remote.py Tools/ue_setup_combat.py
Membuat / mengisi ulang (aman diulang, docs/23 bagian 4.4 & Iterasi 1):
  /Game/Jayadwara/Input/Actions/IA_AttackLight, IA_AttackHeavy, IA_Block, IA_Dodge, IA_LockOn, IA_TransformChord
  /Game/Jayadwara/Input/IMC_Human          salinan IMC_Default (gerak, kamera, lompat, T) + tombol combat KB/M & gamepad;
                                           transformasi gamepad = L1 + R1 (LB ditekan saat RB ditahan: chord)
  /Game/Jayadwara/Data/DA_InputConfig_Human   IA combat -> Input.* tag
  /Game/Jayadwara/Data/DA_AbilitySet_Aksa     atribut awal Aksa (docs/23 bagian 5), buffer input 0,2 s
  BP_Aksa (ability_set, input_config), BP_JDPlayerController (IMC_Human + IMC_MouseLook)
  /Game/Jayadwara/Maps/Test_Combat         lantai 60 x 60 m + beberapa kotak; dibangun ulang hanya kalau REBUILD_LEVEL
Tidak menaruh musuh/Jerangkong di level (ringan untuk laptop); minion masuk di Iterasi 5.
"""
import unreal

REBUILD_LEVEL = False

INPUT = "/Game/Jayadwara/Input"
DATA = "/Game/Jayadwara/Data"
MAP = "/Game/Jayadwara/Maps/Test_Combat"
AKSA_BP = "/Game/Jayadwara/Characters/Aksa/BP_Aksa"
PC_BP = "/Game/Jayadwara/Core/BP_JDPlayerController"
GM_BP = "/Game/Jayadwara/Core/BP_JDGameMode"

# (nama IA, input tag, [tombol]) — docs/23 bagian 4.4. Gamepad memakai nama tombol layout Xbox (x360ce / Steam Input).
COMBAT_ACTIONS = [
    ("IA_AttackLight", "Input.Attack.Light", ["LeftMouseButton", "Gamepad_FaceButton_Left"]),
    ("IA_AttackHeavy", "Input.Attack.Heavy", ["E", "Gamepad_FaceButton_Top"]),
    ("IA_Block", "Input.Block", ["RightMouseButton", "Gamepad_RightTrigger"]),
    ("IA_Dodge", "Input.Dodge", ["LeftShift", "Gamepad_FaceButton_Right"]),
    ("IA_LockOn", "Input.LockOn", ["Q", "MiddleMouseButton", "Gamepad_RightThumbstick"]),
]
AKSA_ATTRIBUTES = {
    "max_health": 100.0, "max_stamina": 100.0, "max_poise": 50.0, "max_sync": 0.0, "max_transform_energy": 100.0,
    "stamina_regen_per_second": 25.0, "stamina_regen_delay": 0.8,
}

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
problems = []


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def fail(msg):
    problems.append(msg)
    unreal.log_error(f"[Jayadwara] {msg}")


def load(path):
    a = EAL.load_asset(path)
    if a is None:
        fail(f"aset tidak ada: {path}")
    return a


def tag(name):
    t = unreal.JDEditorToolsLibrary.make_gameplay_tag(name)
    if name not in t.export_text():
        fail(f"tag tidak terdaftar: {name}")
    return t


def make_key(name):
    k = unreal.Key()
    k.set_editor_property("key_name", name)
    return k


# ------------------------------------------------------------------ input
def ensure_action(name):
    path = f"{INPUT}/Actions/{name}"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    a = asset_tools.create_asset(name, f"{INPUT}/Actions", unreal.InputAction, unreal.InputAction_Factory())
    EAL.save_loaded_asset(a, only_if_is_dirty=False)
    log(f"{name} dibuat")
    return a


def ensure_imc():
    path = f"{INPUT}/IMC_Human"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    imc = EAL.duplicate_asset("/Game/Input/IMC_Default", path)
    log("IMC_Human dibuat dari IMC_Default")
    return imc


def find_mapping(imc, action, key_name):
    for i, m in enumerate(imc.get_editor_property("mappings")):
        if m.get_editor_property("action") == action and m.get_editor_property("key").get_editor_property("key_name") == key_name:
            return i
    return -1


def ensure_mapping(imc, action, key_name, chord=None):
    if find_mapping(imc, action, key_name) < 0:
        imc.map_key(action, make_key(key_name))
        log(f"IMC_Human: {key_name} -> {action.get_name()}")
    if chord is None:
        return
    mappings = imc.get_editor_property("mappings")
    i = find_mapping(imc, action, key_name)
    # ChordAction = EditInstanceOnly: Python menolak mengisinya pada objek yang outer-nya aset ("template"), jadi
    # dibuat di transient, diisi, lalu dipindah ke dalam IMC supaya ikut tersimpan.
    trig = unreal.new_object(unreal.InputTriggerChordAction)
    trig.set_editor_property("chord_action", chord)
    trig.rename("None", imc)
    m = mappings[i]
    m.set_editor_property("triggers", [trig])
    mappings[i] = m
    imc.set_editor_property("mappings", mappings)


def setup_input():
    imc = ensure_imc()
    actions = {}
    for name, _, keys in COMBAT_ACTIONS:
        ia = ensure_action(name)
        actions[name] = ia
        for k in keys:
            ensure_mapping(imc, ia, k)

    # Transformasi gamepad L1 + R1: RB menyalakan IA_TransformChord, LB memicu IA_Transform hanya selama chord aktif.
    chord = ensure_action("IA_TransformChord")
    ensure_mapping(imc, chord, "Gamepad_RightShoulder")
    transform = load("/Game/Input/Actions/IA_Transform")
    if transform:
        ensure_mapping(imc, transform, "T")
        ensure_mapping(imc, transform, "Gamepad_LeftShoulder", chord=chord)
    EAL.save_loaded_asset(imc, only_if_is_dirty=False)
    return imc, actions


# ------------------------------------------------------------------ data
def ensure_data_asset(name, cls):
    path = f"{DATA}/{name}"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    f = unreal.DataAssetFactory()
    f.set_editor_property("data_asset_class", cls)
    a = asset_tools.create_asset(name, DATA, cls, f)
    log(f"{name} dibuat")
    return a


def setup_data(actions):
    cfg = ensure_data_asset("DA_InputConfig_Human", unreal.JDInputConfig)
    entries = []
    for name, tag_name, _ in COMBAT_ACTIONS:
        e = unreal.JDInputAction()
        e.set_editor_property("input_action", actions[name])
        e.set_editor_property("input_tag", tag(tag_name))
        entries.append(e)
    cfg.set_editor_property("ability_input_actions", entries)
    EAL.save_loaded_asset(cfg, only_if_is_dirty=False)

    aset = ensure_data_asset("DA_AbilitySet_Aksa", unreal.JDAbilitySet)
    attrs = aset.get_editor_property("attributes")
    for k, v in AKSA_ATTRIBUTES.items():
        attrs.set_editor_property(k, v)
    aset.set_editor_property("attributes", attrs)
    aset.set_editor_property("input_buffer_time", 0.2)
    EAL.save_loaded_asset(aset, only_if_is_dirty=False)
    log("DA_InputConfig_Human & DA_AbilitySet_Aksa terisi")
    return cfg, aset


def compile_save(bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)


def setup_bps(imc, cfg, aset):
    aksa = load(AKSA_BP)
    if aksa:
        d = unreal.get_default_object(aksa.generated_class())
        d.set_editor_property("ability_set", aset)
        d.set_editor_property("input_config", cfg)
        compile_save(aksa)
        log("BP_Aksa: ability_set & input_config terisi")
    pc = load(PC_BP)
    if pc:
        d = unreal.get_default_object(pc.generated_class())
        d.set_editor_property("human_mapping_contexts", [imc, load("/Game/Input/IMC_MouseLook")])
        compile_save(pc)
        log("BP_JDPlayerController: IMC_Human + IMC_MouseLook")


# ------------------------------------------------------------------ level
def spawn_box(eas, label, center, size_m, mat, folder):
    cube = unreal.load_asset("/Engine/BasicShapes/Cube")
    sx, sy, sz = size_m
    a = eas.spawn_actor_from_object(cube, unreal.Vector(center[0], center[1], center[2] + sz * 50.0))
    a.set_actor_scale3d(unreal.Vector(sx, sy, sz))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    if mat:
        a.static_mesh_component.set_material(0, mat)
    return a


def build_level():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    exists = EAL.does_asset_exist(MAP)
    if exists and not REBUILD_LEVEL:
        les.load_level(MAP)
    else:
        if exists:
            EAL.delete_asset(MAP)
        if not les.new_level_from_template(MAP, "/Engine/Maps/Templates/Template_Default"):
            fail("level Test_Combat gagal dibuat")
            return
        for a in eas.get_all_level_actors():
            if isinstance(a, (unreal.StaticMeshActor, unreal.PlayerStart)):
                a.destroy_actor()
        grid = load("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray")
        dark = load("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_TopDark")
        spawn_box(eas, "Floor", (0, 0, -100), (60, 60, 1), grid, "Combat/Floor")          # 60 x 60 m, permukaan z = 0
        # arena: pinggir rendah supaya terasa ruang tarung, beberapa penghalang untuk uji kamera & dodge
        for i, (x, y, w, d) in enumerate(((0, 2000, 40, 1), (0, -2000, 40, 1), (2000, 0, 1, 40), (-2000, 0, 1, 40))):
            spawn_box(eas, f"Wall_{i}", (x, y, 0), (w, d, 1.2), dark, "Combat/Arena")
        for i, (x, y) in enumerate(((800, 600), (-700, 900), (500, -900))):
            spawn_box(eas, f"Pillar_{i}", (x, y, 0), (1, 1, 3), dark, "Combat/Arena")
        ps = eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-1200, 0, 100))
        ps.set_folder_path("Combat")
        log("level Test_Combat dibangun")

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    gm = load(GM_BP)
    if gm:
        world.get_world_settings().set_editor_property("default_game_mode", gm.generated_class())
    les.save_current_level()
    log("Test_Combat: GameMode Override = BP_JDGameMode, disimpan")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara] PIE sedang jalan — hentikan Play dulu")
        return
    if not hasattr(unreal, "JDInputConfig") or not hasattr(unreal.JDEditorToolsLibrary, "make_gameplay_tag"):
        unreal.log_error("[Jayadwara] C++ Iterasi 1 belum ter-build (JDInputConfig / make_gameplay_tag tidak ada)")
        return
    imc, actions = setup_input()
    cfg, aset = setup_data(actions)
    setup_bps(imc, cfg, aset)
    build_level()
    if problems:
        unreal.log_warning(f"[Jayadwara] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("setup combat Iterasi 1 selesai")


main()
