"""Ukur waktu di udara vs posisi montage air_slam, langsung di PIE (combo iterasi 2).

Jawab pertanyaan: "kenapa tendangan baru setengah tapi sudah mendarat".
Mulai PIE, tunggu level tenang, lompat, tembak ability pukulan berat lewat ASC
(meniru tombol E), lalu catat tiap frame: jam game, tinggi badan, kecepatan Z,
posisi montage. Semua dicatat di memori lalu ditulis sekali di akhir supaya
pencatatan tidak membuat frame stall (percobaan pertama salah karena itu).
Hasil -> Log/probe_pie.txt

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_probe_pie.py
"""
import os

import unreal

LOG = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()),
                   "Hermes", "Art", "combo-iter2", "Log", "probe_pie.txt")
MONT = "/Game/Hermes/ComboIter2/Montages/AM_Hermes_air_slam"
TENANG = 2.0        # detik menunggu setelah PIE mulai sebelum lompat
JEDA_TEKAN = 0.35   # tekan LMB saat masih naik

ST = {"t_mulai": None, "t0": None, "fired": False, "rows": [], "h": None, "akhir": ""}


def tulis(teks):
    with open(LOG, "w", encoding="utf-8") as f:
        f.write(teks)


def selesai():
    tulis("\n".join(ST["rows"]) + "\n" + ST["akhir"] + "\n")
    unreal.unregister_slate_post_tick_callback(ST["h"])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        world = ues.get_game_world()
        if not world:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if ST["t_mulai"] is None:
            ST["t_mulai"] = now
            return
        if now - ST["t_mulai"] < TENANG:
            return
        ch = unreal.GameplayStatics.get_player_pawn(world, 0)
        if not ch:
            return
        mv = ch.get_editor_property("character_movement")
        if ST["t0"] is None:
            ST["t0"] = now
            ch.jump()
            ST["rows"].append("L0 lompat t=0.000 z=%.1f" % ch.get_actor_location().z)
        t = now - ST["t0"]

        if not ST["fired"] and t >= JEDA_TEKAN:
            ST["fired"] = True
            asc = ch.get_component_by_class(unreal.AbilitySystemComponent)
            if not asc:
                ps = unreal.GameplayStatics.get_player_state(world, 0)
                asc = ps.get_component_by_class(unreal.AbilitySystemComponent) if ps else None
            ok = asc.try_activate_ability_by_class(unreal.JDGA_HeavyAttack) if asc else "asc-kosong"
            ST["rows"].append("L1 tekan E t=%.3f z=%.1f vz=%.1f ok=%s" % (
                t, ch.get_actor_location().z, mv.velocity.z, ok))

        mont = unreal.load_asset(MONT)
        anim = ch.get_editor_property("mesh").get_anim_instance()
        pos = -1.0
        try:
            if anim.montage_is_playing(mont):
                pos = anim.montage_get_position(mont)
        except Exception:
            pass
        z = ch.get_actor_location().z
        akt = []
        try:
            asc2 = ch.get_component_by_class(unreal.AbilitySystemComponent)
            kont = asc2.get_editor_property('activatable_abilities')
            items = kont.get_editor_property('items')
            for spec in items:
                if spec.is_active():
                    akt.append(spec.get_editor_property('ability').get_name())
        except Exception as e:
            akt = ["?" + type(e).__name__ + ":" + str(e)[:70]]
        ST["rows"].append("L2 t=%.3f z=%6.1f vz=%6.1f pos=%.3f aktif=%s" % (
            t, z, mv.velocity.z, pos, ",".join(akt) or "-"))

        if t > 0.05 and mv.is_moving_on_ground() and ST.get("t_land") is None:
            ST["t_land"] = t
            ST["pos_land"] = pos
            ST["rows"].append("L3 MENDARAT t=%.3f pos_montage=%.3f" % (t, pos))
        if ST.get("t_land") is not None and t > ST["t_land"] + 1.2:
            ST["akhir"] = ("L4 setelah mendarat 1.2 s: pos_terakhir=%.3f (mendarat di pos %.3f)"
                           % (pos, ST["pos_land"]))
            selesai()
        elif t > 3.5:
            ST["akhir"] = "L3 BATAS WAKTU t=%.3f pos=%.3f" % (t, pos)
            selesai()
    except Exception as e:
        ST["rows"].append("ERR %s" % e)


if os.path.exists(LOG):
    os.remove(LOG)
tulis("menunggu PIE...\n")
ST["h"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
