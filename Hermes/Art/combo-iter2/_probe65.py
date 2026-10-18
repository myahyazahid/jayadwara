
import unreal
EAL = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary
seq = EAL.load_asset("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air_slam")
mon = EAL.load_asset("/Game/Hermes/ComboIter2/Montages/AM_Hermes_air_slam")
print("sequence", round(AL.get_sequence_length(seq), 3), "montage", round(AL.get_montage_length(mon), 3) if hasattr(AL,"get_montage_length") else mon.get_editor_property("sequence_length"))
print("montage play_length", round(mon.get_play_length(), 3), "section", mon.get_num_sections())
