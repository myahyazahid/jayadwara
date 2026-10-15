"""Capture render in-editor untuk H6 di level Test_Hermes_Aksa2.
Dijalankan via: python Tools/ue_remote.py Hermes/Tools/aksa2_72_capture_anim.py
"""
import os
import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_DIR = os.path.join(REPO, "Hermes", "Art", "aksa2", "Render", "h6")
os.makedirs(OUT_DIR, exist_ok=True)

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
AKSA_LAMA = "/Game/Jayadwara/Characters/Aksa/Mesh/SK_Aksa"
AKSA2 = "/Game/Hermes/Aksa2/SK_Aksa2"
ANIM_ROOT = "/Game/Characters/Mannequins/Anims/Unarmed/"

# Pastikan level yang terbuka adalah level sandbox
world = UES.get_editor_world()
world_path = world.get_path_name()
print("World aktif:", world_path)
if "Test_Hermes_Aksa2" not in world_path:
    print("Membuka level sandbox Test_Hermes_Aksa2...")
    unreal.EditorLevelLibrary.load_level("/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2")
    world = UES.get_editor_world()

# Bersihkan aktor lama
for a in EAS.get_all_level_actors():
    lab = a.get_actor_label()
    if lab.startswith("H6_"):
        EAS.destroy_actor(a)

POSES = [
    # (label, anim_path, time_pos, camera_loc, camera_rot, fov)
    ("ue_h6_idle", "MM_Idle", 0.0, unreal.Vector(450, 0, 10095), unreal.Rotator(0, 0, 180), 45.0),
    ("ue_h6_lari", "Jog/MF_Unarmed_Jog_Fwd", 0.35, unreal.Vector(450, 0, 10095), unreal.Rotator(0, 0, 180), 45.0),
    ("ue_h6_serang", "Attack/MM_Attack_01", 0.30, unreal.Vector(450, 0, 10095), unreal.Rotator(0, 0, 180), 45.0),
    ("ue_h6_lompat", "Jump/MM_Jump", 0.20, unreal.Vector(450, 0, 10095), unreal.Rotator(0, 0, 180), 45.0),
]

BASE_Z = 10000.0

for label, anim_rel, t_pos, cam_loc, cam_rot, fov in POSES:
    print(f"\n=== MENGAMBIL SCREENSHOT: {label} (anim: {anim_rel}, t={t_pos}) ===")
    anim_obj = EAL.load_asset(f"{ANIM_ROOT}{anim_rel}")
    assert anim_obj is not None, f"Animasi {anim_rel} tidak ditemukan"
    
    actors = []
    # 3 karakter berdampingan: Manny (Y=-110), Aksa Lama (Y=0), Aksa2 Baru (Y=+110)
    items = [
        ("Manny", MANNY, unreal.Vector(0, -110, BASE_Z)),
        ("AksaLama", AKSA_LAMA, unreal.Vector(0, 0, BASE_Z)),
        ("Aksa2", AKSA2, unreal.Vector(0, 110, BASE_Z)),
    ]
    
    for name, mesh_path, loc in items:
        mesh = EAL.load_asset(mesh_path)
        if not mesh:
            print(f"Peringatan: Mesh {mesh_path} tidak ditemukan")
            continue
        act = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, unreal.Rotator(0, 0, -90))
        act.set_actor_label(f"H6_{label}_{name}")
        c = act.skeletal_mesh_component
        c.set_skeletal_mesh_asset(mesh)
        c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        c.set_animation(anim_obj)
        if hasattr(c, "override_animation_data"):
            c.override_animation_data(anim_obj, False, True, t_pos, 0.0)
        c.set_position(t_pos, False)
        for fn in ("tick_animation", "refresh_bone_transforms"):
            if hasattr(c, fn):
                getattr(c, fn)(*((0.0, False) if fn == "tick_animation" else ()))
        actors.append(act)
    
    # Spawn SceneCapture2D
    cap_act = EAS.spawn_actor_from_class(unreal.SceneCapture2D, cam_loc, cam_rot)
    cap_act.set_actor_label(f"H6_cam_{label}")
    cc = cap_act.capture_component2d
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
    cc.set_editor_property("texture_target", rt)
    cc.set_editor_property("fov_angle", fov)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
    
    # Tangkap scene
    cc.capture_scene()
    
    # Ekspor ke file PNG
    out_file = f"{label}.png"
    unreal.RenderingLibrary.export_render_target(world, rt, OUT_DIR, out_file)
    print(f"Screenshot disimpan -> {os.path.join(OUT_DIR, out_file)}")
    
    # Bersihkan aktor untuk pose ini
    for act in actors:
        EAS.destroy_actor(act)
    EAS.destroy_actor(cap_act)

# Tangkap juga close-up solo Aksa2 saat serang (sudut 3/4 dinamis)
print("\n=== MENGAMBIL SCREENSHOT SOLO 3/4: ue_h6_aksa2_action_close ===")
act_solo = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, BASE_Z), unreal.Rotator(0, 0, -90))
act_solo.set_actor_label("H6_solo_Aksa2")
c_solo = act_solo.skeletal_mesh_component
c_solo.set_skeletal_mesh_asset(EAL.load_asset(AKSA2))
c_solo.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
anim_atk = EAL.load_asset(f"{ANIM_ROOT}Attack/MM_Attack_02")
c_solo.set_animation(anim_atk)
if hasattr(c_solo, "override_animation_data"):
    c_solo.override_animation_data(anim_atk, False, True, 0.25, 0.0)
c_solo.set_position(0.25, False)
for fn in ("tick_animation", "refresh_bone_transforms"):
    if hasattr(c_solo, fn):
        getattr(c_solo, fn)(*((0.0, False) if fn == "tick_animation" else ()))

cap_solo = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(250, 120, BASE_Z + 110), unreal.Rotator(0, -10, -155))
cap_solo.set_actor_label("H6_cam_solo")
cc_solo = cap_solo.capture_component2d
rt_solo = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc_solo.set_editor_property("texture_target", rt_solo)
cc_solo.set_editor_property("fov_angle", 40.0)
cc_solo.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc_solo.capture_scene()

out_solo = "ue_h6_aksa2_solo_attack.png"
unreal.RenderingLibrary.export_render_target(world, rt_solo, OUT_DIR, out_solo)
print(f"Screenshot solo disimpan -> {os.path.join(OUT_DIR, out_solo)}")

EAS.destroy_actor(act_solo)
EAS.destroy_actor(cap_solo)

print("\n=== SEMUA SCREENSHOT IN-EDITOR BERHASIL DIAMBIL ===")
