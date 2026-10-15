"""
Hermes/Tools/aksa2_200_full_jump_framing.py
Menangkap visual utuh lompatan (MM_Jump) SK_Aksa2 v31 di Unreal Engine:
Kamera Z=220, Distance=520, FOV=42 membingkai seluruh lompatan dari kepala, kedua tangan terangkat, badan, hingga sepatu.
"""
from pathlib import Path
import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary

map_path = "/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2"
sub.load_level(map_path)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

# Sembunyikan playable agar tidak menghalangi
playable = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "HERMES_PLAYABLE_AKSA2"), None)
if playable:
    playable.set_actor_location(unreal.Vector(-800, -800, -800), False, False)

actor = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "TEST_Hermes_Aksa2_Baru"), None)
if not actor:
    actor = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 98), unreal.Rotator(pitch=0, yaw=0, roll=0))
    actor.set_actor_label("TEST_Hermes_Aksa2_Baru")

sk_mesh = EAL.load_asset("/Game/Hermes/Aksa2/Mesh/SK_Aksa2")
sk_comp = actor.get_editor_property("skeletal_mesh_component")
sk_comp.set_editor_property("skeletal_mesh_asset", sk_mesh)
actor.set_actor_location(unreal.Vector(0, 0, 98), False, False)
actor.set_actor_rotation(unreal.Rotator(pitch=0, yaw=0, roll=0), False)

# Directional light studio
dir_light = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(500, 0, 400), unreal.Rotator(pitch=-20, yaw=180, roll=0))
dir_light.set_actor_label("HERMES_Studio_Sun")
dlc = dir_light.get_editor_property("light_component")
dlc.set_editor_property("intensity", 3.0)
dlc.set_editor_property("light_color", unreal.Color(r=255, g=250, b=245, a=255))

# Kamera Depan Penuh (X=520, Y=0, Z=220) menghadap -X ke (0,0,220)
cam_front = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(520, 0, 220), unreal.Rotator(pitch=0, yaw=180, roll=0))
cam_front.set_actor_label("HERMES_Cam_Full")
cc_front = cam_front.capture_component2d
rt_front = unreal.RenderingLibrary.create_render_target2d(cam_front, 960, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc_front.set_editor_property("texture_target", rt_front)
cc_front.set_editor_property("fov_angle", 42.0)
cc_front.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc_front.set_editor_property("capture_every_frame", False)

# Kamera Serong Depan 3/4 (X=400, Y=300, Z=220)
cam_34 = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(400, 300, 220), unreal.Rotator(pitch=0, yaw=217, roll=0))
cam_34.set_actor_label("HERMES_Cam_34")
cc_34 = cam_34.capture_component2d
rt_34 = unreal.RenderingLibrary.create_render_target2d(cam_34, 960, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc_34.set_editor_property("texture_target", rt_34)
cc_34.set_editor_property("fov_angle", 42.0)
cc_34.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc_34.set_editor_property("capture_every_frame", False)

out_dir = Path(r"C:\repository\unreal_engine\jayadwara_hermes\Hermes\Art\aksa2\Render")
out_dir.mkdir(parents=True, exist_ok=True)

sk_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
sk_comp.set_update_animation_in_editor(True)

# 1. Pose Lompat Puncak (MM_Jump di pos 0.35s)
jump_anim = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/Jump/MM_Jump")
if jump_anim:
    sk_comp.play_animation(jump_anim, False)
    sk_comp.set_position(0.35, False)
    
    # Render tampak depan
    cc_front.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt_front, str(out_dir), "aksa2_ue_jump_full_front.png")
    print("Captured: aksa2_ue_jump_full_front.png")

    # Render tampak 3/4
    cc_34.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt_34, str(out_dir), "aksa2_ue_jump_full_34.png")
    print("Captured: aksa2_ue_jump_full_34.png")

# Bersihkan aktor capture
EAS.destroy_actor(dir_light)
EAS.destroy_actor(cam_front)
EAS.destroy_actor(cam_34)

# Kembalikan playable
if playable:
    playable.set_actor_location(unreal.Vector(300, 0, 98), False, False)
    mesh_comp = playable.get_component_by_class(unreal.SkeletalMeshComponent)
    if mesh_comp:
        mesh_comp.set_editor_property("skeletal_mesh_asset", sk_mesh)

sub.save_current_level()
print("Selesai render visual utuh lompatan v31!")
