"""Capture 4 render animasi in-editor untuk H6 di level Test_Hermes_Aksa2:
- idle: MM_Idle (t=0.0)
- lari: Jog/MF_Unarmed_Jog_Fwd (t=0.35)
- serang: Attack/MM_Attack_01 (t=0.30)
- lompat: Jump/MM_Jump (t=0.20)
Dijalankan via: python Tools/ue_remote.py Hermes/Tools/aksa2_75_capture_final_h6.py
"""
import os
import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_DIR = os.path.join(REPO, "Hermes", "Art", "aksa2", "Render", "h6")
os.makedirs(OUT_DIR, exist_ok=True)

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = UES.get_editor_world()

MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
AKSA_LAMA = "/Game/Jayadwara/Characters/Aksa/Mesh/SK_Aksa"
AKSA2 = "/Game/Hermes/Aksa2/SK_Aksa2"
ANIM_ROOT = "/Game/Characters/Mannequins/Anims/Unarmed/"

# Bersihkan aktor sementara
for a in EAS.get_all_level_actors():
    lab = a.get_actor_label()
    if lab.startswith("H6_") or lab.startswith("AKCHK_") or lab.startswith("TEST_"):
        EAS.destroy_actor(a)

POSES = [
    ("ue_h6_idle", "MM_Idle", 0.0),
    ("ue_h6_lari", "Jog/MF_Unarmed_Jog_Fwd", 0.35),
    ("ue_h6_serang", "Attack/MM_Attack_01", 0.30),
    ("ue_h6_lompat", "Jump/MM_Jump", 0.20),
]

for label, anim_rel, t_pos in POSES:
    print(f"\n=== CAPTURING {label}: {anim_rel} (t={t_pos}) ===")
    anim_obj = EAL.load_asset(f"{ANIM_ROOT}{anim_rel}")
    
    # 3 karakter berdampingan menghadap kamera (+X):
    # Aksa 2 di Y = +100 (kiri kamera), Aksa Lama di Y = 0 (tengah), Manny di Y = -100 (kanan kamera)
    items = [
        ("Aksa2", AKSA2, unreal.Vector(0, 100, 0)),
        ("AksaLama", AKSA_LAMA, unreal.Vector(0, 0, 0)),
        ("Manny", MANNY, unreal.Vector(0, -100, 0)),
    ]
    
    spawned = []
    for name, mesh_path, loc in items:
        mesh = EAL.load_asset(mesh_path)
        a = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
        a.set_actor_label(f"H6_{label}_{name}")
        c = a.skeletal_mesh_component
        c.set_skinned_asset_and_update(mesh)
        c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        c.set_animation(anim_obj)
        if hasattr(c, "override_animation_data"):
            c.override_animation_data(anim_obj, False, True, t_pos, 0.0)
        c.set_position(t_pos, False)
        for fn in ("tick_animation", "refresh_bone_transforms"):
            if hasattr(c, fn):
                getattr(c, fn)(*((0.0, False) if fn == "tick_animation" else ()))
        spawned.append(a)
    
    # Kamera di X = 380, Y = 0, Z = 105; memandang ke arah -X (Yaw = 180, Pitch = -2.0)
    cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(380, 0, 105), unreal.Rotator(roll=0.0, pitch=-2.0, yaw=180.0))
    cap.set_actor_label(f"H6_cam_{label}")
    cc = cap.capture_component2d
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
    cc.set_editor_property("texture_target", rt)
    cc.set_editor_property("fov_angle", 42.0)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
    
    cc.capture_scene()
    
    out_png = f"{label}.png"
    unreal.RenderingLibrary.export_render_target(world, rt, OUT_DIR, out_png)
    print(f"Screenshot tersimpan -> {os.path.join(OUT_DIR, out_png)}")
    
    for a in spawned:
        EAS.destroy_actor(a)
    EAS.destroy_actor(cap)

print("\n=== SEMUA 4 SCREENSHOT BERHASIL DIAMBIL & DISIMPAN ===")
