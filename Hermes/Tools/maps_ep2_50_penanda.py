"""MK5 — Penanda, zona, batas arena Ep02 (Unreal Editor Python, via Tools/ue_remote.py).

Adaptasi `maps_ep1_v02_50_penanda.py` untuk Ep02: modul `ep02_medan_v02`, JSON
`ep02_layout_v02.json`, level `Test_Hermes_MapsEp2`, GameMode `BP_JDGameMode`,
batas arena 120 m (x -650..690, y -600..330), 5 zona, 23 penanda (1 PlayerStart +
15 titik + 7 area).

1. START -> PlayerStart (label START, folder PENANDA) di elev(-40,155)*100 + 1/2 tinggi
   kapsul (dari BP_JDGameMode.default_pawn_class), yaw -> hadap_ke (jembatan gantung).
   Hapus PlayerStart bawaan template.
2. `titik` -> TargetPoint + TextRenderActor (teks = label, huruf 150 cm, 3 m di atas titik).
   - `z`      : titik di z absolut (T4 dek jembatan 4,2 m, T5 menara 12,2 m).
   - `di_atap`: line trace turun dari z 60 m, titik diletakkan di kena pertama (puncak atap).
3. `area` -> Cylinder diameter 2*radius m, tinggi 0,2 m, MI_Ep02_Penanda, NoCollision + TextRender.
4. `zona` -> TriggerBox persegi x,y tinggi 60 m (label = id) + TextRender 500 cm (warna ikut data).
5. `batas_arena` -> 4 dinding tak terlihat tinggi 120 m (Hidden in Game, BlockAll) di tepi arena
   (x -650/690, y -600/330) + 4 dinding sama di tepi medan (-700/700, -600/400).

Uji: 1 PlayerStart, 15 titik, 7 area, 5 zona, 8 dinding; Z PlayerStart = elev(-40,155)*100 +
1/2 kapsul +/- 10 cm; T1-T3 (di_atap) Z >= 990 cm.

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep2_50_penanda.py
"""
import os
import sys
import json
import math

import unreal

DEST = "/Game/Hermes/MapsEp2"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp2"
MAT_DIR = f"{DEST}/Materials"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art", "Level", "ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
PENANDA = DATA["penanda"]
ZONA = DATA["zona"]
BATAS = DATA["batas_arena"]
MEDAN = DATA["medan"]
XMIN, XMAX = MEDAN["x_min"], MEDAN["x_max"]
YMIN, YMAX = MEDAN["y_min"], MEDAN["y_max"]
START_P = next(p for p in PENANDA if p["jenis"] == "PlayerStart")

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

problems = []
WALL_LABELS = [
    "BATAS_Arena_Barat", "BATAS_Arena_Timur", "BATAS_Arena_Selatan", "BATAS_Arena_Utara",
    "BATAS_Medan_Barat", "BATAS_Medan_Timur", "BATAS_Medan_Selatan", "BATAS_Medan_Utara",
]
WARNA = {"hijau": (0, 255, 60), "merah": (255, 40, 40), "ungu": (170, 40, 255)}


def log(m):
    unreal.log(f"[MK5] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[MK5] {m}")


def elev(x, y):
    return M.elev(x, y)


def sampel_seg(ax, ay, bx, by, step=5.0):
    n = max(1, int(math.hypot(bx - ax, by - ay) / step))
    return [elev(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n + 1)]


def mi(name):
    a = EAL.load_asset(f"{MAT_DIR}/MI_Ep02_{name}")
    if a is None:
        fail(f"MI_Ep02_{name} tidak ada")
    return a


def find_by_label(label):
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


def text_actor(label, loc, txt, size, folder, warna=None):
    a = EAS.spawn_actor_from_class(unreal.TextRenderActor, loc, unreal.Rotator(0.0, 0.0, 0.0))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    try:
        tr = a.text_render
    except Exception:  # noqa: BLE001
        tr = a.get_editor_property("text_render")
    tr.set_editor_property("text", unreal.Text(txt))
    tr.set_editor_property("world_size", float(size))
    if warna is not None:
        try:
            tr.set_editor_property("text_render_color", unreal.Color(r=warna[0], g=warna[1], b=warna[2], a=255))
        except Exception as e:  # noqa: BLE001
            log(f"warna teks {label} gagal ({e}) -- dilewati")
    return a


def half_capsule():
    try:
        gm = EAL.load_asset(GAMEMODE)
        cdo = unreal.get_default_object(gm.generated_class())
        pawn_cls = cdo.get_editor_property("default_pawn_class")
        if pawn_cls is None:
            log("default_pawn_class None (GameMode dasar) -> pakai 88.0 cm")
            return 88.0
        pcdo = unreal.get_default_object(pawn_cls)
        cap = pcdo.get_editor_property("capsule_component")
        h = float(cap.get_editor_property("capsule_half_height"))
        log(f"1/2 kapsul dari {pawn_cls.get_name()} = {h} cm")
        return h
    except Exception as e:  # noqa: BLE001
        log(f"gagal baca kapsul ({e}); pakai 88.0 cm (default ACharacter)")
        return 88.0


def roof_z(x, y):
    """Kena pertama line trace vertikal dari z 60 m ke bawah (meter); fallback elev."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    r = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x * 100.0, -y * 100.0, 6000.0), unreal.Vector(x * 100.0, -y * 100.0, -200.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if r is None:
        return elev(x, y)
    loc = r.to_tuple()[4]
    return (loc.z if loc is not None else elev(x, y) * 100.0) / 100.0


# ------------------------------------------------------------------ pembersihan
def bersihkan():
    labels = set()
    for p in PENANDA:
        labels.add(p["id"])
        labels.add(p["id"] + "_Teks")
    for z in ZONA:
        labels.add(z["id"])
        labels.add(z["id"] + "_Teks")
    for lbl in WALL_LABELS:
        labels.add(lbl)
    n = 0
    for a in list(EAS.get_all_level_actors()):
        if a.get_actor_label() in labels:
            a.destroy_actor()
            n += 1
    np_ = 0
    for a in list(EAS.get_all_level_actors()):
        if isinstance(a, unreal.PlayerStart):
            a.destroy_actor()
            np_ += 1
    log(f"hapus {n} actor MK5 lama + {np_} PlayerStart (termasuk bawaan)")


# ------------------------------------------------------------------ bangun
def build_start(hc):
    x, y = START_P["pos"]
    gx, gy = START_P["hadap_ke"]
    z = elev(x, y) * 100.0 + hc
    dx = gx * 100.0 - x * 100.0
    dy = -gy * 100.0 - (-y * 100.0)
    yaw = math.degrees(math.atan2(dy, dx))
    a = EAS.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(x * 100.0, -y * 100.0, z),
                                   unreal.Rotator(0.0, yaw, 0.0))
    a.set_actor_label("START")
    a.set_folder_path("PENANDA")
    log(f"START PlayerStart: Z={z:.1f} cm (= elev({x},{y})*100 {elev(x, y) * 100:.1f} + kapsul {hc:.1f}); "
        f"yaw={yaw:.1f} (-> jembatan {gx},{gy})")
    return a, z, yaw


def base_titik(p):
    """Alas titik (meter): z absolut bila ada; di_atap -> kena atap; lainnya elev."""
    if "z" in p:
        return float(p["z"])
    if p.get("di_atap"):
        rz = roof_z(p["pos"][0], p["pos"][1])
        log(f"  {p['id']} di_atap: kena atap z={rz:.2f} m")
        return rz
    return elev(p["pos"][0], p["pos"][1])


def build_titik(p):
    x, y = p["pos"]
    base = base_titik(p)
    loc = unreal.Vector(x * 100.0, -y * 100.0, base * 100.0 + 300.0)   # 3 m di atas titik
    tp = EAS.spawn_actor_from_class(unreal.TargetPoint, loc)
    tp.set_actor_label(p["id"])
    tp.set_folder_path("PENANDA")
    text_actor(p["id"] + "_Teks", loc, p["label"], 150.0, "PENANDA")
    log(f"  titik {p['id']}: base={base:.2f} m, TargetPoint Z={loc.z:.0f} cm")
    return tp


def build_area(p, mi_pen):
    x, y = p["pos"]
    r = float(p["radius"])
    gz = elev(x, y) * 100.0
    mesh = EAL.load_asset(CYLINDER)
    loc = unreal.Vector(x * 100.0, -y * 100.0, gz + 10.0)
    a = EAS.spawn_actor_from_object(mesh, loc)
    a.set_actor_label(p["id"])
    a.set_folder_path("PENANDA")
    a.set_actor_scale3d(unreal.Vector(r * 2.0, r * 2.0, 0.2))
    a.static_mesh_component.set_material(0, mi_pen)
    a.static_mesh_component.set_collision_profile_name("NoCollision")
    text_actor(p["id"] + "_Teks", unreal.Vector(loc.x, loc.y, gz + 300.0), p["label"], 150.0, "PENANDA")
    log(f"  area {p['id']}: radius {r} m, Z={gz + 10:.0f} cm")
    return a


def build_zona(z):
    xa, xb = z["x"]
    ya, yb = z["y"]
    cx, cy = (xa + xb) / 2.0, (ya + yb) / 2.0
    ex, ey = (xb - xa) / 2.0 * 100.0, (yb - ya) / 2.0 * 100.0
    ez = 30.0 * 100.0
    gz = elev(cx, cy) * 100.0
    loc = unreal.Vector(cx * 100.0, -cy * 100.0, gz + ez)
    a = EAS.spawn_actor_from_class(unreal.TriggerBox, loc)
    a.set_actor_label(z["id"])
    a.set_folder_path("ZONA")
    try:
        box = a.get_editor_property("collision_component")
    except Exception:  # noqa: BLE001
        box = a.collision_component
    box.set_box_extent(unreal.Vector(ex, ey, ez), False)
    warna = WARNA.get(z.get("warna"))
    text_actor(z["id"] + "_Teks", loc, z["label"], 500.0, "ZONA", warna)
    log(f"zona {z['id']}: extent=({ex:.0f},{ey:.0f},{ez:.0f}) cm, warna={z.get('warna')}")
    return a


def build_walls():
    h = float(BATAS["tinggi"])
    segs = [
        ("BATAS_Arena_Barat", (BATAS["x"][0], BATAS["y"][0]), (BATAS["x"][0], BATAS["y"][1])),
        ("BATAS_Arena_Timur", (BATAS["x"][1], BATAS["y"][0]), (BATAS["x"][1], BATAS["y"][1])),
        ("BATAS_Arena_Selatan", (BATAS["x"][0], BATAS["y"][0]), (BATAS["x"][1], BATAS["y"][0])),
        ("BATAS_Arena_Utara", (BATAS["x"][0], BATAS["y"][1]), (BATAS["x"][1], BATAS["y"][1])),
        ("BATAS_Medan_Barat", (XMIN, YMIN), (XMIN, YMAX)),
        ("BATAS_Medan_Timur", (XMAX, YMIN), (XMAX, YMAX)),
        ("BATAS_Medan_Selatan", (XMIN, YMIN), (XMAX, YMIN)),
        ("BATAS_Medan_Utara", (XMIN, YMAX), (XMAX, YMAX)),
    ]
    mesh = EAL.load_asset(CUBE)
    for label, (ax, ay), (bx, by) in segs:
        base = min(sampel_seg(ax, ay, bx, by, 5.0))
        dx, dy = (bx - ax) * 100.0, -(by - ay) * 100.0
        length_m = math.hypot(dx, dy) / 100.0
        yaw = math.degrees(math.atan2(dy, dx))
        cx, cy = (ax + bx) / 2.0 * 100.0, -(ay + by) / 2.0 * 100.0
        a = EAS.spawn_actor_from_object(mesh, unreal.Vector(cx, cy, (base + h / 2.0) * 100.0),
                                        unreal.Rotator(0.0, yaw, 0.0))
        a.set_actor_label(label)
        a.set_folder_path("BATAS")
        a.set_actor_scale3d(unreal.Vector(length_m, 2.0, h))
        a.static_mesh_component.set_collision_profile_name("BlockAll")
        a.set_actor_hidden_in_game(True)
    log(f"dibuat {len(segs)} dinding batas (Hidden in Game, BlockAll), tinggi {h:.0f} m")


# ------------------------------------------------------------------ uji
def uji(hc):
    def count(pred):
        return sum(1 for a in EAS.get_all_level_actors() if pred(a))
    n_start = count(lambda a: isinstance(a, unreal.PlayerStart))
    n_titik = count(lambda a: isinstance(a, unreal.TargetPoint))
    area_ids = {p["id"] for p in PENANDA if p["jenis"] == "area"}
    n_area = count(lambda a: isinstance(a, unreal.StaticMeshActor) and a.get_actor_label() in area_ids)
    n_zona = count(lambda a: isinstance(a, unreal.TriggerBox))
    n_dinding = count(lambda a: a.get_actor_label() in WALL_LABELS)
    log(f"JUMLAH: PlayerStart={n_start} (1) | titik={n_titik} (15) | area={n_area} (7) | "
        f"zona={n_zona} (5) | dinding={n_dinding} (8)")
    x, y = START_P["pos"]
    exp = elev(x, y) * 100.0 + hc
    a = find_by_label("START")
    got = a.get_actor_location().z if a else None
    d = (got - exp) if got is not None else None
    log(f"PlayerStart Z: aktual={got:.1f} cm, hitung={exp:.1f} cm, d={d:+.1f} cm (tol +/-10)")
    # T1-T3 (di_atap) Z >= 990 cm
    t_low = None
    for pid in ("T1", "T2", "T3"):
        tp = find_by_label(pid)
        zt = tp.get_actor_location().z if tp else None
        if zt is not None:
            log(f"  {pid} Z={zt:.0f} cm (harap >= 990)")
            t_low = zt if t_low is None else min(t_low, zt)
        else:
            fail(f"{pid} tidak ditemukan")
    t_ok = t_low is not None and t_low >= 990.0
    ok = (n_start == 1 and n_titik == 15 and n_area == 7 and n_zona == 5 and n_dinding == 8
          and got is not None and abs(d) <= 10.0 and t_ok)
    return ok


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[MK5] Editor sedang Play (PIE) -- hentikan dulu")
        return
    if not EAL.does_asset_exist(MAP):
        fail(f"level {MAP} tidak ada -- jalankan MK3 dulu")
        return
    LES.load_level(MAP)
    log(f"level dimuat: {MAP}")
    if find_by_label("SM_Ep02_Medan") is None:
        fail("SM_Ep02_Medan tidak ada -- jalankan MK3 dulu")
        return

    bersihkan()
    hc = half_capsule()
    mi_pen = mi("Penanda")
    if problems:
        return

    build_start(hc)
    n_t = n_a = 0
    for p in PENANDA:
        if p["jenis"] == "titik":
            build_titik(p)
            n_t += 1
        elif p["jenis"] == "area":
            build_area(p, mi_pen)
            n_a += 1
    log(f"penanda titik={n_t}, area={n_a}")
    for z in ZONA:
        build_zona(z)
    build_walls()

    ok = uji(hc)
    LES.save_current_level()
    log("level disimpan")
    log(f"CEK MK5: {'LULUS' if (ok and not problems) else 'GAGAL'}")
    if problems:
        for p in problems:
            unreal.log_warning("  - " + p)


main()
