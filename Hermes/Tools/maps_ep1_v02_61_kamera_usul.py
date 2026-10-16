"""V6 (tambahan) — render USULAN kamera C1/C3/C7/C8 (bukan bagian dari 8 render V6).

Empat kamera V6 belum menampilkan sasaran tabel panduan karena data kamera di
`Art/Level/ep01_layout_v02.json` (READ-ONLY) menaruh kamera terlalu dekat / salah arah:
  C1 rumah desa di belakang kamera (kamera di dalam desa, menghadap bukit)
  C3 pilar gerbang 3,5 m dari kamera menutup ~40% frame -> truk derek (61 m) terhalang
  C7 baris kantor/gudang/truk di luar FOV (kamera 320,-20 menghadap (0,0))
  C8 baris pilar memanjang barat-laut -> tenggara, kamera menghadap barat (tegak lurus baris)

Skrip ini TIDAK mengubah data desain; hanya membuktikan usulan angka di laporan bisa
menampilkan sasaran. Hasil -> `Hermes/Art/maps_ep1/v02/Render/usulan/<id>.png`.

Pakai: python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_61_kamera_usul.py
"""
import os
import sys
import math

import unreal

DEST = "/Game/Hermes/MapsEp1"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp1_v02"
LEVEL_NAME = "Test_Hermes_MapsEp1_v02"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
from ep01_medan_v02 import elev  # noqa: E402

# usulan: (id, pos, tinggi_di_atas_tanah, lihat_ke, fov, cahaya, alasan singkat)
USUL = [
    ("C1u_START_Desa", (-150, -450), 2.0, (-250, -100, 30), 70, "sore",
     "mundur ke tepi tenggara desa + arah 106 deg: rumah desa (D5/D6/D8) di kiri, bukit+candi di kanan"),
    ("C3u_GerbangKeTimur", (0, 205), 1.6, (250, 100, 28), 70, "sore",
     "geser 25 m ke utara gerbang supaya pilar gerbang tak lagi mengiris frame; truk derek 61 m + base camp terlihat"),
    ("C7u_BaseCamp", (330, -10), 1.6, (60, 30, 15), 70, "sore",
     "arah 170 deg (bukan 176): baris Kantor1-3 + Gudang + Truk1-3 masuk FOV, galian tetap di belakang"),
    ("C8u_PilarTolRaksasa", (760, -250), 42.0, (560, 96, 35), 70, "senja",
     "pindah ke ujung tenggara baris pilar, hadap 114 deg (sejajar baris): Pilar1-8 + Gelagar1-2 + bukit candi"),
]
CAHAYA = {
    "sore": {"pitch": -25, "yaw": 0, "warna": (1.0, 0.95, 0.88), "intensitas_lux": 8.0},
    "senja": {"pitch": -3, "yaw": 0, "warna": (1.0, 0.45, 0.3), "intensitas_lux": 2.0},
}
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
problems = []


def log(m):
    unreal.log(f"[V6u] {m}")


def ue(x, y, z):
    return unreal.Vector(x * 100.0, -y * 100.0, z * 100.0)


def set_cahaya(nama):
    cfg = CAHAYA[nama]
    ds = [a for a in EAS.get_all_level_actors() if isinstance(a, unreal.DirectionalLight)]
    if not ds:
        unreal.log_error("[V6u] DirectionalLight tidak ada")
        return
    dl = ds[0]
    dl.set_actor_rotation(unreal.Rotator(pitch=cfg["pitch"], yaw=cfg["yaw"], roll=0.0), False)
    c = dl.light_component
    w = cfg["warna"]
    c.set_light_color(unreal.LinearColor(r=w[0], g=w[1], b=w[2], a=1.0))
    c.set_editor_property("intensity", cfg["intensitas_lux"])


def render(cid, loc, rot, fov):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080,
                                                        unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, loc, rot)
    c = cap.capture_component2d
    c.set_editor_property("texture_target", rt)
    c.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    c.set_editor_property("fov_angle", float(fov))
    pps = c.get_editor_property("post_process_settings")
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
    c.set_editor_property("post_process_settings", pps)
    for _ in range(8):
        c.capture_scene()
    out = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Render", "usulan")
    os.makedirs(out, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(world, rt, out.replace("\\", "/"), cid)
    p = os.path.join(out, cid)
    if os.path.exists(p):
        os.replace(p, p + ".png")
    px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 960, 540)
    log(f"{cid}.png tengah=({px.r},{px.g},{px.b})")
    EAS.destroy_actor(cap)


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    nama = world.get_name() if world else None
    if nama != LEVEL_NAME:
        LES.load_level(MAP)
        log(f"level dimuat: {MAP} (kalau gelap, jalankan sekali lagi)")
    else:
        log(f"level sudah terbuka: {nama}")
    for a in list(EAS.get_all_level_actors()):
        if a.get_actor_label().startswith(("C1u_", "C3u_", "C7u_", "C8u_")):
            a.destroy_actor()
    for cid, (x, y), tg, lk, fov, cah, alasan in USUL:
        set_cahaya(cah)
        z = elev(x, y) + float(tg)
        P = ue(x, y, z)
        T = ue(lk[0], lk[1], lk[2])
        d = T - P
        yaw = math.degrees(math.atan2(d.y, d.x))
        pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
        rot = unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0)
        log(f"{cid}: loc=({P.x:.0f},{P.y:.0f},{P.z:.0f}) yaw={yaw:.1f} pitch={pitch:.1f} | {alasan}")
        render(cid, P, rot, fov)
    LES.save_current_level()
    out = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "v02", "Render", "usulan")
    n = len([f for f in os.listdir(out) if f.endswith(".png")])
    log(f"PNG usulan = {n}/{len(USUL)}")
    log(f"CEK V6-usulan: {'LULUS' if n == len(USUL) else 'GAGAL'}")


main()
