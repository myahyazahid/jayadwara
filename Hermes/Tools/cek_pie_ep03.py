import unreal
pies = unreal.EditorLevelLibrary.get_pie_worlds(False)
unreal.log(f"[TP] pie_worlds={len(pies)}")
for w in pies:
    unreal.log(f"[TP] world={w.get_name()}")
    for p in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Pawn):
        loc = p.get_actor_location()
        unreal.log(f"[TP] pawn={p.get_name()} loc=({loc.x:.0f},{loc.y:.0f},{loc.z:.0f})")
