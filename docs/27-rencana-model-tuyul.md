# 27 — Rencana Model Tuyul (Boss Ep 2 + Kawanan Kecil)

> **Status: Tahap 1–2 SELESAI, model dipindah ke proyek (16 Okt 2026); Fase 4 untuk gameplay.** Konsep dan GLB dari developer, Hermes K0–K7 LULUS (gate disetujui developer), review Claude C0 selesai (hasil di bagian 7), aset art dimigrasi ke `Art/` + `Tools/` (C2 sebagian). `BP_Tuyul`, `ABP_Tuyul`, boss `AJDBoss_Tuyul`, kawanan, dan level tetap **Fase 4**. Dokumen ini menetapkan **alur tiga tahap**: developer (konsep + GLB Tripo) → **Hermes** (kerja model di sandbox, instruksi [`Hermes/tuyul_hermes.md`](../Hermes/tuyul_hermes.md)) → **Claude Code** (review, integrasi, polish/perbaikan).
> Mengikuti pola [25](25-rencana-redesign-jayadwara.md) (model Tripo), [20](20-rencana-model-jerangkong.md) (satu model, ukuran ter-bake), `AGENTS.md`, `Hermes/panduan_model_3d.md` (jenis **B**), dan `Hermes/panduan_kerja_claude.md`. Peran di game: [05](05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110), [16](16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul).
> **Scope:** Ep 2 di luar scope fase aktif ([10](10-roadmap.md)). Hermes boleh mengerjakannya di sandbox sebagai **persiapan** (`panduan_model_3d.md` §5); integrasi ke proyek menunggu Fase 4.

## 1. Satu model, tiga ukuran

| Aset | Ukuran | Dipakai untuk |
|---|---|---|
| `SK_Tuyul` | 1,0 m | Kawanan 5 ekor di gang dan atap Kampung Kali (mode manusia) |
| `SK_TuyulBesar` | 27 m (0,6× Jayadwara) | Fase 2: tiga tuyul besar, hanya satu yang asli |
| `SK_TuyulRaksasa` | 45 m (1,0× Jayadwara) | Fase 1: kawanan bergabung, lari dan mencuri properti |

- **Satu model saja** (keputusan developer 15 Okt 2026, supaya tidak mengerjakan dua kali): desain boss (besar dan seram) dipakai juga untuk kawanan kecil; bedanya hanya ukuran. Konsekuensi: tidak ada varian dengan banyak kepala/tangan tambahan (tidak masuk akal di 1 m), dan kawanan terbaca seram-jahil, bukan lucu.
- Skala **di-bake saat export** (pola Jerangkong J2), bukan skala actor di UE.
- Badan **di-skin lunak** (Tuyul tidak rontok/susun ulang seperti Jerangkong), jadi tidak ada potongan kaku atau `SM_` per bagian.
- **Ukuran boss 1,0×** adalah arahan developer (15 Okt 2026: boss sama atau lebih besar dari Jayadwara, seperti kaiju Ultraman). Konflik dengan aturan skala lama **sudah diselesaikan** (keputusan F1, 15 Okt 2026): [16 bagian 2.6](16-panduan-arc-1.md#26-aturan-skala) sekarang membolehkan boss Arc 1 sampai 1,0×. Jerangkong tetap 0,7×.

## 2. Arahan desain (usulan)

Dari [02](02-setting-dunia.md) (energi Kala membesarkan hantu kecil), [06](06-referensi-mitologi.md) (tuyul aman diadaptasi), [16](16-panduan-arc-1.md) (nada diubah 16 Okt 2026: seram dan body-horror). Gaya **realistis** ([README](README.md), 14 Okt 2026).

| Hal | Arahan |
|---|---|
| Siluet | Bungkuk dan bulky, tempurung kepala botak besar berjaring retak menyala, telinga runcing panjang, perut buncit, lengan sangat panjang bercakar, kaki pendek kekar |
| Bukan anak manusia | Kulit coklat-abu gelap (final `#64584A`; usulan awal abu-hijau `#8E9A8B`), telinga runcing, mata tanpa pupil manusia; bukan goblin/Gollum. Pemain memukul makhluk ini, jadi tidak boleh terbaca sebagai anak sungguhan |
| Nada | **Seram dan body-horror** (keputusan developer 16 Okt 2026); pencuri serakah yang membesar. Sosok kecil menyerupai bayi/tengkorak dan tangan kecil menempel di perut, bahu, dan punggung adalah desain sengaja (pengecualian gore, lihat bagian 5) |
| Pesugihan | Cawat dari karung, kantong di punggung, untaian koin berkarat, uang kertas tersangkut |
| Energi Kala | Merah gelap **emissive** (retak tempurung, mata, urat dada/lengan, retak perut); tanpa biru/silver; tanpa darah atau luka basah. Final di UE: `AccentColor` (0,22; 0,010; 0,008) x `GlowIntensity` 0,6 |
| Fase 2 | Tiga tuyul besar identik; penanda "yang asli" = parameter material `RealPulse` (ubun-ubun) saat clue CCTV aktif |

## 3. Alur tiga tahap

```
Developer: konsep + GLB Tripo ──► Hermes: K0–K7 di sandbox (hermes/tuyul) ──► Claude Code: C0–C3
                                        │ GATE di K0, K3, K6                        │
                                        └─ laporan + FBX + aset sandbox ───────────┘
```

### Tahap 1 — Developer
1. Buat konsep dari [`Art/Reference/prompt_tuyul.md`](../Art/Reference/prompt_tuyul.md), simpan di `docs/concept-art/tuyul_v01.*`.
2. Generate model di Tripo dari konsep (ikuti "Tips Tripo" di file prompt), simpan GLB asli di folder lokal.
3. Beri Hermes tugas: `Hermes/tuyul_hermes.md` (worktree sendiri, branch `hermes/tuyul`). Developer menyetujui di gate K0, K3, K6.

### Tahap 2 — Hermes (K0–K7)
Detail langkah dan kriteria lulus di [`Hermes/tuyul_hermes.md`](../Hermes/tuyul_hermes.md). Ringkas:

| Iter | Isi | Gate |
|---|---|---|
| K0 | Intake GLB, kartu model, penilaian (termasuk "bukan anak manusia", geometri mata/mulut) | **Ya** |
| K1 | Skeleton sendiri bernama Mannequin dari landmark mesh | |
| K2 | Pemisahan bagian menyatu, tutup lubang, bersihkan merah basah | |
| K3 | Skinning lunak, export LOD0, validator, audit + banding | **Ya** |
| K4 | Tekstur + `T_Tuyul_Emit` (energi Kala, `RealPulse`, ornamen) | |
| K5 | LOD1–3 dan tiga skala | |
| K6 | Uji di UE sandbox (`/Game/Hermes/Tuyul/`, level `Test_Hermes_Tuyul`) | **Ya** |
| K7 | Laporan akhir + usulan integrasi | |

### Tahap 3 — Claude Code (review, integrasi, polish)
Sesuai `CLAUDE.md` bagian "Hasil kerja Hermes", dimulai setelah developer bilang hasilnya mau dipakai (atau hasilnya belum finish).

| Iter | Isi | Lulus |
|---|---|---|
| **C0 Review** | Baca `Hermes/Laporan/*-tuyul.md`; ulangi sendiri `audit_karakter.py` + `banding_karakter.py` (jangan percaya angka laporan); `git diff origin/development...origin/hermes/tuyul --stat` dan tandai apa pun di luar sandbox; cek checklist bagian 5 | Putusan tertulis: **lulus** / **perlu perbaikan** / **ulang** |
| **C1 Perbaikan** *(bersyarat)* | Kalau belum finish: `diagnosa_mesh.py` → `perbaiki_mesh.py` → diagnosa ulang `--sebelum` ([`panduan_kerja_claude.md`](../Hermes/panduan_kerja_claude.md) §3). Perbaikan khas: ketiak/selangkangan bolong, melar di perut buncit, bobot telinga/kepala, merah basah, bayangan terpanggang, wajah terbaca anak manusia | Tiap temuan C0 selesai atau diterima developer |
| **C2 Integrasi** | Pindah ke struktur proyek: FBX + socket JSON ke `Art/Export/`, skrip ke `Art/Scripts/`/`Tools/` (hapus path tetap), `Tools/ue_import_tuyul.py` + `ue_setup_tuyul.py` (aset ke `/Game/Jayadwara/Characters/Tuyul/`, tidak pernah ke `SK_Mannequin`), `IK_Tuyul` + `RTG_Mannequin_To_Tuyul`, `ABP_Tuyul`, `BP_Tuyul` (Character), `BP_TuyulBesar` dan `BP_TuyulRaksasa` (`AJDGiantCharacter`), `PLACE_IN_LEVELS = False` seperti Jerangkong. `.uasset` hasil sandbox dipindah developer di editor (Move + Fix Up Redirectors) atau diimpor ulang lewat skrip | Aset terpasang; tidak ada aset lama berubah |
| **C3 Polish** | Material master + `MI_Tuyul` (`GlowIntensity`, `RealPulse`, `OrnamentHide`), socket `head_top` → HUD, uji 5 ekor + boss (FPS), perbarui `docs/` (README, 16, 05, 18) | Developer menilai di level uji |

**Pembagian kerja ringkas**

| Developer | Hermes | Claude Code |
|---|---|---|
| Konsep, GLB Tripo, gate K0/K3/K6, animasi dan rasa skala di editor | Pekerjaan model + laporan di sandbox | Review, perbaikan, integrasi ke proyek, C++/Blueprint (`AJDBoss_Tuyul`, kawanan), dokumen |

## 4. Keputusan

| # | Keputusan | Default | Status |
|---|---|---|---|
| **T1** | Jenis model | **B**: skeleton sendiri, nama Mannequin, retarget | Terlaksana (52 tulang, 3 jari) |
| **T2** | Tinggi authoring | 1,0 m | Terlaksana |
| **T3** | Ukuran boss | **1,0× (45 m)**; tuyul besar fase 2 0,6× (27 m) | Disetujui (F1, 15 Okt); [16 bagian 2.6](16-panduan-arc-1.md#26-aturan-skala) sudah diperbarui |
| **T4** | Aset | Tiga FBX ter-bake dari satu model (bukan skala actor) | Terlaksana (12 FBX: 3 skala x LOD0–3) |
| **T5** | Material | Atlas Tripo + `T_Tuyul_Emit` (R energi Kala, G `RealPulse`, B ornamen) | Terlaksana (1 slot); parameter `RealPulse` menyusul di polish |
| **T6** | Cawat/kantong | Di-skin ke tulang, **tanpa Anim Dynamics** | Terlaksana (kantong punggung didominasi `clavicle`, bukan `pelvis`; lihat R5 bagian 7) |
| **T7** | Penanda "yang asli" | Hanya lewat clue CCTV (parameter `RealPulse`) | Mask siap (kanal G, hanya ubun-ubun); parameter di polish |
| **T8** | Wajah | Tanpa morph target; tulang `jaw` bila bibir punya celah; kalau mata/mulut hanya dilukis → GATE K0 | Terlaksana (tulang `jaw`) |
| **T9** | Jadwal | Hermes boleh kapan saja (sandbox, persiapan); Tahap 3 menunggu Fase 4 | **Direvisi 16 Okt 2026:** bagian art Tahap 3 (review, migrasi aset) dikerjakan sekarang atas permintaan developer; gameplay, BP, dan level tetap Fase 4 |

## 5. Checklist rating, budaya & IP (dinilai Hermes di K0, diulang Claude di C0)

- [ ] Tanpa gore; merah selalu emissive. **Pengecualian disetujui developer (16 Okt 2026):** tanpa darah, merah memang hanya emissive, tetapi geometri memuat sosok bayi/tengkorak dan tangan kecil menempel (body-horror sengaja). Dicatat untuk rating remaja.
- [x] Jelas makhluk gaib non-manusia (kulit, telinga runcing, cakar, proporsi), bukan anak sungguhan; tidak meniru tuyul dari film/sinetron/IP tertentu. (Hermes K0 dan review C0.)
- [x] Tuyul termasuk makhluk **aman** diadaptasi ([06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)); sesajen hanya properti latar, bukan ritual nyata.
- [x] Energi Kala merah gelap; tanpa biru/silver.
- [ ] Lisensi Tripo (akun yang dipakai) mengizinkan komersial; pengungkapan konten AI di formulir Steam dicatat. **Belum dikonfirmasi** (developer membahasnya di akhir migrasi; cek juga `Art/README.md` bagian aset pihak ketiga).

## 6. Risiko

| Risiko | Mitigasi |
|---|---|
| GLB Tripo: mata/mulut dilukis, jari menempel (pelajaran Aksa2 H3b, Jerangkong) | Tips Tripo di file prompt; K0 mencatat, GATE sebelum rig |
| Terbaca "anak manusia yang dipukul" | Arahan bagian 2 + penilaian K0 + C0 |
| Skinning lunak di perut buncit/leher pendek melar atau bolong | Banding terhadap `SK_Aksa` untuk regangan; ketiak dari bawah; C1 tersedia |
| Kepala besar dan lengan panjang membuat animasi manusia terlihat aneh | Pose retarget di `RTG` + animasi kustom lari/lompat |
| Desain seram dipakai di 1 m: kawanan terbaca terlalu mengancam atau tidak lucu | Disengaja (satu model); nada jahil-kejam diatur lewat animasi dan SFX, bukan model kedua |
| Boss 45 m berproporsi kecil-kepala-besar tidak terbaca dari kamera | K6 membandingkan tiga skala dengan `SK_Jayadwara2`; ukuran bisa diubah tanpa model ulang |
| Kawanan 5 ekor + boss berat | Kawanan mulai LOD1; uji FPS di C3 |
| Aturan skala [16](16-panduan-arc-1.md#26-aturan-skala) belum diperbarui | **Selesai** (F1, 15 Okt 2026): boss Arc 1 boleh 0,5–1,0x |

## 7. Hasil

### 7.1 Tahap 2 — Hermes K0–K7 (branch `hermes/tuyul`, 16 Okt 2026, semua gate disetujui developer)

| Iter | Hasil | Catatan |
|---|---|---|
| K0 Intake | 1,0000 m, 38.101 tris, 1 mesh, menghadap -Y | Checklist IP: gore ditandai, disetujui sebagai pengecualian |
| K1 Skeleton | 52 tulang (45 deform + 7 IK), 88/88 sendi di dalam mesh | Tangan hanya 3 jari (`thumb`/`index`/`middle`); tulang `jaw` ditambah |
| K2 Bersih | Tepi terbuka 1→0, non-manifold 2→0, IoU badan 0,9996 | Merah basah di tekstur dinetralkan |
| K3 Skinning | Validator 18/18, 8 socket, regangan p99 **52,9%** (batas 40%) | Banding GAGAL, **diterima developer (opsi a)** |
| K4 Tekstur | 5 peta 4096², `T_Tuyul_Emit` R/G (hanya ubun-ubun)/B | Kulit `#64584A` |
| K5 LOD | 12 FBX (3 skala x LOD0–3), 38.090/30.000/14.000/6.000 tris | Regangan LOD1–3 p99 137–165%, diterima |
| K6 UE sandbox | Impor 3 skala, 8 socket, IK Retargeter, anim retarget, Lumen bersih | Pendar dark red (rev3), disetujui |
| K7 Serah terima | Laporan akhir | `Hermes/Laporan/2026-10-16-tuyul.md` |

### 7.2 Tahap 3 — Claude C0 (review) dan C2 (migrasi), 16 Okt 2026

**Putusan C0: LULUS dengan catatan (risiko diterima, uji dan perbaiki setelah masuk `development`).**
- Scope: 897 file berubah, 0 di luar sandbox (`Tools/hermes_cek_sandbox.py` LULUS); uji merge ke `development` bersih.
- Angka Hermes diulang sendiri di Blender 5.2: validator 18/18 pada ke-12 FBX, tris, tinggi, socket (skala 27 dan 45 benar), audit LOD0 x1 (9/10, p99 74,2% `jongkok`) dan banding vs Aksa (GAGAL) **cocok persis**.
- C1 (perbaikan) **tidak dilakukan**: developer memilih menerima apa adanya dan memperbaiki di `development` setelah uji.
- C2 (migrasi): FBX + socket JSON ke `Art/Export/`, tekstur final ke `Art/Export/Textures_Tuyul/`, GLB ke `Art/Source/`, `.blend` final (`tuyul_v05_skin`, `tuyul_v09_smooth`) ke `Art/Blender/tuyul/`, 17 skrip ke `Art/Scripts/` (path via `tuyul_paths.py`), impor UE di `Tools/ue_import_tuyul.py` + `Tools/ue_setup_tuyul.py` (aset ke `/Game/Jayadwara/Characters/Tuyul/`). Bukti gambar, audit, banding, dan `.blend` perantara tetap di branch `hermes/tuyul`.
- **Uji impor UE (tahap 10, 17 Okt 2026, UE 5.6.1):** `Tools/ue_import_tuyul.py` dan `Tools/ue_setup_tuyul.py` berhasil pada percobaan pertama. Terbentuk 12 aset di `/Game/Jayadwara/Characters/Tuyul/` (3 mesh, `SKEL_Tuyul`, 4 tekstur, `M_Tuyul_Master`, `MI_Tuyul_Body`, `IK_Tuyul`, `RTG_Mannequin_To_Tuyul`; ±88 MB). Tinggi 100,0 / 2700,0 / 4500,0 cm, 4 LOD (screen size 1,0/0,45/0,22/0,10), 8 socket per mesh, `IK_Tuyul` 16 chain, `SK_Mannequin` tetap 171 tulang, tidak ada aset lama berubah.

### 7.3 Risiko yang diterima (uji di `development`)

| # | Risiko | Rencana |
|---|---|---|
| R1 | Regangan skinning x1: p99 52,9% (batas 40%); `jongkok` 74%, lengan terangkat 73% | Pantau dengan animasi sungguhan |
| R2 | Regangan LOD1–3: p99 137–165% | Kawanan memakai LOD1+; pantau |
| R3 | **Boss 27 m dan 45 m, LOD0:** p99 77–328%, regangan maks sampai 9,4 m (pose lengan terangkat); dari bawah kulit ketiak/bahu tampak "meleleh", tanpa lubang | Uji pose lengan angkat; cat bobot bahu bila perlu |
| R4 | Bobot LOD0 `SK_Tuyul` (x1, dari `tuyul_v05_skin`: 1.988 vertex 1-tulang) berbeda dari x27/x45 dan semua LOD (`v06`+: 3.615); sebab perbedaan belum diketahui | Samakan bobot (v05 lebih lunak) bila R3 menuntut perbaikan; `v05` ikut dimigrasi untuk ini |
| R5 | Bobot kantong punggung didominasi `clavicle`, belum dikunci ke `pelvis` seperti T6 | Bagian dari perbaikan R3 |
| R6 | Geometri body-horror: rating remaja dan formulir Steam; kemiripan dengan Ep 8 (Wewe Gombel) **dibiarkan** | Dicatat di [16](16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul) Ep 2 |
| R7 | Pendar di UE terbaca sebagai bercak merah bertepi keras di lutut, lengan, rahang/leher (bukan retakan tipis seperti render Blender), dan bercak di sekitar mulut mudah terbaca seperti darah; kulit tampak gelap kebiruan di bawah cahaya langit (27 m) tetapi krem terang di skala 1 m (eksposur/cahaya berbeda). Dikonfirmasi lagi 17 Okt 2026 | Polish material (C3): mask Emit lebih tipis, parameter `BaseColor`/tint, uji di level malam |
| R8 | `SKEL_Tuyul` = duplikat `SK_Mannequin` + Compatible Skeleton; `M_Tuyul_Master` = duplikat `M_Aksa2_Master` | Impor lewat skrip, bukan memindahkan `.uasset`; pola sama dengan Aksa2 |
| R9 | Rantai emissive `M_Tuyul_Master` ditulis ulang di `ue_import_tuyul.py` | **Selesai (17 Okt 2026):** diuji di editor; rantai `Multiply(Multiply(Saturate(Dot(Emit, 1,1,1)), AccentColor), GlowIntensity)` terbentuk, MI membawa dark red x 0,6, tampilan sama dengan tangkapan Hermes K6 |

### 7.4 Catatan terbuka

- **Lisensi Tripo dan pengungkapan AI di Steam** belum dikonfirmasi (dibahas developer di akhir).
- Keputusan developer 16 Okt 2026: nada Tuyul **seram dan body-horror** (bukan lucu); kemiripan dengan Wewe Gombel **dibiarkan**.
- Belum ada: `BP_Tuyul`, `ABP_Tuyul`, parameter material `RealPulse`, AI kawanan dan boss, level. Semuanya Fase 4.
