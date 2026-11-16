"""Tuyul — IK Rig + IK Retargeter (Manny -> Tuyul) di /Game/Jayadwara/Characters/Tuyul/Rig (Unreal Editor Python).

Berasal dari Hermes/Tools/tuyul_63_retarget.py (branch hermes/tuyul), tanpa bagian retarget animasi uji.
Pola: Tools/ue_setup_retarget.py, Tools/ue_setup_jayadwara2.py.
Prasyarat: Tools/ue_import_tuyul.py sudah dijalankan (SK_Tuyul ada).
Membuat / mengisi ulang (idempoten, hanya di folder Tuyul/Rig):
  Rig/IK_Tuyul                   IK Rig dari SK_Tuyul (retarget chain otomatis + FBIK otomatis)
  Rig/RTG_Mannequin_To_Tuyul     sumber IK_Mannequin (Manny) -> target IK_Tuyul; chain EXACT, align CHAIN_TO_CHAIN
Op "Run IK Rig" dimatikan: FBIK pada proporsi Tuyul menurunkan pinggul; FK murni cukup (uji Hermes K6).
Tangan Tuyul hanya 3 jari (thumb/index/middle); ring/pinky Manny tidak punya padanan, dan itu wajar.
Tidak membuat BP/ABP/level (di luar scope fase aktif, docs/27 T9; Ep 2 masuk Fase 4).

Pakai (editor terbuka, TIDAK sedang Play):
  python Tools/ue_remote.py Tools/ue_setup_tuyul.py
Kalau IK_Tuyul + RTG sudah ada, skrip tidak menyentuhnya (melindungi setelan manual di editor).
"""
import unreal

EAL = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
ST = unreal.RetargetSourceOrTarget

RIG_DIR = "/Game/Jayadwara/Characters/Tuyul/Rig"
TUYUL_MESH_PATH = "/Game/Jayadwara/Characters/Tuyul/Mesh/SK_Tuyul"
MANNY_MESH_PATH = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
IK_MANNY_PATH = "/Game/Jayadwara/Characters/Aksa/Rig/IK_Mannequin"
DISABLED_OPS = ["Run IK Rig"]
REBUILD = "--rebuild" in __import__("sys").argv   # default: kalau rig sudah ada, JANGAN ditimpa (ada setelan manual)


def log(msg):
    unreal.log(f"[Tuyul] {msg}")


def fresh(folder, name, cls, factory):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    return AT.create_asset(name, folder, cls, factory)


def ensure_mannequin_bones():
    """SK_Mannequin di disk hanya 92 tulang; tulang lain ditambah UE saat mesh pemakainya dimuat.
    Retarget SEBELUM itu bisa crash (Index -1). Muat pemakai skeleton dulu."""
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
    if not c.apply_auto_generated_retarget_definition():
        unreal.log_warning(f"[Tuyul] {name}: auto retarget definition gagal")
    c.apply_auto_fbik()
    chains = [str(ch.get_editor_property("chain_name")) for ch in c.get_retarget_chains()]
    log(f"{name}: root={c.get_retarget_root()} chain={len(chains)}: {chains}")
    EAL.save_loaded_asset(rig, only_if_is_dirty=False)
    return rig


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        raise RuntimeError("Editor sedang Play (PIE) — hentikan dulu")
    EAL.make_directory(RIG_DIR)
    if not REBUILD and all(EAL.does_asset_exist(f"{RIG_DIR}/{n}") for n in ("IK_Tuyul", "RTG_Mannequin_To_Tuyul")):
        log("IK_Tuyul + RTG_Mannequin_To_Tuyul sudah ada: dibiarkan (ulang dari nol dengan argumen --rebuild).")
        return
    ensure_mannequin_bones()

    manny = EAL.load_asset(MANNY_MESH_PATH)
    tuyul = EAL.load_asset(TUYUL_MESH_PATH)
    ik_m = EAL.load_asset(IK_MANNY_PATH)
    assert manny and tuyul and ik_m, "mesh/IK sumber tidak lengkap (jalankan Tools/ue_import_tuyul.py dulu)"

    log("=== IK_Tuyul ===")
    ik_t = make_ik_rig("IK_Tuyul", tuyul)

    log("=== RTG_Mannequin_To_Tuyul ===")
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
    log("=== SETUP RIG TUYUL SELESAI ===")


main()
