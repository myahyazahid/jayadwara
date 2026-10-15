"""Capture 4 animasi in-editor di level Test_Hermes_Aksa2 menggunakan HighResShot:
- idle (MM_Idle, t=0.0)
- lari (Jog/MF_Unarmed_Jog_Fwd, t=0.35)
- serang (Attack/MM_Attack_01, t=0.30)
- lompat (Jump/MM_Jump, t=0.20)
"""
import os
import time
import unreal

proj_dir = unreal.SystemLibrary.get_project_directory()
saved_shots = os.path.join(proj_dir, "Saved", "Screenshots")
os.makedirs(saved_shots, exist_ok=True)

out_dir = os.path.join(proj_dir, "Hermes", "Art", "aksa2", "Render", "h6")
os.makedirs(out_dir, exist_ok=True)

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAL = unreal.EditorAssetLibrary

MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
AKSA_LAMA = "/Game/Jayadwara/Characters/Aksa/Mesh/SK_Aksa"
AKSA2 = "/Game/Hermes/Aksa2/SK_Aksa2"
ANIM_ROOT = "/Game/Characters/Mannequins/Anims/Unarmed/"

BASE_Z = 10000.0

POSES = [
    ("ue_h6_idle", "MM_Idle", 0.0),
    ("ue_h6_lari", "Jog/MF_Unarmed_Jog_Fwd", 0.35),
    ("ue_h6_serang", "Attack/MM_Attack_01", 0.30),
    ("ue_h6_lompat", "Jump/MM_Jump", 0.20),
]

# Pastikan level sandbox terbuka
world_path = UES.get_editor_world().get_path_name()
print("World aktif:", world_path)
if "Test_Hermes_Aksa2" not in world_path:
    unreal.EditorLevelLibrary.load_level("/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2")

# Bersihkan aktor lama
for a in EAS.get_all_level_actors():
    if a.get_actor_label().startswith("AKCHK_") or a.get_actor_label().startswith("H6_"):
        EAS.destroy_actor(a)

for label, anim_rel, t_pos in POSES:
    print(f"\n--- Mengambil: {label} ({anim_rel}) ---")
    items = [
        (MANNY, f"{ANIM_ROOT}{anim_rel}", t_pos),
        (AKSA_LAMA, f"{ANIM_ROOT}{anim_rel}", t_pos),
        (AKSA2, f"{ANIM_ROOT}{anim_rel}", t_pos),
    ]
    
    # Spawn 3 aktor berdampingan
    spacing = 110.0
    y0 = -spacing * (len(items) - 1) / 2
    spawned = []
    for i, (mesh_path, anim_path, t) in enumerate(items):
        mesh = EAL.load_asset(mesh_path)
        seq = EAL.load_asset(anim_path)
        if mesh is None or seq is None:
            print("Aset hilang:", mesh_path, anim_path)
            continue
        a = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, y0 + i * spacing, BASE_Z), unreal.Rotator(0, 0, -90))
        a.set_actor_label(f"H6_{label}_{i}_{mesh.get_name()}")
        c = a.skeletal_mesh_component
        c.set_skeletal_mesh_asset(mesh)
        c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        c.set_animation(seq)
        if hasattr(c, "override_animation_data"):
            c.override_animation_data(seq, False, True, t, 0.0)
        c.set_position(t, False)
        for fn in ("tick_animation", "refresh_bone_transforms"):
            if hasattr(c, fn):
                getattr(c, fn)(*((0.0, False) if fn == "tick_animation" else ()))
        spawned.append(a)
    
    # Set camera viewport
    UES.set_level_viewport_camera_info(unreal.Vector(650, 0, BASE_Z + 95), unreal.Rotator(0, 0, 180))
    
    # Eksekusi HighResShot
    out_png = os.path.join(saved_shots, f"{label}.png")
    unreal.SystemLibrary.execute_console_command(None, f'HighResShot 1800x700 filename="{out_png}"')
    print("Shot diminta ->", out_png)
    
    # Hapus aktor setelah frame
    time.sleep(1.0)
    for a in spawned:
        EAS.destroy_actor(a)

print("\n=== SEMUA 4 POSE HIGHRESSHOT BERHASIL DIMINTA ===")
