"""Tuyul K6 — buat IK_Tuyul + RTG_Mannequin_To_Tuyul di sandbox, lalu retarget animasi Manny.

Pola mengikuti Tools/ue_setup_retarget.py & ue_setup_jayadwara2.py (proyek):
  IK Rig     : IKRigController.set_skeletal_mesh(mesh) + apply_auto_generated_retarget_definition() + apply_auto_fbik()
  Retargeter : set_ik_rig(SOURCE/TARGET) + set_preview_mesh(SOURCE/TARGET) + add_default_ops()
               + auto_map_chains(EXACT, True) + auto_align_all_bones(TARGET, CHAIN_TO_CHAIN)
  Batch retarget: JDEditorToolsLibrary.retarget_assets_to_folder (langsung tulis ke folder sandbox).

Dijalankan: python Tools/ue_remote.py Hermes/Tools/tuyul_63_retarget.py
"""
import warnings

import unreal

EAL = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
ST = unreal.RetargetSourceOrTarget

RIG_DIR = "/Game/Hermes/Tuyul/Rig"
ANIM_DIR = "/Game/Hermes/Tuyul/Anims"
TUYUL_MESH_PATH = "/Game/Hermes/Tuyul/Mesh/SK_Tuyul"
MANNY_MESH_PATH = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
IK_MANNY_PATH = "/Game/Jayadwara/Characters/Aksa/Rig/IK_Mannequin"
ANIM_ROOT = "/Game/Characters/Mannequins/Anims/Unarmed/"
RETARGET_ANIMS = ["MM_Idle", "Jog/MF_Unarmed_Jog_Fwd"]
SUFFIX = "_Tuyul"
DISABLED_OPS = ["Run IK Rig"]          # FBIK pada proporsi Tuyul menurunkan pinggul; FK murni cukup untuk uji K6


def log(msg):
    unreal.log(f"[Tuyul K6] {msg}")


def fresh(folder, name, cls, factory):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    return AT.create_asset(name, folder, cls, factory)


def ensure_mannequin_bones():
    """SK_Mannequin di disk hanya 92 tulang; tulang lain ditambah UE saat mesh pemakainya dimuat.
    Batch retarget SEBELUM itu bisa crash (Index -1). Muat pemakai skeleton dulu."""
    for m in (MANNY_MESH_PATH, "/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple",
              "/Game/Jayadwara/Characters/Aksa/Mesh/SK_Aksa"):
        if EAL.does_asset_exist(m):
            EAL.load_asset(m)
    sk = EAL.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
    n = len(unreal.AnimPoseExtensions.get_bone_names(unreal.AnimPoseExtensions.get_reference_pose(sk)))
    log(f"SK_Mannequin: {n} tulang di memori")
    if n < 161:
        raise RuntimeError(f"SK_Mannequin hanya {n} tulang - retarget dibatalkan (akan crash)")


def make_ik_rig(name, mesh):
    rig = fresh(RIG_DIR, name, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    c = unreal.IKRigController.get_controller(rig)
    c.set_skeletal_mesh(mesh)
    ok = c.apply_auto_generated_retarget_definition()
    if not ok:
        unreal.log_warning(f"[Tuyul K6] {name}: auto retarget definition gagal")
    c.apply_auto_fbik()
    chains = [str(ch.get_editor_property("chain_name")) for ch in c.get_retarget_chains()]
    log(f"{name}: root={c.get_retarget_root()} chain={len(chains)}: {chains}")
    EAL.save_loaded_asset(rig, only_if_is_dirty=False)
    return rig


def main():
    EAL.make_directory(RIG_DIR)
    EAL.make_directory(ANIM_DIR)

    log("=== 0) pastikan tulang SK_Mannequin lengkap ===")
    ensure_mannequin_bones()

    manny = EAL.load_asset(MANNY_MESH_PATH)
    tuyul = EAL.load_asset(TUYUL_MESH_PATH)
    ik_m = EAL.load_asset(IK_MANNY_PATH)
    assert manny and tuyul and ik_m, "mesh/IK sumber tidak lengkap"

    log("=== 1) IK_Tuyul ===")
    ik_t = make_ik_rig("IK_Tuyul", tuyul)

    log("=== 2) RTG_Mannequin_To_Tuyul ===")
    rtg = fresh(RIG_DIR, "RTG_Mannequin_To_Tuyul", unreal.IKRetargeter, unreal.IKRetargetFactory())
    r = unreal.IKRetargeterController.get_controller(rtg)
    r.set_ik_rig(ST.SOURCE, ik_m)
    r.set_ik_rig(ST.TARGET, ik_t)
    r.set_preview_mesh(ST.SOURCE, manny)
    r.set_preview_mesh(ST.TARGET, tuyul)
    r.add_default_ops()
    r.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    r.auto_align_all_bones(ST.TARGET, unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN)
    for op in DISABLED_OPS:
        i = r.get_index_of_op_by_name(op)
        if i >= 0:
            r.set_retarget_op_enabled(i, False)
    log("RTG ops: " + str([str(r.get_op_name(i)) + ("" if r.get_retarget_op_enabled(i) else " (mati)")
                           for i in range(r.get_num_retarget_ops())]))
    EAL.save_loaded_asset(rtg, only_if_is_dirty=False)

    log("=== 3) retarget animasi -> " + ANIM_DIR + " ===")
    if EAL.does_directory_exist(ANIM_DIR):
        for a in EAL.list_assets(ANIM_DIR, recursive=True):
            EAL.delete_asset(str(a).split(".")[0])
    left = EAL.list_assets(ANIM_DIR, recursive=True) if EAL.does_directory_exist(ANIM_DIR) else []
    if left:
        raise RuntimeError(f"gagal membersihkan {ANIM_DIR}: {left}")

    assets = []
    for rel in RETARGET_ANIMS:
        p = f"{ANIM_ROOT}{rel}"
        a = EAL.load_asset(p)
        if a is None:
            raise RuntimeError(f"anim sumber tidak ada: {p}")
        assets.append(a)
        log(f"  sumber: {p}")
    with warnings.catch_warnings():                    # ratusan "Track with name ... already exists" (UE 5.6.1, tak berbahaya)
        warnings.simplefilter("ignore")
        unreal.JDEditorToolsLibrary.retarget_assets_to_folder(assets, manny, tuyul, rtg, ANIM_DIR, SUFFIX, True)
    EAL.save_directory(ANIM_DIR, only_if_is_dirty=False, recursive=True)
    names = sorted(str(n).rsplit("/", 1)[1].split(".")[0] for n in EAL.list_assets(ANIM_DIR, recursive=False))
    log(f"retarget: {len(names)} aset di {ANIM_DIR}: {names}")

    log("=== 4) verifikasi hasil retarget ===")
    for nm in names:
        seq = EAL.load_asset(f"{ANIM_DIR}/{nm}")
        sk = seq.get_editor_property("skeleton") if hasattr(seq, "get_editor_property") else None
        log(f"  {nm}: skeleton={sk.get_path_name() if sk else None}")

    # bentuk: pose idle t=0 vs t=0.5 harus berbeda & tidak kolaps (pelvis z > 20 cm)
    seq = EAL.load_asset(f"{ANIM_DIR}/MM_Idle{SUFFIX}")
    if seq:
        for t in (0.0, 0.5):
            pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, unreal.AnimPoseEvaluationOptions())
            g = lambda b: unreal.AnimPoseExtensions.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation
            p, h = g("pelvis"), g("head")
            log(f"  idle t={t}: pelvis z={p.z:.1f} head z={h.z:.1f} (cm)")

    log("=== RETARGET K6 SELESAI ===")


main()
