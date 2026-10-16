"""Tuyul K6 — impor 3 skala (LOD0..3) ke sandbox /Game/Hermes/Tuyul/Mesh + 8 socket per mesh.
Dijalankan: python Tools/ue_remote.py Hermes/Tools/tuyul_61_ue_import.py
Pola: Hermes/Tools/aksa2_71_import_mesh.py (branch hermes/aksa2).
"""
import json
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EXPORT = os.path.join(REPO, "Hermes", "Art", "tuyul", "Export")
DEST = "/Game/Hermes/Tuyul"
MESH_DIR = f"{DEST}/Mesh"
SKELETON = f"{MESH_DIR}/SKEL_Tuyul"
MI = f"{DEST}/Materials/MI_Tuyul_Body"
PHYSICS = "/Game/Characters/Mannequins/Rigs/PA_Mannequin"

SCALES = [
    ("SK_Tuyul", "SK_Tuyul.fbx", "SK_Tuyul_sockets.json"),
    ("SK_TuyulBesar", "SK_TuyulBesar.fbx", "SK_TuyulBesar_sockets.json"),
    ("SK_TuyulRaksasa", "SK_TuyulRaksasa.fbx", "SK_TuyulRaksasa_sockets.json"),
]
LOD_SCREEN_SIZE = {0: 1.0, 1: 0.45, 2: 0.22, 3: 0.10}
LEGACY_FBX = True  # True = importer FBX lama (Interchange.FeatureFlags.Import.FBX 0)

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()


def legacy_fbx(fn):
    if not LEGACY_FBX:
        return fn()
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    try:
        return fn()
    finally:
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")


def import_lod0(skeleton, fbx, name):
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
    d.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", os.path.join(EXPORT, fbx))
    t.set_editor_property("destination_path", MESH_DIR)
    t.set_editor_property("destination_name", name)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", False)
    t.set_editor_property("options", ui)
    legacy_fbx(lambda: asset_tools.import_asset_tasks([t]))
    mesh = EAL.load_asset(f"{MESH_DIR}/{name}")
    assert isinstance(mesh, unreal.SkeletalMesh), f"{name} tidak terimpor sebagai SkeletalMesh"
    print("  skeleton mesh:", mesh.get_editor_property("skeleton").get_path_name())
    return mesh


def import_lods(mesh, name):
    sub = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)

    def run():
        for i in (1, 2, 3):
            f = f"{name}_LOD{i}.fbx"
            res = sub.import_lod(mesh, i, os.path.join(EXPORT, f))
            print(f"  LOD{i} <- {f}: {res}")

    legacy_fbx(run)
    infos = []
    for i, info in enumerate(mesh.get_editor_property("lod_info")):
        if i in LOD_SCREEN_SIZE:
            ss = unreal.PerPlatformFloat()
            ss.set_editor_property("default", LOD_SCREEN_SIZE[i])
            info.set_editor_property("screen_size", ss)
        infos.append(info)
    mesh.set_editor_property("lod_info", infos)
    print("  LOD level:", len(infos))


def assign_material(mesh):
    mi = EAL.load_asset(MI)
    mats = []
    for m in mesh.get_editor_property("materials"):
        m.set_editor_property("material_interface", mi)
        mats.append(m)
    mesh.set_editor_property("materials", mats)
    print("  material slot:", len(mats), "->", mi.get_name())


def sockets(mesh, json_file):
    data = json.load(open(os.path.join(EXPORT, json_file), encoding="utf-8"))["sockets"]
    # Transform tulang pada ref pose MESH ini. (AnimPoseExtensions.get_reference_pose hanya menerima
    # Skeleton — dan skeleton bersama SKEL_Tuyul berskala x1 — sehingga untuk mesh x27/x45 harus
    # dibaca dari komponen mesh sendiri, kalau tidak socket jatuh di posisi x1.)
    tmp = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    tmp.set_actor_label("K6_socket_probe")
    comp = tmp.skeletal_mesh_component
    comp.set_skinned_asset_and_update(mesh)
    bone_tf = {}
    for s in data:
        if s["bone"] not in bone_tf:
            bone_tf[s["bone"]] = comp.get_bone_transform(s["bone"], unreal.RelativeTransformSpace.RTS_COMPONENT)
    EAS.destroy_actor(tmp)
    for s in data:
        loc = unreal.Vector(*s["ue_component_cm"])
        rel = bone_tf[s["bone"]].inverse_transform_location(loc)
        sock = mesh.find_socket(s["name"])
        if sock is None:
            sock = unreal.new_object(unreal.SkeletalMeshSocket, outer=mesh)
            sock.set_socket_parent(mesh, s["bone"])
            mesh.add_socket(sock, False)
            assert mesh.rename_socket(str(sock.get_editor_property("socket_name")), s["name"]), "rename_socket gagal"
            sock = mesh.find_socket(s["name"])
        assert str(sock.get_editor_property("bone_name")) == s["bone"], f"socket {s['name']} di tulang salah"
        sock.set_editor_property("relative_location", rel)
        print(f"  socket {s['name']} @ {s['bone']} rel=({rel.x:.1f}, {rel.y:.1f}, {rel.z:.1f})")


if unreal.EditorLevelLibrary.get_pie_worlds(False):
    raise RuntimeError("Editor sedang Play (PIE) — hentikan dulu")

skeleton = EAL.load_asset(SKELETON)
assert skeleton is not None, f"skeleton tidak ada: {SKELETON}"
man = EAL.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
if man not in list(skeleton.get_editor_property("compatible_skeletons")):
    skeleton.add_compatible_skeleton(man)
EAL.save_loaded_asset(skeleton, False)
print("compat:", [x.get_name() for x in skeleton.get_editor_property("compatible_skeletons")])

for name, fbx, sockj in SCALES:
    print(f"=== {name} ===")
    mesh = import_lod0(skeleton, fbx, name)
    assign_material(mesh)
    import_lods(mesh, name)
    assign_material(mesh)
    try:
        pa = EAL.load_asset(PHYSICS)
        if pa:
            mesh.set_editor_property("physics_asset", pa)
    except Exception as e:  # noqa: BLE001
        print("  PERINGATAN physics asset:", e)
    sockets(mesh, sockj)
    EAL.save_loaded_asset(mesh)
    print("  bounds:", mesh.get_bounds())

print("=== IMPOR K6 SELESAI ===")
