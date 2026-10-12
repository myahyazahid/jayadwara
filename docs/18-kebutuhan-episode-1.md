# 18 — Kebutuhan Produksi Episode 1 "Gerbang yang Retak"

> **Status: USULAN v0.1 (12 Okt 2026).** Daftar semua yang harus ada supaya Ep 1 bisa dimainkan dari menu sampai debrief.
> Batas scope tetap [11-vertical-slice-spec.md](11-vertical-slice-spec.md); isi cerita dari [17-skenario-arc-1.md](17-skenario-arc-1.md#episode-1--gerbang-yang-retak); arsitektur dari [12-technical-design.md](12-technical-design.md). Dokumen ini hanya **memecah** scope itu menjadi daftar kerja, tidak menambah fitur.

**Legenda kolom "Oleh":** `C` = Claude (C++, skrip Python editor/Blender, data teks) · `D` = developer (editor, tuning, visual) · `B` = beli/commission/Fab/Mixamo · `C+D` = Claude membuat, developer menyetel/mereview.
**Kolom "Fase":** `F0` = sekarang (Setup) · `F1` = Prototype greybox (Des 2026–Mar 2027) · `F2` = Vertical slice (Apr–Des 2027), mengikuti [10](10-roadmap.md).

---

## 1. Gambaran Besar

| Kelompok | Jumlah item | Mayoritas oleh | Fase utama |
|---|---|---|---|
| A. Sistem C++ | ±30 class/komponen | C | F1 (sistem) → F2 (fitur Ep 1) |
| B. Karakter & animasi | 6 karakter + ±60 animasi | B / C (model) / D | F1 (proxy) → F2 (final) |
| C. Lingkungan & level | 1 map, ±6 zona, 6–10 gedung hancur | B + D | F2 |
| D. VFX | ±13 efek Niagara | D (C bantu parameter) | F2 |
| E. Audio | 4 musik + ±25 SFX | B | F2 |
| F. UI & narasi | 2 HUD, 3 menu, dialog, wayang 2D | C (logika) + D/B (visual) | F1 (fungsi) → F2 (visual) |
| G. Data & konfigurasi | ±15 aset data | C | F1–F2 |
| H. Uji & rilis internal | playtest, performa, footage | D | akhir F2 |

**Anggaran waktu** (kapasitas ±50 jam/bulan): F1 ±4 bulan ≈ **200 jam**, F2 ±9 bulan ≈ **450 jam**. Pembagian per kelompok ada di bagian 4.

---

## 2. Yang Sudah Ada (12 Okt 2026)

| Item | Status |
|---|---|
| Project C++ UE 5.6.1, Git LFS, plugin inti (GAS, Enhanced Input, StateTree, Niagara, Motion Warping) | ✅ Selesai |
| `AJDGameMode`, `AJDPlayerController`, `AJDCharacterBase` (Move/Look/Jump), `AJDHumanCharacter` | ✅ Build sukses |
| `BP_Aksa`, `BP_JDGameMode`, `BP_JDPlayerController`, map `Test_Greybox` | ✅ Lewat `Tools/ue_setup_greybox.py` |
| Model Jayadwara (FBX, 4 LOD, tekstur, 89 tulang) | ✅ Iterasi 0–5 |
| Import Jayadwara ke UE (`SK_`/`SKEL_`/`PA_`, 4 MI, 17 tekstur), `AJDGiantCharacter` (skala, kapsul, kamera), `BP_JDGameMode_Giant`, `Test_GiantScale` | ✅ Iterasi 6 selesai 12 Okt 2026 (mesh 45 m ter-bake, retarget FK, Anim Dynamics); socket hit → Fase 1 |
| Plugin Chaos + `GeometryCollectionEngine` di `Build.cs` | ⏳ Fase 0 tersisa |
| Semua item di bagian 3 di bawah | ❌ Belum |

---

## 3. Daftar Kebutuhan

### A. Sistem C++

#### A1. Inti & alur episode
| Item | Isi | Oleh | Fase |
|---|---|---|---|
| `AJDPlayerController`: transformasi | Ganti pawn manusia ↔ raksasa, sembunyikan pawn manusia, ganti `IMC_Human`/`IMC_Giant`, mulai Level Sequence | C | F1 |
| `UJDEpisodeSubsystem` / `AJDEpisodeDirector` | Fase `Intro → Briefing → Investigation → HumanCombat → Transformation → BossFight → Debrief` dari `UJDEpisodeData` | C | F2 |
| `UJDEpisodeData` | ID, judul, boss, daftar clue, dialog, sequence | C | F2 |
| Checkpoint | Simpan/muat posisi + fase + atribut di titik tertentu (bukan save lengkap) | C | F1 |
| Objektif & penanda tujuan | "Pergi ke gerbang candi", "Scan 3 petunjuk", panah HUD | C | F2 |
| Trigger cutscene | Volume/event yang memutar `LS_` dan mengunci input | C | F2 |

#### A2. GAS & combat (satu sistem, dua skala)
| Item | Isi | Oleh | Fase |
|---|---|---|---|
| `UAbilitySystemComponent` di `AJDCharacterBase` | + `IAbilitySystemInterface` | C | F1 |
| `UJDAttributeSet` | Health, MaxHealth, Stamina, MaxStamina, Sync, MaxSync | C | F1 |
| `UJDCombatComponent` | Target, combo state, hit-stop, lapor hit | C | F1 |
| `UJDCombatProfile` (DataAsset) | Kecepatan animasi, radius hit, damage, camera shake, hit-stop per skala | C+D | F1 |
| `UJDGA_LightAttack` | Combo 3 (montage section + `State.Combat.ComboWindow`) | C | F1 |
| `UJDGA_HeavyAttack` | Pukulan berat, biaya stamina | C | F1 |
| `UJDGA_Dodge` | Dodge + i-frame | C | F1 |
| `UJDGA_Block` + parry | Tangkis, parry di jendela waktu, juga menangkis **puing** di boss fase 2 | C | F1 |
| `UJDGA_Finisher` | Finisher pada musuh stagger; **memecah tengkorak** kerangka | C | F2 |
| `UJDGA_JurusSpesial01` | Jurus spesial Jayadwara #1 | C+D | F2 |
| `UJDAnimNotifyState_HitWindow` | Sphere/capsule trace dari socket tangan/kaki | C | F1 |
| Hit reaction & stagger | Tag `State.Stagger`, montage reaksi, poise sederhana | C | F1 |
| Target lock (soft) | Arahkan serangan ke musuh terdekat; boss: kunci ke titik lemah | C | F1 |
| Motion Warping | Tarik pukulan ke target | C+D | F1 |
| Camera shake & hit-stop | Data dari `UJDCombatProfile` | C+D | F1 |

#### A3. Mode manusia & investigasi
| Item | Isi | Oleh | Fase |
|---|---|---|---|
| `UJDScannerComponent` | Mode scan (toggle), jangkauan, deteksi clue, efek post-process | C | F2 |
| `UJDClueComponent` | Tag clue (`Clue.Ep01.*`), status ditemukan, teks KOMS saat ditemukan | C | F2 |
| `UJDInvestigationSubsystem` | Kumpulkan clue, beri tahu boss kalau kelemahan terpenuhi | C | F2 |
| Interaksi opsional | Batu latihan (adegan 3): prompt + dialog | C | F2 |

#### A4. Mode raksasa
| Item | Isi | Oleh | Fase |
|---|---|---|---|
| `AJDGiantCharacter` | Skala, kapsul, gerak, kamera | C | ✅ F0 (Iterasi 6) |
| Rig kamera raksasa | Jarak, FOV, lag, *framing* boss + kota | C+D | F1 |
| `UJDSyncComponent` | Dengar event gedung/warga → GE penalti; `OnSyncDepleted` → transformasi berakhir | C | F1 |
| `GE_SyncPenalty_Building`, `GE_SyncPenalty_Civilian` | Besaran dari DataAsset | C+D | F1 |

#### A5. Musuh & boss
| Item | Isi | Oleh | Fase |
|---|---|---|---|
| `AJDEnemyBase` | Turunan `AJDCharacterBase`, health, mati, drop | C | F1 |
| Minion kerangka | **Bangkit lagi** kalau tidak di-finisher (adegan 5 gelombang 3) | C | F1 |
| StateTree minion | Dekati, serang, mundur; spawner per gelombang | C+D | F1 |
| `AJDBossBase` | Fase, titik lemah, kelemahan dari tag clue + damage multiplier | C | F1 |
| `AJDBoss_Jerangkong` | Fase 1: anggota tubuh rontok lalu merayap & menyusun ulang (2×); fase 2: tengkorak terekspos, lempar puing ke desa | C | F1 (greybox) → F2 |
| StateTree boss | `Phase1`, `Phase2`, transisi berdasarkan susun ulang ke-2 | C+D | F1 |
| Proyektil puing | Bisa ditangkis; kalau kena desa → penalti meter | C | F2 |

#### A6. Dunia
| Item | Isi | Oleh | Fase |
|---|---|---|---|
| `AJDDestructibleBuilding` | Bungkus Geometry Collection pre-fractured, `OnBuildingDestroyed`, bersihkan puing | C | F1 |
| `AJDCivilian` | Lari menjauhi bahaya, bisa terkena (penalti meter), tanpa Mass AI | C | F2 |

#### A7. UI (base class C++)
| Item | Isi | Oleh | Fase |
|---|---|---|---|
| Base HUD manusia & raksasa | Binding ke atribut GAS | C | F1 |
| Sistem dialog | Baca `DT_Dialogue_Ep01`, potret, teks, lanjut/skip; mode KOMS (tanpa menghentikan gameplay) | C | F2 |
| Menu utama, pause, pengaturan grafis | Base class + logika (resolusi, kualitas, V-Sync) | C | F2 |
| Prompt tutorial | Tampilkan tombol sesuai perangkat (KB/M atau gamepad) | C | F2 |

### B. Karakter & Animasi

#### B1. Model
| Karakter | Kebutuhan | Sumber | Oleh | Fase |
|---|---|---|---|---|
| **Aksa** | Mesh manusia stylized, skeleton kompatibel Mannequin | **Dibuat sendiri** (Blender, Claude + developer; rencana [19](19-rencana-model-aksa.md)). Sementara: **MetaHuman** sebagai mesh visual di atas Manny tersembunyi ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)) | C + D | F1 placeholder → F2 final |
| **Jayadwara** | Sudah ada | Blender (Claude) | C | ✅ |
| **Jerangkong** (boss ±31 m) + **kerangka kecil** (minion) | **Satu model dan rig untuk keduanya**; tulang sebagai potongan kaku; skeleton sendiri bernama Mannequin + retarget (proporsi bungkuk/lengan panjang). Konsep: [`jerangkong_v01.webp`](concept-art/jerangkong_v01.webp); rencana: [20](20-rencana-model-jerangkong.md) | Blender (Claude) | C | F1 proxy → F2 hero |
| Warga desa (2–3 variasi) + mandor | Skeleton Mannequin | Fab / kit stylized | B + D | F2 |
| Arca Dwarapala ×2 | Arca batu (kiri: utuh → retak → hancur; kanan: dililit tali + versi berterpal) | Blender (Claude) atau Fab | C / B | F2 |
| Truk Adikara | Prop untuk adegan 6 | Fab | B | F2 |

#### B2. Animasi
| Set | Isi minimum | Sumber | Fase |
|---|---|---|---|
| Aksa: gerak | Idle, jalan, lari, lompat, dodge (4 arah) | Mannequin / Mixamo | F1 |
| Aksa: silat | Combo ringan ×3, berat, tangkis, parry, hit react ×2, stagger, finisher, pose scan | Mixamo (F1) → video-mocap / commission (F2) | F1 → F2 |
| Jayadwara | **Set silat yang sama** (retarget) + idle kuda-kuda, jurus spesial #1, pose transformasi, penyegelan | Retarget + tuning kecepatan | F1 → F2 |
| Jerangkong | Idle, jalan, sapuan, hantaman, lempar tulang/puing, kena pukul, rontok, susun ulang, raungan fase 2, runtuh | Retarget Mannequin + keyframe kustom (rontok/susun ulang bisa prosedural lewat kode) | F1 → F2 |
| Kerangka kecil | Jalan, serang, kena, rubuh, bangkit lagi | Sama dengan Jerangkong (skala manusia) | F1 |
| Warga | Lari, panik, berlindung | Mixamo | F2 |
| Animation Blueprint | `ABP_Aksa`, `ABP_Jayadwara`, `ABP_Jerangkong` (locomotion + slot montage) | C+D | F1 |
| Gerak sekunder | Anim Dynamics selendang/kain Jayadwara | D | ✅ F0 (Iterasi 6) |

### C. Lingkungan & Level

**Map:** `Ep01_LawangSapta`

| Zona | Isi | Adegan |
|---|---|---|
| Jalan akses | Mobil DWARA, garis polisi, truk & alat berat Adikara, batu latihan | 2, 3, 6 |
| Galian berundak | Lubang galian, tulang (clue 2), titik spawn kerangka | 3–5 |
| Gerbang candi | 2 arca Dwarapala, prasasti retak (clue 3), alas arca | 4, 6, 9 |
| Halaman candi | Arena boss bagian atas | 7 |
| Desa kecil di bawah bukit | **6–10 gedung bisa hancur** (rumah, warung, menara air, gardu ronda), musala (**tidak** bisa hancur), warga | 7 |
| Latar jauh | Bukit, hutan, kota kecil di kejauhan (pembanding skala) | semua |

| Item | Isi | Oleh | Fase |
|---|---|---|---|
| Kit candi stylized | Batu candi modular, tangga, gerbang, relief | Fab + kustom | F2 |
| Kit desa/kota stylized | Rumah, warung, tiang listrik, kendaraan kecil (pembanding skala) | Fab | F2 |
| Gedung hancur | 3–4 mesh dasar → 6–10 varian, di-fracture jadi Geometry Collection | D (C skrip bantu) | F1 uji → F2 |
| Pencahayaan waktu | Sore (adegan 3–5) → senja merah (6) → awal malam (7–9); transisi saat cutscene | D | F2 |
| Fog & skala | Fog jarak, kabut lembah, partikel debu | D | F2 |
| Greybox level | Tata letak kotak-kotak dulu, uji alur & ukuran arena | C (skrip) + D | F1 akhir |

### D. VFX (Niagara)
| Efek | Adegan | Fase |
|---|---|---|
| Pulse mode scan + highlight clue | 4 | F2 |
| Aliran energi Kala (clue 1) | 4 | F2 |
| Percikan pukulan (skala manusia & raksasa) | 5, 7 | F1 (placeholder) → F2 |
| Debu langkah raksasa | 7 | F2 |
| Tulang merayap & menyusun ulang | 5, 7 | F2 |
| Cahaya Kala di rusuk & rongga mata Jerangkong | 6, 7 | F2 |
| Transformasi: pecahan batu berputar + retakan emas dari telapak | 6 | F2 |
| Highlight titik lemah tengkorak | 7 | F2 |
| Debu runtuhan gedung | 7 | F1 → F2 |
| Penyegelan: energi tersedot ke telapak | 8 | F2 |
| Kedipan merah di mata Jayadwara (**bukan** permata dada) | 8 | F2 |
| Jayadwara memudar jadi cahaya + pecahan batu | 8 | F2 |
| Ambient: debu senja, kunang-kunang malam | semua | F2 |

### E. Audio
| Item | Isi | Sumber | Fase |
|---|---|---|---|
| Musik | Tema eksplorasi, tema combat manusia, tema boss (gamelan + orkestra/rock), iringan gamelan wayang | Commission / lisensi | F2 |
| SFX combat | Pukulan ringan/berat, tangkis, parry, dodge, tulang patah, tulang merayap | Pustaka SFX | F1 → F2 |
| SFX raksasa | Langkah raksasa, gedung runtuh, gema kota, raungan Jerangkong | Pustaka + layering | F2 |
| SFX UI & scanner | Scan, clue ditemukan, KOMS masuk, menu | Pustaka | F2 |
| Suara Sang Penjaga | Placeholder: teks + efek suara rendah (voice acting di luar scope) | D | F2 |
| Ambien | Angin bukit, serangga senja, desa | Pustaka | F2 |

Kandidat SFX placeholder (Kenney + Freesound, semua CC0) dan aturan lisensi: [Audio/KANDIDAT.md](../Audio/KANDIDAT.md), [Audio/README.md](../Audio/README.md). Sonniss GDC Bundle didownload manual.

### F. UI & Narasi
| Item | Isi | Oleh | Fase |
|---|---|---|---|
| HUD manusia | Health, stamina, penanda clue, objektif | C (logika) + D (visual) | F1 → F2 |
| HUD raksasa | Health, stamina, **meter sinkronisasi**, penanda tengkorak | C + D | F1 → F2 |
| Kotak dialog + KOMS | Potret 9 karakter (Aksa, Bagas, Sekar, Nadia, Yahyo, Ki Sastro, mandor, ikon Sang Penjaga, Gunadi [opsional]) | C + B (potret) | F2 |
| Pembuka wayang 2D | Kelir, wayang Dwarapala ×2, makhluk Kala, gunungan, parallax, teks narasi | B / D (ilustrasi) + C (pemutar) | F2 |
| Kartu judul **JAYADWARA** + kartu "Episode berikutnya" | | D | F2 |
| Menu utama, pause, pengaturan grafis | | C + D | F2 |
| Subtitle ID + EN | Semua dialog | C (teks) | F2 |

### G. Data & Konfigurasi (semua oleh Claude, angka dituning developer)
| Aset | Isi |
|---|---|
| `DA_Ep01_LawangSapta` | `UJDEpisodeData` |
| `DT_Dialogue_Ep01` | Semua baris dari [17](17-skenario-arc-1.md#episode-1--gerbang-yang-retak), ID + EN |
| `DA_CombatProfile_Human`, `DA_CombatProfile_Giant` | Parameter skala |
| `DA_SyncConfig` | Besaran penalti gedung/warga |
| `DA_Boss_Jerangkong` | HP per fase, jumlah susun ulang, tag kelemahan |
| Gameplay Tags | `Clue.Ep01.*`, `State.Combat.*`, `State.Stagger`, `Boss.Ep01`, `Ability.*` |
| Input | `IA_Move/Look/Jump/Dodge/Light/Heavy/Block/Scan/Interact/Special`, `IMC_Human`, `IMC_Giant` (KB/M + gamepad) |
| Level Sequence | `LS_Ep01_Kebangkitan`, `LS_Ep01_Transformasi`, `LS_Ep01_Penyegelan`, `LS_Ep01_Stinger` (opsional) |

### H. Uji & Rilis Internal
| Item | Target ([11](11-vertical-slice-spec.md#kriteria-selesai)) |
|---|---|
| Playtest | ≥5 orang menyelesaikan episode tanpa bantuan |
| Performa | 1080p 60 FPS di PC menengah; loading < 20 dtk |
| Stabilitas | Tanpa crash dalam satu playthrough |
| Footage | Cukup untuk trailer 60–90 detik |
| Cek IP & budaya | Checklist di [17](17-skenario-arc-1.md#cek-ip--budaya-ep-1) |

---

## 4. Urutan Pengerjaan

### F0 — sekarang (sampai Nov 2026)
1. ~~Selesaikan **Iterasi 6** Jayadwara (retarget, Anim Dynamics, uji skala).~~ ✅ 12 Okt 2026
2. Aktifkan Chaos + `GeometryCollectionEngine`.

### F1 — Prototype greybox (Des 2026 – Mar 2027, ±200 jam)
Mengikuti target bulanan [10](10-roadmap.md#fase-1--prototype-greybox-des-2026--mar-2027). Semua visual masih kotak, Manny, dan Mixamo.

| Bulan | Kerja untuk Ep 1 | Kelompok |
|---|---|---|
| Des 2026 | GAS dasar, combo ringan/berat, dodge, tangkis+parry, hit react, target lock | A2, B2 |
| Jan 2027 | `AJDEnemyBase`, minion kerangka (pakai Manny dulu) + StateTree, Health/Stamina | A5, A2 |
| Feb 2027 | Transformasi (ganti pawn + IMC), kamera raksasa, combat raksasa memakai profil, checkpoint | A1, A4 |
| Mar 2027 | Meter + `AJDDestructibleBuilding` (Chaos), **proxy Jerangkong** (Blender) + boss 2 fase greybox, playtest loop | A4, A5, A6, B1 |

**Gate F1:** satu loop utuh terasa seru (sesuai [10](10-roadmap.md#fase-1--prototype-greybox-des-2026--mar-2027)). Kalau tidak, perbaiki combat dulu sebelum masuk F2.

### F2 — Vertical slice (Apr – Des 2027, ±450 jam)
| Periode | Kerja untuk Ep 1 | Kelompok |
|---|---|---|
| Apr – Mei 2027 | Pengadaan aset: Aksa, kit candi & desa, warga, truk; **Jerangkong hero** + arca (Blender) | B1, C |
| Jun – Jul 2027 | Level `Ep01_LawangSapta` (greybox → art), scanner Netra + 3 clue, investigasi | C, A3 |
| Agu – Sep 2027 | Boss Jerangkong final (rontok/susun ulang, tengkorak, puing), animasi silat final, VFX transformasi & penyegelan | A5, B2, D |
| Okt – Nov 2027 | Pembuka wayang, dialog/briefing/debrief, alur episode, HUD & menu, audio | A1, A7, F, E |
| Des 2027 | Polish, optimasi, playtest ≥5 orang, perbaikan bug, footage trailer | H |

### Perkiraan pembagian jam (kasar)
| Kelompok | F1 | F2 | Catatan |
|---|---|---|---|
| A. Sistem C++ | ±110 | ±90 | Jam Claude tidak dihitung; angka ini jam developer untuk build, uji, dan tuning |
| B. Karakter & animasi | ±30 | ±110 | Silat final adalah item terbesar |
| C. Lingkungan & level | ±25 | ±100 | |
| D. VFX | ±5 | ±50 | |
| E. Audio | – | ±25 | Sebagian besar beli/commission |
| F. UI & narasi | ±15 | ±45 | |
| H. Uji & polish | ±15 | ±30 | |
| **Total** | **±200** | **±450** | Sesuai kapasitas roadmap |

---

## 5. Risiko Terbesar

| Risiko | Dampak | Mitigasi |
|---|---|---|
| **Animasi silat** (manusia & raksasa) | Combat terasa murahan; satu set dipakai dua skala, jadi kualitasnya berlipat pengaruhnya | Mixamo untuk F1; anggarkan video-mocap/commission di F2 sejak awal |
| **Model Aksa** | Bottleneck aset terbesar setelah Jayadwara; wajah, kulit, rambut, dan pakaian lebih sulit dibuat lewat skrip daripada zirah Jayadwara | MetaHuman sebagai placeholder supaya gameplay tidak menunggu; model sendiri dibuat paralel dan diganti tanpa menyentuh logika |
| **Chaos destruction** | Berat; bisa menjatuhkan FPS | Uji di F1 (Mar 2027); batasi jumlah gedung yang runtuh bersamaan; puing dibersihkan |
| **Mekanik rontok & susun ulang Jerangkong** | Fitur boss paling teknis di Ep 1 | Prototype di F1 dengan proxy; fallback: tulang lepas sebagai fisika sederhana, susun ulang lewat animasi |
| **Rasa skala** | Pilar genre; kalau gagal, raksasa terasa kecil | Kamera + pembanding (rumah, tiang listrik, warga) + fog sejak greybox |

---

## 6. Keputusan yang Perlu Diambil

| # | Pertanyaan | Kapan | Usulan Claude |
|---|---|---|---|
| ~~K1~~ | ~~Sumber model Aksa~~ | **Diputuskan 12 Okt 2026** | Dibuat sendiri; MetaHuman sebagai placeholder sampai model jadi ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)) |
| **K2** | Arca Dwarapala: Blender (Claude) atau Fab? | Apr 2027 | Blender: bentuk khas, butuh 3 tahap kerusakan, dan bisa memakai ulang palet/motif Jayadwara |
| **K3** | Ilustrasi wayang 2D: commission, buat sendiri, atau digital oleh Claude (SVG/skrip)? | Okt 2027 | Commission ilustrator wayang: identitas visual paling khas di trailer |
| **K4** | Musik: commission komposer atau lisensi? | Mei 2027 | Commission minimal tema boss (paling sering muncul di trailer); sisanya lisensi |
| **K5** | Debrief Ep 1: bestiary & unlock jurus ([16](16-panduan-arc-1.md#24-debrief)) di luar scope [11](11-vertical-slice-spec.md#di-luar-scope-jangan-dikerjakan-di-fase-ini) | — | Di vertical slice cukup **baris teks** di debrief; UI bestiary & sistem unlock di Fase 4 |
