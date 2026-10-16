"""Tuyul K6 — tangkap render di level Test_Hermes_Tuyul (rasa skala + animasi Manny) & taruh aktor permanen.
Dijalankan: python Tools/ue_remote.py Hermes/Tools/tuyul_62_ue_capture.py

Catatan penting: menerapkan animasi Manny (single node) ke mesh Tuyul x27/x45 membuat tulang
mengikuti skala kerangka Manny sehingga mesh mengecil — jadi shot SKALA memakai ref pose (tanpa
anim), dan animasi Manny hanya dipakai untuk shot mesh x1.
"""
import json
import math
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EXPORT = os.path.join(REPO, "Hermes", "Art", "tuyul", "Export")
OUT_DIR = os.path.join(REPO, "Hermes", "Art", "tuyul", "Render", "k6")
os.makedirs(OUT_DIR, exist_ok=True)

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

LEVEL = "/Game/Hermes/Tuyul/Maps/Test_Hermes_Tuyul"
J2 = "/Game/Jayadwara/Characters/Jayadwara2/Mesh/SK_Jayadwara2"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
MESH = {
    "Tuyul1": "/Game/Hermes/Tuyul/Mesh/SK_Tuyul",
    "Tuyul27": "/Game/Hermes/Tuyul/Mesh/SK_TuyulBesar",
    "Tuyul45": "/Game/Hermes/Tuyul/Mesh/SK_TuyulRaksasa",
}
# tinggi menurut kartu (cm), dipakai untuk penempatan & framing kamera
H = {"Tuyul1": 100.0, "Tuyul27": 2700.0, "Tuyul45": 4500.0, "Jayadwara2": 4713.0, "Manny": 180.0}
SOCK_JSON = {"Tuyul1": "SK_Tuyul_sockets.json", "Tuyul27": "SK_TuyulBesar_sockets.json",
             "Tuyul45": "SK_TuyulRaksasa_sockets.json"}
ANIM_ROOT = "/Game/Characters/Mannequins/Anims/Unarmed/"
# anim Manny langsung (untuk mesh Manny) + anim hasil retarget IK (untuk mesh Tuyul x1)
ANIM_JOG_MANNY = f"{ANIM_ROOT}Jog/MF_Unarmed_Jog_Fwd"
ANIM_IDLE_MANNY = f"{ANIM_ROOT}MM_Idle"
ANIM_JOG_TUYUL = "/Game/Hermes/Tuyul/Anims/MF_Unarmed_Jog_Fwd_Tuyul"
ANIM_IDLE_TUYUL = "/Game/Hermes/Tuyul/Anims/MM_Idle_Tuyul"

world = UES.get_editor_world()
print("World aktif:", world.get_path_name())
if "Test_Hermes_Tuyul" not in world.get_path_name():
    print("Membuka level sandbox Test_Hermes_Tuyul...")
    unreal.EditorLevelLibrary.load_level(LEVEL)
    world = UES.get_editor_world()


def cleanup(prefix="K6_"):
    for a in EAS.get_all_level_actors():
        if a.get_actor_label().startswith(prefix):
            EAS.destroy_actor(a)


def spawn(label, mesh_path, y, anim=None, t=0.0, z=0.0):
    mesh = EAL.load_asset(mesh_path)
    assert mesh is not None, f"mesh tidak ada: {mesh_path}"
    a = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0.0, y, z),
                                   unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
    a.set_actor_label(label)
    c = a.skeletal_mesh_component
    c.set_skinned_asset_and_update(mesh)
    if anim is not None:
        c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        c.set_animation(anim)
        if hasattr(c, "override_animation_data"):
            c.override_animation_data(anim, False, True, t, 0.0)
        c.set_position(t, False)
    for fn, args in (("tick_animation", (0.0, False)), ("refresh_bone_transforms", ())):
        if hasattr(c, fn):
            getattr(c, fn)(*args)
    print(f"    + {label} @ y={y:.0f} (mesh={mesh.get_name()})")
    return a


def capture(label, items, fov=45.0, margin=1.05):
    """items = [(y, tinggi_cm), ...]; kamera mundur sampai semua masuk frame."""
    ys = [y for y, _ in items]
    hs = [h for _, h in items]
    ymin, ymax, zmax = min(ys), max(ys), max(hs)
    cy, cz = (ymin + ymax) / 2.0, zmax / 2.0
    hfov = math.radians(fov)
    vfov = 2 * math.atan(math.tan(hfov / 2) * 1080 / 1920)
    dx = max(((ymax - ymin) + 150.0) / 2 / math.tan(hfov / 2),
             (zmax / 2) / math.tan(vfov / 2)) * margin
    cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(dx, cy, cz),
                                     unreal.Rotator(0.0, -2.0, 180.0))
    cap.set_actor_label(f"K6_cam_{label}")
    cc = cap.capture_component2d
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080,
                                                        unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
    cc.set_editor_property("texture_target", rt)
    cc.set_editor_property("fov_angle", fov)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
    cc.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt, OUT_DIR, f"{label}.png")
    print(f"  simpan {label}.png (kamera x={dx:.0f} y={cy:.0f} z={cz:.0f})")
    EAS.destroy_actor(cap)


# ---------- 1) diagnostik ----------
print("=== BOUNDS & SOCKET ===")
for nm, path in MESH.items():
    m = EAL.load_asset(path)
    want = json.load(open(os.path.join(EXPORT, SOCK_JSON[nm]), encoding="utf-8"))["sockets"]
    found = sum(1 for s in want if m.find_socket(s["name"]) is not None)
    print(f"  {nm}: tinggi aset~{2 * m.get_bounds().box_extent.z:.1f} cm, socket {found}/{len(want)}")
for nm, path in (("Jayadwara2", J2), ("Manny", MANNY)):
    m = EAL.load_asset(path)
    if m:
        print(f"  {nm}: tinggi aset~{2 * m.get_bounds().box_extent.z:.1f} cm")

jog_manny = EAL.load_asset(ANIM_JOG_MANNY)
jog_tuyul = EAL.load_asset(ANIM_JOG_TUYUL)
assert jog_tuyul is not None, "anim retarget Tuyul belum ada - jalankan tuyul_63_retarget.py dulu"


def pose_at(seq, t, bone):
    """posisi tulang (cm, ruang dunia) pada waktu t dari animasi (bukti frame berbeda)."""
    pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, unreal.AnimPoseEvaluationOptions())
    return unreal.AnimPoseExtensions.get_bone_pose(pose, bone, unreal.AnimPoseSpaces.WORLD).translation

# ---------- 2) skala: Tuyul x1 vs Manny (180cm) ----------
print("=== SHOT: skala_human ===")
cleanup()
spawn("K6_h_T1", MESH["Tuyul1"], 0.0)
spawn("K6_h_Manny", MANNY, 250.0)
capture("ue_k6_skala_human", [(0.0, H["Tuyul1"]), (250.0, H["Manny"])], fov=45.0)
cleanup()

# ---------- 3) skala: barisan semua (ref pose) ----------
print("=== SHOT: skala_semua ===")
cleanup()
spawn("K6_s_T1", MESH["Tuyul1"], 0.0)
spawn("K6_s_T27", MESH["Tuyul27"], 3000.0)
spawn("K6_s_T45", MESH["Tuyul45"], 12000.0)
spawn("K6_s_J2", J2, 21000.0)
capture("ue_k6_skala_semua",
        [(0.0, H["Tuyul1"]), (3000.0, H["Tuyul27"]), (12000.0, H["Tuyul45"]), (21000.0, H["Jayadwara2"])],
        fov=45.0)
cleanup()

# ---------- 4) pasangan: skala besar vs Jayadwara2 ----------
for label, key, gap in (("ue_k6_skala_besar", "Tuyul27", 5200.0),
                        ("ue_k6_skala_raksasa", "Tuyul45", 8000.0)):
    print(f"=== SHOT: {label} ===")
    cleanup()
    spawn(f"K6_{key}_A", MESH[key], 0.0)
    spawn(f"K6_{key}_J2", J2, gap)
    capture(label, [(0.0, H[key]), (gap, H["Jayadwara2"])], fov=45.0)
    cleanup()

# ---------- 5) animasi: 2 frame berbeda (Tuyul x1 pakai anim retarget, Manny pakai anim asli) ----------
for label, t in (("ue_k6_anim_a", 0.10), ("ue_k6_anim_b", 0.45)):
    print(f"=== SHOT: {label} (t={t}) ===")
    cleanup()
    spawn("K6_anim_T1", MESH["Tuyul1"], 0.0, anim=jog_tuyul, t=t)
    spawn("K6_anim_Manny", MANNY, 220.0, anim=jog_manny, t=t)
    capture(label, [(0.0, 200.0), (220.0, H["Manny"])], fov=45.0)
cleanup()

# bukti angka: posisi telapak pada kedua waktu harus berbeda (bukan frame identik)
print("=== BUKTI FRAME BERBEDA (anim retarget Tuyul) ===")
for t in (0.10, 0.45):
    fl, fr, p = pose_at(jog_tuyul, t, "foot_l"), pose_at(jog_tuyul, t, "foot_r"), pose_at(jog_tuyul, t, "pelvis")
    print(f"  t={t}: foot_l=({fl.x:.1f},{fl.y:.1f},{fl.z:.1f}) foot_r=({fr.x:.1f},{fr.y:.1f},{fr.z:.1f}) pelvis z={p.z:.1f} cm")

# ---------- 6) aktor permanen di level (untuk developer) ----------
print("=== TARUH AKTOR PERMANEN ===")
cleanup("Tuyul_K6_")
spawn("Tuyul_K6_Jayadwara2", J2, 21000.0)
spawn("Tuyul_K6_TuyulRaksasa", MESH["Tuyul45"], 12000.0)
spawn("Tuyul_K6_TuyulBesar", MESH["Tuyul27"], 3000.0)
spawn("Tuyul_K6_Tuyul", MESH["Tuyul1"], 0.0)
unreal.EditorLevelLibrary.save_current_level()
print("  level disimpan dengan 4 aktor Tuyul_K6_*")

print("=== CAPTURE K6 SELESAI ===")
