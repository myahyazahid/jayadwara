
import unreal
for m in ("set_bone_track_keys","get_model_interface","set_model","set_play_length","resize_play_length","add_bone_track","set_transform_curve_keys","set_transform_curve_key"):
    f = getattr(unreal.AnimSequencerController, m, None)
    print("==", m, "->", (f.__doc__ or "").strip()[:400] if f else None)
