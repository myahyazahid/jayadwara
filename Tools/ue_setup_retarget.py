"""Iterasi 6 (docs/13) — IK Rig + IK Retargeter Mannequin -> Jayadwara, lalu retarget animasi uji (Unreal Editor Python).

Membuat (ditimpa kalau sudah ada):
  /Game/Jayadwara/Characters/Aksa/Rig/IK_Mannequin            dari SKM_Manny_Simple (sumber animasi Third Person)
  /Game/Jayadwara/Characters/Jayadwara/Rig/IK_Jayadwara       dari SK_Jayadwara (nama tulang = Mannequin)
  /Game/Jayadwara/Characters/Jayadwara/Rig/RTG_Mannequin_To_Jayadwara
  /Game/Jayadwara/Characters/Jayadwara/Anims/ABP_Jayadwara    ABP_Unarmed hasil retarget (+ BlendSpace & anim yang dipakainya)
  /Game/Jayadwara/Characters/Jayadwara/Anims/<nama>_JD        animasi hasil retarget (ANIMS + referensi ABP)
Chain & solver FBIK dibuat otomatis (auto-characterize mengenali hierarki gaya Mannequin). Tulang scarf_*/cloth_*
sengaja tanpa chain (nanti Anim Dynamics di ABP). Pose retarget target disejajarkan ke sumber (A-pose 30° vs Manny).

Pakai: python Tools/ue_remote.py Tools/ue_setup_retarget.py
"""
import os
import warnings

import unreal

AKSA_RIG = "/Game/Jayadwara/Characters/Aksa/Rig"
JD = "/Game/Jayadwara/Characters/Jayadwara"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
ANIMS = [
    "/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed",          # locomotion: BS_Idle_Walk_Run, jump/fall/land, foot IK
    "/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_01",
    "/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_02",
    "/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_03",
]

# "Run IK Rig" (solver Full-Body IK) dimatikan: dengan mesh 45 m (skala di-bake, Iterasi 6b) solver ini menurunkan
# pinggul ±19 cm (setara skala manusia) & menggeser badan; retarget FK murni cocok dengan Manny dalam beberapa cm.
DISABLED_OPS = globals().get("DISABLED_OPS", ["Run IK Rig"])

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
ST = unreal.RetargetSourceOrTarget


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def fresh(folder, name, cls, factory):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    return asset_tools.create_asset(name, folder, cls, factory)


def make_ik_rig(folder, name, mesh):
    rig = fresh(folder, name, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    c = unreal.IKRigController.get_controller(rig)
    c.set_skeletal_mesh(mesh)
    if not c.apply_auto_generated_retarget_definition():
        unreal.log_warning(f"[Jayadwara] {name}: auto retarget definition gagal")
    c.apply_auto_fbik()
    chains = [(str(n), str(c.get_retarget_chain_start_bone(n)), str(c.get_retarget_chain_end_bone(n)))
              for n in (ch.get_editor_property("chain_name") for ch in c.get_retarget_chains())]
    log(f"{name}: root={c.get_retarget_root()} chain={len(chains)}")
    for ch in chains:
        log(f"   {ch[0]}: {ch[1]} -> {ch[2]}")
    EAL.save_loaded_asset(rig, only_if_is_dirty=False)
    return rig


def main():
    manny = EAL.load_asset(MANNY)
    jd_mesh = EAL.load_asset(f"{JD}/Mesh/SK_Jayadwara")
    ik_m = make_ik_rig(AKSA_RIG, "IK_Mannequin", manny)
    ik_j = make_ik_rig(f"{JD}/Rig", "IK_Jayadwara", jd_mesh)

    rtg = fresh(f"{JD}/Rig", "RTG_Mannequin_To_Jayadwara", unreal.IKRetargeter, unreal.IKRetargetFactory())
    r = unreal.IKRetargeterController.get_controller(rtg)
    r.set_ik_rig(ST.SOURCE, ik_m)
    r.set_ik_rig(ST.TARGET, ik_j)
    r.set_preview_mesh(ST.SOURCE, manny)
    r.set_preview_mesh(ST.TARGET, jd_mesh)
    r.add_default_ops()
    r.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    r.auto_align_all_bones(ST.TARGET, unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN)
    for op in DISABLED_OPS:
        i = r.get_index_of_op_by_name(op)
        if i >= 0:
            r.set_retarget_op_enabled(i, False)
    ops = [str(r.get_op_name(i)) + ("" if r.get_retarget_op_enabled(i) else " (mati)") for i in range(r.get_num_retarget_ops())]
    log(f"RTG ops: {ops}")
    EAL.save_loaded_asset(rtg, only_if_is_dirty=False)

    # animasi -> Anims/ langsung lewat modul editor C++ (Python duplicate_and_retarget menaruh hasil di /Game, dan
    # memindahkannya memutus rujukan ABP -> animasi di disk). ABP_Unarmed_JD lalu di-rename jadi ABP_Jayadwara.
    dest = f"{JD}/Anims"
    # BP_Jayadwara merujuk ABP_Jayadwara -> lepas dulu supaya ABP lama bisa dihapus (ue_setup_giant.py memasangnya lagi)
    bp_path = f"{JD}/BP_Jayadwara"
    if EAL.does_asset_exist(bp_path):
        bp = EAL.load_asset(bp_path)
        unreal.get_default_object(bp.generated_class()).get_editor_property("mesh").set_editor_property("anim_class", None)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        EAL.save_loaded_asset(bp, only_if_is_dirty=False)
        unreal.SystemLibrary.collect_garbage()
    # Hapus per aset (delete_directory diam-diam gagal kalau ABP masih dirujuk BP_Jayadwara -> ABP lama tertinggal)
    for a in (EAL.list_assets(dest, recursive=True) if EAL.does_directory_exist(dest) else []):
        EAL.delete_asset(str(a).split(".")[0])
    left = EAL.list_assets(dest, recursive=True) if EAL.does_directory_exist(dest) else []
    if left:
        unreal.log_error(f"[Jayadwara] gagal menghapus isi {dest}: {left}")
        return
    with warnings.catch_warnings():                             # ratusan "Track with name ... already exists" (UE 5.6.1, tak berbahaya)
        warnings.simplefilter("ignore")
        unreal.JDEditorToolsLibrary.retarget_assets_to_folder([EAL.load_asset(a) for a in ANIMS], manny, jd_mesh, rtg,
                                                              dest, "_JD", True)
    EAL.save_directory(dest, only_if_is_dirty=False, recursive=True)
    if EAL.does_asset_exist(f"{dest}/ABP_Unarmed_JD"):
        EAL.rename_asset(f"{dest}/ABP_Unarmed_JD", f"{dest}/ABP_Jayadwara")
        EAL.save_asset(f"{dest}/ABP_Jayadwara", only_if_is_dirty=False)
    names = sorted(str(n).rsplit("/", 1)[1].split(".")[0] for n in EAL.list_assets(dest, recursive=False))
    log(f"retarget: {len(names)} aset di {dest}")

    # Cek isi file di disk (bukan memori): ABP harus merujuk BlendSpace & anim di Anims/.
    path = os.path.join(unreal.Paths.project_content_dir(), "Jayadwara/Characters/Jayadwara/Anims/ABP_Jayadwara.uasset")
    with open(path, "rb") as f:
        raw = f.read()
    need = [b"Anims/BS_Idle_Walk_Run_JD", b"Anims/MM_Jump_JD", b"Anims/MM_Land_JD", b"Anims/MM_Fall_Loop_JD"]
    missing = [n.decode() for n in need if n not in raw]
    if missing:
        unreal.log_error(f"[Jayadwara] ABP_Jayadwara di disk tidak merujuk: {missing}")
    else:
        log("ABP_Jayadwara di disk merujuk BlendSpace & anim di Anims/ (OK)")

main()
