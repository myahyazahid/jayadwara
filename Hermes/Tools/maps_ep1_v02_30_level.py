"""V3 — Level UE v02 (Unreal Editor Python, via Tools/ue_remote.py).

DEST = /Game/Hermes/MapsEp1  (sandbox Hermes; material v01 dipakai ulang)
1. Level baru dari /Engine/Maps/Templates/Template_Default -> DEST/Maps/Test_Hermes_MapsEp1_v02;
   hapus lantai bawaan template.
2. Impor 2 FBX v02 (SM_Ep01_Medan_v02, SM_Ep01_Tangga_v02) ke DEST/Meshes sebagai Static Mesh
   (tanpa Nanite, tanpa LOD otomatis). Collision: Use Complex as Simple.
3. Pakai ulang material v01 (M_Hermes_Greybox + 15 MI_Ep01_*) -- TIDAK dibuat ulang; pasang ke
   slot medan/tangga per nama slot.
4. Taruh medan & tangga di (0, 0, 0).
5. World Settings level: GameMode Override = /Game/Jayadwara/Core/BP_JDGameMode_Aksa2 (hanya referensi; pawn = Aksa baru, sesuai keputusan developer 16 Okt 2026 & preseden M7b v01).
6. DirectionalLight = setelan cahaya `sore` v02 dari ep01_layout_v02.json.
7. Simpan level + aset DEST satu per satu (TIDAK PERNAH Save All).

Uji (cetak tabel):
- bounds medan (cm): target X 140000, Y 122000; Z dicetak (v02: kali -14 m .. hutan utara +115 m).
- line trace vertikal di 14 titik uji -> Z = elev(x,y)*100 +/- 5 cm.

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_30_level.py
"""
import os
import sys
import json
import math

import unreal

DEST = "/Game/Hermes/MapsEp1"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp1_v02"
LEVEL_NAME = "Test_Hermes_MapsEp1_v02"
MESH_DIR = f"{DEST}/Meshes"
MAT_DIR = f"{DEST}/Materials"
TEMPLATE = "/Engine/Maps/Templates/Template_Default"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode_Aksa2"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EXPORT = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Export")
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep01_medan_v02 as M  # elev + TITIK_UJI  (v02; JANGAN pakai ep01_medan v01)

with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
CAHAYA = DATA["cahaya"]
CAHAYA_UTAMA = "sore"   # konvensi v02: uji main pakai `sore`

EAL = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary

problems = []


def log(m):
    unreal.log(f"[V3] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[V3] {m}")


# ------------------------------------------------------------------ material (pakai ulang v01)
MI_TABLE = [
    "Andesit", "Arca", "Galian", "Plato", "Sawah", "Desa", "Hutan", "Air",
    "Jalan", "Kayu", "Alat", "Terpal", "Kendaraan", "Musala", "Penanda",
]
ZONA_SLOT = ["Air", "Galian", "Jalan", "Plato", "Sawah", "Desa", "Hutan"]


def load_materials():
    """Pakai ulang material v01 (M_Hermes_Greybox + 15 MI_Ep01_*). TIDAK dibuat ulang."""
    mat = EAL.load_asset(f"{MAT_DIR}/M_Hermes_Greybox")
    if mat is None:
        fail(f"material v01 tidak ada: {MAT_DIR}/M_Hermes_Greybox")
        return None
    mis = {}
    for name in MI_TABLE:
        p = f"{MAT_DIR}/MI_Ep01_{name}"
        mi = EAL.load_asset(p)
        if mi is None:
            fail(f"MI v01 tidak ada: {p}")
        else:
            mis[name] = mi
    log(f"material v01 dipakai ulang: M_Hermes_Greybox + {len(mis)} MI (target 15)")
    return mis


# ------------------------------------------------------------------ impor FBX
def import_static_mesh(fbx, name):
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", True)
    ui.set_editor_property("import_as_skeletal", False)
    ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
    ui.set_editor_property("import_materials", False)
    ui.set_editor_property("import_textures", False)
    ui.set_editor_property("import_animations", False)
    sm = ui.get_editor_property("static_mesh_import_data")
    sm.set_editor_property("import_uniform_scale", 1.0)
    sm.set_editor_property("convert_scene", True)
    sm.set_editor_property("combine_meshes", True)
    sm.set_editor_property("auto_generate_collision", False)
    sm.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)

    t = unreal.AssetImportTask()
    t.set_editor_property("filename", fbx)
    t.set_editor_property("destination_path", MESH_DIR)
    t.set_editor_property("destination_name", name)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", False)
    t.set_editor_property("options", ui)
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    try:
        AT.import_asset_tasks([t])
    finally:
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")

    mesh = EAL.load_asset(f"{MESH_DIR}/{name}")
    if not isinstance(mesh, unreal.StaticMesh):
        fail(f"{name} tidak terimpor sebagai StaticMesh")
        return None
    try:
        ns = mesh.get_editor_property("nanite_settings")
        ns.set_editor_property("enabled", False)
        mesh.set_editor_property("nanite_settings", ns)
    except Exception as e:  # noqa: BLE001
        fail(f"{name}: Nanite off gagal ({e})")
    try:
        unreal.EditorStaticMeshLibrary.set_collision_complexity(mesh, unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    except Exception as e:  # noqa: BLE001
        try:
            bs = mesh.get_editor_property("body_setup")
            bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        except Exception as e2:  # noqa: BLE001
            fail(f"{name}: collision UseComplexAsSimple gagal ({e} / {e2})")
    try:
        mesh.set_editor_property("lod_group", "None")
    except Exception:
        pass
    EAL.save_loaded_asset(mesh, only_if_is_dirty=False)
    slots = [str(m.get_editor_property("material_slot_name")) for m in mesh.get_editor_property("static_materials")]
    log(f"{name} terimpor; slot = {slots}")
    return mesh


def assign_slots(mesh, mis):
    mats = mesh.get_editor_property("static_materials")
    for i, m in enumerate(mats):
        slot = str(m.get_editor_property("material_slot_name"))
        key = slot if slot in mis else next((z for z in ZONA_SLOT if slot.endswith(z)), None)
        if key and key in mis:
            mesh.set_material(i, mis[key])
        else:
            fail(f"slot tak dikenal di {mesh.get_name()}: {slot}")
    got = [(str(m.get_editor_property("material_slot_name")), mesh.get_material(i).get_name())
           for i, m in enumerate(mats)]
    log(f"slot material {mesh.get_name()}: {got}")
    EAL.save_loaded_asset(mesh, only_if_is_dirty=False)


# ------------------------------------------------------------------ level
def build_level():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if EAL.does_asset_exist(MAP):
        les.load_level(MAP)
        log(f"level dimuat ulang: {MAP}")
    else:
        if not les.new_level_from_template(MAP, TEMPLATE):
            fail("level baru gagal dibuat dari template")
            return None
        log(f"level baru dibuat: {MAP} (template {TEMPLATE})")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for a in list(eas.get_all_level_actors()):
        if isinstance(a, unreal.StaticMeshActor):
            a.destroy_actor()
            removed += 1
    log(f"hapus {removed} StaticMeshActor bawaan template (lantai)")
    return les


def spawn_mesh(mesh, label, folder):
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a = eas.spawn_actor_from_object(mesh, unreal.Vector(0.0, 0.0, 0.0))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    return a


def set_gamemode():
    gm = EAL.load_asset(GAMEMODE)
    if gm is None:
        fail(f"GameMode {GAMEMODE} tidak ditemukan")
        return
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", gm.generated_class())
    log(f"World Settings: GameMode Override = {GAMEMODE}")


def set_cahaya(nama):
    cfg = CAHAYA[nama]
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ds = [a for a in eas.get_all_level_actors() if isinstance(a, unreal.DirectionalLight)]
    if not ds:
        fail("DirectionalLight tidak ditemukan di level")
        return
    dl = ds[0]
    dl.set_actor_rotation(unreal.Rotator(pitch=float(cfg["pitch"]), yaw=float(cfg["yaw"]), roll=0.0), False)
    c = dl.light_component
    w = cfg["warna"]
    c.set_light_color(unreal.LinearColor(r=float(w[0]), g=float(w[1]), b=float(w[2]), a=1.0))
    c.set_editor_property("intensity", float(cfg["intensitas_lux"]))
    log(f"cahaya '{nama}': pitch={cfg['pitch']} yaw={cfg['yaw']} "
        f"warna=({w[0]:.2f},{w[1]:.2f},{w[2]:.2f}) intensitas={cfg['intensitas_lux']} lux")


# ------------------------------------------------------------------ uji
def test_bounds(actor):
    origin, extent = actor.get_actor_bounds(False)
    size = extent * 2.0
    log("BOUNDS medan (cm): origin=(%.0f, %.0f, %.0f) size=(%.0f, %.0f, %.0f)  Z %.0f..%.0f"
        % (origin.x, origin.y, origin.z, size.x, size.y, size.z, origin.z - extent.z, origin.z + extent.z))
    return origin, extent


def test_trace(ignore_actors):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    log("LINE TRACE 14 TITIK (cm) [mengenai MEDAN; mesh tangga diabaikan]: titik | UE_x UE_y | elev*100 | hit_z | selisih | actor")
    worst = 0.0
    n_ok = 0
    n = 0
    for label, ((x, y), tgt, tol) in M.TITIK_UJI.items():
        n += 1
        ue_x, ue_y = x * 100.0, -y * 100.0
        exp = M.elev(x, y) * 100.0
        start = unreal.Vector(ue_x, ue_y, 20000.0)
        end = unreal.Vector(ue_x, ue_y, -20000.0)
        res = unreal.SystemLibrary.line_trace_single(
            world, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore_actors,
            unreal.DrawDebugTrace.NONE, True)
        tup = res.to_tuple()
        hit = tup[4].z if tup[0] else None
        actor = tup[9].get_actor_label() if tup[0] and tup[9] else "-"
        if hit is None:
            log("  %-26s (%8.0f,%8.0f) %9.1f   MISS" % (label, ue_x, ue_y, exp))
            continue
        d = hit - exp
        worst = max(worst, abs(d))
        if abs(d) <= 5.0:
            n_ok += 1
        log("  %-26s (%8.0f,%8.0f) %9.1f %9.1f %+7.2f %s %s"
            % (label, ue_x, ue_y, exp, hit, d, "OK" if abs(d) <= 5.0 else "!!", actor))
    log(f"line trace (medan): {n_ok}/{n} dalam +/-5 cm; selisih terburuk {worst:.2f} cm")
    return n_ok, n, worst


# ------------------------------------------------------------------ screenshot (bukti laporan)
def render_viewport():
    """Screenshot viewport perspektif (SceneCapture2D) -> Hermes/Art/maps_ep1/v02/Render/V3_viewport.png."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    P = unreal.Vector(8000.0, 90000.0, 65000.0)   # aerial dari selatan (utara di atas)
    T = unreal.Vector(8000.0, -3000.0, 3000.0)
    d = T - P
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = eas.spawn_actor_from_class(
        unreal.SceneCapture2D, P, unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0))
    comp = cap.capture_component2d
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    comp.set_editor_property("fov_angle", 70.0)
    pps = comp.get_editor_property("post_process_settings")
    for key, val in (("override_auto_exposure_method", True),
                     ("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM),
                     ("override_auto_exposure_speed_up", True), ("auto_exposure_speed_up", 200.0),
                     ("override_auto_exposure_speed_down", True), ("auto_exposure_speed_down", 200.0),
                     ("override_auto_exposure_min_brightness", True), ("auto_exposure_min_brightness", -20.0),
                     ("override_auto_exposure_max_brightness", True), ("auto_exposure_max_brightness", 40.0)):
        try:
            pps.set_editor_property(key, val)
        except Exception:  # noqa: BLE001
            pass
    comp.set_editor_property("post_process_settings", pps)
    for _ in range(8):
        comp.capture_scene()
    out_dir = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Render")
    os.makedirs(out_dir, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(world, rt, out_dir.replace("\\", "/"), "V3_viewport")
    png = os.path.join(out_dir, "V3_viewport.png")
    if os.path.exists(os.path.join(out_dir, "V3_viewport")):
        os.replace(os.path.join(out_dir, "V3_viewport"), png)
    px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 960, 540)
    log("screenshot -> %s ; piksel tengah = %.0f,%.0f,%.0f" % (png, px.r, px.g, px.b))
    eas.destroy_actor(cap)


# ------------------------------------------------------------------ main
def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[V3] Editor sedang Play (PIE) — hentikan dulu lalu jalankan ulang")
        return

    for f in ("SM_Ep01_Medan_v02.fbx", "SM_Ep01_Tangga_v02.fbx"):
        if not os.path.exists(os.path.join(EXPORT, f)):
            fail(f"FBX tidak ada: {os.path.join(EXPORT, f)}")
            return

    les = build_level()
    if les is None:
        return
    medan = import_static_mesh(os.path.join(EXPORT, "SM_Ep01_Medan_v02.fbx"), "SM_Ep01_Medan_v02")
    tangga = import_static_mesh(os.path.join(EXPORT, "SM_Ep01_Tangga_v02.fbx"), "SM_Ep01_Tangga_v02")
    if medan is None or tangga is None:
        return

    mis = load_materials()
    if mis is None:
        return
    assign_slots(medan, mis)
    assign_slots(tangga, mis)   # slot "Andesit" -> MI_Ep01_Andesit

    a_medan = spawn_mesh(medan, "SM_Ep01_Medan_v02", "MEDAN")
    a_tangga = spawn_mesh(tangga, "SM_Ep01_Tangga_v02", "MEDAN")
    log("medan & tangga ditaruh di (0,0,0)")

    set_gamemode()
    set_cahaya(CAHAYA_UTAMA)
    les.save_current_level()
    log("level disimpan")

    origin, extent = test_bounds(a_medan)
    n_ok, n, worst = test_trace([a_tangga])
    render_viewport()

    ok_x = abs(extent.x * 2 - 140000) <= 100
    ok_y = abs(extent.y * 2 - 122000) <= 100
    zmin, zmax = origin.z - extent.z, origin.z + extent.z
    log(f"CEK bounds: X 140000={ok_x} Y 122000={ok_y} (Z {zmin:.0f}..{zmax:.0f} cm)")
    ok_trace = (n_ok == n)

    if problems:
        unreal.log_warning(f"[V3] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    log(f"CEK V3: bounds_x={ok_x} bounds_y={ok_y} trace={n_ok}/{n} -> "
        f"{'LULUS' if (ok_x and ok_y and ok_trace and not problems) else 'GAGAL'}")


main()
