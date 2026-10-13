"""Jubah Jayadwara2 (docs/26 J1c) — probe simulasi rantai di Simulate-In-Editor lewat remote (tanpa input pemain).

Tahap (PROBE_STAGE diset sebelum exec; tiap panggilan remote = frame editor berbeda):
  place : taruh BP_Jayadwara2 (label JCPROBE) PROBE_HEIGHT cm di atas lantai di level editor (sebelum start).
  start : mulai Simulate (aktor uji tersalin ke world Simulate dan jatuh bebas).
  read  : cetak waktu, kecepatan z aktor, FPS kasar, dan offset ujung tiap rantai (cape_*_06) relatif terhadap spine_05
          dalam ruang aktor (cm; +Z = atas). Diam vs jatuh: dz positif = jubah terangkat.
  stop  : hentikan Simulate.
Catatan: editor di latar belakang bisa berjalan beberapa fps; node mereset simulasi bila jeda frame > 0,25 s.
"""
import time

import unreal

STAGE = globals().get("PROBE_STAGE", "read")
J2 = "/Game/Jayadwara/Characters/Jayadwara2"
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
CHAINS = ["c", "l", "r", "fl", "fr"]


def game_world():
    return ues.get_game_world()


if STAGE == "place":
    # aktor uji di level editor (ikut tersalin ke world Simulate); label JCPROBE, dihapus di 'stop'
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("JCPROBE"):
            eas.destroy_actor(a)
    h = float(globals().get("PROBE_HEIGHT", 40000.0))
    bp = unreal.EditorAssetLibrary.load_asset(f"{J2}/BP_Jayadwara2")
    a = eas.spawn_actor_from_class(bp.generated_class(), unreal.Vector(9000, 0, h), unreal.Rotator(roll=0, pitch=0, yaw=180))
    a.set_actor_label("JCPROBE")
    a.tags = ["JCPROBE"]
    print("spawn", a.get_name(), "z", round(a.get_actor_location().z))
elif STAGE == "start":
    les.editor_play_simulate()
    print("simulate dimulai")
elif STAGE == "stop":
    les.editor_request_end_play()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("JCPROBE"):
            eas.destroy_actor(a)
    print("simulate dihentikan, aktor uji dihapus (level tidak disimpan)")
else:
    w = game_world()
    if w is None:
        raise RuntimeError("tidak ada game world (jalankan PROBE_STAGE='start' dulu)")
    actors = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
    probe = next((a for a in actors if a.get_actor_label().startswith("JCPROBE") or "JCPROBE" in a.tags), None)
    if STAGE == "spawn":
        raise RuntimeError("spawn dilakukan di level editor SEBELUM start (PROBE_STAGE='place')")
    else:
        if probe is None:
            raise RuntimeError("aktor JCPROBE tidak ada")
        cape = next(c for c in probe.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name().startswith("Cape"))
        body = probe.mesh
        tf = probe.get_actor_transform()
        sp = tf.inverse_transform_location(body.get_socket_location("spine_05"))
        offs = {}
        for c in CHAINS:
            p = tf.inverse_transform_location(cape.get_socket_location(f"cape_{c}_06"))
            offs[c] = (round(p.x - sp.x), round(p.z - sp.z))
        v = probe.get_velocity()
        print(f"t={time.time():.2f} frame={unreal.SystemLibrary.get_frame_count()} dt~{unreal.GameplayStatics.get_world_delta_seconds(w):.3f} "
              f"vz={v.z:.0f} z={probe.get_actor_location().z:.0f} ujung rantai (x maju, z) rel. spine_05: {offs}")
