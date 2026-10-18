"""Putar AM_Hermes_air_slam langsung di mesh (tanpa ability), catat posisinya.

Tujuan: memisahkan dua kemungkinan penyebab montage hantaman udara berhenti di
pos 0,459 — montage/asetnya sendiri rusak, atau ada yang menghentikannya
(ability / AnimBlueprint). Kalau di sini montage jalan penuh sampai 0,633,
berarti asetnya sehat.

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_probe_montage.py
Hasil -> Log/probe_montage.txt
"""
import os

import unreal

LOG = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()),
                   "Hermes", "Art", "combo-iter2", "Log", "probe_montage.txt")
MONT = unreal.load_asset("/Game/Hermes/ComboIter2/Montages/AM_Hermes_air_slam")
ST = {"mulai": False, "rows": [], "h": None, "t": 0.0}


def tulis(s):
    with open(LOG, "w", encoding="utf-8") as f:
        f.write(s)


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
        if not ST["mulai"]:
            ST["mulai"] = True
            anim.montage_play(MONT, 1.45)
            ST["rows"].append("MULAI montage_play rate 1.45, panjang %.3f" % MONT.get_play_length())
        ST["t"] += dt
        jalan = anim.montage_is_playing(MONT)
        pos = anim.montage_get_position(MONT) if jalan else -1.0
        ST["rows"].append("t=%.3f pos=%.3f jalan=%s" % (ST["t"], pos, "YA" if jalan else "-"))
        if not jalan or ST["t"] > 2.0:
            ST["rows"].append("AKHIR: pos_terakhir=%.3f" % pos)
            tulis("\n".join(ST["rows"]) + "\n")
            unreal.unregister_slate_post_tick_callback(ST["h"])
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception as e:
        ST["rows"].append("ERR %s" % e)


if os.path.exists(LOG):
    os.remove(LOG)
tulis("menunggu PIE...\n")
ST["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
