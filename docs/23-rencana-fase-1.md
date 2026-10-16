# 23 — Rencana Fase 1: Prototype Greybox

> **Status: v0.4 (12 Okt 2026)**. Semua pertanyaan (Q1–Q18) sudah dijawab developer ([bagian 10](#10-keputusan--pertanyaan)); menunggu merge PR. Angka di dokumen ini adalah usulan awal Claude untuk dituning.
> **Tanpa tanggal:** jadwal mulai & selesai tiap iterasi ditentukan developer (Q1). Urutan iterasi tetap.
> Turunan dari [10](10-roadmap.md#fase-1--prototype-greybox-des-2026--mar-2027) (target bulanan), [18](18-kebutuhan-episode-1.md) (daftar kebutuhan bertanda F1), dan [12](12-technical-design.md) (arsitektur). Kalau dokumen ini bertentangan dengan 12, yang menang 12; perbedaannya dicatat di bagian 4.

## 1. Tujuan & syarat selesai

**Tujuan:** membuktikan inti gameplay **seru** sebelum membuat aset mahal. Semua visual masih kotak, Manny, model proxy, dan Mixamo.

**Gate Fase 1** (dari [10](10-roadmap.md)): satu loop utuh terasa seru. Playtest dilakukan **developer sendiri di PC developer** (Q14); playtester lain opsional.

> Aksa bertarung melawan 3 gelombang kerangka → berubah wujud → Jayadwara mengalahkan boss Jerangkong greybox dua fase di arena dengan gedung yang bisa hancur, tanpa menghancurkan terlalu banyak gedung.

Gate dianggap lulus kalau semua ini terpenuhi:

| # | Kriteria | Cara ukur |
|---|---|---|
| G1 | Combat manusia terasa responsif (input tidak "ketelan", pukulan terasa kena) | Form playtest developer: skor ≥ 4/5 |
| G2 | Combat raksasa terasa **berat** tapi tetap bisa dikendalikan | Form playtest developer: skor ≥ 4/5 |
| G3 | Rasa skala: Jayadwara terasa raksasa di antara gedung | Form playtest developer: skor ≥ 4/5 |
| G4 | Meter sinkronisasi terbaca dari layar saja | Tanpa melihat kode/angka debug, jelas kenapa meter turun |
| G5 | Loop selesai 10–20 menit tanpa cheat | Log playtest |
| G6 | 60 FPS di PC developer saat 3 gedung runtuh bersamaan + boss + 6 minion (bukan bersamaan) | `stat unit` / log |
| G7 | Tidak ada crash di 3 sesi playtest | Log |
| G8 | Bisa dimainkan penuh dengan **keyboard-mouse** dan **gamepad** (bagian 4.4) | Satu sesi per perangkat |

Kalau G1–G3 gagal: **perbaiki combat dulu** sebelum masuk Fase 2 ([18](18-kebutuhan-episode-1.md#f1--prototype-greybox-des-2026--mar-2027-200-jam)).

## 2. Batas scope

### Masuk Fase 1
- GAS (ASC, atribut, tag, ability) untuk semua karakter.
- Combat manusia: pukulan ringan (combo 3), berat, dodge, tangkis + parry, hit reaction, stagger, soft target, Motion Warping, hit-stop, camera shake.
- Musuh: minion kerangka (pakai Manny), StateTree, 3 gelombang, **bangkit lagi** kalau tidak dihabisi + **finisher versi greybox** (Q6).
- Checkpoint & kalah (mati → ulang dari checkpoint).
- Transformasi: ganti pawn + ganti IMC + combat raksasa memakai ability yang sama dengan `UJDCombatProfile` raksasa.
- **Kalah sebagai Jayadwara → kembali jadi Aksa di tempat**, bertahan sampai **energi transformasi** penuh lagi, lalu bisa berubah lagi (Q15, bagian 4.5).
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
| Warga dengan AI (`AJDCivilian`) | F2 | Penanda warga statis yang bisa "terkena" (Q11: statis dulu) |
| Jurus spesial #1 Jayadwara | F2 | Finisher / pukulan berat ke tengkorak |
| Menu utama, pause, setting grafis | F2 | Play In Editor / build dev |
| Model final, animasi silat final, VFX final, audio final | F2 | Manny, proxy, Mixamo, kotak, SFX kandidat |
| Jubah upacara Jayadwara (model, animasi pakai/lepas, Niagara, C++ pakai/lepas) — [07](07-gameplay-sistem.md#jubah-upacara), iterasi [26](26-rencana-jubah-jayadwara.md) | F2 (bareng cutscene transformasi) | Tanpa jubah |
| Motion Matching, Mass AI, skill tree, upgrade | Backlog / F4 | — |

## 3. Titik awal (12 Okt 2026)

| Sudah ada | Dipakai di |
|---|---|
| `AJDCharacterBase` (Move/Look/Jump), `AJDHumanCharacter`, `AJDGiantCharacter` (skala, kapsul, kamera, gerak; kelincahan `SpeedScaleExponent` sejak 16 Okt 2026) | Semua iterasi |
| `AJDPlayerController`: transformasi tombol **T** (ganti pawn, pawn manusia disembunyikan, efek tumbuh/menyusut 2 s) | Iterasi 6 tinggal ditambah IMC raksasa, atribut, dan syarat |
| `BP_Aksa`, `BP_Jayadwara`, `BP_JDPlayerController`, `Test_Greybox`, `Test_GiantScale` | Level uji |
| `SK_Jayadwara` + RTG Mannequin → Jayadwara + socket JSON | Retarget animasi combat (Iterasi 6) |
| Model Aksa (Iterasi 5) & MetaHuman placeholder; mesh logika = Manny ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)) | Combat manusia |
| Chaos + `GeometryCollectionEngine` aktif | Iterasi 7 |
| 23 slot kandidat SFX ([Audio/KANDIDAT.md](../Audio/KANDIDAT.md)) | Gameplay Cue mulai Iterasi 2 |
| Model Jerangkong ([20](20-rencana-model-jerangkong.md) jalur B, 12 Okt 2026): `SK_Jerangkong` (boss 30,7 m) & `SK_Kerangka` (minion 1,86 m) + LOD, 14 `SM_Jerangkong_*` + `SK_Jerangkong_parts.json`, `BP_Jerangkong`/`BP_Kerangka`, ABP hasil retarget Mannequin | Iterasi 5 (minion) & 8 (boss); tidak perlu Manny/proxy lagi. **Tidak ditaruh di level uji** sampai iterasinya (berat di laptop developer); `ue_setup_jerangkong.py` → `PLACE_IN_LEVELS = False` |

## 4. Arsitektur Fase 1

Mengikuti [12](12-technical-design.md#arsitektur-inti). Tambahan dan penegasan:

### 4.1 Class C++ baru

| Folder | Class | Isi | Iterasi |
|---|---|---|---|
| `Abilities/` | `UJDAbilitySystemComponent` | Turunan ASC: aktivasi ability dari *input tag* (pressed/held/released), buffer input | 1 |
| | `UJDAttributeSet` | Health, MaxHealth, Stamina, MaxStamina, **Poise, MaxPoise**, Sync, MaxSync, **TransformEnergy, MaxTransformEnergy** (Aksa); meta-attribute `IncomingDamage`, `IncomingPoiseDamage` | 1 |
| | `UJDGameplayAbility` | Basis ability: input tag, kebijakan aktivasi, helper montage & combat profile | 1 |
| | `UJDAbilitySet` (DataAsset) | Ability + GE awal per karakter (Aksa, Jayadwara, minion, boss) | 1 |
| | `UJDInputConfig` (DataAsset) | Input Action → input tag | 1 |
| | GE C++: `UJDGE_Damage`, `UJDGE_StaminaRegen`, `UJDGE_InitAttributes`, `UJDGE_SyncPenalty` | Didefinisikan di C++ (bukan `.uasset`) supaya bisa dibaca & direview; besaran lewat SetByCaller/DataAsset | 1, 7 |
| `Combat/` | `UJDCombatComponent` | Target saat ini, combo state, hit-stop, lapor hit, daftar actor yang sudah kena per serangan | 2 |
| | `UJDCombatProfile` (DataAsset) | Per skala: play rate montage, radius trace, damage, poise damage, shake, hit-stop, jarak warp | 2 |
| | `UJDAnimNotifyState_HitWindow` | Trace sphere/capsule dari socket selama jendela aktif | 2 |
| | `UJDAnimNotifyState_ComboWindow` | Pasang `State.Combat.ComboWindow` | 2 |
| | ~~`UJDAnimNotifyState_Invulnerable`~~ | i-frame dodge. **Diganti** (Iterasi 3): jendela waktu di `UJDCombatProfile` (`DodgeIFrameStart/Duration`), karena dodge harus jalan tanpa animasi; notify bisa ditambah kalau animasi final butuh | 3 |
| | `UJDGA_LightAttack`, `UJDGA_HeavyAttack`, `UJDGA_Dodge`, `UJDGA_Block` (+ parry) | Ability combat bersama dua skala | 2–3 |
| | `UJDGA_HitReact` | Dipicu event hit: reaksi ringan, stagger, knockdown | 4 |
| | `UJDGA_Finisher` *(versi greybox)* | Pukulan berat ke minion yang roboh → tengkorak hancur, tidak bangkit lagi; animasi pukulan berat biasa (Q6). Versi dengan animasi khusus di F2 | 5 |
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
| R2 | Health saat transformasi | **Terpisah** per pawn. Aksa kembali dengan Health saat ia ditinggal. Health Jayadwara habis → kembali jadi Aksa di tempat (Q9, Q15, bagian 4.5) | Sesuai "pawn manusia disembunyikan, bukan dihapus" |
| R3 | Poise | Ditambahkan ke `UJDAttributeSet` | [18](18-kebutuhan-episode-1.md) menyebut "poise sederhana"; GAS membuatnya bisa diregen & dimodifikasi seperti atribut lain |
| R4 | GE di C++ | GE inti didefinisikan di C++; hanya parameter di DataAsset | Claude tidak bisa membaca `.uasset`; review lewat PR jadi mungkin |
| R5 | Feedback (SFX, VFX, shake) | Lewat **Gameplay Cue** (`GameplayCue.Hit.*`, `GameplayCue.Parry`, ...) | Ganti SFX/VFX placeholder → final tanpa menyentuh kode |
| R6 | Input | `IMC_Human` dari `IMC_Default` yang sekarang + `IMC_Giant` baru; aksi combat sama, tombol sama (bagian 4.4) | "Satu sistem, dua skala" juga berlaku untuk tangan pemain |

### 4.3 Gameplay Tags (awal)

Didaftarkan sebagai **native tag C++** (`Abilities/JDGameplayTags.h`, `UE_DEFINE_GAMEPLAY_TAG`) pada Iterasi 1, bukan `Config/DefaultGameplayTags.ini`: kode memakai `JDGameplayTags::Input_Attack_Light` tanpa string, dan tag tetap muncul di pemilih tag editor. Tambahan dari implementasi: `Data.StaminaRegen`, `Data.Init.Max*` (SetByCaller atribut awal), `Cheat.God`.

| Kelompok | Tag |
|---|---|
| Input | `Input.Attack.Light`, `Input.Attack.Heavy`, `Input.Dodge`, `Input.Block`, `Input.Jump`, `Input.Transform`, `Input.LockOn` |
| Ability | `Ability.Attack.Light`, `Ability.Attack.Heavy`, `Ability.Dodge`, `Ability.Block`, `Ability.HitReact`, `Ability.Finisher` |
| State | `State.Transform.Ready`, `State.Attacking`, `State.Combat.ComboWindow`, `State.Dodging`, `State.Invulnerable`, `State.Blocking`, `State.ParryWindow`, `State.Stagger`, `State.Knockdown`, `State.Dead`, `State.Downed` (minion roboh, bisa bangkit) |
| Event | `Event.Hit`, `Event.Hit.Blocked`, `Event.Hit.Parried`, `Event.Combo.Continue`, `Event.Poise.Broken`, `Event.BodyPart.Detached`, `Event.BodyPart.Reattached` |
| Data | `Data.Damage`, `Data.PoiseDamage`, `Data.SyncPenalty` (SetByCaller) |
| Cue | `GameplayCue.Hit.Light`, `GameplayCue.Hit.Heavy`, `GameplayCue.Hit.Blocked`, `GameplayCue.Parry`, `GameplayCue.Dodge`, `GameplayCue.Bone.Break`, `GameplayCue.Giant.Footstep`, `GameplayCue.Building.Collapse` |
| Boss | `Boss.Phase.1`, `Boss.Phase.2`, `Boss.WeakPoint.Exposed` |

### 4.4 Kontrol (Q4, Q5, Q8)

**Keyboard-mouse adalah perangkat utama**; gamepad wajib jalan penuh. Satu Input Action punya dua pemetaan di IMC yang sama.

| Aksi | Keyboard-mouse | PlayStation | Xbox / generik (layout Xbox) |
|---|---|---|---|
| Gerak / kamera | WASD / mouse | L-stick / R-stick | L-stick / R-stick |
| Pukulan ringan | **LMB** | □ | X |
| Pukulan berat (+ finisher) | **E** | △ | Y |
| Tangkis (tahan) + parry (tekan tepat waktu) | **RMB** | **R2** | RT |
| Dodge (arah dari gerak) | **Left Shift** | ○ | B |
| Lompat | **Space** | ✕ | A |
| Lock-on (boss raksasa) | **Q** / klik tengah | R3 | RS (klik) |
| Transformasi | **T** | **L1 + R1** | LB + RB |
| Lepas jubah (raksasa) | otomatis saat lock-on pertama / aksi combat pertama ([07](07-gameplay-sistem.md#jubah-upacara)) | — | — |
| Cheat/konsol (dev) | `~` | — | — |

Keyboard disetujui developer (Q5): tangan kiri WASD + E/Shift/Space/Q/T, tangan kanan di mouse. Tangkis di **RMB** karena parry butuh ketepatan waktu dan jari di mouse paling cepat (pola Sekiro di PC). Kamera tetap di mouse, jadi tidak perlu kamera otomatis (Q18).

**Catatan teknis gamepad:**
- **Xbox (XInput)** langsung terbaca Unreal.
- **DualShock 4 / DualSense** dan **gamepad USB generik** (DirectInput) **tidak** terbaca Unreal secara bawaan. Rilis Steam: **Steam Input** memetakan semuanya ke layout Xbox. Selama pengembangan (PIE di luar Steam): DS4Windows untuk DualShock/DualSense asli; **x360ce** (Xbox 360 Controller Emulator) untuk pad generik, atau plugin **RawInput** (bawaan UE, perlu konfigurasi per perangkat).
- **Controller developer (Q16): pad USB generik gaya PlayStation**, dua analog, tombol bernomor 1–4 (1 = atas/△, 2 = kanan/○, 3 = bawah/✕, 4 = kiri/□), tombol ANALOG harus menyala supaya stik aktif. Jalur uji: x360ce → terbaca sebagai pad Xbox di UE. Disiapkan di Iterasi 1.
- Pad tanpa dua analog stick (mis. gaya PS1 digital) tidak bisa mengendalikan kamera dengan baik.
- Ikon tombol sesuai perangkat (prompt tutorial) tetap F2.

### 4.5 Kalah sebagai Jayadwara & energi transformasi (Q15)

Seperti serial tokusatsu: kalau Jayadwara kalah, ia kembali jadi manusia, dan pertarungan berlanjut.

1. Health Jayadwara 0 **atau meter Sync habis** (Q17) → efek menyusut (yang sudah ada) → **Aksa muncul di tempat Jayadwara jatuh**. Boss tetap di fase & HP-nya (progres tidak hilang).
2. Aksa main biasa, tidak bisa melukai boss raksasa; boss tetap menyerang (injakan, puing) → **menghindar** dengan dodge & lari.
3. **Energi transformasi** (`TransformEnergy`, HUD manusia) habis setelah kalah dan terisi lagi seiring waktu (awal: penuh dalam ±40 s). Saat penuh: `State.Transform.Ready` → tekan **T / L1+R1** → berubah lagi.
4. Jayadwara kembali dengan Health ±50% (kalau kalah) atau Sync ±50% (kalau meter habis); dituning.
5. Aksa mati saat jadi manusia → ulang dari checkpoint awal fase boss.

Aturan IP ([08](08-requirement-produksi.md)): energi ditampilkan sebagai **bar di HUD**, bukan lampu/permata di dada yang berkedip; tidak ada batas waktu 3 menit selama jadi raksasa.

Untuk transformasi pertama Ep 1 (cutscene) dan `Test_Loop`, energi diisi penuh oleh trigger setelah gelombang 3.

## 5. Angka awal combat (semua dituning lewat DataAsset)

| Item | Manusia | Raksasa | Catatan |
|---|---|---|---|
| Combo ringan | **4 pukulan**, damage 10 / 10 / 12 / 20 (dulu 3 pukulan 10 / 10 / 18) | sama × skala damage boss | Jendela combo dari notify. Combo & arah: [07](07-gameplay-sistem.md#combo--arah) (16 Okt 2026) |
| Pembuka arah | terjang (maju, target > 2,5 m, maks. 6 m, berhenti 1 m dari target), mundur 1,5 m sambil memukul; damage 10, poise 8; cari target 8 m | jarak × skala raksasa × 0,6 | Arah input relatif ke target terdekat; kiri/kanan = combo biasa sampai soft target Iterasi 4 |
| Serangan udara | pukulan udara damage 10, maks. 2 per lompatan, "ngambang" 0,3 s (gravitasi ×0,1); hantaman ke bawah 2000 cm/s, radius 2,5 m, damage/poise/stamina = pukulan berat, jeda 0,35 s | kecepatan × skala × 0,6, radius × skala | [07](07-gameplay-sistem.md#serangan-udara) (16 Okt 2026); dodge & tangkis tidak bisa di udara |
| Cabang finisher | pukulan berat setelah pukulan 1 / 2 punya animasi sendiri; angka sama dengan pukulan berat | sama | `HeavyFinishers` di `DA_CombatProfile_*`; slot kosong = pukulan berat biasa |
| Buffer input | 0,2 s | 0,3 s | Input saat animasi berjalan diingat |
| Pukulan berat | damage 30, poise 40, stamina 25 | sama | Tanpa charge di F1 |
| Dodge | stamina 20, i-frame ±0,25 s | durasi 0,35 s & i-frame 0,25 s (sama dengan manusia, ala Mebius), jarak ±55 m | Bisa membatalkan *recovery* serangan setelah frame hit |
| Tangkis | kurangi 80% damage, tiap hit −15 stamina; stamina habis → *guard break* (stagger 1 s) | sama | Tahan tombol |
| Parry | 0,2 s pertama setelah tekan tangkis (tombol sama, Q5) | 0,25 s | Penyerang stagger, `GameplayCue.Parry` |
| Stamina | 100, regen 25/s setelah jeda 0,8 s | sama | |
| Hit-stop | 0,06 s | 0,15 s | Time dilation lokal pada penyerang & korban |
| Play rate montage | 1,0 | **1,0** | Ala Mebius (keputusan developer 16 Okt 2026): serangan raksasa secepat manusia; dulu ±0,55. Berat dari hit-stop & shake |
| Gerak raksasa | lari 5 m/s, berbalik 500°/s | **lari ±70 m/s, animasi ±0,6×, berbalik 720°/s, akselerasi setara manusia, lompat ×1,25** | `SpeedScaleExponent` 0,83 di `BP_Jayadwara2` (0,5 = Froude/berat lama: lari ±24 m/s, animasi 0,2×, berbalik ±100°/s). Boss `BP_Jerangkong` tetap 0,5. Ubah lalu jalankan `Tools/ue_setup_giant_speed.py` + `ue_setup_giant_combo.py` |
| Minion | HP 30, poise 20, wind-up serangan 0,5 s dengan kedip | — | Maks. **2 penyerang** bersamaan (token) |
| Minion bangkit | roboh 4 s lalu bangkit dengan HP 50% kecuali di-finisher | — | Gelombang 3 saja |
| Energi transformasi | 0 → penuh ±40 s setelah kalah | Health kembali ±50% | Bagian 4.5 |
| Dodge arah | 4 animasi (depan, belakang, kiri, kanan) relatif kamera (Q10) | sama | |
| Gedung | Kerusakan sebanding gaya: pukulan, tabrakan badan (termasuk jalan pelan, kerusakan kecil), terpental, proyektil (Q7) | — | Ambang dituning supaya meter tidak terlalu kejam |

## 6. Iterasi

Kapasitas ±50 jam/bulan. Jam di bawah = **jam developer** (build, editor, tuning, uji); jam Claude tidak dihitung, sama seperti [18](18-kebutuhan-episode-1.md#perkiraan-pembagian-jam-kasar). Satu iterasi = satu PR dari branch `claude/f1-iterN` ke `development` (bagian 9). Iterasi dikerjakan berurutan; kapan mulai dan selesai ditentukan developer (Q1).

| Iter | Nama | Jam dev | Level uji |
|---|---|---|---|
| 1 | Fondasi GAS | ±12 | `Test_Combat` |
| 2 | Combo ringan & hit | ±25 | `Test_Combat` |
| 3 | Berat, dodge, tangkis, parry | ±25 | `Test_Combat` |
| 4 | Reaksi, stagger, target, warp | ±20 | `Test_Combat` |
| 5 | Minion, gelombang, checkpoint | ±30 | `Test_Combat` |
| 6 | Transformasi & combat raksasa | ±25 | `Test_GiantScale` |
| 7 | Gedung hancur & meter sinkronisasi | ±30 | `Test_Destruction` |
| 8 | Boss Jerangkong greybox | ±30 | `Test_Boss` |
| 9 | Loop utuh & playtest | ±15 | `Test_Loop` |
| | **Total** | **±212** | Anggaran F1 ±200 |

### Iterasi 1 — Fondasi GAS
- **Claude:** pemetaan kontrol KB/M + gamepad (bagian 4.4), `UJDAbilitySystemComponent`, `UJDAttributeSet`, `UJDGameplayAbility`, `UJDAbilitySet`, `UJDInputConfig`, GE awal (init atribut, regen stamina, damage), ASC di `AJDCharacterBase` + `IAbilitySystemInterface`, binding input tag di karakter (+ buffer input di ASC), native gameplay tag (`JDGameplayTags`), `UJDCheatManager` (`JD.God`, `JD.Damage <n>`, `JD.Heal`, `JD.Stamina <n>`, `JD.Debug.Input`), `UJDHUDWidget` (bar Health/Stamina/Energi, layout bawaan dibuat C++ sehingga jalan tanpa WBP). Skrip `Tools/ue_setup_combat.py`: buat `IMC_Human` (salin `IMC_Default`) + IA combat + chord L1+R1, `DA_InputConfig_Human`, `DA_AbilitySet_Aksa`, isi `BP_Aksa` & `BP_JDPlayerController`, level `Test_Combat` (tanpa musuh).
- **Developer:** build, (Claude menjalankan skrip lewat `ue_remote.py`), uji dengan keyboard-mouse dan pad generik lewat x360ce (Q16). `WBP_HUD_Human` opsional (turunan `UJDHUDWidget`, progress bar bernama `HealthBar`/`StaminaBar`).
- **Gate:** di `Test_Combat`, bar Health/Stamina tampil; gerak + kamera jalan di KB/M dan gamepad; `JD.Damage 10` mengurangi Health; stamina turun lewat cheat lalu regen; `showdebug abilitysystem` menampilkan atribut & tag.

### Iterasi 2 — Combo ringan & hit
- **Claude:** `UJDCombatComponent`, `UJDCombatProfile`, `UJDGA_LightAttack` (3 section, buffer input), notify `HitWindow` & `ComboWindow`, `AJDTrainingDummy` (target diam dengan atribut, angka damage melayang opsional), hit-stop, camera shake, Gameplay Cue hit → SFX kandidat slot 01–02.
- **Developer:** uji rasa & tuning. (Implementasi 12 Okt 2026: **satu montage per langkah** `AM_Aksa_Light_01..03`, bukan satu montage 3 section, supaya bisa dibuat & diisi notify dari Python; placeholder `MM_Attack_01..03` bawaan Mannequin dengan root motion, waktu hit dari analisis kecepatan tulang. Mixamo *Jab/Cross/Hook* opsional: ganti `SOURCE`/waktu di `Tools/ue_setup_light_combo.py` lalu jalankan ulang. `ABP_Aksa` sudah punya `DefaultSlot`.)
- **Gate:** combo 3 pukulan ke dummy terasa responsif (tekan cepat = 3 pukulan beruntun, berhenti menekan = berhenti), hit terasa (hit-stop + shake + suara), hitbox terlihat lewat `JD.Debug.Hitbox 1`.
- **Revisi 16 Okt 2026 (keputusan developer, [07](07-gameplay-sistem.md#combo--arah)):** combo jadi **4 pukulan** (langkah 4 sementara `MM_ChargedAttack`), pembuka **terjang** (maju + pukul ke target yang agak jauh) dan **mundur** (mundur + pukul), serta **cabang finisher** pukulan berat setelah pukulan 1 / 2. C++: `FJDAttackStep` dapat `MoveDistance/MoveDuration/bStopAtTarget`; `UJDCombatProfile` dapat `LungeAttack`, `BackAttack`, `HeavyFinishers`, jarak arah; `UJDCombatComponent::FindNearestTarget` (sementara sampai `UJDTargetingComponent`). Skrip: `ue_setup_light_combo.py` (Aksa), `ue_setup_jayadwara2.py` (retarget `MM_ChargedAttack`) lalu `ue_setup_giant_combo.py` (Jayadwara). Waktu hit langkah 4 dicari otomatis dari puncak kecepatan tangan/kaki (lihat log). **Gate tambahan:** tekan cepat = 4 pukulan; maju + pukul dari ±5 m menerjang lalu combo berlanjut; mundur + pukul mundur sambil memukul; berat setelah pukulan 1 dan 2 terlihat berbeda.
- **Serangan udara (16 Okt 2026, [07](07-gameplay-sistem.md#serangan-udara)):** `AirAttack` (+ `AirComboMax`, `AirHang*`) dan `AirSlam` (+ `AirSlamSpeed/Radius/Recovery`) di `UJDCombatProfile`; `UJDCombatComponent::ApplyAreaHit` + `OnLanded`; tangkis diblok di udara. Placeholder tanpa root motion: udara = salinan `MM_Attack_03`, hantaman = salinan `MM_ChargedAttack` (skrip yang sama). **Gate:** lompat + LMB ×2 = 2 tendangan melayang lalu tidak bisa lagi sampai mendarat; lompat + E di dekat dummy = menukik, dummy kena saat mendarat.

### Iterasi 3 — Pukulan berat, dodge, tangkis, parry
- **Claude:** `UJDGA_HeavyAttack`, `UJDGA_Dodge` (arah dari input, i-frame, biaya stamina, batal recovery), `UJDGA_Block` (tahan, reduksi, guard break, jendela parry), `AJDTrainingDummy` mode **menyerang** berkala dengan wind-up yang terbaca (untuk latihan tangkis/parry), Gameplay Cue blok/parry/dodge.
- **Developer:** animasi berat, dodge 4 arah (Q10), pose tangkis + hit tangkis; montage; tuning jendela.
- **Gate:** parry ke dummy bisa dilakukan dengan sengaja ≥ 7 dari 10 kali setelah 5 menit latihan; dodge menembus serangan tanpa kena; stamina jadi pertimbangan (tidak bisa spam tangkis/dodge).

### Iterasi 4 — Reaksi, stagger, target, warp
- **Claude:** `UJDGA_HitReact` (ringan / stagger / knockdown dari poise), regen poise, `UJDTargetingComponent` (soft target searah input dalam kerucut; indikator di HUD; Q3), Motion Warping ke target, lock kamera (Q3).
- **Developer:** animasi hit react ×2, stagger, knockdown + bangun; warp target di montage; tuning radius target.
- **Gate:** pukulan "menempel" ke musuh terdekat searah stik/WASD tanpa terasa menyedot; pukulan berat membuat dummy stagger; pemain bisa kena stagger juga.

### Iterasi 5 — Minion, gelombang, checkpoint
- **Claude:** `AJDEnemyBase`, minion kerangka (roboh → bangkit lagi, finisher greybox Q6), task StateTree (dekati, strafe, minta token, serang, mundur), `UJDEnemyCoordinatorSubsystem`, `AJDWaveSpawner` (3 gelombang: 3 / 5 / 6), `AJDCheckpoint` + subsystem (mati → muat ulang di awal gelombang 3), cheat `JD.SpawnWave <n>`, `JD.KillAll`.
- **Developer:** `BP_Minion_Skeleton` (turunan `AJDEnemyBase` dengan `SK_Kerangka` + `ABP_Kerangka`; model sudah ada, lihat bagian 3), animasi minion Mixamo (di-retarget ke `SK_Kerangka`) (jalan, serang ×2, roboh, bangkit), `ST_Minion`, susun 3 gelombang di `Test_Combat`, tuning.
- **Gate:** 3 gelombang selesai dalam 4–6 menit; musuh tidak menyerang bareng-bareng; gelombang 3 memaksa pemain memakai finisher; mati di gelombang 3 → ulang dari awal gelombang 3.

### Iterasi 6 — Transformasi & combat raksasa
- **Claude:** `IMC_Giant` (skrip), ASC & atribut Jayadwara (`DA_AbilitySet_Jayadwara`, Sync awal penuh), `DA_CombatProfile_Giant`, socket hit dari `SK_Jayadwara_sockets.json`, rig kamera raksasa (framing target, lag, jarak saat combat) + **lock-on boss** (Q3), transformasi tombol **T** / **L1+R1** dengan syarat (Q8), **kalah → Aksa muncul di tempat + `TransformEnergy` + berubah lagi** (bagian 4.5), `AJDTrainingDummy` skala raksasa.
- **Developer:** retarget montage combat Aksa ke Jayadwara (RTG yang sudah ada), tuning play rate, shake, hit-stop; uji di `Test_GiantScale`.
- **Gate:** combo, berat, dodge, tangkis jalan sebagai Jayadwara dengan **ability yang sama**; terasa raksasa tapi **gesit** (G2, ala Mebius: berat dari impact, bukan dari kelambatan); bolak-balik transformasi tanpa bug kamera/input; kalah → jadi Aksa di tempat → energi penuh → berubah lagi berjalan tanpa reload.

### Iterasi 7 — Gedung hancur & meter sinkronisasi
- **Claude:** `AJDDestructibleBuilding` (kerusakan sebanding gaya dari pukulan, tabrakan badan, terpental, proyektil; Q7), pembersih puing (puing → hilang bertahap), `UJDSyncComponent` + `UJDSyncConfig` + `UJDGE_SyncPenalty`, `OnSyncDepleted` → kembali jadi Aksa di tempat (alur bagian 4.5, Q17), `AJDCivilianMarker` (Q11), `WBP_HUD_Giant` base (bar Sync), cheat `JD.Sync <n>`.
- **Developer:** 3–4 gedung kotak (rumah, warung, menara air) → Fracture Mode → Geometry Collection; `Test_Destruction`; uji performa (berapa gedung runtuh bersamaan sebelum < 60 FPS).
- **Gate:** gedung runtuh meyakinkan dari kamera raksasa; meter turun sesuai DataAsset; meter habis memaksa transformasi berakhir; G6 terpenuhi atau batas jumlah gedung ditetapkan.

### Iterasi 8 — Boss Jerangkong greybox
- **Claude:** `AJDBossBase` (fase, titik lemah, kelemahan dari tag; F1: tag diberikan cheat/otomatis), `AJDBoss_Jerangkong`, `UJDBodyPartComponent` (lengan/kaki rontok saat HP bagian habis → aktor fisika → merayap balik → menyambung lagi), transisi ke fase 2 setelah susun ulang ke-2, tengkorak terekspos (penanda HUD), `AJDDebrisProjectile` (bisa ditangkis), task StateTree boss (sapuan, hantaman, lempar).
- **Developer:** `BP_Boss_Jerangkong` (turunan `AJDBoss_Jerangkong` dengan `SK_Jerangkong`; model, 14 `SM_` potongan & `parts.json` sudah ada, bagian 6.2), animasi dasar (retarget Mannequin + Mixamo zombie/monster), `ST_Boss_Jerangkong`, arena `Test_Boss` (candi kotak + 6 gedung), tuning.
- **Gate:** pemain sadar "memukul badan tidak cukup" di fase 1; fase 2 bisa dimenangkan dengan memukul tengkorak; boss selesai dalam 6–8 menit.

### Iterasi 9 — Loop utuh & playtest
- **Claude:** `UJDPlaytestLogSubsystem` (CSV), alur `Test_Loop` sederhana (trigger area → gelombang → transformasi → boss → layar "Selesai"), daftar pertanyaan playtest (bagian 8), perbaikan bug dari playtest internal.
- **Developer:** rangkai `Test_Loop` (area galian kotak + arena boss), playtest sendiri di PC developer (KB/M dan gamepad), isi hasil di dokumen ini.
- **Gate:** Gate Fase 1 (bagian 1). Hasil + keputusan "lanjut F2 / perbaiki combat" dicatat di bagian 11.

### 6.1 Animasi placeholder (Mixamo → Manny)
Didownload developer (butuh akun Adobe), di-retarget ke skeleton Mannequin (sama untuk Aksa dan minion), lalu ke Jayadwara lewat RTG yang sudah ada.

| Untuk | Animasi (cari di Mixamo) | Iter |
|---|---|---|
| Aksa combo ringan | *Jab*, *Cross Punch*, *Hook Punch*, combo 4 *Spinning Back Kick* / *Spinning Hook Kick* (dwi huryeo chagi) | 2 |
| Aksa pembuka arah | Terjang (lompat kecil, pukulan dari atas ke dada): *Jump Attack* / *Superman Punch* / *Overhand Punch*; mundur: *Back Step Punch* | 2 |
| Aksa serangan udara | *Flying Kick* / *Jump Spin Kick* / *Tornado Kick* (tendangan terbang memutar), *Jump Down Attack* / *Ground Slam* (hantaman) | 2 |
| Aksa cabang finisher | Finisher 1 *Back Kick* / *Spinning Back Kick* (dwi chagi); finisher 2 *Double Kick* / *Jumping Double Kick* (narae chagi) | 2–3 |
| Aksa berat | Pukulan putar satu tangan: *Cross Punch* / *Heavy Punch* / *Spinning Punch* (melangkah + putar badan) | 3 |
| Aksa dodge | Belakang *Back Flip*; kiri/kanan *Dodge Roll* / *Cartwheel*; depan *Quick Step* / *Dodging* ([07](07-gameplay-sistem.md#dodge-per-arah)) | 3 |
| Aksa tangkis | *Body Block*, *Center Block*, *Standing Block React* | 3 |
| Reaksi | *Hit Reaction* ×2, *Stunned*, *Knocked Down*, *Getting Up*, *Dying* | 4 |
| Minion | *Zombie Walk*, *Zombie Attack* ×2, *Zombie Dying*, *Zombie Stand Up* | 5 |
| Boss | *Zombie Punching*, *Mutant Swiping*, *Mutant Jump Attack*, *Throw* | 8 |

Silat sungguhan baru di F2 (video-mocap / commission, [18](18-kebutuhan-episode-1.md#b2-animasi)).

### 6.2 Jalur art paralel (Blender)
| Item | Butuh di | Catatan |
|---|---|---|
| Model Jerangkong + 14 potongan `SM_` ([20](20-rencana-model-jerangkong.md) jalur B) | Iterasi 5 (minion) & 8 (boss) | ✅ **Selesai 12 Okt 2026**: model dibuat developer dengan Tripo AI, dirapikan Claude (rig, potongan, tekstur, LOD, import UE). Pivot SM & rumus pemunculan saat rontok ada di [20](20-rencana-model-jerangkong.md) dan `Art/Export/SK_Jerangkong_parts.json` (dipakai `UJDBodyPartComponent`). Sisa: retak tengkorak bergeometri (opsional), uji FPS |
| Greybox gedung (3–4 bentuk, skala dari kamera raksasa) | Iterasi 7 | Bisa skrip Blender atau langsung kotak di UE |

## 7. Alat debug & cheat

Semua lewat `UJDCheatManager` (konsol `~`) dan CVar, hanya di build dev.

| Perintah | Fungsi |
|---|---|
| `JD.God` | Tidak bisa mati |
| `JD.Damage <n>`, `JD.Heal` | Uji atribut (damage lewat `UJDGE_Damage`, jalur yang sama dengan pukulan musuh) |
| `JD.Stamina <n>` | Kurangi stamina n → regen mulai setelah jeda 0,8 s |
| `JD.Debug.Input 1` | Tampilkan input tag yang ditekan/dilepas di layar (uji pemetaan KB/M & gamepad) |
| `JD.Debug.Hitbox 1` | Gambar sweep hitbox (hijau) & titik kena (merah) |
| `JD.Debug.AI 1` | State StateTree + token di atas musuh |
| `JD.SpawnWave <n>`, `JD.KillAll` | Gelombang |
| `JD.Sync <n>` | Set meter |
| `JD.Dummy.Attack <0\|1>` | Mode menyerang semua training dummy (tanpa argumen = bolak-balik) |
| `JD.Input <tag> <1\|0>` | Tekan/lepas input tag pawn pemain tanpa perangkat (uji otomatis, mis. `JD.Input Input.Block 1`) |
| `JD.Debug.Combat 1` | (bawaan nyala) Tulis hasil serangan yang melibatkan pemain di layar: PARRY!, Ditangkis, GUARD BREAK, Menghindar, Kena |
| `JD.Weakness 1` | Paksa kelemahan boss terbuka (pengganti investigasi) |
| `JD.BossPhase <n>` | Lompat ke fase boss |
| `JD.Checkpoint` | Muat ulang checkpoint terakhir |

## 8. Playtest (Iterasi 9)

**Log otomatis per sesi** (`Saved/Playtest/<tanggal>.csv`): waktu per bagian, jumlah mati & di mana, penggunaan tiap aksi (ringan/berat/dodge/tangkis/parry sukses), gedung hancur, sisa Sync, berapa kali boss menyusun ulang, FPS minimum.

**Form setelah main** (diisi developer, skala 1–5 + satu kalimat; ulangi di sesi berikutnya untuk melihat tren):
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

## 10. Keputusan & pertanyaan

### Sudah dijawab developer (12 Okt 2026)
| # | Pertanyaan | Keputusan |
|---|---|---|
| Q1 | Mulai kapan? | **Developer yang menentukan**; dokumen ini tanpa tanggal |
| Q2 | Referensi rasa combat | **Arkham + Sekiro ringan**: combo sederhana, parry penting, banyak musuh tapi bergantian menyerang |
| Q3 | Kamera combat | **Soft target** untuk minion (gaya Arkham), **lock-on tombol** untuk boss raksasa (framing dua raksasa seperti adegan tokusatsu) |
| Q4 | Perangkat | **Keyboard-mouse utama**; gamepad PlayStation, Xbox, dan generik juga harus bisa (bagian 4.4) |
| Q5 | Tombol | Tangkis + parry satu tombol: **R2** / **RMB**. Keyboard: ringan **LMB**, berat **E**, dodge **Left Shift**, lompat **Space**, lock-on **Q**, transformasi **T** (bagian 4.4) |
| Q6 | Finisher | **Masuk F1** (versi greybox) |
| Q7 | Penyebab gedung hancur | **Semua**: pukulan, tabrakan badan, terpental, proyektil (kerusakan sebanding gaya) |
| Q8 | Tombol transformasi | **T** (keyboard), **L1 + R1** (gamepad), berlaku seterusnya. Syarat di `Test_Loop`: setelah gelombang 3; tombol bebas di level uji |
| Q9 | Health Jayadwara habis | **Kembali jadi manusia** |
| Q10 | Dodge | **4 arah** |
| Q11 | Warga | **Penanda statis** dulu, ditingkatkan nanti |
| Q12 | Proxy boss | **Model Blender dibuat developer**. Terjawab 12 Okt 2026: dibuat developer dengan Tripo AI, dirapikan Claude ([20](20-rencana-model-jerangkong.md) jalur B) |
| Q13 | Task tracker | **GitHub Issues** satu per iterasi, dibuat Claude |
| Q14 | Playtester | **Developer sendiri**, di PC developer |
| Q15 | Setelah kalah | **Aksa muncul di tempat Jayadwara kalah**, tetap dimainkan (menghindar), berubah lagi saat energi cukup (bagian 4.5) |
| Q16 | Controller uji | **Pad USB generik gaya PlayStation**, dua analog (bagian 4.4) |
| Q17 | Meter sinkronisasi habis | **Alur sama dengan kalah** (bagian 4.5); berubah lagi dengan Sync ±50% |
| Q18 | Kamera otomatis untuk layout tanpa mouse | **Tidak perlu**: layout akhir tetap memakai mouse (LMB/RMB) |

## 11. Status & hasil

| Iter | Status | Tanggal | Catatan |
|---|---|---|---|
| 1 | ✅ (KB/M) | 12 Okt 2026 | Build + `ue_setup_combat.py` selesai. Uji otomatis PIE lulus (atribut awal, `JD.Damage`, `JD.God`, `JD.Heal`, regen stamina ±25/s setelah jeda). Uji tangan developer KB/M lulus: HUD tampil (kiri bawah), LMB/E/RMB/Shift/Q terbaca sebagai input tag. **Menyusul:** gamepad lewat x360ce (Q16), `showdebug abilitysystem` |
| 2 | ✅ | 13 Okt 2026 | `ue_setup_light_combo.py` selesai: montage + notify, `GC_Hit_Light/Heavy` (SFX Kenney k1, **pilihan sementara** slot 01–02), `DA_CombatProfile_Human`, `BP_TrainingDummy` di `Test_Combat`. Uji otomatis: pukulan 1 ke dummy -10 HP. Fix 13 Okt: tendangan (langkah 3) tertahan foot IK Control Rig `ABP_Aksa` → node dilepas (kaki kanan 29 → 113 cm pada 0,33 s); telapak tidak menyesuaikan tangga/miring sampai foot IK versi F2 (curve `DisableLegIK` sudah ada di `A_Aksa_Attack_*`). **13 Okt: uji tangan developer lulus** (combo 3 pukulan Aksa sesuai harapan). **16 Okt revisi:** combo 4 + pembuka arah + cabang finisher (bagian 6 Iterasi 2); menunggu build + skrip + uji tangan |
| 3 | 🟡 | 13 Okt 2026 | C++: `UJDGA_HeavyAttack` (dari diam/jendela combo/recovery), `UJDGA_Dodge` (root motion source, hadap tetap, montage 4 arah opsional, i-frame `State.Invulnerable`), `UJDGA_Block` (tahan; tiap tekan buka `State.ParryWindow`, anti spam `ParryLockout` 0,5 s; jalan ×0,4), `UJDCombatComponent::ResolveIncomingHit` (dodge/parry/tangkis hanya dari depan 140°/guard break) + `ApplyStagger` (sementara sampai Iterasi 4), `AJDTrainingDummy` mode menyerang (aba-aba "!" merah berkedip 0,5 s, tiap 2,5 s, jarak 2,5 m). Skrip `Tools/ue_setup_defense.py` (Aksa + dummy; `Dummy_Attacker` di `Test_Combat`) dan `ue_setup_giant_combo.py` (Jayadwara2). Animasi placeholder: berat & pose tangkis dari `A_Aksa_Attack_02` (berat diputar 0,75×, tangkis = frame 0,75 s ditahan), stagger dari `MM_HitReact_Front_Hvy_01` (Rifle), **dodge tanpa animasi**. SFX **pilihan sementara**: tangkis k1, parry k2, dodge k1. Uji otomatis PIE: berat −30 HP/−25 stamina; dodge mundur 404 cm/−20 stamina, i-frame aktif lalu lepas; tangkis −2 HP/−15 stamina, jalan 200; guard break → stagger; parry → tanpa damage, dummy stagger (raksasa: berat −30, dodge ±56 m). Sisa: uji tangan gate (parry ≥ 7/10), animasi Mixamo (berat, dodge 4 arah, tangkis) |
| 4 | ⬜ | | |
| 5 | ⬜ | | |
| 6 | 🟡 | 13 Okt 2026 | Transformasi tombol T sudah ada sejak Iterasi 6 Jayadwara. **Dimajukan (permintaan developer):** combo ringan Jayadwara2 lewat `Tools/ue_setup_giant_combo.py` — `AM_JD2_Light_01..03` (salinan `MM_Attack_0x_JD2`, notify sama dengan Aksa), `DA_CombatProfile_Giant` (laju terlihat 0,55, radius hit 711 cm, hit-stop 0,12 s, shake ×2,5, cue `Hit.Heavy`), `DA_AbilitySet_Jayadwara` (Sync 100, buffer 0,3 s), `BP_Jayadwara2` memakai `DA_InputConfig_Human`, `Dummy_Giant` (BP_TrainingDummy ×20) di `Test_GiantScale`. C++: `JDGA_LightAttack` membagi laju montage dengan `GlobalAnimRateScale` mesh (raksasa ±0,205) supaya `MontagePlayRate` = laju terlihat. Uji otomatis PIE: pukulan 1 ke `Dummy_Giant` −10 HP. Iterasi 3 ikut dipasang (berat, dodge 55 m/0,64 s, tangkis, parry 0,25 s; `AM_JD2_Heavy/Block`). Sisa Iterasi 6: uji tangan & tuning, `IMC_Giant`, rig kamera + lock-on, syarat transformasi, kalah → Aksa. **16 Okt 2026, ala Mebius (permintaan developer):** `AJDGiantCharacter` dapat `SpeedScaleExponent` (0,83: lari ±70 m/s, animasi ±0,6×, kaki tetap menapak), `GiantTurnRate` 720°/s, akselerasi × speed, `JumpBoost` 1,25; combat raksasa laju 1,0, dodge 0,35 s, hit-stop 0,15 s; `BP_Jerangkong` tetap 0,5. Skrip `Tools/ue_setup_giant_speed.py` lalu `ue_setup_giant_combo.py`. Menunggu build + uji tangan developer |
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
