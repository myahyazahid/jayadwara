"""Fase 0 — rangkai Blueprint dasar + level Test_Greybox (Unreal Editor Python).

Membuat (kalau belum ada) lalu mengisi:
  /Game/Jayadwara/Core/BP_JDPlayerController   parent AJDPlayerController, IMC_Default + IMC_MouseLook
  /Game/Jayadwara/Core/BP_JDGameMode           parent AJDGameMode, pawn BP_Aksa, controller BP_JDPlayerController
  /Game/Jayadwara/Characters/Aksa/BP_Aksa      parent AJDHumanCharacter, SKM_Manny_Simple + ABP_Unarmed, IA_*
  /Game/Jayadwara/Maps/Test_Greybox            lantai 200 m, tangga/ramp, blok "gedung" 10–40 m (uji skala raksasa)
Butuh konten Third Person (Characters/, Input/, LevelPrototyping/) di /Game — disalin dari Templates/TemplateResources/High.

Pakai: python Tools/ue_remote.py Tools/ue_setup_greybox.py   (atau Output Log > Python: py "<path>")
Aman dijalankan ulang: aset yang ada diisi ulang; level dibangun ulang hanya kalau REBUILD_LEVEL = True.
"""
import unreal

REBUILD_LEVEL = False

CORE = "/Game/Jayadwara/Core"
AKSA = "/Game/Jayadwara/Characters/Aksa"
MAP = "/Game/Jayadwara/Maps/Test_Greybox"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
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


def make_bp(folder, name, parent):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        bp = EAL.load_asset(path)
        log(f"{name} sudah ada, diisi ulang")
        return bp
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", parent)
    bp = asset_tools.create_asset(name, folder, unreal.Blueprint, f)
    log(f"{name} dibuat (parent {parent.__name__})")
    return bp


def cdo(bp):
    return unreal.get_default_object(bp.generated_class())


def finish(bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)


# ------------------------------------------------------------------ Blueprint
def setup_controller():
    bp = make_bp(CORE, "BP_JDPlayerController", unreal.JDPlayerController)
    imcs = [a for a in (load("/Game/Input/IMC_Default"), load("/Game/Input/IMC_MouseLook")) if a]
    cdo(bp).set_editor_property("human_mapping_contexts", imcs)
    finish(bp)
    return bp


def setup_aksa():
    bp = make_bp(AKSA, "BP_Aksa", unreal.JDHumanCharacter)
    d = cdo(bp)
    mesh = d.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh_asset", load("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"))
    abp = load("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed")
    if abp:
        mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
        mesh.set_editor_property("anim_class", abp.generated_class())
    # Kapsul C++ setengah-tinggi 96: kaki Manny di dasar kapsul, wajah ke +X (arah maju actor).
    mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -96.0))
    mesh.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
    for prop, path in (("move_action", "/Game/Input/Actions/IA_Move"),
                       ("look_action", "/Game/Input/Actions/IA_Look"),
                       ("mouse_look_action", "/Game/Input/Actions/IA_MouseLook"),
                       ("jump_action", "/Game/Input/Actions/IA_Jump")):
        d.set_editor_property(prop, load(path))
    finish(bp)
    return bp


def setup_gamemode(aksa, pc):
    bp = make_bp(CORE, "BP_JDGameMode", unreal.JDGameMode)
    d = cdo(bp)
    d.set_editor_property("default_pawn_class", aksa.generated_class())
    d.set_editor_property("player_controller_class", pc.generated_class())
    finish(bp)
    return bp


# ------------------------------------------------------------------ level
def spawn_box(label, center, size_m, mat, folder="Greybox"):
    """Kubus BasicShapes (100 cm) diskalakan ke size_m (meter). center dalam cm, z = dasar kotak."""
    cube = unreal.load_asset("/Engine/BasicShapes/Cube")
    sx, sy, sz = size_m
    loc = unreal.Vector(center[0], center[1], center[2] + sz * 50.0)
    a = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_object(cube, loc)
    a.set_actor_scale3d(unreal.Vector(sx, sy, sz))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    if mat:
        a.static_mesh_component.set_material(0, mat)
    return a


def build_level(gm):
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    exists = EAL.does_asset_exist(MAP)
    if exists and not REBUILD_LEVEL:
        les.load_level(MAP)
    else:
        if exists:
            EAL.delete_asset(MAP)
        if not les.new_level_from_template(MAP, "/Engine/Maps/Templates/Template_Default"):
            fail("level Test_Greybox gagal dibuat")
            return
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        for a in eas.get_all_level_actors():                      # lantai kecil bawaan template diganti lantai besar
            if isinstance(a, (unreal.StaticMeshActor, unreal.PlayerStart)):
                a.destroy_actor()
        grid = load("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray")
        dark = load("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_TopDark")

        spawn_box("Floor", (0, 0, -100), (200, 200, 1), grid, "Greybox/Floor")   # 200 x 200 m, permukaan z = 0
        # area manusia: tangga, panggung, ramp
        for i in range(5):
            spawn_box(f"Step_{i}", (800 + i * 60, -600, 0), (0.6, 3, 0.2 * (i + 1)), dark, "Greybox/Human")
        spawn_box("Platform", (1300, -600, 0), (4, 4, 1), dark, "Greybox/Human")
        ramp = spawn_box("Ramp", (800, 600, 0), (6, 3, 0.2), dark, "Greybox/Human")
        ramp.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=15.0, yaw=0.0), False)
        for i, (x, y) in enumerate(((600, 1200), (900, 1250), (1200, 1150))):
            spawn_box(f"Crate_{i}", (x, y, 0), (1, 1, 1), dark, "Greybox/Human")
        # skala raksasa (Jayadwara ±45 m, placeholder D4): "gedung" 10–40 m
        for i, (x, y, w, d, h) in enumerate(((-3000, -3000, 12, 12, 20), (-3000, 0, 10, 20, 30), (-3000, 3000, 15, 15, 40),
                                             (-6000, -1500, 20, 10, 15), (-6000, 1500, 12, 12, 25))):
            spawn_box(f"Building_{i}_{h}m", (x, y, 0), (w, d, h), grid, "Greybox/Giant")
        ps = eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 100))
        ps.set_folder_path("Greybox")
        log("level Test_Greybox dibangun")

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", gm.generated_class())
    les.save_current_level()
    log("Test_Greybox: GameMode Override = BP_JDGameMode, disimpan")


def main():
    pc = setup_controller()
    aksa = setup_aksa()
    gm = setup_gamemode(aksa, pc)
    build_level(gm)
    if problems:
        unreal.log_warning(f"[Jayadwara] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("setup greybox selesai")


main()
