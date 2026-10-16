"""MK5b — Screenshot tampak atas semua penanda (Unreal Editor Python, via Tools/ue_remote.py).

Render 1920x1080 dari ketinggian ~1.100 m lurus ke bawah menutup seluruh medan (1400 x 1000 m),
supaya semua penanda terlihat: silinder `area` (MI_Ep02_Penanda), label `zona` (TextRender 5 m),
dan label `titik` (TextRender 1,5 m). Dipisah dari 50_penanda karena render pada invokasi yang
sama dengan load_level sering gelap (lihat catatan Ep1).

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep2_51_shot.py
"""
import os
import math
import time

import unreal

DEST = "/Game/Hermes/MapsEp2"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp2"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RENDER = os.path.join(REPO, "Hermes", "Art", "maps_ep2", "Render")

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def log(m):
    unreal.log(f"[MK5b] {m}")


def render(nama, P, R, fov):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, P, R)
    cap.set_actor_label("MK5_Capture")
    comp = cap.capture_component2d
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    comp.set_editor_property("fov_angle", fov)
    pps = comp.get_editor_property("post_process_settings")
    for k, v in (("override_auto_exposure_method", True),
                 ("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM),
                 ("override_auto_exposure_speed_up", True), ("auto_exposure_speed_up", 200.0),
                 ("override_auto_exposure_speed_down", True), ("auto_exposure_speed_down", 200.0),
                 ("override_auto_exposure_min_brightness", True), ("auto_exposure_min_brightness", -20.0),
                 ("override_auto_exposure_max_brightness", True), ("auto_exposure_max_brightness", 40.0)):
        try:
            pps.set_editor_property(k, v)
        except Exception:  # noqa: BLE001
            pass
    comp.set_editor_property("post_process_settings", pps)
    for _ in range(8):
        comp.capture_scene()
    os.makedirs(RENDER, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(world, rt, RENDER.replace("\\", "/"), nama)
    png = os.path.join(RENDER, nama + ".png")
    raw = os.path.join(RENDER, nama)
    if os.path.exists(raw):
        os.replace(raw, png)
    tot = 0.0
    n = 0
    for i in range(6):
        for j in range(4):
            px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, int(1920 * (i + 0.5) / 6), int(1080 * (j + 0.5) / 4))
            tot += (px.r + px.g + px.b) / 3.0
            n += 1
    EAS.destroy_actor(cap)
    unreal.RenderingLibrary.release_render_target2d(rt)
    log(f"{nama}: kecerahan rata-rata = {tot / n:.1f}/255 ; {png}")
    return tot / n


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[MK5b] Editor sedang Play (PIE) -- hentikan dulu")
        return
    t0 = time.time()
    LES.load_level(MAP)
    log(f"level dimuat: {MAP}")
    for a in list(EAS.get_all_level_actors()):
        if a.get_actor_label() == "MK5_Capture":
            a.destroy_actor()

    # tampak atas: z 1.100 m lurus ke bawah, pusat (0, -100) [tengah medan], FOV 80 -> lebar ~1.846 m
    render("MK5_tampak_atas",
           unreal.Vector(0.0, 10000.0, 110000.0),
           unreal.Rotator(pitch=-90.0, yaw=0.0, roll=0.0), 80.0)
    # dekat pusat aktivitas (kampung + kali): z 350 m, pusat (0, -50), FOV 75 -> lebar ~536 m
    render("MK5_tampak_dekat",
           unreal.Vector(0.0, 5000.0, 35000.0),
           unreal.Rotator(pitch=-90.0, yaw=0.0, roll=0.0), 75.0)
    log(f"WAKTU skrip MK5b: {time.time() - t0:.1f} s")


main()
