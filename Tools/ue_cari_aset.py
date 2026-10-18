import unreal

AR = unreal.AssetRegistryHelpers.get_asset_registry()
cari = ("SK_Mixamo_YBot", "IK_Mixamo", "RTG_Mixamo", "A_Aksa_Mx_finisher_02", "A_Aksa_Mx_air_slam", "SK_Mixamo_YBot_Skeleton")
for ad in AR.get_assets_by_path("/Game", True):
    n = str(ad.asset_name)
    if any(n.startswith(c) for c in cari):
        print("[A] %s.%s  (%s)" % (ad.package_name, n, ad.asset_class_path.asset_name))
