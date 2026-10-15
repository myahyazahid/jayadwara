"""
Hermes/Tools/aksa2_210_clean_studio_capture.py
Membersihkan aktor ganda dan mengambil render studio tunggal bersih SK_Aksa2:
- Hanya ada 1 karakter di level (HERMES_PLAYABLE_AKSA2) di (0, 0, 98)
- Kamera membingkai seluruh tubuh dari kepala hingga kaki tanpa ada aktor lain yang menghalangi
- Menghasilkan:
  1. aksa2_studio_front.png (Tampak depan utuh)
  2. aksa2_studio_34.png (Tampak serong 3/4)
  3. aksa2_studio_back.png (Tampak belakang utuh)
"""
from pathlib import Path
import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

map_path = "/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2"
sub.load_level(map_path)

# 1. Hapus semua aktor duplikat/sisa pengujian lama
for a in EAS.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl.startswith("TEST_") or "Dummy" in lbl or "HERMES_Cam" in lbl or "HERMES_Studio" in lbl:
        EAS.destroy_actor(a)

# 2. Ambil HERMES_PLAYABLE_AKSA2 sebagai satu-satunya aktor karakter di level
char_actor = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "HERMES_PLAYABLE_AKSA2"), None)
if not char_actor:
    bp_class = EAL.load_asset("/Game/Hermes/Aksa2/Blueprints/BP_Hermes_Aksa2")
    char_actor = EAS.spawn_actor_from_object(bp_class, unreal.Vector(0, 0, 98), unreal.Rotator(pitch=0, yaw=0, roll=0))
    char_actor.set_actor_label("HERMES_PLAYABLE_AKSA2")

char_actor.set_actor_location(unreal.Vector(0, 0, 98), False, False)
char_actor.set_actor_rotation(unreal.Rotator(pitch=0, yaw=0, roll=0), False)

# Pastikan skeletal mesh dan material terpasang
sk_mesh = EAL.load_asset("/Game/Hermes/Aksa2/Mesh/SK_Aksa2")
mi_body = EAL.load_asset("/Game/Hermes/Aksa2/Materials/MI_Aksa2_Body")
mesh_comp = char_actor.get_component_by_class(unreal.SkeletalMeshComponent)
if mesh_comp and sk_mesh:
    mesh_comp.set_editor_property("skeletal_mesh_asset", sk_mesh)
    if mi_body:
        mats = mesh_comp.get_editor_property("materials")
        for m in mats:
            m.set_editor_property("material_interface", mi_body)
        mesh_comp.set_editor_property("materials", mats)

# 3. Directional Light lembut
dir_light = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(400, 0, 350), unreal.Rotator(pitch=-20, yaw=180, roll=0))
dir_light.set_actor_label("HERMES_Studio_Sun")
dlc = dir_light.get_editor_property("light_component")
dlc.set_editor_property("intensity", 3.0)
dlc.set_editor_property("light_color", unreal.Color(r=255, g=250, b=245, a=255))

out_dir = Path(r"C:\repository\unreal_engine\jayadwara_hermes\Hermes\Art\aksa2\Render")
out_dir.mkdir(parents=True, exist_ok=True)

# 4. Kamera Studio Tunggal
cam = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(380, 0, 185), unreal.Rotator(pitch=-6, yaw=180, roll=0))
cam.set_actor_label("HERMES_Studio_Cam")
cc = cam.capture_component2d
rt = unreal.RenderingLibrary.create_render_target2d(cam, 960, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
cc.set_editor_property("texture_target", rt)
cc.set_editor_property("fov_angle", 35.0)
cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
cc.set_editor_property("capture_every_frame", False)

# Tampak Depan
cc.capture_scene()
unreal.RenderingLibrary.export_render_target(cam, rt, str(out_dir), "aksa2_studio_front.png")
print("Captured: aksa2_studio_front.png")

# Tampak Serong 3/4 (Kamera digeser ke X=300, Y=220)
cam.set_actor_location(unreal.Vector(300, 220, 185), False, False)
cam.set_actor_rotation(unreal.Rotator(pitch=-6, yaw=216, roll=0), False)
cc.capture_scene()
unreal.RenderingLibrary.export_render_target(cam, rt, str(out_dir), "aksa2_studio_34.png")
print("Captured: aksa2_studio_34.png")

# Tampak Belakang (Kamera digeser ke X=-380, Y=0)
cam.set_actor_location(unreal.Vector(-380, 0, 185), False, False)
cam.set_actor_rotation(unreal.Rotator(pitch=-6, yaw=0, roll=0), False)
cc.capture_scene()
unreal.RenderingLibrary.export_render_target(cam, rt, str(out_dir), "aksa2_studio_back.png")
print("Captured: aksa2_studio_back.png")

# Bersihkan aktor studio
EAS.destroy_actor(dir_light)
EAS.destroy_actor(cam)

sub.save_current_level()
print("Selesai capture studio tunggal Aksa2 v31!")
