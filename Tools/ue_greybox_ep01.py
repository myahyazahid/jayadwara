"""Greybox Ep01_LawangSapta di UE (Unreal Editor Python): membangun SELURUH level dari file data Art/Level/ep01_*.

Dipindah dan digabung dari skrip Hermes V3–V7 (hermes/maps_ep1_v02: maps_ep1_v02_30_level, _40_objek, _50_penanda, _60_kamera,
_72_rute_mesh). Perbedaan: aset ke struktur proyek (bukan sandbox Hermes), alas objek = `alas_m` (elev titik tengah tapak) dan
`pondasi_m` dari JSON (G4, docs/30 bagian 2a), satu skrip untuk semua tahap.

Prasyarat: Art/Export/Level/SM_Ep01_Medan.fbx + SM_Ep01_Tangga.fbx (Art/Scripts/ep01_medan_blender.py), editor terbuka,
BP_JDGameMode_Aksa2 ada, tidak sedang Play.

Membuat / mengisi ulang (aman dijalankan ulang; isi level dibangun ulang, template lighting dipertahankan):
  /Game/Jayadwara/Environment/Ep01Greybox/Materials   M_Greybox + MI_Ep01_<15 warna>
  /Game/Jayadwara/Environment/Ep01Greybox/Meshes      SM_Ep01_Medan, SM_Ep01_Tangga (tanpa Nanite, Use Complex as Simple)
  /Game/Jayadwara/Maps/Ep01_LawangSapta_Greybox       level: medan, objek (tag hancur/adikara/cadangan), pohon + tiang (ISM),
                                                      penanda (PlayerStart, TargetPoint, area, zona TriggerBox), dinding batas,
                                                      kamera C1–C8, cahaya `sore`, GameMode Override Aksa2

Uji (dicetak, akhir: "CEK EP01 GREYBOX: LULUS/GAGAL"): bounds medan, line trace TITIK_UJI, alas semua objek, tag, jumlah pohon/tiang,
penanda/zona/dinding/kamera, tinggi PlayerStart, rute Aksa di mesh nyata (panjang, lereng maks < WalkableFloorAngle), persistensi.
Render kamera C1–C8 ada di Tools/ue_greybox_ep01_render.py (jalankan sebagai invokasi terpisah).

Pakai: python Tools/ue_remote.py Tools/ue_greybox_ep01.py
"""
import json
import math
import os
import sys

import unreal

# ------------------------------------------------------------------ jalur
ENV = "/Game/Jayadwara/Environment/Ep01Greybox"
MESH_DIR = f"{ENV}/Meshes"
MAT_DIR = f"{ENV}/Materials"
MAP = "/Game/Jayadwara/Maps/Ep01_LawangSapta_Greybox"
TEMPLATE = "/Engine/Maps/Templates/Template_Default"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode_Aksa2"
CUBE = "/Engine/BasicShapes/Cube"
PLANE = "/Engine/BasicShapes/Plane"
CONE = "/Engine/BasicShapes/Cone"
CYLINDER = "/Engine/BasicShapes/Cylinder"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EXPORT = os.path.join(REPO, "Art", "Export", "Level")
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep01_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
OBJEK, POHON, POHON_BENTUK, TIANG = DATA["objek"], DATA["pohon_kelompok"], DATA["pohon_bentuk"], DATA["tiang_listrik"]
PENANDA, ZONA, BATAS, KAMERA, CAHAYA = DATA["penanda"], DATA["zona"], DATA["batas_arena"], DATA["kamera"], DATA["cahaya"]
MEDAN = DATA["medan"]
CAHAYA_UTAMA = "sore"
ORTHO_Z_M = 600.0
WARNA_TEKS = {"hijau": (0, 255, 60), "merah": (255, 40, 40), "biru": (40, 140, 255)}
WALL_LABELS = ["BATAS_Arena_Barat", "BATAS_Arena_Timur", "BATAS_Arena_Selatan", "BATAS_Arena_Utara",
               "BATAS_Medan_Barat", "BATAS_Medan_Timur", "BATAS_Medan_Selatan", "BATAS_Medan_Utara"]

MI_TABLE = [
    ("Andesit", (108, 120, 113)), ("Arca", (150, 140, 110)), ("Galian", (181, 88, 47)),
    ("Plato", (128, 132, 118)), ("Sawah", (126, 162, 89)), ("Desa", (199, 166, 121)),
    ("Hutan", (79, 107, 74)), ("Air", (91, 143, 176)), ("Jalan", (150, 120, 90)),
    ("Kayu", (140, 100, 60)), ("Alat", (230, 180, 40)), ("Terpal", (60, 110, 200)),
    ("Kendaraan", (40, 40, 45)), ("Musala", (240, 240, 235)), ("Penanda", (225, 50, 50)),
]
ZONA_SLOT = ["Air", "Galian", "Jalan", "Plato", "Sawah", "Desa", "Hutan"]

EAL = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

problems = []
hasil = {}


def log(m):
    unreal.log(f"[Ep01] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[Ep01] {m}")


def ue(x, y, z):
    """data (meter; x timur, y utara) -> UE (cm; Y = -y)."""
    return unreal.Vector(x * 100.0, -y * 100.0, z * 100.0)


def world():
    return UES.get_editor_world()


def find_by_label(label):
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


def angle_diff(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def srgb_to_linear(v):
    c = v / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


# ================================================================== 1. material
def build_materials():
    path = f"{MAT_DIR}/M_Greybox"
    if EAL.does_asset_exist(path):
        mat = EAL.load_asset(path)
    else:
        mat = AT.create_asset("M_Greybox", MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
        vp = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -350, 0)
        vp.set_editor_property("parameter_name", "Warna")
        vp.set_editor_property("default_value", unreal.LinearColor(0.5, 0.5, 0.5, 1.0))
        if not MEL.connect_material_property(vp, "", unreal.MaterialProperty.MP_BASE_COLOR):
            fail("M_Greybox: Warna -> Base Color gagal")
        rp = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -350, 250)
        rp.set_editor_property("parameter_name", "Roughness")
        rp.set_editor_property("default_value", 0.9)
        if not MEL.connect_material_property(rp, "", unreal.MaterialProperty.MP_ROUGHNESS):
            fail("M_Greybox: Roughness gagal")
        MEL.recompile_material(mat)
        EAL.save_loaded_asset(mat, only_if_is_dirty=False)
    mis = {}
    for name, srgb in MI_TABLE:
        p = f"{MAT_DIR}/MI_Ep01_{name}"
        mi = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(
            f"MI_Ep01_{name}", MAT_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mi.set_editor_property("parent", mat)
        MEL.set_material_instance_vector_parameter_value(
            mi, "Warna", unreal.LinearColor(srgb_to_linear(srgb[0]), srgb_to_linear(srgb[1]), srgb_to_linear(srgb[2]), 1.0))
        EAL.save_loaded_asset(mi, only_if_is_dirty=False)
        mis[name] = mi
    log(f"material: M_Greybox + {len(mis)} MI_Ep01_* (target {len(MI_TABLE)})")
    return mis


# ================================================================== 2. mesh
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
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")   # importer lama (lihat docs/aksa2 jebakan)
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
    EAL.save_loaded_asset(mesh, only_if_is_dirty=False)
    return mesh


def assign_slots(mesh, mis):
    for i, m in enumerate(mesh.get_editor_property("static_materials")):
        slot = str(m.get_editor_property("material_slot_name"))
        key = slot if slot in mis else next((z for z in ZONA_SLOT if slot.endswith(z)), None)
        if key and key in mis:
            mesh.set_material(i, mis[key])
        else:
            fail(f"slot tak dikenal di {mesh.get_name()}: {slot}")
    EAL.save_loaded_asset(mesh, only_if_is_dirty=False)
    log(f"slot material {mesh.get_name()}: " + str([(str(m.get_editor_property('material_slot_name')), mesh.get_material(i).get_name())
                                                    for i, m in enumerate(mesh.get_editor_property('static_materials'))]))


# ================================================================== 3. level
def build_level():
    if EAL.does_asset_exist(MAP):
        LES.load_level(MAP)
        log(f"level dimuat ulang: {MAP}")
    else:
        if not LES.new_level_from_template(MAP, TEMPLATE):
            fail("level baru gagal dibuat dari template")
            return False
        log(f"level baru: {MAP} (template {TEMPLATE})")
    # bersihkan isi lama: hanya jenis actor yang dibuat skrip ini; lighting template (DirectionalLight, Sky*, Fog, Cloud) dipertahankan
    mine = (unreal.StaticMeshActor, unreal.TextRenderActor, unreal.TargetPoint, unreal.TriggerBox, unreal.PlayerStart,
            unreal.CameraActor, unreal.SceneCapture2D)
    n = 0
    for a in list(EAS.get_all_level_actors()):
        if isinstance(a, mine) or a.get_class().get_name() == "Actor":
            a.destroy_actor()
            n += 1
    log(f"hapus {n} actor lama (lantai template + isi build sebelumnya)")
    return True


def spawn_mesh(mesh, label, folder):
    a = EAS.spawn_actor_from_object(mesh, unreal.Vector(0.0, 0.0, 0.0))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    return a


def set_gamemode():
    gm = EAL.load_asset(GAMEMODE)
    if gm is None:
        fail(f"GameMode {GAMEMODE} tidak ditemukan")
        return
    world().get_world_settings().set_editor_property("default_game_mode", gm.generated_class())
    log(f"World Settings: GameMode Override = {GAMEMODE}")


def set_cahaya(nama):
    cfg = CAHAYA[nama]
    ds = [a for a in EAS.get_all_level_actors() if isinstance(a, unreal.DirectionalLight)]
    if not ds:
        fail("DirectionalLight tidak ditemukan")
        return
    dl = ds[0]
    dl.set_actor_rotation(unreal.Rotator(pitch=float(cfg["pitch"]), yaw=float(cfg["yaw"]), roll=0.0), False)
    w = cfg["warna"]
    dl.light_component.set_light_color(unreal.LinearColor(r=float(w[0]), g=float(w[1]), b=float(w[2]), a=1.0))
    dl.light_component.set_editor_property("intensity", float(cfg["intensitas_lux"]))
    log(f"cahaya '{nama}': pitch={cfg['pitch']} yaw={cfg['yaw']} intensitas={cfg['intensitas_lux']} lux")


# ================================================================== 4. objek
def bottom_local(mesh):
    b = mesh.get_bounds()
    return b.origin.z - b.box_extent.z


def alas_data(o):
    """Alas (m) dari data: 'z' absolut, atau `alas_m` (elev titik tengah tapak, dibuat generator) + z_dasar_relatif."""
    if o.get("z") is not None:
        b = float(o["z"])
    elif o["jenis"] == "tangga":
        b = o["dari"][2]
    elif "alas_m" in o:
        b = float(o["alas_m"])
    else:
        fail(f"{o['id']}: tanpa alas_m — jalankan Art/Level/buat_layout_ep01_v02.py")
        b = 0.0
    return b + o.get("z_dasar_relatif", 0.0) + (0.05 if o["jenis"] == "bidang" else 0.0)


def bawah_data(o):
    return alas_data(o) - o.get("pondasi_m", 0.0)


def add_tags(actor, tags):
    if tags:
        try:
            actor.set_editor_property("tags", [unreal.Name(t) for t in tags])
        except Exception as e:  # noqa: BLE001
            fail(f"tag {tags} gagal pada {actor.get_actor_label()}: {e}")


def set_nocollision(actor):
    try:
        actor.static_mesh_component.set_collision_profile_name("NoCollision")
    except Exception:  # noqa: BLE001
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)


def spawn(shape_path, label, loc, yaw_ue, scale_m, mi, folder, tags):
    a = EAS.spawn_actor_from_object(EAL.load_asset(shape_path), loc, unreal.Rotator(pitch=0.0, yaw=yaw_ue, roll=0.0))
    a.set_actor_label(label)
    a.set_actor_scale3d(unreal.Vector(scale_m[0], scale_m[1], scale_m[2]))
    a.set_folder_path(folder)
    if mi is not None:
        a.static_mesh_component.set_material(0, mi)
    add_tags(a, tags)
    return a


def tags_for(o):
    return [t for t, on in (("hancur", o.get("hancur")), ("cadangan", o.get("cadangan")), ("adikara", o.get("milik") == "Adikara")) if on]


def build_objek(o, mi):
    idd, j = o["id"], o["jenis"]
    folder, tags, base, pond = idd.split("_")[0], tags_for(o), alas_data(o), o.get("pondasi_m", 0.0)

    if j == "kotak":
        x, y = o["pos"]
        P, L, T = o["ukuran"]
        return [spawn(CUBE, idd, ue(x, y, base - pond + (T + pond) / 2.0), -o.get("yaw", 0.0), (P, L, T + pond), mi, folder, tags)]

    if j == "rumah":
        x, y = o["pos"]
        P, L, T = o["ukuran"]
        hw = T - 2.0
        yaw_ue = -o.get("yaw", 0.0)
        wall = spawn(CUBE, idd, ue(x, y, base - pond + (hw + pond) / 2.0), yaw_ue, (P, L, hw + pond), mi, folder, tags)
        roof = spawn(CUBE, idd + "_Atap", ue(x, y, base + hw + 1.0), yaw_ue, (P + 0.6, L + 0.6, 2.0), mi, folder, [])
        roof.attach_to_actor(wall, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD,
                             unreal.AttachmentRule.KEEP_WORLD, False)
        return [wall, roof]

    if j == "candi_bertingkat":
        x, y = o["pos"]
        z, actors = base, []
        for i, (p, l, t) in enumerate(o["tingkat"]):
            actors.append(spawn(CUBE, idd if i == 0 else f"{idd}_T{i + 1}", ue(x, y, z + t / 2.0), 0.0, (p, l, t), mi, folder,
                                tags if i == 0 else []))
            z += t
        return actors

    if j == "kerucut":
        x, y = o["pos"]
        d1, d2, t = o["ukuran"]
        loc = unreal.Vector(x * 100.0, -y * 100.0, base * 100.0 - bottom_local(EAL.load_asset(CONE)) * t)
        a = spawn(CONE, idd, loc, -o.get("yaw", 0.0), (d1, d2, t), mi, folder, tags)
        if o.get("tanpa_tabrakan"):
            set_nocollision(a)
        return [a]

    if j == "dinding":
        (ax, ay), (bx, by) = o["dari"], o["ke"]
        dx, dy = (bx - ax) * 100.0, -(by - ay) * 100.0
        length_m = math.hypot(dx, dy) / 100.0
        a = spawn(CUBE, idd, ue((ax + bx) / 2.0, (ay + by) / 2.0, base + o["tinggi"] / 2.0), math.degrees(math.atan2(dy, dx)),
                  (length_m, o["tebal"], o["tinggi"]), mi, folder, tags)
        if o.get("tanpa_tabrakan"):
            set_nocollision(a)
        return [a]

    if j == "bidang":
        x, y = o["pos"]
        P, L = o["ukuran"]
        return [spawn(PLANE, idd, ue(x, y, base), -o.get("yaw", 0.0), (P, L, 1.0), mi, folder, tags)]

    if j == "tangga":
        a = find_by_label("SM_Ep01_Tangga")
        if a is None:
            fail("actor SM_Ep01_Tangga tidak ada")
            return []
        a.set_actor_label(idd)
        a.set_folder_path(folder)
        add_tags(a, tags)
        return [a]

    fail(f"jenis tak dikenal: {idd} / {j}")
    return []


def new_ism(actor, root, nama, mesh, mi, collision):
    params = unreal.AddNewSubobjectParams()
    params.set_editor_property("parent_handle", root)
    params.set_editor_property("new_class", unreal.InstancedStaticMeshComponent)
    h, msg = SDS.add_new_subobject(params)
    if str(msg):
        fail(f"ISM {nama} pada {actor.get_actor_label()}: {msg}")
    SDS.rename_subobject(h, nama)
    comp = next((c for c in actor.get_components_by_class(unreal.InstancedStaticMeshComponent) if c.get_name() == nama), None)
    if comp is None:
        fail(f"ISM {nama} tidak ditemukan di {actor.get_actor_label()}")
        return None
    comp.set_static_mesh(mesh)
    if mi is not None:
        comp.set_material(0, mi)
    try:
        comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    except Exception:  # noqa: BLE001
        pass
    comp.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    return comp


def build_pohon(mis):
    b, t = POHON_BENTUK["batang"], POHON_BENTUK["tajuk"]
    mesh_b, mesh_t = EAL.load_asset(CYLINDER), EAL.load_asset(CONE)
    zb, zt = bottom_local(mesh_b), bottom_local(mesh_t)
    for grup, titik in POHON.items():
        a = EAS.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0))
        a.set_actor_label(f"POHON_{grup}")
        a.set_folder_path("POHON")
        root = SDS.k2_gather_subobject_data_for_instance(a)[0]
        cb = new_ism(a, root, "Batang", mesh_b, mis[b["mi"]], True)
        ct = new_ism(a, root, "Tajuk", mesh_t, mis[t["mi"]], False)
        if cb is None or ct is None:
            continue
        for (x, y, s) in titik:
            e = M.elev(x, y)
            tb, tt = b["tinggi"] * s, t["tinggi"] * s
            cb.add_instance(unreal.Transform(location=unreal.Vector(x * 100.0, -y * 100.0, e * 100.0 - zb * tb),
                                             scale=unreal.Vector(b["diameter"] * s, b["diameter"] * s, tb)))
            ct.add_instance(unreal.Transform(location=unreal.Vector(x * 100.0, -y * 100.0, (e + t["z_relatif"]) * 100.0 - zt * tt),
                                             scale=unreal.Vector(t["diameter"] * s, t["diameter"] * s, tt)))


def build_tiang(mis):
    mesh = EAL.load_asset(CYLINDER)
    z = bottom_local(mesh)
    a = EAS.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0))
    a.set_actor_label("TIANG_Listrik")
    a.set_folder_path("TIANG")
    c = new_ism(a, SDS.k2_gather_subobject_data_for_instance(a)[0], "Tiang", mesh, mis[TIANG["mi"]], True)
    if c is None:
        return
    h = TIANG["tinggi"]
    for (x, y) in TIANG["titik"]:
        c.add_instance(unreal.Transform(location=unreal.Vector(x * 100.0, -y * 100.0, M.elev(x, y) * 100.0 - z * h),
                                        scale=unreal.Vector(TIANG["diameter"], TIANG["diameter"], h)))


# ================================================================== 5. penanda, zona, batas
def text_actor(label, loc, txt, size, folder, warna=None):
    a = EAS.spawn_actor_from_class(unreal.TextRenderActor, loc, unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    tr = a.get_editor_property("text_render")
    tr.set_editor_property("text", unreal.Text(txt))
    tr.set_editor_property("world_size", float(size))
    if warna is not None:
        tr.set_editor_property("text_render_color", unreal.Color(r=warna[0], g=warna[1], b=warna[2], a=255))
    return a


def half_capsule():
    try:
        gm = EAL.load_asset(GAMEMODE)
        pawn_cls = unreal.get_default_object(gm.generated_class()).get_editor_property("default_pawn_class")
        cap = unreal.get_default_object(pawn_cls).get_editor_property("capsule_component")
        return float(cap.get_editor_property("capsule_half_height"))
    except Exception as e:  # noqa: BLE001
        log(f"gagal baca kapsul ({e}); pakai 88 cm")
        return 88.0


def build_penanda(mis, hc):
    start = next(p for p in PENANDA if p["jenis"] == "PlayerStart")
    x, y = start["pos"]
    gx, gy = start["hadap_ke"]
    yaw = math.degrees(math.atan2(-gy * 100.0 + y * 100.0, gx * 100.0 - x * 100.0))
    a = EAS.spawn_actor_from_class(unreal.PlayerStart, ue(x, y, M.elev(x, y) + hc / 100.0), unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0))
    a.set_actor_label("START")
    a.set_folder_path("PENANDA")
    for p in PENANDA:
        x, y = p["pos"]
        gz = M.elev(x, y) * 100.0
        if p["jenis"] == "titik":
            loc = unreal.Vector(x * 100.0, -y * 100.0, gz + 300.0)
            tp = EAS.spawn_actor_from_class(unreal.TargetPoint, loc)
            tp.set_actor_label(p["id"])
            tp.set_folder_path("PENANDA")
            text_actor(p["id"] + "_Teks", loc, p["label"], 150.0, "PENANDA", WARNA_TEKS["biru"] if p["id"].startswith("LORE_") else None)
        elif p["jenis"] == "area":
            r = float(p["radius"])
            loc = unreal.Vector(x * 100.0, -y * 100.0, gz + 10.0)
            a = EAS.spawn_actor_from_object(EAL.load_asset(CYLINDER), loc)
            a.set_actor_label(p["id"])
            a.set_folder_path("PENANDA")
            a.set_actor_scale3d(unreal.Vector(r * 2.0, r * 2.0, 0.2))
            a.static_mesh_component.set_material(0, mis["Penanda"])
            a.static_mesh_component.set_collision_profile_name("NoCollision")
            text_actor(p["id"] + "_Teks", unreal.Vector(loc.x, loc.y, gz + 300.0), p["label"], 150.0, "PENANDA")
    for z in ZONA:
        xa, xb = z["x"]
        ya, yb = z["y"]
        cx, cy = (xa + xb) / 2.0, (ya + yb) / 2.0
        ez = 3000.0
        loc = unreal.Vector(cx * 100.0, -cy * 100.0, M.elev(cx, cy) * 100.0 + ez)
        a = EAS.spawn_actor_from_class(unreal.TriggerBox, loc)
        a.set_actor_label(z["id"])
        a.set_folder_path("ZONA")
        a.get_editor_property("collision_component").set_box_extent(unreal.Vector((xb - xa) * 50.0, (yb - ya) * 50.0, ez), False)
        text_actor(z["id"] + "_Teks", loc, z["label"], 500.0, "ZONA", WARNA_TEKS.get(z.get("warna")))


def build_walls():
    h = float(BATAS["tinggi"])
    xa, xb, ya, yb = BATAS["x"][0], BATAS["x"][1], BATAS["y"][0], BATAS["y"][1]
    X0, X1, Y0, Y1 = MEDAN["x_min"], MEDAN["x_max"], MEDAN["y_min"], MEDAN["y_max"]
    segs = [("BATAS_Arena_Barat", (xa, ya), (xa, yb)), ("BATAS_Arena_Timur", (xb, ya), (xb, yb)),
            ("BATAS_Arena_Selatan", (xa, ya), (xb, ya)), ("BATAS_Arena_Utara", (xa, yb), (xb, yb)),
            ("BATAS_Medan_Barat", (X0, Y0), (X0, Y1)), ("BATAS_Medan_Timur", (X1, Y0), (X1, Y1)),
            ("BATAS_Medan_Selatan", (X0, Y0), (X1, Y0)), ("BATAS_Medan_Utara", (X0, Y1), (X1, Y1))]
    mesh = EAL.load_asset(CUBE)
    for label, (ax, ay), (bx, by) in segs:
        n = max(1, int(math.hypot(bx - ax, by - ay) / 5.0))
        base = min(M.elev(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n + 1))
        dx, dy = (bx - ax) * 100.0, -(by - ay) * 100.0
        a = EAS.spawn_actor_from_object(mesh, ue((ax + bx) / 2.0, (ay + by) / 2.0, base + h / 2.0),
                                        unreal.Rotator(pitch=0.0, yaw=math.degrees(math.atan2(dy, dx)), roll=0.0))
        a.set_actor_label(label)
        a.set_folder_path("BATAS")
        a.set_actor_scale3d(unreal.Vector(math.hypot(dx, dy) / 100.0, 2.0, h))
        a.static_mesh_component.set_collision_profile_name("BlockAll")
        a.set_actor_hidden_in_game(True)


def build_kamera():
    for k in KAMERA:
        x, y = k["pos"]
        if k.get("ortho"):
            z = M.elev(x, y) + ORTHO_Z_M
            rot = unreal.Rotator(pitch=-90.0, yaw=-90.0, roll=0.0)           # lurus ke bawah, utara di atas
        else:
            z = M.elev(x, y) + float(k["tinggi_di_atas_tanah"])
            d = ue(*k["lihat_ke"]) - ue(x, y, z)
            rot = unreal.Rotator(pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x)), roll=0.0)
        a = EAS.spawn_actor_from_class(unreal.CameraActor, ue(x, y, z), rot)
        a.set_actor_label(k["id"])
        a.set_folder_path("KAMERA")
        cc = a.camera_component
        cc.set_editor_property("field_of_view", float(k["fov"]) if not k.get("ortho") else 90.0)
        if k.get("ortho"):
            cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
            cc.set_editor_property("ortho_width", float(k["lebar_ortho"]) * 100.0)


# ================================================================== 6. uji
def trace_medan(x, y, ignore):
    res = unreal.SystemLibrary.line_trace_single(world(), unreal.Vector(x * 100.0, -y * 100.0, 20000.0),
                                                 unreal.Vector(x * 100.0, -y * 100.0, -20000.0),
                                                 unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore, unreal.DrawDebugTrace.NONE, True)
    if res is None:                       # tidak kena apa pun
        return None
    t = res.to_tuple()
    return t[4].z / 100.0 if t[0] else None


def uji_medan(medan, tangga):
    ignore = [a for a in EAS.get_all_level_actors() if a is not medan]    # objek (gerbang, tangga, dll.) tidak boleh ikut terkena trace
    origin, extent = medan.get_actor_bounds(False)
    sx, sy = extent.x * 2, extent.y * 2
    ex, ey = (MEDAN["x_max"] - MEDAN["x_min"]) * 100.0, (MEDAN["y_max"] - MEDAN["y_min"]) * 100.0
    ok_b = abs(sx - ex) <= 100 and abs(sy - ey) <= 100
    log(f"bounds medan (cm): {sx:.0f} x {sy:.0f} (target {ex:.0f} x {ey:.0f}), Z {origin.z - extent.z:.0f}..{origin.z + extent.z:.0f}")
    n_ok = n = 0
    for label, ((x, y), tgt, tol) in M.TITIK_UJI.items():
        n += 1
        z = trace_medan(x, y, ignore)
        d = None if z is None else z - M.elev(x, y)
        ok = d is not None and abs(d) <= 0.05
        n_ok += ok
        log(f"  trace {label:26s} elev={M.elev(x, y):7.2f} hit={z if z is None else round(z, 2)} d={d if d is None else round(d, 3)} {'OK' if ok else '!!'}")
    log(f"line trace: {n_ok}/{n} dalam ±5 cm")
    hasil["bounds"], hasil["trace"] = ok_b, n_ok == n


def uji_objek():
    n_ok = n_hancur = n_adikara = n_cadangan = 0
    for o in OBJEK:
        a = find_by_label(o["id"])
        if a is None:
            fail(f"objek hilang: {o['id']}")
            continue
        origin, extent = a.get_actor_bounds(False)
        bawah = (origin.z - extent.z) / 100.0
        exp = bawah_data(o)
        if abs(bawah - exp) <= 0.05:
            n_ok += 1
        else:
            fail(f"{o['id']}: bawah actor {bawah:.2f} m != data {exp:.2f} m")
        tags = [str(t) for t in a.get_editor_property("tags")]
        n_hancur += "hancur" in tags
        n_adikara += "adikara" in tags
        n_cadangan += "cadangan" in tags
    e_h = sum(1 for o in OBJEK if o.get("hancur"))
    e_a = sum(1 for o in OBJEK if o.get("milik") == "Adikara")
    e_c = sum(1 for o in OBJEK if o.get("cadangan"))
    bad = []
    for o in OBJEK:
        if o["id"] == "DESA_Musala" or o["id"].startswith(("CANDI_", "DESA_RumahLatar")):
            a = find_by_label(o["id"])
            if a is not None and "hancur" in [str(t) for t in a.get_editor_property("tags")]:
                bad.append(o["id"])
    if bad:
        fail(f"seharusnya tanpa tag hancur: {bad}")
    log(f"objek {len(OBJEK)}: bawah sesuai data {n_ok}; tag hancur {n_hancur}/{e_h}, adikara {n_adikara}/{e_a}, cadangan {n_cadangan}/{e_c}")
    hasil["objek"] = n_ok == len(OBJEK) and (n_hancur, n_adikara, n_cadangan) == (e_h, e_a, e_c) and not bad


def hitung_ism():
    nb = nt = ntiang = 0
    for a in EAS.get_all_level_actors():
        lbl = a.get_actor_label()
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if lbl.startswith("POHON_"):
                nb += c.get_instance_count() if c.get_name() == "Batang" else 0
                nt += c.get_instance_count() if c.get_name() == "Tajuk" else 0
            elif lbl == "TIANG_Listrik":
                ntiang += c.get_instance_count()
    return nb, nt, ntiang


def uji_penanda(hc):
    def count(pred):
        return sum(1 for a in EAS.get_all_level_actors() if pred(a))
    ids_area = {p["id"] for p in PENANDA if p["jenis"] == "area"}
    c = (count(lambda a: isinstance(a, unreal.PlayerStart)), count(lambda a: isinstance(a, unreal.TargetPoint)),
         count(lambda a: isinstance(a, unreal.StaticMeshActor) and a.get_actor_label() in ids_area),
         count(lambda a: isinstance(a, unreal.TriggerBox)), count(lambda a: a.get_actor_label() in WALL_LABELS),
         count(lambda a: isinstance(a, unreal.CameraActor)))
    e = (1, sum(1 for p in PENANDA if p["jenis"] == "titik"), len(ids_area), len(ZONA), 8, len(KAMERA))
    log(f"PlayerStart/titik/area/zona/dinding/kamera = {c} (target {e})")
    sx, sy = next(p for p in PENANDA if p["jenis"] == "PlayerStart")["pos"]
    st = find_by_label("START")
    d = st.get_actor_location().z - (M.elev(sx, sy) * 100.0 + hc) if st else 999
    r = st.get_actor_rotation()
    gx, gy = next(p for p in PENANDA if p["jenis"] == "PlayerStart")["hadap_ke"]
    yaw_exp = math.degrees(math.atan2(-gy * 100.0 + sy * 100.0, gx * 100.0 - sx * 100.0))
    yaw_ok = angle_diff(r.yaw, yaw_exp) < 1.0 and abs(r.pitch) < 1.0 and abs(r.roll) < 1.0
    log(f"PlayerStart: Z-hitung d={d:+.1f} cm (toleransi 10); rotasi pitch {r.pitch:.1f} yaw {r.yaw:.1f} roll {r.roll:.1f} (yaw harus {yaw_exp:.1f}): {yaw_ok}")
    hasil["penanda"] = c == e and abs(d) <= 10.0 and yaw_ok


def uji_dinding():
    h = float(BATAS["tinggi"])
    xa, xb, ya, yb = BATAS["x"][0], BATAS["x"][1], BATAS["y"][0], BATAS["y"][1]
    X0, X1, Y0, Y1 = MEDAN["x_min"], MEDAN["x_max"], MEDAN["y_min"], MEDAN["y_max"]
    spek = {"BATAS_Arena_Barat": ("y", yb - ya), "BATAS_Arena_Timur": ("y", yb - ya), "BATAS_Arena_Selatan": ("x", xb - xa),
            "BATAS_Arena_Utara": ("x", xb - xa), "BATAS_Medan_Barat": ("y", Y1 - Y0), "BATAS_Medan_Timur": ("y", Y1 - Y0),
            "BATAS_Medan_Selatan": ("x", X1 - X0), "BATAS_Medan_Utara": ("x", X1 - X0)}
    bad = 0
    for label, (sumbu, panjang) in spek.items():
        o, e = find_by_label(label).get_actor_bounds(False)
        ext = (e.x * 2 / 100.0, e.y * 2 / 100.0, e.z * 2 / 100.0)
        along, thin = (ext[0], ext[1]) if sumbu == "x" else (ext[1], ext[0])
        ok = abs(along - panjang) < 5.0 and thin < 4.0 and abs(ext[2] - h) < 5.0
        bad += not ok
        if not ok:
            log(f"  {label}: bounds {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f} m, harus sepanjang {panjang:.0f} m, tebal ~2 m, tinggi {h:.0f} m")
    log(f"dinding batas: {8 - bad}/8 berarah benar")
    hasil["dinding"] = bad == 0


def uji_kamera():
    bad = 0
    for k in KAMERA:
        a = find_by_label(k["id"])
        r, loc = a.get_actor_rotation(), a.get_actor_location()
        if k.get("ortho"):
            ok = abs(r.pitch + 90.0) < 0.5 and angle_diff(r.yaw, -90.0) < 0.5
        else:
            d = ue(*k["lihat_ke"]) - loc
            ok = angle_diff(r.yaw, math.degrees(math.atan2(d.y, d.x))) < 1.0 and abs(r.pitch - math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))) < 1.0
        bad += not ok
        if not ok:
            log(f"  {k['id']}: arah salah (pitch {r.pitch:.1f} yaw {r.yaw:.1f})")
    log(f"kamera: {len(KAMERA) - bad}/{len(KAMERA)} berarah benar")
    hasil["kamera"] = bad == 0


def uji_rute():
    gm = EAL.load_asset(GAMEMODE)
    cm = unreal.get_default_object(unreal.get_default_object(gm.generated_class()).get_editor_property("default_pawn_class")).get_editor_property("character_movement")
    v = float(cm.get_editor_property("max_walk_speed")) / 100.0
    wa = float(cm.get_editor_property("walkable_floor_angle"))
    ignore = [a for a in EAS.get_all_level_actors() if a.get_actor_label() != "SM_Ep01_Medan"]
    pts = [(float(x), float(y)) for x, y in DATA["rute_aksa"]]
    total = maks = 0.0
    miss = 0
    prev = None
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]))))
        for i in range(n + 1):
            x, y = a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n
            z = trace_medan(x, y, ignore)
            if z is None:
                miss += 1
                continue
            if prev is not None:
                dd = math.hypot(x - prev[0], y - prev[1])
                total += math.hypot(dd, z - prev[2])
                if dd > 1e-9:
                    maks = max(maks, abs(z - prev[2]) / dd)
            prev = (x, y, z)
    sudut = math.degrees(math.atan(maks))
    log(f"rute Aksa di mesh: {total:.1f} m, {total / v:.0f} s @ {v * 100:.0f} cm/s; lereng maks {sudut:.1f} deg (WalkableFloorAngle {wa:.1f}); MISS {miss}")
    hasil["rute"] = sudut < wa and miss == 0


# ================================================================== main
def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Ep01] Editor sedang Play (PIE) — hentikan dulu")
        return
    for f in ("SM_Ep01_Medan.fbx", "SM_Ep01_Tangga.fbx"):
        if not os.path.exists(os.path.join(EXPORT, f)):
            fail(f"FBX tidak ada: {os.path.join(EXPORT, f)} (jalankan Art/Scripts/ep01_medan_blender.py)")
            return
    mis = build_materials()
    if not build_level():
        return
    medan = import_static_mesh(os.path.join(EXPORT, "SM_Ep01_Medan.fbx"), "SM_Ep01_Medan")
    tangga = import_static_mesh(os.path.join(EXPORT, "SM_Ep01_Tangga.fbx"), "SM_Ep01_Tangga")
    if medan is None or tangga is None:
        return
    assign_slots(medan, mis)
    assign_slots(tangga, mis)
    a_medan = spawn_mesh(medan, "SM_Ep01_Medan", "MEDAN")
    a_tangga = spawn_mesh(tangga, "SM_Ep01_Tangga", "MEDAN")

    for o in OBJEK:
        if not build_objek(o, mis[o["mi"]]):
            fail(f"tidak terbangun: {o['id']}")
    build_pohon(mis)
    build_tiang(mis)
    hc = half_capsule()
    build_penanda(mis, hc)
    build_walls()
    build_kamera()
    set_gamemode()
    set_cahaya(CAHAYA_UTAMA)
    LES.save_current_level()
    log("level disimpan")

    uji_medan(a_medan, a_tangga)
    uji_objek()
    nb, nt, ntiang = hitung_ism()
    n_pohon = sum(len(v) for v in POHON.values())
    log(f"pohon batang/tajuk = {nb}/{nt} (target {n_pohon}); tiang = {ntiang} (target {len(TIANG['titik'])})")
    hasil["ism"] = nb == nt == n_pohon and ntiang == len(TIANG["titik"])
    uji_penanda(hc)
    uji_dinding()
    uji_kamera()
    uji_rute()

    LES.load_level(MAP)       # persistensi: muat ulang lalu hitung lagi
    nb2, nt2, ntiang2 = hitung_ism()
    hasil["persist"] = (nb2, nt2, ntiang2) == (nb, nt, ntiang) and find_by_label("START") is not None
    log(f"setelah muat ulang: pohon {nb2}/{nt2}, tiang {ntiang2}, START ada = {find_by_label('START') is not None}")

    ok = all(hasil.values()) and not problems
    log("RINGKAS: " + ", ".join(f"{k}={'ok' if v else 'GAGAL'}" for k, v in hasil.items()))
    for p in problems:
        unreal.log_warning("  - " + p)
    log(f"CEK EP01 GREYBOX: {'LULUS' if ok else 'GAGAL'}")


main()
