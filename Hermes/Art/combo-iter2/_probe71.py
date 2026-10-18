
import unreal
ar = unreal.AssetRegistryHelpers.get_asset_registry()
print("loading:", ar.is_loading_assets())
try:
    ar.scan_paths_synchronous(["/Game/Hermes"], True, True)
    print("scan selesai")
except Exception as e:
    print("scan gagal:", str(e)[:200])
print("loading:", ar.is_loading_assets())
print("mixamo:", [a.asset_name for a in ar.get_assets_by_path("/Game/Hermes/ComboIter2/Mixamo", recursive=False)][:5])
