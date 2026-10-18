
import unreal
p = unreal.EditorAssetLibrary.load_asset("/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes")
def dump(nama):
    arr = p.get_editor_property(nama)
    print("==", nama, len(arr))
    for i, s in enumerate(arr):
        try:
            d = {k: s.get_editor_property(k) for k in ("montage","move_distance","move_duration","move_height","play_rate","damage")}
        except Exception as e:
            d = {"err": str(e)}
        print("  ", i, {k:(getattr(v,"get_name",lambda: v)() if k=="montage" else v) for k,v in d.items()})
for n in ("light_combo","air_combo","lunge_attack","back_attack","air_attack","air_slam","heavy_finishers"):
    try: dump(n)
    except Exception as e: print(n, "ERR", e)
