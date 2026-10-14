"""Uji coba animasi Aksa2 Spike di Unreal Engine 5.6 (R1).
Menempatkan SK_Aksa (Lama) dan SK_Aksa2_Spike (Baru) berdampingan di Test_Combat dan memutar animasi Mannequin.
"""
import unreal

EAL = unreal.EditorAssetLibrary
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# Buka level Test_Combat
map_path = "/Game/Jayadwara/Maps/Test_Combat"
ok = sub.load_level(map_path)
print(f"Loaded map {map_path}: {ok}")

world = sub.get_current_level().get_world()

# Cari atau buat 2 SkeletalMeshActor untuk perbandingan
old_mesh_path = "/Game/Jayadwara/Characters/Aksa/Mesh/SK_Aksa"
new_mesh_path = "/Game/Jayadwara/Characters/Aksa2/Mesh/SK_Aksa2_Spike"

old_mesh = EAL.load_asset(old_mesh_path)
new_mesh = EAL.load_asset(new_mesh_path)

if not old_mesh or not new_mesh:
    raise RuntimeError(f"Gagal memuat mesh: old={bool(old_mesh)}, new={bool(new_mesh)}")

# Hapus actor uji lama jika ada
for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SkeletalMeshActor):
    if a.get_actor_label().startswith("TEST_Aksa_"):
        a.destroy_actor()

# Spawn Model Lama di (0, -80, 5)
loc_old = unreal.Vector(0, -80, 5)
rot = unreal.Rotator(0, 0, 0)
actor_old = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkeletalMeshActor, loc_old, rot)
actor_old.set_actor_label("TEST_Aksa_Lama")
sk_old = actor_old.get_editor_property("skeletal_mesh_component")
sk_old.set_editor_property("skeletal_mesh", old_mesh)

# Spawn Model Baru di (0, 80, 5)
loc_new = unreal.Vector(0, 80, 5)
actor_new = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkeletalMeshActor, loc_new, rot)
actor_new.set_actor_label("TEST_Aksa_Baru_Spike")
sk_new = actor_new.get_editor_property("skeletal_mesh_component")
sk_new.set_editor_property("skeletal_mesh", new_mesh)

# Uji animasi MM_Idle, Walk_Fwd, MM_Attack_01..03
anims_to_test = [
    ("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle", "MM_Idle"),
    ("/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd", "Walk_Fwd"),
    ("/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_01", "MM_Attack_01"),
    ("/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_02", "MM_Attack_02"),
    ("/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_03", "MM_Attack_03"),
]

print("=== VERIFIKASI ANIMASI MANNEQUIN PADA SK_Aksa2_Spike ===")
for a_path, a_name in anims_to_test:
    anim_seq = EAL.load_asset(a_path)
    if anim_seq:
        sk_new.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        sk_new.animation_data.anim_to_play = anim_seq
        sk_old.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        sk_old.animation_data.anim_to_play = anim_seq
        print(f"  [OK] Animasi {a_name} berhasil dipasang ke SK_Aksa2_Spike!")
    else:
        print(f"  [MISSING] Animasi {a_name} tidak ditemukan di {a_path}")

# Default set to Idle
idle_anim = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle")
if idle_anim:
    sk_new.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    sk_new.animation_data.anim_to_play = idle_anim
    sk_old.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    sk_old.animation_data.anim_to_play = idle_anim

print("Actor uji perbandingan berhasil ditaruh berdampingan di Test_Combat:")
print(f"- {actor_old.get_actor_label()} pada {loc_old}")
print(f"- {actor_new.get_actor_label()} pada {loc_new}")
