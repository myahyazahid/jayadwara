
import unreal
EAL = unreal.EditorAssetLibrary
for peran in ("air", "light_01"):
    m = EAL.load_asset(f"/Game/Hermes/ComboIter2/Montages/AM_Hermes_{peran}")
    bi = m.get_editor_property("blend_in"); bo = m.get_editor_property("blend_out")
    print(f"{peran}: panjang {m.get_editor_property('sequence_length'):.3f} s | blend_in {bi.get_editor_property('blend_time'):.2f} | blend_out {bo.get_editor_property('blend_time'):.2f}")
    seq = m.get_editor_property("sequence")
    print("   seq:", seq.get_name(), "panjang", unreal.AnimationLibrary.get_sequence_length(seq))
