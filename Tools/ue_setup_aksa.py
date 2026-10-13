"""Iterasi 6 (docs/19) — pasang SK_Aksa di game: Physics Asset, ABP dengan Anim Dynamics kain, dan BP_Aksa (Unreal Editor Python).

Butuh: SK_Aksa hasil Tools/ue_import_aksa.py (skeleton = SK_Mannequin asli) dan modul editor C++ JayadwaraEditor
(unreal.JDEditorToolsLibrary, sama dengan ue_setup_giant.py).
Membuat / mengisi ulang:
  Aksa/Mesh/PA_Aksa      salinan PA_Mannequin, dibangun ulang dari mesh Aksa (1 kapsul per anggota badan, tanpa sash_/jacket_)
  Aksa/Anims/ABP_Aksa    salinan ABP_Unarmed (logika gerak identik, foot IK Mannequin tetap: proporsi Aksa = Manny) + node
                         Anim Dynamics untuk ujung jaket jacket_l/r_01..02 (selendang dilepas sementara)
  UI/Portraits           T_Aksa_Portrait_{Neutral,Smile,Angry} (tekstur UI) dari Art/Export/Portraits
  BP_Aksa                mesh = SK_Aksa + ABP_Aksa (menggantikan SKM_Manny_Simple + ABP_Unarmed). Tidak ada perubahan kode C++.
Keputusan: SK_Aksa memakai skeleton Mannequin asli (jalur (a), docs/19), jadi ia LANGSUNG menjadi mesh logika (docs/12 sudah
mengizinkan); MetaHuman placeholder tidak pernah dibuat sehingga lapisan "mesh visual" tidak diperlukan.
Pakai: python Tools/ue_remote.py Tools/ue_setup_aksa.py
"""
import unreal

AK = "/Game/Jayadwara/Characters/Aksa"
EAL = unreal.EditorAssetLibrary


def log(msg):
    unreal.log(f"[Aksa] {msg}")


PA_BODIES = ["pelvis", "spine_01", "spine_03", "spine_05", "neck_01", "head",
             "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
             "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r"]
PA_EXCLUDE = ["sash_", "jacket_", "ik_"]          # digerakkan Anim Dynamics / tulang IK, bukan body fisika
# (awal, akhir, ayun°, twist°): selendang batik panjang lebih lentur dari ujung depan jaket
# Selendang (sash_01..06) DILEPAS dulu (developer 12 Okt 2026: desain belum pas; objek disembunyikan di blend, tulang tetap ada).
# Catatan uji PIE: rantai 6 body berskala manusia melar ke bawah dengan iterasi solver bawaan (gravitasi > batas linear);
# saat selendang kembali, naikkan NumSolverIterationsPre/PostUpdate di JDEditorToolsLibrary atau pakai GravityScale kecil.
CHAINS = [("jacket_l_01", "jacket_l_02", 22.0, 4.0), ("jacket_r_01", "jacket_r_02", 22.0, 4.0)]
LIMIT_BONES = ["thigh_l", "thigh_r"]
LIMIT_RADIUS = 6.5                                # cm. Bola di tengah tulang paha; selendang berpose rest ±9 cm dari sumbu paha.
# Uji PIE 12 Okt 2026: pelvis + radius 10 cm -> selendang mulai DI DALAM bola, terdorong keras dan rantai "meledak" (melar >2 m).
BODY_EXTENT = 2.5                                 # cm
SIM_SPACE_COMPONENT, ACC_SCALE, GRAVITY_SCALE = 0, 0.1, 1.0


def dup(src, folder, name):
    path = f"{folder}/{name}"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    a = EAL.duplicate_asset(src, path)
    log(f"{name} dibuat dari {src.split('/')[-1]}")
    return a


def import_portraits():
    """Potret dialog (Art/Export/Portraits, dari aksa_61_portraits.py) -> /Game/Jayadwara/UI/Portraits, pengaturan tekstur UI."""
    import os
    src = os.path.join(unreal.SystemLibrary.get_project_directory(), "Art", "Export", "Portraits")
    if not os.path.isdir(src):
        log("potret: folder tidak ada (jalankan Art/Scripts/aksa_61_portraits.py)")
        return
    tasks = []
    for f in sorted(os.listdir(src)):
        if f.startswith("T_Aksa_Portrait_") and f.endswith(".png"):
            t = unreal.AssetImportTask()
            t.set_editor_property("filename", os.path.join(src, f))
            t.set_editor_property("destination_path", "/Game/Jayadwara/UI/Portraits")
            t.set_editor_property("automated", True)
            t.set_editor_property("replace_existing", True)
            t.set_editor_property("save", False)
            tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for t in tasks:
        name = os.path.splitext(os.path.basename(t.get_editor_property("filename")))[0]
        tex = EAL.load_asset(f"/Game/Jayadwara/UI/Portraits/{name}")
        if tex:
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
            tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
            tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
            EAL.save_loaded_asset(tex, only_if_is_dirty=False)
    log(f"potret dialog: {len(tasks)} -> /Game/Jayadwara/UI/Portraits")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Aksa] Editor sedang Play (PIE) — hentikan dulu lalu jalankan ulang")
        return
    mesh = EAL.load_asset(f"{AK}/Mesh/SK_Aksa")
    pa = dup("/Game/Characters/Mannequins/Rigs/PA_Mannequin", f"{AK}/Mesh", "PA_Aksa")
    n = unreal.JDEditorToolsLibrary.rebuild_physics_asset(pa, mesh, PA_BODIES, PA_EXCLUDE, 30.0)
    mesh.set_editor_property("physics_asset", pa)
    EAL.save_loaded_asset(pa, only_if_is_dirty=False)
    EAL.save_loaded_asset(mesh, only_if_is_dirty=False)
    log(f"PA_Aksa: {n} body (target {len(PA_BODIES)}), terpasang di SK_Aksa")

    abp = dup("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed", f"{AK}/Anims", "ABP_Aksa")
    chains = []
    for start, end, swing, twist in CHAINS:
        c = unreal.JDAnimDynamicsChain()
        c.set_editor_property("start_bone", start)
        c.set_editor_property("end_bone", end)
        c.set_editor_property("swing_limit", swing)
        c.set_editor_property("twist_limit", twist)
        c.set_editor_property("box_extents", unreal.Vector(BODY_EXTENT, BODY_EXTENT, BODY_EXTENT))
        c.set_editor_property("collision_radius", BODY_EXTENT)
        chains.append(c)
    k = unreal.JDEditorToolsLibrary.add_anim_dynamics_chains(abp, chains, LIMIT_BONES, LIMIT_RADIUS, SIM_SPACE_COMPONENT, ACC_SCALE,
                                                             GRAVITY_SCALE)
    EAL.save_loaded_asset(abp, only_if_is_dirty=False)
    log(f"ABP_Aksa: {k} rantai Anim Dynamics")

    bp = EAL.load_asset(f"{AK}/BP_Aksa")
    d = unreal.get_default_object(bp.generated_class())
    m = d.get_editor_property("mesh")
    m.set_editor_property("skeletal_mesh_asset", mesh)
    m.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    m.set_editor_property("anim_class", abp.generated_class())
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)
    log("BP_Aksa: mesh = SK_Aksa, anim = ABP_Aksa")
    import_portraits()


main()
