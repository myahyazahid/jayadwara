"""Fase 1 Iterasi 3 — parry tepis: 2 tepisan bergantian, hit-stop parry, percikan, slow-mo, serangan balik (Unreal Editor Python).

Butuh: build C++ parry tepis (UJDCombatProfile::ParryMontages dkk., Effect di JDGameplayCueNotify_Sound), hasil
ue_setup_light_combo.py dan ue_setup_defense.py (Iterasi 2–3).
Pakai: python Tools/ue_remote.py Tools/ue_setup_parry.py
Membuat / mengisi ulang (aman diulang):
  Aksa/Anims/Montages/AM_Aksa_Parry_01, _02   tepisan placeholder dari A_Aksa_Attack_01 (jab) & _03 (hook), tanpa hit
  VFX/NS_Parry_Spark                          salinan template Niagara "burst" bawaan engine (kalau belum ada)
  GC_Parry                                    + Effect NS_Parry_Spark
  DA_CombatProfile_Human                      tepisan, hit-stop parry, slow-mo, shake, serangan balik AM_Aksa_Light_04
  DA_CombatProfile_Giant                      angka rasa parry yang sama (montage tepisan raksasa menyusul)
Animasi placeholder: ganti PARRY_SOURCES dengan animasi tepis Mixamo / hasil mocap Rokoko lalu jalankan ulang.
"""
import unreal

AKSA = "/Game/Jayadwara/Characters/Aksa"
SEQS = f"{AKSA}/Anims/Attack"
MONTAGES = f"{AKSA}/Anims/Montages"
CUES = "/Game/Jayadwara/Abilities/GameplayCues"
DATA = "/Game/Jayadwara/Data"
VFX = "/Game/Jayadwara/VFX"
SPARK = "NS_Parry_Spark"

PARRY_SOURCES = [("AM_Aksa_Parry_01", f"{SEQS}/A_Aksa_Attack_01"),   # tepis luar (placeholder: jab)
                 ("AM_Aksa_Parry_02", f"{SEQS}/A_Aksa_Attack_03")]   # tepis dalam (placeholder: hook)
COUNTER = {"montage": f"{MONTAGES}/AM_Aksa_Light_04", "damage": 25.0, "poise": 30.0, "rate": 1.2}
# Hasil Tools/ue_import_mixamo.py (parry_01/02) menggantikan placeholder; laju tepisan lalu 1,0.
MIXAMO = f"{AKSA}/Anims/Mixamo"

# docs/07 "Parry": beku sesaat -> lambat -> normal. Durasi dalam detik nyata.
FEEL = {"parry_montage_rate": 1.6, "parry_hit_stop_duration": 0.12, "parry_hit_stop_time_dilation": 0.02,
        "parry_slow_mo_duration": 0.35, "parry_slow_mo_time_dilation": 0.35, "parry_camera_shake_scale": 1.5,
        "parry_counter_window": 0.8}

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


def tag(name):
    t = unreal.JDEditorToolsLibrary.make_gameplay_tag(name)
    if name not in t.export_text():
        fail(f"tag tidak terdaftar: {name}")
    return t


def make_montage(name, seq_path, blend_in=0.04, blend_out=0.15):
    """Montage baru tanpa notify (dibuat ulang tiap jalan)."""
    path = f"{MONTAGES}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    seq = load(seq_path)
    if not seq:
        return None
    f = unreal.AnimMontageFactory()
    f.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset(name, MONTAGES, unreal.AnimMontage, f)
    for prop, t in (("blend_in", blend_in), ("blend_out", blend_out)):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t)
        m.set_editor_property(prop, b)
    EAL.save_loaded_asset(m, only_if_is_dirty=False)
    log(f"{name} dari {seq_path.rsplit('/', 1)[1]}")
    return m


def setup_spark():
    """Percikan: salin template Niagara bawaan engine yang namanya mengandung 'Burst' (ganti/tint di editor kalau mau)."""
    path = f"{VFX}/{SPARK}"
    if EAL.does_asset_exist(path):
        return EAL.load_asset(path)
    candidates = [p.split(".")[0] for p in EAL.list_assets("/Niagara/DefaultAssets/Templates", True, False)
                  if "burst" in p.rsplit("/", 1)[1].lower()]
    systems = [p for p in candidates if isinstance(EAL.load_asset(p), unreal.NiagaraSystem)]
    if not systems:
        fail(f"template Niagara 'Burst' tidak ketemu; buat {path} manual (New Niagara System > template burst) lalu jalankan ulang")
        return None
    src = sorted(systems, key=lambda p: ("omni" not in p.lower(), p))[0]
    spark = EAL.duplicate_asset(src, path)
    log(f"{SPARK} disalin dari {src}")
    return spark


def setup_cue(spark):
    bp = load(f"{CUES}/GC_Parry")
    if not bp or not spark:
        return
    d = unreal.get_default_object(bp.generated_class())
    d.set_editor_property("effect", spark)
    d.set_editor_property("effect_scale", 0.5)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)
    log(f"GC_Parry: + efek {SPARK}")


def fill_feel(prof):
    for k, v in FEEL.items():
        prof.set_editor_property(k, v)
    prof.set_editor_property("parry_camera_shake", unreal.JDCameraShake_Hit.static_class())


def setup_human():
    sources, mixamo = [], 0
    for i, (name, src) in enumerate(PARRY_SOURCES):
        mx = f"{MIXAMO}/A_Aksa_Mx_parry_0{i + 1}"
        if EAL.does_asset_exist(mx):
            src, mixamo = mx, mixamo + 1
        sources.append((name, src))
    montages = [m for m in (make_montage(n, s) for n, s in sources) if m]
    if mixamo == len(PARRY_SOURCES):
        FEEL["parry_montage_rate"] = 1.0
    prof = load(f"{DATA}/DA_CombatProfile_Human")
    if not prof:
        return
    fill_feel(prof)
    prof.set_editor_property("parry_montages", montages)
    counter = load(COUNTER["montage"])
    if counter:
        s = unreal.JDAttackStep()
        s.set_editor_property("montage", counter)
        s.set_editor_property("damage", COUNTER["damage"])
        s.set_editor_property("poise_damage", COUNTER["poise"])
        s.set_editor_property("play_rate", COUNTER["rate"])
        s.set_editor_property("hit_cue", tag("GameplayCue.Hit.Heavy"))
        prof.set_editor_property("parry_counter_attack", s)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log(f"DA_CombatProfile_Human: {len(montages)} tepisan, hit-stop 0,12 s, slow-mo 0,35 s x0,35, serangan balik 0,8 s")


def setup_giant():
    path = f"{DATA}/DA_CombatProfile_Giant"
    if not EAL.does_asset_exist(path):
        log("DA_CombatProfile_Giant belum ada, dilewati")
        return
    prof = EAL.load_asset(path)
    fill_feel(prof)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)
    log("DA_CombatProfile_Giant: angka rasa parry (tanpa montage tepisan & serangan balik khusus)")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara] PIE sedang jalan — hentikan Play dulu")
        return
    try:
        unreal.get_default_object(unreal.JDCombatProfile.static_class()).get_editor_property("parry_montages")
    except Exception:
        unreal.log_error("[Jayadwara] C++ parry tepis belum ter-build (UJDCombatProfile::ParryMontages tidak ada)")
        return
    setup_cue(setup_spark())
    setup_human()
    setup_giant()
    if problems:
        unreal.log_warning(f"[Jayadwara] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    else:
        log("setup parry tepis selesai")


main()
