# Combat Iterasi 2b (Jayadwara = Aksa): Instruksi Kerja untuk Hermes

> Dari Claude, untuk Hermes. **File ini read-only bagimu.** Progres ditulis di `Hermes/Laporan/YYYY-MM-DD-combo-iter2b.md`.
> Baca dulu `AGENTS.md` sampai habis (§0 Cara kerja, §1 Git, §2 Area sandbox, §3 Unreal), lalu `docs/23-rencana-fase-1.md` §6 **Iterasi 2b** dan `docs/07-gameplay-sistem.md` ("Combo & arah", "Daftar jurus Jayadwara (usulan)", "Serangan udara", "Parry"). Semua aturan di `AGENTS.md` berlaku; kalau ada beda, `AGENTS.md` menang atas file ini.
> Versi: 18 Okt 2026.
> **Di dalam scope fase aktif:** Fase 1, Iterasi 2b. Tulis kalimat itu di laporan.

---

## 0. Ringkasan

Combat **Aksa** sudah final dan lulus uji tangan developer (18 Okt 2026): 4 langkah combo, terjang, pukul mundur, 3 finisher, serangan udara + hantaman, tangkis, stagger — 14 montage, 10 di antaranya memakai animasi **Mixamo** hasil kerja Iterasi 2.

Combat **Jayadwara** masih tertinggal: `Content/Jayadwara/Characters/Jayadwara2/Combat/` baru berisi `AM_JD2_Light_01..03`, `AM_JD2_Heavy`, `AM_JD2_Block` — **3 langkah**, animasinya placeholder Mannequin (`MM_Attack_0x_JD2`), tanpa terjang, tanpa finisher ke-3, tanpa serangan udara, tanpa dodge/tangkis beranimasi.

Tugasmu: **membuktikan di sandbox** bahwa animasi Aksa bisa di-retarget ke `SKEL_Jayadwara2` **tanpa mengubah rasa** — tabel notify tiap montage raksasa harus identik dengan pasangan Aksanya (tulang, waktu, jumlah jendela), dan tubuh setinggi 45 m tidak rusak karenanya (kaki menembus lantai, tangan menembus badan, root motion melenceng). Hasilnya di-review Claude, lalu Claude yang memasang ke proyek utama.

**Kamu tidak membuat animasi baru, tidak download Mixamo, tidak tuning rasa.** Semua sumber sudah ada di repo.

| Kamu kerjakan | Bukan tugasmu |
|---|---|
| Audit tabel notify 14 montage Aksa (`Log/parity_aksa.json`) | Memilih / download animasi Mixamo |
| Retarget 13 animasi sumber → skeleton Jayadwara2 **di `/Game/Hermes/ComboIter2b/`** | Menjalankan `Tools/ue_setup_giant_*.py`, `ue_setup_jayadwara2.py`, `ue_setup_light_combo.py` |
| Montage + notify paritas + laporan paritas (`Log/parity.json`) | Mengubah C++, `Tools/`, `docs/`, aset `/Game/Jayadwara/` |
| Level uji sandbox + checklist uji tangan untuk developer | Menilai "seru" (developer yang main) |
| Cek 45 m: kaki/lantai, tangan/badan, root motion | Tuning angka damage, jarak, shake (sudah ditetapkan `docs/23` §5) |

### Sumber kebenaran (baca, jangan ubah)
| File | Dipakai untuk |
|---|---|
| `docs/23` §6 Iterasi 2b + §5 | Aturan paritas, daftar gate G2b-1…4, angka berskala |
| `docs/07` "Combo & arah", "Daftar jurus", "Serangan udara", "Parry" | Bentuk gerak & urutan jurus tiap peran |
| `Tools/ue_setup_light_combo.py` (`STEPS`, `add_combat_notifies`, `setup_profile`) | Pola montage + notify + isi profil Aksa |
| `Tools/ue_setup_defense.py`, `Tools/ue_setup_parry.py` | Slot berat/tangkis/tepisan & angka rasa parry |
| `Tools/ue_setup_giant_combo.py` | Pola penamaan `AM_JD2_*`, kompensasi `GlobalAnimRateScale`, angka berskala raksasa |
| `Tools/ue_setup_jayadwara2.py` (`retarget()`) | Cara RTG Mannequin→Jayadwara2 dibuat & dipakai |
| `Source/Jayadwara/Combat/JDCombatProfile.h` | Nama field profil (`light_combo`, `heavy_finishers`, `dodge_montages`, `parry_montages`, …) |

### Isi combat Aksa yang jadi patokan (14 montage)
Sumber tiap montage **baca dari montage-nya** (`source_animation`), jangan menebak dari tabel ini — tabel ini hanya peta jalan.

| Montage Aksa | Sumber animasi (per 18 Okt) | Dari Mixamo? | Notify |
|---|---|---|---|
| `AM_Aksa_Light_01..04` | `A_Aksa_Mx_light_01..04` | ya | Hit Window + Combo Window (langkah 4 **juga** punya combo) |
| `AM_Aksa_Lunge` | `A_Aksa_Attack_01` (placeholder, `lunge.fbx` salah isi) | tidak | Hit + Combo, `MoveHeight` > 0 (lompat kecil) |
| `AM_Aksa_Back` | `A_Aksa_Mx_back` | ya | Hit + Combo, `MoveDistance` negatif |
| `AM_Aksa_Finisher_01..03` | `A_Aksa_Mx_finisher_01..03` | ya | Hit Window saja (sengaja tanpa combo) |
| `AM_Aksa_Heavy` | `A_Aksa_Attack_02`, laju 0,75 | tidak | Hit Window |
| `AM_Aksa_Air` | `A_Aksa_Mx_air` (tanpa root motion) | ya | Hit + Combo |
| `AM_Aksa_AirSlam` | `A_Aksa_Mx_air_slam` (tanpa root motion) | ya | Hit Window |
| `AM_Aksa_Block` | `A_Aksa_Attack_02`, frame ditahan | tidak | — |
| `AM_Aksa_Stagger` | `A_Aksa_Stagger` (dari `MM_HitReact_Front_Hvy_01`) | tidak | — |

Kalau ada montage yang **tidak** ada di daftar ini saat kamu audit (mis. `AM_Aksa_Dodge_*` / `AM_Aksa_Parry_*` sudah dibuat Claude), **ikutkan** — aturannya satu: setiap montage Aksa harus punya pasangan raksasa.

---

## 1. Persiapan (sekali)

Kode C++ **tidak berubah** di 2b (hanya Python + aset), jadi cukup build yang sudah ada di `development`. PR #48 (integrasi combo Iterasi 2) sudah di-merge 18 Okt 2026 — commit `5b53b49`.

```
cd C:\repository\unreal_engine\jayadwara
git fetch origin development
git worktree add C:\repository\unreal_engine\jayadwara_hermes_combo2b -b hermes/combo-iter2b origin/development
cd C:\repository\unreal_engine\jayadwara_hermes_combo2b
git lfs pull
```
- Cek sandbox **selalu dengan base yang sama**: `python -I Tools/hermes_cek_sandbox.py --base origin/development`.
- Buka `WORKTREE\Jayadwara.uproject`, compile C++ (Yes). **Kalau compile gagal, berhenti** dan tempel errornya di laporan — itu masalah `development`, bukan tugasmu.
- Kalau `git worktree add` menolak karena folder sudah ada dari tugas lain, pakai `git switch -c hermes/combo-iter2b origin/development` di WORKTREE lama setelah branch tugas sebelumnya di-push.

### Nama & lokasi (pakai persis)
| Apa | Path |
|---|---|
| Branch | `hermes/combo-iter2b` |
| WORKTREE | `C:\repository\unreal_engine\jayadwara_hermes_combo2b` |
| Tujuan UE (`DEST`) | `/Game/Hermes/ComboIter2b` (`Anims/`, `Montages/`, `Data/`, `Maps/`, `Rig/`) |
| Skrip | `Hermes/Tools/combo_iter2b_*.py` |
| Log & JSON | `Hermes/Art/combo-iter2b/Log/` |
| Level uji | `/Game/Hermes/ComboIter2b/Maps/Test_Hermes_ComboIter2b` |
| Laporan | `Hermes/Laporan/YYYY-MM-DD-combo-iter2b.md` |

**Jangan** menulis ke `/Game/Jayadwara/Characters/Jayadwara2/` — folder itu milik proyek. Kamu hanya **membacanya**.

---

## 2. M1: Audit "emas" dari Aksa (read-only)

Tulis `Hermes/Tools/combo_iter2b_audit_aksa.py` (UE Python, **hanya membaca**). Jalankan: `python Tools/ue_remote.py Hermes/Tools/combo_iter2b_audit_aksa.py`.

Untuk tiap `AM_Aksa_*` di `/Game/Jayadwara/Characters/Aksa/Anims/Montages/`, catat ke `Hermes/Art/combo-iter2b/Log/parity_aksa.json`:

| Field | Isi |
|---|---|
| `montage`, `length`, `blend_in`, `blend_out` | nilai mentah (`get_editor_property`) |
| `source_animation` | path animasi sumbernya (ini yang kamu retarget) |
| `source_skeleton` | `SK_Mannequin`? tulis nama aslinya |
| `notifies[]` | per entri track `Combat`: nama class (`JDAnimNotifyState_HitWindow` / `JDAnimNotifyState_ComboWindow`), `start`, `duration`, `socket_name`, `radius_override`, `new_hit`, tag/`cue` kalau ada |
| `hit_window_count` | jumlah jendela hit |

Tambahan yang juga dicatat:
- Isi `DA_CombatProfile_Human`: **field mana saja yang tidak kosong** (light_combo 4 langkah + damage/poise/stamina/play_rate, lunge/back, heavy_finishers 3 slot, heavy, air, air_slam, dodge 4 arah, parry_montages, block, parry hit-stop/slow-mo/counter, stagger). Tulis angka tiap field berskala-netral.
- Daftar tulang `SKEL_Jayadwara2` (dari `SK_Jayadwara2`): pastikan `pelvis`, `hand_l`, `hand_r`, `foot_l`, `foot_r`, `spine_03`, `head` ada. Catat jumlah tulang.
- `GlobalAnimRateScale` mesh `BP_Jayadwara2` (dipakai untuk mengali blend time nanti).

**Kriteria lulus M1:** `parity_aksa.json` memuat **semua** montage Aksa; tiap montage menyerang punya ≥ 1 hit window (yang tidak menyerang: `Block`, `Stagger`, `Parry*`, `Dodge*`); tabel ringkas (montage → jumlah hit window → tulang → waktu) dicetak di output dan disalin ke laporan.

---

## 3. M2: Retarget ke skeleton Jayadwara2 (di sandbox)

Tulis `Hermes/Tools/combo_iter2b_retarget.py`. Yang **dibaca** (read-only, jangan disimpan/diubah): `SKM_Manny_Simple`, `SK_Jayadwara2`, `RTG_Mannequin_To_Jayadwara2`, `IK_Jayadwara2`, `IK_Mannequin`.

```python
DEST = "/Game/Hermes/ComboIter2b"
# assets = daftar unik source_animation dari parity_aksa.json (13 animasi)
unreal.JDEditorToolsLibrary.retarget_assets_to_folder(
    [unreal.EditorAssetLibrary.load_asset(p) for p in sources],
    manny_mesh, jd2_mesh, rtg, f"{DEST}/Anims", "_H2b", True)
```

Catatan penting:
- Helper itu **mengosongkan folder tujuan** sebelum menulis — karena itu tujuannya wajib `{DEST}/Anims`, jangan pernah folder proyek.
- **Jangan** menjalankan `Tools/ue_setup_jayadwara2.py` (skrip itu menghapus seluruh `Jayadwara2/Anims`). Kamu hanya meminjam RTG-nya.
- Kalau hasil retarget jelas rusak (kaki menggantung, badan melipat), **duplikat** RTG ke `{DEST}/Rig/RTG_Mannequin_To_Jayadwara2_Hermes` lalu sesuaikan salinannya (pola `retarget()` di `ue_setup_jayadwara2.py`: `add_default_ops`, `auto_map_chains(EXACT)`, `auto_align_all_bones(CHAIN_TO_CHAIN)`, `Run IK Rig` dimatikan). Jangan menyimpan RTG proyek.

**Kriteria lulus M2:** 13 animasi `A_H2b_*` ada di `{DEST}/Anims`, semuanya di skeleton `SKEL_Jayadwara2`, panjangnya sama dengan sumber (±1 frame), dan log mencetak per file: nama, skeleton, panjang sumber vs hasil. Kalau ada yang gagal retarget setelah **3 percobaan**, lewati, tulis di laporan (AGENTS.md §0.5).

**Bahaya (insiden `SK_Mannequin`, AGENTS.md §3):** setelah skrip jalan, `git status --porcelain Content/Characters Content/Jayadwara` harus **kosong**. Kalau tidak: `git restore` file itu dan tulis di laporan. Saat menutup editor, dialog "Save content" yang berisi aset di luar `/Game/Hermes/` → **Don't Save**.

---

## 4. M3: Montage + paritas notify

Tulis `Hermes/Tools/combo_iter2b_montages.py`. Untuk tiap montage Aksa, buat `AM_H2b_<nama>` di `{DEST}/Montages` dari animasi hasil retarget, lalu **salin tabel notify dari montage Aksa apa adanya** — jangan menghitung ulang dari kecepatan tulang (itu yang dilakukan `ue_setup_light_combo.py` untuk animasi baru; di sini sumbernya identik, jadi menyalin = paritas).

| Yang disalin | Aturan |
|---|---|
| Jumlah & urutan jendela | sama persis (mis. `Light_04` tetap punya Hit + Combo) |
| `start`, `duration` | sama persis (detik animasi) |
| `socket_name` | sama; cek tulangnya ada di `SKEL_Jayadwara2` |
| `radius_override` | sama (kalau ada) |
| `new_hit` | sama (narae chagi 2× kena bergantung ini) |
| `blend_in`, `blend_out` | nilai montage Aksa **× `GlobalAnimRateScale` mesh raksasa** (pola `ue_setup_giant_combo.py`; raksasa diperlambat mesh, jadi blend dalam detik nyata butuh kompensasi) |
| Root motion | animasi udara/hantaman: `enable_root_motion = False` seperti Aksa |

Tulis `Hermes/Tools/combo_iter2b_cek_paritas.py` (hanya membaca) → `Log/parity.json`:

| Cek | Lulus kalau |
|---|---|
| Pasangan | tiap `AM_Aksa_*` punya `AM_H2b_*` (14/14, atau semua yang ada saat audit) |
| Jumlah jendela | sama (hit & combo terpisah) |
| Tulang | `socket_name` sama |
| Waktu | `start` & `duration` selisih ≤ **0,01 s** |
| `new_hit` / `radius_override` | sama |
| Tulang raksasa | semua socket ada di `SKEL_Jayadwara2` |
| Tidak patah | tidak ada tulang yang lompat > 50 cm antar-frame (retarget pecah) |
| Kaki & lantai | untuk animasi darat: `foot_l`/`foot_r` tidak di bawah `root` lebih dari 5 cm (kecuali `air*`, `dodge_*`) — catat nilai minimum |
| Tangan & badan | jarak `hand_l`/`hand_r` ke garis `spine_03`→`pelvis` tidak < 12 cm di luar jendela hit (indikasi tangan menembus badan); kalau ragu, andalkan pemutar gerak (di bawah) |

Ekspor gerak untuk developer: salin `Tools/ue_export_combat_motion.py` ke `Hermes/Tools/combo_iter2b_export_motion.py`, arahkan ke `AM_H2b_*`, output `Hermes/Art/combo-iter2b/Log/combat_motion_jd2.json`. Developer bisa memutar JSON itu di pemutar "Gerak Jurus" (tautan dari Claude) untuk menilai 45 m secara visual.

**Kriteria lulus M3:** `parity.json` PASS untuk semua pasangan (atau gagal dijelaskan per file dengan angka), `combat_motion_jd2.json` ter-commit, tabel paritas (montage → jumlah jendela → tulang → waktu) masuk laporan.

---

## 5. M4: Profil, pawn, dan level uji (sandbox)

Tulis `Hermes/Tools/combo_iter2b_setup.py`:

1. **Profil** — duplikat `/Game/Jayadwara/Data/DA_CombatProfile_Giant` → `{DEST}/Data/DA_CombatProfile_Giant_Hermes` (aslinya tidak disentuh). Isi **semua slot yang terisi di `DA_CombatProfile_Human`** dengan `AM_H2b_*`:

   | Slot | Isi |
   |---|---|
   | `light_combo[0..3]` | `AM_H2b_Light_01..04` (damage/poise tetap seperti profil raksasa: 10/10/12/20) |
   | `lunge_attack`, `back_attack` | `AM_H2b_Lunge`, `AM_H2b_Back` (+ `move_distance`/`move_duration`/`move_height`/`stop_at_target` sama seperti Aksa) |
   | `heavy_finishers[0..2]` | `AM_H2b_Finisher_01..03` (3 slot — raksasa sekarang baru 2) |
   | `heavy_attack` | `AM_H2b_Heavy` (laju 0,75 seperti Aksa) |
   | `air_attack`, `air_slam` | `AM_H2b_Air`, `AM_H2b_AirSlam` |
   | `dodge_montages` | isi kalau Aksa punya; kalau kosong, biarkan kosong |
   | `parry_montages` | isi kalau Aksa punya; kalau kosong, biarkan kosong |
   | `block_montage` | `AM_H2b_Block` |
   | `stagger_montage` | `AM_H2b_Stagger` |
   | `parry_counter_attack` | `AM_H2b_Light_04` (sama seperti Aksa) |

   Angka yang **boleh** beda dari Aksa (jangan "diperbaiki" jadi sama): radius hit ×skala, `dodge_distance` 5500, `block_pushback` 1500, `hit_camera_shake_scale` 2,5, `hit_stop_duration` 0,15, `parry_window` 0,25, `air_slam_speed` ×skala×0,6, `air_slam_radius` ×skala, `montage_play_rate` 1,0. Angka lain **sama**.

2. **Pawn** — duplikat `/Game/Jayadwara/Characters/Jayadwara2/BP_Jayadwara2` → `{DEST}/BP_Jayadwara2_Hermes`, `combat_component.combat_profile` = profil Hermes.
3. **Level** — duplikat `/Game/Jayadwara/Maps/Test_GiantScale` → `{DEST}/Maps/Test_Hermes_ComboIter2b`, buka **level salinan**, taruh `BP_Jayadwara2_Hermes` di PlayerStart (`auto_possess_player = PLAYER0`), plus dummy berskala ×20 sekitar 30 m di depan (pola `place_dummy()` di `ue_setup_giant_combo.py`).

Catat `Log/profile.json`: isi tiap slot setelah dibaca balik (`get_editor_property`), plus daftar slot yang kosong di **kedua** profil (itu sah, bukan bug).

**Kriteria lulus M4:** level terbuka tanpa error di Output Log; semua slot yang terisi di profil manusia terisi di profil Hermes; `python -I Tools/hermes_cek_sandbox.py --base origin/development` LULUS; `git status` di luar sandbox bersih.

---

## 6. M5: Uji tangan oleh developer

Tulis bagian "Cara mencoba" di laporan sebagai checklist. Isinya: buka `Test_Hermes_ComboIter2b`, Play, `JD.Debug.Hitbox 1`, lalu:

| # | Coba | Yang harus terjadi |
|---|---|---|
| 1 | LMB ×4 cepat | 4 jurus beruntun (jab, cross, hook, tendangan putar belakang), langkah 4 tetap bisa disambung |
| 2 | LMB ×3, lalu LMB lagi | Tidak menambah jadi 5 — combo berhenti di 4 |
| 3 | W + LMB dari ±30 m | Terjang: lompat kecil ke dummy, pukulan kena, combo lanjut dari langkah 2 |
| 4 | S + LMB | Mundur sambil memukul |
| 5 | LMB, lalu E | Finisher 1 (tendangan belakang) |
| 6 | LMB ×2, lalu E | Finisher 2 (narae chagi), **dua** kali kena |
| 7 | LMB ×3, lalu E | Finisher 3 — sebelumnya **tidak ada** di raksasa |
| 8 | E dari diam | Pukulan putar (berat biasa) |
| 9 | Space + LMB | Tendangan terbang, 1× per lompatan, tidak "ngambang" |
| 10 | Space + E | Hantaman berputar di tempat (tidak menukik), kaki kena |
| 11 | Shift + arah | Dodge (jarak raksasa ±55 m), tidak menembus lantai |
| 12 | RMB tahan | Pose tangkis; RMB tepat waktu ke serangan dummy = parry (kalau dummy menyerang tersedia) |
| 13 | Main bebas 5 menit | Skor developer 1–5: "gerak sesuai Aksa" dan "tidak ada kaki/tangan rusak di skala 45 m" |

Yang kelihatan aneh (kaki melayang, tangan menembus badan, arah hadap salah, badan melipat) dicatat developer per nomor. Kamu boleh memperbaiki **di sandbox saja** (RTG salinan, blend, atau animasi sumber yang dipilih) dan wajib mencatat angka sebelum/sesudah.

---

## 7. Laporan & selesai

- Laporan mengikuti format `AGENTS.md` §8, diperbarui tiap M selesai. Tabel progres berisi M1–M5.
- Tambahkan bagian **"Untuk Claude"**: tabel paritas final (montage → jendela → tulang → waktu), daftar animasi yang lulus/gagal retarget beserta alasannya, temuan khas raksasa (kaki/lantai, tangan/badan, root motion) dengan angka, dan usulan perubahan di skrip proyek (**jangan** kamu kerjakan sendiri).
- Sebelum commit terakhir: `python -I Tools/hermes_cek_sandbox.py --base origin/development` LULUS. Tempel baris terakhirnya di laporan.
- Push `hermes/combo-iter2b`. **Jangan merge, jangan buat PR.**

---

## 8. Sesudahnya: tahap Claude (konteks, bukan tugasmu)

C1. Claude me-review branch: `git diff origin/development...origin/hermes/combo-iter2b --stat` (semua harus di `Content/Hermes/`, `Hermes/`), menjalankan ulang `combo_iter2b_cek_paritas.py` sendiri, dan membandingkan angkanya dengan laporan.
C2. Claude menulis `Tools/ue_setup_giant_mixamo.py` (retarget ke `/Game/Jayadwara/Characters/Jayadwara2/Anims/Mixamo/A_JD2_Mx_*`) dan menulis ulang `Tools/ue_setup_giant_combo.py` (4 langkah + `light_04` berjendela combo, terjang lompat, 3 finisher, udara/hantaman angka 18 Okt, blend per peran, profil lengkap).
C3. Developer: build → `ue_setup_giant_mixamo.py` → `ue_setup_giant_combo.py` → `ue_setup_giant_speed.py` (kalau kelincahan diubah) → uji gate G2b-3 di `Test_GiantScale`.
C4. Lulus → Claude memperbarui `docs/23` §11 + `KONTEKS_PROYEK.md`, lalu PR ke `development`. Sisa tuning rasa raksasa tetap di Iterasi 6.
