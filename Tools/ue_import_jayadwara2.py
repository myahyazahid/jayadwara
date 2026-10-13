"""Import paket Jayadwara2 (redesign Tripo, docs/25) ke Unreal Editor Python. Tidak menyentuh aset Jayadwara lama.

Hasil di /Game/Jayadwara/Characters/Jayadwara2/:
  Textures/  T_Jayadwara2_BC / _N (flip green) / _ORM / _Emit (R permata, G mata) / _Mask (RGBA zona: R merah, G emas, B hitam, A putih); make_textures_jayadwara2.py
  Materials/ M_Jayadwara2_Master (BC x AO, Roughness=ORM.G, Metallic=ORM.B, Normal, Emissive=warna x Emit; recolor per zona lewat Mask; two-sided) + MI_Jayadwara2 + MI_Jayadwara2_TesWarna (uji recolor)
  Mesh/      SK_Jayadwara2 (LOD0–3 dari SK_Jayadwara2_LOD1..3.fbx, layar 1,0/0,5/0,25/0,12), SKEL_Jayadwara2, PA_Jayadwara2, 9 socket (SK_Jayadwara2_sockets.json)
Skala import 1 (FBX sudah setinggi raksasa 45 m, di-bake). Pakai: python Tools/ue_remote.py Tools/ue_import_jayadwara2.py
Mesh/ dihapus dulu (impor ulang bersih; skeleton dibuat ulang -> jalankan lagi ue_setup_jayadwara2.py).
"""
import json
import os

import unreal

REPO = r"C:/repository/unreal_engine/jayadwara"
EXPORT = os.path.join(REPO, "Art", "Export")
TEX_DIR = os.path.join(EXPORT, "Textures_Jayadwara2")
ROOT = "/Game/Jayadwara/Characters/Jayadwara2"
MESH_NAME = "SK_Jayadwara2"
LOD_FILES = {1: "SK_Jayadwara2_LOD1.fbx", 2: "SK_Jayadwara2_LOD2.fbx", 3: "SK_Jayadwara2_LOD3.fbx"}
LOD_SCREEN_SIZE = {0: 1.0, 1: 0.5, 2: 0.25, 3: 0.12}      # titik awal (sama dengan Jayadwara lama); tuning di level uji
METALLIC_SCALE, ROUGHNESS_MIN, NORMAL_STRENGTH = 0.35, 0.55, 0.5
# emissive KONSTAN (aturan IP docs/13: tidak dikaitkan ke meter Sync); warna & intensitas sama dengan Jayadwara lama
GEM_COLOR, EYE_COLOR, EMISSIVE_INTENSITY = "#FFC86B", "#FFF1C8", 3.0
EYE_SCALE = 0.45                                         # mata = EMISSIVE_INTENSITY x EYE_SCALE: 3,0 membuat krem #FFF1C8 terbakar jadi putih (tampak 13 Okt 2026)


def lin_color(hexstr):
    h = hexstr.lstrip("#")
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))
    return unreal.LinearColor(r, g, b, 1.0)
      # parameter material; ubah di MI_Jayadwara2 atau di sini

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
problems = []


def log(m):
    unreal.log(f"[Jayadwara2] {m}")


def manual(m):
    problems.append(m)
    unreal.log_warning(f"[Jayadwara2][MANUAL] {m}")


def set_fbx_legacy(enabled):
    unreal.SystemLibrary.execute_console_command(None, f"Interchange.FeatureFlags.Import.FBX {0 if enabled else 1}")


def import_textures():
    tasks = []
    for fn in sorted(os.listdir(TEX_DIR)):
        if fn.startswith("T_Jayadwara2_") and fn.endswith(".png"):
            t = unreal.AssetImportTask()
            t.set_editor_property("filename", os.path.join(TEX_DIR, fn))
            t.set_editor_property("destination_path", f"{ROOT}/Textures")
            t.set_editor_property("automated", True)
            t.set_editor_property("replace_existing", True)
            t.set_editor_property("save", False)
            tasks.append(t)
    asset_tools.import_asset_tasks(tasks)
    tex = {}
    for kind in ("BC", "N", "ORM", "Emit", "Mask"):
        a = EAL.load_asset(f"{ROOT}/Textures/T_Jayadwara2_{kind}")
        if a is None:
            manual(f"tekstur {kind} tidak terimpor")
            continue
        if kind == "BC":
            a.set_editor_property("srgb", True)
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
        elif kind == "N":
            a.set_editor_property("srgb", False)
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            a.set_editor_property("flip_green_channel", True)         # Tripo NormalGL = OpenGL; UE = DirectX
        elif kind == "Mask":                                              # RGBA zona: butuh alpha -> bukan TC_MASKS (BC1 tanpa alpha)
            a.set_editor_property("srgb", False)
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
        else:
            a.set_editor_property("srgb", False)
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        tex[kind] = a
    log(f"tekstur: {sorted(tex)}")
    return tex


def build_material(tex):
    path = f"{ROOT}/Materials/M_Jayadwara2_Master"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    mat = asset_tools.create_asset("M_Jayadwara2_Master", f"{ROOT}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    S = unreal.MaterialSamplerType
    y = [0]

    def tparam(name, sampler):
        e = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -800, y[0])
        y[0] += 220
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("sampler_type", sampler)
        e.set_editor_property("texture", tex[name.split("_")[1]])
        return e

    t_bc = tparam("T_BC", S.SAMPLERTYPE_COLOR)
    t_n = tparam("T_N", S.SAMPLERTYPE_NORMAL)
    t_orm = tparam("T_ORM", S.SAMPLERTYPE_MASKS)
    t_emit = tparam("T_Emit", S.SAMPLERTYPE_MASKS)
    t_mask = tparam("T_Mask", S.SAMPLERTYPE_LINEAR_COLOR if hasattr(S, "SAMPLERTYPE_LINEAR_COLOR") else S.SAMPLERTYPE_MASKS)
    # --- recolor per zona (Mask RGBA: R merah, G emas, B hitam, A putih). Bawaan Amount = 0 -> warna asli.
    # target_i = Zone_i_Color x (luma(BC) / RefLuma_i)  (menjaga tekstur/ukiran), lalu lerp(BC, target_i, Amount_i), dijumlah menurut mask.
    import json as _json
    zinfo = _json.load(open(os.path.join(TEX_DIR, "T_Jayadwara2_Mask.json"), encoding="utf-8"))
    luma_w = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -1100, 1500)
    luma_w.set_editor_property("constant", unreal.LinearColor(0.2126, 0.7152, 0.0722, 1.0))
    dot = MEL.create_material_expression(mat, unreal.MaterialExpressionDotProduct, -900, 1500)
    MEL.connect_material_expressions(t_bc, "RGB", dot, "A")
    MEL.connect_material_expressions(luma_w, "", dot, "B")
    acc = None
    for zi, (zname, ch) in enumerate((("red", "R"), ("gold", "G"), ("black", "B"), ("white", "A"))):
        zy = 1600 + zi * 300
        ref = zinfo[zname]["ref_luma_linear"]
        zc = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -1100, zy)
        zc.set_editor_property("parameter_name", f"Zone_{zname}_Color")
        mc = zinfo[zname]["mean_color_linear"]
        zc.set_editor_property("default_value", unreal.LinearColor(mc[0], mc[1], mc[2], 1.0))
        za = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -1100, zy + 100)
        za.set_editor_property("parameter_name", f"Zone_{zname}_Amount")
        za.set_editor_property("default_value", 0.0)
        kref = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, -900, zy + 100)
        kref.set_editor_property("r", 1.0 / max(ref, 1e-4))
        ratio = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -750, zy + 50)
        MEL.connect_material_expressions(dot, "", ratio, "A")
        MEL.connect_material_expressions(kref, "", ratio, "B")
        tgt = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -600, zy)
        MEL.connect_material_expressions(zc, "", tgt, "A")
        MEL.connect_material_expressions(ratio, "", tgt, "B")
        lp = MEL.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, -450, zy)
        MEL.connect_material_expressions(t_bc, "RGB", lp, "A")
        MEL.connect_material_expressions(tgt, "", lp, "B")
        MEL.connect_material_expressions(za, "", lp, "Alpha")
        mm = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -300, zy)
        MEL.connect_material_expressions(lp, "", mm, "A")
        MEL.connect_material_expressions(t_mask, ch, mm, "B")
        if acc is None:
            acc = mm
        else:
            ad = MEL.create_material_expression(mat, unreal.MaterialExpressionAdd, -150, zy)
            MEL.connect_material_expressions(acc, "", ad, "A")
            MEL.connect_material_expressions(mm, "", ad, "B")
            acc = ad
    ao = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -400, 0)
    MEL.connect_material_expressions(acc, "", ao, "A")
    MEL.connect_material_expressions(t_orm, "R", ao, "B")

    def sparam(name, v, yy):
        e = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -800, yy)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", v)
        return e

    # Tripo memberi emas metalik berkekasaran rendah: di UE memantulkan langit & memperlihatkan permukaan bergelombang.
    # Diatur lewat parameter (nilai awal diuji 13 Okt 2026, lihat docs/25).
    k_met = sparam("MetallicScale", METALLIC_SCALE, 700)
    k_rmin = sparam("RoughnessMin", ROUGHNESS_MIN, 800)
    k_flat = sparam("NormalStrength", NORMAL_STRENGTH, 900)
    met = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -400, 200)
    MEL.connect_material_expressions(t_orm, "B", met, "A")
    MEL.connect_material_expressions(k_met, "", met, "B")
    rough = MEL.create_material_expression(mat, unreal.MaterialExpressionMax, -400, 100)
    MEL.connect_material_expressions(t_orm, "G", rough, "A")
    MEL.connect_material_expressions(k_rmin, "", rough, "B")
    up = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -800, 1000)
    up.set_editor_property("constant", unreal.LinearColor(0.0, 0.0, 1.0, 1.0))
    flat = MEL.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, -400, 300)   # 0 = datar, 1 = penuh
    MEL.connect_material_expressions(up, "", flat, "A")
    MEL.connect_material_expressions(t_n, "RGB", flat, "B")
    MEL.connect_material_expressions(k_flat, "", flat, "Alpha")
    # Emissive = (GemColor x Emit.R + EyeColor x Emit.G) x Intensity
    def vparam(name, hexstr, yy):
        e = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -800, yy)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", lin_color(hexstr))
        return e

    c_gem, c_eye = vparam("Gem_Color", GEM_COLOR, 1100), vparam("Eye_Color", EYE_COLOR, 1200)
    k_int = sparam("Emissive_Intensity", EMISSIVE_INTENSITY, 1300)

    def mul(a, ao_, b, bo_, xx, yy):
        e = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, xx, yy)
        MEL.connect_material_expressions(a, ao_, e, "A")
        MEL.connect_material_expressions(b, bo_, e, "B")
        return e

    g1 = mul(c_gem, "", t_emit, "R", -500, 1100)
    k_eye = sparam("Eye_Scale", EYE_SCALE, 1350)
    e0 = mul(c_eye, "", t_emit, "G", -550, 1200)
    e1 = mul(e0, "", k_eye, "", -450, 1250)
    sm = MEL.create_material_expression(mat, unreal.MaterialExpressionAdd, -350, 1150)
    MEL.connect_material_expressions(g1, "", sm, "A")
    MEL.connect_material_expressions(e1, "", sm, "B")
    emi = mul(sm, "", k_int, "", -200, 1150)
    P = unreal.MaterialProperty
    MEL.connect_material_property(emi, "", P.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(ao, "", P.MP_BASE_COLOR)
    MEL.connect_material_property(rough, "", P.MP_ROUGHNESS)
    MEL.connect_material_property(met, "", P.MP_METALLIC)
    MEL.connect_material_property(flat, "", P.MP_NORMAL)
    mat.set_editor_property("used_with_skeletal_mesh", True)
    mat.set_editor_property("two_sided", True)                          # kain & sayap berupa lembar tipis
    MEL.layout_material_expressions(mat)
    MEL.recompile_material(mat)
    name = "MI_Jayadwara2"
    mpath = f"{ROOT}/Materials/{name}"
    mi = EAL.load_asset(mpath) if EAL.does_asset_exist(mpath) else asset_tools.create_asset(
        name, f"{ROOT}/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, mat)
    MEL.update_material_instance(mi)
    # instance uji recolor (BUKAN untuk game): merah -> ungu tua, hitam -> hampir biru-hitam; emas & putih tetap. Membuktikan Mask & recolor bekerja.
    tpath = f"{ROOT}/Materials/MI_Jayadwara2_TesWarna"
    ti = EAL.load_asset(tpath) if EAL.does_asset_exist(tpath) else asset_tools.create_asset(
        "MI_Jayadwara2_TesWarna", f"{ROOT}/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(ti, mat)
    MEL.set_material_instance_vector_parameter_value(ti, "Zone_red_Color", lin_color("#5A2A8C"))
    MEL.set_material_instance_scalar_parameter_value(ti, "Zone_red_Amount", 1.0)
    MEL.set_material_instance_vector_parameter_value(ti, "Zone_black_Color", lin_color("#1B2438"))
    MEL.set_material_instance_scalar_parameter_value(ti, "Zone_black_Amount", 1.0)
    MEL.update_material_instance(ti)
    log("M_Jayadwara2_Master + MI_Jayadwara2 + MI_Jayadwara2_TesWarna")
    return mi


def import_mesh(mi):
    dest = f"{ROOT}/Mesh"
    if EAL.does_directory_exist(dest):
        for a in EAL.list_assets(dest, recursive=True, include_folder=False):
            EAL.delete_asset(a.split(".")[0])
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", True)
    ui.set_editor_property("import_as_skeletal", True)
    ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    ui.set_editor_property("import_materials", False)
    ui.set_editor_property("import_textures", False)
    ui.set_editor_property("import_animations", False)
    ui.set_editor_property("create_physics_asset", True)
    d = ui.get_editor_property("skeletal_mesh_import_data")
    d.set_editor_property("import_uniform_scale", 1.0)
    d.set_editor_property("convert_scene", True)
    d.set_editor_property("import_morph_targets", False)
    d.set_editor_property("use_t0_as_ref_pose", False)
    d.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", os.path.join(EXPORT, f"{MESH_NAME}.fbx"))
    t.set_editor_property("destination_path", dest)
    t.set_editor_property("destination_name", MESH_NAME)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", False)
    t.set_editor_property("options", ui)
    set_fbx_legacy(True)
    try:
        asset_tools.import_asset_tasks([t])
    finally:
        set_fbx_legacy(False)
    mesh = EAL.load_asset(f"{dest}/{MESH_NAME}")
    if not isinstance(mesh, unreal.SkeletalMesh):
        manual("SK_Jayadwara2 tidak terimpor sebagai SkeletalMesh")
        return None
    mats = []
    for m in mesh.get_editor_property("materials"):
        m.set_editor_property("material_interface", mi)
        mats.append(m)
    mesh.set_editor_property("materials", mats)
    for prop, new in (("skeleton", "SKEL_Jayadwara2"), ("physics_asset", "PA_Jayadwara2")):
        a = mesh.get_editor_property(prop)
        if a is None:
            manual(f"{prop} tidak ada")
            continue
        old = a.get_path_name().split(".")[0]
        if not old.endswith("/" + new):
            EAL.rename_asset(old, f"{dest}/{new}")
    log(f"{MESH_NAME} terimpor")
    return mesh


def import_lods(mesh):
    sub = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem) if hasattr(unreal, "SkeletalMeshEditorSubsystem") else None
    fn = getattr(sub, "import_lod", None) if sub else None
    if fn is None:
        manual("API import LOD tidak ditemukan - impor LOD1-3 manual (Skeletal Mesh Editor > LOD Settings > LOD Import)")
        return
    set_fbx_legacy(True)
    try:
        for i, f in LOD_FILES.items():
            path = os.path.join(EXPORT, f)
            if not os.path.exists(path):
                manual(f"{f} tidak ada (jalankan Art/Scripts/jayadwara2_16_make_lods.py)")
                continue
            res = fn(mesh, i, path)
            if res is None or (isinstance(res, int) and res < 0):
                manual(f"LOD{i} gagal diimpor dari {f}")
            else:
                log(f"LOD{i} <- {f}")
    finally:
        set_fbx_legacy(False)
    try:
        infos = []
        for i, info in enumerate(mesh.get_editor_property("lod_info")):
            if i in LOD_SCREEN_SIZE:
                ss = unreal.PerPlatformFloat()
                ss.set_editor_property("default", LOD_SCREEN_SIZE[i])
                info.set_editor_property("screen_size", ss)
            infos.append(info)
        mesh.set_editor_property("lod_info", infos)
    except Exception as e:  # noqa: BLE001
        manual(f"screen size LOD: set manual {LOD_SCREEN_SIZE} ({e})")
    sub2 = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    n = len(mesh.get_editor_property("lod_info"))
    log(f"LOD: {n} level, vertex render {[sub2.get_num_verts(mesh, i) for i in range(n)]} (tris di Blender 37.438/18.719/8.609/3.742)")


def add_sockets(mesh):
    data = json.load(open(os.path.join(EXPORT, f"{MESH_NAME}_sockets.json"), encoding="utf-8"))["sockets"]
    skel = mesh.get_editor_property("skeleton")
    pose = unreal.AnimPoseExtensions.get_reference_pose(skel)
    for s in data:
        name = s["name"].replace("SOCKET_", "")
        if mesh.find_socket(name) is not None:
            continue
        loc = unreal.Vector(*s["ue_component_cm"])
        bt = unreal.AnimPoseExtensions.get_bone_pose(pose, s["bone"], unreal.AnimPoseSpaces.WORLD)
        rel = bt.inverse_transform_location(loc)
        try:
            sock = unreal.new_object(unreal.SkeletalMeshSocket, outer=mesh)
            sock.set_socket_parent(mesh, s["bone"])
            sock.set_editor_property("relative_location", rel)
            mesh.add_socket(sock, False)
            if not mesh.rename_socket(str(sock.get_editor_property("socket_name")), name):
                raise RuntimeError("rename_socket gagal")
        except Exception as e:  # noqa: BLE001
            manual(f"socket {name}: {e}")
    log(f"socket: {len(data)}")


def main():
    if globals().get("ONLY_MATERIAL"):                                   # bangun ulang material saja (tanpa impor ulang mesh)
        tex = import_textures()
        build_material(tex)
        EAL.save_directory(f"{ROOT}/Materials", only_if_is_dirty=True, recursive=True)
        log("material dibangun ulang (mesh tidak diimpor ulang)")
        return
    for f in (f"{MESH_NAME}.fbx", f"{MESH_NAME}_sockets.json"):
        if not os.path.exists(os.path.join(EXPORT, f)):
            unreal.log_error(f"[Jayadwara2] tidak ada: {f} (jalankan Art/Scripts/jayadwara2_14_export.py)")
            return
    tex = import_textures()
    mi = build_material(tex)
    mesh = import_mesh(mi)
    if mesh is not None:
        import_lods(mesh)
        add_sockets(mesh)
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    log("selesai." + (f" {len(problems)} langkah manual: {problems}" if problems else ""))


main()
