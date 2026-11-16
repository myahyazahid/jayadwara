# Tuyul — Instruksi Kerja untuk Hermes

> Dari Claude, untuk Hermes. **File ini read-only bagimu**; progres ditulis di `Hermes/Laporan/YYYY-MM-DD-tuyul.md`.
> Baca dulu `AGENTS.md` sampai habis (terutama §0 Cara kerja, §3 Unreal, §5 Blender), lalu [`panduan_model_3d.md`](panduan_model_3d.md) (jenis **B**, iterasi K0–K7) dan [`panduan_kerja_claude.md`](panduan_kerja_claude.md) §8 (model realistis). Semua aturan di sana berlaku. Kalau ada beda, file ini menang atas `panduan_model_3d.md`, dan `AGENTS.md` menang atas keduanya.
> Contoh terisi untuk jenis A: [`aksa_hermes.md`](aksa_hermes.md). Rencana lengkap dan tahap Claude sesudahnya: `docs/27-rencana-model-tuyul.md`.
> Versi: 15 Okt 2026.
> **Di luar scope fase aktif (persiapan):** boss Ep 2 masuk Fase 4 (`docs/10`). Tulis kalimat itu di laporan. Integrasi ke proyek menunggu fasenya.

---

## 0. Ringkasan

**Tuyul** = boss Ep 2 "Tangan-Tangan Kecil" (`docs/05`, `docs/16` kartu Ep 2). **Satu model saja**: desain boss (besar dan seram) dipakai juga untuk kawanan kecil, bedanya hanya ukuran (keputusan developer 15 Okt 2026, supaya tidak mengerjakan dua kali). Jadi tiga ukuran dari satu model:

| Aset | Ukuran | Dipakai untuk |
|---|---|---|
| `SK_Tuyul` | **1,0 m** | Kawanan 5 ekor yang dikejar Aksa di gang dan atap |
| `SK_TuyulBesar` | **27 m** (0,6× Jayadwara) | Fase 2: tiga tuyul besar, hanya satu yang asli |
| `SK_TuyulRaksasa` | **45 m** (1,0× Jayadwara) | Fase 1: kawanan bergabung jadi satu, mencuri properti |

**Ukuran boss 1,0×** mengikuti arahan developer 15 Okt 2026 ("boss sama atau lebih besar dari Jayadwara"). Itu **berbeda** dari `docs/16` §2.6 (Tuyul 0,5×) dan baris Tuyul di `panduan_model_3d.md` §1: untuk Tuyul, **file ini yang berlaku**. `docs/16` akan diperbarui Claude; jangan kamu ubah. Skala di-**bake** saat export (bukan skala actor), pola Jerangkong J2 (`docs/20`).

Sumber model: GLB **Tripo** dari developer (realistis, `docs/README` 14 Okt 2026). Kerjamu: intake, skeleton, pembersihan, skinning, tekstur, LOD, uji di UE sandbox. Pembanding wajib: `SK_Jerangkong` (§0 di bawah dan K0).

### Sumber kebenaran (baca, jangan ubah)
| Dokumen / file | Isi yang dipakai |
|---|---|
| `docs/05` (baris Ep 2), `docs/16` (kartu Ep 2), `docs/02` (energi Kala membesarkan hantu kecil) | Peran dan mekanik |
| `docs/06` (+ panduan sensitivitas) | Tuyul = makhluk **aman diadaptasi** |
| `docs/20`, `docs/24` | Pola Jerangkong: satu model, dua aset ter-bake, material + mask emissive, socket |
| `docs/25` (R2–R8) | Pelajaran model Tripo (ketiak bolong, insiden `SK_Mannequin`) |
| `Art/Export/SK_Jerangkong.fbx`, `SK_Jerangkong_sockets.json` | Pembanding (`--lama`) |
| `Art/Scripts/jk_skeleton.py`, `jd2_skeleton.py` | Pola skeleton sendiri bernama Mannequin, sendi diukur dari mesh |
| `Art/Scripts/jerangkong_01_import_tripo.py`, `jerangkong_14_export.py` | Pola intake dan export |
| `Art/Scripts/pose_profil/manny.json` | Profil pose (default, jenis B) |

### Arahan desain (dari developer + docs)
- **Desain boss**: bungkuk dan bulky, tempurung kepala botak besar berjaring retak merah menyala, telinga runcing panjang, mata merah menyala di bawah alis tebal, rahang lebar bergigi kecil runcing dengan celah bibir, perut buncit berurat menyala, lengan sangat panjang (melewati lutut) bercakar, kaki pendek kekar. Siluet terbaca dari kamera raksasa.
- Satu model dipakai di 1 m (kawanan), 27 m, dan 45 m: **jangan** menambah detail yang hanya masuk akal di satu ukuran (mis. banyak kepala/tangan tambahan; varian "kawanan menyatu" dibatalkan karena tidak bisa dipakai untuk kawanan kecil).
- **Bukan anak manusia, bukan goblin/Gollum**: kulit abu-abu pucat kehijauan, telinga runcing, mata tanpa pupil manusia. Pemain memukul makhluk ini; tidak boleh terbaca sebagai anak sungguhan.
- Seram dan mengancam, tetapi **bukan horor**; ada nada jahil-kejam (pencuri serakah yang membesar). Cawat dari karung lusuh, kantong di punggung, untaian koin berkarat dan uang kertas tersangkut di badan.
- Energi Kala **merah gelap emissive** (retak tempurung, mata, urat dada/lengan, retak perut). Tanpa biru/silver. **Tanpa gore.**
- Fase 2: tiga tuyul besar **identik secara bentuk**. Penanda "yang asli" datang dari clue CCTV lewat parameter material `RealPulse` (denyut halus di ubun-ubun), bukan dari bentuk.

---

## 1. Persiapan (sekali)

```
cd C:\repository\unreal_engine\jayadwara
git fetch origin development
git worktree add C:\repository\unreal_engine\jayadwara_hermes_tuyul -b hermes/tuyul origin/development
cd C:\repository\unreal_engine\jayadwara_hermes_tuyul
git lfs pull
```
Kalau worktree `jayadwara_hermes` masih dipakai tugas lain: pakai folder di atas (atau `git switch -c hermes/tuyul origin/development` setelah tugas lama di-push, AGENTS.md §1a). Perintah di bawah dijalankan dari WORKTREE; `blender` = path lengkap `blender.exe` Blender 5.2.

### Nama & lokasi (pakai persis)
| Apa | Path |
|---|---|
| Sumber GLB | `Hermes/Art/tuyul/Source/tuyul_tripo_v01.glb` (salinan; asli developer tidak diubah) |
| Konsep | `Hermes/Art/tuyul/Reference/` (salinan dari `docs/concept-art/tuyul_v01.*` bila ada) |
| File Blender | `Hermes/Art/tuyul/Blender/tuyul_v01_intake.blend`, `tuyul_v02_rig.blend`, ... (nomor naik, tidak menimpa) |
| Skrip | `Hermes/Tools/tuyul_<nomor>_<nama>.py` |
| Export | `Hermes/Art/tuyul/Export/SK_Tuyul.fbx`, `SK_TuyulBesar.fbx`, `SK_TuyulRaksasa.fbx` (+ `_LOD1..3`), `*_sockets.json`, `Textures/T_Tuyul_*.png` |
| Audit / Banding | `Hermes/Art/tuyul/Audit/<nama>/`, `Hermes/Art/tuyul/Banding/<langkah>/` |
| Aset UE | `/Game/Hermes/Tuyul/{Rig,Mesh,Materials,Textures,Maps}/` |
| Laporan | `Hermes/Laporan/YYYY-MM-DD-tuyul.md` |
| Objek Blender | awalan `TY_` (`TY_Body`, `TY_Armature`) |

### Pembanding (sekali, di awal)
```
blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- Art/Export/SK_Jerangkong.fbx --out Hermes/Art/tuyul/Audit/lama --height 30.66
```
Harus selesai tanpa error. `SK_Jerangkong` model **kaku** (potongan), jadi regangan ≈ 0 % dan **tidak bisa dipakai menilai kualitas skinning lunak** Tuyul. Karena itu tambahkan pembanding kedua khusus regangan/bobot (sama-sama default `manny.json`):
```
blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- Art/Export/SK_Aksa.fbx --out Hermes/Art/tuyul/Audit/lama_aksa --height 1.806
```
`panduan_kerja_claude.md` §8: antar-gaya, tepi terbuka/normal/tembus tidak bisa dibandingkan; nilai lewat gambar.

---

## 2. Cara membaca hasil audit & banding

Ikuti **`aksa_hermes.md` §2** apa adanya (berlaku untuk semua model), dengan dua perbedaan:
- `banding_karakter.py --lama Audit/lama` (Jerangkong) untuk siluet, pose, dan deskripsi per pose; `--lama Audit/lama_aksa` hanya untuk regangan per pose. Profil pose sama untuk lama dan baru. `--toleransi 3` (kualitas dilihat dekat).
- IoU **tidak** dibandingkan antar-model berbeda bentuk (`panduan_model_3d.md` §4); yang dibandingkan regangan per pose dan gambar.

---

## 3. Kartu model (K0, isi di laporan, jangan ubah isinya tanpa gate)

```markdown
## Kartu model: Tuyul
- Topik/branch: hermes/tuyul
- Jenis: B — alasan: biped dengan proporsi sendiri (kepala besar, kaki pendek); skeleton sendiri, nama dan hierarki tulang Manny; animasi lewat IK Retargeter (pola jk_skeleton.py / jd2_skeleton.py)
- Sumber desain: docs/05 baris Ep 2, docs/06 (aman diadaptasi), docs/16 kartu Ep 2, docs/02 (energi Kala)
- Konsep/referensi dari developer: Hermes/Art/tuyul/Reference/... (tulis path; belum ada → tulis "tidak ada, hanya GLB")
- Mekanik yang butuh geometri/tulang khusus: kawanan kecil yang berlari/melompat di atap; boss mengangkat dan melempar properti (mobil, gerobak) → socket carry; ubun-ubun menyala saat clue aktif (RealPulse); mulut menyeringai/berteriak
- Tinggi authoring: 1,0 m (tinggi berdiri bungkuk; model sama untuk ketiga ukuran) | skala bake: kecil 1,0 m, besar 27 m (0,6× Jayadwara), raksasa 45 m (1,0× Jayadwara, arahan developer 15 Okt)
- Skeleton: sendiri (nama Mannequin) + tulang tambahan `jaw` (hanya kalau mulut punya celah, cek di K0) + tulang telinga TIDAK ditambah
- Profil pose: Art/Scripts/pose_profil/manny.json
- Pembanding (--lama): Art/Export/SK_Jerangkong.fbx (monster biped terdekat, kaku) + Art/Export/SK_Aksa.fbx (regangan/bobot lunak saja)
- Anggaran tris LOD0/1/2/3: 100k/30k/14k/6k untuk ketiga ukuran (satu model, LOD sama; boss raksasa seperti Jayadwara2). Kawanan 5 ekor (`SK_Tuyul`) di UE mulai dari LOD1. Terlampaui → LAPORKAN angkanya, jangan decimate agresif
- Gaya: realistis (docs/README 14 Okt). Baca panduan_kerja_claude.md §8
- Slot material: ikut atlas Tripo (target 1–2). Mask emissive T_Tuyul_Emit: R = energi Kala, G = RealPulse (ubun-ubun), B = uang/ornamen
- Socket: hand_l_hit (hand_l), hand_r_hit (hand_r), foot_l_hit (foot_l), foot_r_hit (foot_r), head_top (head, penanda RealPulse & HUD), carry_l (hand_l), carry_r (hand_r), mouth_fx (head/jaw)
- Ekspresi wajah: tanpa morph target. Mulut: tulang jaw bila ada celah bibir; kalau bibir menyatu → tulis dan GATE (jangan mengarang geometri)
- Checklist IP/budaya: bukan anak manusia (kulit, telinga, mata); tidak meniru tuyul dari film/sinetron/IP tertentu; tanpa gore; merah hanya emissive; tidak ada ritual nyata (sesajen hanya properti latar)
- Nama: objek Blender TY_, aset SK_Tuyul / SK_TuyulBesar / SK_TuyulRaksasa, UE /Game/Hermes/Tuyul/
```
Palet usulan (dikunci developer di K0): kulit `#8E9A8B` (bayangan `#6F7A6D`), cawat `#5A4A3A`, mata `#0B0B0B`, pendar Kala `#8B1A1A` **emissive** (bukan warna dasar).

---

## 4. Iterasi

Setiap iterasi: kerjakan → jalankan cek → isi tabel progres → commit (`hermes_cek_sandbox.py` LULUS dulu, pesan commit `[hermes] tuyul ...`) → push. Bertanda **GATE** = berhenti dan tunggu developer bilang "lanjut". Tabel kriteria lulus per iterasi sama dengan `panduan_model_3d.md` §3; yang khusus Tuyul:

### K0 — Intake GLB & kartu · **GATE**
1. Salin GLB ke `Hermes/Art/tuyul/Source/tuyul_tripo_v01.glb`.
2. Salin `Art/Scripts/jerangkong_01_import_tripo.py` → `Hermes/Tools/tuyul_01_import_tripo.py`; ubah hanya path, nama objek (`TY_Source`), collection, `ROOT` → WORKTREE; cek `findstr` AGENTS.md §5. Jalankan dengan tinggi kepala sesuai kartu (1,0 m); arah hadap -Y (coba `--rot-z` 0/90/-90/180).
3. Render ortografis depan/samping/belakang; kalau ada konsep, pakai kanvas yang sama.
4. Laporan K0: kartu model (§3), tris/objek/material/ukuran tekstur, non-manifold, pulau mesh, simetri, **bagian menyatu** (jari, lengan ke badan, cawat ke paha, kantong ke badan), **geometri wajah** (apakah mata punya kelopak/bola mata terpisah atau hanya dilukis; apakah bibir punya celah; jumlah vertex kepala), bayangan terpanggang di tekstur (render datar), noda merah basah di kulit, checklist IP satu per satu (✅/❌), penilaian "terbaca bukan anak manusia" (ya/tidak + alasan dari gambar).
- **Lulus K0:** tinggi 1,0 m ±1 %; menghadap -Y; tidak ada ❌ di checklist IP. **GATE:** developer menyetujui kartu dan GLB (atau minta GLB baru).

### K1 — Skeleton sendiri (nama Mannequin)
Skeleton dari landmark mesh (pola `jk_skeleton.py`/`jd2_skeleton.py`): hierarki dan nama Mannequin, root di tanah menghadap +Y, tanpa twist bone, `jaw` hanya bila disetujui di K0. Tabel sendi (posisi terukur dari mesh) di laporan.
- **Lulus K1:** setiap sendi di dalam volume mesh (render tulang tembus pandang).

### K2 — Pemisahan & pembersihan
Pisahkan yang menyatu (dari laporan K0), tutup lubang, buang serpihan, bersihkan merah basah di kulit tekstur (netralkan ke warna kulit; pendar hanya lewat emissive). Mesh-mu bukan model kaku: **jangan memotong badan jadi potongan**.
- **Lulus K2:** tepi terbuka di zona ketiak, selangkangan, leher, siku dalam turun (angka sebelum/sesudah); IoU badan selisih ≤ 0,02 dari K1.

### K3 — Skinning · **GATE**
Bobot lunak (otomatis lalu dirapikan di bahu, pinggul, perut buncit, leher, kaki); cawat dan kantong dikunci ke `pelvis`/tulang terdekat; maks 4 influence, normalisasi. Export LOD0 `SK_Tuyul.fbx` (kontrak `docs/20` §6.5 / Jayadwara pasca-Iterasi 6: armature `Armature`, cm, skala di-apply, `FBX_SCALE_ALL`, tanpa empty/animasi), socket JSON (§3). Cek berurutan: validator (salin `validate_jerangkong.py`/`validate_jayadwara.py` ke `Hermes/Tools/validate_tuyul.py`, ubah profil: tidak kaku, 1 tulang tidak wajib; nama tulang Mannequin, tinggi, UV, slot, socket), `audit_karakter.py`, `banding_karakter.py`.
- **Lulus K3:** validator PASS (tempel output); VONIS LULUS terhadap dua pembanding (§1); deskripsi setiap pose di laporan (cara `aksa_hermes.md` §2.3), tanpa lubang di ketiak/selangkangan dan tanpa melar yang terlihat. **GATE:** developer menilai `banding_pose.png`.
- Gagal 3× → berhenti dan laporkan (AGENTS.md §0.5).

### K4 — Tekstur & material
Atlas Tripo dipertahankan. Perbaiki warna salah; buat `T_Tuyul_N`, `T_Tuyul_ORM`, dan **`T_Tuyul_Emit`** (R, G, B sesuai kartu; area pendar hanya di zona konsep: mata, urat dada/lengan, ubun-ubun). Render datar (Workbench TEXTURE) untuk bayangan terpanggang.
- **Lulus K4:** hex sampel per zona palet vs usulan; pendar terbaca emissive, bukan basah/darah; `RealPulse` (G) hanya di ubun-ubun; laporan bayangan terpanggang (lokasi).

### K5 — LOD & tiga skala
LOD1–3 (pola `jayadwara2_16_make_lods.py`; lindungi kepala, mata, tangan). Export **tiga skala** dari model yang sama: `SK_Tuyul` (×1), `SK_TuyulBesar` (×27), `SK_TuyulRaksasa` (×45). Audit tiap skala dengan `--height` miliknya (1.0 / 27.0 / 45.0).
- **Lulus K5:** 4 LOD × 3 skala: validator PASS; tabel tris; banding LULUS per LOD (pembanding LOD1–3 Jerangkong sesuai ketersediaan; tulis kalau tidak ada).

### K6 — Uji di Unreal (sandbox) · **GATE**
Ikuti `aksa_hermes.md` H6 (salinan skeleton di sandbox, **tidak pernah impor ke `SK_Mannequin`**; `SKEL_Tuyul` ditambah Compatible Skeletons `SK_Mannequin`; impor di `/Game/Hermes/Tuyul/Mesh/`; level `Test_Hermes_Tuyul` dari duplikat `Test_Combat`; `SK_Jerangkong`/`SK_Aksa` tidak perlu, cukup ketiga skala Tuyul berdampingan dengan `SK_Jayadwara2` untuk rasa skala). Animasi Manny berjalan (screenshot 2 frame berbeda), bounds sesuai kartu (100 / 2700 / 4500 cm), 8 socket ada, cek sandbox LULUS. Cek di level dengan Lumen: seam normal map, bayangan terpanggang.
- **GATE:** developer membuka `Test_Hermes_Tuyul` dan menilai rasa skala dan tampilan.

### K7 — Laporan akhir & serah terima
Laporan lengkap (template AGENTS.md §8) + tabel K0–K6 + semua `banding.md` + daftar gambar. "Usulan perubahan di luar sandbox": impor ke skeleton proyek (`SKEL_Tuyul` + `RTG_Mannequin_To_Tuyul`), `BP_Tuyul` (Character) dan `BP_TuyulRaksasa`/`BP_TuyulBesar` (`AJDGiantCharacter`), material parameter (`GlowIntensity`, `RealPulse`), Physics Asset, kawanan mulai LOD1, cara kembali. **Tidak dikerjakan sendiri.** `hermes_cek_sandbox.py` LULUS → push `hermes/tuyul`. Claude yang me-review dan memindahkan.

---

## 5. Kesalahan yang sudah pernah terjadi (jangan diulang)

Sama dengan `aksa_hermes.md` §4 (impor ke `SK_Mannequin`, bekerja di luar worktree, ketiak bolong, klaim tanpa angka, skrip dengan path tetap, mengubah tulang). Tambahan khusus model ini:

| Kesalahan | Pencegahan |
|---|---|
| Memotong badan Tuyul jadi potongan kaku seperti Jerangkong | Tuyul di-skin lunak; hanya Jerangkong yang memakai pola potongan |
| Mengarang geometri kelopak/bibir yang tidak ada | K0 mencatat; mata/mulut yang hanya dilukis → GATE |
| Memakai skala actor di UE untuk ukuran boss | Tiga FBX ter-bake (K5) |
| Merah basah di kulit terbaca darah | Kulit netral; merah hanya `T_Tuyul_Emit` |
