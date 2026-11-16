# Combo Iterasi 2 (jurus baru dari Mixamo): Instruksi Kerja untuk Hermes

> Dari Claude, untuk Hermes. **File ini read-only bagimu.** Progres ditulis di `Hermes/Laporan/YYYY-MM-DD-combo-iter2.md`.
> Baca dulu `AGENTS.md` sampai habis (terutama §0 Cara kerja, §1 Git, §3 Unreal, §5 Blender), lalu [`mixamo/README.md`](../mixamo/README.md). Semua aturan di sana berlaku. Kalau ada beda, `AGENTS.md` menang atas file ini.
> Desain: `docs/07-gameplay-sistem.md` (bagian "Combo & arah", "Daftar jurus", "Dodge per arah", "Serangan udara", "Parry"), `docs/23-rencana-fase-1.md` Iterasi 2–3.
> Versi: 17 Okt 2026.
> **Di dalam scope fase aktif:** Fase 1, revisi Iterasi 2 (dan animasi dodge/parry Iterasi 3). Tulis kalimat itu di laporan.

---

## 0. Ringkasan

Kode combo Aksa sudah jadi (combo 4 pukulan, terjang, pukul mundur, 2 finisher berat, serangan udara, dodge per arah, parry tepis). Yang belum: **animasinya masih placeholder Mannequin**. Developer sudah menyetujui jurus baru pada 16 Okt 2026 (`docs/07` "Daftar jurus"): tendangan taekwondo dan dodge salto/guling. Animasinya diambil dari **Mixamo**.

Tugasmu: menyiapkan daftar Mixamo untuk developer, memeriksa FBX yang di-download developer, lalu membuktikan di **sandbox UE** bahwa animasi itu ter-retarget ke Manny, waktu kenanya benar, dan semuanya bisa dimainkan. Hasilnya di-review Claude, lalu Claude yang memasang ke proyek utama.

| Kamu kerjakan | Bukan tugasmu |
|---|---|
| `mixamo/asset/DAFTAR_ANIMASI.md` | Login / download di Mixamo (developer) |
| Cek FBX di `mixamo/result/`, pindahkan ke sandbox | Mengubah C++ proyek, `Tools/`, `docs/`, aset `/Game/Jayadwara/` |
| Import + retarget + montage + profil + level **di `/Game/Hermes/ComboIter2/`** | Menjalankan `Tools/ue_import_mixamo.py` atau `Tools/ue_setup_*.py` langsung |
| Angka waktu kena, ekspor gerak, laporan | Menilai "seru" (developer yang main) |

### Sumber kebenaran (baca, jangan ubah)
| File | Dipakai untuk |
|---|---|
| `docs/07` tabel "Daftar jurus" + "Dodge per arah" + "Parry" | Bentuk gerak tiap peran |
| `Tools/ue_import_mixamo.py` | Logika import + IK Rig + retarget (disalin ke `Hermes/Tools/`) |
| `Tools/ue_setup_light_combo.py` (`strike_timings`, `add_combat_notifies`, `apply_mixamo`) | Cara membuat montage + JD Hit/Combo Window |
| `Tools/ue_setup_defense.py`, `Tools/ue_setup_parry.py` | Slot montage dodge & tepisan |
| `Tools/ue_export_combat_motion.py` | Ekspor gerak tulang ke JSON (untuk pemutar 3D developer) |
| `Source/Jayadwara/Combat/JDCombatProfile.h` | Nama field profil (`light_combo`, `heavy_finishers`, `dodge_montages`, `parry_montages`, …) |

---

## 1. Persiapan (sekali)

Kode yang dibutuhkan (`MoveHeight`, `bNewHit` di JD Hit Window, `ParryMontages`) ada di PR #38, branch `claude/project-thread-re8qwd`. **Selama PR #38 belum di-merge, cabangkan dari branch itu**, bukan dari `development`:

```
cd C:\repository\unreal_engine\jayadwara
git fetch origin claude/project-thread-re8qwd development
git worktree add C:\repository\unreal_engine\jayadwara_hermes_combo -b hermes/combo-iter2 origin/claude/project-thread-re8qwd
cd C:\repository\unreal_engine\jayadwara_hermes_combo
git lfs pull
```
- Kalau PR #38 sudah di-merge (cek `git log origin/development --oneline | findstr "parry tepis"`), pakai `origin/development` sebagai titik cabang.
- Cek sandbox **selalu dengan base yang sama dengan titik cabang**, misalnya `python -I Tools/hermes_cek_sandbox.py --base origin/claude/project-thread-re8qwd`. Tanpa `--base`, file PR #38 ikut terhitung "luar sandbox".
- Buka `WORKTREE\Jayadwara.uproject` dan compile C++ (Yes). Catat di laporan: compile berhasil atau tidak. **Kalau compile gagal, berhenti**, tempel errornya di laporan, dan beri tahu developer. Itu bug PR #38, jadi Claude yang memperbaiki.

### Nama & lokasi (pakai persis)
| Apa | Path |
|---|---|
| Branch | `hermes/combo-iter2` |
| WORKTREE | `C:\repository\unreal_engine\jayadwara_hermes_combo` |
| Tujuan UE (`DEST`) | `/Game/Hermes/ComboIter2` (Rig/, Mixamo/, Mixamo/Raw/, Montages/, Data/, Maps/) |
| FBX hasil cek | `Hermes/Art/combo-iter2/Mixamo/<peran>.fbx` |
| Log & JSON | `Hermes/Art/combo-iter2/Log/` |
| Skrip | `Hermes/Tools/combo_iter2_*.py` |
| Level uji | `/Game/Hermes/ComboIter2/Maps/Test_Hermes_ComboIter2` |
| Laporan | `Hermes/Laporan/YYYY-MM-DD-combo-iter2.md` |

---

## 2. M1: Daftar animasi untuk developer (`mixamo/asset/`)

Tulis `mixamo/asset/DAFTAR_ANIMASI.md` (kamu **boleh** menulis di `mixamo/asset/`; `mixamo/README.md` read-only). Isinya tabel di bawah, ditambah kolom **centang** (☐) supaya developer bisa menandai yang sudah di-download. Bahasa Indonesia santai, satu baris per file. Di bagian paling atas, tulis langkah singkat untuk developer: buka mixamo.com, login, pilih karakter Y Bot (bawaan), cari kata kunci, atur setting, Download, ganti nama, taruh di `WORKTREE\mixamo\result\`.

**Prioritas 1 (wajib, jurus yang disetujui 16 Okt):**

| Nama file | Jurus (docs/07) | Kata kunci Mixamo (coba berurutan) | Setting khusus | Kena (tulang, jumlah) |
|---|---|---|---|---|
| `ybot.fbx` | Karakter sumber retarget | Pilih karakter **Y Bot**, tanpa animasi (T-pose) | **With Skin** | — |
| `light_04.fbx` | Tendangan putar belakang (*dwi huryeo chagi*), akhir combo | Spinning Back Kick, Spin Kick, Mma Kick | In Place | kaki, 1 |
| `finisher_01.fbx` | Tendangan belakang (*dwi chagi*) | Back Kick, Mule Kick | In Place | kaki, 1 |
| `finisher_02.fbx` | Tendangan ganda melompat (*narae chagi*) | Double Kick, Jumping Double Kick, Martelo 2 | In Place | kaki, **2** |
| `air.fbx` | Tendangan terbang memutar | Tornado Kick, Butterfly Kick, Jump Spin Kick | In Place | kaki, 1 |
| `dodge_back.fbx` | Salto belakang | Back Flip, Backflip | In Place | — |
| `dodge_left.fbx` | Guling / cartwheel ke kiri | Dodge Roll Left, Cartwheel, Side Roll | In Place | — |
| `dodge_right.fbx` | Guling / cartwheel ke kanan | sama dengan kiri | In Place + **Mirror** kalau hanya ada versi kiri | — |
| `dodge_forward.fbx` | Langkah cepat menunduk | Quick Step, Dodge Forward, Evade | In Place | — |

**Prioritas 2 (opsional, kalau developer mau semua placeholder diganti):**

| Nama file | Jurus | Kata kunci | Kena |
|---|---|---|---|
| `light_01.fbx` | Jab, tangan kiri depan | Jab, Lead Jab | tangan, 1 |
| `light_02.fbx` | Cross, tangan kanan | Cross Punch, Punching | tangan, 1 |
| `light_03.fbx` | Hook, tangan kiri | Hook Punch, Left Hook | tangan, 1 |
| `lunge.fbx` | Terjang: lompat kecil, tangan kanan dari atas ke dada | Superman Punch, Jumping Punch | tangan, 1 |
| `back.fbx` | Pukul mundur: langkah mundur lalu jab | Step Back Punch, Retreat Jab | tangan, 1 |
| `heavy.fbx` | Pukulan putar: badan diputar menjauh, lalu pukulan lurus keras | Spinning Punch, Power Punch, Haymaker | tangan, 1 |
| `air_slam.fbx` | Hantaman ke bawah, berlutut | Ground Punch, Ground Slam | — (kena area dari kode) |
| `parry_01.fbx` | Tepis luar | Block / Parry, Outward Block | — |
| `parry_02.fbx` | Tepis dalam | Inward Block, Parry | — |

**Kriteria lulus M1:** file ada, 18 baris (1 karakter + 8 + 9), nama file persis seperti tabel, setting default dari `mixamo/README.md` disalin ke atas daftar. Commit + push, lalu **berhenti dan beri tahu developer** bahwa daftarnya siap. Jangan lanjut ke M2 sebelum ada file di `result/`.

Opsional: gambar referensi pose per jurus di `mixamo/asset/ref/<nama file>.png` (pose kunci saat kena, dari tabel docs/07). Kalau tidak bisa membuat gambar yang jelas, lewati dan tulis di laporan.

---

## 3. M2: Developer download (kamu menunggu)

Developer menaruh FBX di `WORKTREE\mixamo\result\`. Kalau developer ternyata menaruhnya di folder lain (misalnya `C:\repository\unreal_engine\jayadwara\mixamo\result\`), **salin** (bukan pindah) ke `WORKTREE\mixamo\result\`, lalu tulis di laporan supaya developer mengosongkan folder aslinya sendiri. Jangan pernah menghapus apa pun di folder developer.

---

## 4. M3: Cek FBX, lalu pindahkan ke sandbox

Tulis `Hermes/Tools/combo_iter2_cek_fbx.py` (Blender headless: `blender --background --factory-startup --python Hermes/Tools/combo_iter2_cek_fbx.py -- <folder result> <folder log>`). Untuk tiap `*.fbx` di `result/`, impor ke scene kosong, lalu catat ke `Hermes/Art/combo-iter2/Log/cek_fbx.json`:

| Cek | Lulus kalau |
|---|---|
| Nama file | Ada di tabel M1 (huruf kecil, persis) |
| Armature | Tepat 1, tulang diawali `mixamorig` (boleh `mixamorig:` atau `mixamorig1:`), ada `Hips`, `Spine`, `LeftHand`, `RightFoot` |
| `ybot.fbx` | Punya mesh berskin. Tinggi bounding box 160–200 cm (setelah skala impor) |
| Animasi (selain ybot) | Ada action. Frame ≥ 10. FPS scene 30 (tulis nilai aslinya) |
| *In Place* | Perpindahan horizontal `Hips` awal→akhir < 30 cm. Kalau lebih: **bukan gagal**, catat "tidak In Place" + jaraknya. Developer memutuskan download ulang atau tidak |
| Semua file pakai skeleton yang sama | Nama tulang identik dengan `ybot.fbx` (prefix sama). Beda prefix = gagal: retarget satu RTG tidak bisa |

Setelah cek: file **lulus** dipindah (`move`) dari `WORKTREE\mixamo\result\` ke `Hermes/Art/combo-iter2/Mixamo/` (nama tetap). File **gagal** tetap di `result/`; alasannya ditulis di laporan dan dicetak di akhir skrip. Commit FBX lewat LFS (`git lfs status` harus menunjukkan `.fbx` sebagai LFS).

**Kriteria lulus M3:** `ybot.fbx` + 8 file prioritas 1 lulus, `cek_fbx.json` ter-commit, `result/` hanya berisi file gagal (kalau ada).

---

## 5. M4: Import + retarget di sandbox UE

Salin `Tools/ue_import_mixamo.py` ke `Hermes/Tools/combo_iter2_import_mixamo.py`, lalu ubah **hanya** ini:

| Konstanta / bagian | Nilai baru |
|---|---|
| `DEST` (tambahkan) | `"/Game/Hermes/ComboIter2"` |
| `RIG`, `MX`, `RAW` | `f"{DEST}/Rig"`, `f"{DEST}/Mixamo"`, `f"{DEST}/Mixamo/Raw"` |
| `SOURCE_DIR` | `"Hermes/Art/combo-iter2/Mixamo"` |
| `ik_dst = EAL.load_asset(f"{RIG}/IK_Mannequin") or ...` | Selalu `make_ik_rig("IK_Mannequin", manny)` di `RIG` sandbox. Jangan memuat `/Game/Jayadwara/Characters/Aksa/Rig/IK_Mannequin` |
| `MANNY` | Tetap `/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple` (**hanya dibaca**, jadi target retarget) |

Jalankan: `python Tools/ue_remote.py Hermes/Tools/combo_iter2_import_mixamo.py` dari WORKTREE (editor WORKTREE terbuka, level apa pun milikmu).

**Bahaya (insiden SK_Mannequin, AGENTS.md §3):** retarget ke Manny bisa membuat skeleton `SK_Mannequin` ditandai berubah (curve/notify baru). **Jangan simpan aset itu.** Setelah skrip jalan:
1. `git status --porcelain Content/Characters Content/Jayadwara` harus **kosong**. Kalau tidak kosong: `git restore` file itu, lalu tulis di laporan.
2. Saat menutup editor, kalau dialog "Save content" menampilkan aset di luar `/Game/Hermes/`, pilih **Don't Save**.

Lalu tulis `Hermes/Tools/combo_iter2_cek_retarget.py` (UE Python, hanya membaca). Untuk tiap `A_Aksa_Mx_<peran>` di `DEST/Mixamo`, catat ke `Log/cek_retarget.json`:

| Cek | Lulus kalau |
|---|---|
| Panjang | Sama dengan FBX (±1 frame) |
| Skeleton | `SK_Mannequin` (anim di skeleton Manny, siap dipakai Aksa) |
| Tulang kena | Puncak kecepatan tangan/kaki relatif `pelvis` (pakai `strike_timings` dari `Tools/ue_setup_light_combo.py`, disalin) jatuh di tulang yang benar menurut kolom "Kena" M1 (tangan = `hand_l`/`hand_r`, kaki = `foot_l`/`foot_r`), dengan jumlah puncak sesuai (narae chagi 2, berjarak ≥ 0,2 s) |
| Pinggul | `pelvis` tidak pernah di bawah 40 cm dari tanah, kecuali `dodge_*`, `air_slam`, `dodge_forward`. Tulis tinggi minimumnya |
| Tidak rusak | Tidak ada tulang yang lompat > 50 cm antar-frame (tanda retarget patah) |

Ekspor gerak untuk developer: salin `Tools/ue_export_combat_motion.py` ke `Hermes/Tools/combo_iter2_export_motion.py`. Arahkan daftar animasinya ke `DEST/Mixamo/A_Aksa_Mx_*` dan outputnya ke `Hermes/Art/combo-iter2/Log/combat_motion.json`. Developer bisa membuka JSON itu di pemutar "Gerak Jurus Aksa" (link dari Claude).

**Kriteria lulus M4:** semua file lulus M3 punya `A_Aksa_Mx_*` di sandbox, semua baris `cek_retarget.json` lulus (atau gagalnya dijelaskan per file dengan angka), `git status` folder lama bersih, `combat_motion.json` ter-commit. Setelah **3 percobaan** gagal pada satu animasi, lewati animasi itu dan tulis (AGENTS.md §0.5).

---

## 6. M5: Montage, profil, dan level uji di sandbox

Tulis `Hermes/Tools/combo_iter2_setup.py`. Isinya salinan bagian `Tools/ue_setup_light_combo.py` yang membuat montage (`strike_timings`, `combo_after`, `add_combat_notifies`, pembuatan montage), tetapi semua tujuan di `DEST`. Lalu:

1. **Montage** di `DEST/Montages`, satu per peran yang ada: `AM_Hermes_<peran>`. Notify track `Combat`:
   - JD Hit Window dari `strike_timings` (tulang & waktu otomatis). Untuk peran dengan "Kena 2", buat 2 jendela, dan jendela kedua `new_hit = True`.
   - JD Combo Window (`combo_after`) untuk `light_01..03`, `lunge`, `back`, `air`. **Tidak ada** untuk `light_04`, finisher, `heavy`.
   - Dodge, parry, dan `air_slam`: tanpa notify.
   - Blend in 0,08 / out 0,2 (dodge 0,05 / 0,15; parry 0,04 / 0,15).
2. **Profil**: `EAL.duplicate_asset("/Game/Jayadwara/Data/DA_CombatProfile_Human", f"{DEST}/Data/DA_CombatProfile_Human_Hermes")` (duplikat, aslinya tidak disentuh). Isi salinannya:

   | Peran | Field profil |
   |---|---|
   | `light_01..04` | `light_combo[0..3].montage` (langkah lain dan damage tetap) |
   | `lunge`, `back` | `lunge_attack.montage`, `back_attack.montage`. `lunge_attack.move_height` = 60, `move_duration` = 0,35 |
   | `finisher_01/02/03` | `heavy_finishers[0/1/2].montage` (`finisher_03` hanya kalau file-nya ada; kalau tidak, slot 2 dibiarkan kosong) |
   | `heavy` | `heavy_attack.montage` |
   | `air`, `air_slam` | `air_attack.montage`, `air_slam.montage` |
   | `dodge_forward/back/left/right` | `dodge_montages.forward/backward/left/right` |
   | `parry_01/02` | `parry_montages` = [01, 02], `parry_montage_rate` = 1,0 |

   `JDAttackStep` adalah struct. Ambil elemennya, ubah, lalu `set_editor_property` lagi seluruh array/struct-nya (lihat pola `setup_profile` di `ue_setup_light_combo.py`).
3. **Pawn uji**: duplikat `/Game/Jayadwara/Characters/Aksa/BP_Aksa` ke `DEST/BP_Aksa_Hermes`. Di salinannya, `combat_component.combat_profile` = profil Hermes.
4. **Level**: duplikat `/Game/Jayadwara/Maps/Test_Combat` ke `DEST/Maps/Test_Hermes_ComboIter2`, lalu buka **level salinan itu**. Taruh `BP_Aksa_Hermes` di lokasi PlayerStart dengan `auto_possess_player = PLAYER0`. Dummy (`Dummy_01`, `Dummy_Attacker`) ikut dari duplikat. Simpan level milikmu saja.

Catat ke `Log/montage.json`, per montage: tulang & waktu tiap hit window, combo window, panjang, laju. Tabel ringkasnya masuk ke laporan.

**Kriteria lulus M5:** semua montage ada; tulang hit sesuai kolom "Kena"; `finisher_02` punya 2 hit window (yang kedua `new_hit`); combo window hanya di peran yang disebut; profil Hermes terisi (baca balik `get_editor_property` lalu cetak); level terbuka tanpa error di Output Log; `git status` di luar sandbox bersih; `hermes_cek_sandbox.py --base …` LULUS.

---

## 7. M6: Uji tangan oleh developer

Tulis bagian "Cara mencoba" di laporan sebagai checklist untuk developer. Isinya: buka `Test_Hermes_ComboIter2`, Play, `JD.Debug.Hitbox 1`, lalu cek:

| # | Coba | Yang harus terjadi |
|---|---|---|
| 1 | LMB ×4 cepat ke Dummy_01 | 4 serangan beruntun. Ke-4 tendangan putar belakang, kakinya kena dummy (bola merah di kaki) |
| 2 | W + LMB dari ±5 m | Lompat kecil ke dummy, pukulan kena, combo bisa lanjut |
| 3 | S + LMB | Mundur sambil memukul |
| 4 | LMB, lalu E | Dwi chagi (tendangan belakang) |
| 5 | LMB ×2, lalu E | Narae chagi, **dua** kali kena (2 angka damage / 2 bola merah) |
| 6 | Space + LMB ×3 | 2 tendangan terbang memutar, lalu tidak bisa lagi sampai mendarat |
| 7 | Shift + S / A / D / W | Salto belakang / guling kiri / guling kanan / langkah cepat, tidak menembus lantai |
| 8 | RMB tepat waktu ke Dummy_Attacker | Tepisan bergantian 2 gerakan |
| 9 | Main bebas 5 menit | Skor developer 1–5: "pukulan terasa kena" dan "gerakan sesuai jurus" (isi di laporan) |

Animasi yang kelihatan aneh (kaki melayang, tangan menembus badan, arah hadap salah) dicatat developer di laporan per nomor. Kamu boleh memperbaiki waktu hit atau laju montage berdasarkan catatan itu, tapi **di sandbox saja**, dan catat angka sebelum/sesudah.

---

## 8. Laporan & selesai

- Laporan mengikuti format `AGENTS.md` §8 dan diperbarui tiap M selesai. Tabel progres berisi M1–M6.
- Tambahkan bagian **"Untuk Claude"**: daftar peran yang lulus + tulang/waktu hit final per montage (siap disalin ke `STEPS` di `Tools/ue_setup_light_combo.py`), file yang gagal + alasannya, dan perubahan yang kamu sarankan di skrip proyek (jangan kamu kerjakan sendiri).
- Sebelum commit terakhir: `python -I Tools/hermes_cek_sandbox.py --base <titik cabang>` LULUS. Tempel baris terakhirnya di laporan.
- Push `hermes/combo-iter2`. **Jangan merge, jangan buat PR.**

## 9. Sesudahnya: tahap Claude (untuk konteks, bukan tugasmu)

C1. Claude me-review branch: `git diff <titik cabang>...origin/hermes/combo-iter2 --stat` (semua harus di sandbox atau `mixamo/asset/`), menjalankan ulang `combo_iter2_cek_fbx.py` dan `combo_iter2_cek_retarget.py` sendiri, dan membandingkan angkanya dengan laporan.
C2. FBX yang lulus dipindah ke `Art/Mixamo/` (LFS). Developer menjalankan `Tools/ue_import_mixamo.py`, lalu `ue_setup_light_combo.py`, `ue_setup_defense.py`, `ue_setup_parry.py` di proyek utama. Waktu hit final dari laporanmu disalin ke `STEPS` supaya tetap.
C3. `docs/23` diperbarui (animasi Iterasi 2–3 terpasang), lalu PR ke `development`.
