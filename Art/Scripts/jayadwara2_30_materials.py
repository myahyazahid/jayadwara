"""Jayadwara2 R4 — material preview Blender yang meniru M_Jayadwara2_Master di UE (BC x AO, metalik x MetallicScale, kekasaran max RoughnessMin,
normal x NormalStrength, emissive permata/mata konstan). Zona recolor TIDAK dimodelkan di sini (hanya di UE).

  blender --background Art/Blender/jayadwara2_v03_rig_r2.blend --python Art/Scripts/jayadwara2_30_materials.py
Hasil: Art/Blender/jayadwara2_v04_tex.blend (file kerja R4) + render Art/Export/_jd2/_bl_depan.png / _bl_kepala.png (EEVEE bila ada, jika tidak Workbench)."""
import os

import bpy
from mathutils import Vector

ROOT = r"C:\repository\unreal_engine\jayadwara"
TEX = os.path.join(ROOT, "Art", "Export", "Textures_Jayadwara2")
OUT = os.path.join(ROOT, "Art", "Blender", "jayadwara2_v04_tex.blend")
PARAM = dict(MetallicScale=0.35, RoughnessMin=0.55, NormalStrength=0.5, Intensity=3.0, EyeScale=0.45)
GEM, EYE = "#FFC86B", "#FFF1C8"


def lin(h):
    h = h.lstrip("#")
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1.0,)


def img(name, cs):
    old = bpy.data.images.get(name)
    if old:
        bpy.data.images.remove(old)
    im = bpy.data.images.load(os.path.join(TEX, name), check_existing=False)
    im.colorspace_settings.name = cs
    im.pack()
    return im


body = bpy.data.objects["JD2_Body"]
mat = bpy.data.materials.get("M_Jayadwara2") or bpy.data.materials.new("M_Jayadwara2")
mat.use_nodes = True
mat.use_backface_culling = False
nt = mat.node_tree
nt.nodes.clear()
N = nt.nodes.new
out = N("ShaderNodeOutputMaterial"); out.location = (900, 0)
pr = N("ShaderNodeBsdfPrincipled"); pr.location = (600, 0)
nt.links.new(pr.outputs["BSDF"], out.inputs["Surface"])


def tex_node(name, cs, loc):
    t = N("ShaderNodeTexImage"); t.image = img(name, cs); t.location = loc; t.interpolation = "Linear"
    return t


t_bc = tex_node("T_Jayadwara2_BC.png", "sRGB", (-900, 300))
t_n = tex_node("T_Jayadwara2_N.png", "Non-Color", (-900, -100))
t_orm = tex_node("T_Jayadwara2_ORM.png", "Non-Color", (-900, -500))
t_em = tex_node("T_Jayadwara2_Emit.png", "Non-Color", (-900, -900))
sep = N("ShaderNodeSeparateColor"); sep.location = (-600, -500)
nt.links.new(t_orm.outputs["Color"], sep.inputs["Color"])
mix = N("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.location = (-300, 300)
mix.inputs["Factor"].default_value = 1.0
nt.links.new(t_bc.outputs["Color"], mix.inputs["A"])
ao = N("ShaderNodeCombineColor"); ao.location = (-450, 150)
for k in ("Red", "Green", "Blue"):
    nt.links.new(sep.outputs["Red"], ao.inputs[k])                      # AO = ORM.R
nt.links.new(ao.outputs["Color"], mix.inputs["B"])
nt.links.new(mix.outputs["Result"], pr.inputs["Base Color"])
met = N("ShaderNodeMath"); met.operation = "MULTIPLY"; met.location = (-300, -400); met.inputs[1].default_value = PARAM["MetallicScale"]
nt.links.new(sep.outputs["Blue"], met.inputs[0]); nt.links.new(met.outputs[0], pr.inputs["Metallic"])
rg = N("ShaderNodeMath"); rg.operation = "MAXIMUM"; rg.location = (-300, -550); rg.inputs[1].default_value = PARAM["RoughnessMin"]
nt.links.new(sep.outputs["Green"], rg.inputs[0]); nt.links.new(rg.outputs[0], pr.inputs["Roughness"])
nm = N("ShaderNodeNormalMap"); nm.location = (-300, -150); nm.inputs["Strength"].default_value = PARAM["NormalStrength"]
nt.links.new(t_n.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], pr.inputs["Normal"])
# emissive: (GemColor x R + EyeColor x G x EyeScale) x Intensity
sepe = N("ShaderNodeSeparateColor"); sepe.location = (-600, -900)
nt.links.new(t_em.outputs["Color"], sepe.inputs["Color"])
rgb_g = N("ShaderNodeRGB"); rgb_g.outputs[0].default_value = lin(GEM); rgb_g.location = (-600, -1100)
rgb_e = N("ShaderNodeRGB"); rgb_e.outputs[0].default_value = lin(EYE); rgb_e.location = (-600, -1250)
def mulvec(a_out, b_out, loc):
    m = N("ShaderNodeVectorMath"); m.operation = "MULTIPLY"; m.location = loc
    nt.links.new(a_out, m.inputs[0]); nt.links.new(b_out, m.inputs[1]); return m
gvec = N("ShaderNodeCombineXYZ"); gvec.location = (-450, -900)
for k in ("X", "Y", "Z"):
    nt.links.new(sepe.outputs["Red"], gvec.inputs[k])
evec = N("ShaderNodeCombineXYZ"); evec.location = (-450, -1000)
for k in ("X", "Y", "Z"):
    nt.links.new(sepe.outputs["Green"], evec.inputs[k])
g1 = mulvec(rgb_g.outputs[0], gvec.outputs[0], (-250, -1100))
e1 = mulvec(rgb_e.outputs[0], evec.outputs[0], (-250, -1250))
es = N("ShaderNodeVectorMath"); es.operation = "SCALE"; es.location = (-50, -1250); es.inputs["Scale"].default_value = PARAM["EyeScale"]
nt.links.new(e1.outputs[0], es.inputs[0])
sm = N("ShaderNodeVectorMath"); sm.operation = "ADD"; sm.location = (150, -1150)
nt.links.new(g1.outputs[0], sm.inputs[0]); nt.links.new(es.outputs[0], sm.inputs[1])
fin = N("ShaderNodeVectorMath"); fin.operation = "SCALE"; fin.location = (350, -1150); fin.inputs["Scale"].default_value = PARAM["Intensity"]
nt.links.new(sm.outputs[0], fin.inputs[0])
nt.links.new(fin.outputs[0], pr.inputs["Emission Color"]); pr.inputs["Emission Strength"].default_value = 1.0
body.data.materials.clear(); body.data.materials.append(mat)

# --- render
sc = bpy.context.scene
engines = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
eng = next((e for e in engines if "EEVEE" in e), "BLENDER_WORKBENCH")
sc.render.engine = eng
sc.view_settings.view_transform = "Standard" if "Standard" in [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties["view_transform"].enum_items] else sc.view_settings.view_transform
sc.world = sc.world or bpy.data.worlds.new("w"); sc.world.use_nodes = True
bg = sc.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.35, 0.45, 0.6, 1); bg.inputs["Strength"].default_value = 1.0
for o in list(bpy.data.objects):
    if o.type == "LIGHT":
        bpy.data.objects.remove(o, do_unlink=True)
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (0.9, 0.0, 0.5)
for o in bpy.data.objects:
    if o.type in {"ARMATURE", "EMPTY"}:
        o.hide_render = True
src = bpy.data.objects.get("JD2_Source")
if src:
    src.hide_render = True
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
for name, loc, tgt, orth, res in (("depan", (0, -10, 1.055), (0, 0, 1.055), 2.28, (760, 1200)), ("kepala", (0, -10, 1.76), (0, 0, 1.76), 0.34, (1000, 1000))):
    cd.type, cd.ortho_scale = "ORTHO", orth
    cam.location = Vector(loc); cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(ROOT, "Art", "Export", "_jd2", f"_bl_{name}.png")
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("engine", eng, "| disimpan", OUT)
