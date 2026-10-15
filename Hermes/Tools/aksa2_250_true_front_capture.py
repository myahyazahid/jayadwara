"""
Hermes/Tools/aksa2_250_true_front_capture.py
Menangkap tampak depan murni, tampak 3/4, dan tampak belakang utuh SK_Aksa2 di Unreal Engine.
Kamera ditempatkan pada sumbu -Y menghadap +Y tepat ke wajah dan dada karakter.
"""
from pathlib import Path
import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

map_path = "/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2"
sub.load_level(map_path)

# 1. Bersihkan aktor pengujian sisa
for a in EAS.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl.startswith("TEST_") or "Dummy" in lbl or "HERMES_Cam" in lbl or "HERMES_Studio" in lbl:
        EAS.destroy_actor(a)

# 2. HERMES_PLAYABLE_AKSA2 di (0, 0, 98)
char_actor = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "HERMES_PLAYABLE_AKSA2"), None)
if not char_actor:
    bp_class = EAL.load_asset("/Game/Hermes/Aksa2/Blueprints/BP_Hermes_Aksa2")
    char_actor = EAS.spawn_actor_from_object(bp_class, unreal.Vector(0, 0, 98), unreal.Rotator(pitch=0, yaw=90, roll=0))
    char_actor.set_actor_label("HERMES_PLAYABLE_AKSA2")

char_actor.set_actor_location(unreal.Vector(0, 0, 98), False, False)
char_actor.set_actor_rotation(unreal.Rotator(pitch=0, yaw=90, roll=0), False)

sk_mesh = EAL.load_asset("/Game/Hermes/Aksa2/Mesh/SK_Aksa2")
mi_body = EAL.load_asset("/Game/Hermes/Aksa2/Materials/MI_Aksa2_Body")
mesh_comp = char_actor.get_component_by_class(unreal.SkeletalMeshComponent)
if mesh_comp and sk_mesh:
    mesh_comp.set_editor_property("skeletal_mesh_asset", sk_mesh)
    if mi_body:
        mats = mesh_comp.get_editor_property("override_materials")
        for m in mats:
            m.set_editor_property("material_interface", mi_body)
        mesh_comp.set_editor_property("override_materials", mats)

# 3. Studio Directional Light dari arah depan-atas (menghadap ke arah +Y)
dir_light = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, -450, 400), unreal.Rotator(pitch=-25, yaw=90, roll=0))
dir_light.set_actor_label("HERMES_Studio_Sun")
dlc = dir_light.get_editor_property("light_component")
dlc.set_editor_property("intensity", 3.2)
dlc.set_editor_property("light_color", unreal.Color(r=255, g=250, b=245, a=255))

out_dir = Path(r"C:\repository\unreal_engine\jayadwara_hermes\Hermes\Art\aksa2\Render")
out_dir.mkdir(parents=True, exist_ok=True)

# 4. Kamera Utama Terpusat (Y=-420, X=0, Z=92 cm, Pitch=0, Yaw=90)
cam = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, -420, 92), unreal.Rotator(pitch=0, yaw=90, roll=0))
cam.set_actor_label("HERMES_Studio_Cam")
cc = cam.capture_component2d
rt = unreal.RenderingLibrary.create_render_target2d(cam, 960, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc.set_editor_property("texture_target", rt)
cc.set_editor_property("fov_angle", 42.0)
cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc.set_editor_property("capture_every_frame", False)

# 1. Tampak Depan Murni Idle
cc.capture_scene()
unreal.RenderingLibrary.export_render_target(cam, rt, str(out_dir), "aksa2_ue_true_front_idle.png")
print("Captured: aksa2_ue_true_front_idle.png")

# 2. Tampak Serong 3/4 Idle (X=260, Y=-340, Z=92, Yaw=127)
cam.set_actor_location(unreal.Vector(260, -340, 92), False, False)
cam.set_actor_rotation(unreal.Rotator(pitch=0, yaw=127, roll=0), False)
cc.capture_scene()
unreal.RenderingLibrary.export_render_target(cam, rt, str(out_dir), "aksa2_ue_true_34_idle.png")
print("Captured: aksa2_ue_true_34_idle.png")

# 3. Tampak Belakang Murni Idle (X=0, Y=420, Z=92, Yaw=-90)
cam.set_actor_location(unreal.Vector(0, 420, 92), False, False)
cam.set_actor_rotation(unreal.Rotator(pitch=0, yaw=-90, roll=0), False)
cc.capture_scene()
unreal.RenderingLibrary.export_render_target(cam, rt, str(out_dir), "aksa2_ue_true_back_idle.png")
print("Captured: aksa2_ue_true_back_idle.png")

# Bersihkan aktor pembantu
EAS.destroy_actor(dir_light)
EAS.destroy_actor(cam)

sub.save_current_level()
print("Selesai True Front Capture Aksa2 v32!")
