"""Jubah Jayadwara2 (docs/26 J1) — tangkapan visual BP_Jayadwara2 + komponen Cape dari editor (SceneCapture2D -> PNG).

Dua tahap (CAP_STAGE diset sebelum exec; editor perlu satu frame di antaranya supaya streaming tekstur & capture siap):
  setup: di Test_GiantScale2 memunculkan dua BP_Jayadwara2 (label JCCAP_*; satu menghadap kamera, satu membelakangi supaya
         punggung terkena matahari) di lantai kosong +X, plus kamera depan/samping/belakang/3-4.
  shoot: menangkap ke Saved/Screenshots/jc_cap_<nama>.png lalu menghapus aktor JCCAP_* dan menyimpan level.
CAP_DISSOLVE = [0.0, 0.3, 0.6, 0.85] menambah deret aktor membelakangi kamera dengan nilai Dissolve itu (uji lepas jubah) -> jc_cap_dissolve.png.
Editor tidak men-tick animasi: badan & jubah dalam pose rest (cek letak, skala, material, celah). Gerak diuji di Play.
  python Tools/ue_remote.py -c "CAP_STAGE='setup'; exec(open(r'Tools/ue_capture_jayadwara2_cape.py').read())"
  python Tools/ue_remote.py -c "CAP_STAGE='shoot'; exec(open(r'Tools/ue_capture_jayadwara2_cape.py').read())"
"""
import os

import unreal

STAGE = globals().get("CAP_STAGE", "setup")
J2 = "/Game/Jayadwara/Characters/Jayadwara2"
EAL = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
OUT = os.path.join(unreal.Paths.project_saved_dir(), "Screenshots")
os.makedirs(OUT, exist_ok=True)
X0, Z0 = 9000.0, 2200.0
R = 7200.0
Y_BACK = 6000.0     # aktor kedua membelakangi kamera (punggung ke sisi terang)
SHOTS = {   # nama: (yaw kamera dari aktor (derajat dunia), tinggi z, fov, y aktor)
    "depan": (180.0, Z0, 50.0, 0.0),
    "samping": (225.0, Z0, 50.0, Y_BACK),
    "depan34": (215.0, Z0 + 600, 50.0, 0.0),
    "belakang": (180.0, Z0, 50.0, Y_BACK),
    "belakang34": (145.0, Z0 + 600, 50.0, Y_BACK),
    "bahu34": (150.0, 3700.0, 20.0, Y_BACK),
    "atas": (None, 9000.0, 40.0, 0.0),              # tegak dari atas (keluhan "tempelan" J1d)
    "atas_belakang": (150.0, 8000.0, 35.0, Y_BACK),
    "samping_atas_blk": (120.0, 7000.0, 40.0, Y_BACK),  # sudut screenshot developer (J1e): belakang-samping dari atas
    "samping_atas_dpn": (240.0, 7000.0, 40.0, 0.0),     # depan-samping dari atas
}

if STAGE == "setup":
    les.load_level("/Game/Jayadwara/Maps/Test_GiantScale2")
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("JCCAP_"):
            eas.destroy_actor(a)
    bp = EAL.load_asset(f"{J2}/BP_Jayadwara2")
    import math
    # yaw 180 -> menghadap -X (sisi terkena matahari); yaw 0 -> punggung ke -X. Kapsul karakter: pusat setinggi half height.
    for label, y, yaw in (("JCCAP_Depan", 0.0, 180), ("JCCAP_Punggung", Y_BACK, 0)):
        act = eas.spawn_actor_from_class(bp.generated_class(), unreal.Vector(X0, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
        act.set_actor_label(label)
        hh = act.capsule_component.get_scaled_capsule_half_height()
        act.set_actor_location(unreal.Vector(X0, y, hh), False, False)
        comps = {c.get_name(): c for c in act.get_components_by_class(unreal.SkeletalMeshComponent)}
        cape = next((c for n, c in comps.items() if n.startswith("Cape")), None)
        print(label, "komponen:", sorted(comps), "| cape attach ke:", cape.get_attach_parent().get_name() if cape else None,
              "| anim:", cape.get_anim_instance().get_class().get_name() if cape and cape.get_anim_instance() else None,
              "| half height", round(hh))
    for name, (yaw, z, fov, y) in SHOTS.items():
        if yaw is None:
            loc, tgt = unreal.Vector(X0 - 10, y, z), unreal.Vector(X0, y, 3400.0)
        else:
            ang = math.radians(yaw)
            rr = R * (0.55 if name == "atas_belakang" else 0.9 if name.startswith("samping_atas") else 1.0)
            loc = unreal.Vector(X0 + math.cos(ang) * rr, y + math.sin(ang) * rr, z)
            tgt = unreal.Vector(X0, y, z if name == "bahu34" else (3300.0 if name == "atas_belakang" else 2600.0 if name.startswith("samping_atas") else Z0))
        rot = unreal.MathLibrary.find_look_at_rotation(loc, tgt)
        cap = eas.spawn_actor_from_class(unreal.SceneCapture2D, loc, rot)
        cap.set_actor_label(f"JCCAP_cam_{name}")
        cc = cap.capture_component2d
        rt = unreal.RenderingLibrary.create_render_target2d(cap, 1280, 960, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
        cc.set_editor_property("texture_target", rt)
        cc.set_editor_property("fov_angle", fov)
        cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
        cc.set_editor_property("capture_every_frame", True)
    # deret uji lepas jubah: aktor membelakangi kamera dengan Dissolve berbeda (UJDCapeComponent memakai parameter yang sama)
    DIS = list(globals().get("CAP_DISSOLVE", []))
    for i, dv in enumerate([d for d in DIS if d is not None]):
        y = -6000.0 - i * 4200.0
        act = eas.spawn_actor_from_class(bp.generated_class(), unreal.Vector(X0, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=0))
        act.set_actor_label(f"JCCAP_Dis{i}")
        act.set_actor_location(unreal.Vector(X0, y, act.capsule_component.get_scaled_capsule_half_height()), False, False)
        cape = next(c for c in act.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name().startswith("Cape"))
        mid = cape.create_dynamic_material_instance(0)
        mid.set_scalar_parameter_value("Dissolve", dv)
    if globals().get("CAP_TES"):                                  # J2: uji recolor zona (MI_Jayadwara2_Cape_TesWarna)
        act = eas.spawn_actor_from_class(bp.generated_class(), unreal.Vector(X0, -6000.0, 0), unreal.Rotator(roll=0, pitch=0, yaw=0))
        act.set_actor_label("JCCAP_Tes")
        act.set_actor_location(unreal.Vector(X0, -6000.0, act.capsule_component.get_scaled_capsule_half_height()), False, False)
        cape = next(c for c in act.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name().startswith("Cape"))
        cape.set_material(0, EAL.load_asset(f"{J2}/Cape/Materials/MI_Jayadwara2_Cape_TesWarna"))
        DIS = [None]
    if DIS:
        mid_y = -3000.0 if DIS == [None] else -6000.0 - (len(DIS) - 1) * 2100.0
        cap = eas.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(X0 - 14000, mid_y, Z0),
                                         unreal.MathLibrary.find_look_at_rotation(unreal.Vector(X0 - 14000, mid_y, Z0), unreal.Vector(X0, mid_y, Z0)))
        cap.set_actor_label("JCCAP_cam_dissolve")
        cc = cap.capture_component2d
        rt = unreal.RenderingLibrary.create_render_target2d(cap, 1920, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
        cc.set_editor_property("texture_target", rt)
        cc.set_editor_property("fov_angle", 70.0)
        cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
        cc.set_editor_property("capture_every_frame", True)
    unreal.SystemLibrary.execute_console_command(None, "Streaming.FlushResourceStreaming")
    print("setup ok")
else:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("JCCAP_cam_"):
            cc = a.capture_component2d
            cc.capture_scene()
            name = lab.replace("JCCAP_cam_", "")
            unreal.RenderingLibrary.export_render_target(world, cc.get_editor_property("texture_target"), OUT, f"jc_cap_{name}.png")
            print("ditulis", os.path.join(OUT, f"jc_cap_{name}.png"))
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("JCCAP_"):
            eas.destroy_actor(a)
    les.save_current_level()
