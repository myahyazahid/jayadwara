"""MK5c -- Verifikasi ulang penanda dari disk (Unreal Editor Python, via Tools/ue_remote.py).

Muat ulang level dari disk (tanpa modifikasi), hitung 1 PlayerStart + 15 TargetPoint +
7 Cylinder area + 5 TriggerBox zona + 8 dinding batas; cek Z PlayerStart = elev(-40,155)*100
+ 1/2 kapsul (+/- 10 cm); cek T1-T3 (di_atap) Z >= 990 cm. Tanpa save (read-only verifikasi).
"""
import os
import sys
import json
import math

import unreal

DEST = "/Game/Hermes/MapsEp2"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp2"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art/Level/ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
PENANDA = DATA["penanda"]
START_P = next(p for p in PENANDA if p["jenis"] == "PlayerStart")
WALL_LABELS = [
    "BATAS_Arena_Barat", "BATAS_Arena_Timur", "BATAS_Arena_Selatan", "BATAS_Arena_Utara",
    "BATAS_Medan_Barat", "BATAS_Medan_Timur", "BATAS_Medan_Selatan", "BATAS_Medan_Utara",
]
AREA_IDS = {p["id"] for p in PENANDA if p["jenis"] == "area"}

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
problems = []


def log(m):
    unreal.log(f"[MK5c] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[MK5c] {m}")


def elev(x, y):
    return M.elev(x, y)


def half_capsule():
    try:
        gm = EAL.load_asset(GAMEMODE)
        cdo = unreal.get_default_object(gm.generated_class())
        pawn_cls = cdo.get_editor_property("default_pawn_class")
        if pawn_cls is None:
            return 88.0
        pcdo = unreal.get_default_object(pawn_cls)
        cap = pcdo.get_editor_property("capsule_component")
        return float(cap.get_editor_property("capsule_half_height"))
    except Exception:  # noqa: BLE001
        return 88.0


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        fail("Editor sedang Play (PIE) -- hentikan dulu")
        return
    t0 = __import__("time").time()
    LES.load_level(MAP)
    log(f"level dimuat ulang dari disk: {MAP}")
    actors = EAS.get_all_level_actors()
    log(f"total actor di level: {len(actors)}")

    n_start = sum(1 for a in actors if isinstance(a, unreal.PlayerStart))
    n_titik = sum(1 for a in actors if isinstance(a, unreal.TargetPoint))
    n_area = sum(1 for a in actors if isinstance(a, unreal.StaticMeshActor) and a.get_actor_label() in AREA_IDS)
    n_zona = sum(1 for a in actors if isinstance(a, unreal.TriggerBox))
    n_dinding = sum(1 for a in actors if a.get_actor_label() in WALL_LABELS)
    n_capture = sum(1 for a in actors if a.get_actor_label() == "MK5_Capture")
    log(f"PlayerStart={n_start} (1) | TargetPoint={n_titik} (15) | area Cylinder={n_area} (7) | "
        f"zona TriggerBox={n_zona} (5) | dinding={n_dinding} (8) | sisa Capture={n_capture} (0)")

    # Z PlayerStart
    hc = half_capsule()
    x, y = START_P["pos"]
    exp = elev(x, y) * 100.0 + hc
    start_a = next((a for a in actors if isinstance(a, unreal.PlayerStart)), None)
    got = start_a.get_actor_location().z if start_a else None
    d = (got - exp) if got is not None else None
    log(f"PlayerStart Z: aktual={got:.1f} cm, hitung={exp:.1f} cm, d={d:+.1f} cm (tol +/-10)")

    # folder check
    folders = set()
    for a in actors:
        if a.get_actor_label() in AREA_IDS or isinstance(a, (unreal.PlayerStart, unreal.TargetPoint)):
            folders.add(a.get_folder_path() if hasattr(a, "get_folder_path") else "?")
    log(f"folder penanda: {sorted(folders)}")

    # T1-T3 di_atap Z >= 990
    tzs = {}
    for pid in ("T1", "T2", "T3"):
        tp = next((a for a in actors if isinstance(a, unreal.TargetPoint) and a.get_actor_label() == pid), None)
        zt = tp.get_actor_location().z if tp else None
        tzs[pid] = zt
        log(f"  {pid} Z={zt:.0f} cm (harap >= 990)" if zt else f"  {pid} TIDAK ADA")
    t_ok = all(z is not None and z >= 990.0 for z in tzs.values())

    # wall "Hidden in Game" (bukan editor hide): set_actor_hidden_in_game(True) di skrip 50
    wbad = 0
    for a in actors:
        if a.get_actor_label() in WALL_LABELS:
            try:
                hidden = a.get_editor_property("is_hidden")
            except Exception:  # noqa: BLE001
                hidden = None
            if hidden is not None and not hidden:
                wbad += 1
    log(f"dinding tidak Hidden in Game: {wbad} (0)")

    ok = (n_start == 1 and n_titik == 15 and n_area == 7 and n_zona == 5 and n_dinding == 8
          and n_capture == 0 and got is not None and abs(d) <= 10.0 and t_ok and wbad == 0)
    log(f"WAKTU: {__import__('time').time() - t0:.1f} s")
    log(f"CEK MK5c (disk): {'LULUS' if (ok and not problems) else 'GAGAL'}")
    if problems:
        for p in problems:
            unreal.log_warning("  - " + p)


main()
