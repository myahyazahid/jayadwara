"""
Hermes/Tools/aksa2_280_capture_exact_fall_loop.py
Menangkap pose in-air MM_Fall_Loop pada SK_Aksa2 v33 secara utuh:
- Karakter melayang di udara (Head Z=260cm, Center Z=190cm).
- Kamera ditempatkan di (160, -260, 260) menghadap ke pusat tubuh karakter di (0, 0, 190).
- Menggunakan override_animation_data agar pose Fall Loop terevaluasi 100% presisi.
"""
from pathlib import Path
import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

map_path = "/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2"
sub.load_level(map_path)

# 1. Bersihkan aktor pengujian lama
for a in EAS.get_all_level_actors():
    if a.get_actor_label() in ["HERMES_Jump_Cam", "HERMES_Jump_Sun", "TEST_Jump_Actor"]:
        EAS.destroy_actor(a)

playable = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "HERMES_PLAYABLE_AKSA2"), None)
if playable:
    playable.set_actor_location(unreal.Vector(-600, -600, -600), False, False)

# 2. SkeletalMeshActor untuk pengujian pose Fall Loop
test_actor = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 98), unreal.Rotator(pitch=0, yaw=0, roll=0))
test_actor.set_actor_label("TEST_Jump_Actor")

sk_mesh = EAL.load_asset("/Game/Hermes/Aksa2/Mesh/SK_Aksa2")
mi_body = EAL.load_asset("/Game/Hermes/Aksa2/Materials/MI_Aksa2_Body")
sk_comp = test_actor.get_editor_property("skeletal_mesh_component")
sk_comp.set_editor_property("skeletal_mesh_asset", sk_mesh)
mats = sk_comp.get_editor_property("override_materials")
for m in mats:
    m.set_editor_property("material_interface", mi_body)
sk_comp.set_editor_property("override_materials", mats)

# Putar animasi MM_Fall_Loop dengan override_animation_data
fall_anim = EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/Jump/MM_Fall_Loop")
sk_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
sk_comp.set_update_animation_in_editor(True)
sk_comp.override_animation_data(fall_anim, False, False, 0.25)

# 3. Studio Directional Light menerangi punggung dan lengan dari arah kamera
sun = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(250, -350, 450), unreal.Rotator(pitch=-30, yaw=55, roll=0))
sun.set_actor_label("HERMES_Jump_Sun")
dlc = sun.get_editor_property("light_component")
dlc.set_editor_property("intensity", 3.5)
dlc.set_editor_property("light_color", unreal.Color(r=255, g=250, b=245, a=255))

# 4. Kamera membingkai seluruh tubuh di udara
# Center tubuh saat fall loop berada di Z=190 cm
cam_loc = unreal.Vector(180, -280, 260)
target_loc = unreal.Vector(0, 0, 190)
cam_rot = unreal.MathLibrary.find_look_at_rotation(cam_loc, target_loc)

cam = EAS.spawn_actor_from_class(unreal.SceneCapture2D, cam_loc, cam_rot)
cam.set_actor_label("HERMES_Jump_Cam")
cc = cam.capture_component2d
rt = unreal.RenderingLibrary.create_render_target2d(cam, 800, 600, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc.set_editor_property("texture_target", rt)
cc.set_editor_property("fov_angle", 52.0)
cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc.set_editor_property("capture_every_frame", False)

out_dir = Path(r"C:\repository\unreal_engine\jayadwara_hermes\Hermes\Art\aksa2\Render")
cc.capture_scene()
unreal.RenderingLibrary.export_render_target(cam, rt, str(out_dir), "aksa2_ue_fall_loop_exact_framed.png")
print("Captured: aksa2_ue_fall_loop_exact_framed.png")

# Bersihkan aktor pembantu
EAS.destroy_actor(sun)
EAS.destroy_actor(cam)
EAS.destroy_actor(test_actor)

if playable:
    playable.set_actor_location(unreal.Vector(0, 0, 98), False, False)

sub.save_current_level()
print("Selesai render tepat sasaran Fall Loop!")
