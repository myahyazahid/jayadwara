"""Import paket Jayadwara (Art/Export) ke Unreal Engine 5.6 — Unreal Editor Python.

STATUS: teruji di UE 5.6.1 (Iterasi 6, 12 Okt 2026). Langkah yang gagal mencetak "[MANUAL]" berisi langkah pengganti
(lihat juga Art/Export/README_IMPORT_UE.md). Aset di Mesh/ dihapus dulu (impor ulang bersih; skeleton bisa berubah).

Pakai (Python Editor Script Plugin aktif):
  Output Log -> Python:  py "C:/repository/unreal_engine/jayadwara/Tools/ue_import_jayadwara.py"
  atau Tools -> Execute Python Script...

Hasil di /Game/Jayadwara/Characters/Jayadwara/:
  Textures/  T_Jayadwara_<Slot>_<Mask|BC|N|ORM> + T_Jayadwara_Face_Emit (setelan sRGB/kompresi docs/15)
  Materials/ M_Jayadwara_Master + MI_Jayadwara_<Body|Armor|Cloth|Face>
  Mesh/      SK_Jayadwara (LOD0–3), SKEL_Jayadwara, PA_Jayadwara, socket dari SK_Jayadwara_sockets.json
Skala 1 (tinggi 199 cm, sama dengan Mannequin). Skala raksasa TIDAK di sini — lihat catatan IMPORT_UNIFORM_SCALE.
"""
import json
import os

import unreal

# ------------------------------------------------------------------ konfigurasi
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EXPORT = os.path.join(REPO, "Art", "Export")
TEX_DIR = os.path.join(EXPORT, "Textures")
ROOT = "/Game/Jayadwara/Characters/Jayadwara"
MESH_NAME = "SK_Jayadwara"
SLOTS = ["Body", "Armor", "Cloth", "Face"]

# Harus 1. Di UE 5.6.1 Import Uniform Scale skeletal mesh masuk ke SKALA tulang root (tidak di-bake ke posisi tulang),
# dan animasi retarget yang mengunci skala root = 1 akan mengecilkan raksasa lagi. Skala raksasa (±45 m, placeholder)
# dipasang di komponen mesh karakter raksasa (docs/13 D4, revisi Iterasi 6).
IMPORT_UNIFORM_SCALE = 1.0

LOD_FILES = {1: "SK_Jayadwara_LOD1.fbx", 2: "SK_Jayadwara_LOD2.fbx", 3: "SK_Jayadwara_LOD3.fbx"}
LOD_SCREEN_SIZE = {0: 1.0, 1: 0.5, 2: 0.25, 3: 0.12}             # titik awal; tuning di level uji (Iterasi 6)

# warna sRGB dari Art/Scripts/jd_common.py (HEX) — sama dengan material Blender 08_materials.py
COLORS = {"Color_Red": "#A8262B", "Color_Gold": "#D6A33A", "Color_Black": "#2A2626", "Color_White": "#E2E0DE",
          "Emissive_Color": "#FFC86B"}
EMISSIVE_INTENSITY = 3.0                                         # KONSTAN — aturan IP: tidak dikaitkan ke meter Sync

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
problems = []


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def manual(msg):
    problems.append(msg)
    unreal.log_warning(f"[Jayadwara][MANUAL] {msg}")


def lin_color(hexstr):
    h = hexstr.lstrip("#")

    def s2l(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (s2l(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))
    return unreal.LinearColor(r, g, b, 1.0)


def run_tasks(tasks):
    asset_tools.import_asset_tasks(tasks)
    return [p for t in tasks for p in (t.get_editor_property("imported_object_paths") or [])]


def set_fbx_legacy(enabled):
    """UE 5.5+ memakai Interchange untuk FBX secara default; opsi FbxImportUI di bawah untuk importer lama.
    Nama CVar ini asumsi (belum diuji) — kalau tidak ada, perintah diabaikan dan Interchange yang dipakai."""
    unreal.SystemLibrary.execute_console_command(None, f"Interchange.FeatureFlags.Import.FBX {0 if enabled else 1}")


# ------------------------------------------------------------------ 1. tekstur
def import_textures():
    dest = f"{ROOT}/Textures"
    tasks = []
    for fn in sorted(os.listdir(TEX_DIR)):
        if not (fn.startswith("T_Jayadwara_") and fn.endswith(".png")):
            continue
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", os.path.join(TEX_DIR, fn))
        t.set_editor_property("destination_path", dest)
        t.set_editor_property("automated", True)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("save", False)
        tasks.append(t)
    run_tasks(tasks)
    tex = {}
    for fn in sorted(os.listdir(TEX_DIR)):
        if not (fn.startswith("T_Jayadwara_") and fn.endswith(".png")):
            continue
        name = fn[:-4]
        a = EAL.load_asset(f"{dest}/{name}")
        if a is None:
            manual(f"tekstur {name} tidak terimpor")
            continue
        kind = name.rsplit("_", 1)[1]
        if kind == "BC":
            a.set_editor_property("srgb", True)
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
        elif kind == "N":
            a.set_editor_property("srgb", False)
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            a.set_editor_property("flip_green_channel", True)    # normal dari Blender = OpenGL (+Y); UE = DirectX
        else:                                                    # Mask, ORM, Emit: data linear
            a.set_editor_property("srgb", False)
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        tex[name] = a
    log(f"tekstur: {len(tex)} di {dest}")
    return tex


# ------------------------------------------------------------------ 2. master material + instance
def sampler(kind):
    S = unreal.MaterialSamplerType
    return {"BC": S.SAMPLERTYPE_COLOR, "N": S.SAMPLERTYPE_NORMAL}.get(kind, S.SAMPLERTYPE_MASKS)


def build_master(tex):
    """docs/15: warna = lerp zona (Mask R merah, G emas, A putih; dasar hitam) x BC x AO(ORM.R);
    Roughness ORM.G, Metallic ORM.B, Normal N; Emissive = Emissive_Color x Emit.R x Intensity x Emissive_Enable."""
    path = f"{ROOT}/Materials/M_Jayadwara_Master"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    mat = asset_tools.create_asset("M_Jayadwara_Master", f"{ROOT}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    y = [0]

    def expr(cls, x=-1200):
        e = MEL.create_material_expression(mat, cls, x, y[0])
        y[0] += 140
        return e

    def tparam(name, kind, default):
        e = expr(unreal.MaterialExpressionTextureSampleParameter2D)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("sampler_type", sampler(kind))
        e.set_editor_property("texture", default)
        return e

    def vparam(name):
        e = expr(unreal.MaterialExpressionVectorParameter, -900)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", lin_color(COLORS[name]))
        return e

    def sparam(name, v):
        e = expr(unreal.MaterialExpressionScalarParameter, -900)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", v)
        return e

    def op(cls, a, a_out, b, b_out, x=-500):
        e = expr(cls, x)
        MEL.connect_material_expressions(a, a_out, e, "A")
        MEL.connect_material_expressions(b, b_out, e, "B")
        return e

    def lerp(a, a_out, b, b_out, alpha, alpha_out, x=-600):
        e = op(unreal.MaterialExpressionLinearInterpolate, a, a_out, b, b_out, x)
        MEL.connect_material_expressions(alpha, alpha_out, e, "Alpha")
        return e

    t_mask = tparam("T_Mask", "Mask", tex["T_Jayadwara_Armor_Mask"])
    t_bc = tparam("T_BC", "BC", tex["T_Jayadwara_Armor_BC"])
    t_n = tparam("T_N", "N", tex["T_Jayadwara_Armor_N"])
    t_orm = tparam("T_ORM", "ORM", tex["T_Jayadwara_Armor_ORM"])
    t_emit = tparam("T_Emit", "Emit", tex["T_Jayadwara_Face_Emit"])
    c = {n: vparam(n) for n in COLORS}
    k_int = sparam("Emissive_Intensity", EMISSIVE_INTENSITY)
    k_en = sparam("Emissive_Enable", 0.0)                         # 1 hanya di MI_Jayadwara_Face

    z1 = lerp(c["Color_Black"], "", c["Color_Red"], "", t_mask, "R")
    z2 = lerp(z1, "", c["Color_Gold"], "", t_mask, "G")
    z3 = lerp(z2, "", c["Color_White"], "", t_mask, "A")
    m_bc = op(unreal.MaterialExpressionMultiply, z3, "", t_bc, "RGB")
    m_ao = op(unreal.MaterialExpressionMultiply, m_bc, "", t_orm, "R")
    e_mask = op(unreal.MaterialExpressionMultiply, t_emit, "R", k_en, "")
    base = lerp(m_ao, "", c["Emissive_Color"], "", e_mask, "", -300)          # area emissive: warna dasar = warna cahaya
    e1 = op(unreal.MaterialExpressionMultiply, c["Emissive_Color"], "", e_mask, "", -300)
    e2 = op(unreal.MaterialExpressionMultiply, e1, "", k_int, "", -200)

    P = unreal.MaterialProperty
    MEL.connect_material_property(base, "", P.MP_BASE_COLOR)
    MEL.connect_material_property(t_orm, "G", P.MP_ROUGHNESS)
    MEL.connect_material_property(t_orm, "B", P.MP_METALLIC)
    MEL.connect_material_property(t_n, "RGB", P.MP_NORMAL)
    MEL.connect_material_property(e2, "", P.MP_EMISSIVE_COLOR)
    mat.set_editor_property("used_with_skeletal_mesh", True)
    MEL.layout_material_expressions(mat)
    MEL.recompile_material(mat)
    log("M_Jayadwara_Master dibuat")
    return mat


def build_instances(master, tex):
    mis = {}
    for s in SLOTS:
        name = f"MI_Jayadwara_{s}"
        path = f"{ROOT}/Materials/{name}"
        mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else asset_tools.create_asset(
            name, f"{ROOT}/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        MEL.set_material_instance_parent(mi, master)
        for p, kind in (("T_Mask", "Mask"), ("T_BC", "BC"), ("T_N", "N"), ("T_ORM", "ORM")):
            MEL.set_material_instance_texture_parameter_value(mi, p, tex[f"T_Jayadwara_{s}_{kind}"])
        if s == "Face":
            MEL.set_material_instance_texture_parameter_value(mi, "T_Emit", tex["T_Jayadwara_Face_Emit"])
            MEL.set_material_instance_scalar_parameter_value(mi, "Emissive_Enable", 1.0)
        if s == "Cloth":                                         # kain: two-sided (docs/15)
            try:
                ov = mi.get_editor_property("base_property_overrides")
                ov.set_editor_property("override_two_sided", True)
                ov.set_editor_property("two_sided", True)
                mi.set_editor_property("base_property_overrides", ov)
            except Exception as e:  # noqa: BLE001
                manual(f"MI_Jayadwara_Cloth: centang Details > Material Property Overrides > Two Sided ({e})")
        MEL.update_material_instance(mi)
        mis[s] = mi
    log("material instance: " + ", ".join(mis))
    return mis


# ------------------------------------------------------------------ 3. skeletal mesh + LOD
def fbx_options():
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", True)
    ui.set_editor_property("import_as_skeletal", True)
    ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    ui.set_editor_property("import_materials", False)            # material = MI di atas, dipasang per slot
    ui.set_editor_property("import_textures", False)
    ui.set_editor_property("import_animations", False)
    ui.set_editor_property("create_physics_asset", True)
    d = ui.get_editor_property("skeletal_mesh_import_data")
    d.set_editor_property("import_uniform_scale", IMPORT_UNIFORM_SCALE)
    d.set_editor_property("convert_scene", True)
    d.set_editor_property("import_morph_targets", False)
    d.set_editor_property("use_t0_as_ref_pose", False)
    d.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    return ui


def clean_mesh_folder():
    dest = f"{ROOT}/Mesh"
    if EAL.does_directory_exist(dest):
        for a in EAL.list_assets(dest, recursive=True, include_folder=False):
            EAL.delete_asset(a.split(".")[0])
        log(f"isi {dest} dihapus (impor ulang bersih)")


def import_mesh():
    dest = f"{ROOT}/Mesh"
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", os.path.join(EXPORT, f"{MESH_NAME}.fbx"))
    t.set_editor_property("destination_path", dest)
    t.set_editor_property("destination_name", MESH_NAME)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", False)
    t.set_editor_property("options", fbx_options())
    set_fbx_legacy(True)
    try:
        run_tasks([t])
    finally:
        set_fbx_legacy(False)
    mesh = EAL.load_asset(f"{dest}/{MESH_NAME}")
    if not isinstance(mesh, unreal.SkeletalMesh):
        manual(f"{MESH_NAME} tidak terimpor sebagai SkeletalMesh — impor manual (README_IMPORT_UE.md langkah B2)")
        return None
    log(f"{MESH_NAME} terimpor ({dest})")
    return mesh


def import_lods(mesh):
    sub = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem) if hasattr(unreal, "SkeletalMeshEditorSubsystem") else None
    fn = getattr(sub, "import_lod", None) if sub else None
    if fn is None and hasattr(unreal, "EditorSkeletalMeshLibrary"):
        fn = getattr(unreal.EditorSkeletalMeshLibrary, "import_lod", None)
    if fn is None:
        manual("API import LOD tidak ditemukan — Skeletal Mesh Editor > LOD Settings > LOD Import (LOD1–3)")
        return
    set_fbx_legacy(True)
    try:
        for i, f in LOD_FILES.items():
            res = fn(mesh, i, os.path.join(EXPORT, f))
            if res is None or (isinstance(res, int) and res < 0):
                manual(f"LOD{i} gagal diimpor dari {f}")
            else:
                log(f"LOD{i} <- {f}")
    finally:
        set_fbx_legacy(False)
    try:                                                         # ukuran layar per LOD
        infos = []
        for i, info in enumerate(mesh.get_editor_property("lod_info")):
            if i in LOD_SCREEN_SIZE:
                ss = unreal.PerPlatformFloat()
                ss.set_editor_property("default", LOD_SCREEN_SIZE[i])
                info.set_editor_property("screen_size", ss)
            infos.append(info)
        mesh.set_editor_property("lod_info", infos)
    except Exception as e:  # noqa: BLE001
        manual(f"screen size LOD: set manual {LOD_SCREEN_SIZE} ({e})")


def assign_materials(mesh, mis):
    # Elemen array struct dari get_editor_property adalah salinan: ubah lalu kumpulkan ke list baru, baru di-set.
    out = []
    for m in mesh.get_editor_property("materials"):
        slot = str(m.get_editor_property("material_slot_name"))
        key = next((s for s in SLOTS if slot.endswith(s) or slot == f"M_Jayadwara_{s}"), None)
        if key:
            m.set_editor_property("material_interface", mis[key])
        else:
            manual(f"slot material tak dikenal: {slot}")
        out.append(m)
    mesh.set_editor_property("materials", out)
    got = [(str(m.get_editor_property("material_slot_name")), m.get_editor_property("material_interface")) for m in mesh.get_editor_property("materials")]
    for slot, mi in got:
        if mi is None:
            manual(f"slot {slot} kosong — pasang MI_Jayadwara_* manual di Asset Details > Material Slots")
    log("material terpasang: " + ", ".join(f"{s}={mi.get_name() if mi else None}" for s, mi in got))


def rename_companions(mesh):
    dest = f"{ROOT}/Mesh"
    for prop, new in (("skeleton", "SKEL_Jayadwara"), ("physics_asset", "PA_Jayadwara")):
        a = mesh.get_editor_property(prop)
        if a is None:
            manual(f"{prop} tidak ada (physics asset tidak dibuat?)")
            continue
        old = a.get_path_name().split(".")[0]
        if old.endswith("/" + new):
            continue
        if EAL.does_asset_exist(f"{dest}/{new}"):
            manual(f"{dest}/{new} sudah ada — {old} tidak di-rename")
            continue
        EAL.rename_asset(old, f"{dest}/{new}")
        log(f"{old} -> {dest}/{new}")


# ------------------------------------------------------------------ 4. socket
def add_sockets(mesh):
    """UE tidak membuat socket skeletal mesh dari empty FBX. Posisi socket (ruang komponen) diubah ke ruang tulang
    memakai pose referensi skeleton."""
    with open(os.path.join(EXPORT, f"{MESH_NAME}_sockets.json"), encoding="utf-8") as f:
        data = json.load(f)["sockets"]
    skel = mesh.get_editor_property("skeleton")
    try:
        pose = unreal.AnimPoseExtensions.get_reference_pose(skel)
    except Exception as e:  # noqa: BLE001
        pose = None
        manual(f"pose referensi tidak terbaca ({e}); socket dibuat tanpa offset")
    for s in data:
        name = s["name"].replace("SOCKET_", "")                 # nama socket UE: hand_r, chest_sun, ...
        if mesh.find_socket(name) is not None:
            continue
        loc = unreal.Vector(*[c * IMPORT_UNIFORM_SCALE for c in s["ue_component_cm"]])
        rel = loc
        if pose is not None:
            bt = unreal.AnimPoseExtensions.get_bone_pose(pose, s["bone"], unreal.AnimPoseSpaces.WORLD)
            rel = bt.inverse_transform_location(loc)
        try:
            # socket_name & bone_name read-only di Python: set_socket_parent mengisi tulang (nama jadi "Socket"),
            # lalu rename_socket memberi nama akhir.
            sock = unreal.new_object(unreal.SkeletalMeshSocket, outer=mesh)
            sock.set_socket_parent(mesh, s["bone"])
            sock.set_editor_property("relative_location", rel)
            mesh.add_socket(sock, False)
            if not mesh.rename_socket(str(sock.get_editor_property("socket_name")), name):
                raise RuntimeError("rename_socket gagal")
            log(f"socket {name} @ {s['bone']} ({rel.x:.1f}, {rel.y:.1f}, {rel.z:.1f})")
        except Exception as e:  # noqa: BLE001
            manual(f"socket {name}: tambah manual di tulang {s['bone']}, Relative Location ({rel.x:.1f}, {rel.y:.1f}, {rel.z:.1f}) ({e})")


# ------------------------------------------------------------------ main
def main():
    for f in [f"{MESH_NAME}.fbx", f"{MESH_NAME}_sockets.json", *LOD_FILES.values()]:
        if not os.path.exists(os.path.join(EXPORT, f)):
            unreal.log_error(f"[Jayadwara] file tidak ada: {f} — jalankan Art/Scripts/16_make_lods.py di Blender dulu")
            return
    tex = import_textures()
    master = build_master(tex)
    mis = build_instances(master, tex)
    clean_mesh_folder()
    mesh = import_mesh()
    if mesh is not None:
        import_lods(mesh)
        assign_materials(mesh, mis)
        rename_companions(mesh)
        add_sockets(mesh)
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    log(f"selesai. Skala import {IMPORT_UNIFORM_SCALE:.2f}.")
    if problems:
        unreal.log_warning(f"[Jayadwara] {len(problems)} langkah perlu dikerjakan manual:")
        for p in problems:
            unreal.log_warning("  - " + p)


main()
