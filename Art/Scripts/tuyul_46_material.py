"""K4.4 - Pasang material M_Tuyul (Color/N/ORM/Emit) di blend, simpan v07.

  blender --background Art/Blender/tuyul/tuyul_v06_export.blend \
      --python Art/Scripts/tuyul_46_material.py -- <Textures dir> <out blend>

Konvensi docs/20: Emissive = R x warna Kala + G x warna RealPulse + B x warna ornamen,
kekuatan dari parameter GlowIntensity (2,5 boss, seperti Jerangkong).
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuyul_paths as P  # noqa: E402

ROOT = P.ROOT
TEX = P.TEX
OUTB = P.BLENDER / "tuyul_v07_material.blend"
OBJ = "TY_Source"
KALA = (0.545, 0.102, 0.102, 1.0)     # #8B1A1A
PULSE = (1.00, 0.85, 0.45, 1.0)       # RealPulse (ubun-ubun)
ORN = (0.95, 0.78, 0.32, 1.0)         # ornamen/koin kuningan
GLOW = 2.5


def load(name):
    p = TEX / name
    img = bpy.data.images.get(name)
    if img is None:
        img = bpy.data.images.load(str(p), check_existing=True)
    img.filepath = str(p)
    return img


def main():
    mat = bpy.data.materials["M_Tuyul"]
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    n = nt.nodes
    bsdf = n.new("ShaderNodeBsdfPrincipled")
    out = n.new("ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    def tex(img, loc, non_color=True):
        t = n.new("ShaderNodeTexImage")
        t.image = img
        t.location = loc
        if non_color:
            img.colorspace_settings.name = "Non-Color"
        return t

    base = n.new("ShaderNodeTexImage")
    base.image = load("T_Tuyul_Color.png")
    base.image.colorspace_settings.name = "sRGB"
    base.location = (-900, 300)
    nt.links.new(base.outputs["Color"], bsdf.inputs["Base Color"])

    nrm = tex(load("T_Tuyul_N.png"), (-900, 0))
    nm = n.new("ShaderNodeNormalMap")
    nm.location = (-600, 0)
    nt.links.new(nrm.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

    orm = tex(load("T_Tuyul_ORM.png"), (-900, -300))
    sep = n.new("ShaderNodeSeparateColor")
    sep.location = (-600, -300)
    nt.links.new(orm.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])

    emit = tex(load("T_Tuyul_Emit.png"), (-900, -600))
    esep = n.new("ShaderNodeSeparateColor")
    esep.location = (-600, -600)
    nt.links.new(emit.outputs["Color"], esep.inputs["Color"])

    def mul(col, loc):
        m = n.new("ShaderNodeMix")
        m.data_type = "RGBA"
        m.blend_type = "MULTIPLY"
        m.location = loc
        m.inputs[0].default_value = 1.0
        m.inputs[6].default_value = col
        return m

    mr = mul(KALA, (-300, -450))
    mg = mul(PULSE, (-300, -600))
    mb = mul(ORN, (-300, -750))
    nt.links.new(esep.outputs["Red"], mr.inputs[7])
    nt.links.new(esep.outputs["Green"], mg.inputs[7])
    nt.links.new(esep.outputs["Blue"], mb.inputs[7])
    a1 = n.new("ShaderNodeMix")
    a1.data_type, a1.blend_type, a1.location = "RGBA", "ADD", (0, -520)
    nt.links.new(mr.outputs[2], a1.inputs[6])
    nt.links.new(mg.outputs[2], a1.inputs[7])
    a2 = n.new("ShaderNodeMix")
    a2.data_type, a2.blend_type, a2.location = "RGBA", "ADD", (200, -620)
    nt.links.new(a1.outputs[2], a2.inputs[6])
    nt.links.new(mb.outputs[2], a2.inputs[7])
    nt.links.new(a2.outputs[2], bsdf.inputs["Emission Color"])

    gi = n.new("ShaderNodeValue")
    gi.label = "GlowIntensity"
    gi.location = (0, -820)
    gi.outputs[0].default_value = GLOW
    nt.links.new(gi.outputs[0], bsdf.inputs["Emission Strength"])

    print("material", mat.name, "node:", sorted({x.type for x in n}))
    print("  BaseColor <-", base.image.name, base.image.size[:])
    print("  Normal    <-", nrm.image.name, " ORM <-", orm.image.name)
    print("  Emit      <-", emit.image.name, " GlowIntensity =", GLOW)
    print("  tekstur dipakai mesh:", sorted({m.name for m in bpy.data.objects[OBJ].data.materials}))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTB))
    print("simpan", OUTB)


main()
