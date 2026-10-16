"""V6 — Kamera C1–C8 + cahaya sore/senja + render PNG (Unreal Editor Python).

Adaptasi `maps_ep1_60_kamera.py` v01 (skrip v01 TIDAK diubah). Bedanya: modul medan
`ep01_medan_v02`, JSON `ep01_layout_v02.json`, level `Test_Hermes_MapsEp1_v02`,
**8 kamera** (2 baru: C7_BaseCamp, C8_PilarTolRaksasa), render ke
`Hermes/Art/maps_ep1/v02/Render/<id>_<cahaya>.png` 1920x1080.

1. CameraActor per kamera JSON (label = id, folder `KAMERA`): posisi = `pos` + `tinggi_di_atas_tanah`
   di atas `elev`, arah ke `lihat_ke`, FOV dari JSON. `C5_TampakAtas` = ortografis (lebar
   `lebar_ortho` m), menghadap lurus ke bawah, yaw −90 supaya utara di atas (sama seperti denah docs/30).
2. Setel DirectionalLight sesuai `cahaya` kamera (`sore`/`senja`) sebelum render.
3. Render SceneCapture2D (ikut transform/FOV/ortho kamera) ke Render Target 1920x1080 -> PNG.
   Auto-exposure dipercepat (speed 200 + rentang brightness lebar) supaya beberapa frame cukup.
   Level TIDAK dimuat ulang (`load_level` merusak exposure SceneCapture -> render hitam).

Uji (cetak): 8 CameraActor, 8 PNG ada, tabel kamera.

Pakai (dari WORKTREE, editor worktree terbuka, level v02 terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_60_kamera.py
"""
import os
import sys
import json
import math

import unreal

DEST = "/Game/Hermes/MapsEp1"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp1_v02"
LEVEL_NAME = "Test_Hermes_MapsEp1_v02"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
from ep01_medan_v02 import elev  # noqa: E402

with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
KAMERA = DATA["kamera"]
CAHAYA = DATA["cahaya"]
CAM_LABELS = [k["id"] for k in KAMERA]

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

ORTHO_Z_M = 600.0   # tinggi kamera C5 (ortografis) di atas tanah, meter

problems = []


def log(m):
    unreal.log(f"[V6] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[V6] {m}")


def ue(x, y, z):
    """data (meter) -> UE (cm)."""
    return unreal.Vector(x * 100.0, -y * 100.0, z * 100.0)


def rot_lihat(dari, ke):
    d = ke - dari
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    return unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0)


def bersihkan():
    n = 0
    for a in list(EAS.get_all_level_actors()):
        if a.get_actor_label() in CAM_LABELS or a.get_folder_path() == "KAMERA":
            a.destroy_actor()
            n += 1
    log(f"hapus {n} CameraActor lama")


def dirlight():
    ds = [a for a in EAS.get_all_level_actors() if isinstance(a, unreal.DirectionalLight)]
    if not ds:
        fail("DirectionalLight tidak ditemukan")
        return None
    return ds[0]


def set_cahaya(nama):
    cfg = CAHAYA[nama]
    dl = dirlight()
    if dl is None:
        return None
    dl.set_actor_rotation(unreal.Rotator(pitch=float(cfg["pitch"]), yaw=float(cfg["yaw"]), roll=0.0), False)
    c = dl.light_component
    w = cfg["warna"]
    c.set_light_color(unreal.LinearColor(r=float(w[0]), g=float(w[1]), b=float(w[2]), a=1.0))
    c.set_editor_property("intensity", float(cfg["intensitas_lux"]))
    log(f"cahaya '{nama}': pitch={cfg['pitch']} yaw={cfg['yaw']} "
        f"warna=({w[0]:.2f},{w[1]:.2f},{w[2]:.2f}) intensitas={cfg['intensitas_lux']} lux")
    return dl


def build_camera(k):
    x, y = k["pos"]
    if k.get("ortho"):
        z = elev(x, y) + ORTHO_Z_M
        rot = unreal.Rotator(pitch=-90.0, yaw=-90.0, roll=0.0)   # lurus ke bawah, utara di atas
    else:
        z = elev(x, y) + float(k["tinggi_di_atas_tanah"])
        lk = k["lihat_ke"]
        rot = rot_lihat(ue(x, y, z), ue(lk[0], lk[1], lk[2]))
    loc = ue(x, y, z)
    a = EAS.spawn_actor_from_class(unreal.CameraActor, loc, rot)
    a.set_actor_label(k["id"])
    a.set_folder_path("KAMERA")
    cc = a.camera_component
    cc.set_editor_property("field_of_view", float(k["fov"]) if not k.get("ortho") else 90.0)
    if k.get("ortho"):
        cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
        cc.set_editor_property("ortho_width", float(k["lebar_ortho"]) * 100.0)
    log(f"{k['id']}: UE loc=({loc.x:.0f},{loc.y:.0f},{loc.z:.0f}) pitch={rot.pitch:.1f} yaw={rot.yaw:.1f} "
        f"{'ortho %.0f m' % k['lebar_ortho'] if k.get('ortho') else 'fov %.0f' % k['fov']} cahaya={k['cahaya']}")
    return a


def render(k, cam):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080,
                                                        unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, cam.get_actor_location(), cam.get_actor_rotation())
    c = cap.capture_component2d
    c.set_editor_property("texture_target", rt)
    c.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    if k.get("ortho"):
        c.set_editor_property("projection_type", unreal.CameraProjectionMode.ORTHOGRAPHIC)
        c.set_editor_property("ortho_width", float(k["lebar_ortho"]) * 100.0)
        for p, v in (("ortho_far_clip_plane", 100000.0), ("ortho_near_clip_plane", 0.0)):
            try:
                c.set_editor_property(p, v)
            except Exception:  # noqa: BLE001
                pass
    else:
        c.set_editor_property("fov_angle", float(k["fov"]))
    # auto-exposure: percepat adaptasi (cahaya senja 2 lux butuh ~40 frame kalau normal)
    pps = c.get_editor_property("post_process_settings")
    for key, val in (("override_auto_exposure_method", True),
                     ("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM),
                     ("override_auto_exposure_speed_up", True), ("auto_exposure_speed_up", 200.0),
                     ("override_auto_exposure_speed_down", True), ("auto_exposure_speed_down", 200.0),
                     ("override_auto_exposure_min_brightness", True), ("auto_exposure_min_brightness", -20.0),
                     ("override_auto_exposure_max_brightness", True), ("auto_exposure_max_brightness", 40.0)):
        try:
            pps.set_editor_property(key, val)
        except Exception as e:  # noqa: BLE001
            log(f"catatan: pps '{key}' gagal ({e})")
    c.set_editor_property("post_process_settings", pps)
    for _ in range(8):
        c.capture_scene()
    out_dir = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Render")
    os.makedirs(out_dir, exist_ok=True)
    name = f"{k['id']}_{k['cahaya']}"
    unreal.RenderingLibrary.export_render_target(world, rt, out_dir.replace("\\", "/"), name)
    p = os.path.join(out_dir, name)
    if os.path.exists(p):
        os.replace(p, p + ".png")
    px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 960, 540)
    log(f"render -> {name}.png ; tengah=({px.r},{px.g},{px.b})")
    EAS.destroy_actor(cap)
    return os.path.join(out_dir, name + ".png")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[V6] Editor sedang Play (PIE) — hentikan dulu")
        return
    if not EAL.does_asset_exist(MAP):
        fail(f"level {MAP} tidak ada")
        return
    # JANGAN memuat ulang level: `load_level` merusak exposure SceneCapture (render jadi hitam).
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    nama = world.get_name() if world else None
    if nama != LEVEL_NAME:
        LES.load_level(MAP)
        log(f"level dimuat ulang: {MAP} — kalau render gelap, jalankan skrip sekali lagi")
    else:
        log(f"level sudah terbuka: {nama} (tidak dimuat ulang)")

    bersihkan()
    if problems:
        return

    hasil = []
    cahaya_kini = None
    for k in KAMERA:
        if k["cahaya"] != cahaya_kini:
            set_cahaya(k["cahaya"])
            cahaya_kini = k["cahaya"]
        cam = build_camera(k)
        hasil.append(render(k, cam))

    LES.save_current_level()
    log("level disimpan")

    n_cam = sum(1 for a in EAS.get_all_level_actors() if a.get_folder_path() == "KAMERA")
    log(f"JUMLAH: CameraActor folder KAMERA = {n_cam} (target {len(KAMERA)})")
    ada = 0
    for p in hasil:
        if os.path.exists(p):
            ada += 1
        else:
            fail(f"PNG tidak ada: {p}")
    log(f"PNG ada = {ada}/{len(KAMERA)}")
    ok = (n_cam == len(KAMERA) and ada == len(KAMERA) and not problems)
    log(f"CEK V6: {'LULUS' if ok else 'GAGAL'}")
    for p in problems:
        unreal.log_warning("  - " + p)


main()
