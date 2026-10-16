"""Tuyul K6 rev3 — aksen pendar REDUP rust/merah gelap (buang ungu), arahan developer 16 Okt 2026.

Latar: material UE menyalurkan RGB mentah `T_Tuyul_Emit` ke Emission, sehingga kanal G tampil
HIJAU & B tampil BIRU. Perbaikannya menyisipkan mask (jumlah kanal emit) x warna aksen:
    Emission = mask(jumlah kanal emit) x AccentColor x GlowIntensity
- rev1: merah menyala (0.50, 0.02, 0.02) -> developer: "gausa merah merah".
- rev2: ungu (0.30, 0.07, 0.55)          -> developer: "gausah ada warna ungu-ungu ini".
- rev3: redup merah gelap (dark red, bukan oranye/rust), sesuai arahan developer
        + design docs/27 ("Energi Kala merah gelap emissive ... tanpa biru/silver").

Base color / normal / ORM TIDAK diubah (kulit tetap warna aslinya). Skrip hanya mencari
VectorParameter (aksen) & ScalarParameter (glow) yang sudah ada di rantai emissive lalu
memperbarui nilainya (idempoten, tidak menggandakan node).

Jalankan: python Tools/ue_remote.py Hermes/Tools/tuyul_64_ue_recolor.py
"""
import unreal

MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
MASTER = "/Game/Hermes/Tuyul/Materials/M_Tuyul_Master"
MI = "/Game/Hermes/Tuyul/Materials/MI_Tuyul_Body"
ACCENT = unreal.LinearColor(0.22, 0.010, 0.008, 1.0)   # merah gelap (linear; ~#811A16 sRGB)
GLOW = 0.6                                              # redup (rev2 = 1.5)

m = EAL.load_asset(MASTER)
assert m is not None, MASTER

emul = MEL.get_material_property_input_node(m, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
assert emul is not None, "tak menemukan node emissive"
print("emissive input:", emul.get_class().get_name())

# telusuri rantai emissive -> cari VectorParameter (aksen) & ScalarParameter (glow)
vec = None
scl = None
stack = list(MEL.get_inputs_for_material_expression(m, emul))
seen = set()
while stack:
    e = stack.pop()
    if e is None:
        continue
    n = e.get_name()
    if n in seen:
        continue
    seen.add(n)
    if isinstance(e, unreal.MaterialExpressionVectorParameter) and vec is None:
        vec = e
    if isinstance(e, unreal.MaterialExpressionScalarParameter) and scl is None:
        scl = e
    stack.extend(MEL.get_inputs_for_material_expression(m, e))
print("node aksen ditemukan:", vec.get_name() if vec else None,
      "| glow:", scl.get_name() if scl else None)

assert vec is not None, "tak menemukan VectorParameter aksen di rantai emissive"
vec.set_editor_property("parameter_name", "AccentColor")
vec.set_editor_property("default_value", ACCENT)
if scl is not None:
    scl.set_editor_property("parameter_name", "GlowIntensity")
    scl.set_editor_property("default_value", GLOW)
MEL.recompile_material(m)
EAL.save_loaded_asset(m)
print(f"M_Tuyul_Master: emissive = mask x AccentColor {ACCENT} x GlowIntensity {GLOW}")

mi = EAL.load_asset(MI)
MEL.set_material_instance_vector_parameter_value(mi, "AccentColor", ACCENT)
MEL.set_material_instance_scalar_parameter_value(mi, "GlowIntensity", GLOW)
MEL.update_material_instance(mi)
EAL.save_loaded_asset(mi)
print(f"MI_Tuyul_Body: AccentColor {ACCENT} GlowIntensity {GLOW}")
print("SELESAI")
