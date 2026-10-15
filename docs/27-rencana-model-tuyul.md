# 27 — Rencana Model Tuyul (Boss Ep 2 + Kawanan Kecil)

> **Status: USULAN v0.2 (15 Okt 2026), backlog Fase 4.** Belum ada konsep, model, atau skenario Ep 2. Dokumen ini menetapkan **alur tiga tahap**: developer (konsep + GLB Tripo) → **Hermes** (kerja model di sandbox, instruksi [`Hermes/tuyul_hermes.md`](../Hermes/tuyul_hermes.md)) → **Claude Code** (review, integrasi, polish/perbaikan).
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

Dari [02](02-setting-dunia.md) (energi Kala membesarkan hantu kecil), [06](06-referensi-mitologi.md) (tuyul aman diadaptasi), [16](16-panduan-arc-1.md) ("boleh lucu dan jahil"). Gaya **realistis** ([README](README.md), 14 Okt 2026).

| Hal | Arahan |
|---|---|
| Siluet | Bungkuk dan bulky, tempurung kepala botak besar berjaring retak menyala, telinga runcing panjang, perut buncit, lengan sangat panjang bercakar, kaki pendek kekar |
| Bukan anak manusia | Kulit abu-abu pucat kehijauan, telinga runcing, mata tanpa pupil manusia; bukan goblin/Gollum. Pemain memukul makhluk ini, jadi tidak boleh terbaca sebagai anak sungguhan |
| Nada | Seram dan mengancam, tetapi bukan horor; pencuri serakah yang membesar |
| Pesugihan | Cawat dari karung, kantong di punggung, untaian koin berkarat, uang kertas tersangkut |
| Energi Kala | Merah gelap **emissive** (retak tempurung, mata, urat dada/lengan, retak perut); tanpa biru/silver; tanpa gore |
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
| **T1** | Jenis model | **B**: skeleton sendiri, nama Mannequin, retarget | Usulan |
| **T2** | Tinggi authoring | 1,0 m | Usulan |
| **T3** | Ukuran boss | **1,0× (45 m)**; tuyul besar fase 2 0,6× (27 m) | Arahan developer 15 Okt untuk boss ≥ Jayadwara; angka 0,6× usulan |
| **T4** | Aset | Tiga FBX ter-bake dari satu model (bukan skala actor) | Usulan |
| **T5** | Material | Atlas Tripo + `T_Tuyul_Emit` (R energi Kala, G `RealPulse`, B ornamen) | Usulan |
| **T6** | Cawat/kantong | Di-skin ke tulang, **tanpa Anim Dynamics** | Usulan |
| **T7** | Penanda "yang asli" | Hanya lewat clue CCTV (parameter `RealPulse`) | Usulan |
| **T8** | Wajah | Tanpa morph target; tulang `jaw` bila bibir punya celah; kalau mata/mulut hanya dilukis → GATE K0 | Usulan |
| **T9** | Jadwal | Hermes boleh kapan saja (sandbox, persiapan); Tahap 3 menunggu Fase 4 | Usulan |

## 5. Checklist rating, budaya & IP (dinilai Hermes di K0, diulang Claude di C0)

- [ ] Tanpa gore; merah selalu emissive.
- [ ] Jelas makhluk gaib non-manusia (kulit, telinga, mata), bukan anak sungguhan; tidak meniru tuyul dari film/sinetron/IP tertentu.
- [ ] Tuyul termasuk makhluk **aman** diadaptasi ([06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)); sesajen hanya properti latar, bukan ritual nyata.
- [ ] Energi Kala merah gelap; tanpa biru/silver.
- [ ] Lisensi Tripo (akun yang dipakai) mengizinkan komersial; pengungkapan konten AI di formulir Steam dicatat.

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
| Aturan skala [16](16-panduan-arc-1.md#26-aturan-skala) belum diperbarui | Keputusan Jerangkong/Ep 20 ada di developer; sampai itu, `tuyul_hermes.md` menang untuk Tuyul |

## 7. Hasil

*(Diisi saat Tahap 2 dan 3 berjalan: ringkasan laporan Hermes, putusan C0, hasil C1–C3.)*
