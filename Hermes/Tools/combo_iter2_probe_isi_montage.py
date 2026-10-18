"""Cetak isi dalam AM_Hermes_air_slam: segmen, section, pengaturan blend.

Dipakai untuk memastikan montage benar-benar memutar seluruh klip 0,633 s atau
hanya sebagian (mis. segmen berhenti di 0,459).

Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_probe_isi_montage.py
"""
import unreal

m = unreal.load_asset("/Game/Hermes/ComboIter2/Montages/AM_Hermes_air_slam")


def coba(label, fn):
    try:
        print(f"{label}: {fn()}")
    except Exception as e:
        print(f"{label}: ERR {type(e).__name__} {e}")


print("panjang", m.get_play_length(), "seq", m.get_editor_property("sequence_length"))
coba("auto_blend_out", lambda: m.get_editor_property("enable_auto_blend_out"))
coba("blend_in", lambda: m.get_editor_property("blend_in").get_editor_property("blend_time"))
coba("blend_out", lambda: m.get_editor_property("blend_out").get_editor_property("blend_time"))
coba("blendout_trig", lambda: m.get_editor_property("blend_out_trigger_time"))
coba("rate_scale", lambda: m.get_editor_property("rate_scale"))
coba("sections", lambda: [(s.get_editor_property("section_name"), s.get_editor_property("link_time"))
                          for s in m.get_editor_property("composite_sections")])
coba("tracks_len", lambda: len(m.get_editor_property("slot_anim_tracks")))


def segmen():
    keluar = []
    for t in m.get_editor_property("slot_anim_tracks"):
        keluar.append("slot=" + str(t.get_editor_property("slot_name")))
        for s in t.get_editor_property("anim_track").get_editor_property("anim_segments"):
            a = s.get_editor_property("anim_reference").get_editor_property("anim_sequence")
            keluar.append("  %s start=%.3f end=%.3f rate=%.2f" % (
                a.get_name() if a else "-",
                s.get_editor_property("anim_start_time"),
                s.get_editor_property("anim_end_time"),
                s.get_editor_property("anim_play_rate")))
    return keluar


coba("segmen", segmen)
