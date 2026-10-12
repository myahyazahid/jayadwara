"""Jerangkong (jalur B) — material Blender M_Jerangkong dari Art/Export/Textures_Jerangkong (meniru master UE).

Jalankan setelah make_textures_jerangkong.py, di jerangkong_v02_rig.blend (headless atau MCP); menyimpan file itu.
BC x AO(ORM.R) -> Base Color; ORM.G -> Roughness; ORM.B -> Metallic; N (OpenGL) -> Normal;
Emission = GLOW_COLOR x (Emit.R + Emit.G x WEAK_POINT) x GLOW_INTENSITY (docs/20 6.4: GlowIntensity, WeakPointPulse).
Gambar Tripo tertanam yang tidak dipakai lagi dibuang dari file.
"""
import os

import bpy

ROOT = r"C:\repository\unreal_engine\jayadwara"
TEX = os.path.join(ROOT, "Art", "Export", "Textures_Jerangkong")
GLOW_COLOR = (0.66, 0.025, 0.012, 1.0)          # #B0201A linear (merah Kala gelap, docs/24)
GLOW_INTENSITY = 2.5
WEAK_POINT = 1.0

mat = bpy.data.materials.get("M_Jerangkong") or bpy.data.materials.new("M_Jerangkong")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
nt.links.new(bs.outputs[0], out.inputs[0])


def tex(name, noncolor):
    path = os.path.join(TEX, f"T_Jerangkong_{name}.png")
    img = bpy.data.images.get(f"T_Jerangkong_{name}.png") or bpy.data.images.load(path, check_existing=True)
    img.filepath = bpy.path.relpath(path) if bpy.data.filepath else path
    img.reload()
    img.colorspace_settings.name = "Non-Color" if noncolor else "sRGB"
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = img
    n.label = name
    return n


t_bc, t_n, t_orm, t_e = tex("BC", False), tex("N", True), tex("ORM", True), tex("Emit", True)
sep = nt.nodes.new("ShaderNodeSeparateColor")
nt.links.new(t_orm.outputs["Color"], sep.inputs[0])
mul = nt.nodes.new("ShaderNodeMix")
mul.data_type = "RGBA"
mul.blend_type = "MULTIPLY"
mul.inputs["Factor"].default_value = 1.0
nt.links.new(t_bc.outputs["Color"], mul.inputs["A"])
nt.links.new(sep.outputs[0], mul.inputs["B"])
nt.links.new(mul.outputs["Result"], bs.inputs["Base Color"])
nt.links.new(sep.outputs[1], bs.inputs["Roughness"])
nt.links.new(sep.outputs[2], bs.inputs["Metallic"])
nm = nt.nodes.new("ShaderNodeNormalMap")
nt.links.new(t_n.outputs["Color"], nm.inputs["Color"])
nt.links.new(nm.outputs[0], bs.inputs["Normal"])
se = nt.nodes.new("ShaderNodeSeparateColor")
nt.links.new(t_e.outputs["Color"], se.inputs[0])
wk = nt.nodes.new("ShaderNodeMath")
wk.operation = "MULTIPLY_ADD"                      # R + G x WEAK_POINT
nt.links.new(se.outputs[1], wk.inputs[0])
wk.inputs[1].default_value = WEAK_POINT
nt.links.new(se.outputs[0], wk.inputs[2])
scale = nt.nodes.new("ShaderNodeMath")
scale.operation = "MULTIPLY"
nt.links.new(wk.outputs[0], scale.inputs[0])
scale.inputs[1].default_value = GLOW_INTENSITY
nt.links.new(scale.outputs[0], bs.inputs["Emission Strength"])
bs.inputs["Emission Color"].default_value = GLOW_COLOR
for i, n in enumerate(nt.nodes):
    n.location = (-300 * (i % 4) - 300, -250 * (i // 4))
bs.location, out.location = (200, 0), (500, 0)

for ob in bpy.data.objects:
    if ob.name.startswith("JK_P_"):
        ob.data.materials.clear()
        ob.data.materials.append(mat)

for im in list(bpy.data.images):                  # gambar Tripo tertanam (sudah diganti T_Jerangkong_*)
    if im.users == 0:
        bpy.data.images.remove(im)
for m in list(bpy.data.materials):
    if m.users == 0:
        bpy.data.materials.remove(m)
bpy.ops.wm.save_mainfile()
print("M_Jerangkong siap; gambar:", [i.name for i in bpy.data.images])
