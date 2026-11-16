"""Tuyul (model Tripo, docs/27 + laporan Hermes 16 Okt 2026) — impor ke folder karakter proyek (Unreal Editor Python).

Berasal dari Hermes/Tools/tuyul_60_ue_setup.py + tuyul_61_ue_import.py + tuyul_64_ue_recolor.py (branch hermes/tuyul),
dipindah ke /Game/Jayadwara/Characters/Tuyul/. Pola: Tools/ue_import_aksa2.py.
Sumber: Art/Export/SK_Tuyul*.fbx (3 skala x LOD0..3) + SK_Tuyul*_sockets.json + Art/Export/Textures_Tuyul/*.png.
Membuat / mengisi ulang (idempoten):
  Tuyul/Mesh/SKEL_Tuyul            salinan SK_Mannequin + Compatible Skeleton SK_Mannequin (disimpan paksa)
  Tuyul/Mesh/SK_Tuyul              1,0 m  (kawanan, mode manusia)      4 LOD, 1 slot, 8 socket
  Tuyul/Mesh/SK_TuyulBesar         27 m   (fase 2, tiga tuyul besar)   4 LOD, 1 slot, 8 socket
  Tuyul/Mesh/SK_TuyulRaksasa       45 m   (fase 1, boss)               4 LOD, 1 slot, 8 socket
  Tuyul/Textures/T_Tuyul_*         Color (sRGB), N, ORM, Emit
  Tuyul/Materials/M_Tuyul_Master   salinan M_Aksa2_Master + rantai emissive: mask(Emit) x AccentColor x GlowIntensity
  Tuyul/Materials/MI_Tuyul_Body    instance (BaseColor, Normal, ORM, Emissive, AccentColor dark red, GlowIntensity 0,6)
Tidak menyentuh SK_Mannequin, SK_Aksa*, M_Aksa2_Master, level apa pun. Rig (IK_Tuyul + retargeter): Tools/ue_setup_tuyul.py.

Kombinasi WAJIB (sama dengan Aksa2, docs/19 6.4 + docs/25): FBX skala di-bake (cm) + importer FBX LAMA
(Interchange.FeatureFlags.Import.FBX 0) + Compatible Skeleton SK_Mannequin TERSIMPAN di SKEL_Tuyul.
Skala boss di-bake di FBX (27 m / 45 m), bukan skala actor.

CATATAN: rantai emissive M_Tuyul_Master ditulis ulang di sini (rev1-rev3 Hermes menyisipkannya lewat perintah terpisah
yang tidak ada di repo). Diuji di proyek utama 17 Okt 2026 (UE 5.6.1): 12 aset terbentuk, tampilan sama dengan tangkapan Hermes K6.

Pakai (editor terbuka, TIDAK sedang Play):
  python Tools/ue_remote.py Tools/ue_import_tuyul.py
"""
import json
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EXPORT = os.path.join(REPO, "Art", "Export")
TEX_DIR = os.path.join(EXPORT, "Textures_Tuyul")
DEST = "/Game/Jayadwara/Characters/Tuyul"
MESH_DIR, TEX_DEST, MAT_DIR = f"{DEST}/Mesh", f"{DEST}/Textures", f"{DEST}/Materials"
SKELETON = f"{MESH_DIR}/SKEL_Tuyul"
MI_PATH = f"{MAT_DIR}/MI_Tuyul_Body"
MASTER_PATH = f"{MAT_DIR}/M_Tuyul_Master"

MANNY_SKEL = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
MASTER_SRC = "/Game/Jayadwara/Characters/Aksa2/Materials/M_Aksa2_Master"
PHYSICS = "/Game/Characters/Mannequins/Rigs/PA_Mannequin"

SCALES = [
    ("SK_Tuyul", "SK_Tuyul.fbx", "SK_Tuyul_sockets.json"),
    ("SK_TuyulBesar", "SK_TuyulBesar.fbx", "SK_TuyulBesar_sockets.json"),
    ("SK_TuyulRaksasa", "SK_TuyulRaksasa.fbx", "SK_TuyulRaksasa_sockets.json"),
]
LOD_SCREEN_SIZE = {0: 1.0, 1: 0.45, 2: 0.22, 3: 0.10}
LEGACY_FBX = True  # True = importer FBX lama (Interchange.FeatureFlags.Import.FBX 0)

# Pendar Energi Kala (disetujui developer 16 Okt 2026, rev3): merah gelap, redup.
ACCENT = unreal.LinearColor(0.22, 0.010, 0.008, 1.0)   # ~#811A16 sRGB
GLOW = 0.6

TEX = {  # nama aset: (berkas, sRGB, kompresi)
    "T_Tuyul_Color": ("T_Tuyul_Color.png", True, unreal.TextureCompressionSettings.TC_DEFAULT),
    "T_Tuyul_N": ("T_Tuyul_N.png", False, unreal.TextureCompressionSettings.TC_NORMALMAP),
    "T_Tuyul_ORM": ("T_Tuyul_ORM.png", False, unreal.TextureCompressionSettings.TC_MASKS),
    # Emit adalah mask data, tetapi tetap sRGB/TC_DEFAULT: begitu yang dipakai Hermes saat developer menyetujui tampilan
    # pendar (K6 rev3). Mengubah ke linear/TC_MASKS membuat pendar lebih tipis dan redup (kandidat polish R7).
    "T_Tuyul_Emit": ("T_Tuyul_Emit.png", True, unreal.TextureCompressionSettings.TC_DEFAULT),
}

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
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


def setup_folders():
    for sub in ("", "/Mesh", "/Textures", "/Materials", "/Rig"):
        p = f"{DEST}{sub}"
        if not EAL.does_directory_exist(p):
            EAL.make_directory(p)
            print("  mkdir", p)


def ensure_mannequin_bones():
    """SK_Mannequin di disk hanya 92 tulang; sisanya ditambah UE saat mesh pemakainya dimuat. Duplikasi/impor
    sebelum itu menghasilkan SKEL_Tuyul yang salah. Muat pemakai skeleton dulu, lalu cek 171 tulang."""
    for m in ("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple", "/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple",
              "/Game/Jayadwara/Characters/Aksa/Mesh/SK_Aksa"):
        if EAL.does_asset_exist(m):
            EAL.load_asset(m)
    sk = EAL.load_asset(MANNY_SKEL)
    n = len(unreal.AnimPoseExtensions.get_bone_names(unreal.AnimPoseExtensions.get_reference_pose(sk)))
    print(f"  SK_Mannequin: {n} tulang di memori")
    if n < 161:
        raise RuntimeError(f"SK_Mannequin hanya {n} tulang - impor dibatalkan (SKEL_Tuyul akan salah)")


def setup_skeleton():
    ensure_mannequin_bones()
    if not EAL.does_asset_exist(SKELETON):
        skel = EAL.duplicate_asset(MANNY_SKEL, SKELETON)
        print("  SKEL_Tuyul dibuat dari SK_Mannequin")
    else:
        skel = EAL.load_asset(SKELETON)
        print("  SKEL_Tuyul sudah ada")
    assert skel is not None, f"gagal membuat {SKELETON}"
    man = EAL.load_asset(MANNY_SKEL)
    if man not in list(skel.get_editor_property("compatible_skeletons")):
        skel.add_compatible_skeleton(man)
        print("  + Compatible Skeleton: SK_Mannequin")
    EAL.save_loaded_asset(skel, False)   # disimpan paksa: compat yang tidak tersimpan = mesh hancur saat animasi
    print("  compat:", [x.get_name() for x in skel.get_editor_property("compatible_skeletons")])
    return skel


def import_textures():
    tex = {}
    for name, (fn, srgb, comp) in TEX.items():
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", os.path.join(TEX_DIR, fn))
        task.set_editor_property("destination_path", TEX_DEST)
        task.set_editor_property("destination_name", name)
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", True)
        task.set_editor_property("save", False)
        asset_tools.import_asset_tasks([task])
        t = EAL.load_asset(f"{TEX_DEST}/{name}")
        assert t is not None, f"gagal impor tekstur {name}"
        t.set_editor_property("srgb", srgb)
        t.set_editor_property("compression_settings", comp)
        EAL.save_loaded_asset(t)
        tex[name] = t
        print("  tekstur:", f"{TEX_DEST}/{name}")
    return tex


def build_master(tex):
    """M_Tuyul_Master = salinan M_Aksa2_Master + Emission = mask(Emit) x AccentColor x GlowIntensity.
    mask = jumlah kanal R+G+B T_Tuyul_Emit (dot dengan (1,1,1), saturate), supaya kanal G/B tidak tampil hijau/biru."""
    if EAL.does_asset_exist(MASTER_PATH):
        master = EAL.load_asset(MASTER_PATH)
        if MEL.get_material_property_input_node(master, unreal.MaterialProperty.MP_EMISSIVE_COLOR) is not None:
            print("  M_Tuyul_Master sudah ada dan emissive terpasang (tidak dibuat ulang)")
            return master
        print("  M_Tuyul_Master sudah ada TANPA emissive (run sebelumnya terputus): rantai dibuat sekarang")
    else:
        master = EAL.duplicate_asset(MASTER_SRC, MASTER_PATH)
        assert master is not None, f"gagal menyalin {MASTER_SRC}"
        print("  M_Tuyul_Master disalin dari M_Aksa2_Master")
    new = MEL.create_material_expression
    tn = new(master, unreal.MaterialExpressionTextureSampleParameter2D, -1100, 300)
    tn.set_editor_property("parameter_name", "Emissive")
    tn.set_editor_property("texture", tex["T_Tuyul_Emit"])
    ones = new(master, unreal.MaterialExpressionConstant3Vector, -1100, 520)
    ones.set_editor_property("constant", unreal.LinearColor(1.0, 1.0, 1.0, 0.0))
    dot = new(master, unreal.MaterialExpressionDotProduct, -820, 400)
    sat = new(master, unreal.MaterialExpressionSaturate, -620, 400)
    acc = new(master, unreal.MaterialExpressionVectorParameter, -620, 560)
    acc.set_editor_property("parameter_name", "AccentColor")
    acc.set_editor_property("default_value", ACCENT)
    mul1 = new(master, unreal.MaterialExpressionMultiply, -380, 440)
    glow = new(master, unreal.MaterialExpressionScalarParameter, -380, 640)
    glow.set_editor_property("parameter_name", "GlowIntensity")
    glow.set_editor_property("default_value", GLOW)
    mul2 = new(master, unreal.MaterialExpressionMultiply, -140, 500)
    MEL.connect_material_expressions(tn, "RGB", dot, "A")
    MEL.connect_material_expressions(ones, "", dot, "B")
    MEL.connect_material_expressions(dot, "", sat, "")
    MEL.connect_material_expressions(sat, "", mul1, "A")
    MEL.connect_material_expressions(acc, "", mul1, "B")
    MEL.connect_material_expressions(mul1, "", mul2, "A")
    MEL.connect_material_expressions(glow, "", mul2, "B")
    MEL.connect_material_property(mul2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(master)
    EAL.save_loaded_asset(master)
    print("  + emissive = mask(Emit) x AccentColor x GlowIntensity")
    return master


def build_instance(master, tex):
    mi = EAL.load_asset(MI_PATH)
    if mi is None:
        mi = asset_tools.create_asset("MI_Tuyul_Body", MAT_DIR, unreal.MaterialInstanceConstant,
                                      unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, master)
    for pname, key in (("BaseColor", "T_Tuyul_Color"), ("Normal", "T_Tuyul_N"),
                       ("ORM", "T_Tuyul_ORM"), ("Emissive", "T_Tuyul_Emit")):
        MEL.set_material_instance_texture_parameter_value(mi, pname, tex[key])
        print(f"  MI param {pname} <- {key}")
    MEL.set_material_instance_vector_parameter_value(mi, "AccentColor", ACCENT)
    MEL.set_material_instance_scalar_parameter_value(mi, "GlowIntensity", GLOW)
    MEL.update_material_instance(mi)
    EAL.save_loaded_asset(mi)
    print("  MI_Tuyul_Body siap")
    return mi


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


def assign_material(mesh, mi):
    mats = []
    for m in mesh.get_editor_property("materials"):
        m.set_editor_property("material_interface", mi)
        mats.append(m)
    mesh.set_editor_property("materials", mats)
    print("  material slot:", len(mats), "->", mi.get_name())


def sockets(mesh, json_file):
    data = json.load(open(os.path.join(EXPORT, json_file), encoding="utf-8"))["sockets"]
    # Transform tulang pada ref pose MESH ini (skeleton bersama berskala x1, jadi untuk mesh x27/x45
    # harus dibaca dari komponen mesh sendiri; kalau tidak socket jatuh di posisi x1).
    tmp = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    tmp.set_actor_label("Tuyul_socket_probe")
    try:
        comp = tmp.skeletal_mesh_component
        comp.set_skinned_asset_and_update(mesh)
        bone_tf = {}
        for s in data:
            if s["bone"] not in bone_tf:
                bone_tf[s["bone"]] = comp.get_bone_transform(s["bone"], unreal.RelativeTransformSpace.RTS_COMPONENT)
    finally:
        EAS.destroy_actor(tmp)          # jangan tinggalkan aktor probe di level yang terbuka
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

print(f"=== TUYUL IMPOR: DEST = {DEST} ===")
setup_folders()
skeleton = setup_skeleton()
textures = import_textures()
master_mat = build_master(textures)
mi_body = build_instance(master_mat, textures)

for name, fbx, sockj in SCALES:
    print(f"=== {name} ===")
    mesh = import_lod0(skeleton, fbx, name)
    assign_material(mesh, mi_body)
    import_lods(mesh, name)
    assign_material(mesh, mi_body)
    pa = EAL.load_asset(PHYSICS)
    if pa:
        mesh.set_editor_property("physics_asset", pa)
    sockets(mesh, sockj)
    EAL.save_loaded_asset(mesh)
    print("  bounds:", mesh.get_bounds())

print("=== IMPOR TUYUL SELESAI ===")
