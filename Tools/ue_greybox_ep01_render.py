"""Render kamera C1–C8 level Ep01_LawangSapta_Greybox ke PNG 1920x1080 (Unreal Editor Python).

Kamera dibuat oleh Tools/ue_greybox_ep01.py (folder KAMERA). Skrip ini memakai transform/FOV/ortho tiap CameraActor lewat SceneCapture2D,
menyetel cahaya sesuai kamera (`sore`/`senja`), lalu mengembalikan cahaya ke `sore`. Level TIDAK disimpan.

Level harus sudah terbuka dan skrip ini dijalankan sebagai invokasi TERPISAH dari ue_greybox_ep01.py: `load_level` di invokasi yang sama
merusak exposure SceneCapture (render gelap, temuan Hermes). Kalau level belum terbuka skrip memuatnya, lalu jalankan ulang sekali.

Keluaran: Saved/Ep01Greybox/<id>_<cahaya>.png (di luar Git).
Pakai: python Tools/ue_remote.py Tools/ue_greybox_ep01_render.py
"""
import json
import os

import unreal

MAP = "/Game/Jayadwara/Maps/Ep01_LawangSapta_Greybox"
LEVEL_NAME = "Ep01_LawangSapta_Greybox"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(REPO, "Saved", "Ep01Greybox")

with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
KAMERA, CAHAYA = DATA["kamera"], DATA["cahaya"]

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def log(m):
    unreal.log(f"[Ep01 render] {m}")


def set_cahaya(nama):
    cfg = CAHAYA[nama]
    dl = next(a for a in EAS.get_all_level_actors() if isinstance(a, unreal.DirectionalLight))
    dl.set_actor_rotation(unreal.Rotator(pitch=float(cfg["pitch"]), yaw=float(cfg["yaw"]), roll=0.0), False)
    w = cfg["warna"]
    dl.light_component.set_light_color(unreal.LinearColor(r=float(w[0]), g=float(w[1]), b=float(w[2]), a=1.0))
    dl.light_component.set_editor_property("intensity", float(cfg["intensitas_lux"]))


def render(k, cam):
    world = UES.get_editor_world()
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, cam.get_actor_location(), cam.get_actor_rotation())
    c = cap.capture_component2d
    c.set_editor_property("texture_target", rt)
    c.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    if k.get("ortho"):
        c.set_editor_property("projection_type", unreal.CameraProjectionMode.ORTHOGRAPHIC)
        c.set_editor_property("ortho_width", float(k["lebar_ortho"]) * 100.0)
    else:
        c.set_editor_property("fov_angle", float(k["fov"]))
    pps = c.get_editor_property("post_process_settings")
    for key, val in (("override_auto_exposure_method", True), ("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM),
                     ("override_auto_exposure_speed_up", True), ("auto_exposure_speed_up", 200.0),
                     ("override_auto_exposure_speed_down", True), ("auto_exposure_speed_down", 200.0),
                     ("override_auto_exposure_min_brightness", True), ("auto_exposure_min_brightness", -20.0),
                     ("override_auto_exposure_max_brightness", True), ("auto_exposure_max_brightness", 40.0)):
        try:
            pps.set_editor_property(key, val)
        except Exception:  # noqa: BLE001
            pass
    c.set_editor_property("post_process_settings", pps)
    for _ in range(8):
        c.capture_scene()
    os.makedirs(OUT, exist_ok=True)
    name = f"{k['id']}_{k['cahaya']}"
    unreal.RenderingLibrary.export_render_target(world, rt, OUT.replace("\\", "/"), name)
    p = os.path.join(OUT, name)
    if os.path.exists(p):
        os.replace(p, p + ".png")
    px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 960, 540)
    log(f"{name}.png tengah=({px.r},{px.g},{px.b})")
    EAS.destroy_actor(cap)


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Ep01 render] Editor sedang Play (PIE) — hentikan dulu")
        return
    world = UES.get_editor_world()
    if world is None or world.get_name() != LEVEL_NAME:
        LES.load_level(MAP)
        log(f"level dimuat: {MAP} — jalankan skrip ini sekali lagi supaya render tidak gelap")
        return
    cams = {a.get_actor_label(): a for a in EAS.get_all_level_actors() if a.get_folder_path() == "KAMERA"}
    cahaya = None
    for k in KAMERA:
        if k["id"] not in cams:
            unreal.log_error(f"[Ep01 render] kamera {k['id']} tidak ada — jalankan ue_greybox_ep01.py")
            continue
        if k["cahaya"] != cahaya:
            set_cahaya(k["cahaya"])
            cahaya = k["cahaya"]
        render(k, cams[k["id"]])
    set_cahaya("sore")
    log(f"selesai -> {OUT}")


main()
