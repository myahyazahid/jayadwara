import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

MX = "/Game/Hermes/ComboIter2/Mixamo"
MONT = "/Game/Hermes/ComboIter2/Montages"
PROF = "/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes"
TRACK = "Combat"
BLEND_IN, BLEND_OUT = 0.05, 0.22

JOBS = {
    "finisher_02": [(0.40, 0.24, "foot_r", False), (0.70, 0.24, "foot_r", True)],
    "air_slam": [],
}

baru = {}
for peran, hits in JOBS.items():
    seq = EAL.load_asset("%s/A_Aksa_Mx_%s" % (MX, peran))
    if not isinstance(seq, unreal.AnimSequence):
        print("[V] %s: sequence tidak ada" % peran)
        continue
    nama = "AM_Hermes_%s_v2" % peran
    path = "%s/%s" % (MONT, nama)
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
        unreal.SystemLibrary.collect_garbage()
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset(nama, MONT, unreal.AnimMontage, f)
    if not m:
        print("[V] %s: gagal buat montage" % peran)
        continue
    for prop, t in (("blend_in", BLEND_IN), ("blend_out", BLEND_OUT)):
        b = m.get_editor_property(prop)
        if b:
            b.set_editor_property("blend_time", t)
            m.set_editor_property(prop, b)
    # track notify harus ada dulu sebelum event bisa ditambah
    nama_track = [str(n) for n in AL.get_animation_notify_track_names(m)]
    if TRACK in nama_track:
        AL.remove_animation_notify_events_by_track(m, TRACK)
    elif hits:
        AL.add_animation_notify_track(m, TRACK, unreal.LinearColor(1.0, 0.3, 0.2, 1.0))
    for start, dur, socket, new_hit in hits:
        ev = AL.add_animation_notify_state_event(m, TRACK, start, dur, unreal.JDAnimNotifyState_HitWindow)
        ev.set_editor_property("socket_name", socket)
        ev.set_editor_property("new_hit", new_hit)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    baru[peran] = m
    print("[V] %s: %.3f s, %d hit window" % (nama, m.get_play_length(), len(hits)))

# arahkan profil combat ke montage baru
prof = EAL.load_asset(PROF)
if prof and len(baru) == 2:
    fins = list(prof.get_editor_property("heavy_finishers"))
    s = fins[1]
    s.set_editor_property("montage", baru["finisher_02"])
    s.set_editor_property("play_rate", 1.25)
    fins[1] = s
    prof.set_editor_property("heavy_finishers", fins)

    slam = prof.get_editor_property("air_slam")
    slam.set_editor_property("montage", baru["air_slam"])
    prof.set_editor_property("air_slam", slam)
    EAL.save_loaded_asset(prof)

    p2 = EAL.load_asset(PROF)
    f2 = list(p2.get_editor_property("heavy_finishers"))[1]
    sl2 = p2.get_editor_property("air_slam")
    mf = f2.get_editor_property("montage")
    ms = sl2.get_editor_property("montage")
    print("[V] profil: finisher_02 -> %s @%.2f (%.2f s) | air_slam -> %s (%.2f s)" % (
        mf.get_name() if mf else "-", f2.get_editor_property("play_rate"),
        mf.get_play_length() if mf else 0.0,
        ms.get_name() if ms else "-", ms.get_play_length() if ms else 0.0))
else:
    print("[V] profil tidak diubah (montage belum lengkap)")
