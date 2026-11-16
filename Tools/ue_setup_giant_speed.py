"""Fase 1 Iterasi 6 — kelincahan raksasa "ala Mebius" (16 Okt 2026, docs/07, docs/23 bagian 5) (Unreal Editor Python).

Butuh: build C++ dengan AJDGiantCharacter::SpeedScaleExponent / GetSpeedScale (16 Okt 2026).
Yang dilakukan (aman diulang; tidak membangun ulang pawn, retarget, atau level):
  BP_Jerangkong          SpeedScaleExponent = 0,5 (boss tetap berat/Froude, cocok dengan BS x sqrt(skala) miliknya)
  BS_Idle_Walk_Run_JD2   sumbu Speed = BlendSpace Mannequin x GetSpeedScale() BP_Jayadwara2 (kaki tetap menapak)
  BS_Idle_Walk_Run_JD    sama, untuk BP_Jayadwara lama (kalau ada)
Lalu jalankan ulang Tools/ue_setup_giant_combo.py: montage combat (blend time ikut GlobalAnimRateScale baru), laju terlihat
1,0, dodge 0,35 s, hit-stop 0,15 s di DA_CombatProfile_Giant.
Mengubah kelincahan nanti: ubah SpeedScaleExponent di Class Defaults BP_Jayadwara2 (0,5 berat … 1,0 animasi normal),
GiantTurnRate (°/s), JumpBoost; lalu jalankan skrip ini + ue_setup_giant_combo.py lagi.
Pakai: python Tools/ue_remote.py Tools/ue_setup_giant_speed.py
"""
import math

import unreal

EAL = unreal.EditorAssetLibrary
SRC_BS = "/Game/Characters/Mannequins/Anims/Unarmed/BS_Idle_Walk_Run"
GIANTS = [   # (BP, BlendSpace raksasa)
    ("/Game/Jayadwara/Characters/Jayadwara2/BP_Jayadwara2", "/Game/Jayadwara/Characters/Jayadwara2/Anims/BS_Idle_Walk_Run_JD2"),
    ("/Game/Jayadwara/Characters/Jayadwara/BP_Jayadwara", "/Game/Jayadwara/Characters/Jayadwara/Anims/BS_Idle_Walk_Run_JD"),
]
JERANGKONG = "/Game/Jayadwara/Characters/Jerangkong/BP_Jerangkong"


def log(msg):
    unreal.log(f"[Jayadwara] {msg}")


def scale_blendspace(path, factor):
    """Sampel & batas sumbu Speed = BS Mannequin x factor (selalu dari sumber, jadi aman diulang)."""
    src = EAL.load_asset(SRC_BS)
    bs = EAL.load_asset(path)
    samples = []
    for s, o in zip(bs.get_editor_property("sample_data"), src.get_editor_property("sample_data")):
        v = o.get_editor_property("sample_value")
        s.set_editor_property("sample_value", unreal.Vector(v.x, v.y * factor, v.z))
        samples.append(s)
    params = []
    for i, p in enumerate(bs.get_editor_property("blend_parameters")):
        if i == 1:   # sumbu 1 = Speed
            p.set_editor_property("max", src.get_editor_property("blend_parameters")[1].get_editor_property("max") * factor)
        params.append(p)
    bs.set_editor_property("blend_parameters", params)
    bs.set_editor_property("sample_data", samples)
    EAL.save_loaded_asset(bs, only_if_is_dirty=False)


def keep_jerangkong_heavy():
    if not EAL.does_asset_exist(JERANGKONG):
        log("BP_Jerangkong tidak ada, dilewati")
        return
    bp = EAL.load_asset(JERANGKONG)
    d = unreal.get_default_object(bp.generated_class())
    d.set_editor_property("speed_scale_exponent", 0.5)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)
    d = unreal.get_default_object(bp.generated_class())
    log(f"BP_Jerangkong: SpeedScaleExponent 0,5 (berat); speed x{d.get_speed_scale():.2f} = sqrt(skala) "
        f"{math.sqrt(d.get_giant_scale()):.2f}")


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[Jayadwara] PIE sedang jalan — hentikan Play dulu")
        return
    keep_jerangkong_heavy()
    for bp_path, bs_path in GIANTS:
        if not (EAL.does_asset_exist(bp_path) and EAL.does_asset_exist(bs_path)):
            log(f"{bp_path.split('/')[-1]} / BlendSpace tidak ada, dilewati")
            continue
        d = unreal.get_default_object(EAL.load_asset(bp_path).generated_class())
        scale, speed = d.get_giant_scale(), d.get_speed_scale()
        scale_blendspace(bs_path, speed)
        log(f"{bp_path.split('/')[-1]}: skala {scale:.2f}, exponent {d.get_editor_property('speed_scale_exponent'):.2f} → "
            f"lari {500 * speed / 100:.0f} m/s, animasi x{speed / scale:.2f}, berbalik {d.get_editor_property('giant_turn_rate'):.0f}°/s; "
            f"{bs_path.split('/')[-1]} Speed x{speed:.2f}")
    log("Selesai. Lanjut: python Tools/ue_remote.py Tools/ue_setup_giant_combo.py")


main()
