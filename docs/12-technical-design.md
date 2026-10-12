# 12 — Technical Design Document (TDD)

> Arsitektur teknis untuk Unreal Engine **5.6.1**, pendekatan **C++ + Blueprint**.
> Dokumen hidup — diperbarui seiring prototype berjalan.

## Pembagian Kerja

| Dikerjakan Claude (file teks) | Dikerjakan developer (editor) |
|---|---|
| Kode C++ (logic, GAS, AI, sistem episode) | Membuat Blueprint turunan dari class C++ |
| Config `.ini`, `.uproject`, `Build.cs` | Menata level, lighting, menaruh aset |
| Script Python editor (otomasi) | Animasi, material, Niagara, Sequencer |
| `.gitignore`, `.gitattributes`, dokumen | Playtest & mengatur angka (tuning) |

**Prinsip**: logic di C++, data & visual di Blueprint/DataAsset. Blueprint tidak boleh berisi logic inti yang rumit — Claude tidak bisa membaca file `.uasset`.

---

## Lingkungan

| Item | Nilai |
|---|---|
| Engine | Unreal Engine 5.6.1 (Epic Games Launcher) |
| IDE / toolchain | Visual Studio 2022 (workload *Game development with C++*) atau Rider. **Terpasang (Okt 2026):** Build Tools 2022 17.14 + *.NET Framework 4.8 SDK* + MSVC v14.38 (versi preferred UE 5.6), tanpa IDE. Tanpa .NET Framework SDK, UBT gagal dengan "Could not find NetFxSDK install dir". |
| Lokasi project | `C:\repository\unreal_engine\jayadwara` |
| Nama project / module | `Jayadwara` |
| Prefix class C++ | `JD` (contoh: `AJDHumanCharacter`) |
| Version control | Git + **Git LFS** (repo sendiri di folder `jayadwara`) |
| Otomasi editor | **Python Remote Execution** aktif (`DefaultEngine.ini`). Claude menjalankan skrip di editor yang sedang terbuka dengan `python Tools/ue_remote.py <file.py>` (atau `-c "<kode>"`) dan membaca output-nya. Membuat/mengisi `.uasset` lewat skrip Python di `Tools/`, bukan edit manual |

## Plugin

| Plugin | Fungsi |
|---|---|
| **Gameplay Abilities** | GAS: ability, attribute, effect |
| **Enhanced Input** | Input dua mode (default di UE5) |
| **StateTree** + Gameplay StateTree | AI musuh & boss |
| **Chaos Destruction** / Geometry Collection | Gedung hancur |
| **Niagara** | VFX |
| **Motion Warping** | Serangan melee yang "menempel" ke target |
| **Common UI** *(opsional)* | Menu & HUD yang mendukung gamepad |
| **Pose Search / Motion Matching** *(nanti)* | Locomotion lebih halus setelah prototype |

### Dependensi module (`Jayadwara.Build.cs`)
`Core`, `CoreUObject`, `Engine`, `InputCore`, `EnhancedInput`, `GameplayAbilities`, `GameplayTags`, `GameplayTasks`, `AIModule`, `StateTreeModule`, `GameplayStateTreeModule`, `UMG`, `Niagara`, `GeometryCollectionEngine`, `MotionWarping`

---

## Arsitektur Inti

### Karakter & Transformasi

```
AJDCharacterBase (ACharacter, IAbilitySystemInterface)
├── UAbilitySystemComponent
├── UJDAttributeSet
├── UJDCombatComponent        (hit detection, combo state)
│
├── AJDHumanCharacter         (Aksa)
│   └── UJDScannerComponent   (Netra)
└── AJDGiantCharacter         (Jayadwara)
    └── UJDSyncComponent      (meter sinkronisasi)

AJDEnemyBase  (AJDCharacterBase)
└── AJDBossBase  (fase, titik lemah)
```

- **Transformasi = ganti pawn**. `AJDPlayerController` melakukan `UnPossess` pawn manusia → spawn/aktifkan pawn raksasa → `Possess`. Pawn manusia disembunyikan, bukan dihapus.
- Alasan memilih ganti pawn (bukan memperbesar satu karakter): kamera, collision, movement, dan animasi untuk dua skala sangat berbeda; lebih mudah dikontrol dan di-debug.
- Transisi visual memakai **Level Sequence** (Sequencer).

#### Mesh logika vs mesh visual (Aksa)

Model Aksa dibuat sendiri; sampai jadi, **MetaHuman** dipakai sebagai placeholder visual (keputusan 12 Okt 2026). Supaya penggantiannya tidak menyentuh logika:

| Lapisan | Isi | Diganti saat model sendiri jadi? |
|---|---|---|
| **Mesh logika** = `GetMesh()` di `BP_Aksa` | Manny (`SKM_Manny_Simple`), **disembunyikan** tapi animasi tetap jalan (`VisibilityBasedAnimTickOption = AlwaysTickPoseAndRefreshBones`). Menjalankan `ABP_Aksa`, montage silat, Anim Notify hit, socket | Tidak |
| **Mesh visual** | Komponen MetaHuman (body, face, groom) yang menyalin pose dari mesh logika lewat **Retarget Pose From Mesh** | **Ya**: ganti komponen ini dengan `SK_Aksa` |

Aturan:
- Kode C++, montage, Anim Notify, dan trace hit **hanya** memakai mesh logika dan nama tulang Mannequin (`hand_r`, `foot_l`, ...). Tidak ada referensi ke aset MetaHuman di C++.
- Semua animasi dibuat/diimpor untuk **skeleton Mannequin**, tidak pernah untuk skeleton MetaHuman.
- Jangan bergantung pada fitur khusus MetaHuman (rig wajah, Live Link, lip-sync). Dialog vertical slice = teks + potret.
- `SK_Aksa` nanti dibuat dengan nama tulang Mannequin (seperti Jayadwara), sehingga bisa memakai retarget yang sama atau langsung menjadi mesh logika.
- Kapsul dan kamera disetel untuk tinggi Aksa, bukan tinggi MetaHuman/Manny; retarget menutupi selisih proporsi.

### Combat (satu sistem, dua skala)

- Semua serangan adalah **Gameplay Ability** (`UJDGA_LightAttack`, `UJDGA_HeavyAttack`, `UJDGA_Dodge`, `UJDGA_Block`, dst.) yang dipakai **manusia dan raksasa**.
- Perbedaan skala diatur lewat **DataAsset** `UJDCombatProfile`: kecepatan animasi, radius hit, damage, camera shake, hit-stop.
- **Hit detection**: Anim Notify State → sphere/capsule trace dari socket senjata/tangan.
- **Combo**: montage section + gameplay tag window (`State.Combat.ComboWindow`).
- **Motion Warping** untuk mendekatkan pukulan ke target.

### Attribute (`UJDAttributeSet`)

| Attribute | Dipakai oleh |
|---|---|
| `Health`, `MaxHealth` | Semua karakter |
| `Stamina`, `MaxStamina` | Dodge, block, serangan berat |
| `Sync`, `MaxSync` | Hanya Jayadwara |

### Meter Sinkronisasi

- `UJDSyncComponent` mendengarkan event:
  - `AJDDestructibleBuilding::OnBuildingDestroyed` → apply `GE_SyncPenalty_Building`
  - NPC warga terkena damage → `GE_SyncPenalty_Civilian`
  - NPC diselamatkan → `GE_SyncReward_Rescue`
- `Sync` mencapai 0 → event `OnSyncDepleted` → transformasi berakhir paksa / gagal misi.
- Besaran penalti/hadiah disimpan di DataAsset agar mudah di-tuning.

### Investigasi & Kelemahan Boss

- `UJDClueComponent` dipasang pada actor petunjuk (punya `GameplayTag` unik, mis. `Clue.Ep01.Prasasti`).
- `UJDScannerComponent` melakukan scan → menemukan clue → melapor ke `UJDInvestigationSubsystem` (World Subsystem).
- Boss mendefinisikan kelemahan sebagai daftar tag clue yang dibutuhkan. Jika terpenuhi → titik lemah ditandai di HUD dan/atau damage multiplier aktif.

### AI

- **StateTree** untuk minion dan boss.
- Boss: state per fase (`Phase1`, `Phase2`), transisi berdasarkan Health atau event (mis. tengkorak terekspos).
- Musuh kecil mode manusia: perilaku sederhana (dekati, serang, mundur).

### Destruction

- `AJDDestructibleBuilding` membungkus Geometry Collection yang sudah **pre-fractured**.
- Setelah runtuh: puing diganti mesh statis / dihapus bertahap untuk menjaga FPS.
- Batas jumlah gedung yang bisa hancur bersamaan ditetapkan saat uji performa.

### Alur Episode

- `AJDEpisodeDirector` (actor per level) atau `UJDEpisodeSubsystem` mengelola fase:
  `Intro → Briefing → Investigation → HumanCombat → Transformation → BossFight → Debrief`
- Tiap episode punya DataAsset `UJDEpisodeData`: ID, judul, boss, daftar clue, dialog, sequence.

### Input

- `IMC_Human` dan `IMC_Giant` (Enhanced Input Mapping Context), diganti saat transformasi.
- Mendukung keyboard-mouse dan gamepad sejak awal. **Keyboard-mouse perangkat utama**; gamepad PlayStation, Xbox, dan generik harus bisa (pemetaan tombol & catatan teknis di [23](23-rencana-fase-1.md#44-kontrol-q4-q5-q8)). Transformasi: **T** / **L1 + R1**.

### UI

- UMG. HUD terpisah untuk mode manusia dan raksasa.
- Dialog sederhana berbasis **DataTable** (`DT_Dialogue_Ep01`).

### Save

- Vertical slice: checkpoint saja.
- Nanti: `UJDSaveGame` (progres episode, upgrade, hubungan karakter).

---

## Struktur Folder

### Source (C++)
```
Source/Jayadwara/
├── Jayadwara.Build.cs
├── Core/            (GameMode, PlayerController, GameInstance)
├── Characters/      (CharacterBase, Human, Giant, Enemy, Boss)
├── Abilities/       (AttributeSet, GameplayAbility, GameplayEffect C++)
├── Combat/          (CombatComponent, CombatProfile, AnimNotify)
├── Sync/            (SyncComponent)
├── Investigation/   (ClueComponent, ScannerComponent, InvestigationSubsystem)
├── AI/              (StateTree tasks & conditions)
├── World/           (DestructibleBuilding, Civilian)
├── Episode/         (EpisodeDirector, EpisodeData)
└── UI/              (base class widget C++)

Source/JayadwaraEditor/   (modul Editor-only, tidak ikut build game)
└── JDEditorToolsLibrary  (dipanggil skrip Python di Tools/: Physics Asset, node Anim Graph, retarget ke folder)
```

### Content
```
Content/Jayadwara/
├── Core/            (GameMode, PlayerController BP)
├── Characters/      (Aksa/, Jayadwara/, Enemies/, Bosses/)
├── Abilities/       (GA_, GE_)
├── Data/            (DA_, DT_)
├── Input/           (IA_, IMC_)
├── Maps/            (Ep01_LawangSapta, Test_*)
├── Environment/     (Candi/, Kota/)
├── VFX/
├── Audio/
├── UI/
└── Cinematics/      (LS_)
```
Konten pihak ketiga tetap di folder aslinya supaya referensinya tidak putus: `Characters/Mannequins/`, `Input/`, `LevelPrototyping/` (disalin dari `Templates/TemplateResources/High` UE 5.6, tanpa `.fbx` sumber). Placeholder Fase 0–1, diganti aset Aksa sendiri di Fase 2.

File sumber audio (WAV kandidat, lisensi, pilihan) ada di `Audio/` di root repo, di luar `Content/` seperti `Art/`; import ke `Audio/` di atas lewat `Tools/ue_import_audio.py` (lihat [Audio/README.md](../Audio/README.md)).

## Konvensi Penamaan Aset

| Prefix | Jenis | Prefix | Jenis |
|---|---|---|---|
| `BP_` | Blueprint | `ABP_` | Animation Blueprint |
| `SM_` | Static Mesh | `AM_` | Anim Montage |
| `SK_` | Skeletal Mesh | `NS_` | Niagara System |
| `M_` / `MI_` | Material / Instance | `WBP_` | Widget Blueprint |
| `T_` | Texture | `DA_` / `DT_` | Data Asset / Data Table |
| `GA_` / `GE_` | Gameplay Ability / Effect | `IA_` / `IMC_` | Input Action / Mapping Context |
| `LS_` | Level Sequence | `S_` / `SC_` | Sound Wave / Sound Cue |
| `SKEL_` | Skeleton | `PA_` | Physics Asset |
| `IK_` | IK Rig | `RTG_` | IK Retargeter |

> `SKEL_`, `PA_`, `IK_`, `RTG_` ditambahkan di Iterasi 5 model Jayadwara (usulan [13](13-rencana-model-jayadwara.md)); contoh `SKEL_Jayadwara`, `PA_Jayadwara`, `IK_Jayadwara`, `RTG_Mannequin_To_Jayadwara`. LOD tetap di dalam satu aset `SK_` (bukan aset terpisah).

## Version Control

- Repo Git sendiri di `C:\repository\unreal_engine\jayadwara` (Git LFS 3.7.1 sudah terpasang).
- **`.gitattributes`** — LFS untuk: `*.uasset`, `*.umap`, `*.fbx`, `*.obj`, `*.png`, `*.tga`, `*.psd`, `*.wav`, `*.mp3`, `*.ogg`, `*.mp4`, `*.blend`.
- **`.gitignore`** — abaikan: `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `.vs/`, `*.sln`, `*.suo`, `*.VC.db`.
- Commit minimal setiap sesi kerja; pesan commit jelas (mis. `feat(combat): tambah combo pukulan ringan`).
- **Branch:**
  - `main`: versi stabil. Diisi merge dari `development` di akhir fase/milestone.
  - `development`: integrasi harian. Kerja editor (`.uasset`/`.umap`) dilakukan di sini.
  - `claude/*`: kode dari Claude. Developer `git checkout` branch ini + `git pull`, mengetes build di editor, lalu membuat PR ke `development` dan merge. (Auto-merge lewat GitHub Actions sempat dicoba dan dihapus: runner GitHub tidak punya UE, jadi C++ tidak bisa diverifikasi sebelum merge.)
- Tutup editor sebelum `git checkout` / `git pull` (aset biner yang sedang terbuka tidak ter-reload).
- Pertimbangkan backup remote privat (GitHub/GitLab dengan kuota LFS yang cukup).

## Target Performa

| Item | Target |
|---|---|
| FPS | 60 FPS di 1080p, PC kelas menengah |
| Lumen | Diuji saat prototype; siap dimatikan / diturunkan untuk gaya stylized |
| Nanite | Untuk gedung & lingkungan statis |
| Destruction | Pre-fractured, jumlah dibatasi, puing dibersihkan |

*Spesifikasi PC minimum ditetapkan setelah uji performa di akhir Fase 1.*

## Langkah Setup Project (Fase 0)

1. Install UE 5.6.1 dan Visual Studio 2022.
2. Claude membuat kerangka project C++: `Jayadwara.uproject`, `Source/Jayadwara/*`, `Target.cs`, config dasar, `.gitignore`, `.gitattributes`.
3. Klik kanan `Jayadwara.uproject` → **Generate Visual Studio project files**.
4. Buka `.sln` → build **Development Editor** → jalankan editor.
5. Commit pertama.
