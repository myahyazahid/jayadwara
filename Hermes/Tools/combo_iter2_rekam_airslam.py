"""Perekam sesi Play: catat pukulan udara (LMB) dan hantaman udara (E).

Dipakai untuk dua pertanyaan sekaligus:
  1. "lompat + LMB malah nambah tinggi" -> apakah z naik setelah montage mulai?
  2. "lompat + E" -> apakah montage hantaman masih selesai sebelum mendarat?

Cara pakai:
  1. python Tools/ue_remote.py Hermes/Tools/combo_iter2_rekam_airslam.py
  2. di editor: Play (PIE), lakukan lompat + LMB 2x, lalu lompat + E 2x
  3. berhenti Play, baca Log/rekam_airslam6.log

Tiap sesi ditulis sebagai blok: baris MULAI (aksi, z, posisi montage), satu baris per
frame (dt, z, vz, posisi montage, mode gerak), ditutup baris AKHIR + ringkasan
(naik berapa cm dari mulai, z puncak, posisi montage terakhir). Tidak menyentuh aset.
"""
import os

import unreal

LOG = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()),
                   "Hermes", "Art", "combo-iter2", "Log", "rekam_airslam6.log")
MONT = {
    "LMB": unreal.load_asset("/Game/Hermes/ComboIter2/Montages/AM_Hermes_air"),
    "E": unreal.load_asset("/Game/Hermes/ComboIter2/Montages/AM_Hermes_air_slam"),
}

ST = {"aksi": None, "rows": [], "sesi": 0, "h": None, "z0": 0.0, "zmax": 0.0, "pos_max": 0.0}


def tulis(teks):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(teks)


def tick(dt):
    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if not world:
            return
        ch = unreal.GameplayStatics.get_player_pawn(world, 0)
        if not ch:
            return
        anim = ch.get_editor_property("mesh").get_anim_instance()
        if not anim:
            return

        aksi = None
        pos = -1.0
        for nama, mont in MONT.items():
            if mont and anim.montage_is_playing(mont):
                aksi = nama
                pos = anim.montage_get_position(mont)
                break

        z = ch.get_actor_location().z
        mv = ch.get_editor_property("character_movement")

        if aksi and not ST["aksi"]:
            ST["aksi"] = aksi
            ST["sesi"] += 1
            ST["z0"] = z
            ST["zmax"] = z
            ST["pos_max"] = pos
            ST["rows"] = ["S%d MULAI %s dt=%.3f z=%.1f" % (ST["sesi"], aksi, dt, z)]

        if ST["aksi"]:
            ST["zmax"] = max(ST["zmax"], z)
            ST["pos_max"] = max(ST["pos_max"], pos)
            ST["rows"].append("S%d %s dt=%.3f z=%6.1f vz=%6.1f pos=%.3f mode=%s" % (
                ST["sesi"], ST["aksi"], dt, z, mv.velocity.z, pos,
                mv.get_editor_property("movement_mode")))
            if not aksi:
                ST["rows"].append("S%d AKHIR %s: naik %.1f cm dari mulai, z puncak %.1f, "
                                  "posisi montage terakhir %.3f" % (
                                      ST["sesi"], ST["aksi"], ST["zmax"] - ST["z0"],
                                      ST["zmax"], ST["pos_max"]))
                tulis("\n".join(ST["rows"]) + "\n---\n")
                ST["aksi"] = None
    except Exception as e:
        tulis("ERR %s\n" % e)


if os.path.exists(LOG):
    os.remove(LOG)
tulis("perekam aktif\n")
ST["h"] = unreal.register_slate_post_tick_callback(tick)
print("perekam aktif ->", LOG)
