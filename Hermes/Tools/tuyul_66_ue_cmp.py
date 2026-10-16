"""Tuyul K6b — sandingkan TuyulBesar(27m) + TuyulRaksasa(45m) + Jayadwara2(47m)
jadi berdampingan & terpusat di level sandbox Test_Hermes_Tuyul, lalu render.
Dijalankan: python Tools/ue_remote.py Hermes/Tools/tuyul_66_ue_cmp.py
"""
import math
import os

import unreal

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
RL = unreal.RenderingLibrary
LEVEL = "/Game/Hermes/Tuyul/Maps/Test_Hermes_Tuyul"

world = UES.get_editor_world()
if "Test_Hermes_Tuyul" not in world.get_path_name():
    print("Membuka level sandbox...")
    unreal.EditorLevelLibrary.load_level(LEVEL)
    world = UES.get_editor_world()
print("World aktif:", world.get_path_name())

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_DIR = os.path.join(REPO, "Hermes", "Art", "tuyul", "Render", "k6")
os.makedirs(OUT_DIR, exist_ok=True)

PATHS = {
    "Tuyul_K6_TuyulBesar":   "/Game/Hermes/Tuyul/Mesh/SK_TuyulBesar",
    "Tuyul_K6_TuyulRaksasa": "/Game/Hermes/Tuyul/Mesh/SK_TuyulRaksasa",
    "Tuyul_K6_Jayadwara2":   "/Game/Jayadwara/Characters/Jayadwara2/Mesh/SK_Jayadwara2",
}
ORDER = ["Tuyul_K6_TuyulBesar", "Tuyul_K6_TuyulRaksasa", "Tuyul_K6_Jayadwara2"]

# ukuran aset (bounds)
H, HALF = {}, {}
for lbl, p in PATHS.items():
    m = EAL.load_asset(p)
    b = m.get_bounds().box_extent
    H[lbl] = 2 * b.z
    HALF[lbl] = max(b.x, b.y)
    print(f"  {lbl}: tinggi={H[lbl]:.0f} cm  halfwidth={HALF[lbl]:.0f} cm")

# spacing center-to-center: rapat, tidak overlap (gap edge ~800 cm)
SP = max(HALF.values()) * 2 + 800.0
print(f"  spacing center={SP:.0f} cm")

# pindahkan 3 aktor jadi berdampingan terpusat di y=0
NEW = {ORDER[i]: (0.0, (i - 1) * SP, 0.0) for i in range(3)}
moved = {}
for a in EAS.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl in NEW:
        x, y, z = NEW[lbl]
        a.set_actor_location(unreal.Vector(x, y, z), False, False)
        a.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0), False)
        moved[lbl] = (y, H[lbl])
        print(f"  moved {lbl} -> y={y:.0f}")
assert len(moved) == 3, f"Aktor kurang: {list(moved)}"

# render side-by-side (mirror logic capture() tuyul_62)
items = [moved[k] for k in ORDER]
ys = [y for y, _ in items]
ymin, ymax, zmax = min(ys), max(ys), max(h for _, h in items)
cy, cz = (ymin + ymax) / 2.0, zmax / 2.0
fov, margin = 40.0, 1.12
hfov = math.radians(fov)
vfov = 2 * math.atan(math.tan(hfov / 2) * 1080 / 1920)
dx = max(((ymax - ymin) + 300.0) / 2 / math.tan(hfov / 2),
         (zmax / 2) / math.tan(vfov / 2)) * margin
cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(dx, cy, cz),
                                 unreal.Rotator(0.0, -2.0, 180.0))
cap.set_actor_label("K6_cam_cmp")
cc = cap.capture_component2d
rt = RL.create_render_target2d(world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc.set_editor_property("texture_target", rt)
cc.set_editor_property("fov_angle", fov)
cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc.capture_scene()
RL.export_render_target(world, rt, OUT_DIR, "ue_k6_cmp_sidebyside.png")
print(f"  render: {os.path.join(OUT_DIR, 'ue_k6_cmp_sidebyside.png')}")
EAS.destroy_actor(cap)

unreal.EditorLevelLibrary.save_current_level()
print("  level sandbox disimpan (3 aktor berdampingan)")
print("=== DONE ===")
