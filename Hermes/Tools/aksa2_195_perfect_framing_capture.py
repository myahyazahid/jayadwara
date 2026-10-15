"""
Hermes/Tools/aksa2_195_perfect_framing_capture.py
Menangkap visual seluruh tubuh (head to toe) SK_Aksa2 v31 di Unreal Engine:
1. Tampak Depan Idle (aksa2_ue_v31_front_idle.png)
2. Tampak Depan Jump (aksa2_ue_v31_front_jump.png)
3. Tampak Belakang Jump (aksa2_ue_v31_back_jump.png)
4. Tampak Depan Walk (aksa2_ue_v31_front_walk.png)
"""
from pathlib import Path
import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary

map_path = "/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2"
sub.load_level(map_path)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

# Sembunyikan atau posisikan aktor yang ada
playable = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "HERMES_PLAYABLE_AKSA2"), None)
if playable:
    playable.set_actor_location(unreal.Vector(-500, -500, -500), False, False)

# Gunakan TEST_Hermes_Aksa2_Baru sebagai subjek render utama
actor = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "TEST_Hermes_Aksa2_Baru"), None)
if not actor:
    actor = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 98), unreal.Rotator(pitch=0, yaw=0, roll=0))
    actor.set_actor_label("TEST_Hermes_Aksa2_Baru")

sk_mesh = EAL.load_asset("/Game/Hermes/Aksa2/Mesh/SK_Aksa2")
sk_comp = actor.get_editor_property("skeletal_mesh_component")
sk_comp.set_editor_property("skeletal_mesh_asset", sk_mesh)
actor.set_actor_location(unreal.Vector(0, 0, 98), False, False)
actor.set_actor_rotation(unreal.Rotator(pitch=0, yaw=0, roll=0), False)

# Directional light depan
dir_light = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(400, 0, 300), unreal.Rotator(pitch=-20, yaw=180, roll=0))
dir_light.set_actor_label("HERMES_Capture_Sun")
dlc = dir_light.get_editor_property("light_component")
dlc.set_editor_property("intensity", 3.0)
dlc.set_editor_property("light_color", unreal.Color(r=255, g=250, b=245, a=255))

# Kamera Depan (X=360, Y=0, Z=180) menghadap -X ke (0,0,180) -> Yaw=180
cam_front = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(360, 0, 180), unreal.Rotator(pitch=-8, yaw=180, roll=0))
cam_front.set_actor_label("HERMES_Cam_Front")
cc_front = cam_front.capture_component2d
rt_front = unreal.RenderingLibrary.create_render_target2d(cam_front, 960, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc_front.set_editor_property("texture_target", rt_front)
cc_front.set_editor_property("fov_angle", 35.0)
cc_front.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc_front.set_editor_property("capture_every_frame", False)

# Kamera Belakang (X=-360, Y=0, Z=180) menghadap +X ke (0,0,180) -> Yaw=0
cam_back = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(-360, 0, 180), unreal.Rotator(pitch=-8, yaw=0, roll=0))
cam_back.set_actor_label("HERMES_Cam_Back")
cc_back = cam_back.capture_component2d
rt_back = unreal.RenderingLibrary.create_render_target2d(cam_back, 960, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc_back.set_editor_property("texture_target", rt_back)
cc_back.set_editor_property("fov_angle", 35.0)
cc_back.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc_back.set_editor_property("capture_every_frame", False)

out_dir = Path(r"C:\repository\unreal_engine\jayadwara_hermes\Hermes\Art\aksa2\Render")
out_dir.mkdir(parents=True, exist_ok=True)

sk_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
sk_comp.set_update_animation_in_editor(True)

# 1. Idle Depan
idle_anim = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle")
if idle_anim:
    sk_comp.play_animation(idle_anim, False)
    sk_comp.set_position(0.0, False)
    cc_front.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt_front, str(out_dir), "aksa2_ue_v31_front_idle.png")
    print("Captured: aksa2_ue_v31_front_idle.png")

# 2. Jump Depan & Belakang
jump_anim = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/Jump/MM_Jump")
if jump_anim:
    sk_comp.play_animation(jump_anim, False)
    sk_comp.set_position(0.35, False)
    cc_front.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt_front, str(out_dir), "aksa2_ue_v31_front_jump.png")
    print("Captured: aksa2_ue_v31_front_jump.png")

    cc_back.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt_back, str(out_dir), "aksa2_ue_v31_back_jump.png")
    print("Captured: aksa2_ue_v31_back_jump.png")

# 3. Walk Depan
walk_anim = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd")
if walk_anim:
    sk_comp.play_animation(walk_anim, False)
    sk_comp.set_position(0.40, False)
    cc_front.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt_front, str(out_dir), "aksa2_ue_v31_front_walk.png")
    print("Captured: aksa2_ue_v31_front_walk.png")

# Bersihkan aktor capture
EAS.destroy_actor(dir_light)
EAS.destroy_actor(cam_front)
EAS.destroy_actor(cam_back)

# Kembalikan playable ke posisi awal
if playable:
    playable.set_actor_location(unreal.Vector(300, 0, 98), False, False)
    sk_play = playable.get_editor_property("skeletal_mesh_component") if hasattr(playable, "skeletal_mesh_component") else None
    # Update playable skeletal mesh asset
    mesh_comp = playable.get_component_by_class(unreal.SkeletalMeshComponent)
    if mesh_comp:
        mesh_comp.set_editor_property("skeletal_mesh_asset", sk_mesh)

sub.save_current_level()
print("Selesai capture visual sempurna v31!")
