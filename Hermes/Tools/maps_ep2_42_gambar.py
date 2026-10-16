"""MK4c — 6 screenshot bukti MK4 (Unreal Editor Python, via Tools/ue_remote.py).

Render 1920x1080 dengan SceneCapture2D dari 6 sudut yang diminta MK4 (setinggi mata 1,7 m
kecuali disebut):
  1 MK4c_1_gang      mulut gang utama (sudut kamera C1) — jembatan gantung di ujungnya
  2 MK4c_2_atap      di atas atap T1 menuju T3 (deret atap oranye + papan di atas gang)
  3 MK4c_3_jembatan  jembatan gantung kuning dari bantaran
  4 MK4c_4_gudang    gudang Adikara dari dermaga
  5 MK4c_5_layang    jalan layang dari jalan raya
  6 MK4c_6_45m       tampak 45 m dari JAYADWARA_Mulai ke kampung

Tinggi kamera = permukaan pertama dari line trace ke bawah (jadi di atap pun benar).
Juga menyalakan `stat RHI` di viewport dan mencatat jumlah draw call + rata-rata kecerahan tiap PNG.
Tidak menyimpan level (murni render).

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep2_42_gambar.py
"""
import os
import sys
import math
import time

import unreal

DEST = "/Game/Hermes/MapsEp2"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp2"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RENDER = os.path.join(REPO, "Hermes", "Art", "maps_ep2", "Render")

sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# nama, (cam_x, cam_y) meter, tinggi mata/titik (m), (target_x, target_y, target_z) meter, fov, mode tinggi
#   mode "trace"  = tinggi di atas permukaan pertama dari trace ke bawah (benar untuk di atap)
#   mode "tanah"  = tinggi di atas elevasi medan (untuk di bawah dek jalan layang)
SHOTS = [
    ("MK4c_1_gang", (-26.0, 140.0), 1.6, (-26.0, -40.0, 4.5), 70.0, "tanah"),
    ("MK4c_2_atap", (-170.0, 98.0), 1.7, (117.0, 26.0, 10.0), 75.0, "trace"),
    ("MK4c_3_jembatan", (-105.0, -72.0), 1.7, (-105.0, -108.0, 6.5), 70.0, "trace"),
    ("MK4c_4_gudang", (485.0, -68.0), 1.7, (600.0, 100.0, 10.0), 70.0, "trace"),
    ("MK4c_5_layang", (-300.0, 139.0), 1.7, (350.0, 155.0, 23.5), 70.0, "tanah"),
    ("MK4c_6_45m", (-380.0, -105.0), 45.0, (525.0, 60.0, 6.0), 70.0, "trace"),
]

problems = []


def log(m):
    unreal.log(f"[MK4c] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[MK4c] {m}")


def ue(x, y, z):
    return unreal.Vector(x * 100.0, -y * 100.0, z * 100.0)


def z_atas(x, y):
    """Elevasi permukaan pertama dari line trace vertikal ke bawah (meter)."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    res = unreal.SystemLibrary.line_trace_single(
        world, ue(x, y, 600.0), ue(x, y, -200.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if res is None:
        return M.elev(x, y)
    tup = res.to_tuple()
    loc = tup[4]
    return (loc.z if loc is not None else M.elev(x, y) * 100.0) / 100.0


def render(nama, cam, tinggi, tgt, fov, mode):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    dasar = z_atas(cam[0], cam[1]) if mode == "trace" else M.elev(cam[0], cam[1])
    cz = dasar + tinggi
    P = ue(cam[0], cam[1], cz)
    T = ue(tgt[0], tgt[1], tgt[2])
    d = T - P
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, P,
                                     unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0))
    cap.set_actor_label("MK4_Capture")
    comp = cap.capture_component2d
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    comp.set_editor_property("fov_angle", fov)
    pps = comp.get_editor_property("post_process_settings")
    for key, val in (("override_auto_exposure_method", True),
                     ("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM),
                     ("override_auto_exposure_speed_up", True), ("auto_exposure_speed_up", 200.0),
                     ("override_auto_exposure_speed_down", True), ("auto_exposure_speed_down", 200.0),
                     ("override_auto_exposure_min_brightness", True), ("auto_exposure_min_brightness", -20.0),
                     ("override_auto_exposure_max_brightness", True), ("auto_exposure_max_brightness", 40.0)):
        try:
            pps.set_editor_property(key, val)
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
    # kecerahan: rata-rata 6x4 piksel
    tot = 0.0
    n = 0
    for i in range(6):
        for j in range(4):
            px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, int(1920 * (i + 0.5) / 6), int(1080 * (j + 0.5) / 4))
            tot += (px.r + px.g + px.b) / 3.0
            n += 1
    terang = tot / n
    EAS.destroy_actor(cap)
    unreal.RenderingLibrary.release_render_target2d(rt)
    log(f"{nama}: cam=({cam[0]:.0f},{cam[1]:.0f}) z={cz:.1f} m -> tgt=({tgt[0]:.0f},{tgt[1]:.0f},{tgt[2]:.0f}) "
        f"fov={fov:.0f} ; kecerahan rata-rata = {terang:.1f}/255 ; {png}")
    if terang <= 20.0:
        fail(f"{nama}: kecerahan {terang:.1f} <= 20/255")
    return terang


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[MK4c] Editor sedang Play (PIE) — hentikan dulu lalu jalankan ulang")
        return
    t0 = time.time()
    if not EAL.does_asset_exist(MAP):
        fail(f"level {MAP} tidak ada")
        return
    LES.load_level(MAP)
    log(f"level dimuat: {MAP}")
    for a in list(EAS.get_all_level_actors()):
        if a.get_actor_label() == "MK4_Capture":
            a.destroy_actor()

    # stat RHI di viewport (jumlah draw call dicatat di laporan)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    try:
        unreal.AutomationLibrary.enable_stat_group(world, "RHI")
        log("stat RHI dinyalakan di viewport (enable_stat_group)")
    except Exception as e:  # noqa: BLE001
        log(f"enable_stat_group(world,'RHI') err: {e}")
    try:
        unreal.SystemLibrary.execute_console_command(world, "stat RHI")
    except Exception as e:  # noqa: BLE001
        log(f"execute_console_command(stat RHI) err: {e}")

    terang = []
    for nama, cam, tinggi, tgt, fov, mode in SHOTS:
        terang.append(render(nama, cam, tinggi, tgt, fov, mode))

    # setelah beberapa frame dirender, baru baca stat
    draw = None
    for nm in ("Draw Calls", "DrawCalls", "RHI.DrawCalls", "DrawPrimitiveCalls",
               "RHI.DrawPrimitiveCalls", "MeshDrawCalls", "BasePassDrawCalls"):
        try:
            v = unreal.AutomationLibrary.get_stat_call_count(nm)
            if isinstance(v, (int, float)) and v > 0:
                log(f"stat '{nm}': call count = {v}")
                if draw is None:
                    draw = v
        except Exception as e:  # noqa: BLE001
            log(f"stat '{nm}' err {type(e).__name__}: {e}")
    for nm in ("Draw Calls", "DrawCalls", "DrawPrimitiveCalls"):
        for fn in ("get_stat_exc_average", "get_stat_inc_average"):
            try:
                v = getattr(unreal.AutomationLibrary, fn)(nm)
                log(f"{fn}('{nm}') = {v}")
            except Exception:  # noqa: BLE001
                pass

    dt = time.time() - t0
    # proxy draw call: jumlah komponen mesh berisi mesh (StaticMeshActor + tiap ISM)
    proxy = 0
    for a in EAS.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.get_editor_property("static_mesh") is not None:
                proxy += 1
    log(f"proxy draw call (jumlah komponen mesh berisi mesh) = {proxy}")
    log(f"WAKTU skrip MK4c: {dt:.1f} s ; draw call dari stat = {draw}")
    log(f"kecerahan min = {min(terang):.1f}/255 (harus > 20)")
    log(f"CEK MK4c: 6 png = {len(terang)} ; kecerahan>20 = {all(t > 20.0 for t in terang)} -> "
        f"{'LULUS' if len(terang) == 6 and all(t > 20.0 for t in terang) and not problems else 'GAGAL'}")
    if problems:
        for p in problems:
            unreal.log_warning("[MK4c] masalah: " + p)


main()
