"""Cek visual Aksa di editor: barisan karakter (Manny pembanding + SK_Aksa) dengan animasi Mannequin dibekukan, lalu screenshot.

Meletakkan actor sementara berlabel `AKCHK_*` + kamera di ketinggian 100 m di level yang sedang terbuka (jauh dari isi level),
memindahkan kamera viewport editor ke sana dan mengambil HighResShot (kamera lama disimpan di Saved/aksa_check_cam.json dan
dipulihkan saat CLEAN). Hapus actor sementara + pulihkan kamera dengan: python Tools/ue_remote.py -c "CLEAN=True; exec(open(r'<path ini>').read())"
Pakai: python Tools/ue_remote.py Tools/ue_check_aksa.py   (variabel global opsional LABEL, ITEMS, CLEAN lewat -c)
Screenshot: <project>/Saved/Screenshots/<LABEL>.png (asinkron, muncul setelah beberapa frame; editor harus terlihat).
"""
import json
import os

import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
CAM_FILE = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "aksa_check_cam.json")
EAL = unreal.EditorAssetLibrary
ANIM = "/Game/Characters/Mannequins/Anims/Unarmed/"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
AKSA = "/Game/Jayadwara/Characters/Aksa/Mesh/SK_Aksa"
BASE_Z = 10000.0

if globals().get("CLEAN"):
    n = 0
    for a in EAS.get_all_level_actors():
        if a.get_actor_label().startswith("AKCHK_"):
            EAS.destroy_actor(a)
            n += 1
    print(f"actor sementara dihapus: {n}")
    if os.path.exists(CAM_FILE):
        d = json.load(open(CAM_FILE))
        UES.set_level_viewport_camera_info(unreal.Vector(*d["loc"]), unreal.Rotator(*d["rot"]))
        os.remove(CAM_FILE)
        print("kamera viewport dipulihkan")
else:
    label = globals().get("LABEL") or "aksa_check"
    items = globals().get("ITEMS") or [(MANNY, "Attack/MM_Attack_01", 0.30), (AKSA, "Attack/MM_Attack_01", 0.30),
                                       (AKSA, "Walk/MF_Unarmed_Walk_Fwd", 0.35), (AKSA, "MM_Idle", 0.0)]
    for a in EAS.get_all_level_actors():                                  # bersihkan sisa uji sebelumnya
        if a.get_actor_label().startswith("AKCHK_"):
            EAS.destroy_actor(a)
    spacing = 100.0
    y0 = -spacing * (len(items) - 1) / 2
    for i, (mesh_path, anim, t) in enumerate(items):
        mesh = EAL.load_asset(mesh_path)
        seq = EAL.load_asset(ANIM + anim)
        if mesh is None or seq is None:
            print("aset tidak ada:", mesh_path, anim)
            continue
        a = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, y0 + i * spacing, BASE_Z), unreal.Rotator(0, 0, -90))
        a.set_actor_label(f"AKCHK_{i}_{mesh.get_name()}")
        c = a.skeletal_mesh_component
        c.set_skeletal_mesh_asset(mesh)
        c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        if hasattr(c, "set_update_animation_in_editor"):
            c.set_update_animation_in_editor(True)
        c.set_animation(seq)
        if hasattr(c, "override_animation_data"):
            c.override_animation_data(seq, False, True, t, 0.0)          # main dengan laju 0 = beku di waktu t
        c.set_position(t, False)
        for fn in ("tick_animation", "refresh_bone_transforms"):
            if hasattr(c, fn):
                getattr(c, fn)(*((0.0, False) if fn == "tick_animation" else ()))
        print(f"{a.get_actor_label()}  anim={anim}  t={t}")
    if not os.path.exists(CAM_FILE):
        loc, rot = UES.get_level_viewport_camera_info()
        json.dump({"loc": [loc.x, loc.y, loc.z], "rot": [rot.roll, rot.pitch, rot.yaw]}, open(CAM_FILE, "w"))
    UES.set_level_viewport_camera_info(unreal.Vector(650, 0, BASE_Z + 95), unreal.Rotator(0, 0, 180))
    out = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "Screenshots", label + ".png")
    unreal.SystemLibrary.execute_console_command(None, f'HighResShot 1800x700 filename="{out}"')
    print("screenshot diminta ->", out)
