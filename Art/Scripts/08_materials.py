"""Iterasi 4 — material Blender berbasis tekstur, meniru master material Unreal (docs/15).

Per slot (Body, Armor, Cloth, Face):
  warna zona = campuran 4 warna parameter lewat Mask (R merah, G emas, B hitam, A putih) -> x BC (pengali) -> x AO
  Roughness/Metallic dari ORM (G/B), Normal dari N, Emissive hanya Face (T_Jayadwara_Face_Emit, KONSTAN).
Tekstur dibaca dari Art/Export/Textures (dibuat make_textures.py). Aman dijalankan ulang.
Nama node parameter (label) = nama parameter yang akan dibuat di M_Jayadwara_Master.
"""
import os
import sys

import bpy

SCRIPTS = r"C:\repository\unreal_engine\jayadwara\Art\Scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import jd_common as C

TEX = r"C:\repository\unreal_engine\jayadwara\Art\Export\Textures"
SLOTS = ["Body", "Armor", "Cloth", "Face"]


def lin(hexstr):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (C.srgb_to_linear(r), C.srgb_to_linear(g), C.srgb_to_linear(b), 1.0)


def image(slot, kind, data):
    path = os.path.join(TEX, f"T_Jayadwara_{slot}_{kind}.png")
    img = bpy.data.images.load(path, check_existing=True)
    img.reload()
    img.colorspace_settings.name = "sRGB" if not data else "Non-Color"
    if kind == "Mask":
        img.alpha_mode = "CHANNEL_PACKED"
    return img


def build(slot):
    mat = bpy.data.materials.get(f"M_Jayadwara_{slot}") or bpy.data.materials.new(f"M_Jayadwara_{slot}")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N = nt.nodes
    L = nt.links
    x = -1400

    def node(kind, label, loc, **props):
        n = N.new(kind)
        n.label = label
        n.location = loc
        for k, v in props.items():
            setattr(n, k, v)
        return n

    uvn = node("ShaderNodeUVMap", "UV", (x, 0), uv_map="UVMap")

    def tex(label, slot_, kind, data, loc):
        t = node("ShaderNodeTexImage", label, loc)
        t.image = image(slot_, kind, data)
        t.interpolation = "Linear"
        L.new(uvn.outputs["UV"], t.inputs["Vector"])
        return t

    t_mask = tex("T_Mask", slot, "Mask", True, (x + 300, 300))
    t_bc = tex("T_BC", slot, "BC", False, (x + 300, 0))
    t_n = tex("T_N", slot, "N", True, (x + 300, -300))
    t_orm = tex("T_ORM", slot, "ORM", True, (x + 300, -600))
    sep_m = node("ShaderNodeSeparateColor", "Mask RGB", (x + 650, 300))
    L.new(t_mask.outputs["Color"], sep_m.inputs["Color"])
    sep_o = node("ShaderNodeSeparateColor", "ORM RGB", (x + 650, -600))
    L.new(t_orm.outputs["Color"], sep_o.inputs["Color"])

    def rgb(label, hexstr, loc):
        n = node("ShaderNodeRGB", label, loc)
        n.outputs[0].default_value = lin(hexstr)
        return n

    c_black = rgb("Color_Black", C.HEX["black"], (x + 650, 150))
    c_red = rgb("Color_Red", C.HEX["red"], (x + 650, 80))
    c_gold = rgb("Color_Gold", C.HEX["gold"], (x + 650, 10))
    c_white = rgb("Color_White", C.HEX["white"], (x + 650, -60))

    def mix(label, a, b, fac_socket, loc):
        m = node("ShaderNodeMix", label, loc, data_type="RGBA", blend_type="MIX")
        L.new(a, m.inputs["A"])
        L.new(b, m.inputs["B"])
        L.new(fac_socket, m.inputs["Factor"])
        return m

    m1 = mix("zone R", c_black.outputs[0], c_red.outputs[0], sep_m.outputs["Red"], (x + 950, 150))
    m2 = mix("zone G", m1.outputs["Result"], c_gold.outputs[0], sep_m.outputs["Green"], (x + 1150, 150))
    m3 = mix("zone A", m2.outputs["Result"], c_white.outputs[0], t_mask.outputs["Alpha"], (x + 1350, 150))
    mul_bc = node("ShaderNodeMix", "x BC", (x + 1550, 100), data_type="RGBA", blend_type="MULTIPLY")
    mul_bc.inputs["Factor"].default_value = 1.0
    L.new(m3.outputs["Result"], mul_bc.inputs["A"])
    L.new(t_bc.outputs["Color"], mul_bc.inputs["B"])
    mul_ao = node("ShaderNodeMix", "x AO", (x + 1750, 100), data_type="RGBA", blend_type="MULTIPLY")
    mul_ao.inputs["Factor"].default_value = 1.0
    L.new(mul_bc.outputs["Result"], mul_ao.inputs["A"])
    L.new(sep_o.outputs["Red"], mul_ao.inputs["B"])          # AO (R) sebagai pengali; input B menerima float->warna abu
    base_out = mul_ao.outputs["Result"]

    bsdf = node("ShaderNodeBsdfPrincipled", "Principled", (x + 2050, 0))
    out = node("ShaderNodeOutputMaterial", "Output", (x + 2350, 0))
    nmap = node("ShaderNodeNormalMap", "Normal", (x + 1750, -300), space="TANGENT", uv_map="UVMap")
    L.new(t_n.outputs["Color"], nmap.inputs["Color"])
    L.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    L.new(sep_o.outputs["Green"], bsdf.inputs["Roughness"])
    L.new(sep_o.outputs["Blue"], bsdf.inputs["Metallic"])

    if slot == "Face":
        t_e = tex("T_Emit", "Face", "Emit", True, (x + 300, -900))
        c_emit = rgb("Emissive_Color", C.HEX["gem"], (x + 1350, -900))
        k_int = node("ShaderNodeValue", "Emissive_Intensity", (x + 1350, -1050))
        k_int.outputs[0].default_value = 3.0                    # KONSTAN; tidak dihubungkan ke meter Sync (aturan IP)
        mulE = node("ShaderNodeMath", "Emit x Intensity", (x + 1550, -950), operation="MULTIPLY")
        L.new(t_e.outputs["Color"], mulE.inputs[0])
        L.new(k_int.outputs[0], mulE.inputs[1])
        base_mix = mix("base->emissive", base_out, c_emit.outputs[0], t_e.outputs["Color"], (x + 1900, -200))
        base_out = base_mix.outputs["Result"]
        L.new(c_emit.outputs[0], bsdf.inputs["Emission Color"])
        L.new(mulE.outputs[0], bsdf.inputs["Emission Strength"])
    L.new(base_out, bsdf.inputs["Base Color"])
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if slot == "Cloth":
        mat.use_backface_culling = False
    mat["JD_TEX"] = 1
    return mat


for s in SLOTS:
    build(s)
    print("material siap:", f"M_Jayadwara_{s}")
if bpy.data.filepath:
    bpy.ops.file.make_paths_relative()
