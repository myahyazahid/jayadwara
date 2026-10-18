import unreal

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
MX = "/Game/Hermes/ComboIter2/Mixamo"
MONT = "/Game/Hermes/ComboIter2/Montages"

seq = EAL.load_asset(MX + "/A_Aksa_Mx_finisher_02")
print("[D2] seq %s %.3f s" % (seq.get_name() if seq else "None", seq.get_play_length() if seq else 0))

path = MONT + "/AM_UJI_montage"
if EAL.does_asset_exist(path):
    EAL.delete_asset(path)
f = unreal.AnimMontageFactory()
f.set_editor_property("source_animation", seq)
m = asset_tools.create_asset("AM_UJI_montage", MONT, unreal.AnimMontage, f)
print("[D2] m = %s (%s)" % (m, m.get_class().get_name() if m else "-"))
if m:
    print("[D2] panjang %.3f s" % m.get_play_length())
    for prop in ("blend_in", "blend_out"):
        v = m.get_editor_property(prop)
        print("[D2] %s -> %s (%s)" % (prop, v, type(v).__name__))
