import unreal

EAL = unreal.EditorAssetLibrary
AR = unreal.AssetRegistryHelpers.get_asset_registry()

found = []
for ad in AR.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Jayadwara", "JDCombatProfile"), True):
    found.append(ad.package_name)
if not found:
    for ad in AR.get_assets_by_path("/Game", True):
        if "CombatProfile" in str(ad.asset_name):
            found.append(ad.package_name)

for p in found:
    a = EAL.load_asset(str(p))
    if not a:
        continue
    steps = a.get_editor_property("light_combo")
    fins = a.get_editor_property("heavy_finishers")
    air = a.get_editor_property("air_attack")
    slam = a.get_editor_property("air_slam")
    names = []
    for s in steps:
        m = s.get_editor_property("montage")
        names.append("%s@%.2f" % (m.get_name() if m else "-", s.get_editor_property("play_rate")))
    fnames = []
    for s in fins:
        m = s.get_editor_property("montage")
        fnames.append("%s@%.2f(%.2fs)" % (m.get_name() if m else "-", s.get_editor_property("play_rate"),
                                          m.get_play_length() if m else 0.0))
    am = air.get_editor_property("montage")
    sm = slam.get_editor_property("montage")
    print("[P] %s | light %d: %s | finisher %d: %s | air %s | slam %s | airmax %d" % (
        str(p), len(steps), names, len(fins), fnames,
        am.get_name() if am else "-", sm.get_name() if sm else "-",
        a.get_editor_property("air_combo_max")))
