import unreal
pies = unreal.EditorLevelLibrary.get_pie_worlds(False)
unreal.log(f"[TP] pie_worlds={len(pies)}")
if not pies:
    unreal.log_error("[TP] PIE belum jalan")
else:
    w = pies[0]
    pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
    dest = unreal.Vector(-41000.0, -3500.0, 22150.0)
    if pawn:
        pawn.set_actor_location(dest, False, False)
        pawn.set_actor_rotation(unreal.Rotator(0.0, -30.0, 0.0), False)
        ctrl = unreal.GameplayStatics.get_player_controller(w, 0)
        if ctrl:
            ctrl.set_control_rotation(unreal.Rotator(0.0, -30.0, 0.0))
        loc = pawn.get_actor_location()
        unreal.log(f"[TP] pawn di ({loc.x:.0f},{loc.y:.0f},{loc.z:.0f}) — atap, menghadap timur-laut")
    else:
        unreal.log_error("[TP] pawn tidak ditemukan")
