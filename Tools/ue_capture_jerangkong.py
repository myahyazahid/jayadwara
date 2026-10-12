"""Jerangkong — tangkapan visual dari editor tanpa HighResShot (SceneCapture2D -> render target -> PNG).

Pakai (dua tahap, supaya animasi sempat di-tick satu frame editor di antaranya):
  python Tools/ue_remote.py -c "CAP_STAGE='setup'; exec(open(r'C:/repository/unreal_engine/jayadwara/Tools/ue_capture_jerangkong.py').read())"
  python Tools/ue_remote.py -c "CAP_STAGE='shoot'; exec(open(r'C:/repository/unreal_engine/jayadwara/Tools/ue_capture_jerangkong.py').read())"
setup: di Test_GiantScale memunculkan aktor uji sementara (label JKCAP_*) di lantai kosong +X (difoto dari sisi -X yang terkena matahari): Jerangkong & Jayadwara
       berdampingan (rasa skala), Jerangkong memutar MM_Attack_01_JK, 2 minion (idle & serangan), plus kamera capture;
       "boss_depan" memotret BP_Jerangkong yang ditempatkan di level dari posisi PlayerStart.
shoot: menangkap tiap kamera ke Saved/Screenshots/jk_cap_<nama>.png lalu menghapus semua aktor JKCAP_* (level tidak disimpan).
"""
import os

import unreal

STAGE = globals().get("CAP_STAGE", "setup")
JK = "/Game/Jayadwara/Characters/Jerangkong"
EAL = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
OUT = os.path.join(unreal.Paths.project_saved_dir(), "Screenshots")
os.makedirs(OUT, exist_ok=True)

# (nama, lokasi kamera, rotasi kamera, fov)
SHOTS = {   # matahari level menyinari ke arah +X: kamera di sisi -X subjek supaya sisi terang terlihat
    "skala": (unreal.Vector(1000, 0, 2300), unreal.Rotator(roll=0, pitch=-3, yaw=0), 60.0),
    "boss_depan": (unreal.Vector(2000, 0, 1700), unreal.Rotator(roll=0, pitch=2, yaw=-141), 70.0),
    "anim": (unreal.Vector(2500, -6000, 1600), unreal.Rotator(roll=0, pitch=0, yaw=0), 55.0),
    "minion": (unreal.Vector(8450, 5075, 110), unreal.Rotator(roll=0, pitch=-3, yaw=0), 50.0),
    "rontok": (unreal.Vector(3500, -10000, 1500), unreal.Rotator(roll=0, pitch=0, yaw=0), 55.0),
}
# uji pivot SM (gate Iterasi 1, docs/20): tulang disembunyikan di SK, SM dimunculkan di transform tulangnya
PIVOT_TEST = [("LowerArmL", "lowerarm_l"), ("HandL", "hand_l")]


def spawn_mesh(label, mesh_path, loc, yaw, anim=None):
    a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    a.set_actor_label(label)
    c = a.skeletal_mesh_component
    c.set_skinned_asset_and_update(EAL.load_asset(mesh_path))
    if anim:
        c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        c.set_update_animation_in_editor(True)
        c.play_animation(EAL.load_asset(anim), True)
        c.set_position(0.55, False)
    return a


if STAGE == "setup":
    les.load_level("/Game/Jayadwara/Maps/Test_GiantScale")
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("JKCAP_"):
            eas.destroy_actor(a)
    # area lantai kosong di +X. Mesh menghadap +Y komponen; yaw 90 aktor -> menghadap -X (ke kamera, sisi terang)
    spawn_mesh("JKCAP_Boss", f"{JK}/Mesh/SK_Jerangkong", unreal.Vector(9000, -1800, 0), 90)
    spawn_mesh("JKCAP_Jayadwara", "/Game/Jayadwara/Characters/Jayadwara/Mesh/SK_Jayadwara", unreal.Vector(9000, 1800, 0), 90)
    spawn_mesh("JKCAP_JKAnim", f"{JK}/Mesh/SK_Jerangkong", unreal.Vector(9000, -6000, 0), 120,
               f"{JK}/Anims_Jerangkong/MM_Attack_01_JK")
    spawn_mesh("JKCAP_Minion1", f"{JK}/Mesh/SK_Kerangka", unreal.Vector(9000, 4980, 0), 90,
               f"{JK}/Anims_Kerangka/MM_Idle_KR")
    spawn_mesh("JKCAP_Minion2", f"{JK}/Mesh/SK_Kerangka", unreal.Vector(9000, 5170, 0), 60,
               f"{JK}/Anims_Kerangka/MM_Attack_02_KR")
    r = spawn_mesh("JKCAP_Rontok", f"{JK}/Mesh/SK_Jerangkong", unreal.Vector(9000, -10000, 0), 120,
                   f"{JK}/Anims_Jerangkong/MM_Attack_01_JK")
    r.skeletal_mesh_component.hide_bone_by_name("lowerarm_l", unreal.PhysBodyOp.PBO_NONE)
    for name, (loc, rot, fov) in SHOTS.items():
        cap = eas.spawn_actor_from_class(unreal.SceneCapture2D, loc, rot)
        cap.set_actor_label(f"JKCAP_cam_{name}")
        cc = cap.capture_component2d
        rt = unreal.RenderingLibrary.create_render_target2d(cap, 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
        cc.set_editor_property("texture_target", rt)
        cc.set_editor_property("fov_angle", fov)
        cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_TONE_CURVE_HDR)
        cc.set_editor_property("capture_every_frame", True)
    print("setup ok")
else:
    import json
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    parts = {p["piece"]: p for p in json.load(open(os.path.join(unreal.Paths.project_dir(), "Art", "Export",
                                                                 "SK_Jerangkong_parts.json"), encoding="utf-8"))["parts"]}
    sk = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == "JKCAP_Rontok").skeletal_mesh_component
    ref = unreal.AnimPoseExtensions.get_reference_pose(sk.get_skinned_asset().get_editor_property("skeleton"))
    for piece, bone in PIVOT_TEST:
        pv = parts[piece]["pivot_ue_cm_boss"]
        bone_ref = unreal.AnimPoseExtensions.get_bone_pose(ref, bone, unreal.AnimPoseSpaces.WORLD)
        bone_now = sk.get_socket_transform(bone, unreal.RelativeTransformSpace.RTS_WORLD)
        piv = unreal.Transform(location=unreal.Vector(*pv))
        t = unreal.MathLibrary.compose_transforms(unreal.MathLibrary.compose_transforms(piv, bone_ref.inverse()), bone_now)
        a = eas.spawn_actor_from_class(unreal.StaticMeshActor, t.translation, t.rotation.rotator())
        a.set_actor_label(f"JKCAP_SM_{piece}")
        a.static_mesh_component.set_static_mesh(EAL.load_asset(f"{JK}/Parts/SM_Jerangkong_{piece}"))
        print(f"SM {piece}: pivot dunia {t.translation} = sendi {bone_now.translation} (selisih "
              f"{(t.translation - bone_now.translation).length():.2f} cm)")
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("JKCAP_cam_"):
            cc = a.capture_component2d
            cc.capture_scene()
            name = lab.replace("JKCAP_cam_", "")
            unreal.RenderingLibrary.export_render_target(world, cc.get_editor_property("texture_target"), OUT, f"jk_cap_{name}.png")
            print("ditulis", os.path.join(OUT, f"jk_cap_{name}.png"))
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("JKCAP_"):
            eas.destroy_actor(a)
    les.save_current_level()                     # level kembali seperti semula (aktor JKCAP_ sudah dihapus)
