"""Animasi Mixamo -> Aksa (Manny): import FBX, IK Rig Mixamo, retarget (Unreal Editor Python).

Revisi jurus Iterasi 2–3 (docs/07 "Daftar jurus", "Dodge per arah", "Parry"). Animasi placeholder Fase 1 dari Mixamo
(docs/23 bagian 6.1); skrip combo/dodge/parry memakai hasilnya otomatis kalau ada.

Alur file (mixamo/README.md): developer download dari mixamo.com ke mixamo/result/ (nama file = peran di ROLES,
plus ybot.fbx = Y Bot With Skin), agent memeriksa lalu memindahkan ke Art/Mixamo/ (LFS) — folder yang dibaca skrip ini.
Pakai: python Tools/ue_remote.py Tools/ue_import_mixamo.py
Lalu jalankan ulang: ue_setup_light_combo.py, ue_setup_defense.py, ue_setup_parry.py (urutan itu).

Membuat (ditimpa tiap jalan):
  Aksa/Anims/Mixamo/Raw/SK_Mixamo_YBot (+ skeleton)    mesh sumber retarget
  Aksa/Anims/Mixamo/Raw/A_Aksa_Mx_<peran>              animasi asli Mixamo
  Aksa/Rig/IK_Mixamo, Aksa/Rig/RTG_Mixamo_To_Manny     IK Rig (auto-characterize) + retargeter
  Aksa/Anims/Mixamo/A_Aksa_Mx_<peran>                  hasil retarget ke skeleton Mannequin (dipakai skrip setup)
"""
import os
import warnings

import unreal

AKSA = "/Game/Jayadwara/Characters/Aksa"
RIG = f"{AKSA}/Rig"
MX = f"{AKSA}/Anims/Mixamo"
RAW = f"{MX}/Raw"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
SOURCE_DIR = "Art/Mixamo"            # relatif ke folder proyek; diisi agent dari mixamo/result/
MESH_FILE = "ybot.fbx"
MESH_NAME = "SK_Mixamo_YBot"

# peran (nama file tanpa .fbx) -> jurus (docs/07). Yang tidak ada dilewati; skrip setup tetap pakai placeholder.
ROLES = {
    "light_01": "Jab",
    "light_02": "Cross",
    "light_03": "Hook",
    "light_04": "Tendangan putar belakang (dwi huryeo chagi) — Mixamo: Spinning Back Kick",
    "lunge": "Terjang: lompat kecil, tangan kanan dari atas ke dada",
    "back": "Pukul mundur",
    "heavy": "Pukulan putar",
    "finisher_01": "Tendangan belakang (dwi chagi) — Mixamo: Back Kick",
    "finisher_02": "Tendangan ganda melompat (narae chagi) — Mixamo: Double Kick",
    "finisher_03": "Finisher 3 (ringan x3 -> berat), dipilih developer",
    "air": "Tendangan terbang memutar — Mixamo: Tornado Kick",
    "air_slam": "Hantaman ke bawah",
    "dodge_back": "Salto belakang — Mixamo: Back Flip",
    "dodge_left": "Guling kiri — Mixamo: Dodge Roll / Cartwheel",
    "dodge_right": "Guling kanan — Mixamo: Dodge Roll / Cartwheel (Mirror)",
    "dodge_forward": "Langkah cepat — Mixamo: Quick Step / Dodge Forward",
    "parry_01": "Tepis luar",
    "parry_02": "Tepis dalam",
    "counter": "Serangan balik setelah parry",
    "stagger": "Terhuyung (Iterasi 4) — Mixamo: Hit Reaction",
}

EAL = unreal.EditorAssetLibrary
ST = unreal.RetargetSourceOrTarget
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
problems = []


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def fail(msg):
    problems.append(msg)
    unreal.log_error(f"[Jayadwara] {msg}")


def import_fbx(path, dest, name, skeleton=None):
    """Importer FBX lama (sama dengan ue_import_aksa.py): Interchange mengubah skala/hierarki Mixamo."""
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_materials", False)
    ui.set_editor_property("import_textures", False)
    ui.set_editor_property("create_physics_asset", False)
    if skeleton:
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
        ui.set_editor_property("original_import_type", unreal.FBXImportType.FBXIT_ANIMATION)
        ui.set_editor_property("import_mesh", False)
        ui.set_editor_property("import_animations", True)
        ui.set_editor_property("skeleton", skeleton)
        a = ui.get_editor_property("anim_sequence_import_data")
        a.set_editor_property("convert_scene", True)
        a.set_editor_property("import_bone_tracks", True)
        a.set_editor_property("remove_redundant_keys", False)
    else:
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
        ui.set_editor_property("import_mesh", True)
        ui.set_editor_property("import_as_skeletal", True)
        ui.set_editor_property("import_animations", False)
        d = ui.get_editor_property("skeletal_mesh_import_data")
        d.set_editor_property("convert_scene", True)
        d.set_editor_property("use_t0_as_ref_pose", False)
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", path)
    t.set_editor_property("destination_path", dest)
    t.set_editor_property("destination_name", name)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", True)
    t.set_editor_property("options", ui)
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    try:
        asset_tools.import_asset_tasks([t])
    finally:
        unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 1")


def fresh(folder, name, cls, factory):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    return asset_tools.create_asset(name, folder, cls, factory)


def make_ik_rig(name, mesh):
    rig = fresh(RIG, name, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    c = unreal.IKRigController.get_controller(rig)
    c.set_skeletal_mesh(mesh)
    if not c.apply_auto_generated_retarget_definition():
        fail(f"{name}: auto retarget definition gagal (skeleton tidak dikenali)")
    c.apply_auto_fbik()
    log(f"{name}: root={c.get_retarget_root()} chain={len(c.get_retarget_chains())}")
    EAL.save_loaded_asset(rig, only_if_is_dirty=False)
    return rig


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara] PIE sedang jalan — hentikan Play dulu")
        return
    folder = os.path.normpath(os.path.join(unreal.Paths.project_dir(), SOURCE_DIR))
    files = {f[:-4].lower(): os.path.join(folder, f) for f in (os.listdir(folder) if os.path.isdir(folder) else [])
             if f.lower().endswith(".fbx")}
    if MESH_FILE[:-4] not in files:
        unreal.log_error(f"[Jayadwara] {MESH_FILE} (Y Bot With Skin) tidak ada di {folder}")
        return
    unknown = sorted(k for k in files if k not in ROLES and k != MESH_FILE[:-4])
    if unknown:
        fail(f"nama file tidak dikenal (lihat ROLES): {unknown}")

    import_fbx(files[MESH_FILE[:-4]], RAW, MESH_NAME)
    mesh = EAL.load_asset(f"{RAW}/{MESH_NAME}")
    if not isinstance(mesh, unreal.SkeletalMesh):
        unreal.log_error(f"[Jayadwara] {MESH_NAME} gagal diimpor")
        return
    skeleton = mesh.get_editor_property("skeleton")
    log(f"{MESH_NAME}: skeleton {skeleton.get_name()}")

    anims = []
    for role in ROLES:
        if role not in files:
            continue
        name = f"A_Aksa_Mx_{role}"
        import_fbx(files[role], RAW, name, skeleton)
        seq = EAL.load_asset(f"{RAW}/{name}")
        if not isinstance(seq, unreal.AnimSequence):
            fail(f"{role}.fbx: tidak menghasilkan AnimSequence")
            continue
        anims.append(seq)
        log(f"{name}: {unreal.AnimationLibrary.get_sequence_length(seq):.2f} s — {ROLES[role]}")
    if not anims:
        unreal.log_error("[Jayadwara] tidak ada animasi peran yang diimpor")
        return

    manny = EAL.load_asset(MANNY)
    ik_src = make_ik_rig("IK_Mixamo", mesh)
    ik_dst = EAL.load_asset(f"{RIG}/IK_Mannequin") or make_ik_rig("IK_Mannequin", manny)
    rtg = fresh(RIG, "RTG_Mixamo_To_Manny", unreal.IKRetargeter, unreal.IKRetargetFactory())
    r = unreal.IKRetargeterController.get_controller(rtg)
    r.set_ik_rig(ST.SOURCE, ik_src)
    r.set_ik_rig(ST.TARGET, ik_dst)
    r.set_preview_mesh(ST.SOURCE, mesh)
    r.set_preview_mesh(ST.TARGET, manny)
    r.add_default_ops()
    r.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    r.auto_align_all_bones(ST.TARGET, unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN)
    EAL.save_loaded_asset(rtg, only_if_is_dirty=False)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unreal.JDEditorToolsLibrary.retarget_assets_to_folder(anims, mesh, manny, rtg, MX, "", False)
    EAL.save_directory(MX, only_if_is_dirty=False, recursive=False)
    done = [a.get_name() for a in anims if EAL.does_asset_exist(f"{MX}/{a.get_name()}")]
    log(f"retarget ke Manny: {len(done)}/{len(anims)} animasi di {MX}")
    if len(done) < len(anims):
        fail(f"gagal retarget: {sorted(set(a.get_name() for a in anims) - set(done))}")

    if problems:
        unreal.log_warning(f"[Jayadwara] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("import Mixamo selesai — jalankan ulang ue_setup_light_combo.py, ue_setup_defense.py, ue_setup_parry.py")


main()
