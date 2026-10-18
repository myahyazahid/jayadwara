import unreal

EAL = unreal.EditorAssetLibrary
m = EAL.load_asset("/Game/Hermes/ComboIter2/Montages/AM_Hermes_finisher_02")
print("[N] panjang %.3f s, rate %.2f" % (m.get_play_length(), m.get_editor_property("rate_scale")))

data = m.get_editor_property("notify_tracks")
if not data:
    # fallback: ambil dari sequence
    seq = m.get_editor_property("sequence")
    data = seq.get_editor_property("notify_tracks") if seq else []

for trk in data:
    for n in trk.get_editor_property("notifies"):
        print("[N] notify %-28s @ %.3f s" % (n.get_editor_property("notify_name"), n.get_editor_property("time")))

secs = m.get_editor_property("composite_sections")
for s in secs:
    print("[N] section %s -> %s" % (s.get_editor_property("section_name"), s.get_editor_property("next_section")))
