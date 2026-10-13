"""Jayadwara2 — tangkapan visual lama vs baru dari editor (SceneCapture2D -> render target -> PNG), pola ue_capture_jerangkong.py.

Dua tahap (supaya animasi sempat di-tick satu frame editor di antaranya). Variabel CAP_STAGE diset sebelum exec:
  setup: di Test_GiantScale2 memunculkan aktor sementara (label J2CAP_*) di lantai kosong +X (difoto dari sisi -X yang terkena matahari):
         Jayadwara LAMA (y=-1800) dan BARU (y=+1800) berdampingan, plus pasangan beranimasi (CAP_ANIM, default MM_Attack_01 pada posisi 0,45) dan kamera.
         CATATAN: editor tidak men-tick animasi, jadi pasangan beranimasi tetap berpose rest; animasi diuji lewat PIE (ue_pie_jayadwara2.py).
  shoot: menangkap tiap kamera ke Saved/Screenshots/j2_cap_<nama>.png lalu menghapus semua aktor J2CAP_* dan menyimpan level.
"""
import os

import unreal

STAGE = globals().get("CAP_STAGE", "setup")
J1 = "/Game/Jayadwara/Characters/Jayadwara"
J2 = "/Game/Jayadwara/Characters/Jayadwara2"
EAL = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
OUT = os.path.join(unreal.Paths.project_saved_dir(), "Screenshots")
os.makedirs(OUT, exist_ok=True)
X0 = 9000.0

SHOTS = {   # (lokasi kamera, rotasi, fov)
    "berdampingan": (unreal.Vector(0, 0, 2300), unreal.Rotator(roll=0, pitch=0, yaw=0), 70.0),
    "baru_depan": (unreal.Vector(2000, 1800, 2300), unreal.Rotator(roll=0, pitch=0, yaw=0), 55.0),
    "lama_depan": (unreal.Vector(2000, -1800, 2300), unreal.Rotator(roll=0, pitch=0, yaw=0), 55.0),
    "baru_kepala": (unreal.Vector(6000, 1800, 3900), unreal.Rotator(roll=0, pitch=0, yaw=0), 38.0),
    "lama_kepala": (unreal.Vector(6000, -1800, 3900), unreal.Rotator(roll=0, pitch=0, yaw=0), 38.0),
    "baru_mata": (unreal.Vector(7000, 1800, 4150), unreal.Rotator(roll=0, pitch=0, yaw=0), 14.0),
    "lama_mata": (unreal.Vector(7000, -1800, 4150), unreal.Rotator(roll=0, pitch=0, yaw=0), 14.0),
    "baru_mata34": (unreal.Vector(7500, 800, 4150), unreal.Rotator(roll=0, pitch=0, yaw=33.7), 14.0),
    "baru_kaki": (unreal.Vector(6500, 1800, 1700), unreal.Rotator(roll=0, pitch=0, yaw=0), 32.0),
    "baru_kaki34": (unreal.Vector(7200, 300, 1700), unreal.Rotator(roll=0, pitch=0, yaw=38.0), 32.0),
    "tes_warna": (unreal.Vector(2000, -5300, 2300), unreal.Rotator(roll=0, pitch=0, yaw=0), 55.0),
    "lod": (unreal.Vector(0, -8600, 2300), unreal.Rotator(roll=0, pitch=0, yaw=0), 62.0),
    "lod0_kepala": (unreal.Vector(7000, -9500, 4150), unreal.Rotator(roll=0, pitch=0, yaw=0), 14.0),
    "lod1_kepala": (unreal.Vector(7000, -7700, 4150), unreal.Rotator(roll=0, pitch=0, yaw=0), 14.0),
    "lod2_kepala": (unreal.Vector(7000, -5900, 4150), unreal.Rotator(roll=0, pitch=0, yaw=0), 14.0),
    "lod3_kepala": (unreal.Vector(7000, -4100, 4150), unreal.Rotator(roll=0, pitch=0, yaw=0), 14.0),
    "anim": (unreal.Vector(0, 5250, 2300), unreal.Rotator(roll=0, pitch=0, yaw=0), 70.0),
}
ANIM = globals().get("CAP_ANIM", "MM_Attack_01")
ANIM_POS = float(globals().get("CAP_ANIM_POS", 0.45))


def spawn_mesh(label, mesh_path, loc, yaw, anim=None, pos=0.5):
    a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    a.set_actor_label(label)
    c = a.skeletal_mesh_component
    c.set_skinned_asset_and_update(EAL.load_asset(mesh_path))
    if anim:
        c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        c.set_update_animation_in_editor(True)
        c.play_animation(EAL.load_asset(anim), True)
        c.set_position(pos, False)
    return a


if STAGE == "setup":
    les.load_level("/Game/Jayadwara/Maps/Test_GiantScale2")
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("J2CAP_"):
            eas.destroy_actor(a)
    # mesh menghadap +Y komponen; yaw 90 aktor -> menghadap -X (ke kamera, sisi terang)
    spawn_mesh("J2CAP_Lama", f"{J1}/Mesh/SK_Jayadwara", unreal.Vector(X0, -1800, 0), 90)
    spawn_mesh("J2CAP_Baru", f"{J2}/Mesh/SK_Jayadwara2", unreal.Vector(X0, 1800, 0), 90)
    tes = spawn_mesh("J2CAP_Tes", f"{J2}/Mesh/SK_Jayadwara2", unreal.Vector(X0, -5300, 0), 90)
    tes.skeletal_mesh_component.set_material(0, EAL.load_asset(f"{J2}/Materials/MI_Jayadwara2_TesWarna"))     # uji recolor zona
    for i in range(4):                                                                 # LOD0-3 berdampingan (LOD dipaksa)
        a_ = spawn_mesh(f"J2CAP_LOD{i}", f"{J2}/Mesh/SK_Jayadwara2", unreal.Vector(X0, -9500 + i * 1800, 0), 90)
        a_.skeletal_mesh_component.set_forced_lod(i + 1)
    spawn_mesh("J2CAP_LamaAnim", f"{J1}/Mesh/SK_Jayadwara", unreal.Vector(X0, 3500, 0), 90, f"{J1}/Anims/{ANIM}_JD", ANIM_POS)
    spawn_mesh("J2CAP_BaruAnim", f"{J2}/Mesh/SK_Jayadwara2", unreal.Vector(X0, 7000, 0), 90, f"{J2}/Anims/{ANIM}_JD2", ANIM_POS)
    for name, (loc, rot, fov) in SHOTS.items():
        cap = eas.spawn_actor_from_class(unreal.SceneCapture2D, loc, rot)
        cap.set_actor_label(f"J2CAP_cam_{name}")
        cc = cap.capture_component2d
        rt = unreal.RenderingLibrary.create_render_target2d(cap, 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
        cc.set_editor_property("texture_target", rt)
        cc.set_editor_property("fov_angle", fov)
        cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
        cc.set_editor_property("capture_every_frame", True)
    print("setup ok")
else:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("J2CAP_cam_"):
            cc = a.capture_component2d
            cc.capture_scene()
            name = lab.replace("J2CAP_cam_", "")
            unreal.RenderingLibrary.export_render_target(world, cc.get_editor_property("texture_target"), OUT, f"j2_cap_{name}.png")
            print("ditulis", os.path.join(OUT, f"j2_cap_{name}.png"))
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("J2CAP_"):
            eas.destroy_actor(a)
    les.save_current_level()
