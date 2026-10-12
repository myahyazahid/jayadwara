# 23 — Rencana Fase 1: Prototype Greybox

> **Status: USULAN v0.1 (12 Okt 2026)**, menunggu jawaban developer atas pertanyaan di [bagian 10](#10-pertanyaan-untuk-developer). Angka di dokumen ini adalah usulan awal Claude; yang ditandai **(Q#)** bergantung pada jawaban pertanyaan itu.
> Turunan dari [10](10-roadmap.md#fase-1--prototype-greybox-des-2026--mar-2027) (target bulanan), [18](18-kebutuhan-episode-1.md) (daftar kebutuhan bertanda F1), dan [12](12-technical-design.md) (arsitektur). Kalau dokumen ini bertentangan dengan 12, yang menang 12; perbedaannya dicatat di bagian 4.

## 1. Tujuan & syarat selesai

**Tujuan:** membuktikan inti gameplay **seru** sebelum membuat aset mahal. Semua visual masih kotak, Manny, model proxy, dan Mixamo.

**Gate Fase 1** (dari [10](10-roadmap.md)): satu loop utuh terasa seru menurut developer dan minimal 2–3 playtester:

> Aksa bertarung melawan 3 gelombang kerangka → berubah wujud → Jayadwara mengalahkan boss Jerangkong greybox dua fase di arena dengan gedung yang bisa hancur, tanpa menghancurkan terlalu banyak gedung.

Gate dianggap lulus kalau semua ini terpenuhi:

| # | Kriteria | Cara ukur |
|---|---|---|
| G1 | Combat manusia terasa responsif (input tidak "ketelan", pukulan terasa kena) | Playtest: skor ≥ 4/5 dari mayoritas |
| G2 | Combat raksasa terasa **berat** tapi tetap bisa dikendalikan | Playtest: skor ≥ 4/5 dari mayoritas |
| G3 | Rasa skala: Jayadwara terasa raksasa di antara gedung | Playtest: skor ≥ 4/5 dari mayoritas |
| G4 | Meter sinkronisasi dimengerti tanpa dijelaskan developer | Playtester bisa menjelaskan kenapa meter turun |
| G5 | Loop selesai 10–20 menit tanpa bantuan | Log playtest |
| G6 | 60 FPS di PC developer saat 3 gedung runtuh bersamaan + boss + 6 minion (bukan bersamaan) | `stat unit` / log |
| G7 | Tidak ada crash di 3 sesi playtest | Log |

Kalau G1–G3 gagal: **perbaiki combat dulu** sebelum masuk Fase 2 ([18](18-kebutuhan-episode-1.md#f1--prototype-greybox-des-2026--mar-2027-200-jam)).

## 2. Batas scope

### Masuk Fase 1
- GAS (ASC, atribut, tag, ability) untuk semua karakter.
- Combat manusia: pukulan ringan (combo 3), berat, dodge, tangkis + parry, hit reaction, stagger, soft target, Motion Warping, hit-stop, camera shake.
- Musuh: minion kerangka (pakai Manny), StateTree, 3 gelombang, **bangkit lagi** kalau tidak dihabisi (Q6).
- Checkpoint & kalah (mati → ulang dari checkpoint).
- Transformasi: ganti pawn + ganti IMC + combat raksasa memakai ability yang sama dengan `UJDCombatProfile` raksasa.
- Gedung hancur (Chaos, pre-fractured), meter sinkronisasi, transformasi berakhir paksa.
- Boss Jerangkong greybox: fase 1 rontok & susun ulang 2×, fase 2 tengkorak sebagai titik lemah.
- HUD debug sederhana (bar Health/Stamina/Sync, penanda target) — fungsional, bukan visual final.
- SFX placeholder dari `Audio/Kandidat/` lewat Gameplay Cue.
- Alat debug & cheat (bagian 7), log playtest.

### Tidak masuk (tetap di Fase 2 atau backlog)
| Item | Ke mana | Pengganti di Fase 1 |
|---|---|---|
| Scanner Netra, clue, investigasi | F2 | Kelemahan boss aktif lewat cheat `JD.Weakness 1` atau selalu aktif |
| Dialog, KOMS, briefing, wayang | F2 | Teks debug di layar (opsional) |
| Cutscene transformasi (Sequencer) | F2 | Efek tumbuh/menyusut yang sudah ada |
| Warga dengan AI (`AJDCivilian`) | F2 | Penanda warga statis yang bisa "terkena" (Q11) |
| Jurus spesial #1 Jayadwara | F2 | Finisher / pukulan berat ke tengkorak |
| Menu utama, pause, setting grafis | F2 | Play In Editor / build dev |
| Model final, animasi silat final, VFX final, audio final | F2 | Manny, proxy, Mixamo, kotak, SFX kandidat |
| Motion Matching, Mass AI, skill tree, upgrade | Backlog / F4 | — |

## 3. Titik awal (12 Okt 2026)

| Sudah ada | Dipakai di |
|---|---|
| `AJDCharacterBase` (Move/Look/Jump), `AJDHumanCharacter`, `AJDGiantCharacter` (skala, kapsul, kamera, gerak Froude) | Semua iterasi |
| `AJDPlayerController`: transformasi tombol **T** (ganti pawn, pawn manusia disembunyikan, efek tumbuh/menyusut 2 s) | Iterasi 6 tinggal ditambah IMC raksasa, atribut, dan syarat |
| `BP_Aksa`, `BP_Jayadwara`, `BP_JDPlayerController`, `Test_Greybox`, `Test_GiantScale` | Level uji |
| `SK_Jayadwara` + RTG Mannequin → Jayadwara + socket JSON | Retarget animasi combat (Iterasi 6) |
| Model Aksa (Iterasi 5) & MetaHuman placeholder; mesh logika = Manny ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)) | Combat manusia |
| Chaos + `GeometryCollectionEngine` aktif | Iterasi 7 |
| 23 slot kandidat SFX ([Audio/KANDIDAT.md](../Audio/KANDIDAT.md)) | Gameplay Cue mulai Iterasi 2 |
| Rencana model Jerangkong ([20](20-rencana-model-jerangkong.md), belum disetujui) | Proxy untuk Iterasi 8 (Q12) |

## 4. Arsitektur Fase 1

Mengikuti [12](12-technical-design.md#arsitektur-inti). Tambahan dan penegasan:

### 4.1 Class C++ baru

| Folder | Class | Isi | Iterasi |
|---|---|---|---|
| `Abilities/` | `UJDAbilitySystemComponent` | Turunan ASC: aktivasi ability dari *input tag* (pressed/held/released), buffer input | 1 |
| | `UJDAttributeSet` | Health, MaxHealth, Stamina, MaxStamina, **Poise, MaxPoise**, Sync, MaxSync; meta-attribute `IncomingDamage`, `IncomingPoiseDamage` | 1 |
| | `UJDGameplayAbility` | Basis ability: input tag, kebijakan aktivasi, helper montage & combat profile | 1 |
| | `UJDAbilitySet` (DataAsset) | Ability + GE awal per karakter (Aksa, Jayadwara, minion, boss) | 1 |
| | `UJDInputConfig` (DataAsset) | Input Action → input tag | 1 |
| | GE C++: `UJDGE_Damage`, `UJDGE_StaminaRegen`, `UJDGE_InitAttributes`, `UJDGE_SyncPenalty` | Didefinisikan di C++ (bukan `.uasset`) supaya bisa dibaca & direview; besaran lewat SetByCaller/DataAsset | 1, 7 |
| `Combat/` | `UJDCombatComponent` | Target saat ini, combo state, hit-stop, lapor hit, daftar actor yang sudah kena per serangan | 2 |
| | `UJDCombatProfile` (DataAsset) | Per skala: play rate montage, radius trace, damage, poise damage, shake, hit-stop, jarak warp | 2 |
| | `UJDAnimNotifyState_HitWindow` | Trace sphere/capsule dari socket selama jendela aktif | 2 |
| | `UJDAnimNotifyState_ComboWindow` | Pasang `State.Combat.ComboWindow` | 2 |
| | `UJDAnimNotifyState_Invulnerable` | i-frame dodge | 3 |
| | `UJDGA_LightAttack`, `UJDGA_HeavyAttack`, `UJDGA_Dodge`, `UJDGA_Block` (+ parry) | Ability combat bersama dua skala | 2–3 |
| | `UJDGA_HitReact` | Dipicu event hit: reaksi ringan, stagger, knockdown | 4 |
| | `UJDGA_Finisher` *(versi greybox)* | Pukulan ke musuh yang roboh/stagger; memecah tengkorak (Q6) | 5 |
| | `UJDTargetingComponent` | Soft target: pilih musuh terdekat searah input; boss → titik lemah | 4 |
| `Characters/` | `AJDEnemyBase` | Atribut, mati, roboh, **bangkit lagi** (minion), token serangan | 5 |
| | `AJDBossBase`, `AJDBoss_Jerangkong` | Fase, titik lemah, bagian tubuh yang bisa rontok & menyusun ulang | 8 |
| | `UJDBodyPartComponent` | HP per bagian (lengan/kaki/tengkorak), lepas → aktor fisika → merayap balik | 8 |
| `AI/` | Task & condition StateTree: `MoveToTarget`, `RequestAttackToken`, `PlayAttack`, `Strafe`, `Retreat`, `BossPhase` | Minion & boss | 5, 8 |
| | `UJDEnemyCoordinatorSubsystem` | Token serangan (maks. N penyerang bersamaan) | 5 |
| `World/` | `AJDWaveSpawner` | Gelombang musuh, event selesai, terhubung ke checkpoint | 5 |
| | `AJDCheckpoint`, `UJDCheckpointSubsystem` | Simpan posisi, atribut, gelombang/fase; muat ulang saat mati | 5 |
| | `AJDDestructibleBuilding` | Geometry Collection pre-fractured, ambang kerusakan, `OnBuildingDestroyed`, bersihkan puing | 7 |
| | `AJDCivilianMarker` *(greybox)* | Penanda warga statis; kena → penalti (Q11) | 7 |
| | `AJDDebrisProjectile` | Puing lempar boss fase 2, bisa ditangkis | 8 |
| `Sync/` | `UJDSyncComponent`, `UJDSyncConfig` (DataAsset) | Dengar event gedung/warga → GE penalti; `OnSyncDepleted` | 7 |
| `Core/` | `UJDCheatManager` | Perintah cheat (bagian 7) | 1 → tiap iterasi |
| | `UJDPlaytestLogSubsystem` | Log CSV per sesi (bagian 8) | 9 |
| `UI/` | `UJDHUDWidget` (base) | Binding ke atribut GAS; turunan WBP manusia & raksasa | 1, 7 |

### 4.2 Keputusan arsitektur yang perlu ditegaskan

| # | Hal | Usulan | Alasan |
|---|---|---|---|
| R1 | Letak ASC | Di **karakter** (bukan PlayerState) | Aksa dan Jayadwara adalah dua pawn dengan atribut berbeda; Sync hanya milik Jayadwara. Single-player, tidak butuh replikasi |
| R2 | Health saat transformasi | **Terpisah** per pawn. Aksa kembali dengan Health saat ia ditinggal (Q9) | Sesuai "pawn manusia disembunyikan, bukan dihapus" |
| R3 | Poise | Ditambahkan ke `UJDAttributeSet` | [18](18-kebutuhan-episode-1.md) menyebut "poise sederhana"; GAS membuatnya bisa diregen & dimodifikasi seperti atribut lain |
| R4 | GE di C++ | GE inti didefinisikan di C++; hanya parameter di DataAsset | Claude tidak bisa membaca `.uasset`; review lewat PR jadi mungkin |
| R5 | Feedback (SFX, VFX, shake) | Lewat **Gameplay Cue** (`GameplayCue.Hit.*`, `GameplayCue.Parry`, ...) | Ganti SFX/VFX placeholder → final tanpa menyentuh kode |
| R6 | Input | `IMC_Human` dari `IMC_Default` yang sekarang + `IMC_Giant` baru; aksi combat sama, tombol sama | "Satu sistem, dua skala" juga berlaku untuk tangan pemain |

### 4.3 Gameplay Tags (awal)

Didaftarkan di `Config/DefaultGameplayTags.ini` pada Iterasi 1.

| Kelompok | Tag |
|---|---|
| Input | `Input.Attack.Light`, `Input.Attack.Heavy`, `Input.Dodge`, `Input.Block`, `Input.Transform`, `Input.LockOn` (Q3) |
| Ability | `Ability.Attack.Light`, `Ability.Attack.Heavy`, `Ability.Dodge`, `Ability.Block`, `Ability.HitReact`, `Ability.Finisher` |
| State | `State.Attacking`, `State.Combat.ComboWindow`, `State.Dodging`, `State.Invulnerable`, `State.Blocking`, `State.ParryWindow`, `State.Stagger`, `State.Knockdown`, `State.Dead`, `State.Downed` (minion roboh, bisa bangkit) |
| Event | `Event.Hit`, `Event.Hit.Blocked`, `Event.Hit.Parried`, `Event.Combo.Continue`, `Event.Poise.Broken`, `Event.BodyPart.Detached`, `Event.BodyPart.Reattached` |
| Data | `Data.Damage`, `Data.PoiseDamage`, `Data.SyncPenalty` (SetByCaller) |
| Cue | `GameplayCue.Hit.Light`, `GameplayCue.Hit.Heavy`, `GameplayCue.Hit.Blocked`, `GameplayCue.Parry`, `GameplayCue.Dodge`, `GameplayCue.Bone.Break`, `GameplayCue.Giant.Footstep`, `GameplayCue.Building.Collapse` |
| Boss | `Boss.Phase.1`, `Boss.Phase.2`, `Boss.WeakPoint.Exposed` |

## 5. Angka awal combat (semua dituning lewat DataAsset)

| Item | Manusia | Raksasa | Catatan |
|---|---|---|---|
| Combo ringan | 3 pukulan, damage 10 / 10 / 18 | sama × skala damage boss | Jendela combo dari notify |
| Buffer input | 0,2 s | 0,3 s | Input saat animasi berjalan diingat |
| Pukulan berat | damage 30, poise 40, stamina 25 | sama | Tanpa charge di F1 |
| Dodge | stamina 20, i-frame ±0,25 s | i-frame lebih panjang, jarak × skala | Bisa membatalkan *recovery* serangan setelah frame hit |
| Tangkis | kurangi 80% damage, tiap hit −15 stamina; stamina habis → *guard break* (stagger 1 s) | sama | Tahan tombol |
| Parry | 0,2 s pertama setelah tekan tangkis (Q5) | 0,25 s | Penyerang stagger, `GameplayCue.Parry` |
| Stamina | 100, regen 25/s setelah jeda 0,8 s | sama | |
| Hit-stop | 0,06 s | 0,12 s | Time dilation lokal pada penyerang & korban |
| Play rate montage | 1,0 | **±0,55** (Q1 terkait rasa) | Locomotion raksasa sudah 1/√skala ≈ 0,2; serangan setara itu terlalu lambat, jadi angka ini dicari di Iterasi 6 |
| Minion | HP 30, poise 20, wind-up serangan 0,5 s dengan kedip | — | Maks. **2 penyerang** bersamaan (token) |
| Minion bangkit | roboh 4 s lalu bangkit dengan HP 50% kecuali di-finisher | — | Gelombang 3 saja (Q6) |

## 6. Iterasi

Kapasitas ±50 jam/bulan. Jam di bawah = **jam developer** (build, editor, tuning, uji); jam Claude tidak dihitung, sama seperti [18](18-kebutuhan-episode-1.md#perkiraan-pembagian-jam-kasar). Satu iterasi = satu PR dari branch `claude/f1-iterN` ke `development` (bagian 9). Bulan mengikuti roadmap; kalau mulai lebih awal (Q1), semuanya maju.

| Iter | Nama | Bulan | Jam dev | Level uji |
|---|---|---|---|---|
| 1 | Fondasi GAS | Nov / awal Des 2026 | ±12 | `Test_Combat` |
| 2 | Combo ringan & hit | Des 2026 | ±25 | `Test_Combat` |
| 3 | Berat, dodge, tangkis, parry | Des 2026 | ±25 | `Test_Combat` |
| 4 | Reaksi, stagger, target, warp | Jan 2027 | ±20 | `Test_Combat` |
| 5 | Minion, gelombang, checkpoint | Jan 2027 | ±30 | `Test_Combat` |
| 6 | Transformasi & combat raksasa | Feb 2027 | ±25 | `Test_GiantScale` |
| 7 | Gedung hancur & meter sinkronisasi | Feb – Mar 2027 | ±30 | `Test_Destruction` |
| 8 | Boss Jerangkong greybox | Mar 2027 | ±30 | `Test_Boss` |
| 9 | Loop utuh & playtest | akhir Mar 2027 | ±15 | `Test_Loop` |
| | **Total** | | **±212** | Anggaran F1 ±200 |

### Iterasi 1 — Fondasi GAS
- **Claude:** `UJDAbilitySystemComponent`, `UJDAttributeSet`, `UJDGameplayAbility`, `UJDAbilitySet`, `UJDInputConfig`, GE awal (init atribut, regen stamina, damage), ASC di `AJDCharacterBase` + `IAbilitySystemInterface`, binding input tag di karakter, `DefaultGameplayTags.ini`, `UJDCheatManager` (`JD.God`, `JD.Damage <n>`), `UJDHUDWidget` (bar Health/Stamina). Skrip `Tools/ue_setup_combat.py`: buat `IMC_Human` (salin `IMC_Default`) + IA combat, `DA_InputConfig_Human`, `DA_AbilitySet_Aksa`, level `Test_Combat`.
- **Developer:** build, jalankan skrip, buat `WBP_HUD_Human` dari base class (dua progress bar), uji.
- **Gate:** di `Test_Combat`, bar Health/Stamina tampil; `JD.Damage 10` mengurangi Health; stamina turun lewat cheat lalu regen; `showdebug abilitysystem` menampilkan atribut & tag.

### Iterasi 2 — Combo ringan & hit
- **Claude:** `UJDCombatComponent`, `UJDCombatProfile`, `UJDGA_LightAttack` (3 section, buffer input), notify `HitWindow` & `ComboWindow`, `AJDTrainingDummy` (target diam dengan atribut, angka damage melayang opsional), hit-stop, camera shake, Gameplay Cue hit → SFX kandidat slot 01–02.
- **Developer:** download animasi Mixamo (bagian 6.1), retarget ke Manny, buat `AM_Aksa_LightCombo` (3 section + notify), slot montage di `ABP_Aksa`, `DA_CombatProfile_Human`, tuning.
- **Gate:** combo 3 pukulan ke dummy terasa responsif (tekan cepat = 3 pukulan beruntun, berhenti menekan = berhenti), hit terasa (hit-stop + shake + suara), hitbox terlihat lewat `JD.Debug.Hitbox 1`.

### Iterasi 3 — Pukulan berat, dodge, tangkis, parry
- **Claude:** `UJDGA_HeavyAttack`, `UJDGA_Dodge` (arah dari input, i-frame, biaya stamina, batal recovery), `UJDGA_Block` (tahan, reduksi, guard break, jendela parry), `AJDTrainingDummy` mode **menyerang** berkala dengan wind-up yang terbaca (untuk latihan tangkis/parry), Gameplay Cue blok/parry/dodge.
- **Developer:** animasi berat, dodge 4 arah (atau 1 arah + rotasi, Q10), pose tangkis + hit tangkis; montage; tuning jendela.
- **Gate:** parry ke dummy bisa dilakukan dengan sengaja ≥ 7 dari 10 kali setelah 5 menit latihan; dodge menembus serangan tanpa kena; stamina jadi pertimbangan (tidak bisa spam tangkis/dodge).

### Iterasi 4 — Reaksi, stagger, target, warp
- **Claude:** `UJDGA_HitReact` (ringan / stagger / knockdown dari poise), regen poise, `UJDTargetingComponent` (soft target searah input dalam kerucut; indikator di HUD), Motion Warping ke target, lock kamera (Q3).
- **Developer:** animasi hit react ×2, stagger, knockdown + bangun; warp target di montage; tuning radius target.
- **Gate:** pukulan "menempel" ke musuh terdekat searah stik/WASD tanpa terasa menyedot; pukulan berat membuat dummy stagger; pemain bisa kena stagger juga.

### Iterasi 5 — Minion, gelombang, checkpoint
- **Claude:** `AJDEnemyBase`, minion kerangka (roboh → bangkit lagi, finisher greybox Q6), task StateTree (dekati, strafe, minta token, serang, mundur), `UJDEnemyCoordinatorSubsystem`, `AJDWaveSpawner` (3 gelombang: 3 / 5 / 6), `AJDCheckpoint` + subsystem (mati → muat ulang di awal gelombang 3), cheat `JD.SpawnWave <n>`, `JD.KillAll`.
- **Developer:** `BP_Minion_Skeleton` (Manny abu-abu, skala ±1,0), animasi minion Mixamo (jalan, serang ×2, roboh, bangkit), `ST_Minion`, susun 3 gelombang di `Test_Combat`, tuning.
- **Gate:** 3 gelombang selesai dalam 4–6 menit; musuh tidak menyerang bareng-bareng; gelombang 3 memaksa pemain memakai finisher; mati di gelombang 3 → ulang dari awal gelombang 3.

### Iterasi 6 — Transformasi & combat raksasa
- **Claude:** `IMC_Giant` (skrip), ASC & atribut Jayadwara (`DA_AbilitySet_Jayadwara`, Sync awal penuh), `DA_CombatProfile_Giant`, socket hit dari `SK_Jayadwara_sockets.json`, rig kamera raksasa (framing target, lag, jarak saat combat), syarat transformasi (Q8), `AJDTrainingDummy` skala raksasa.
- **Developer:** retarget montage combat Aksa ke Jayadwara (RTG yang sudah ada), tuning play rate, shake, hit-stop; uji di `Test_GiantScale`.
- **Gate:** combo, berat, dodge, tangkis jalan sebagai Jayadwara dengan **ability yang sama**; terasa berat tapi tidak lamban (G2); bolak-balik transformasi tanpa bug kamera/input.

### Iterasi 7 — Gedung hancur & meter sinkronisasi
- **Claude:** `AJDDestructibleBuilding` (ambang kerusakan dari pukulan, tabrakan badan di atas kecepatan tertentu, proyektil; Q7), pembersih puing (puing → hilang bertahap), `UJDSyncComponent` + `UJDSyncConfig` + `UJDGE_SyncPenalty`, `OnSyncDepleted` → kembali ke manusia + ulang checkpoint, `AJDCivilianMarker` (Q11), `WBP_HUD_Giant` base (bar Sync), cheat `JD.Sync <n>`.
- **Developer:** 3–4 gedung kotak (rumah, warung, menara air) → Fracture Mode → Geometry Collection; `Test_Destruction`; uji performa (berapa gedung runtuh bersamaan sebelum < 60 FPS).
- **Gate:** gedung runtuh meyakinkan dari kamera raksasa; meter turun sesuai DataAsset; meter habis memaksa transformasi berakhir; G6 terpenuhi atau batas jumlah gedung ditetapkan.

### Iterasi 8 — Boss Jerangkong greybox
- **Claude:** `AJDBossBase` (fase, titik lemah, kelemahan dari tag; F1: tag diberikan cheat/otomatis), `AJDBoss_Jerangkong`, `UJDBodyPartComponent` (lengan/kaki rontok saat HP bagian habis → aktor fisika → merayap balik → menyambung lagi), transisi ke fase 2 setelah susun ulang ke-2, tengkorak terekspos (penanda HUD), `AJDDebrisProjectile` (bisa ditangkis), task StateTree boss (sapuan, hantaman, lempar).
- **Developer:** `BP_Boss_Jerangkong` dengan proxy (Q12), animasi dasar (retarget Mannequin + Mixamo zombie/monster), `ST_Boss_Jerangkong`, arena `Test_Boss` (candi kotak + 6 gedung), tuning.
- **Gate:** pemain sadar "memukul badan tidak cukup" di fase 1; fase 2 bisa dimenangkan dengan memukul tengkorak; boss selesai dalam 6–8 menit.

### Iterasi 9 — Loop utuh & playtest
- **Claude:** `UJDPlaytestLogSubsystem` (CSV), alur `Test_Loop` sederhana (trigger area → gelombang → transformasi → boss → layar "Selesai"), daftar pertanyaan playtest (bagian 8), perbaikan bug dari playtest internal.
- **Developer:** rangkai `Test_Loop` (area galian kotak + arena boss), playtest sendiri, lalu 2–3 playtester, isi hasil di dokumen ini.
- **Gate:** Gate Fase 1 (bagian 1). Hasil + keputusan "lanjut F2 / perbaiki combat" dicatat di bagian 11.

### 6.1 Animasi placeholder (Mixamo → Manny)
Didownload developer (butuh akun Adobe), di-retarget ke skeleton Mannequin (sama untuk Aksa dan minion), lalu ke Jayadwara lewat RTG yang sudah ada.

| Untuk | Animasi (cari di Mixamo) | Iter |
|---|---|---|
| Aksa combo ringan | *Jab*, *Cross Punch*, *Hook Punch* (atau *Punching* 3 variasi) | 2 |
| Aksa berat | *Mma Kick* / *Uppercut* | 3 |
| Aksa dodge | *Dodging* / *Standing Dodge* (kiri, kanan, belakang, depan) | 3 |
| Aksa tangkis | *Body Block*, *Center Block*, *Standing Block React* | 3 |
| Reaksi | *Hit Reaction* ×2, *Stunned*, *Knocked Down*, *Getting Up*, *Dying* | 4 |
| Minion | *Zombie Walk*, *Zombie Attack* ×2, *Zombie Dying*, *Zombie Stand Up* | 5 |
| Boss | *Zombie Punching*, *Mutant Swiping*, *Mutant Jump Attack*, *Throw* | 8 |

Silat sungguhan baru di F2 (video-mocap / commission, [18](18-kebutuhan-episode-1.md#b2-animasi)).

### 6.2 Jalur art paralel (Claude, Blender)
| Item | Butuh di | Catatan |
|---|---|---|
| Proxy Jerangkong + 14 potongan `SM_` ([20](20-rencana-model-jerangkong.md) Iterasi 0–1) | Iterasi 5 (minion) & 8 (boss) | Kalau Q12 = "kotak dulu", bergeser ke F2 |
| Greybox gedung (3–4 bentuk, skala dari kamera raksasa) | Iterasi 7 | Bisa skrip Blender atau langsung kotak di UE |

## 7. Alat debug & cheat

Semua lewat `UJDCheatManager` (konsol `~`) dan CVar, hanya di build dev.

| Perintah | Fungsi |
|---|---|
| `JD.God` | Tidak bisa mati |
| `JD.Damage <n>`, `JD.Heal` | Uji atribut |
| `JD.Debug.Hitbox 1` | Gambar trace hit, jendela combo/parry |
| `JD.Debug.AI 1` | State StateTree + token di atas musuh |
| `JD.SpawnWave <n>`, `JD.KillAll` | Gelombang |
| `JD.Sync <n>` | Set meter |
| `JD.Weakness 1` | Paksa kelemahan boss terbuka (pengganti investigasi) |
| `JD.BossPhase <n>` | Lompat ke fase boss |
| `JD.Checkpoint` | Muat ulang checkpoint terakhir |

## 8. Playtest (Iterasi 9)

**Log otomatis per sesi** (`Saved/Playtest/<tanggal>.csv`): waktu per bagian, jumlah mati & di mana, penggunaan tiap aksi (ringan/berat/dodge/tangkis/parry sukses), gedung hancur, sisa Sync, berapa kali boss menyusun ulang, FPS minimum.

**Pertanyaan setelah main** (skala 1–5 + satu kalimat):
1. Pukulan Aksa terasa kena?
2. Ada momen tombol tidak menurut?
3. Jayadwara terasa raksasa? Terasa berat?
4. Kenapa meter di atas turun? (jawaban bebas, untuk G4)
5. Kapan kamu sadar harus memukul kepala?
6. Bagian paling seru / paling membosankan?
7. Mau main lagi kalau ada episode berikutnya?

## 9. Alur kerja per iterasi

1. Claude menulis C++ + skrip Python + update dokumen di `claude/f1-iterN`, lalu membuka PR ke `development`.
2. Developer: tutup editor → `git fetch` + checkout branch → hapus `Binaries/` kalau C++ berubah → buka `.uproject` (build) → jalankan skrip `Tools/` → kerja editor → uji gate.
3. Error build/log ditempel ke Claude → perbaikan di branch yang sama.
4. Gate lulus → developer merge PR, centang iterasi di bagian 11.

PR dibuat kecil (satu iterasi atau setengahnya) karena Claude tidak bisa build UE di cloud; setiap error build hanya ketahuan di PC developer.

## 10. Pertanyaan untuk developer

| # | Pertanyaan | Usulan Claude |
|---|---|---|
| **Q1** | Mulai Fase 1 kapan? Kita lebih cepat dari jadwal di sisi art | Mulai **Iterasi 1 sekarang** (Okt–Nov); Fase 0 tinggal task tracker |
| **Q2** | Referensi rasa combat: Arkham (freeflow, counter), Sekiro (parry & postur), God of War / DMC (combo, berat), atau lainnya? | **Campuran Arkham + Sekiro ringan**: combo sederhana, parry penting, banyak musuh tapi bergantian menyerang. Paling pas dengan silat & gelombang kerangka |
| **Q3** | Kamera combat: soft target saja, atau ada lock-on (tombol) seperti Souls? | Soft target untuk minion; **lock-on tombol** untuk boss raksasa (kamera raksasa sulit tanpa itu) |
| **Q4** | Perangkat utama: keyboard-mouse atau gamepad? Layout tombol? | Desain untuk **gamepad dulu**, KB/M tetap jalan. Gamepad: X ringan, Y berat, A dodge, RB tahan tangkis, RS klik lock-on. KB/M: LMB ringan, RMB berat, Space dodge, Shift tangkis, Tab lock-on |
| **Q5** | Parry: tombol sama dengan tangkis (tekan tepat waktu) atau tombol terpisah? | **Tombol sama**, jendela 0,2 s di awal tangkis |
| **Q6** | Minion bangkit lagi + finisher dikerjakan di F1? ([18](18-kebutuhan-episode-1.md) menaruh finisher di F2, padahal bangkit-lagi di F1) | **Ya, versi greybox di F1**: pukulan berat ke minion roboh = finisher. Ini pelajaran inti "pecahkan kepala" yang dipakai lagi di boss |
| **Q7** | Gedung hancur karena apa saja? | Pukulan raksasa, **tabrakan badan saat lari/terpental**, proyektil boss. Jalan pelan menyenggol tidak menghancurkan |
| **Q8** | Syarat transformasi di F1? | Tombol T **bebas** untuk uji; di `Test_Loop` hanya bisa setelah gelombang 3 (trigger). Kembali ke manusia hanya lewat meter habis / boss kalah |
| **Q9** | Health Jayadwara habis = apa? | Sama dengan Sync habis: kembali ke manusia + ulang checkpoint awal fase boss |
| **Q10** | Dodge: 4 animasi arah, atau 1 animasi (karakter berputar ke arah input)? | **1 arah + rotasi** di F1 (lebih murah, cukup untuk uji rasa) |
| **Q11** | Warga di F1: tidak ada, penanda statis, atau warga sederhana yang lari? | **Penanda statis** (`AJDCivilianMarker`): cukup untuk menguji penalti meter; warga ber-AI tetap F2 |
| **Q12** | Boss F1 pakai proxy Jerangkong dari Blender ([20](20-rencana-model-jerangkong.md) Iterasi 0–1, perlu persetujuan dokumen 20) atau susunan kotak/kapsul di UE? | **Proxy Blender**, dikerjakan Claude paralel mulai Iterasi 3. Potongan `SM_` dibutuhkan untuk mekanik rontok, dan minion juga memakainya |
| **Q13** | Task tracker: GitHub Projects, Trello, atau Notion? Mau Claude buatkan issue per iterasi? | **GitHub Issues** satu per iterasi (Claude yang buat), papan di GitHub Projects (developer) |
| **Q14** | Playtester: siapa dan main di mana (PC kamu atau build dikirim)? | 2–3 teman main di **PC developer**; build terpisah baru di F2 |

## 11. Status & hasil

| Iter | Status | Tanggal | Catatan |
|---|---|---|---|
| 1 | ⬜ | | |
| 2 | ⬜ | | |
| 3 | ⬜ | | |
| 4 | ⬜ | | |
| 5 | ⬜ | | |
| 6 | ⬜ | | Transformasi tombol T sudah ada sejak Iterasi 6 Jayadwara |
| 7 | ⬜ | | |
| 8 | ⬜ | | |
| 9 | ⬜ | | |

**Hasil playtest & keputusan gate:** *(diisi di akhir Fase 1)*

## 12. Risiko Fase 1

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Rasa combat dengan animasi Mixamo terasa "murah" | Gate G1 sulit dinilai | Nilai **respons & feedback** (hit-stop, shake, suara), bukan keindahan gerak; animasi final F2 |
| Build gagal karena Claude tidak bisa compile di cloud | Iterasi tersendat | PR kecil, kode mengikuti pola yang sudah lolos build, error ditempel balik dan diperbaiki di branch yang sama |
| Kurva belajar GAS | Waktu developer membengkak | Logika GAS di C++; developer hanya mengisi DataAsset & montage; `showdebug abilitysystem` sejak Iterasi 1 |
| Mekanik rontok & susun ulang Jerangkong | Fitur paling teknis | Bagian tubuh = `SM_` terpisah (dokumen 20); fallback: bagian hilang lalu muncul lagi dengan efek, tanpa merayap |
| Performa Chaos | G6 gagal | Uji di Iterasi 7, batasi jumlah runtuh bersamaan, puing dibersihkan |
| Scope melebar (ide baru saat main) | F1 molor | Ide baru → backlog; dokumen ini batasnya |
