
import unreal
EAL = unreal.EditorAssetLibrary
for p in ("/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air",
          "/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_air_slam",
          "/Game/Hermes/ComboIter2/Mixamo/A_Aksa_Mx_light_04"):
    a = EAL.load_asset(p)
    print("==", a.get_name())
    for prop in ("enable_root_motion", "root_motion_root_lock", "force_root_motion_root_lock",
                 "enable_root_motion_scale", "b_enable_root_motion"):
        try:
            print("   ", prop, "=", a.get_editor_property(prop))
        except Exception as e:
            print("   ", prop, "GAGAL", str(e)[:80])
m = EAL.load_asset("/Game/Hermes/ComboIter2/Montages/AM_Hermes_air")
print("== montage", m.get_name())
print("   props root:", [x for x in dir(m) if "root" in x.lower()])
