"""
Hermes/Tools/aksa2_185_capture_perfect_ue.py
Menangkap visual model SK_Aksa2 v30 di Unreal Engine pada animasi Idle, Jump, dan Walk.
"""
from pathlib import Path
import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary

map_path = "/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2"
sub.load_level(map_path)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

# Cari atau spawn SkeletalMeshActor untuk pengujian visual
actor_new = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "TEST_Hermes_Aksa2_Baru"), None)
if not actor_new:
    actor_new = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(pitch=0, yaw=0, roll=0))
    actor_new.set_actor_label("TEST_Hermes_Aksa2_Baru")

sk_mesh = EAL.load_asset("/Game/Hermes/Aksa2/Mesh/SK_Aksa2")
sk_comp = actor_new.get_editor_property("skeletal_mesh_component")
sk_comp.set_editor_property("skeletal_mesh_asset", sk_mesh)
actor_new.set_actor_location(unreal.Vector(0, 0, 0), False, False)
actor_new.set_actor_rotation(unreal.Rotator(pitch=0, yaw=0, roll=0), False)

# Directional Light lembut dari arah depan kamera (Pitch=-15, Yaw=180)
dir_light = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(500, 0, 300), unreal.Rotator(pitch=-15, yaw=180, roll=0))
dir_light.set_actor_label("HERMES_Studio_Sun")
dlc = dir_light.get_editor_property("light_component")
dlc.set_editor_property("intensity", 3.0)
dlc.set_editor_property("light_color", unreal.Color(r=255, g=250, b=245, a=255))

# Kamera SceneCapture2D membingkai seluruh tubuh
cam_loc = unreal.Vector(450, 0, 95)
cam_rot = unreal.Rotator(pitch=0, yaw=180, roll=0)
cap_actor = EAS.spawn_actor_from_class(unreal.SceneCapture2D, cam_loc, cam_rot)
cap_actor.set_actor_label("HERMES_Studio_Camera")
cc = cap_actor.capture_component2d
rt = unreal.RenderingLibrary.create_render_target2d(cap_actor, 1600, 900, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc.set_editor_property("texture_target", rt)
cc.set_editor_property("fov_angle", 32.0)
cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc.set_editor_property("capture_every_frame", False)

out_dir = Path(r"C:\repository\unreal_engine\jayadwara_hermes\Hermes\Art\aksa2\Render")
out_dir.mkdir(parents=True, exist_ok=True)

sk_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
sk_comp.set_update_animation_in_editor(True)

# 1. Idle
idle_anim = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle")
if idle_anim:
    sk_comp.play_animation(idle_anim, False)
    sk_comp.set_position(0.0, False)
    cc.capture_scene()
    out_name = "aksa2_ue_perfect_v30_idle.png"
    unreal.RenderingLibrary.export_render_target(world, rt, str(out_dir), out_name)
    print(f"Captured: {out_name}")

# 2. Jump (Mid-Air tangan terangkat)
jump_anim = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/Jump/MM_Jump")
if jump_anim:
    sk_comp.play_animation(jump_anim, False)
    sk_comp.set_position(0.35, False)
    cc.capture_scene()
    out_name = "aksa2_ue_perfect_v30_jump.png"
    unreal.RenderingLibrary.export_render_target(world, rt, str(out_dir), out_name)
    print(f"Captured: {out_name}")

# 3. Walk
walk_anim = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd")
if walk_anim:
    sk_comp.play_animation(walk_anim, False)
    sk_comp.set_position(0.40, False)
    cc.capture_scene()
    out_name = "aksa2_ue_perfect_v30_walk.png"
    unreal.RenderingLibrary.export_render_target(world, rt, str(out_dir), out_name)
    print(f"Captured: {out_name}")

# Bersihkan aktor pembantu
EAS.destroy_actor(dir_light)
EAS.destroy_actor(cap_actor)

if idle_anim:
    sk_comp.play_animation(idle_anim, True)

sub.save_current_level()
print("Selesai render visual Unreal Engine v30!")
