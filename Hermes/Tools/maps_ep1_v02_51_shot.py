"""V5 (screenshot) — tampak atas level v02 (Unreal Editor Python).

Level `Test_Hermes_MapsEp1_v02` HARUS sudah terbuka; skrip ini **tidak** memuat ulang level
(memuat ulang level merusak exposure SceneCapture -> render gelap; catatan M6 v01 / V3).
Render SceneCapture2D ortografis -> Hermes/Art/maps_ep1/v02/Render/V5_*.png (1920x1080):
  - V5_tampak_atas      : seluruh arena (ortografis, utara di atas)
  - V5_candi_atas       : zoom halaman candi (label terbaca)
  - V5_tampak_atas_pin  : sama dengan di atas + pin debug sementara di setiap penanda
Pin/overlay dibangun sementara lalu dihapus (TargetPoint/TriggerBox/PlayerStart tidak
punya geometri game-view).

Pakai (dari WORKTREE, editor worktree terbuka, level v02 terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_51_shot.py
"""
import os
import sys
import json
import math

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
from ep01_medan_v02 import elev  # noqa: E402

OUT_DIR = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Render")
LEVEL_NAME = "Test_Hermes_MapsEp1_v02"
MAT_DIR = "/Game/Hermes/MapsEp1/Materials"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"

with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
PENANDA, ZONA = DATA["penanda"], DATA["zona"]
WALL_LABELS = [
    "BATAS_Arena_Barat", "BATAS_Arena_Timur", "BATAS_Arena_Selatan", "BATAS_Arena_Utara",
    "BATAS_Medan_Barat", "BATAS_Medan_Timur", "BATAS_Medan_Selatan", "BATAS_Medan_Utara",
]

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def log(m):
    unreal.log(f"[V5s] {m}")


def shot(name, P, T, ortho_m):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    d = T - P
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, P, unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0))
    c = cap.capture_component2d
    c.set_editor_property("texture_target", rt)
    c.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    c.set_editor_property("projection_type", unreal.CameraProjectionMode.ORTHOGRAPHIC)
    c.set_editor_property("ortho_width", ortho_m * 100.0)
    for _ in range(12):
        c.capture_scene()
    os.makedirs(OUT_DIR, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(world, rt, OUT_DIR.replace("\\", "/"), name)
    p = os.path.join(OUT_DIR, name)
    if os.path.exists(p):
        os.replace(p, p + ".png")
    px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 960, 540)
    log("%-20s -> %s ; tengah=%.0f,%.0f,%.0f" % (name, os.path.join(OUT_DIR, name + ".png"), px.r, px.g, px.b))
    EAS.destroy_actor(cap)


def build_overlay():
    ov = []
    mesh_c = EAL.load_asset(CUBE)
    mesh_cyl = EAL.load_asset(CYLINDER)
    mi_pin = EAL.load_asset(f"{MAT_DIR}/MI_Ep01_Alat")
    mi_pen = EAL.load_asset(f"{MAT_DIR}/MI_Ep01_Penanda")
    for p in PENANDA:
        x, y = p["pos"]
        d = EAS.spawn_actor_from_object(mesh_cyl, unreal.Vector(x * 100.0, -y * 100.0, 20000.0))
        d.set_actor_scale3d(unreal.Vector(28.0, 28.0, 1.0))      # r=14 m, melayang 200 m
        d.static_mesh_component.set_material(0, mi_pin)
        d.static_mesh_component.set_collision_profile_name("NoCollision")
        d.set_actor_label("_ov_pin")
        ov.append(d)
    for z in ZONA:
        xa, xb = z["x"]
        ya, yb = z["y"]
        cx, cy = (xa + xb) / 2.0, (ya + yb) / 2.0
        gz = elev(cx, cy) * 100.0
        a = EAS.spawn_actor_from_object(mesh_c, unreal.Vector(cx * 100.0, -cy * 100.0, gz + 25.0))
        a.set_actor_scale3d(unreal.Vector((xb - xa), (yb - ya), 0.5))
        a.static_mesh_component.set_material(0, mi_pen)
        a.static_mesh_component.set_collision_profile_name("NoCollision")
        a.set_actor_label("_ov_zona")
        ov.append(a)
    for lbl in WALL_LABELS:
        w = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == lbl), None)
        if w is None:
            continue
        a = EAS.spawn_actor_from_object(mesh_c, w.get_actor_location(), w.get_actor_rotation())
        a.set_actor_scale3d(w.get_actor_scale3d())
        a.static_mesh_component.set_material(0, mi_pen)
        a.static_mesh_component.set_collision_profile_name("NoCollision")
        a.set_actor_label("_ov_wall")
        ov.append(a)
    log(f"overlay debug: {len(ov)} actor (sementara)")
    return ov


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    nama = world.get_name() if world else None
    log(f"level terbuka: {nama}")
    if nama != LEVEL_NAME:
        unreal.log_error(f"[V5s] level terbuka bukan {LEVEL_NAME} — buka dulu, jangan lanjut")
        return

    # seluruh arena (x -470..720, y -525..500) -> pusat (125,-12,5) -> UE (12500,1250)
    shot("V5_tampak_atas", unreal.Vector(12500.0, 1250.0, 80000.0), unreal.Vector(12500.0, 1250.0, 0.0), 2000.0)
    # zoom halaman candi (plato)
    shot("V5_candi_atas", unreal.Vector(0.0, -17500.0, 30000.0), unreal.Vector(0.0, -17500.0, 0.0), 400.0)
    # dengan pin debug
    ov = build_overlay()
    shot("V5_tampak_atas_pin", unreal.Vector(12500.0, 1250.0, 80000.0), unreal.Vector(12500.0, 1250.0, 0.0), 2000.0)
    for a in ov:
        a.destroy_actor()
    log("selesai")


main()
