"""Greybox Ep02_KampungKali di UE (Unreal Editor Python): membangun SELURUH level dari file data Art/Level/ep02_*.

Dipindah dan digabung dari skrip Hermes MK3–MK7 (hermes/maps_ep2: maps_ep2_30_level, _40_objek, _41_kelompok, _50_penanda, _60_kamera,
_70_rute) setelah review 17 Okt 2026 (docs/31 bagian 2a, keputusan K1–K4). Beda dari versi Hermes: aset ke struktur proyek, alas objek =
`alas_m` + `pondasi_m` dari JSON, GameMode Aksa2, SEMUA rotasi dibuat dengan nama argumen (urutan posisional unreal.Rotator = roll, pitch, yaw;
bug itu membalik 4 dinding batas dan arah START di versi Hermes), jumlah target diturunkan dari data (bukan angka keras), dan uji tambahan:
arah dinding batas, arah START, arah kamera, gang utama terbuka.

Prasyarat: Art/Export/Level/SM_Ep02_Medan.fbx (Art/Scripts/ep02_medan_blender.py), editor terbuka, BP_JDGameMode_Aksa2 ada, tidak sedang Play.

Membuat / mengisi ulang (aman dijalankan ulang; isi level dibangun ulang, template lighting dipertahankan):
  /Game/Jayadwara/Environment/Ep02Greybox/Materials   M_Greybox + MI_Ep02_<semua warna di mi_warna>
  /Game/Jayadwara/Environment/Ep02Greybox/Meshes      SM_Ep02_Medan (tanpa Nanite, Use Complex as Simple)
  /Game/Jayadwara/Maps/Ep02_KampungKali_Greybox       level: medan, objek (tag hancur/penalti/blok_chaos/atap_naik/adikara/curian),
                                                      kelompok ISM (rumah ribuan), pohon + tiang (ISM), penanda, zona, dinding batas,
                                                      kamera C1–C8, cahaya `siang`, GameMode Override Aksa2

Uji (dicetak, akhir: "CEK EP02 GREYBOX: LULUS/GAGAL"). Render kamera: Tools/ue_greybox_ep02_render.py (invokasi terpisah).
Pakai: python Tools/ue_remote.py Tools/ue_greybox_ep02.py
"""
import json
import math
import os
import sys

import unreal

# ------------------------------------------------------------------ jalur
ENV = "/Game/Jayadwara/Environment/Ep02Greybox"
MESH_DIR = f"{ENV}/Meshes"
MAT_DIR = f"{ENV}/Materials"
MAP = "/Game/Jayadwara/Maps/Ep02_KampungKali_Greybox"
LEVEL_NAME = "Ep02_KampungKali_Greybox"
TEMPLATE = "/Engine/Maps/Templates/Template_Default"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode_Aksa2"
CUBE = "/Engine/BasicShapes/Cube"
PLANE = "/Engine/BasicShapes/Plane"
CONE = "/Engine/BasicShapes/Cone"
CYLINDER = "/Engine/BasicShapes/Cylinder"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EXPORT = os.path.join(REPO, "Art", "Export", "Level")
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art", "Level", "ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
OBJEK, KELOMPOK = DATA["objek"], DATA["kelompok"]
POHON, POHON_BENTUK, TIANG = DATA["pohon_kelompok"], DATA["pohon_bentuk"], DATA["tiang_listrik"]
PENANDA, ZONA, BATAS, KAMERA, CAHAYA = DATA["penanda"], DATA["zona"], DATA["batas_arena"], DATA["kamera"], DATA["cahaya"]
MEDAN, MI_WARNA = DATA["medan"], DATA["mi_warna"]
CAHAYA_UTAMA = "siang"
ZONA_SLOT = ["Air", "Rel", "Jalan", "Gudang", "Paving", "Kampung", "Bantaran", "Sawah"]
WARNA_TEKS = {"hijau": (0, 255, 60), "merah": (255, 40, 40), "ungu": (170, 40, 255)}
WALL_LABELS = ["BATAS_Arena_Barat", "BATAS_Arena_Timur", "BATAS_Arena_Selatan", "BATAS_Arena_Utara",
               "BATAS_Medan_Barat", "BATAS_Medan_Timur", "BATAS_Medan_Selatan", "BATAS_Medan_Utara"]
ORTHO_Z_M = 600.0

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
    unreal.log(f"[Ep02] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[Ep02] {m}")


def ue(x, y, z):
    """data (meter; x timur, y utara) -> UE (cm; Y = -y)."""
    return unreal.Vector(x * 100.0, -y * 100.0, z * 100.0)


def rot(pitch=0.0, yaw=0.0, roll=0.0):
    """Selalu dengan nama argumen (urutan posisional unreal.Rotator = roll, pitch, yaw)."""
    return unreal.Rotator(pitch=float(pitch), yaw=float(yaw), roll=float(roll))


def world():
    return UES.get_editor_world()


def find_by_label(label):
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


def srgb_to_linear(v):
    c = v / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def angle_diff(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def trace(x, y, z0_cm, z1_cm, ignore=None):
    """Line trace vertikal; None bila tidak kena (line_trace_single mengembalikan None, bukan HitResult kosong)."""
    res = unreal.SystemLibrary.line_trace_single(world(), unreal.Vector(x * 100.0, -y * 100.0, z0_cm), unreal.Vector(x * 100.0, -y * 100.0, z1_cm),
                                                 unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore or [], unreal.DrawDebugTrace.NONE, True)
    if res is None:
        return None
    t = res.to_tuple()
    return t[4].z / 100.0 if t[0] else None


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
    for name, rgb in MI_WARNA.items():
        p = f"{MAT_DIR}/MI_Ep02_{name}"
        mi = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(
            f"MI_Ep02_{name}", MAT_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mi.set_editor_property("parent", mat)
        MEL.set_material_instance_vector_parameter_value(
            mi, "Warna", unreal.LinearColor(srgb_to_linear(rgb[0]), srgb_to_linear(rgb[1]), srgb_to_linear(rgb[2]), 1.0))
        EAL.save_loaded_asset(mi, only_if_is_dirty=False)
        mis[name] = mi
    log(f"material: M_Greybox + {len(mis)} MI_Ep02_* (= jumlah warna di mi_warna)")
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
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")   # importer lama
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
    log("slot material " + mesh.get_name() + ": " + str([str(m.get_editor_property("material_slot_name"))
                                                         for m in mesh.get_editor_property("static_materials")]))


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
    mine = (unreal.StaticMeshActor, unreal.TextRenderActor, unreal.TargetPoint, unreal.TriggerBox, unreal.PlayerStart,
            unreal.CameraActor, unreal.SceneCapture2D)
    n = 0
    for a in list(EAS.get_all_level_actors()):
        if isinstance(a, mine) or a.get_class().get_name() == "Actor":
            a.destroy_actor()
            n += 1
    log(f"hapus {n} actor lama (lantai template + isi build sebelumnya)")
    return True


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
    dl.set_actor_rotation(rot(cfg["pitch"], cfg["yaw"], 0.0), False)
    w = cfg["warna"]
    dl.light_component.set_light_color(unreal.LinearColor(r=float(w[0]), g=float(w[1]), b=float(w[2]), a=1.0))
    dl.light_component.set_editor_property("intensity", float(cfg["intensitas_lux"]))
    log(f"cahaya '{nama}': pitch={cfg['pitch']} yaw={cfg['yaw']} intensitas={cfg['intensitas_lux']} lux")


# ================================================================== 4. objek
def bottom_local(mesh):
    b = mesh.get_bounds()
    return b.origin.z - b.box_extent.z


def alas_data(o):
    """Alas (m): 'z' absolut, atau `alas_m` (elev titik tengah tapak, dibuat generator) + z_dasar_relatif (+5 cm untuk bidang tanpa z)."""
    if o.get("z") is not None:
        b = float(o["z"])
    elif "alas_m" in o:
        b = float(o["alas_m"])
    else:
        fail(f"{o['id']}: tanpa alas_m — jalankan Art/Level/buat_layout_ep02_v02.py")
        b = 0.0
    return b + o.get("z_dasar_relatif", 0.0) + (0.05 if o["jenis"] == "bidang" and o.get("z") is None else 0.0)


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


def spawn(shape_path, label, loc, yaw_ue, scale_m, mi, folder, tags, collision=True):
    a = EAS.spawn_actor_from_object(EAL.load_asset(shape_path), loc, rot(0.0, yaw_ue, 0.0))
    a.set_actor_label(label)
    a.set_actor_scale3d(unreal.Vector(scale_m[0], scale_m[1], scale_m[2]))
    a.set_folder_path(folder)
    if mi is not None:
        a.static_mesh_component.set_material(0, mi)
    if not collision:
        set_nocollision(a)
    add_tags(a, tags)
    return a


def new_component(actor, root, cls, nama, mesh, mi, collision):
    params = unreal.AddNewSubobjectParams()
    params.set_editor_property("parent_handle", root)
    params.set_editor_property("new_class", cls)
    h, msg = SDS.add_new_subobject(params)
    if str(msg):
        fail(f"{nama} pada {actor.get_actor_label()}: {msg}")
    SDS.rename_subobject(h, nama)
    comp = next((c for c in actor.get_components_by_class(cls) if c.get_name() == nama), None)
    if comp is None:
        fail(f"{nama} tidak ditemukan di {actor.get_actor_label()}")
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


def tags_for(o):
    tags = []
    if o.get("hancur"):
        tags.append("hancur")
    tags += {"tinggi": ["penalti_tinggi"], "normal": ["penalti_normal"], "tanpa": ["tanpa_penalti"]}.get(o.get("penalti"), [])
    if o.get("blok_chaos"):
        tags += ["blok_chaos", o["blok_chaos"]]
    if o.get("tukar_puing"):
        tags.append("tukar_puing")
    if o.get("atap_naik"):
        tags.append("atap_naik")
    if o.get("milik") == "Adikara":
        tags.append("adikara")
    if o.get("curian"):
        tags.append("curian")
    return tags


def build_objek(o, mis):
    idd, j = o["id"], o["jenis"]
    folder, tags, base, pond = idd.split("_")[0], tags_for(o), alas_data(o), o.get("pondasi_m", 0.0)
    mi = mis.get(o["mi"])
    col = not o.get("tanpa_tabrakan")

    if j == "kotak":
        x, y = o["pos"]
        P, L, T = o["ukuran"]
        return spawn(CUBE, idd, ue(x, y, base - pond + (T + pond) / 2.0), -o.get("yaw", 0.0), (P, L, T + pond), mi, folder, tags, col)

    if j == "rumah":     # 1 actor (dinding = root StaticMeshComponent) + komponen anak "Atap" (bare Actor memunculkan billboard yang mengotori bounds)
        x, y = o["pos"]
        P, L, T = o["ukuran"]
        hw = T - 0.5
        sz = hw + pond
        a = spawn(CUBE, idd, ue(x, y, base - pond + sz / 2.0), -o.get("yaw", 0.0), (P, L, sz), mi, folder, tags, col)
        hb = SDS.k2_gather_subobject_data_for_instance(a)
        ca = new_component(a, hb[0], unreal.StaticMeshComponent, "Atap", EAL.load_asset(CUBE), mis.get(o.get("mi_atap")), col)
        if ca is not None:
            ca.set_relative_location(unreal.Vector(0.0, 0.0, (hw / 2.0 + 0.25 + pond / 2.0) / sz * 100.0), False, False)
            ca.set_relative_scale3d(unreal.Vector((P + 0.4) / P, (L + 0.4) / L, 0.5 / sz))
        return a

    if j == "bidang":
        x, y = o["pos"]
        P, L = o["ukuran"]
        return spawn(PLANE, idd, ue(x, y, base), -o.get("yaw", 0.0), (P, L, 1.0), mi, folder, tags, col)

    if j == "dinding":
        (ax, ay), (bx, by) = o["dari"], o["ke"]
        dx, dy = (bx - ax) * 100.0, -(by - ay) * 100.0
        return spawn(CUBE, idd, ue((ax + bx) / 2.0, (ay + by) / 2.0, base + o["tinggi"] / 2.0), math.degrees(math.atan2(dy, dx)),
                     (math.hypot(dx, dy) / 100.0, o["tebal"], o["tinggi"]), mi, folder, tags, col)

    if j == "kerucut":
        x, y = o["pos"]
        d1, d2, t = o["ukuran"]
        loc = unreal.Vector(x * 100.0, -y * 100.0, base * 100.0 - bottom_local(EAL.load_asset(CONE)) * t)
        return spawn(CONE, idd, loc, -o.get("yaw", 0.0), (d1, d2, t), mi, folder, tags, col)

    fail(f"jenis tak dikenal: {idd} / {j}")
    return None


def build_kelompok(k, mis):
    idd, bentuk = k["id"], k["bentuk"]
    z_abs = k.get("z")
    a = EAS.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0))
    a.set_actor_label(idd)
    a.set_folder_path(idd.split("_")[0])
    add_tags(a, tags_for(k))
    root = SDS.k2_gather_subobject_data_for_instance(a)[0]
    mesh = EAL.load_asset(CUBE)
    ISM = unreal.InstancedStaticMeshComponent
    if bentuk == "rumah":
        cd = new_component(a, root, ISM, "Dinding", mesh, mis[k["mi"]], True)
        ca = new_component(a, root, ISM, "Atap", mesh, mis[k["mi_atap"]], True)
        if cd is None or ca is None:
            return
        for (x, y, P, L, T, yaw) in k["item"]:
            base = z_abs if z_abs is not None else M.elev(x, y)          # K3: titik tengah (selisih ke titik terendah maks 0,11 m)
            hw = T - 0.5
            cd.add_instance(unreal.Transform(location=ue(x, y, base + hw / 2.0), rotation=rot(0.0, -yaw, 0.0), scale=unreal.Vector(P, L, hw)))
            ca.add_instance(unreal.Transform(location=ue(x, y, base + hw + 0.25), rotation=rot(0.0, -yaw, 0.0),
                                             scale=unreal.Vector(P + 0.4, L + 0.4, 0.5)))
    else:
        c = new_component(a, root, ISM, "Badan", mesh, mis[k["mi"]], True)
        if c is None:
            return
        for (x, y, P, L, T, yaw) in k["item"]:
            base = z_abs if z_abs is not None else M.elev(x, y)
            c.add_instance(unreal.Transform(location=ue(x, y, base + T / 2.0), rotation=rot(0.0, -yaw, 0.0), scale=unreal.Vector(P, L, T)))


def build_pohon(mis):
    b, t = POHON_BENTUK["batang"], POHON_BENTUK["tajuk"]
    mesh_b, mesh_t = EAL.load_asset(CYLINDER), EAL.load_asset(CONE)
    zb, zt = bottom_local(mesh_b), bottom_local(mesh_t)
    ISM = unreal.InstancedStaticMeshComponent
    for grup, titik in POHON.items():
        a = EAS.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0))
        a.set_actor_label(f"POHON_{grup}")
        a.set_folder_path("POHON")
        root = SDS.k2_gather_subobject_data_for_instance(a)[0]
        cb = new_component(a, root, ISM, "Batang", mesh_b, mis[b["mi"]], True)
        ct = new_component(a, root, ISM, "Tajuk", mesh_t, mis[t["mi"]], False)
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
    c = new_component(a, SDS.k2_gather_subobject_data_for_instance(a)[0], unreal.InstancedStaticMeshComponent, "Tiang", mesh, mis[TIANG["mi"]], True)
    if c is None:
        return
    h = TIANG["tinggi"]
    for (x, y) in TIANG["titik"]:
        c.add_instance(unreal.Transform(location=unreal.Vector(x * 100.0, -y * 100.0, M.elev(x, y) * 100.0 - z * h),
                                        scale=unreal.Vector(TIANG["diameter"], TIANG["diameter"], h)))


# ================================================================== 5. penanda, zona, batas
def text_actor(label, loc, txt, size, folder, warna=None):
    a = EAS.spawn_actor_from_class(unreal.TextRenderActor, loc, rot(0.0, 0.0, 0.0))
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


def start_yaw(p):
    x, y = p["pos"]
    gx, gy = p["hadap_ke"]
    return math.degrees(math.atan2(-gy * 100.0 + y * 100.0, gx * 100.0 - x * 100.0))


def titik_alas(p):
    """Alas titik (m): z absolut; `di_atap` -> permukaan pertama trace dari z 60 m (puncak atap); lainnya elev."""
    if "z" in p:
        return float(p["z"])
    if p.get("di_atap"):
        z = trace(p["pos"][0], p["pos"][1], 6000.0, -200.0)
        return z if z is not None else M.elev(p["pos"][0], p["pos"][1])
    return M.elev(p["pos"][0], p["pos"][1])


def build_penanda(mis, hc):
    for p in PENANDA:
        x, y = p["pos"]
        if p["jenis"] == "PlayerStart":
            a = EAS.spawn_actor_from_class(unreal.PlayerStart, ue(x, y, M.elev(x, y) + hc / 100.0), rot(0.0, start_yaw(p), 0.0))
            a.set_actor_label("START")
            a.set_folder_path("PENANDA")
        elif p["jenis"] == "titik":
            loc = unreal.Vector(x * 100.0, -y * 100.0, titik_alas(p) * 100.0 + 300.0)
            tp = EAS.spawn_actor_from_class(unreal.TargetPoint, loc)
            tp.set_actor_label(p["id"])
            tp.set_folder_path("PENANDA")
            text_actor(p["id"] + "_Teks", loc, p["label"], 150.0, "PENANDA")
        elif p["jenis"] == "area":
            r = float(p["radius"])
            gz = M.elev(x, y) * 100.0
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


def wall_specs():
    h = float(BATAS["tinggi"])
    xa, xb, ya, yb = BATAS["x"][0], BATAS["x"][1], BATAS["y"][0], BATAS["y"][1]
    X0, X1, Y0, Y1 = MEDAN["x_min"], MEDAN["x_max"], MEDAN["y_min"], MEDAN["y_max"]
    return h, [("BATAS_Arena_Barat", (xa, ya), (xa, yb)), ("BATAS_Arena_Timur", (xb, ya), (xb, yb)),
               ("BATAS_Arena_Selatan", (xa, ya), (xb, ya)), ("BATAS_Arena_Utara", (xa, yb), (xb, yb)),
               ("BATAS_Medan_Barat", (X0, Y0), (X0, Y1)), ("BATAS_Medan_Timur", (X1, Y0), (X1, Y1)),
               ("BATAS_Medan_Selatan", (X0, Y0), (X1, Y0)), ("BATAS_Medan_Utara", (X0, Y1), (X1, Y1))]


def build_walls():
    h, segs = wall_specs()
    mesh = EAL.load_asset(CUBE)
    for label, (ax, ay), (bx, by) in segs:
        n = max(1, int(math.hypot(bx - ax, by - ay) / 5.0))
        base = min(M.elev(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n + 1))
        dx, dy = (bx - ax) * 100.0, -(by - ay) * 100.0
        a = EAS.spawn_actor_from_object(mesh, ue((ax + bx) / 2.0, (ay + by) / 2.0, base + h / 2.0), rot(0.0, math.degrees(math.atan2(dy, dx)), 0.0))
        a.set_actor_label(label)
        a.set_folder_path("BATAS")
        a.set_actor_scale3d(unreal.Vector(math.hypot(dx, dy) / 100.0, 2.0, h))
        a.static_mesh_component.set_collision_profile_name("BlockAll")
        a.set_actor_hidden_in_game(True)


def cam_base(x, y):
    """Alas kamera (m): permukaan yang diinjak (trace dari z 60 m); tanah bila trace kena struktur >5 m di atas tanah (overhang)."""
    tz, gz = trace(x, y, 6000.0, -200.0), M.elev(x, y)
    if tz is None or tz - gz > 5.0:
        return gz
    return tz


def cam_rotasi(k, z):
    if k.get("ortho"):
        return rot(-90.0, -90.0, 0.0)                    # lurus ke bawah, yaw -90: utara di atas (sama dengan denah docs/31)
    x, y = k["pos"]
    d = ue(*k["lihat_ke"]) - ue(x, y, z)
    return rot(math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), math.degrees(math.atan2(d.y, d.x)), 0.0)


def build_kamera():
    for k in KAMERA:
        x, y = k["pos"]
        z = (M.elev(x, y) + ORTHO_Z_M) if k.get("ortho") else cam_base(x, y) + float(k["tinggi_di_atas_tanah"])
        a = EAS.spawn_actor_from_class(unreal.CameraActor, ue(x, y, z), cam_rotasi(k, z))
        a.set_actor_label(k["id"])
        a.set_folder_path("KAMERA")
        cc = a.camera_component
        cc.set_editor_property("field_of_view", float(k["fov"]) if not k.get("ortho") else 90.0)
        if k.get("ortho"):
            cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
            cc.set_editor_property("ortho_width", float(k["lebar_ortho"]) * 100.0)


# ================================================================== 6. uji
def uji_medan(medan):
    ignore = [a for a in EAS.get_all_level_actors() if a is not medan]
    origin, extent = medan.get_actor_bounds(False)
    sx, sy = extent.x * 2, extent.y * 2
    ex, ey = (MEDAN["x_max"] - MEDAN["x_min"]) * 100.0, (MEDAN["y_max"] - MEDAN["y_min"]) * 100.0
    log(f"bounds medan (cm): {sx:.0f} x {sy:.0f} (data {ex:.0f} x {ey:.0f}), Z {origin.z - extent.z:.0f}..{origin.z + extent.z:.0f}")
    n_ok = 0
    for label, ((x, y), tgt, tol) in M.TITIK_UJI.items():
        z = trace(x, y, 20000.0, -20000.0, ignore)
        ok = z is not None and abs(z - M.elev(x, y)) <= 0.05
        n_ok += ok
        if not ok:
            log(f"  trace {label}: elev={M.elev(x, y):.2f} hit={z}")
    log(f"line trace TITIK_UJI: {n_ok}/{len(M.TITIK_UJI)} dalam ±5 cm")
    hasil["bounds"] = abs(sx - ex) <= 100 and abs(sy - ey) <= 100
    hasil["trace"] = n_ok == len(M.TITIK_UJI)


def uji_objek():
    n_ok = 0
    cnt = dict.fromkeys(("hancur", "penalti_tinggi", "penalti_normal", "tanpa_penalti", "blok_chaos", "atap_naik", "adikara", "curian"), 0)
    blok = {}
    for o in OBJEK:
        a = find_by_label(o["id"])
        if a is None:
            fail(f"objek hilang: {o['id']}")
            continue
        origin, extent = a.get_actor_bounds(False)
        bawah = (origin.z - extent.z) / 100.0
        if abs(bawah - bawah_data(o)) <= 0.05:
            n_ok += 1
        else:
            fail(f"{o['id']}: bawah actor {bawah:.2f} m != data {bawah_data(o):.2f} m")
        tags = [str(t) for t in a.get_editor_property("tags")]
        for t in cnt:
            cnt[t] += t in tags
        if "blok_chaos" in tags:
            for t in tags:
                if t.startswith("BLOK"):
                    blok[t] = blok.get(t, 0) + 1
    exp = dict.fromkeys(cnt, 0)
    for o in OBJEK:
        for t in tags_for(o):
            if t in exp:
                exp[t] += 1
    exp_blok = {}
    for o in OBJEK:
        if o.get("blok_chaos"):
            exp_blok[o["blok_chaos"]] = exp_blok.get(o["blok_chaos"], 0) + 1
    log(f"objek {len(OBJEK)}: bawah sesuai data {n_ok}; tag {cnt} (data {exp}); blok_chaos per deret {dict(sorted(blok.items()))}")
    hasil["objek"] = n_ok == len(OBJEK) and cnt == exp and blok == exp_blok


def hitung_ism():
    jml = {"kelompok": {}, "batang": 0, "tajuk": 0, "tiang": 0, "pohon_actor": 0}
    for a in EAS.get_all_level_actors():
        lbl = a.get_actor_label()
        comps = a.get_components_by_class(unreal.InstancedStaticMeshComponent)
        if lbl.startswith("POHON_"):
            jml["pohon_actor"] += 1
            for c in comps:
                jml["batang" if c.get_name() == "Batang" else "tajuk"] += c.get_instance_count()
        elif lbl == "TIANG_Listrik":
            jml["tiang"] = sum(c.get_instance_count() for c in comps)
        elif comps:
            jml["kelompok"][lbl] = {c.get_name(): c.get_instance_count() for c in comps}
    return jml


def uji_ism(jml):
    ok = True
    for k in KELOMPOK:
        got = jml["kelompok"].get(k["id"], {})
        n = len(k["item"])
        want = {"Dinding": n, "Atap": n} if k["bentuk"] == "rumah" else {"Badan": n}
        if got != want:
            fail(f"{k['id']}: instance {got} != {want}")
            ok = False
    n_pohon = sum(len(v) for v in POHON.values())
    ok = ok and jml["batang"] == jml["tajuk"] == n_pohon and jml["pohon_actor"] == len(POHON) and jml["tiang"] == len(TIANG["titik"])
    log(f"kelompok {sum(len(k['item']) for k in KELOMPOK)} item/{len(KELOMPOK)} actor; pohon {jml['batang']}/{jml['tajuk']} (data {n_pohon}); "
        f"tiang {jml['tiang']} (data {len(TIANG['titik'])})")
    hasil["ism"] = ok


def uji_penanda(hc):
    def count(pred):
        return sum(1 for a in EAS.get_all_level_actors() if pred(a))
    ids_area = {p["id"] for p in PENANDA if p["jenis"] == "area"}
    got = (count(lambda a: isinstance(a, unreal.PlayerStart)), count(lambda a: isinstance(a, unreal.TargetPoint)),
           count(lambda a: isinstance(a, unreal.StaticMeshActor) and a.get_actor_label() in ids_area),
           count(lambda a: isinstance(a, unreal.TriggerBox)), count(lambda a: a.get_actor_label() in WALL_LABELS),
           count(lambda a: isinstance(a, unreal.CameraActor)))
    want = (1, sum(1 for p in PENANDA if p["jenis"] == "titik"), len(ids_area), len(ZONA), 8, len(KAMERA))
    p0 = next(p for p in PENANDA if p["jenis"] == "PlayerStart")
    st = find_by_label("START")
    r = st.get_actor_rotation()
    yaw_ok = angle_diff(r.yaw, start_yaw(p0)) < 1.0 and abs(r.pitch) < 1.0 and abs(r.roll) < 1.0
    dz = st.get_actor_location().z - (M.elev(*p0["pos"]) * 100.0 + hc)
    log(f"PlayerStart/titik/area/zona/dinding/kamera = {got} (data {want}); START yaw {r.yaw:.1f} (harus {start_yaw(p0):.1f}) "
        f"pitch {r.pitch:.1f} roll {r.roll:.1f}; Z d={dz:+.1f} cm")
    atap = [p for p in PENANDA if p.get("di_atap")]
    atap_ok = all(find_by_label(p["id"]).get_actor_location().z / 100.0 - 3.0 > M.elev(*p["pos"]) + 2.5 for p in atap)
    log(f"titik di_atap ({[p['id'] for p in atap]}) di atas atap (>= tanah + 2,5 m): {atap_ok}")
    hasil["penanda"] = got == want and yaw_ok and abs(dz) <= 10.0 and atap_ok


def uji_dinding():
    h, segs = wall_specs()
    bad = 0
    for label, (ax, ay), (bx, by) in segs:
        o, e = find_by_label(label).get_actor_bounds(False)
        ext = (e.x * 2 / 100.0, e.y * 2 / 100.0, e.z * 2 / 100.0)
        panjang = abs(bx - ax) if abs(bx - ax) > abs(by - ay) else abs(by - ay)
        along, thin = (ext[0], ext[1]) if abs(bx - ax) > abs(by - ay) else (ext[1], ext[0])
        ok = abs(along - panjang) < 5.0 and thin < 4.0 and abs(ext[2] - h) < 5.0
        bad += not ok
        if not ok:
            log(f"  {label}: bounds {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f} m, harus sepanjang {panjang:.0f} m, tebal ~2 m, tinggi {h:.0f} m")
    log(f"dinding batas: {8 - bad}/8 berarah benar (memanjang sesuai sisi, tebal ~2 m, tinggi {h:.0f} m)")
    hasil["dinding"] = bad == 0


def uji_kamera():
    bad = 0
    for k in KAMERA:
        a = find_by_label(k["id"])
        r, loc = a.get_actor_rotation(), a.get_actor_location()
        if k.get("ortho"):
            ok = abs(r.pitch + 90.0) < 0.5 and angle_diff(r.yaw, -90.0) < 0.5 and \
                a.camera_component.get_editor_property("ortho_width") >= (MEDAN["y_max"] - MEDAN["y_min"]) * 16.0 / 9.0 * 100.0
        else:
            d = ue(*k["lihat_ke"]) - loc
            ok = angle_diff(r.yaw, math.degrees(math.atan2(d.y, d.x))) < 1.0 and abs(r.pitch - math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))) < 1.0
        bad += not ok
        if not ok:
            log(f"  {k['id']}: arah salah (pitch {r.pitch:.1f} yaw {r.yaw:.1f})")
    log(f"kamera: {len(KAMERA) - bad}/{len(KAMERA)} berarah benar (C5: lurus ke bawah, utara di atas, lebar >= tinggi medan x 16/9)")
    hasil["kamera"] = bad == 0


def uji_gang():
    medan = find_by_label("SM_Ep02_Medan")
    hits = 0
    for i in range(186):
        y0, y1 = 138.0 - i, 137.0 - i
        r = unreal.SystemLibrary.line_trace_single(world(), ue(M.GANG_UTAMA_X, y0, M.elev(M.GANG_UTAMA_X, y0) + 1.0),
                                                   ue(M.GANG_UTAMA_X, y1, M.elev(M.GANG_UTAMA_X, y1) + 1.0),
                                                   unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [medan], unreal.DrawDebugTrace.NONE, True)
        hits += bool(r is not None and r.to_tuple()[0])
    log(f"gang utama x={M.GANG_UTAMA_X:g} (y 138..-48) 1 m di atas tanah: {'BEBAS' if hits == 0 else f'TERHALANG di {hits} tempat'}")
    hasil["gang"] = hits == 0


def uji_rute():
    v = DATA["kecepatan_rute_ms"]
    ok = True
    for nama, kunci in (("rute_investigasi", "investigasi"), ("rute_kejar", "kejar")):
        pts, target = DATA[nama], DATA["rute_panjang_m"][kunci]
        tot, prev, miss = 0.0, None, 0
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = max(1, int(round(math.hypot(bx - ax, by - ay))))
            for j in range(n + 1):
                x, y = ax + (bx - ax) * j / n, ay + (by - ay) * j / n
                z = trace(x, y, M.elev(x, y) * 100.0 + 200.0, M.elev(x, y) * 100.0 - 1300.0)    # permukaan yang diinjak
                if z is None:
                    miss += 1
                    z = M.elev(x, y)
                cur = (x, y, z)
                if prev is not None:
                    tot += math.dist(prev, cur)
                prev = cur
        diff = (tot - target) / target * 100.0
        log(f"{nama}: {tot:.1f} m (data {target:.1f}, {diff:+.2f}%), {tot / v:.0f} s @ {v:g} m/s ({tot / v / 60:.1f} menit); meleset {miss}")
        ok = ok and abs(diff) <= 3.0 and miss == 0
    hasil["rute"] = ok


# ================================================================== main
def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Ep02] Editor sedang Play (PIE) — hentikan dulu")
        return
    fbx = os.path.join(EXPORT, "SM_Ep02_Medan.fbx")
    if not os.path.exists(fbx):
        fail(f"FBX tidak ada: {fbx} (jalankan Art/Scripts/ep02_medan_blender.py)")
        return
    mis = build_materials()
    if not build_level():
        return
    mesh = import_static_mesh(fbx, "SM_Ep02_Medan")
    if mesh is None:
        return
    assign_slots(mesh, mis)
    a_medan = EAS.spawn_actor_from_object(mesh, unreal.Vector(0.0, 0.0, 0.0))
    a_medan.set_actor_label("SM_Ep02_Medan")
    a_medan.set_folder_path("MEDAN")

    for o in OBJEK:
        if build_objek(o, mis) is None:
            fail(f"tidak terbangun: {o['id']}")
    for k in KELOMPOK:
        build_kelompok(k, mis)
    build_pohon(mis)
    build_tiang(mis)
    hc = half_capsule()
    build_penanda(mis, hc)           # setelah objek: titik di_atap memakai trace ke atap
    build_walls()
    build_kamera()                   # setelah objek: C2 berdiri di atap
    set_gamemode()
    set_cahaya(CAHAYA_UTAMA)
    LES.save_current_level()
    log("level disimpan")

    uji_medan(a_medan)
    uji_objek()
    jml = hitung_ism()
    uji_ism(jml)
    uji_penanda(hc)
    uji_dinding()
    uji_kamera()
    uji_gang()
    uji_rute()

    LES.load_level(MAP)       # persistensi: muat ulang lalu hitung lagi
    jml2 = hitung_ism()
    hasil["persist"] = jml2 == jml and find_by_label("START") is not None
    log(f"setelah muat ulang: ISM sama = {jml2 == jml}, START ada = {find_by_label('START') is not None}")

    ok = all(hasil.values()) and not problems
    log("RINGKAS: " + ", ".join(f"{k}={'ok' if v else 'GAGAL'}" for k, v in hasil.items()))
    for p in problems:
        unreal.log_warning("  - " + p)
    log(f"CEK EP02 GREYBOX: {'LULUS' if ok else 'GAGAL'}")


main()
