
import unreal
EAL = unreal.EditorAssetLibrary
for peran in ("light_01","light_02","light_03","light_04"):
    m = EAL.load_asset(f"/Game/Hermes/ComboIter2/Montages/AM_Hermes_{peran}")
    bi = m.get_editor_property("blend_in").get_editor_property("blend_time")
    bo = m.get_editor_property("blend_out").get_editor_property("blend_time")
    print(f"{peran}: panjang {m.get_editor_property('sequence_length'):.2f} s | blend_in {bi:.2f} s | blend_out {bo:.2f} s")
