"""Aksa2 — impor ulang SK_Aksa2 (LOD0..3) ke sandbox /Game/Hermes/Aksa2 dengan opsi yang sama seperti Tools/ue_import_aksa.py.

Beda dengan aksa2_70_ue_setup.py: socket diberi offset relatif tulang dari ue_component_cm (aksa2_70 memakai kunci
`rel_loc` yang tidak ada, jadi semua socket jatuh di origin tulang), LOD1-3 ikut, dan skeleton tidak diduplikasi ulang.
Pakai: python Tools/ue_remote.py Hermes/Tools/aksa2_71_import_mesh.py
"""
import json
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EXPORT = os.path.join(REPO, "Hermes", "Art", "aksa2", "Export")
DEST = "/Game/Hermes/Aksa2"
MESH_NAME = "SK_Aksa2"
SKELETON = f"{DEST}/SKEL_Aksa2"
MI = f"{DEST}/Materials/MI_Aksa2_Body"
PHYSICS = "/Game/Characters/Mannequins/Rigs/PA_Mannequin"
LOD_FILES = {1: "SK_Aksa2_LOD1.fbx", 2: "SK_Aksa2_LOD2.fbx", 3: "SK_Aksa2_LOD3.fbx"}
LOD_SCREEN_SIZE = {0: 1.0, 1: 0.45, 2: 0.22, 3: 0.10}
LEGACY_FBX = True    # True = importer FBX lama (Interchange.FeatureFlags.Import.FBX 0)

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()


def legacy_fbx(fn):
    if not LEGACY_FBX:
        return fn()
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    try:
        return fn()
    finally:
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")


def import_mesh(skeleton):
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
    t.set_editor_property("filename", os.path.join(EXPORT, "SK_Aksa2.fbx"))
    t.set_editor_property("destination_path", DEST)
    t.set_editor_property("destination_name", MESH_NAME)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", False)
    t.set_editor_property("options", ui)
    legacy_fbx(lambda: asset_tools.import_asset_tasks([t]))
    mesh = EAL.load_asset(f"{DEST}/{MESH_NAME}")
    assert isinstance(mesh, unreal.SkeletalMesh), "SK_Aksa2 tidak terimpor sebagai SkeletalMesh"
    print("skeleton mesh:", mesh.get_editor_property("skeleton").get_path_name())
    return mesh


def import_lods(mesh):
    sub = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    def run():
        for i, f in LOD_FILES.items():
            res = sub.import_lod(mesh, i, os.path.join(EXPORT, f))
            print(f"LOD{i} <- {f}: {res}")
    legacy_fbx(run)
    infos = []
    for i, info in enumerate(mesh.get_editor_property("lod_info")):
        if i in LOD_SCREEN_SIZE:
            ss = unreal.PerPlatformFloat()
            ss.set_editor_property("default", LOD_SCREEN_SIZE[i])
            info.set_editor_property("screen_size", ss)
        infos.append(info)
    mesh.set_editor_property("lod_info", infos)
    print("LOD level:", len(infos))


def assign_material(mesh):
    mi = EAL.load_asset(MI)
    mats = []
    for m in mesh.get_editor_property("materials"):
        m.set_editor_property("material_interface", mi)
        mats.append(m)
    mesh.set_editor_property("materials", mats)
    print("material slot:", len(mats), "->", mi.get_name())


def sockets(mesh):
    data = json.load(open(os.path.join(EXPORT, "SK_Aksa2_sockets.json"), encoding="utf-8"))["sockets"]
    pose = unreal.AnimPoseExtensions.get_reference_pose(mesh.get_editor_property("skeleton"))
    for s in data:
        loc = unreal.Vector(*s["ue_component_cm"])
        bt = unreal.AnimPoseExtensions.get_bone_pose(pose, s["bone"], unreal.AnimPoseSpaces.WORLD)
        rel = bt.inverse_transform_location(loc)
        sock = mesh.find_socket(s["name"])
        if sock is None:
            sock = unreal.new_object(unreal.SkeletalMeshSocket, outer=mesh)
            sock.set_socket_parent(mesh, s["bone"])
            mesh.add_socket(sock, False)
            assert mesh.rename_socket(str(sock.get_editor_property("socket_name")), s["name"]), "rename_socket gagal"
            sock = mesh.find_socket(s["name"])
        assert str(sock.get_editor_property("bone_name")) == s["bone"], f"socket {s['name']} di tulang salah"
        sock.set_editor_property("relative_location", rel)
        print(f"socket {s['name']} @ {s['bone']} rel=({rel.x:.1f}, {rel.y:.1f}, {rel.z:.1f})")


if unreal.EditorLevelLibrary.get_pie_worlds(False):
    raise RuntimeError("Editor sedang Play (PIE) — hentikan dulu")
skeleton = EAL.load_asset(SKELETON)
man = EAL.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
if man not in list(skeleton.get_editor_property("compatible_skeletons")):
    skeleton.add_compatible_skeleton(man)
EAL.save_loaded_asset(skeleton, False)          # compat HARUS tersimpan (sebelumnya hanya di memori editor)
print("compat:", [x.get_name() for x in skeleton.get_editor_property("compatible_skeletons")])
mesh = import_mesh(skeleton)
assign_material(mesh)
import_lods(mesh)
assign_material(mesh)
pa = EAL.load_asset(PHYSICS)
if pa:
    mesh.set_editor_property("physics_asset", pa)
sockets(mesh)
EAL.save_loaded_asset(mesh)
print("bounds:", mesh.get_bounds())
print("SELESAI impor SK_Aksa2")
