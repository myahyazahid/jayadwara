"""M5 (lanjutan): level uji /Game/Hermes/ComboIter2/Maps/Test_Hermes_ComboIter2.

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_level.py
Dijalankan DUA kali (sengaja):
  1. pertama  : duplikat Test_Combat -> sandbox, simpan, lalu berhenti (load_level pada map yang baru diduplikat
                di sesi yang sama membuat UnrealEditor crash — LevelEditor.dll, lihat log 17 Okt 10.06).
  2. kedua    : map sudah ada di disk -> buka, buang instance BP_Aksa lama, taruh BP_Aksa_Hermes di PlayerStart
                (auto possess Player0), simpan level.
Dummy_01 / Dummy_Attacker ikut dari duplikat (tidak disentuh).
"""
import json
import os

import unreal

DEST = "/Game/Hermes/ComboIter2"
MAPS = f"{DEST}/Maps"
SRC_MAP = "/Game/Jayadwara/Maps/Test_Combat"
DST_MAP = f"{MAPS}/Test_Hermes_ComboIter2"
PAWN = f"{DEST}/BP_Aksa_Hermes"
LOG_DIR = os.path.join(unreal.Paths.project_dir(), "Hermes/Art/combo-iter2/Log")

EAL = unreal.EditorAssetLibrary


def log(msg):
    unreal.log(f"[combo_level] {msg}")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[combo_level] PIE sedang jalan — hentikan Play dulu")
        return
    if not EAL.does_asset_exist(PAWN):
        unreal.log_error(f"[combo_level] {PAWN} belum ada — jalankan combo_iter2_setup.py dulu")
        return

    if not EAL.does_asset_exist(DST_MAP):
        if not EAL.does_directory_exist(MAPS):
            EAL.make_directory(MAPS)
        if not EAL.duplicate_asset(SRC_MAP, DST_MAP):
            unreal.log_error(f"[combo_level] gagal menduplikat {SRC_MAP}")
            return
        EAL.save_asset(DST_MAP, only_if_is_dirty=False)
        log(f"map diduplikat & disimpan: {DST_MAP} — jalankan skrip ini sekali lagi untuk mengisi level")
        return

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level(DST_MAP)
    log(f"level dibuka: {DST_MAP}")

    aktor = eas.get_all_level_actors()
    log("isi level: " + str([f"{a.get_actor_label()}({a.get_class().get_name()})" for a in aktor]))

    # instance BP_Aksa dari level proyek masih memakai profil proyek -> buang dari salinan
    dibuang = []
    for a in aktor:
        if isinstance(a, unreal.JDHumanCharacter) or "Aksa" in a.get_class().get_name():
            dibuang.append(a.get_actor_label())
            eas.destroy_actor(a)
    if dibuang:
        log(f"instance lama dibuang dari level salinan: {dibuang}")

    ps = next((a for a in eas.get_all_level_actors() if isinstance(a, unreal.PlayerStart)), None)
    loc = ps.get_actor_location() if ps else unreal.Vector(0, 0, 100)
    rot = ps.get_actor_rotation() if ps else unreal.Rotator(0, 0, 0)
    bp = EAL.load_asset(PAWN)
    pawn = eas.spawn_actor_from_class(bp.generated_class(), loc + unreal.Vector(0, 0, 2), rot)
    pawn.set_actor_label("BP_Aksa_Hermes")
    pawn.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
    pawn.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.DISABLED)
    les.save_current_level()
    log(f"BP_Aksa_Hermes ditaruh di PlayerStart {loc} (auto possess Player0), level disimpan")

    isi = {"level": DST_MAP, "aktor": [f"{a.get_actor_label()}({a.get_class().get_name()})"
                                      for a in eas.get_all_level_actors()],
           "dibuang": dibuang}
    os.makedirs(LOG_DIR, exist_ok=True)
    p = os.path.join(LOG_DIR, "level.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(isi, fh, indent=2, ensure_ascii=False)
    log(f"level.json ditulis: {isi['aktor']}")


main()
