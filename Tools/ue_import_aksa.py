"""Import proxy/model Aksa (Art/Export) ke Unreal Engine 5.6 — Unreal Editor Python.

Mesh diimpor ke skeleton Mannequin ASLI (/Game/Characters/Mannequins/Meshes/SK_Mannequin, jalur (a) docs/19): tulang tambahan
(sash_01..06, nanti jacket_*) digabung ke skeleton itu (SK_Mannequin ikut ter-save; Manny/Quinn tidak berubah bentuk).
Hasil di /Game/Jayadwara/Characters/Aksa/:
  Textures/  T_Aksa_<Slot>_<BC|N|ORM|SSS|Mask> dari Art/Export/Textures_Aksa (yang sudah ada TIDAK ditimpa kecuali AKSA_RETEX=1)
  Materials/ M_Aksa_Master (BC*AO, N, ORM; two-sided) + MI_Aksa_<Skin|Eyes|Hair|Cloth|Gear> (parameter tekstur BC/N/ORM)
  Mesh/      SK_Aksa (skala 1; tinggi 180,6 cm = Manny) + 7 socket dari SK_Aksa_Proxy_sockets.json
Pakai: python Tools/ue_remote.py Tools/ue_import_aksa.py   (FBX dipilih otomatis: SK_Aksa.fbx > SK_Aksa_WIP.fbx > SK_Aksa_Proxy.fbx)
Mesh lama di Mesh/ dihapus dulu (impor ulang bersih). Langkah yang gagal mencetak "[MANUAL]".
"""
import json
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
_EXPORT = os.path.join(REPO, "Art", "Export")
FBX = os.environ.get("AKSA_FBX") or next(
    (os.path.join(_EXPORT, f) for f in ("SK_Aksa.fbx", "SK_Aksa_WIP.fbx", "SK_Aksa_Proxy.fbx") if os.path.exists(os.path.join(_EXPORT, f))),
    os.path.join(_EXPORT, "SK_Aksa_WIP.fbx"))                # paket final > WIP terbaru > proxy Iterasi 1
SOCKETS_JSON = os.path.splitext(FBX)[0] + "_sockets.json"
ROOT = "/Game/Jayadwara/Characters/Aksa"
MESH_NAME = "SK_Aksa"
SKELETON = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
PHYSICS = "/Game/Characters/Mannequins/Rigs/PA_Mannequin"
SLOTS = ["Skin", "Eyes", "Hair", "Cloth", "Gear"]
ROUGHNESS = {"Skin": 0.55, "Eyes": 0.15, "Hair": 0.6, "Cloth": 0.85, "Gear": 0.6}

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
problems = []


def log(msg):
    unreal.log(f"[Aksa] {msg}")


def manual(msg):
    problems.append(msg)
    unreal.log_warning(f"[Aksa][MANUAL] {msg}")


# ------------------------------------------------------------------ tekstur + material (Iterasi 5)
TEX_DIR = os.path.join(_EXPORT, "Textures_Aksa")
TEX_ROOT = f"{ROOT}/Textures"
RETEX = os.environ.get("AKSA_RETEX") == "1"            # timpa tekstur yang sudah ada (default: JANGAN — developer mungkin sudah mengecat)
TEX_KINDS = {"BC": (True, "TC_DEFAULT"), "N": (False, "TC_NORMALMAP"), "ORM": (False, "TC_MASKS"), "SSS": (False, "TC_MASKS"),
             "Mask": (False, "TC_MASKS")}


def import_textures():
    """T_Aksa_<Slot>_<Kind>.png -> /Game/.../Textures. Tekstur yang sudah ada dilewati kecuali AKSA_RETEX=1."""
    if not os.path.isdir(TEX_DIR):
        manual(f"folder tekstur tidak ada: {TEX_DIR} — jalankan Art/Scripts/make_textures_aksa.py")
        return {}
    tasks, names = [], []
    for f in sorted(os.listdir(TEX_DIR)):
        if not (f.startswith("T_Aksa_") and f.endswith(".png")):
            continue
        name = f[:-4]
        if EAL.does_asset_exist(f"{TEX_ROOT}/{name}") and not RETEX:
            log(f"tekstur {name} sudah ada — dilewati (AKSA_RETEX=1 untuk menimpa)")
            names.append(name)
            continue
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", os.path.join(TEX_DIR, f))
        t.set_editor_property("destination_path", TEX_ROOT)
        t.set_editor_property("destination_name", name)
        t.set_editor_property("automated", True)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("save", False)
        tasks.append(t)
        names.append(name)
    if tasks:
        asset_tools.import_asset_tasks(tasks)
    out = {}
    for name in names:
        tex = EAL.load_asset(f"{TEX_ROOT}/{name}")
        if tex is None:
            manual(f"tekstur {name} gagal diimpor")
            continue
        kind = name.rsplit("_", 1)[1]
        srgb, comp = TEX_KINDS.get(kind, (False, "TC_DEFAULT"))
        if name in {t.get_editor_property("destination_name") for t in tasks}:           # hanya yang baru diimpor diatur ulang
            tex.set_editor_property("srgb", srgb)
            tex.set_editor_property("compression_settings", getattr(unreal.TextureCompressionSettings, comp))
            if kind == "Mask":
                tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
        out[name] = tex
    log(f"tekstur: {len(out)} ({len(tasks)} baru diimpor)")
    return out


def build_master():
    path = f"{ROOT}/Materials/M_Aksa_Master"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    mat = asset_tools.create_asset("M_Aksa_Master", f"{ROOT}/Materials", unreal.Material, unreal.MaterialFactoryNew())

    def tex_param(name, y, sampler):
        n = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -600, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("sampler_type", sampler)
        return n

    bc = tex_param("BC", -250, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    nr = tex_param("N", 0, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    orm = tex_param("ORM", 250, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    ao_mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -250, -250)
    MEL.connect_material_expressions(bc, "RGB", ao_mul, "A")
    MEL.connect_material_expressions(orm, "R", ao_mul, "B")
    ok = MEL.connect_material_property(ao_mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
    ok &= MEL.connect_material_property(nr, "RGB", unreal.MaterialProperty.MP_NORMAL)
    ok &= MEL.connect_material_property(orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
    ok &= MEL.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)
    if not ok:
        manual("M_Aksa_Master: ada pin yang gagal terhubung (BC*AO / N / Roughness / Metallic)")
    mat.set_editor_property("two_sided", True)
    mat.set_editor_property("used_with_skeletal_mesh", True)
    MEL.recompile_material(mat)
    return mat


def build_materials(textures):
    master = build_master()
    mis = {}
    for s in SLOTS:
        p = f"{ROOT}/Materials/MI_Aksa_{s}"
        if EAL.does_asset_exist(p):
            EAL.delete_asset(p)
        mi = asset_tools.create_asset(f"MI_Aksa_{s}", f"{ROOT}/Materials", unreal.MaterialInstanceConstant,
                                      unreal.MaterialInstanceConstantFactoryNew())
        mi.set_editor_property("parent", master)
        for kind in ("BC", "N", "ORM"):
            tex = textures.get(f"T_Aksa_{s}_{kind}")
            if tex is None:
                manual(f"MI_Aksa_{s}: tekstur {kind} tidak ada")
                continue
            MEL.set_material_instance_texture_parameter_value(mi, kind, tex)
        mis[s] = mi
    log("M_Aksa_Master + 5 MI dibuat (BC/N/ORM per slot)")
    return mis


# ------------------------------------------------------------------ mesh
def import_mesh(skeleton):
    dest = f"{ROOT}/Mesh"
    for name in (MESH_NAME,):
        if EAL.does_asset_exist(f"{dest}/{name}"):
            EAL.delete_asset(f"{dest}/{name}")
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", True)
    ui.set_editor_property("import_as_skeletal", True)
    ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    ui.set_editor_property("skeleton", skeleton)
    ui.set_editor_property("import_materials", False)
    ui.set_editor_property("import_textures", False)
    ui.set_editor_property("import_animations", False)
    ui.set_editor_property("create_physics_asset", False)
    d = ui.get_editor_property("skeletal_mesh_import_data")
    d.set_editor_property("import_uniform_scale", 1.0)
    d.set_editor_property("convert_scene", True)
    d.set_editor_property("import_morph_targets", True)                 # morph target ekspresi wajah ak_*
    d.set_editor_property("use_t0_as_ref_pose", False)
    d.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)   # warna zona dari AK_Zone
    d.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", FBX)
    t.set_editor_property("destination_path", dest)
    t.set_editor_property("destination_name", MESH_NAME)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", False)
    t.set_editor_property("options", ui)
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")     # importer lama (seperti Jayadwara)
    try:
        asset_tools.import_asset_tasks([t])
    finally:
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")
    mesh = EAL.load_asset(f"{dest}/{MESH_NAME}")
    if not isinstance(mesh, unreal.SkeletalMesh):
        manual(f"{MESH_NAME} tidak terimpor sebagai SkeletalMesh — impor manual dengan skeleton SK_Mannequin")
        return None
    used = mesh.get_editor_property("skeleton")
    log(f"{MESH_NAME} terimpor; skeleton = {used.get_path_name()} (sama dengan SK_Mannequin: {used.get_path_name().split('.')[0] == SKELETON})")
    return mesh


def assign_materials(mesh, mis):
    out = []
    for m in mesh.get_editor_property("materials"):
        slot = str(m.get_editor_property("material_slot_name"))
        key = next((s for s in SLOTS if slot.endswith(s)), None)
        if key:
            m.set_editor_property("material_interface", mis[key])
        else:
            manual(f"slot material tak dikenal: {slot}")
        out.append(m)
    mesh.set_editor_property("materials", out)
    got = [(str(m.get_editor_property("material_slot_name")), m.get_editor_property("material_interface")) for m in mesh.get_editor_property("materials")]
    log("material terpasang: " + ", ".join(f"{s}={mi.get_name() if mi else None}" for s, mi in got))


def add_sockets(mesh):
    with open(SOCKETS_JSON, encoding="utf-8") as f:
        data = json.load(f)["sockets"]
    skel = mesh.get_editor_property("skeleton")
    try:
        pose = unreal.AnimPoseExtensions.get_reference_pose(skel)
    except Exception as e:  # noqa: BLE001
        pose = None
        manual(f"pose referensi tidak terbaca ({e}); socket dibuat tanpa offset")
    for s in data:
        name = s["name"]
        if mesh.find_socket(name) is not None:
            continue
        loc = unreal.Vector(*s["ue_component_cm"])
        rel = loc
        if pose is not None:
            bt = unreal.AnimPoseExtensions.get_bone_pose(pose, s["bone"], unreal.AnimPoseSpaces.WORLD)
            rel = bt.inverse_transform_location(loc)
        try:
            sock = unreal.new_object(unreal.SkeletalMeshSocket, outer=mesh)
            sock.set_socket_parent(mesh, s["bone"])
            sock.set_editor_property("relative_location", rel)
            mesh.add_socket(sock, False)
            if not mesh.rename_socket(str(sock.get_editor_property("socket_name")), name):
                raise RuntimeError("rename_socket gagal")
            log(f"socket {name} @ {s['bone']} ({rel.x:.1f}, {rel.y:.1f}, {rel.z:.1f})")
        except Exception as e:  # noqa: BLE001
            manual(f"socket {name}: tambah manual di tulang {s['bone']}, Relative Location ({rel.x:.1f}, {rel.y:.1f}, {rel.z:.1f}) ({e})")


def main():
    if not os.path.exists(FBX):
        unreal.log_error(f"[Aksa] FBX tidak ada: {FBX} — jalankan Art/Scripts/aksa_14_export.py di Blender dulu")
        return
    skeleton = EAL.load_asset(SKELETON)
    if skeleton is None:
        unreal.log_error(f"[Aksa] {SKELETON} tidak ditemukan")
        return
    mis = build_materials(import_textures())
    mesh = import_mesh(skeleton)
    if mesh is not None:
        assign_materials(mesh, mis)
        pa = EAL.load_asset(PHYSICS)
        if pa is not None:
            mesh.set_editor_property("physics_asset", pa)
            log("physics asset: PA_Mannequin (sementara)")
        add_sockets(mesh)
        try:
            mts = [str(m.get_name()) for m in mesh.get_editor_property("morph_targets")]
            log(f"morph target: {len(mts)} {mts}")
        except Exception as e:  # noqa: BLE001
            log(f"morph target tidak terbaca ({e})")
        try:
            names = [str(n) for n in unreal.AnimPoseExtensions.get_bone_names(unreal.AnimPoseExtensions.get_reference_pose(mesh.get_editor_property("skeleton")))]
            log(f"skeleton: {len(names)} tulang; sash: {[n for n in names if n.startswith('sash_')]}")
        except Exception as e:  # noqa: BLE001
            log(f"daftar tulang tidak terbaca ({e})")
        EAL.save_asset(SKELETON, only_if_is_dirty=False)
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    log("selesai.")
    if problems:
        unreal.log_warning(f"[Aksa] {len(problems)} langkah perlu dikerjakan manual:")
        for p in problems:
            unreal.log_warning("  - " + p)


main()
