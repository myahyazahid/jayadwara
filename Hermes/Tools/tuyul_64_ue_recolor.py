"""Tuyul K6 rev — pendar jadi MERAH (second color), arahan developer 16 Okt 2026.

Akar masalah: `M_Tuyul_Master` menyalurkan RGB mentah `T_Tuyul_Emit` ke Emission Color,
sehingga kanal G (`RealPulse`) tampil HIJAU dan kanal B (ornamen) tampil BIRU. Design
docs/27: "Energi Kala merah gelap emissive ... tanpa biru/silver".

Skrip menyisipkan mask (jumlah kanal emit) x warna Kala merah ke rangkaian emissive.
Base color / normal / ORM TIDAK diubah (main color tetap warna asli Tuyul).
Idempoten: kalau jalur merah sudah ada, hanya nilainya yang diperbarui.

Jalankan: python Tools/ue_remote.py Hermes/Tools/tuyul_64_ue_recolor.py
"""
import unreal

MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
MASTER = "/Game/Hermes/Tuyul/Materials/M_Tuyul_Master"
MI = "/Game/Hermes/Tuyul/Materials/MI_Tuyul_Body"
KALA = unreal.LinearColor(0.50, 0.02, 0.02, 1.0)   # merah pekat (linear; ~#8B1A1A sRGB)
GLOW = 1.5

m = EAL.load_asset(MASTER)
assert m is not None, MASTER


def input_names(expr):
    try:
        return list(MEL.get_material_expression_input_names(expr))
    except Exception:
        return []


def input_at(expr, idx):
    ins = MEL.get_inputs_for_material_expression(m, expr)
    return ins[idx] if idx < len(ins) else None


emul = MEL.get_material_property_input_node(m, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
assert emul is not None, "tak menemukan node emissive"
print("emissive input:", emul.get_class().get_name())

tex = None
for e in MEL.get_inputs_for_material_expression(m, emul):
    if isinstance(e, unreal.MaterialExpressionTextureSampleParameter2D):
        tex = e

# --- cek apakah jalur merah (mask x KalaColor) sudah ada ---
red = input_at(emul, 0)
col = None
if isinstance(red, unreal.MaterialExpressionMultiply):
    for e in MEL.get_inputs_for_material_expression(m, red):
        if isinstance(e, unreal.MaterialExpressionVectorParameter) and \
                e.get_editor_property("parameter_name") == "KalaColor":
            col = e
print("jalur merah sudah ada:", col is not None)

if col is None:
    assert tex is not None, "tak menemukan param Emissive"
    print("tex param:", tex.get_editor_property("parameter_name"))
    # mask = dot(tex.RGB, (1,1,1)) = jumlah kanal -> ~1 di zona pendar
    dot = MEL.create_material_expression(m, unreal.MaterialExpressionDotProduct, -560, 720)
    ones = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -780, 800)
    ones.set_editor_property("constant", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
    dn = input_names(dot)
    MEL.connect_material_expressions(tex, "RGB", dot, dn[0])
    MEL.connect_material_expressions(ones, "", dot, dn[1])

    col = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -560, 900)
    col.set_editor_property("parameter_name", "KalaColor")

    red = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -320, 780)
    rn = input_names(red)
    MEL.connect_material_expressions(dot, "", red, rn[0])
    MEL.connect_material_expressions(col, "", red, rn[1])

    # alihkan input pertama multiply (x GlowIntensity) -> emissive (overwrite tex.RGB)
    MEL.connect_material_expressions(red, "", emul, input_names(emul)[0])

col.set_editor_property("default_value", KALA)
MEL.recompile_material(m)
EAL.save_loaded_asset(m)
print("M_Tuyul_Master: emissive = mask x KalaColor", KALA)

mi = EAL.load_asset(MI)
MEL.set_material_instance_vector_parameter_value(mi, "KalaColor", KALA)
MEL.set_material_instance_scalar_parameter_value(mi, "GlowIntensity", GLOW)
MEL.update_material_instance(mi)
EAL.save_loaded_asset(mi)
print("MI_Tuyul_Body: KalaColor", KALA, "GlowIntensity", GLOW)
print("SELESAI")
