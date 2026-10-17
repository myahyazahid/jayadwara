"""combo iterasi 2 - penyetelan rasa combo (umpan balik developer M6).

Masalah yang dilaporkan: "setelah memukul gerakannya tidak berlanjut, terasa kaku/reset".

Sebabnya (dibaca dari kode, bukan dugaan):
  * Jendela combo lama dibuka di 0,62 / 0,70 / 1,02 s, yaitu SETELAH hantaman selesai.
    Tekanan yang wajar (spam ringan) jatuh sebelum jendela -> ditolak buffer 0,2 s
    (JDGA_LightAttack.cpp TryAdvanceCombo baris 319) -> montage diputar sampai habis
    (2,0-2,3 s, termasuk recovery kembali ke pose idle) -> baru pukulan berikutnya dari frame 0.
    Itu yang terlihat sebagai "reset".
  * Klip Mixamo utuh: wind-up 0,43 s sebelum hantaman, recovery 1,5 s sesudahnya.
    Placeholder Mannequin dulu hanya ~1 s dengan hantaman di 0,4 s.

Yang diubah (semua di sandbox /Game/Hermes/ComboIter2):
  1. Jendela combo ditaruh di 0,55 s TERAKHIR klip (bukan di hantaman).
     Umpan balik M6 kedua: "klik cepat jangan sampai memotong animasi".
     Dengan jendela di ekor, tekanan cepat tidak menyela gerakan; jurus berikutnya
     baru dimulai setelah gerakan sebelumnya selesai. Tekanan tetap tertangkap karena
     buffer input 0,2 s (JDGA_LightAttack.cpp:319).
  2. Laju main (play_rate) dinaikkan supaya wind-up 0,43 s -> ~0,27 s. Finisher tetap berat.
  3. blend_in 0,05 s (masuk cepat) dan blend_out 0,22 s (interupsi mulus, tidak menyentak).

Jalankan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_tune.py
"""

import json
import os

import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary

MONTAGE_DIR = "/Game/Hermes/ComboIter2/Montages"
PROFIL = "/Game/Hermes/ComboIter2/Data/DA_CombatProfile_Human_Hermes"
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Art", "combo-iter2", "Log")

# laju main per peran. finisher_02 sengaja 0,85: dua tendangannya hanya berjarak 0,15 s,
# kalau dipercepat keduanya jatuh hampir bersamaan (lihat laporan, temuan 5).
LAJU = {
    "light_01": 1.60, "light_02": 1.60, "light_03": 1.60, "light_04": 1.45,
    "lunge": 1.50, "back": 1.50,
    "finisher_01": 1.25, "finisher_02": 0.85, "finisher_03": 1.15,
    "air": 1.20, "air_slam": 1.00,
}

# (nama properti profil, indeks dalam array atau None, peran)
SLOT = [
    ("light_combo", 0, "light_01"), ("light_combo", 1, "light_02"),
    ("light_combo", 2, "light_03"), ("light_combo", 3, "light_04"),
    ("lunge_attack", None, "lunge"), ("back_attack", None, "back"),
    ("heavy_finishers", 0, "finisher_01"), ("heavy_finishers", 1, "finisher_02"),
    ("heavy_finishers", 2, "finisher_03"),
    ("air_attack", None, "air"), ("air_slam", None, "air_slam"),
]

TRACK = "Combat"
# finisher tidak diberi jendela combo: kalau ada, tombol E saat finisher berjalan
# akan lolos CanActivate (butuh IsAttackCancelable ATAU tag ComboWindow) dan memutar ulang dirinya.
TANPA_COMBO = {"finisher_01", "finisher_02", "finisher_03"}
# air_slam memang tanpa hit window: damage-nya area saat mendarat, bukan dari tulang.
LEWATI = {"air_slam"}
BLEND_IN = 0.05
BLEND_OUT = 0.22
EKOR_JENDELA = 0.55   # jendela combo = EKOR_JENDELA terakhir dari klip (bukan di hantaman!)
SISA_UJUNG = 0.02     # sisa di ujung montage

baris = []


def catat(msg):
    print(msg)
    baris.append(msg)


def kelas_notify(ev):
    """FAnimNotifyEvent itu struct. Untuk notify state, instance template-nya ada di
    properti 'notify_state_class' (bukan 'notify' yang kosong)."""
    n = ev.get_editor_property("notify")
    if n:
        return n.get_class().get_name(), n
    nsc = ev.get_editor_property("notify_state_class")
    if nsc:
        return nsc.get_class().get_name(), nsc
    return "", None


def baca_notify(m):
    """-> (hit[], combo[]) dengan hit = (mulai, durasi, tulang, new_hit)."""
    hits, combo = [], []
    for ev in AL.get_animation_notify_events(m):
        nama, obj = kelas_notify(ev)
        t = round(AL.get_anim_notify_event_trigger_time(ev), 3)
        d = round(AL.get_anim_notify_event_duration(ev), 3)
        if "HitWindow" in nama:
            socket = obj.get_editor_property("socket_name") if obj else ""
            new_hit = bool(obj.get_editor_property("new_hit")) if obj else False
            if not socket:  # cadangan: nama notify berbentuk "Hit hand_r"
                socket = str(ev.get_editor_property("notify_name")).replace("Hit ", "").strip()
            hits.append((t, d, str(socket), new_hit))
        elif "ComboWindow" in nama:
            combo.append((t, d))
    return sorted(hits), sorted(combo)


def tune_montage(peran, laju):
    path = f"{MONTAGE_DIR}/AM_Hermes_{peran}"
    m = EAL.load_asset(path)
    if not m:
        catat(f"GAGAL  {peran}: montage tidak ada di {path}")
        return None
    if peran in LEWATI:
        catat(f"LEWAT  {peran:12s} tanpa notify HitWindow (damage area saat mendarat), tidak disetel")
        return None
    panjang = m.get_editor_property("sequence_length")
    hits, combo = baca_notify(m)
    if not hits:
        catat(f"GAGAL  {peran}: tidak ada notify HitWindow, jendela combo tidak bisa dihitung")
        return None

    awal_hit = hits[0][0]
    # Jendela combo ditaruh di EKOR klip: tekanan cepat tidak memotong animasi yang sedang jalan,
    # dan jurus berikutnya baru mulai setelah gerakan sebelumnya selesai (umpan balik M6 kedua).
    baru_mulai = max(0.05, round(panjang - EKOR_JENDELA, 3))
    baru_durasi = round(panjang - baru_mulai - SISA_UJUNG, 3)

    # tulis ulang seluruh track "Combat": jendela hit dipertahankan, jendela combo diganti
    AL.remove_animation_notify_events_by_track(m, TRACK)
    for start, dur, socket, new_hit in hits:
        ev = AL.add_animation_notify_state_event(m, TRACK, start, dur,
                                                 unreal.JDAnimNotifyState_HitWindow)
        ev.set_editor_property("socket_name", socket)
        ev.set_editor_property("new_hit", new_hit)
    if peran not in TANPA_COMBO:
        AL.add_animation_notify_state_event(m, TRACK, baru_mulai, baru_durasi,
                                            unreal.JDAnimNotifyState_ComboWindow)
    else:
        baru_mulai, baru_durasi = None, None

    # blend
    for prop, t in (("blend_in", BLEND_IN), ("blend_out", BLEND_OUT)):
        b = m.get_editor_property(prop)
        b.set_editor_property("blend_time", t)
        m.set_editor_property(prop, b)

    EAL.save_loaded_asset(m, only_if_is_dirty=False)

    lama = combo[0] if combo else (None, None)
    teks_baru = ("tidak diberi jendela combo" if baru_mulai is None
                 else f"{baru_mulai:.2f}->{round(baru_mulai + baru_durasi, 2)}")
    catat(f"OK     {peran:12s} panjang {panjang:.2f} s ({panjang / laju:.2f} s nyata) | "
          f"hantaman {awal_hit:.2f} s | jendela combo {lama[0]}->{round((lama[0] or 0) + (lama[1] or 0), 2)} "
          f"jadi {teks_baru} | laju {laju:.2f}x")
    return {
        "peran": peran,
        "panjang": round(panjang, 3),
        "panjang_nyata": round(panjang / laju, 3),
        "hantaman": hits,
        "combo_lama": combo,
        "combo_baru": [baru_mulai, baru_durasi],
        "laju": laju,
        "blend": [BLEND_IN, BLEND_OUT],
    }


def tune_profil(prof):
    """Tulis play_rate ke tiap langkah profil (struct di TArray: ubah salinan lalu ganti elemen)."""
    for prop, idx, peran in SLOT:
        laju = LAJU[peran]
        if idx is None:
            s = prof.get_editor_property(prop)
            s.set_editor_property("play_rate", laju)
            prof.set_editor_property(prop, s)
        else:
            arr = list(prof.get_editor_property(prop))
            while len(arr) <= idx:
                arr.append(unreal.JDAttackStep())
            s = arr[idx]
            s.set_editor_property("play_rate", laju)
            arr[idx] = s
            prof.set_editor_property(prop, arr)
    EAL.save_loaded_asset(prof, only_if_is_dirty=False)


def main():
    prof = EAL.load_asset(PROFIL)
    if not prof:
        catat(f"GAGAL: profil {PROFIL} tidak ada")
        return

    catat("=== penyetelan combo iterasi 2 ===")
    hasil = []
    for prop, idx, peran in SLOT:
        r = tune_montage(peran, LAJU[peran])
        if r:
            hasil.append(r)
    tune_profil(prof)

    # baca balik: bukti, bukan klaim
    catat("--- baca balik dari aset ---")
    for prop, idx, peran in SLOT:
        if idx is None:
            s = prof.get_editor_property(prop)
        else:
            s = list(prof.get_editor_property(prop))[idx]
        m = s.get_editor_property("montage")
        hits, combo = baca_notify(m)
        catat(f"     {peran:12s} play_rate {s.get_editor_property('play_rate'):.2f} | "
              f"montage {m.get_name()} | combo {combo} | hit {hits}")

    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "tune.json"), "w", encoding="utf-8") as f:
        json.dump(hasil, f, ensure_ascii=False, indent=2)
    with open(os.path.join(LOG_DIR, "tune.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(baris))
    catat(f"log: {os.path.join(LOG_DIR, 'tune.json')}")


main()
