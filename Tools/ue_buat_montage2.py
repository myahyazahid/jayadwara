import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

MX = "/Game/Hermes/ComboIter2/Mixamo"
MONT = "/Game/Hermes/ComboIter2/Montages"
TRACK = "Combat"
BLEND_IN, BLEND_OUT = 0.05, 0.22

# peran -> daftar jendela hit (mulai, durasi, tulang, new_hit)
JOBS = {
    # puncak tendangan baru: foot_r @0,517 s dan @0,817 s
    "finisher_02": [(0.40, 0.24, "foot_r", False), (0.70, 0.24, "foot_r", True)],
    # air_slam: damage dari area saat mendarat, tanpa jendela hit
    "air_slam": [],
}

for peran, hits in JOBS.items():
    seq = EAL.load_asset("%s/A_Aksa_Mx_%s" % (MX, peran))
    if not isinstance(seq, unreal.AnimSequence):
        print("[M] %s: sequence tidak ada" % peran)
        continue
    path = "%s/AM_Hermes_%s" % (MONT, peran)
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset("AM_Hermes_%s" % peran, MONT, unreal.AnimMontage, f)
    for prop, t in (("blend_in", BLEND_IN), ("blend_out", BLEND_OUT)):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t)
        m.set_editor_property(prop, b)
    for start, dur, socket, new_hit in hits:
        ev = AL.add_animation_notify_state_event(m, TRACK, start, dur, unreal.JDAnimNotifyState_HitWindow)
        ev.set_editor_property("socket_name", socket)
        ev.set_editor_property("new_hit", new_hit)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    print("[M] AM_Hermes_%s dibuat: %.3f s, %d jendela hit" % (peran, m.get_play_length(), len(hits)))
