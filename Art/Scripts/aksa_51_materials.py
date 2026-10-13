"""Aksa Iterasi 5 — material Blender berbasis tekstur (5 slot), meniru master material UE (M_Aksa_Master).

Jalankan di Blender (MCP: exec(open(path).read())) dengan aksa_v05_tex.blend, setelah aksa_50_uv.py dan make_textures_aksa.py.
Per slot: BC (sRGB) -> Base Color; ORM (Non-Color) R=AO (x Base Color), G=Roughness, B=Metallic; N -> Normal Map (OpenGL).
Skin: SSS lembut (Subsurface) dari mask T_Aksa_Skin_SSS; Eyes: Coat (kornea). Material ditandai AK_TEX supaya get_material() (ak_common)
tidak menimpanya. Parameter di UE: tekstur BC/N/ORM per Material Instance. Aman diulang.
"""
import os

import bpy

TEX = r"C:\repository\unreal_engine\jayadwara\Art\Export\Textures_Aksa"
SLOTS = ["Skin", "Eyes", "Hair", "Cloth", "Gear"]


def image(slot, kind, data):
    img = bpy.data.images.load(os.path.join(TEX, f"T_Aksa_{slot}_{kind}.png"), check_existing=True)
    img.reload()
    img.colorspace_settings.name = "Non-Color" if data else "sRGB"
    return img


def build(slot):
    mat = bpy.data.materials.get(f"M_Aksa_{slot}") or bpy.data.materials.new(f"M_Aksa_{slot}")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N, L = nt.nodes, nt.links

    def node(kind, label, loc):
        n = N.new(kind)
        n.label = label
        n.location = loc
        return n

    uvn = node("ShaderNodeUVMap", "UV", (-1300, 0))
    uvn.uv_map = "UVMap"

    def tex(label, kind, data, loc):
        t = node("ShaderNodeTexImage", label, loc)
        t.image = image(slot, kind, data)
        L.new(uvn.outputs["UV"], t.inputs["Vector"])
        return t

    bc, orm, nrm = tex("BC", "BC", False, (-1000, 300)), tex("ORM", "ORM", True, (-1000, 0)), tex("N", "N", True, (-1000, -300))
    sep = node("ShaderNodeSeparateColor", "ORM split", (-700, 0))
    L.new(orm.outputs["Color"], sep.inputs["Color"])
    mul = node("ShaderNodeMix", "BC x AO", (-500, 300))
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    L.new(bc.outputs["Color"], mul.inputs["A"])
    L.new(sep.outputs["Red"], mul.inputs["B"])
    nm = node("ShaderNodeNormalMap", "Normal", (-500, -300))
    nm.uv_map = "UVMap"
    L.new(nrm.outputs["Color"], nm.inputs["Color"])
    bsdf = node("ShaderNodeBsdfPrincipled", "Aksa", (-150, 0))
    out = node("ShaderNodeOutputMaterial", "Output", (200, 0))
    L.new(mul.outputs["Result"], bsdf.inputs["Base Color"])
    L.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    L.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
    L.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if slot == "Skin":
        sss = tex("SSS", "SSS", True, (-1000, -600))
        L.new(sss.outputs["Color"], bsdf.inputs["Subsurface Weight"])
        bsdf.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.2)
        bsdf.inputs["Subsurface Scale"].default_value = 0.012
        bsdf.inputs["Specular IOR Level"].default_value = 0.4
    if slot == "Eyes":
        bsdf.inputs["Coat Weight"].default_value = 1.0
        bsdf.inputs["Coat Roughness"].default_value = 0.02
    mat.use_backface_culling = False
    mat["AK_TEX"] = True
    return mat


for s in SLOTS:
    m = build(s)
    print("material:", m.name)
# pasang ke bagian per ak_slot (slot indeks 0 per objek)
for o in bpy.data.objects:
    if o.type == "MESH" and o.name.startswith("AK_") and "ak_slot" in o:
        o.data.materials.clear()
        o.data.materials.append(bpy.data.materials[f"M_Aksa_{o['ak_slot']}"])
bpy.ops.wm.save_mainfile()
print("disimpan:", bpy.data.filepath)
