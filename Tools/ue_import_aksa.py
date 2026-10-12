"""Import proxy/model Aksa (Art/Export) ke Unreal Engine 5.6 — Unreal Editor Python.

Mesh diimpor ke skeleton Mannequin ASLI (/Game/Characters/Mannequins/Meshes/SK_Mannequin, jalur (a) docs/19): tulang tambahan
(sash_01..06, nanti jacket_*) digabung ke skeleton itu (SK_Mannequin ikut ter-save; Manny/Quinn tidak berubah bentuk).
Hasil di /Game/Jayadwara/Characters/Aksa/:
  Materials/ M_Aksa_Proxy (warna dari vertex color AK_Zone, two-sided) + MI_Aksa_<Skin|Eyes|Hair|Cloth|Gear>
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


# ------------------------------------------------------------------ material proxy
def build_materials():
    path = f"{ROOT}/Materials/M_Aksa_Proxy"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    mat = asset_tools.create_asset("M_Aksa_Proxy", f"{ROOT}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    vc = MEL.create_material_expression(mat, unreal.MaterialExpressionVertexColor, -700, 0)
    lin = MEL.create_material_expression(mat, unreal.MaterialExpressionPower, -450, 0)         # FBX membawa byte sRGB; UE membacanya linear
    lin.set_editor_property("const_exponent", 2.2)
    rough = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -450, 220)
    rough.set_editor_property("parameter_name", "Roughness")
    rough.set_editor_property("default_value", 0.7)
    MEL.connect_material_expressions(vc, "", lin, "Base")
    if not MEL.connect_material_property(lin, "", unreal.MaterialProperty.MP_BASE_COLOR):
        manual("M_Aksa_Proxy: vertex color gagal terhubung ke Base Color")
    MEL.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mat.set_editor_property("two_sided", True)
    mat.set_editor_property("used_with_skeletal_mesh", True)
    MEL.recompile_material(mat)
    mis = {}
    for s in SLOTS:
        p = f"{ROOT}/Materials/MI_Aksa_{s}"
        if EAL.does_asset_exist(p):
            EAL.delete_asset(p)
        mi = asset_tools.create_asset(f"MI_Aksa_{s}", f"{ROOT}/Materials", unreal.MaterialInstanceConstant,
                                      unreal.MaterialInstanceConstantFactoryNew())
        mi.set_editor_property("parent", mat)
        MEL.set_material_instance_scalar_parameter_value(mi, "Roughness", ROUGHNESS[s])
        mis[s] = mi
    log("M_Aksa_Proxy + 5 MI dibuat")
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
    d.set_editor_property("import_morph_targets", False)
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
    mis = build_materials()
    mesh = import_mesh(skeleton)
    if mesh is not None:
        assign_materials(mesh, mis)
        pa = EAL.load_asset(PHYSICS)
        if pa is not None:
            mesh.set_editor_property("physics_asset", pa)
            log("physics asset: PA_Mannequin (sementara)")
        add_sockets(mesh)
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
