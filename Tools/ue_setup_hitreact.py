"""Fase 1 Iterasi 4 — reaksi kena pukul, poise, soft target + warp (Unreal Editor Python).

Butuh: build C++ Iterasi 4 (UJDGA_HitReact, UJDTargetingComponent, field Hit React/Targeting di UJDCombatProfile),
hasil ue_setup_defense.py (Iterasi 3) dan, untuk raksasa, ue_setup_giant_combo.py.
Pakai: python Tools/ue_remote.py Tools/ue_setup_hitreact.py
Membuat / mengisi ulang (aman diulang):
  Aksa/Anims/Attack/A_Aksa_HitReact_01..02 + Montages/AM_Aksa_HitReact_01..02   dari MM_HitReact_Front_Lgt_01/02 (placeholder)
  Aksa/Anims/Attack/A_Aksa_Stagger + Montages/AM_Aksa_Stagger    disalin ulang dari MM_HitReact_Front_Hvy_01 kalau hilang
  DA_CombatProfile_Human, DA_CombatProfile_Dummy   hit react ringan, stagger, flag Jatuh di finisher berat & hantaman udara
  DA_CombatProfile_Giant    flag Jatuh, warp & pushback x skala (tanpa montage reaksi: belum ada animasi JD2)
  DA_CombatProfile_Dummy    poise pukulan dummy 25 (2 pukulan memecah poise Aksa 50)
  DA_AbilitySet_Aksa/Jayadwara   poise 50, regen poise 20/s setelah 1,5 s
Knockdown & bangun belum punya animasi (Mixamo menyusul): isi KNOCKDOWN/GET_UP lalu jalankan ulang. Kosong = ditahan
di montage stagger selama KnockdownDuration.
"""
import unreal

AKSA = "/Game/Jayadwara/Characters/Aksa"
SEQS = f"{AKSA}/Anims/Attack"
MONTAGES = f"{AKSA}/Anims/Montages"
DATA = "/Game/Jayadwara/Data"
GIANT_BP = "/Game/Jayadwara/Characters/Jayadwara2/BP_Jayadwara2"
HIT_REACT = "/Game/Characters/Mannequins/Anims/Rifle/HitReact"

LIGHT_REACTS = [("A_Aksa_HitReact_01", f"{HIT_REACT}/MM_HitReact_Front_Lgt_01"),
                ("A_Aksa_HitReact_02", f"{HIT_REACT}/MM_HitReact_Front_Lgt_02")]
STAGGER = ("A_Aksa_Stagger", f"{HIT_REACT}/MM_HitReact_Front_Hvy_01")
KNOCKDOWN = None    # ("A_Aksa_Knockdown", "/Game/.../sumber") — Mixamo menyusul
GET_UP = None       # ("A_Aksa_GetUp", "/Game/.../sumber")

# docs/23 bagian 5 (Iterasi 4)
HIT_REACT_VALUES = {"light_react_duration": 0.3, "stagger_duration": 1.2, "knockdown_duration": 1.9, "get_up_duration": 0.7,
                    "reset_poise_after_stagger": True, "hit_react_armor_while_attacking": False}
PUSHBACK = {"stagger_pushback": 300.0, "knockdown_pushback": 600.0}
WARP = {"soft_target_half_angle": 30.0, "soft_target_angle_weight": 0.5, "warp_duration": 0.1}
WARP_MOVE = {"warp_max_gap": 220.0, "warp_max_slide": 200.0}   # x skala gerak raksasa (skala x 0,6, sama dengan dodge)
WARP_STOP_GAP = 20.0                                            # x skala raksasa (jarak kepalan ke badan)
MOVE_SCALE_FACTOR = 0.6
ATTRIBUTES = {"max_poise": 50.0, "poise_regen_per_second": 20.0, "poise_regen_delay": 1.5}
DUMMY_ATTACK_POISE = 25.0

EAL = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
problems = []


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def fail(msg):
    problems.append(msg)
    unreal.log_error(f"[Jayadwara] {msg}")


def load(path):
    a = EAL.load_asset(path)
    if a is None:
        fail(f"aset tidak ada: {path}")
    return a


def make_react_montage(entry, blend_in=0.05, blend_out=0.2):
    """Salin sumber ke Aksa/Anims/Attack (sekali), lalu montage AM_<nama tanpa A_> dibuat ulang tiap jalan."""
    if not entry:
        return None
    seq_name, source = entry
    seq_path = f"{SEQS}/{seq_name}"
    if not EAL.does_asset_exist(seq_path):
        if not EAL.does_asset_exist(source):
            fail(f"sumber animasi tidak ada: {source}")
            return None
        EAL.duplicate_asset(source, seq_path)
        log(f"{seq_name} disalin dari {source.rsplit('/', 1)[1]}")
    name = "AM_" + seq_name[2:]
    path = f"{MONTAGES}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", load(seq_path))
    m = asset_tools.create_asset(name, MONTAGES, unreal.AnimMontage, f)
    for prop, t in (("blend_in", blend_in), ("blend_out", blend_out)):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t)
        m.set_editor_property(prop, b)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    log(f"{name} dari {seq_name}")
    return m


def mark_knockdown(prof):
    """Finisher berat & hantaman udara = Jatuh (docs/07 "Reaksi kena pukul"). Struct salinan, jadi ditulis balik."""
    fins = []
    for s in prof.get_editor_property("heavy_finishers"):
        if s.get_editor_property("montage"):
            s.set_editor_property("knockdown", True)
        fins.append(s)
    prof.set_editor_property("heavy_finishers", fins)
    slam = prof.get_editor_property("air_slam")
    if slam.get_editor_property("montage"):
        slam.set_editor_property("knockdown", True)
    prof.set_editor_property("air_slam", slam)
    return len([s for s in fins if s.get_editor_property("knockdown")])


def fill_reactions(prof, lights, stagger, knockdown, get_up, scale=1.0, move_scale=1.0):
    for k, v in HIT_REACT_VALUES.items():
        prof.set_editor_property(k, v)
    for k, v in PUSHBACK.items():
        prof.set_editor_property(k, v * move_scale)
    for k, v in WARP.items():
        prof.set_editor_property(k, v)
    for k, v in WARP_MOVE.items():
        prof.set_editor_property(k, v * move_scale)
    prof.set_editor_property("warp_stop_gap", WARP_STOP_GAP * scale)
    if lights is not None:
        prof.set_editor_property("hit_react_montages", lights)
        prof.set_editor_property("stagger_montage", stagger)
        prof.set_editor_property("knockdown_montage", knockdown)
        prof.set_editor_property("get_up_montage", get_up)


def set_attributes(name):
    aset = load(f"{DATA}/{name}")
    if not aset:
        return
    attrs = aset.get_editor_property("attributes")
    for k, v in ATTRIBUTES.items():
        attrs.set_editor_property(k, v)
    aset.set_editor_property("attributes", attrs)
    EAL.save_loaded_asset(aset, only_if_is_dirty=False)
    log(f"{name}: poise 50, regen 20/s setelah 1,5 s")


def setup_human(lights, stagger, knockdown, get_up):
    prof = load(f"{DATA}/DA_CombatProfile_Human")
    if not prof:
        return
    fill_reactions(prof, lights, stagger, knockdown, get_up)
    n = mark_knockdown(prof)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log(f"DA_CombatProfile_Human: {len(lights)} reaksi ringan, stagger 1,2 s, {n} finisher + hantaman udara = Jatuh, warp 2,2 m")
    set_attributes("DA_AbilitySet_Aksa")


def setup_dummy(lights, stagger, knockdown, get_up):
    prof = load(f"{DATA}/DA_CombatProfile_Dummy")
    if not prof:
        return
    fill_reactions(prof, lights, stagger, knockdown, get_up)
    combo = []
    for s in prof.get_editor_property("light_combo"):
        s.set_editor_property("poise_damage", DUMMY_ATTACK_POISE)
        combo.append(s)
    prof.set_editor_property("light_combo", combo)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log(f"DA_CombatProfile_Dummy: reaksi ringan + stagger, poise pukulan {DUMMY_ATTACK_POISE:.0f}")


def setup_giant():
    prof = EAL.load_asset(f"{DATA}/DA_CombatProfile_Giant")
    bp = EAL.load_asset(GIANT_BP)
    if not prof or not bp:
        log("DA_CombatProfile_Giant / BP_Jayadwara2 belum ada, raksasa dilewati")
        return
    scale = unreal.get_default_object(bp.generated_class()).get_giant_scale()
    move_scale = scale * MOVE_SCALE_FACTOR
    fill_reactions(prof, None, None, None, None, scale, move_scale)
    n = mark_knockdown(prof)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log(f"DA_CombatProfile_Giant: {n} finisher + hantaman udara = Jatuh, warp {WARP_MOVE['warp_max_gap'] * move_scale / 100:.0f} m")
    set_attributes("DA_AbilitySet_Jayadwara")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara] PIE sedang jalan — hentikan Play dulu")
        return
    if not hasattr(unreal, "JDGA_HitReact"):
        unreal.log_error("[Jayadwara] C++ Iterasi 4 belum ter-build (JDGA_HitReact tidak ada)")
        return
    lights = [m for m in (make_react_montage(e) for e in LIGHT_REACTS) if m]
    stagger = make_react_montage(STAGGER, blend_out=0.25)
    knockdown = make_react_montage(KNOCKDOWN, blend_out=0.1)
    get_up = make_react_montage(GET_UP, blend_in=0.1)
    setup_human(lights, stagger, knockdown, get_up)
    setup_dummy(lights, stagger, knockdown, get_up)
    setup_giant()
    if problems:
        unreal.log_warning(f"[Jayadwara] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("setup Iterasi 4 selesai: Play di Test_Combat, JD.Debug.Target 1 untuk lihat soft target")


main()
