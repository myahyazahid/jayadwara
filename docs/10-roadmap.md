# 10 — Roadmap

> Asumsi: **solo**, **±10–15 jam/minggu** (≈ 50 jam/bulan), mulai **Oktober 2026**.
> Semua perkiraan waktu **kasar** dan akan direvisi di akhir tiap fase.

## Gambaran Besar

| Fase | Perkiraan Waktu | Hasil |
|---|---|---|
| **0. Setup & Fondasi** | Okt – Nov 2026 (±6 minggu) | Project C++ jalan, Git LFS, belajar alur kerja dasar |
| **1. Prototype (greybox)** | Des 2026 – Mar 2027 (±4 bulan) | Inti gameplay terbukti seru dalam bentuk kotak-kotak |
| **2. Vertical Slice (Ep 1)** | Apr – Des 2027 (±9 bulan) | Episode 1 lengkap dengan kualitas mendekati final |
| **3. Steam Page & Demo** | Jan – Mar 2028 (±3 bulan) | Halaman Steam, trailer, demo untuk Next Fest |
| **4. Produksi Season 1 (Ep 2–10)** | Apr 2028 – ±akhir 2029 (±18 bulan) | 9 episode tambahan |
| **5. Early Access Season 1** | ±Akhir 2029 | Rilis Arc 1 di Steam |

**Total ke rilis Season 1: ±3 tahun** dengan kapasitas sambilan. Lihat [opsi mempercepat](#opsi-mempercepat) di bawah.

---

## Fase 0 — Setup & Fondasi (Okt – Nov 2026)

- [x] Install Unreal Engine 5.6.1
- [x] Install toolchain C++ — Build Tools 2022 + .NET Framework 4.8 SDK + MSVC v14.38 (lihat [12](12-technical-design.md#lingkungan)); IDE penuh opsional
- [x] Buat project C++ **Jayadwara** di `C:\repository\unreal_engine\jayadwara` (template Blank C++, dibuat di folder sementara lalu dipindah, karena wizard menolak folder berisi file)
- [x] Setup Git LFS, `.gitattributes`, `.gitignore`; commit pertama
- [x] Aktifkan plugin inti — GAS, Enhanced Input, StateTree, Niagara, Motion Warping; **Chaos Destruction** (`GeometryCollectionPlugin`, `ChaosEditor`/`Fracture` untuk Fracture Mode) diaktifkan di `.uproject` + `GeometryCollectionEngine` di `Build.cs` (12 Okt 2026, build sukses)
- [x] Kelas C++ dasar (`AJDGameMode`, `AJDPlayerController`, `AJDCharacterBase`, `AJDHumanCharacter`) — build sukses di editor. Setelah `git pull` yang mengubah C++: hapus `Binaries/` lalu buka `.uproject` (tanpa itu editor memuat DLL lama)
- [x] Blueprint dari class C++ (`BP_Aksa`, `BP_JDPlayerController`, `BP_JDGameMode`), level `Test_Greybox`, Play In Editor — dibuat skrip `Tools/ue_setup_greybox.py` lewat Python Remote Execution (12 Okt 2026); `Test_Greybox` jadi map default
- [ ] Siapkan task tracker (Trello / GitHub Projects / Notion)

**Selesai jika**: project bisa di-build dari Visual Studio, karakter default bisa dimainkan, dan semua tersimpan di Git.

### Jalur art paralel — Model Jayadwara (mulai Okt 2026)
Model raksasa Jayadwara dibuat di Blender **lebih awal** dari rencana semula (sebelumnya: pengadaan Apr–Mei 2027) dan **tanpa menunggu UE terpasang**. Rencana, iterasi, dan gate ada di [13-rencana-model-jayadwara.md](13-rencana-model-jayadwara.md).
- Estimasi **±88–110 jam** sebelum integrasi UE (Iterasi 0–5) → menggeser waktu Fase 0–1 pada kapasitas ±50 jam/bulan. Tanggal direvisi di akhir Iterasi 1.
- Proxy dari Iterasi 1 dipakai sebagai pawn raksasa di prototype Fase 1 (Feb 2027).
- Integrasi UE (Iterasi 6) ✅ selesai 12 Okt 2026: Jayadwara 45 m bisa dimainkan di `Test_GiantScale` (detail di [13](13-rencana-model-jayadwara.md)). Socket hit menyusul di Fase 1.

### Jalur paralel — Level/Map *(mulai 16 Okt 2026, keputusan developer)*
Desain map (denah, alur, zona, konsep) dan **greybox UE** dikerjakan terpisah dari iterasi Fase 1, karena sebagian besar keputusannya selera developer. Struktur map mengikuti [28](28-struktur-level-episode.md) (satu map per episode ala RE4). Angka yang bergantung pada Fase 1 (luas arena dari Iterasi 6–8, jumlah gedung dari Iterasi 7) disimpan di file data `Art/Level/`, jadi cukup dikoreksi lalu skrip dijalankan ulang. **Status 17 Okt 2026:** greybox Ep 1 (`Ep01_LawangSapta_Greybox`, [30](30-desain-level-ep01.md)) dan Ep 2 (`Ep02_KampungKali_Greybox`, [31](31-desain-level-ep02.md)) sudah dibangun dari data lewat `Tools/ue_greybox_ep01.py` dan `ue_greybox_ep02.py` (hasil Hermes direview dulu, bug ditemukan dan diperbaiki); level art tetap di fase semula.
- Ep 1: desain [30](30-desain-level-ep01.md), data `Art/Level/ep01_*`, greybox pertama oleh Hermes ([`Hermes/maps_ep1_hermes.md`](../Hermes/maps_ep1_hermes.md), branch `hermes/maps_ep1`).
- Ep 2: desain [31](31-desain-level-ep02.md) (tata letak v02), data `Art/Level/ep02_*`, greybox oleh Hermes ([`Hermes/maps_ep2_hermes.md`](../Hermes/maps_ep2_hermes.md), branch `hermes/maps_ep2`; dimajukan atas permintaan developer 16 Okt 2026).
- Ep 3: desain [32](32-desain-level-ep03.md) v1.0 (tata letak memanjang; H2–H8 disetujui 18 Okt 2026). Data `Art/Level/ep03_*` dan greybox `/Game/Jayadwara/Maps/Ep03_Adikara_Greybox` dibangun 18 Okt 2026 (branch `claude/maps_ep3`); level art tetap Fase 4. Ep 4–10 menyusul.
- Level art realistis tetap di jadwal semula: Ep 1 di Fase 2, Ep 2–10 di Fase 4. Jam editor developer untuk jalur ini dicicil supaya Fase 1 tidak molor.

### Jalur art paralel — Model Aksa *(Iterasi 0 berjalan sejak 12 Okt 2026; jadwal menunggu konfirmasi developer)*
Model Aksa dibuat sendiri di Blender; rencana & iterasi di [19-rencana-model-aksa.md](19-rencana-model-aksa.md) (±90–115 jam), model sheet di [21-model-sheet-aksa.md](21-model-sheet-aksa.md). Sementara, MetaHuman dipakai sebagai placeholder visual. Persiapan (reference plane, model sheet, scene Blender) sudah jadi; spike skeleton menunggu editor UE. Mulai penuh sekarang (menggeser Fase 0–1) atau di pengadaan aset Fase 2 (Apr–Mei 2027) tetap keputusan developer (A9).

### Jalur art paralel — Model Tuyul *(persiapan Ep 2; selesai 16 Okt 2026)*
Model boss + kawanan Ep 2 dikerjakan Hermes di sandbox dari GLB Tripo developer (K0–K7 lulus) dan aset art-nya sudah dimigrasi ke `Art/` dan `Tools/`; rencana dan hasil di [27-rencana-model-tuyul.md](27-rencana-model-tuyul.md). **Tetap di luar scope fase aktif:** `BP_Tuyul`, `ABP_Tuyul`, AI kawanan dan boss, serta level Ep 2 masuk Fase 4 (tabel Ep 2 di bawah). Aset hanya diimpor ke UE untuk uji visual.

## Fase 1 — Prototype Greybox (Des 2026 – Mar 2027)

Tujuan: membuktikan **inti gameplay seru** sebelum membuat aset mahal. Semua visual masih kotak, mannequin, dan Mixamo.

Rencana kerja rinci (iterasi, gate, pembagian Claude/developer): [23-rencana-fase-1.md](23-rencana-fase-1.md).

| Bulan | Target |
|---|---|
| **Des 2026** | Gerak karakter manusia + kamera; combo silat dasar (pukul ringan, berat, hindar, tangkis) |
| **Jan 2027** | Musuh dummy dengan AI sederhana; hit reaction; GAS (Health, Stamina) |
| **Feb 2027** | Transformasi (ganti pawn manusia ↔ raksasa); kamera skala raksasa; combat raksasa memakai sistem yang sama |
| **Mar 2027** | Meter sinkronisasi + gedung hancur (Chaos); satu boss greybox dua fase; playtest |

**Selesai jika**: satu loop utuh — manusia bertarung → berubah wujud → kalahkan boss greybox tanpa merusak terlalu banyak gedung — terasa seru menurut kamu (playtest sendiri di PC developer, keputusan 12 Okt 2026; playtester lain opsional).

## Fase 2 — Vertical Slice: Episode 1 "Gerbang yang Retak" (Apr – Des 2027)

Lihat spesifikasi lengkap di [11-vertical-slice-spec.md](11-vertical-slice-spec.md).

| Periode | Target |
|---|---|
| Apr – Mei 2027 | Art direction final (realistis), art bible ringkas; pengadaan/commission model Aksa, Jayadwara, Jerangkong |
| Jun – Jul 2027 | Level Situs Lawang Sapta + blok kota kecil; scanner Netra + 3 petunjuk |
| Agu – Sep 2027 | Boss Jerangkong final; animasi silat; VFX transformasi |
| Okt – Nov 2027 | Pembuka wayang, briefing, UI/HUD, audio placeholder → audio final |
| Des 2027 | Polish, optimasi, playtest, bug fixing |

**Selesai jika**: Episode 1 bisa dimainkan 20–30 menit dari awal sampai akhir, memenuhi target performa, dan layak dipakai untuk trailer.

## Fase 3 — Steam Page & Demo (Jan – Mar 2028)

- [ ] Capsule art, screenshot, deskripsi Steam (ID + EN)
- [ ] Trailer gameplay dari vertical slice
- [ ] Buka halaman Steam (**secepatnya** — wishlist dikumpulkan dari sini)
- [ ] Demo Episode 1 untuk **Steam Next Fest** terdekat
- [ ] Devlog / media sosial rutin

## Fase 4 — Produksi Season 1: Ep 2–10 (Apr 2028 – ±akhir 2029)

- Rata-rata **±2 bulan per episode** dengan pakai ulang sistem dan aset dari Ep 1.
- Prioritas pembangunan sistem tambahan sesuai kebutuhan episode:

| Episode | Sistem baru yang dibutuhkan |
|---|---|
| Ep 2 (Tuyul) | Kejar-kejaran mode manusia, kawanan musuh |
| Ep 4 (Babi Ngepet) | Investigasi warga / dialog |
| Ep 6 (Kemamang) | Api menyebar, tutorial meter penuh |
| Ep 7 (Kalong Wewe) | Pertarungan udara |
| Ep 9 (Genderuwo) | Musuh tak terlihat + scanner lanjutan |
| Ep 10 (Banaspati) | Kota terbakar skala besar |

- Markas DWARA (hub) dan sistem upgrade dibangun di fase ini.
- Level: satu map per episode ala Resident Evil 4, dari kit distrik yang dipakai ulang ([28](28-struktur-level-episode.md)).

## Fase 5 — Early Access Season 1 (±Akhir 2029)

- Rilis Arc 1 di Steam.
- Kumpulkan feedback → tentukan model Season 2 (update gratis atau DLC) dan apakah perlu menambah tim.

---

## Opsi Mempercepat

| Opsi | Efek |
|---|---|
| **Season 1 diperkecil** jadi Ep 1–5 | Rilis ±1 tahun lebih cepat |
| **Beli / commission aset 3D** karakter dan monster | Memangkas bottleneck terbesar |
| Pakai aset kota realistis dari Fab / Megascans | Level jauh lebih cepat |
| Menambah jam kerja / merekrut 1 artis | Pengaruh terbesar pada timeline |

## Aturan Kerja

- Review roadmap **di akhir setiap fase**; geser tanggal tanpa merasa gagal.
- Fitur yang tidak ada di dokumen fase saat ini → catat di backlog, jangan dikerjakan dulu.
- Commit ke Git minimal setiap sesi kerja.
