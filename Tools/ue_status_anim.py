import unreal

EAL = unreal.EditorAssetLibrary
RAW = "/Game/Hermes/ComboIter2/Mixamo/Raw"
MX = "/Game/Hermes/ComboIter2/Mixamo"

print("[S] === RAW ===")
for p in sorted(EAL.list_assets(RAW, True, False)):
    a = EAL.load_asset(p)
    cls = a.get_class().get_name() if a else "?"
    ex = ""
    if isinstance(a, unreal.AnimSequence):
        ex = " | %.3f s" % a.get_play_length()
    print("[S] %-52s %s%s" % (p.split("/")[-1], cls, ex))

print("[S] === RETARGET (MX) ===")
for p in sorted(EAL.list_assets(MX, True, False)):
    a = EAL.load_asset(p)
    cls = a.get_class().get_name() if a else "?"
    ex = ""
    if isinstance(a, unreal.AnimSequence):
        ex = " | %.3f s" % a.get_play_length()
    print("[S] %-52s %s%s" % (p.split("/")[-1], cls, ex))

print("[S] === MONTAGE ===")
for p in sorted(EAL.list_assets("/Game/Hermes/ComboIter2/Montages", True, False)):
    a = EAL.load_asset(p)
    if isinstance(a, unreal.AnimMontage):
        seq = a.get_editor_property("sequence")
        print("[S] %-30s %.3f s | seq %s (%.3f s)" % (
            p.split("/")[-1], a.get_play_length(),
            seq.get_name() if seq else "-", seq.get_play_length() if seq else 0.0))
