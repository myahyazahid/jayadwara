"""Import paket Jerangkong (Art/Export, jalur B docs/20) ke Unreal Engine 5.6 — Unreal Editor Python.

Pakai: python Tools/ue_remote.py Tools/ue_import_jerangkong.py
Hasil di /Game/Jayadwara/Characters/Jerangkong/:
  Textures/  T_Jerangkong_{BC,N,ORM,Emit}
  Materials/ M_Jerangkong_Master + MI_Jerangkong (boss) + MI_Kerangka (minion: gelang disamarkan, J8)
  Mesh/      SK_Jerangkong (boss, ±30,7 m ter-bake) + SKEL_/PA_Jerangkong; SK_Kerangka (minion ±1,86 m, MinLOD 1)
             + SKEL_/PA_Kerangka; socket dari *_sockets.json
  Parts/     SM_Jerangkong_<Potongan> (14, skala boss, collision kapsul) — mekanik rontok (docs/20 6.2, parts.json)
Master material (docs/20 6.4, disatukan jadi 1 slot): BaseColor = lerp(BC x AO, OrnamentTint, Emit.B x OrnamentHide),
Roughness ORM.G, Metallic ORM.B, Normal N, Emissive = GlowColor x (Emit.R + Emit.G x WeakPointPulse x denyut) x GlowIntensity.
Pola sama dengan ue_import_jayadwara.py (importer FBX lama, skala import 1, isi Mesh/ dihapus dulu).
"""
import json
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EXPORT = os.path.join(REPO, "Art", "Export")
TEX_DIR = os.path.join(EXPORT, "Textures_Jerangkong")
PARTS_DIR = os.path.join(EXPORT, "Jerangkong_Parts")
ROOT = "/Game/Jayadwara/Characters/Jerangkong"
MESHES = {"SK_Jerangkong": {"min_lod": 0, "mi": "MI_Jerangkong"}, "SK_Kerangka": {"min_lod": 1, "mi": "MI_Kerangka"}}
LOD_SCREEN_SIZE = {0: 1.0, 1: 0.5, 2: 0.25, 3: 0.12}
GLOW = "#B0201A"
ORNAMENT_TINT = "#8E7258"                        # warna tulang redup: gelang minion "hilang" ke tulang

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
problems = []


def log(msg):
    unreal.log(f"[Jerangkong] {msg}")


def manual(msg):
    problems.append(msg)
    unreal.log_warning(f"[Jerangkong][MANUAL] {msg}")


def lin_color(hexstr):
    h = hexstr.lstrip("#")

    def s2l(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (s2l(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))
    return unreal.LinearColor(r, g, b, 1.0)


def task(filename, dest, name=None, options=None):
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", filename)
    t.set_editor_property("destination_path", dest)
    if name:
        t.set_editor_property("destination_name", name)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("save", False)
    if options is not None:
        t.set_editor_property("options", options)
    return t


def set_fbx_legacy(enabled):
    unreal.SystemLibrary.execute_console_command(None, f"Interchange.FeatureFlags.Import.FBX {0 if enabled else 1}")


# ------------------------------------------------------------------ 1. tekstur
def import_textures():
    dest = f"{ROOT}/Textures"
    files = [f for f in sorted(os.listdir(TEX_DIR)) if f.startswith("T_Jerangkong_") and f.endswith(".png")]
    asset_tools.import_asset_tasks([task(os.path.join(TEX_DIR, f), dest) for f in files])
    tex = {}
    C = unreal.TextureCompressionSettings
    for f in files:
        name = f[:-4]
        a = EAL.load_asset(f"{dest}/{name}")
        kind = name.rsplit("_", 1)[1]
        if kind == "BC":
            a.set_editor_property("srgb", True)
            a.set_editor_property("compression_settings", C.TC_DEFAULT)
        elif kind == "N":
            a.set_editor_property("srgb", False)
            a.set_editor_property("compression_settings", C.TC_NORMALMAP)
            a.set_editor_property("flip_green_channel", True)    # Tripo/Blender = OpenGL; UE = DirectX
        else:
            a.set_editor_property("srgb", False)
            a.set_editor_property("compression_settings", C.TC_MASKS)
        tex[kind] = a
    log(f"tekstur: {sorted(tex)}")
    return tex


# ------------------------------------------------------------------ 2. material
def build_master(tex):
    path = f"{ROOT}/Materials/M_Jerangkong_Master"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    mat = asset_tools.create_asset("M_Jerangkong_Master", f"{ROOT}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    y = [0]

    def expr(cls, x=-1200):
        e = MEL.create_material_expression(mat, cls, x, y[0])
        y[0] += 140
        return e

    def tparam(name, kind, default):
        e = expr(unreal.MaterialExpressionTextureSampleParameter2D)
        e.set_editor_property("parameter_name", name)
        S = unreal.MaterialSamplerType
        e.set_editor_property("sampler_type", {"BC": S.SAMPLERTYPE_COLOR, "N": S.SAMPLERTYPE_NORMAL}.get(kind, S.SAMPLERTYPE_MASKS))
        e.set_editor_property("texture", default)
        return e

    def vparam(name, hexstr):
        e = expr(unreal.MaterialExpressionVectorParameter, -900)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", lin_color(hexstr))
        return e

    def sparam(name, v):
        e = expr(unreal.MaterialExpressionScalarParameter, -900)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", v)
        return e

    def op(cls, a, a_out, b, b_out, x=-500):
        e = expr(cls, x)
        MEL.connect_material_expressions(a, a_out, e, "A")
        MEL.connect_material_expressions(b, b_out, e, "B")
        return e

    t_bc, t_n, t_orm, t_e = tparam("T_BC", "BC", tex["BC"]), tparam("T_N", "N", tex["N"]), tparam("T_ORM", "ORM", tex["ORM"]), tparam("T_Emit", "Emit", tex["Emit"])
    glow = vparam("GlowColor", GLOW)
    tint = vparam("OrnamentTint", ORNAMENT_TINT)
    k_int = sparam("GlowIntensity", 8.0)
    k_weak = sparam("WeakPointPulse", 0.0)              # 1 saat kelemahan aktif (fase 2)
    k_speed = sparam("PulseSpeed", 3.0)
    k_hide = sparam("OrnamentHide", 0.0)                # 1 = minion (J8)

    bc_ao = op(unreal.MaterialExpressionMultiply, t_bc, "RGB", t_orm, "R")
    orn = op(unreal.MaterialExpressionMultiply, t_e, "B", k_hide, "")
    base = op(unreal.MaterialExpressionLinearInterpolate, bc_ao, "", tint, "", -400)
    MEL.connect_material_expressions(orn, "", base, "Alpha")
    # denyut 0,5..1 = 0,75 + 0,25 sin(t x speed)
    tm = expr(unreal.MaterialExpressionTime, -1000)
    ts = op(unreal.MaterialExpressionMultiply, tm, "", k_speed, "", -800)
    sn = expr(unreal.MaterialExpressionSine, -700)
    MEL.connect_material_expressions(ts, "", sn, "")
    sn.set_editor_property("period", 6.283185)
    s1 = expr(unreal.MaterialExpressionMultiply, -600)
    MEL.connect_material_expressions(sn, "", s1, "A")
    s1.set_editor_property("const_b", 0.25)
    s2 = expr(unreal.MaterialExpressionAdd, -500)
    MEL.connect_material_expressions(s1, "", s2, "A")
    s2.set_editor_property("const_b", 0.75)
    weak = op(unreal.MaterialExpressionMultiply, t_e, "G", k_weak, "", -500)
    weak2 = op(unreal.MaterialExpressionMultiply, weak, "", s2, "", -400)
    weak3 = expr(unreal.MaterialExpressionMultiply, -350)
    MEL.connect_material_expressions(weak2, "", weak3, "A")
    weak3.set_editor_property("const_b", 4.0)                                   # retak menyala jauh lebih terang
    emask = op(unreal.MaterialExpressionAdd, t_e, "R", weak3, "", -300)
    e1 = op(unreal.MaterialExpressionMultiply, glow, "", emask, "", -250)
    e2 = op(unreal.MaterialExpressionMultiply, e1, "", k_int, "", -200)

    P = unreal.MaterialProperty
    MEL.connect_material_property(base, "", P.MP_BASE_COLOR)
    MEL.connect_material_property(t_orm, "G", P.MP_ROUGHNESS)
    MEL.connect_material_property(t_orm, "B", P.MP_METALLIC)
    MEL.connect_material_property(t_n, "RGB", P.MP_NORMAL)
    MEL.connect_material_property(e2, "", P.MP_EMISSIVE_COLOR)
    mat.set_editor_property("used_with_skeletal_mesh", True)
    mat.set_editor_property("used_with_static_lighting", False)
    MEL.layout_material_expressions(mat)
    MEL.recompile_material(mat)
    log("M_Jerangkong_Master dibuat")
    return mat


def build_instances(master):
    mis = {}
    for name, params in (("MI_Jerangkong", {}), ("MI_Kerangka", {"OrnamentHide": 1.0, "GlowIntensity": 5.0})):
        path = f"{ROOT}/Materials/{name}"
        mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else asset_tools.create_asset(
            name, f"{ROOT}/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        MEL.set_material_instance_parent(mi, master)
        for k, v in params.items():
            MEL.set_material_instance_scalar_parameter_value(mi, k, v)
        MEL.update_material_instance(mi)
        mis[name] = mi
    log("material instance: " + ", ".join(mis))
    return mis


# ------------------------------------------------------------------ 3. skeletal mesh
def sk_options():
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
    return ui


def clean_folder(dest, keep_prefix=None):
    if EAL.does_directory_exist(dest):
        for a in EAL.list_assets(dest, recursive=True, include_folder=False):
            p = a.split(".")[0]
            if keep_prefix is None or p.rsplit("/", 1)[1].startswith(keep_prefix):
                EAL.delete_asset(p)


def import_lods(mesh, name):
    sub = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    for i in (1, 2, 3):
        res = sub.import_lod(mesh, i, os.path.join(EXPORT, f"{name}_LOD{i}.fbx"))
        if res is None or (isinstance(res, int) and res < 0):
            manual(f"{name} LOD{i} gagal")
    infos = []
    for i, info in enumerate(mesh.get_editor_property("lod_info")):
        ss = unreal.PerPlatformFloat()
        ss.set_editor_property("default", LOD_SCREEN_SIZE.get(i, 0.1))
        info.set_editor_property("screen_size", ss)
        infos.append(info)
    mesh.set_editor_property("lod_info", infos)


def add_sockets(mesh, name):
    with open(os.path.join(EXPORT, f"{name}_sockets.json"), encoding="utf-8") as f:
        data = json.load(f)["sockets"]
    pose = unreal.AnimPoseExtensions.get_reference_pose(mesh.get_editor_property("skeleton"))
    for s in data:
        sname = s["name"].replace("SOCKET_", "")
        if mesh.find_socket(sname) is not None:
            continue
        loc = unreal.Vector(*s["ue_component_cm"])
        bt = unreal.AnimPoseExtensions.get_bone_pose(pose, s["bone"], unreal.AnimPoseSpaces.WORLD)
        rel = bt.inverse_transform_location(loc)
        sock = unreal.new_object(unreal.SkeletalMeshSocket, outer=mesh)
        sock.set_socket_parent(mesh, s["bone"])
        sock.set_editor_property("relative_location", rel)
        mesh.add_socket(sock, False)
        mesh.rename_socket(str(sock.get_editor_property("socket_name")), sname)
    log(f"{name}: {len(data)} socket")


def import_skeletal(name, cfg, mis):
    dest = f"{ROOT}/Mesh"
    short = name.replace("SK_", "")
    for prefix in (name, f"SKEL_{short}", f"PA_{short}"):
        if EAL.does_asset_exist(f"{dest}/{prefix}"):
            EAL.delete_asset(f"{dest}/{prefix}")
    set_fbx_legacy(True)
    try:
        asset_tools.import_asset_tasks([task(os.path.join(EXPORT, f"{name}.fbx"), dest, name, sk_options())])
        mesh = EAL.load_asset(f"{dest}/{name}")
        if not isinstance(mesh, unreal.SkeletalMesh):
            manual(f"{name} tidak terimpor sebagai SkeletalMesh")
            return None
        import_lods(mesh, name)
    finally:
        set_fbx_legacy(False)
    mats = []
    for m in mesh.get_editor_property("materials"):
        m.set_editor_property("material_interface", mis[cfg["mi"]])
        mats.append(m)
    mesh.set_editor_property("materials", mats)
    if cfg["min_lod"]:
        ml = unreal.PerPlatformInt()
        ml.set_editor_property("default", cfg["min_lod"])
        mesh.set_editor_property("min_lod", ml)
    for prop, new in (("skeleton", f"SKEL_{short}"), ("physics_asset", f"PA_{short}")):
        a = mesh.get_editor_property(prop)
        if a is None:
            manual(f"{name}: {prop} tidak ada")
            continue
        old = a.get_path_name().split(".")[0]
        if not old.endswith("/" + new):
            EAL.rename_asset(old, f"{dest}/{new}")
    add_sockets(mesh, name)
    lods = len(mesh.get_editor_property("lod_info"))
    log(f"{name}: {lods} LOD, skeleton {len(mesh.get_editor_property('skeleton').get_editor_property('bone_tree'))} tulang")
    return mesh


# ------------------------------------------------------------------ 4. static mesh potongan
def sm_options():
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", True)
    ui.set_editor_property("import_as_skeletal", False)
    ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
    ui.set_editor_property("import_materials", False)
    ui.set_editor_property("import_textures", False)
    d = ui.get_editor_property("static_mesh_import_data")
    d.set_editor_property("import_uniform_scale", 1.0)
    d.set_editor_property("convert_scene", True)
    d.set_editor_property("combine_meshes", True)
    d.set_editor_property("auto_generate_collision", False)
    d.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    return ui


def import_parts(mis):
    dest = f"{ROOT}/Parts"
    clean_folder(dest, "SM_Jerangkong_")
    files = [f for f in sorted(os.listdir(PARTS_DIR)) if f.endswith(".fbx")]
    set_fbx_legacy(True)
    try:
        asset_tools.import_asset_tasks([task(os.path.join(PARTS_DIR, f), dest, f[:-4], sm_options()) for f in files])
    finally:
        set_fbx_legacy(False)
    sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    n = 0
    for f in files:
        sm = EAL.load_asset(f"{dest}/{f[:-4]}")
        if not isinstance(sm, unreal.StaticMesh):
            manual(f"{f} tidak terimpor")
            continue
        sm.set_material(0, mis["MI_Jerangkong"])
        sub.remove_collisions(sm)
        sub.add_simple_collisions(sm, unreal.ScriptCollisionShapeType.CAPSULE)
        n += 1
    log(f"Parts: {n} static mesh + collision kapsul")


def main():
    for f in [*(f"{m}{s}.fbx" for m in MESHES for s in ("", "_LOD1", "_LOD2", "_LOD3")), "SK_Jerangkong_parts.json"]:
        if not os.path.exists(os.path.join(EXPORT, f)):
            unreal.log_error(f"[Jerangkong] file tidak ada: {f} — jalankan Art/Scripts/jerangkong_14_export.py dulu")
            return
    tex = import_textures()
    master = build_master(tex)
    mis = build_instances(master)
    for name, cfg in MESHES.items():
        import_skeletal(name, cfg, mis)
    import_parts(mis)
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    log("selesai")
    for p in problems:
        unreal.log_warning("  - " + p)


main()
