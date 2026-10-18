import unreal

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

MX = "/Game/Hermes/ComboIter2/Mixamo"
MONT = "/Game/Hermes/ComboIter2/Montages"
PROF = "/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes"

seq = EAL.load_asset(MX + "/A_Aksa_Mx_air_slam")
print("[V6] sequence %.3f s" % seq.get_play_length())

nama = "AM_Hermes_air_slam_v6"
path = "%s/%s" % (MONT, nama)
if EAL.does_asset_exist(path):
    EAL.delete_asset(path)
    unreal.SystemLibrary.collect_garbage()

f = unreal.AnimMontageFactory()
f.set_editor_property("source_animation", seq)
m = asset_tools.create_asset(nama, MONT, unreal.AnimMontage, f)
if not m:
    print("[V6] gagal buat montage")
else:
    for prop, t in (("blend_in", 0.06), ("blend_out", 0.20)):
        b = m.get_editor_property(prop)
        if b:
            b.set_editor_property("blend_time", t)
            m.set_editor_property(prop, b)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)

    prof = EAL.load_asset(PROF)
    slam = prof.get_editor_property("air_slam")
    slam.set_editor_property("montage", m)
    prof.set_editor_property("air_slam", slam)
    EAL.save_loaded_asset(prof)

    p2 = EAL.load_asset(PROF)
    m2 = p2.get_editor_property("air_slam").get_editor_property("montage")
    print("[V6] profil air_slam -> %s | %.3f s" % (m2.get_name(), m2.get_play_length()))
