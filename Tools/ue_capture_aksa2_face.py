"""Cek visual 8 morph wajah Aksa2 di PIE (HighResShot): CameraActor sementara 65 cm di depan wajah, FOV 20.

Alasan PIE: SceneCapture/HighResShot di viewport editor tidak merender andal saat jendela editor di latar belakang.
Editor terbuka, level uji = Test_Combat_Aksa2 (pawn BP_Aksa2). Tahap (satu panggilan ue_remote tiap tahap; PIE jalan di antaranya):
  STAGE='cam'    pasang CameraActor `AK2CAM` di depan PlayerStart (level tidak disimpan)
  (panggil sendiri editor_request_begin_play, tunggu PIE)
  STAGE='view'   jadikan AK2CAM view target PIE
  STAGE='morph'  MORPH='ak_smile' / None: set morph pawn + HighResShot -> Saved/Screenshots/WindowsEditor/aksa2_face_<morph>.png
  (editor_request_end_play)
  STAGE='clean'  hapus AK2CAM
Semua sekaligus: bash Tools/ue_capture_aksa2_face.sh
"""
import math

import unreal

STAGE = globals().get("STAGE", "cam")
MORPH = globals().get("MORPH")
ALL = ["ak_blink_L", "ak_blink_R", "ak_smile", "ak_angry", "ak_mouth_open", "ak_brow_up", "ak_wince", "ak_sad"]
HEAD_Z, DIST, FOV = 161.5, 65.0, 20.0

if STAGE in ("cam", "clean"):
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == "AK2CAM":
            eas.destroy_actor(a)
    if STAGE == "cam":
        start = next(a for a in eas.get_all_level_actors() if isinstance(a, unreal.PlayerStart))
        loc, yaw = start.get_actor_location(), start.get_actor_rotation().yaw
        r = math.radians(yaw)
        pos = unreal.Vector(loc.x + math.cos(r) * DIST, loc.y + math.sin(r) * DIST, HEAD_Z)
        cam = eas.spawn_actor_from_class(unreal.CameraActor, pos, unreal.Rotator(0, 0, yaw + 180.0))
        cam.set_actor_label("AK2CAM")
        cam.get_editor_property("camera_component").set_editor_property("field_of_view", FOV)
        print("kamera di", pos, "yaw", yaw + 180.0, "| PlayerStart", loc)
    else:
        print("kamera sementara dihapus")
else:
    w = unreal.EditorLevelLibrary.get_pie_worlds(False)[0]
    if STAGE == "view":
        cam = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.CameraActor) if a.get_actor_label() == "AK2CAM")
        unreal.GameplayStatics.get_player_controller(w, 0).set_view_target_with_blend(cam, 0.0)
        print("view target = AK2CAM")
    elif STAGE == "morph":
        m = unreal.GameplayStatics.get_player_pawn(w, 0).get_editor_property("mesh")
        for n in ALL:
            m.set_morph_target(n, 1.0 if n == MORPH else 0.0, True)
        unreal.SystemLibrary.execute_console_command(w, f"HighResShot 1024x1024 filename=aksa2_face_{MORPH or 'netral'}")
        print("shot:", MORPH or "netral")
