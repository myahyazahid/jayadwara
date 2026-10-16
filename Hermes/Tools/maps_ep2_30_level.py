"""MK3 — Level UE + medan (Unreal Editor Python, via Tools/ue_remote.py).

DEST = /Game/Hermes/MapsEp2  (sandbox Hermes)
1. Level baru dari /Engine/Maps/Templates/Template_Default -> DEST/Maps/Test_Hermes_MapsEp2;
   hapus lantai bawaan template.
2. Impor SM_Ep02_Medan.fbx ke DEST/Meshes sebagai Static Mesh (tanpa Nanite, tanpa LOD otomatis).
   Collision: Use Complex as Simple.
3. Buat M_Hermes_Greybox (parameter vektor `Warna` -> Base Color, Roughness 0.9) + 23
   MI_Ep02_<Nama> dari mi_warna JSON (sRGB 0-255 -> linear). Pasang 8 MI ke slot medan per nama slot.
4. Medan di (0, 0, 0). World Settings: GameMode Override = /Game/Jayadwara/Core/BP_JDGameMode
   (hanya dirujuk, tidak diubah).
5. DirectionalLight = setelan cahaya `siang` dari ep02_layout_v02.json.
6. Simpan level + aset DEST satu per satu (TIDAK PERNAH Save All).

Uji (cetak tabel):
- bounds medan (cm): target X 140000, Y 100000; Z dicetak (target -150 .. 1200).
- line trace vertikal di 14 titik uji -> Z = elev(x,y)*100 +/- 5 cm.

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep2_30_level.py
"""
import os
import sys
import json
import math

import unreal

DEST = "/Game/Hermes/MapsEp2"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp2"
LEVEL_NAME = "Test_Hermes_MapsEp2"
MESH_DIR = f"{DEST}/Meshes"
MAT_DIR = f"{DEST}/Materials"
TEMPLATE = "/Engine/Maps/Templates/Template_Default"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EXPORT = os.path.join(REPO, "Hermes", "Art", "maps_ep2", "Export")
RENDER = os.path.join(REPO, "Hermes", "Art", "maps_ep2", "Render")
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402  (elev, zona_material, TITIK_UJI)

with open(os.path.join(REPO, "Art", "Level", "ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
MI_WARNA = DATA["mi_warna"]
CAHAYA = DATA["cahaya"]
CAHAYA_UTAMA = "siang"

# 8 slot medan (nama slot mesh = nama MI tanpa awalan); 15 sisanya untuk objek (MK4)
ZONA_SLOT = ["Air", "Rel", "Jalan", "Gudang", "Paving", "Kampung", "Bantaran", "Sawah"]

EAL = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary

problems = []


def log(m):
    unreal.log(f"[MK3] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[MK3] {m}")


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


# ------------------------------------------------------------------ material (dibuat di DEST)
def make_master():
    path = f"{MAT_DIR}/M_Hermes_Greybox"
    if EAL.does_asset_exist(path):
        mat = EAL.load_asset(path)
        log(f"material master sudah ada: {path}")
        return mat
    factory = unreal.MaterialFactoryNew()
    mat = AT.create_asset("M_Hermes_Greybox", MAT_DIR, unreal.Material, factory)
    if mat is None:
        fail("M_Hermes_Greybox gagal dibuat")
        return None
    vp = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, 0)
    vp.set_editor_property("parameter_name", "Warna")
    vp.set_editor_property("default_value", unreal.LinearColor(0.5, 0.5, 0.5, 1.0))
    MEL.connect_material_property(vp, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rc = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 250)
    rc.set_editor_property("r", 0.9)
    MEL.connect_material_property(rc, "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat, only_if_is_dirty=False)
    log("M_Hermes_Greybox dibuat (param `Warna` -> Base Color, Roughness 0.9)")
    return mat


def make_mi(name, rgb, parent):
    path = f"{MAT_DIR}/MI_Ep02_{name}"
    if EAL.does_asset_exist(path):
        mi = EAL.load_asset(path)
    else:
        factory = unreal.MaterialInstanceConstantFactoryNew()
        mi = AT.create_asset(f"MI_Ep02_{name}", MAT_DIR, unreal.MaterialInstanceConstant, factory)
    if mi is None:
        fail(f"MI_Ep02_{name} gagal dibuat")
        return None
    mi.set_editor_property("parent", parent)
    lin = [srgb_to_linear(v) for v in rgb]
    MEL.set_material_instance_vector_parameter_value(
        mi, "Warna", unreal.LinearColor(lin[0], lin[1], lin[2], 1.0))
    MEL.update_material_instance(mi)
    EAL.save_loaded_asset(mi, only_if_is_dirty=False)
    return mi


def build_materials():
    master = make_master()
    if master is None:
        return None
    mis = {}
    for name, rgb in MI_WARNA.items():
        mi = make_mi(name, rgb, master)
        if mi is not None:
            mis[name] = mi
    log(f"MI dibuat/dimuat: {len(mis)} (target 23)")
    if len(mis) != 23:
        fail(f"jumlah MI {len(mis)} != 23")
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
    log(f"{name} terimpor; {len(slots)} slot = {slots}")
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
    log("LINE TRACE 14 TITIK (cm) [mengenai MEDAN]: titik | UE_x UE_y | elev*100 | hit_z | selisih | actor")
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
    """Screenshot viewport perspektif (SceneCapture2D) -> Hermes/Art/maps_ep2/Render/MK3_perspektif.png."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    P = unreal.Vector(0.0, 130000.0, 80000.0)   # aerial dari selatan (utara di atas)
    T = unreal.Vector(0.0, 10000.0, 2000.0)
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
    out_dir = RENDER
    os.makedirs(out_dir, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(world, rt, out_dir.replace("\\", "/"), "MK3_perspektif")
    png = os.path.join(out_dir, "MK3_perspektif.png")
    if os.path.exists(os.path.join(out_dir, "MK3_perspektif")):
        os.replace(os.path.join(out_dir, "MK3_perspektif"), png)
    px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 960, 540)
    log("screenshot -> %s ; piksel tengah = %.0f,%.0f,%.0f" % (png, px.r, px.g, px.b))
    eas.destroy_actor(cap)


# ------------------------------------------------------------------ main
def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[MK3] Editor sedang Play (PIE) — hentikan dulu lalu jalankan ulang")
        return

    fbx = os.path.join(EXPORT, "SM_Ep02_Medan.fbx")
    if not os.path.exists(fbx):
        fail(f"FBX tidak ada: {fbx}")
        return

    les = build_level()
    if les is None:
        return
    mis = build_materials()
    if mis is None:
        return
    medan = import_static_mesh(fbx, "SM_Ep02_Medan")
    if medan is None:
        return
    assign_slots(medan, mis)

    a_medan = spawn_mesh(medan, "SM_Ep02_Medan", "MEDAN")
    log("medan ditaruh di (0,0,0)")

    set_gamemode()
    set_cahaya(CAHAYA_UTAMA)
    les.save_current_level()
    log("level disimpan")

    origin, extent = test_bounds(a_medan)
    n_ok, n, worst = test_trace([])
    render_viewport()

    ok_x = abs(extent.x * 2 - 140000) <= 100
    ok_y = abs(extent.y * 2 - 100000) <= 100
    zmin, zmax = origin.z - extent.z, origin.z + extent.z
    ok_z = abs(zmin - (-150.0)) <= 5.0 and abs(zmax - 1200.0) <= 5.0
    log(f"CEK bounds: X 140000={ok_x} Y 100000={ok_y} Z -150..1200={ok_z} (Z {zmin:.0f}..{zmax:.0f} cm)")
    ok_trace = (n_ok == n)

    if problems:
        unreal.log_warning(f"[MK3] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    log(f"CEK MK3: bounds_x={ok_x} bounds_y={ok_y} bounds_z={ok_z} trace={n_ok}/{n} -> "
        f"{'LULUS' if (ok_x and ok_y and ok_z and ok_trace and not problems) else 'GAGAL'}")


main()
