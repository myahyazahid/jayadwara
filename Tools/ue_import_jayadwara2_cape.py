"""Import jubah Jayadwara2 (docs/26 J1) ke Unreal Editor Python. Tidak menyentuh aset badan Jayadwara2.

Hasil di /Game/Jayadwara/Characters/Jayadwara2/Cape/:
  Textures/  T_Jayadwara2_Cape_BC / _N (flip green) / _ORM (atlas Tripo cap02) + _Emit (hitam) / _Mask (zona merah penuh) — J1 sementara
  Materials/ M_Jayadwara2_Cape_Master (salinan M_Jayadwara2_Master + Masked dissolve "Dissolve" & pinggiran emas, J1b)
             MI_Jayadwara2_Cape (redaman logam/kekasaran/normal sama dengan badan, two-sided)
  Mesh/      SK_Jayadwara2_Cape + SKEL_Jayadwara2_Cape (89 tulang badan, nama sama, + rantai cape_*), tanpa Physics Asset
Skala import 1 (FBX sudah setinggi raksasa, di-bake). Pakai: python Tools/ue_remote.py Tools/ue_import_jayadwara2_cape.py
Mesh/ dihapus dulu (impor ulang bersih) -> jalankan lagi Tools/ue_setup_jayadwara2_cape.py (skeleton dibuat ulang).
Butuh: ue_import_jayadwara2.py sudah dijalankan (M_Jayadwara2_Master).
"""
import os

import unreal

REPO = r"C:/repository/unreal_engine/jayadwara"
EXPORT = os.path.join(REPO, "Art", "Export")
TEX_DIR = os.path.join(EXPORT, "Textures_Jayadwara2_Cape")
J2 = "/Game/Jayadwara/Characters/Jayadwara2"
ROOT = f"{J2}/Cape"
MESH_NAME = "SK_Jayadwara2_Cape"
MASTER = f"{J2}/Materials/M_Jayadwara2_Master"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
problems = []


def log(m):
    unreal.log(f"[Jayadwara2Cape] {m}")


def manual(m):
    problems.append(m)
    unreal.log_warning(f"[Jayadwara2Cape][MANUAL] {m}")


def set_fbx_legacy(enabled):
    unreal.SystemLibrary.execute_console_command(None, f"Interchange.FeatureFlags.Import.FBX {0 if enabled else 1}")


def import_textures():
    tasks = []
    for fn in sorted(os.listdir(TEX_DIR)):
        if fn.startswith("T_Jayadwara2_Cape_") and fn.endswith(".png"):
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
        a = EAL.load_asset(f"{ROOT}/Textures/T_Jayadwara2_Cape_{kind}")
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
        elif kind == "Mask":
            a.set_editor_property("srgb", False)
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
        else:
            a.set_editor_property("srgb", False)
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        tex[kind] = a
    log(f"tekstur: {sorted(tex)}")
    return tex


def build_cape_master():
    """M_Jayadwara2_Cape_Master = salinan M_Jayadwara2_Master + Masked dissolve untuk lepas/pakai jubah (UJDCapeComponent).

    v = 0,6 x noise(posisi lokal) + 0,4 x tinggi (0 = ujung bawah) -> buyar dari bawah ke atas.
    OpacityMask = v - Dissolve + 0,5 (clip 0,5); pinggiran |v - Dissolve| < EdgeWidth menyala emas (ditambah ke emissive asli).
    """
    path = f"{ROOT}/Materials/M_Jayadwara2_Cape_Master"
    mi_path = f"{ROOT}/Materials/MI_Jayadwara2_Cape"
    if EAL.does_asset_exist(mi_path):                                   # lepas rujukan sebelum master jubah dibuat ulang
        MEL.set_material_instance_parent(EAL.load_asset(mi_path), EAL.load_asset(MASTER))
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    mat = EAL.duplicate_asset(MASTER, path)
    P = unreal.MaterialProperty
    emi_old = MEL.get_material_property_input_node(mat, P.MP_EMISSIVE_COLOR)
    emi_old_out = MEL.get_material_property_input_node_output_name(mat, P.MP_EMISSIVE_COLOR) if emi_old else ""
    X = -1600

    def node(cls, y, **props):
        e = MEL.create_material_expression(mat, cls, X, y)
        for k, v in props.items():
            e.set_editor_property(k, v)
        return e

    def link(a, ao, b, bi):
        MEL.connect_material_expressions(a, ao, b, bi)

    def binop(cls, a, b, y, ao="", bo=""):
        e = node(cls, y)
        link(a, ao, e, "A")
        link(b, bo, e, "B")
        return e

    def const(v, y):
        return node(unreal.MaterialExpressionConstant, y, r=v)

    def sparam(name, v, y):
        return node(unreal.MaterialExpressionScalarParameter, y, parameter_name=name, default_value=v)

    pos_cls = getattr(unreal, "MaterialExpressionLocalPosition", None) or unreal.MaterialExpressionWorldPosition
    pos = node(pos_cls, 2600)
    noise = node(unreal.MaterialExpressionNoise, 2700, scale=0.004, levels=4, output_min=0.0, output_max=1.0)
    link(pos, "", noise, "Position")
    zc = node(unreal.MaterialExpressionComponentMask, 2800, r=False, g=False, b=True, a=False)
    link(pos, "", zc, "")
    zg = node(unreal.MaterialExpressionSaturate, 2900)
    link(binop(unreal.MaterialExpressionDivide, zc, sparam("Dissolve_HeightRef", 4000.0, 2850), 2880), "", zg, "")
    v = binop(unreal.MaterialExpressionAdd,
              binop(unreal.MaterialExpressionMultiply, noise, const(0.6, 2950), 2960),
              binop(unreal.MaterialExpressionMultiply, zg, const(0.4, 3000), 3010), 3050)
    d = sparam("Dissolve", 0.0, 3100)
    diff = binop(unreal.MaterialExpressionSubtract, v, d, 3150)
    mask = binop(unreal.MaterialExpressionAdd, diff, const(0.5, 3180), 3200)
    MEL.connect_material_property(mask, "", P.MP_OPACITY_MASK)
    # pinggiran bercahaya
    ab = node(unreal.MaterialExpressionAbs, 3250)
    link(diff, "", ab, "")
    om = node(unreal.MaterialExpressionOneMinus, 3300)
    link(binop(unreal.MaterialExpressionDivide, ab, sparam("Dissolve_EdgeWidth", 0.04, 3260), 3280), "", om, "")
    edge = node(unreal.MaterialExpressionSaturate, 3350)
    link(om, "", edge, "")
    on = node(unreal.MaterialExpressionSaturate, 3400)
    link(binop(unreal.MaterialExpressionMultiply, d, const(20.0, 3380), 3390), "", on, "")
    col = node(unreal.MaterialExpressionVectorParameter, 3450, parameter_name="Dissolve_GlowColor",
               default_value=unreal.LinearColor(1.0, 0.58, 0.15, 1.0))
    glow = binop(unreal.MaterialExpressionMultiply,
                 binop(unreal.MaterialExpressionMultiply, col, sparam("Dissolve_GlowIntensity", 25.0, 3470), 3480),
                 binop(unreal.MaterialExpressionMultiply, edge, on, 3490), 3500)
    emi = binop(unreal.MaterialExpressionAdd, emi_old, glow, 3550, ao=emi_old_out) if emi_old else glow
    MEL.connect_material_property(emi, "", P.MP_EMISSIVE_COLOR)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    mat.set_editor_property("opacity_mask_clip_value", 0.5)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat, only_if_is_dirty=False)
    log("M_Jayadwara2_Cape_Master (Masked dissolve + pinggiran emas; parameter Dissolve 0..1)")
    return mat


def build_material(tex):
    if EAL.load_asset(MASTER) is None:
        raise RuntimeError(f"{MASTER} belum ada: jalankan Tools/ue_import_jayadwara2.py dulu")
    master = build_cape_master()
    name = "MI_Jayadwara2_Cape"
    path = f"{ROOT}/Materials/{name}"
    mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else asset_tools.create_asset(
        name, f"{ROOT}/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, master)
    for kind, t in tex.items():
        MEL.set_material_instance_texture_parameter_value(mi, f"T_{kind}", t)
    MEL.update_material_instance(mi)
    log(f"{name} (induk M_Jayadwara2_Cape_Master, tekstur jubah)")
    return mi


def release_bp_reference():
    """Komponen Cape di BP_Jayadwara2 merujuk mesh lama -> penghapusan gagal diam-diam dan impor tidak terjadi.
    Kosongkan mesh & ABP komponen itu dulu (ue_setup_jayadwara2_cape.py memasangnya lagi)."""
    bp = EAL.load_asset(f"{J2}/BP_Jayadwara2")
    if bp is None:
        return
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        d = lib.get_data(h)
        if str(lib.get_variable_name(d)) == "Cape":
            comp = lib.get_object(d)
            comp.set_editor_property("anim_class", None)
            comp.set_editor_property("skeletal_mesh_asset", None)
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
            EAL.save_loaded_asset(bp, only_if_is_dirty=False)
            log("rujukan BP_Jayadwara2.Cape ke mesh lama dilepas (setup akan memasang lagi)")
    unreal.SystemLibrary.collect_garbage()


def import_mesh(mi):
    dest = f"{ROOT}/Mesh"
    release_bp_reference()
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
    ui.set_editor_property("create_physics_asset", False)
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
        manual(f"{MESH_NAME} tidak terimpor sebagai SkeletalMesh")
        return None
    mats = []
    for m in mesh.get_editor_property("materials"):
        m.set_editor_property("material_interface", mi)
        mats.append(m)
    mesh.set_editor_property("materials", mats)
    skel = mesh.get_editor_property("skeleton")
    old = skel.get_path_name().split(".")[0]
    if not old.endswith("/SKEL_Jayadwara2_Cape"):
        EAL.rename_asset(old, f"{dest}/SKEL_Jayadwara2_Cape")
    ref = unreal.AnimPoseExtensions.get_reference_pose(mesh.get_editor_property("skeleton"))
    names = [str(n) for n in unreal.AnimPoseExtensions.get_bone_names(ref)]
    body = EAL.load_asset(f"{J2}/Mesh/SK_Jayadwara2")
    body_names = set(str(n) for n in unreal.AnimPoseExtensions.get_bone_names(
        unreal.AnimPoseExtensions.get_reference_pose(body.get_editor_property("skeleton")))) if body else set()
    shared = [n for n in names if n in body_names]
    cape = [n for n in names if n.startswith("cape_")]
    log(f"{MESH_NAME} terimpor: {len(names)} tulang ({len(shared)} sama nama dengan SK_Jayadwara2, {len(cape)} cape_*)")
    if body_names and len(shared) != len(names) - len(cape):
        manual(f"tulang tak cocok dengan badan: {[n for n in names if n not in body_names and not n.startswith('cape_')][:8]}")
    return mesh


def main():
    for f in (f"{MESH_NAME}.fbx",):
        if not os.path.exists(os.path.join(EXPORT, f)):
            unreal.log_error(f"[Jayadwara2Cape] tidak ada: {f} (jalankan Art/Scripts/jayadwara2_cape_14_export.py)")
            return
    tex = import_textures()
    mi = build_material(tex)
    if import_mesh(mi) is None:
        # mesh lama yang masih dirujuk BP/level kadang baru terhapus tuntas setelah GC -> coba sekali lagi
        unreal.SystemLibrary.collect_garbage()
        problems.clear()
        import_mesh(mi)
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    log("selesai." + (f" {len(problems)} langkah manual: {problems}" if problems else ""))


main()
