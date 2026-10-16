"""V7 (tambahan) — rute Aksa diukur di MESH NYATA (line trace), bukan hanya `elev` analitik.

Kenapa: `elev()` analitik punya diskontinuitas (mis. tangga tanah ~2 m di tepi sawah/desa)
yang tidak bisa diwakili grid mesh 2,5 m (lihat catatan "artefak resolusi" laporan v01 M2).
Akibatnya lereng maks versi analitik (63 deg) lebih terjal dari yang benar-benar dilalui pawn.

Skrip ini:
1. baca parameter pawn dari CDO GameMode level (`BP_JDGameMode_Aksa2` -> default_pawn_class):
   `MaxWalkSpeed`, `MaxStepHeight`, `WalkableFloorAngle`;
2. line trace turun tiap 1 m sepanjang `rute_aksa` (hanya mengenai SM_Ep01_Medan_v02);
3. cetak panjang permukaan mesh per ruas + lereng maks, banding dengan versi `elev` analitik;
4. cek lereng maks mesh < `WalkableFloorAngle`.

Tidak mengubah level/aset apa pun. Pakai (editor worktree terbuka, level v02 terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_72_rute_mesh.py
"""
import json
import math
import os
import sys

import unreal

DEST = "/Game/Hermes/MapsEp1"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp1_v02"
LEVEL_NAME = "Test_Hermes_MapsEp1_v02"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode_Aksa2"
MEDAN_LABEL = "SM_Ep01_Medan_v02"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
from ep01_medan_v02 import elev  # noqa: E402

LANGKAH_M = 1.0
with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
TITIK = [(float(x), float(y)) for x, y in DATA["rute_aksa"]]

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
problems = []


def log(m):
    unreal.log(f"[V7m] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[V7m] {m}")


def pawn_params():
    """MaxWalkSpeed / MaxStepHeight / WalkableFloorAngle dari CDO pawn GameMode."""
    out = {}
    try:
        gm = unreal.load_asset(GAMEMODE)
        cdo = unreal.get_default_object(gm.generated_class())
        cls = cdo.get_editor_property("default_pawn_class")
        pcdo = unreal.get_default_object(cls)
        out["pawn"] = pcdo.get_class().get_name()
        cm = pcdo.get_editor_property("character_movement")
        out["max_walk_speed"] = float(cm.get_editor_property("max_walk_speed"))
        out["max_step_height"] = float(cm.get_editor_property("max_step_height"))
        out["walkable_floor_angle"] = float(cm.get_editor_property("walkable_floor_angle"))
    except Exception as e:  # noqa: BLE001
        fail(f"gagal baca CDO pawn: {e}")
    return out


def mesh_z(world, ignore, x, y):
    ue_x, ue_y = x * 100.0, -y * 100.0
    res = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(ue_x, ue_y, 20000.0), unreal.Vector(ue_x, ue_y, -20000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore,
        unreal.DrawDebugTrace.NONE, True)
    tup = res.to_tuple()
    if not tup[0]:
        return None
    return tup[4].z / 100.0


def ruas(world, ignore, a, b):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(math.ceil(d / LANGKAH_M)))
    Lm = La = 0.0
    maks = 0.0
    zm0 = zm1 = None
    prev_m = prev_a = None
    miss = 0
    for i in range(n + 1):
        t = i / n
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        z = mesh_z(world, ignore, x, y)
        if z is None:
            miss += 1
            continue
        if zm0 is None:
            zm0 = z
        zm1 = z
        za = elev(x, y)
        if prev_m is not None:
            dd = math.hypot(x - prev_m[0], y - prev_m[1])
            Lm += math.hypot(dd, z - prev_m[2])
            La += math.hypot(dd, za - prev_a[2])
            if dd > 1e-9:
                maks = max(maks, abs(z - prev_m[2]) / dd)
        prev_m = (x, y, z)
        prev_a = (x, y, za)
    return {"datar": d, "mesh": Lm, "elev": La, "z0": zm0, "z1": zm1, "maks": maks, "miss": miss}


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    nama = world.get_name() if world else None
    if nama != LEVEL_NAME:
        LES.load_level(MAP)
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        log(f"level dimuat: {MAP}")
    else:
        log(f"level sudah terbuka: {nama}")

    par = pawn_params()
    if par:
        log(f"pawn {par.get('pawn')}: MaxWalkSpeed={par.get('max_walk_speed')} cm/s "
            f"MaxStepHeight={par.get('max_step_height')} cm WalkableFloorAngle={par.get('walkable_floor_angle'):.2f} deg")

    ignore = [a for a in EAS.get_all_level_actors() if a.get_actor_label() != MEDAN_LABEL]
    log(f"line trace hanya mengenai '{MEDAN_LABEL}' (abaikan {len(ignore)} actor lain)")

    v = par.get("max_walk_speed", 500.0) / 100.0
    log("RUTE AKSA di MESH nyata vs elev analitik (sampel tiap %.0f m)" % LANGKAH_M)
    log("%-4s %9s %11s %11s %8s %8s %9s" % ("ruas", "datar(m)", "mesh(m)", "elev(m)", "z awal", "z akhir", "lereng"))
    tot_d = tot_m = tot_a = 0.0
    maks_semua = 0.0
    maks_ruas = 0
    n_miss = 0
    for i in range(len(TITIK) - 1):
        r = ruas(world, ignore, TITIK[i], TITIK[i + 1])
        tot_d += r["datar"]
        tot_m += r["mesh"]
        tot_a += r["elev"]
        n_miss += r["miss"]
        if r["maks"] > maks_semua:
            maks_semua, maks_ruas = r["maks"], i + 1
        log("%-4d %9.2f %11.2f %11.2f %8.2f %8.2f %8.1f%%" % (
            i + 1, r["datar"], r["mesh"], r["elev"], r["z0"] if r["z0"] is not None else -999,
            r["z1"] if r["z1"] is not None else -999, r["maks"] * 100.0))
    log("TOTAL  datar=%.2f m | mesh=%.2f m | elev=%.2f m | waktu=%.1f s (%.1f menit)" % (
        tot_d, tot_m, tot_a, tot_m / v, tot_m / v / 60.0))
    log("lereng maks mesh = %.1f deg (%.0f%%) di ruas %d ; lereng maks elev analitik = %.1f deg" % (
        math.degrees(math.atan(maks_semua)), maks_semua * 100.0, maks_ruas,
        math.degrees(math.atan(2.003))))
    log("selisih mesh vs elev = %+.2f m (%.2f%%) ; titik MISS = %d" % (
        tot_m - tot_a, (tot_m - tot_a) / tot_a * 100.0, n_miss))
    log("target panduan V7 = 735 m ; mesh %+.1f m | elev %+.1f m" % (tot_m - 735.0, tot_a - 735.0))

    wa = par.get("walkable_floor_angle")
    ok_slope = wa is not None and math.degrees(math.atan(maks_semua)) < wa
    ok_miss = (n_miss == 0)
    ok = ok_slope and ok_miss and not problems
    log(f"CEK V7-mesh: lereng_maks<WalkableFloorAngle={ok_slope} tanpa_MISS={ok_miss} -> "
        f"{'LULUS' if ok else 'GAGAL'}")
    for p in problems:
        unreal.log_warning("  - " + p)


main()
