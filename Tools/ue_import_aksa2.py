"""Aksa2 (model Tripo, docs/19 + laporan Hermes 15 Okt 2026) — impor ke folder karakter proyek (Unreal Editor Python).

Berasal dari Hermes/Tools/aksa2_71_import_mesh.py (branch hermes/aksa2), dipindah ke /Game/Jayadwara/Characters/Aksa2/.
Sumber: Art/Export/SK_Aksa2.fbx + SK_Aksa2_LOD1..3.fbx + SK_Aksa2_sockets.json + Art/Export/Textures_Aksa2/*.png.
Membuat / mengisi ulang (idempoten):
  Aksa2/Mesh/SKEL_Aksa2             salinan SK_Mannequin + Compatible Skeleton SK_Mannequin (disimpan paksa)
  Aksa2/Mesh/SK_Aksa2               4 LOD, 1 slot, 7 socket berofset, physics = PA_Mannequin
  Aksa2/Textures/T_Aksa2_Body_*     BC (sRGB), N, ORM  (nama Body supaya tidak menimpa T_Aksa2_BC/N/ORM milik spike lama)
  Aksa2/Materials/MI_Aksa2_Body     instance dari M_Aksa2_Master (parameter BaseColor, Normal, ORM)
Tidak menyentuh SK_Mannequin, SK_Aksa, BP_Aksa, SK_Aksa2_Spike. Pemasangan di game (BP_Aksa2 paralel): Tools/ue_setup_aksa2.py.

Kombinasi WAJIB (docs/19 §6.4, docs/25): FBX BAKE_CM=100 + importer FBX LAMA (Interchange.FeatureFlags.Import.FBX 0)
+ Compatible Skeleton SK_Mannequin TERSIMPAN di SKEL_Aksa2. Interchange membuat karakter 100x raksasa; compat yang tidak
tersimpan membuat mesh hancur (pita hitam) hanya saat animasi, padahal rest pose normal.

Pakai (editor terbuka, TIDAK sedang Play):
  python Tools/ue_remote.py Tools/ue_import_aksa2.py
"""
import json
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EXPORT = os.path.join(REPO, "Art", "Export")
TEX_DIR = os.path.join(EXPORT, "Textures_Aksa2")
DEST = "/Game/Jayadwara/Characters/Aksa2"
MESH_DIR, TEX_DEST, MAT_DIR = f"{DEST}/Mesh", f"{DEST}/Textures", f"{DEST}/Materials"
MESH_NAME = "SK_Aksa2"
SKELETON = f"{MESH_DIR}/SKEL_Aksa2"
MI = f"{MAT_DIR}/MI_Aksa2_Body"
MASTER = f"{MAT_DIR}/M_Aksa2_Master"
MANNY_SKEL = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
PHYSICS = "/Game/Characters/Mannequins/Rigs/PA_Mannequin"
LOD_FILES = {1: "SK_Aksa2_LOD1.fbx", 2: "SK_Aksa2_LOD2.fbx", 3: "SK_Aksa2_LOD3.fbx"}
LOD_SCREEN_SIZE = {0: 1.0, 1: 0.45, 2: 0.22, 3: 0.10}
TEXTURES = {  # nama aset: (berkas, sRGB, kompresi)
    "T_Aksa2_Body_BC": ("T_Aksa2_D.png", True, unreal.TextureCompressionSettings.TC_DEFAULT),
    "T_Aksa2_Body_N": ("T_Aksa2_N.png", False, unreal.TextureCompressionSettings.TC_NORMALMAP),
    "T_Aksa2_Body_ORM": ("T_Aksa2_ORM.png", False, unreal.TextureCompressionSettings.TC_MASKS),
}
TEX_PARAM = {"T_Aksa2_Body_BC": "BaseColor", "T_Aksa2_Body_N": "Normal", "T_Aksa2_Body_ORM": "ORM"}

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()


def log(msg):
    unreal.log(f"[Aksa2] {msg}")


def legacy_fbx(fn):
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    try:
        return fn()
    finally:
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")


def ensure_dirs():
    for d in (MESH_DIR, TEX_DEST, MAT_DIR):
        if not EAL.does_directory_exist(d):
            EAL.make_directory(d)


def ensure_skeleton():
    man = EAL.load_asset(MANNY_SKEL)
    assert man, f"{MANNY_SKEL} tidak ada"
    if EAL.does_asset_exist(SKELETON):
        skel = EAL.load_asset(SKELETON)
    else:
        skel = EAL.duplicate_asset(MANNY_SKEL, SKELETON)
        log("SKEL_Aksa2 dibuat dari SK_Mannequin")
    if man not in list(skel.get_editor_property("compatible_skeletons")):
        skel.add_compatible_skeleton(man)
    EAL.save_loaded_asset(skel, False)           # compat HARUS tersimpan (save default hanya menyimpan aset dirty)
    log("compat: " + ", ".join(x.get_name() for x in skel.get_editor_property("compatible_skeletons")))
    return skel


def import_textures():
    out = {}
    for name, (fname, srgb, comp) in TEXTURES.items():
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", os.path.join(TEX_DIR, fname))
        t.set_editor_property("destination_path", TEX_DEST)
        t.set_editor_property("destination_name", name)
        t.set_editor_property("automated", True)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("save", False)
        asset_tools.import_asset_tasks([t])
        tex = EAL.load_asset(f"{TEX_DEST}/{name}")
        assert tex, f"tekstur {name} gagal diimpor"
        tex.set_editor_property("srgb", srgb)
        tex.set_editor_property("compression_settings", comp)
        EAL.save_loaded_asset(tex, False)
        out[name] = tex
        log(f"tekstur {name} <- {fname}")
    return out


def ensure_material(tex):
    master = EAL.load_asset(MASTER)
    assert master, f"{MASTER} tidak ada"
    if not master.get_editor_property("used_with_skeletal_mesh"):
        # Tanpa flag ini mesh skeletal memakai material DEFAULT (abu-abu) di Play (peringatan "missing bUsedWithSkeletalMesh").
        master.set_editor_property("used_with_skeletal_mesh", True)
        MEL.recompile_material(master)
        EAL.save_loaded_asset(master, False)
        log("M_Aksa2_Master: Used With Skeletal Mesh dinyalakan")
    if EAL.does_asset_exist(MI):
        mi = EAL.load_asset(MI)
    else:
        mi = asset_tools.create_asset("MI_Aksa2_Body", MAT_DIR, unreal.MaterialInstanceConstant,
                                      unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, master)
    for name, param in TEX_PARAM.items():
        MEL.set_material_instance_texture_parameter_value(mi, param, tex[name])
    MEL.update_material_instance(mi)
    EAL.save_loaded_asset(mi, False)
    log("MI_Aksa2_Body siap")
    return mi


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
    d.set_editor_property("import_morph_targets", False)     # morph wajah menyusul (H3b → Claude)
    d.set_editor_property("use_t0_as_ref_pose", False)
    d.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", os.path.join(EXPORT, "SK_Aksa2.fbx"))
    t.set_editor_property("destination_path", MESH_DIR)
    t.set_editor_property("destination_name", MESH_NAME)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", False)
    t.set_editor_property("options", ui)
    legacy_fbx(lambda: asset_tools.import_asset_tasks([t]))
    mesh = EAL.load_asset(f"{MESH_DIR}/{MESH_NAME}")
    assert isinstance(mesh, unreal.SkeletalMesh), "SK_Aksa2 tidak terimpor sebagai SkeletalMesh"
    log("skeleton mesh: " + mesh.get_editor_property("skeleton").get_path_name())
    return mesh


def import_lods(mesh):
    sub = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)

    def run():
        for i, f in LOD_FILES.items():
            log(f"LOD{i} <- {f}: {sub.import_lod(mesh, i, os.path.join(EXPORT, f))}")
    legacy_fbx(run)
    infos = []
    for i, info in enumerate(mesh.get_editor_property("lod_info")):
        if i in LOD_SCREEN_SIZE:
            ss = unreal.PerPlatformFloat()
            ss.set_editor_property("default", LOD_SCREEN_SIZE[i])
            info.set_editor_property("screen_size", ss)
        infos.append(info)
    mesh.set_editor_property("lod_info", infos)
    log(f"LOD: {len(infos)} level")


def assign_material(mesh, mi):
    mats = []
    for m in mesh.get_editor_property("materials"):
        m.set_editor_property("material_interface", mi)
        mats.append(m)
    mesh.set_editor_property("materials", mats)
    log(f"material: {len(mats)} slot -> {mi.get_name()}")


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
        log(f"socket {s['name']} @ {s['bone']} rel=({rel.x:.1f}, {rel.y:.1f}, {rel.z:.1f})")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        raise RuntimeError("Editor sedang Play (PIE), hentikan dulu")
    ensure_dirs()
    skeleton = ensure_skeleton()
    tex = import_textures()
    mi = ensure_material(tex)
    mesh = import_mesh(skeleton)
    assign_material(mesh, mi)
    import_lods(mesh)
    assign_material(mesh, mi)                     # import_lod bisa mengembalikan slot
    pa = EAL.load_asset(PHYSICS)
    if pa:
        mesh.set_editor_property("physics_asset", pa)
    sockets(mesh)
    EAL.save_loaded_asset(mesh, False)
    b = mesh.get_bounds()
    log(f"bounds: extent=({b.box_extent.x:.1f}, {b.box_extent.y:.1f}, {b.box_extent.z:.1f}) cm "
        f"(harus tinggi 180,6 cm: extent Z kira-kira 90,3)")
    log("SELESAI impor SK_Aksa2")


main()
