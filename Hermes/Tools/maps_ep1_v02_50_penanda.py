"""V5 — Penanda gameplay, zona, batas arena Ep01 v02 (Unreal Editor Python).

Adaptasi `maps_ep1_50_penanda.py` v01 (skrip v01 TIDAK diubah). Bedanya: modul medan
`ep01_medan_v02`, JSON `ep01_layout_v02.json`, level `Test_Hermes_MapsEp1_v02`,
GameMode `BP_JDGameMode_Aksa2`, batas arena 120 m, 4 zona, 13 penanda (8 titik + 4 area),
render ke `Hermes/Art/maps_ep1/v02/Render/`.

1. START -> PlayerStart (label START, folder PENANDA) di elev(-160,-425)*100 + 1/2 tinggi
   kapsul, yaw -> hadap_ke (gerbang candi). Hapus PlayerStart bawaan template.
2. Penanda `titik` -> TargetPoint + TextRenderActor (teks = label, tinggi huruf 150 cm, 3 m di atas tanah).
   `LORE_*` diberi teks **biru** (opsional/usulan, §V5 panduan).
3. Penanda `area`  -> Cylinder radius `radius` m, tinggi 0,2 m, MI_Ep01_Penanda, NoCollision + TextRender.
4. `zona` -> TriggerBox seukuran persegi x,y, tinggi 60 m (label = id) + TextRender besar 500 cm;
   warna teks ikut `warna` data (hijau/merah).
5. `batas_arena` -> 4 dinding kotak tak terlihat (Hidden in Game, BlockAll), tinggi 120 m, di tepi persegi;
   + 4 dinding sama di tepi medan (-620/780, -580/640) sebagai pengaman jatuh.

Uji (cetak): 1 PlayerStart, 8 titik, 4 area, 4 zona, 8 dinding;
Z PlayerStart = elev(-160,-425)*100 + 1/2 kapsul +/- 10 cm.

Screenshot tampak atas dibuat terpisah oleh `maps_ep1_v02_51_shot.py` (render SceneCapture
di invokasi yang sama dengan load_level menghasilkan gambar gelap).

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_50_penanda.py
"""
import os
import sys
import json
import math

import unreal

DEST = "/Game/Hermes/MapsEp1"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp1_v02"
LEVEL_NAME = "Test_Hermes_MapsEp1_v02"
MAT_DIR = f"{DEST}/Materials"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
GAMEMODE = "/Game/Jayadwara/Core/BP_JDGameMode_Aksa2"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
from ep01_medan_v02 import elev  # noqa: E402

LAYOUT = os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json")
with open(LAYOUT, encoding="utf-8") as f:
    DATA = json.load(f)
PENANDA = DATA["penanda"]
ZONA = DATA["zona"]
BATAS = DATA["batas_arena"]
MEDAN = DATA["medan"]
XMIN, XMAX = MEDAN["x_min"], MEDAN["x_max"]
YMIN, YMAX = MEDAN["y_min"], MEDAN["y_max"]
START_POS = [p["pos"] for p in PENANDA if p["jenis"] == "PlayerStart"][0]

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

problems = []
WALL_LABELS = [
    "BATAS_Arena_Barat", "BATAS_Arena_Timur", "BATAS_Arena_Selatan", "BATAS_Arena_Utara",
    "BATAS_Medan_Barat", "BATAS_Medan_Timur", "BATAS_Medan_Selatan", "BATAS_Medan_Utara",
]
WARNA = {"hijau": (0, 255, 60), "merah": (255, 40, 40), "biru": (40, 140, 255)}


def log(m):
    unreal.log(f"[V5] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[V5] {m}")


def sampel_seg(ax, ay, bx, by, step=5.0):
    n = max(1, int(math.hypot(bx - ax, by - ay) / step))
    return [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n,
             elev(ax + (bx - ax) * i / n, ay + (by - ay) * i / n)) for i in range(n + 1)]


def mi(name):
    a = EAL.load_asset(f"{MAT_DIR}/MI_Ep01_{name}")
    if a is None:
        fail(f"MI_Ep01_{name} tidak ada")
    return a


def text_actor(label, loc, txt, size, folder, warna=None):
    a = EAS.spawn_actor_from_class(unreal.TextRenderActor, loc, unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0))
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
            log(f"warna teks {label} gagal ({e}) — dilewati")
    return a


def half_capsule():
    try:
        gm = EAL.load_asset(GAMEMODE)
        cdo = unreal.get_default_object(gm.generated_class())
        pawn_cls = cdo.get_editor_property("default_pawn_class")
        pcdo = unreal.get_default_object(pawn_cls)
        cap = pcdo.get_editor_property("capsule_component")
        h = float(cap.get_editor_property("capsule_half_height"))
        log(f"1/2 tinggi kapsul dari {pawn_cls.get_name()} = {h} cm")
        return h
    except Exception as e:  # noqa: BLE001
        log(f"gagal baca kapsul ({e}); pakai 88.0 cm (default ACharacter)")
        return 88.0


def find_by_label(label):
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


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
    log(f"hapus {n} actor V5 lama + {np_} PlayerStart (termasuk bawaan template)")


# ------------------------------------------------------------------ bangun penanda
def build_start(p, hc):
    x, y = p["pos"]
    gx, gy = p["hadap_ke"]
    z = elev(x, y) * 100.0 + hc
    dx, dy = gx * 100.0 - x * 100.0, -gy * 100.0 - (-y * 100.0)
    yaw = math.degrees(math.atan2(dy, dx))
    a = EAS.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(x * 100.0, -y * 100.0, z),
                                   unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0))
    a.set_actor_label("START")
    a.set_folder_path("PENANDA")
    log(f"START PlayerStart: Z={z:.1f} cm (= elev({x},{y})*100 {elev(x, y) * 100:.1f} + kapsul {hc:.1f}); yaw={yaw:.1f} (-> gerbang)")
    return a, z, yaw


def build_titik(p):
    x, y = p["pos"]
    gz = elev(x, y) * 100.0
    loc = unreal.Vector(x * 100.0, -y * 100.0, gz + 300.0)
    tp = EAS.spawn_actor_from_class(unreal.TargetPoint, loc)
    tp.set_actor_label(p["id"])
    tp.set_folder_path("PENANDA")
    warna = WARNA["biru"] if p["id"].startswith("LORE_") else None
    text_actor(p["id"] + "_Teks", loc, p["label"], 150.0, "PENANDA", warna)
    return tp


def build_area(p, mi_pen):
    x, y = p["pos"]
    r = float(p["radius"])
    gz = elev(x, y) * 100.0
    mesh = EAL.load_asset(CYLINDER)
    loc = unreal.Vector(x * 100.0, -y * 100.0, gz + 10.0)   # tinggi 0,2 m -> pusat +10 cm
    a = EAS.spawn_actor_from_object(mesh, loc)
    a.set_actor_label(p["id"])
    a.set_folder_path("PENANDA")
    a.set_actor_scale3d(unreal.Vector(r * 2.0, r * 2.0, 0.2))
    a.static_mesh_component.set_material(0, mi_pen)
    a.static_mesh_component.set_collision_profile_name("NoCollision")
    text_actor(p["id"] + "_Teks", unreal.Vector(loc.x, loc.y, gz + 300.0), p["label"], 150.0, "PENANDA")
    return a


def build_zona(z):
    xa, xb = z["x"]
    ya, yb = z["y"]
    cx, cy = (xa + xb) / 2.0, (ya + yb) / 2.0
    ex, ey = (xb - xa) / 2.0 * 100.0, (yb - ya) / 2.0 * 100.0
    ez = 30.0 * 100.0                       # tinggi 60 m -> setengah 30 m
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
    log(f"zona {z['id']}: extent=({ex:.0f},{ey:.0f},{ez:.0f}) cm, tengah z={gz:.0f} cm, warna={z.get('warna')}")
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
        base = min(p[2] for p in sampel_seg(ax, ay, bx, by, 5.0))
        dx, dy = (bx - ax) * 100.0, -(by - ay) * 100.0
        length_m = math.hypot(dx, dy) / 100.0
        yaw = math.degrees(math.atan2(dy, dx))
        cx, cy = (ax + bx) / 2.0 * 100.0, -(ay + by) / 2.0 * 100.0
        a = EAS.spawn_actor_from_object(mesh, unreal.Vector(cx, cy, (base + h / 2.0) * 100.0),
                                        unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0))
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
    n_area = count(lambda a: isinstance(a, unreal.StaticMeshActor)
                   and a.get_actor_label() in {p["id"] for p in PENANDA if p["jenis"] == "area"})
    n_zona = count(lambda a: isinstance(a, unreal.TriggerBox))
    n_dinding = count(lambda a: a.get_actor_label() in WALL_LABELS)
    log(f"JUMLAH: PlayerStart={n_start} (1) | titik={n_titik} (8) | area={n_area} (4) | zona={n_zona} (4) | dinding={n_dinding} (8)")
    x, y = START_POS
    exp = elev(x, y) * 100.0 + hc
    a = find_by_label("START")
    got = a.get_actor_location().z if a else None
    d = (got - exp) if got is not None else None
    log(f"PlayerStart Z: aktual={got:.1f} cm, hitung={exp:.1f} cm, d={d:+.1f} cm (tol +/-10)")
    ok = (n_start == 1 and n_titik == 8 and n_area == 4 and n_zona == 4 and n_dinding == 8
          and got is not None and abs(d) <= 10.0)
    return ok


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[V5] Editor sedang Play (PIE) — hentikan dulu")
        return
    if not EAL.does_asset_exist(MAP):
        fail(f"level {MAP} tidak ada — jalankan V3 dulu")
        return
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world.get_name() != LEVEL_NAME:
        LES.load_level(MAP)
        log(f"level dimuat: {MAP}")
    else:
        log(f"level sudah terbuka: {LEVEL_NAME}")

    bersihkan()
    hc = half_capsule()
    mi_pen = mi("Penanda")
    if problems:
        return

    start_p = next(p for p in PENANDA if p["jenis"] == "PlayerStart")
    build_start(start_p, hc)
    n_t = 0
    for p in PENANDA:
        if p["jenis"] == "titik":
            build_titik(p)
            n_t += 1
        elif p["jenis"] == "area":
            build_area(p, mi_pen)
    log(f"penanda titik={n_t}, area={sum(1 for p in PENANDA if p['jenis'] == 'area')}")
    for z in ZONA:
        build_zona(z)
    build_walls()

    ok = uji(hc)
    LES.save_current_level()
    log("level disimpan")

    log(f"CEK V5: {'LULUS' if (ok and not problems) else 'GAGAL'}")
    if problems:
        for p in problems:
            unreal.log_warning("  - " + p)


main()
