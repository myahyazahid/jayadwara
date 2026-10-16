"""V3 (tambahan) — screenshot viewport level v02 (Unreal Editor Python).

Level `Test_Hermes_MapsEp1_v02` HARUS sudah terbuka; skrip ini **tidak** memuat ulang level
(memuat ulang level merusak exposure SceneCapture -> render hitam, lihat catatan M6 v01).
Render SceneCapture2D aerial dari selatan -> Hermes/Art/maps_ep1/v02/Render/V3_viewport.png.

Pakai (dari WORKTREE, editor worktree terbuka, level v02 terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_31_viewport.py
"""
import os
import math

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_DIR = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Render")
LEVEL_NAME = "Test_Hermes_MapsEp1_v02"


def log(m):
    unreal.log(f"[V3r] {m}")


def render(nama, P, T, fov, frames, pps_override):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    d = T - P
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = eas.spawn_actor_from_class(
        unreal.SceneCapture2D, P, unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0))
    c = cap.capture_component2d
    c.set_editor_property("texture_target", rt)
    c.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    c.set_editor_property("fov_angle", fov)
    if pps_override:
        pps = c.get_editor_property("post_process_settings")
        for key, val in (("override_auto_exposure_method", True),
                         ("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM),
                         ("override_auto_exposure_speed_up", True), ("auto_exposure_speed_up", 400.0),
                         ("override_auto_exposure_speed_down", True), ("auto_exposure_speed_down", 400.0),
                         ("override_auto_exposure_min_brightness", True), ("auto_exposure_min_brightness", -6.0),
                         ("override_auto_exposure_max_brightness", True), ("auto_exposure_max_brightness", 20.0)):
            try:
                pps.set_editor_property(key, val)
            except Exception:  # noqa: BLE001
                pass
        c.set_editor_property("post_process_settings", pps)
    for _ in range(frames):
        c.capture_scene()
    px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 960, 540)
    log(f"{nama}: piksel tengah = ({px.r},{px.g},{px.b})  pitch={pitch:.1f} yaw={yaw:.1f} fov={fov} frames={frames}")
    os.makedirs(OUT_DIR, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(world, rt, OUT_DIR.replace("\\", "/"), nama)
    p = os.path.join(OUT_DIR, nama)
    if os.path.exists(p):
        os.replace(p, p + ".png")
    eas.destroy_actor(cap)
    return (px.r + px.g + px.b) / 3.0


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    nama = world.get_name() if world else None
    log(f"level terbuka: {nama}")
    if nama != LEVEL_NAME:
        unreal.log_error(f"[V3r] level terbuka bukan {LEVEL_NAME} — buka dulu, jangan lanjut")
        return
    # aerial dari selatan, sedikit lebih tegak supaya medan mendominasi (exposure tidak ditarik langit)
    P = unreal.Vector(8000.0, 82000.0, 88000.0)
    T = unreal.Vector(8000.0, -3000.0, 3000.0)
    v = render("V3_viewport", P, T, 62.0, 30, True)
    log(f"selesai; kecerahan tengah = {v:.1f}")


main()
