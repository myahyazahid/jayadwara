"""MK6 -- Kamera C1-C8 + render per cahaya (Unreal Editor Python, via Tools/ue_remote.py).

`Hermes/Tools/maps_ep2_60_kamera.py`:
- CameraActor per kamera (label C1..C8, folder KAMERA) di `pos` + `tinggi_di_atas_tanah`
  di atas permukaan pertama line-trace dari atas (supaya C2 berdiri di atap). Khusus kamera
  yang trace kena struktur di atas kepala (dek layang, overhead > 5 m di atas elevasi medan)
  -> pakai elevasi medan (supaya C1 di jalan raya di bawah dek, bukan di atas dek).
- Arah `lihat_ke` (yaw + pitch dari vektor kamera->target). FOV dari JSON.
- `C5_TampakAtas` ortografis (projection_type=ORTHOGRAPHIC, ortho_width=1450 m), lurus ke bawah.
- DirectionalLight level diset ke preset `cahaya` (siang/sore/keemasan: pitch/yaw/warna/intensitas)
  sebelum tiap render.
- SceneCapture2D 1920x1080 -> Hermes/Art/maps_ep2/Render/<id>_<cahaya>.png.

Lulus: 8 PNG 1920x1080, rata-rata kecerahan > 20/255.
Pakai: python Tools/ue_remote.py Hermes/Tools/maps_ep2_60_kamera.py
"""
import os
import sys
import json
import math
import time

import unreal

DEST = "/Game/Hermes/MapsEp2"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp2"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RENDER = os.path.join(REPO, "Hermes", "Art", "maps_ep2", "Render")

sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art/Level/ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
KAM = DATA["kamera"]
CAHAYA = DATA["cahaya"]

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

problems = []


def log(m):
    unreal.log(f"[MK6] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[MK6] {m}")


def elev(x, y):
    return M.elev(x, y)


def trace_down(x, y):
    """Kena pertama line trace vertikal dari z 60 m (meter); None bila tak kena."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    r = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x * 100.0, -y * 100.0, 6000.0), unreal.Vector(x * 100.0, -y * 100.0, -200.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if r is None:
        return None
    loc = r.to_tuple()[4]
    return (loc.z / 100.0) if loc is not None else None


def cam_base(x, y):
    """Alas kamera (m): trace bila permukaan berdiri; terrain bila trace kena struktur di atas kepala."""
    tz = trace_down(x, y)
    gz = elev(x, y)
    if tz is None:
        return gz, gz, 0.0, "tanah(nohit)"
    overhead = tz - gz
    if overhead > 5.0:
        return gz, tz, overhead, "tanah(overhead)"
    return tz, tz, overhead, "trace"


def look_rot(x, y, cam_z, target):
    lx, ly, lz = target[0], target[1], target[2]
    dx = (lx - x) * 100.0
    dy = (y - ly) * 100.0          # UE y = -y_json -> dy_UE = (y - ly)*100
    dz = (lz - cam_z) * 100.0
    horiz = math.hypot(dx, dy)
    yaw = math.degrees(math.atan2(dy, dx))
    pitch = math.degrees(math.atan2(dz, horiz)) if horiz > 1e-6 else (90.0 if dz > 0 else -90.0)
    r = unreal.Rotator()
    r.set_editor_property("pitch", pitch)
    r.set_editor_property("yaw", yaw)
    r.set_editor_property("roll", 0.0)
    return r


def find_light():
    for a in EAS.get_all_level_actors():
        if isinstance(a, unreal.DirectionalLight):
            return a
    a = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 3000), unreal.Rotator(-62, 20, 0))
    log("(buat DirectionalLight baru)")
    return a


def set_cahaya(light, name):
    p = CAHAYA[name]
    # Rotator() argumen posisional salah urutan (pitch jadi +20) -> pakai set_editor_property per-attr
    r = unreal.Rotator()
    r.set_editor_property("pitch", float(p["pitch"]))
    r.set_editor_property("yaw", float(p["yaw"]))
    r.set_editor_property("roll", 0.0)
    light.set_actor_rotation(r, False)
    try:
        lc = light.get_editor_property("light_component")
    except Exception:  # noqa: BLE001
        lc = light.get_components_by_class(unreal.LightComponent)[0]
    lc.set_editor_property("intensity", float(p["intensitas_lux"]))
    w = p["warna"]
    lc.set_editor_property("light_color", unreal.Color(int(w[0] * 255), int(w[1] * 255), int(w[2] * 255), 255))
    rb = light.get_actor_rotation()
    log(f"cahaya={name}: pitch={rb.pitch:.0f} yaw={rb.yaw:.0f} (target {p['pitch']}/{p['yaw']}) lux={p['intensitas_lux']} warna={w}")


def render_shot(fname, loc, rot, fov, ortho, ortho_w, bias=0.0):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, loc, rot)
    cap.set_actor_label("MK6_Capture")
    comp = cap.capture_component2d
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    if ortho:
        comp.set_editor_property("projection_type", unreal.CameraProjectionMode.ORTHOGRAPHIC)
        comp.set_editor_property("ortho_width", float(ortho_w) * 100.0)
    else:
        comp.set_editor_property("projection_type", unreal.CameraProjectionMode.PERSPECTIVE)
        comp.set_editor_property("fov_angle", float(fov))
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
    # SceneCapture2D auto-exposure tak beradaptasi pasca-ganti cahaya (viewport basi);
    # untuk mood redup (keemasan) tambah bias EV supaya terlihat.
    if bias != 0.0:
        try:
            pps.set_editor_property("override_auto_exposure_bias", True)
            pps.set_editor_property("auto_exposure_bias", float(bias))
        except Exception as e:  # noqa: BLE001
            log(f"bias err {e}")
    comp.set_editor_property("post_process_settings", pps)
    for _ in range(8):
        comp.capture_scene()
    os.makedirs(RENDER, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(world, rt, RENDER.replace("\\", "/"), fname)
    raw = os.path.join(RENDER, fname)
    png = os.path.join(RENDER, fname + ".png")
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
    b = tot / n
    log(f"  render {fname}.png: kecerahan {b:.1f}/255")
    return b


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        fail("Editor sedang Play (PIE) -- hentikan dulu")
        return
    t0 = time.time()
    LES.load_level(MAP)
    log(f"level dimuat: {MAP}")
    # bersihkan kamera MK6 lama + sisa capture
    for a in list(EAS.get_all_level_actors()):
        lbl = a.get_actor_label()
        if lbl == "MK6_Capture" or (lbl.startswith("C") and len(lbl) >= 2 and lbl[1] == "_" and isinstance(a, unreal.CameraActor)):
            a.destroy_actor()
    light = find_light()
    results = []
    for k in KAM:
        cid = k["id"]
        cah = k["cahaya"]
        bias = 8.0 if cah == "keemasan" else 0.0   # keemasan redup, auto-exposure SceneCapture tak adaptasi
        set_cahaya(light, cah)
        x, y = k["pos"]
        if k.get("ortho"):
            base, tz, oh, mode = elev(x, y), elev(x, y), 0.0, "ortho"
            cam_z = base + 600.0   # 600 m di atas (ortho tak peduli tinggi, asal di atas semua)
            loc = unreal.Vector(x * 100.0, -y * 100.0, cam_z * 100.0)
            rot = unreal.Rotator()
            rot.set_editor_property("pitch", -90.0)
            rot.set_editor_property("yaw", 0.0)
            rot.set_editor_property("roll", 0.0)
            # CameraActor (acuan, orto)
            ca = EAS.spawn_actor_from_class(unreal.CameraActor, loc, rot)
            ca.set_actor_label(cid)
            ca.set_folder_path("KAMERA")
            cc = ca.get_editor_property("camera_component")
            cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
            cc.set_editor_property("ortho_width", float(k["lebar_ortho"]) * 100.0)
            b = render_shot(f"{cid}_{cah}", loc, rot, None, True, k["lebar_ortho"], bias)
            log(f"{cid}: ORTHO lebar {k['lebar_ortho']} m, pusat ({x},{y})")
            results.append((cid, b))
            continue
        h = float(k["tinggi_di_atas_tanah"])
        base, tz, oh, mode = cam_base(x, y)
        cam_z = base + h
        loc = unreal.Vector(x * 100.0, -y * 100.0, cam_z * 100.0)
        rot = look_rot(x, y, cam_z, k["lihat_ke"])
        # CameraActor (acuan)
        ca = EAS.spawn_actor_from_class(unreal.CameraActor, loc, rot)
        ca.set_actor_label(cid)
        ca.set_folder_path("KAMERA")
        cc = ca.get_editor_property("camera_component")
        cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.PERSPECTIVE)
        cc.set_editor_property("field_of_view", float(k["fov"]))
        b = render_shot(f"{cid}_{cah}", loc, rot, k["fov"], False, None, bias)
        log(f"{cid}: pos=({x},{y}) base={base:.2f} ({mode}, trace={tz:.2f} overhead={oh:.2f}) cam_z={cam_z:.2f} m, "
            f"lihat_ke={k['lihat_ke']} fov={k['fov']} -> kec={b:.1f}")
        results.append((cid, b))
    # kembalikan cahaya level ke siang (default) + simpan
    set_cahaya(light, "siang")
    LES.save_current_level()
    ok = all(b > 20.0 for _, b in results) and len(results) == 8 and not problems
    log(f"WAKTU MK6: {time.time() - t0:.1f} s")
    log(f"CEK MK6: {'LULUS' if ok else 'GAGAL'} ({len(results)} PNG, kec min={min(b for _, b in results):.1f})")
    if problems:
        for p in problems:
            unreal.log_warning("  - " + p)


main()
