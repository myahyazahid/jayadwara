"""
Hermes/Tools/aksa2_370_configure_playable_bp.py
Mengonfigurasi BP_Hermes_Aksa2 dan instance level di Unreal Engine:
- Memasang SK_Aksa2 v36 (watertight, 0 boundary edges, bobot tersinkronisasi).
- Memasang Anim Class ke ABP_Hermes_Aksa2 (bebas Anim Dynamics glitched).
- Memasang Physics Asset PA_Aksa2 dan mengaktifkan use_attach_parent_bound.
- Menyimpan permanen ke disk.
"""
import unreal

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

map_path = "/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2"
sub.load_level(map_path)

bp_path = "/Game/Hermes/Aksa2/Blueprints/BP_Hermes_Aksa2"
bp = EAL.load_asset(bp_path)
sk_mesh = EAL.load_asset("/Game/Hermes/Aksa2/Mesh/SK_Aksa2")
pa_aksa = EAL.load_asset("/Game/Hermes/Aksa2/Rig/PA_Aksa2")
abp_hermes = EAL.load_asset("/Game/Hermes/Aksa2/Anims/ABP_Hermes_Aksa2")
mi_body = EAL.load_asset("/Game/Hermes/Aksa2/Materials/MI_Aksa2_Body")

# 1. Konfigurasi CDO BP_Hermes_Aksa2
cdo = unreal.get_default_object(bp.generated_class())
m = cdo.get_editor_property("mesh")
m.set_editor_property("skeletal_mesh_asset", sk_mesh)
m.set_editor_property("anim_class", abp_hermes.generated_class())
m.set_editor_property("physics_asset_override", pa_aksa)
m.set_editor_property("use_attach_parent_bound", True)
m.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -96.0))
m.set_editor_property("relative_rotation", unreal.Rotator(pitch=0.0, yaw=-90.0, roll=0.0))

unreal.EditorAssetLibrary.save_loaded_asset(bp)
print("CDO BP_Hermes_Aksa2 berhasil dikonfigurasi dan disimpan.")

# 2. Update level instance HERMES_PLAYABLE_AKSA2
playable = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "HERMES_PLAYABLE_AKSA2"), None)
if playable:
    pm = playable.get_component_by_class(unreal.SkeletalMeshComponent)
    pm.set_editor_property("skeletal_mesh_asset", sk_mesh)
    pm.set_editor_property("anim_class", abp_hermes.generated_class())
    pm.set_editor_property("physics_asset_override", pa_aksa)
    pm.set_editor_property("use_attach_parent_bound", True)
    pm.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    playable.set_actor_location(unreal.Vector(0.0, 0.0, 98.0), False, False)
    playable.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0), False)
    print("Instance HERMES_PLAYABLE_AKSA2 di level berhasil diperbarui.")

sub.save_current_level()
print("Level Test_Hermes_Aksa2 berhasil disimpan.")
