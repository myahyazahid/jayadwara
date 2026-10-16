"""V4 (screenshot) — 4 sudut level v02 (Unreal Editor Python).

Level `Test_Hermes_MapsEp1_v02` HARUS sudah terbuka; skrip ini **tidak** memuat ulang level
(memuat ulang level merusak exposure SceneCapture -> render gelap, catatan M6 v01).
Render SceneCapture2D -> Hermes/Art/maps_ep1/v02/Render/V4_*.png (1920x1080).

Pakai (dari WORKTREE, editor worktree terbuka, level v02 terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_41_shot.py
"""
import os
import math

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_DIR = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Render")
LEVEL_NAME = "Test_Hermes_MapsEp1_v02"

# (nama, kamera P (UE cm), lihat T (UE cm), fov)
SHOTS = [
    ("V4_desa",         (-16000.0, 42500.0, 250.0),  (-31000.0, 39500.0, 350.0),  70.0),   # desa dari START
    ("V4_basecamp",     (47000.0, 3000.0, 2800.0),   (22000.0, -1000.0, 2500.0),  70.0),   # base camp dari jalan akses
    ("V4_pilartol",     (43000.0, 19000.0, 5000.0),  (63000.0, -9000.0, 3800.0),  72.0),   # area pilar tol
    ("V4_hutanperwara", (0.0, -32000.0, 9000.0),     (500.0, -43000.0, 4300.0),   75.0),   # hutan perwara
]


def log(m):
    unreal.log(f"[V4s] {m}")


def shot(name, P, T, fov, frames=30):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    P, T = unreal.Vector(*P), unreal.Vector(*T)
    d = T - P
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = eas.spawn_actor_from_class(
        unreal.SceneCapture2D, P, unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0))
    comp = cap.capture_component2d
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    comp.set_editor_property("fov_angle", fov)
    for _ in range(frames):
        comp.capture_scene()
    os.makedirs(OUT_DIR, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(world, rt, OUT_DIR.replace("\\", "/"), name)
    no_ext = os.path.join(OUT_DIR, name)
    if os.path.exists(no_ext):
        os.replace(no_ext, no_ext + ".png")
    png = os.path.join(OUT_DIR, name + ".png")
    px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 960, 540)
    lum = (px.r + px.g + px.b) / 3.0
    log("%-16s -> %s ; piksel tengah = %.0f,%.0f,%.0f (lum %.0f) pitch=%.1f" % (name, png, px.r, px.g, px.b, lum, pitch))
    eas.destroy_actor(cap)
    return lum


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    nama = world.get_name() if world else None
    log(f"level terbuka: {nama}")
    if nama != LEVEL_NAME:
        unreal.log_error(f"[V4s] level terbuka bukan {LEVEL_NAME} — buka dulu, jangan lanjut")
        return
    for name, P, T, fov in SHOTS:
        shot(name, P, T, fov)
    log("selesai")


main()
