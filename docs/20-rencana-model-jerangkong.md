# 20 — Rencana Implementasi: Model Jerangkong (Boss Ep 1 + Minion Kerangka)

> **Status: v0.2 (12 Okt 2026).** Iterasi 0 selesai; **jalur B (model Tripo developer) disetujui dan dikerjakan sampai integrasi UE** (lihat [Jalur B](#jalur-b--basis-model-developer-tripo-ai-12-okt-2026)). Lisensi Tripo dikonfirmasi developer (komersial); material 1 slot + mask disetujui.
> Mengikuti pola [13](13-rencana-model-jayadwara.md) dan [19](19-rencana-model-aksa.md), memakai ulang pipeline `Art/Scripts/` (validator, render pembanding, LOD, kontrak export yang sudah diperbaiki di Iterasi 6 Jayadwara).
> Konsep: [`jerangkong_v01.webp`](concept-art/jerangkong_v01.webp) · Prompt: [`Art/Reference/prompt_jerangkong.md`](../Art/Reference/prompt_jerangkong.md) · Peran di game: [05](05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110), [16](16-panduan-arc-1.md#26-aturan-skala), [17](17-skenario-arc-1.md#adegan-7--jayadwara-vs-jerangkong--main), [18](18-kebutuhan-episode-1.md#b1-model).

## 1. Tujuan & definisi "siap dipakai di UE"

**Satu model, dua musuh:** boss Jerangkong (±31 m, 0,7× Jayadwara) dan minion kerangka kecil (skala manusia) memakai mesh & rig yang sama.

- [ ] Skeletal mesh `SK_Jerangkong` (LOD0–LOD3), tulang sebagai **potongan kaku** (tanpa skinning badan).
- [ ] **17 potongan**; **14** yang bisa terlepas juga diekspor sebagai static mesh `SM_Jerangkong_<Bagian>` dengan pivot di sendi tulangnya, untuk mekanik rontok & susun ulang (bagian 6.2).
- [ ] Skeleton bernama Mannequin + IK Retargeter, sehingga animasi Mannequin/Mixamo bisa dipakai sebagai dasar.
- [ ] Material 4 slot, energi Kala **emissive** (bukan merah basah).
- [ ] Socket titik lemah tengkorak, hit, dan VFX.
- [ ] Lulus validasi otomatis, uji pose, checklist rating & IP (bagian 8).
- [ ] Terpasang di UE: boss di `Test_GiantScale` (di samping Jayadwara), minion di `Test_Greybox`.

## 2. Titik awal & keputusan dari review konsep (12 Okt 2026)

| Dari konsep | Keputusan untuk model |
|---|---|
| Siluet bungkuk, lengan lewat lutut, tengkorak besar, retak merah di dahi | **Dipertahankan**: ini identitas & penanda titik lemah |
| Skala di chart ±0,85× hero | **0,7×** sesuai [16](16-panduan-arc-1.md#26-aturan-skala), supaya Ep 20 tetap "raksasa setara pertama" |
| View depan tegak, view samping kepala menggantung jauh ke depan | **Bungkuk sedang**: jelas bungkuk, tapi tengkorak tetap terjangkau pukulan Jayadwara (fase 2) |
| Anatomi & tekstur tulang condong realistis | **Disederhanakan** jadi bentuk tulang tebal yang tegas; retak, lumut, tanah dipindah ke tekstur (stylized semi-realistis) |
| Rusuk satu per satu | **Pelat rusuk** (2–3 lapis per sisi): hemat poligon dan jadi potongan yang enak untuk rontok |
| Energi merah di sendi & tulang belakang | **Emissive** menyala, tidak boleh terbaca sebagai darah/daging |
| Kain batik lusuh, gelang perunggu berpatina, pecahan batu di tengkorak | Dipertahankan (lore bangsawan kuno yang tersegel) |
| Kaki menggumpal tanah | Dipertahankan: membuat raksasa terasa "menapak" |

## 3. Keputusan Teknis (dengan default yang direkomendasikan)

| # | Keputusan | Default | Alasan |
|---|---|---|---|
| **J1** | Skeleton | **Skeleton sendiri bernama Mannequin + `IK_Jerangkong` + `RTG_Mannequin_To_Jerangkong`** | Proporsinya sengaja aneh (bungkuk, lengan panjang), jadi tidak boleh dipaksa memakai skeleton Manny asli (beda dengan Aksa). Pola ini sudah terbukti di Jayadwara |
| **J2** | Tinggi model di Blender | **±2,2 m** (berdiri), skala di UE lewat komponen seperti `AJDGiantCharacter` | Boss ≈ ×14 (31 m), minion ≈ ×0,85 (±1,9 m). Satu aset untuk dua ukuran |
| **J3** | Mekanik rontok & susun ulang | **SK + static mesh per potongan**: saat rontok, tulang di SK disembunyikan dan `SM_` dengan fisika dimunculkan di transform tulangnya; saat susun ulang, `SM_` ditarik kembali lalu tulang SK dimunculkan lagi | Paling terkontrol dan murah. Fallback: ragdoll Physics Asset + animasi bangkit |
| **J4** | Energi Kala | **Mesh inti emissive** (sendi, tulang belakang, rongga mata, retak tengkorak) + Niagara untuk kepulan halus nanti | Mesh memberi bentuk yang selalu terlihat; Niagara cukup sebagai tambahan (Fase 2) |
| **J5** | Kain batik | Rantai tulang depan/belakang (±3 tulang) + Anim Dynamics | Sama dengan kain Jayadwara |
| **J6** | Rahang | Tulang tambahan `jaw` (daun di bawah `head`) | Untuk raungan fase 2; tidak mengganggu retarget |
| **J7** | Anggaran poligon | LOD0 ≤ **35k** · LOD1 ≤ 15k · LOD2 ≤ 6k · LOD3 ≤ 2,5k | Lebih ringan dari Jayadwara. Minion (sampai 6 sekaligus) dipaksa mulai dari LOD1 |
| **J8** | Variasi minion | **Model sama**, tanpa gelang perunggu (disembunyikan per material/section) + skala lebih kecil | Pemain bisa membedakan minion dari boss; tidak ada model kedua |

## 4. Prinsip Desain Model

- **Tengkorak adalah bintang:** bagian dengan detail tertinggi, karena itu titik lemah, close-up cutscene, dan target pukulan. Retaknya harus terbaca dari kamera raksasa.
- **Tebal, bukan kurus:** di skala 31 m tulang tipis hilang di layar. Semua tulang dibuat lebih tebal dari anatomi asli.
- **Potongan = unit gameplay:** setiap potongan harus terbaca sebagai "satu tulang" saat rontok dan menggelinding.
- **Seram, bukan menjijikkan:** tanpa daging, darah, organ (target rating remaja).

### Daftar potongan & anggaran poligon LOD0

| # | Potongan | Tulang | Rontok? | Anggaran |
|---|---|---|---|---|
| 1 | Tengkorak (+ pecahan batu, retak, rongga mata) | `head` | Fase 2 saja (titik lemah) | 6k |
| 2 | Rahang | `jaw` | Tidak | 1k |
| 3 | Pelat rusuk (kiri+kanan+tulang dada) | `spine_03`–`spine_05` | Ya | 5k |
| 4 | Ruas tulang belakang + leher | `spine_01`–`neck_02` | Tidak (poros susun ulang) | 3k |
| 5 | Panggul + kain batik | `pelvis` (+ rantai kain) | Tidak | 4k |
| 6–7 | Lengan atas L/R (+ gelang) | `upperarm_l/r` | Ya | 2k |
| 8–9 | Lengan bawah L/R (+ gelang) | `lowerarm_l/r` | Ya | 2k |
| 10–11 | Tangan L/R (jari panjang) | `hand_l/r` + jari | Ya | 4k |
| 12–13 | Paha L/R | `thigh_l/r` | Ya | 2k |
| 14–15 | Betis L/R | `calf_l/r` | Ya | 2k |
| 16–17 | Kaki L/R (gumpalan tanah) | `foot_l/r`, `ball_l/r` | Ya | 2k |
| — | Inti energi Kala (sendi, tulang belakang, mata, retak) | ikut tulangnya | — | 2k |
| **Total** | | | | **±35k** |

*(17 potongan total. **14 bisa terlepas** dan punya `SM_`: 1, 3, 6–17. Tengkorak hanya terlepas saat fase 2/kalah; rahang, tulang belakang, dan panggul tetap menempel sebagai poros susun ulang.)*

## 5. Pembagian Kerja

| Claude (skrip Blender & UE) | Developer |
|---|---|
| Reference plane, model sheet (bagian 9), keputusan konsep | Menyetujui J1–J9 |
| Modeling semua potongan lewat skrip, rig, uji pose, validator | Review per kelompok, terutama tengkorak |
| UV, tekstur dasar (tulang, tanah, lumut, batik, perunggu), material preview | Hand-paint opsional (noda tanah, lumut) |
| LOD, export SK + 14 SM, import UE, retarget, uji di level | Menilai seram/lucunya, rasa skala di samping Jayadwara |
| C++ rontok & susun ulang (`AJDBoss_Jerangkong`, Fase 1) | Tuning gerakan & timing di editor |

## 6. Spesifikasi Teknis Aset

### 6.1 Skeleton
Hierarki & nama Mannequin (tanpa twist bone; tulang kaku tidak butuh) + `jaw` + `cloth_front_01..03`, `cloth_back_01..03`. Jari 3 ruas × 5 per tangan (jari panjang, nama Mannequin). Root di tanah, menghadap +Y (sama dengan kontrak Jayadwara).

### 6.2 Static mesh per potongan (untuk J3)
- `SM_Jerangkong_<Bagian>` untuk 14 potongan yang bisa terlepas, diekspor dari geometri yang sama dengan LOD1 (lebih ringan saat jatuh dengan fisika).
- **Pivot = posisi kepala tulang** di rest pose, orientasi = orientasi tulang, sehingga C++ cukup menyalin transform tulang ke actor potongan.
- Collision sederhana (kapsul/kotak) dibuat di skrip import.
- Daftar pemetaan tulang → potongan disimpan di `SK_Jerangkong_parts.json` (dibaca skrip import dan dipakai sebagai referensi C++).

### 6.3 Socket (lewat `SK_Jerangkong_sockets.json`)
`skull_weakpoint` (penanda HUD & target lock fase 2), `hand_l_hit`, `hand_r_hit`, `foot_l_hit`, `foot_r_hit`, `mouth_fx` (raungan), `chest_core` (sumber energi Kala), `throw_r` (lempar puing/tulang).

### 6.4 Material (4 slot)
| Slot | Isi | Tekstur | Parameter UE |
|---|---|---|---|
| `MI_Jerangkong_Bone` | Semua tulang, tanah, lumut, pecahan batu | Tile tulang + mask (tanah/lumut/retak), N, ORM; 2048² | Warna tulang, jumlah tanah/lumut |
| `MI_Jerangkong_Cloth` | Kain batik lusuh | BC (batik motif umum), N, ORM; 1024² | — |
| `MI_Jerangkong_Ornament` | Gelang perunggu berpatina | BC, ORM; 512² | Visibilitas (minion = sembunyi, J8) |
| `MI_Jerangkong_KalaGlow` | Inti energi, mata, retak tengkorak | Emissive datar | `GlowIntensity`, `WeakPointPulse` (retak berdenyut saat kelemahan aktif) |

### 6.5 Kontrak export & validasi
- Export sama dengan kontrak Jayadwara pasca-Iterasi 6 ([13](13-rencana-model-jayadwara.md#iterasi-6--integrasi-unreal)): armature bernama `Armature`, data cm & skala di-apply, `FBX_SCALE_ALL`, tanpa empty, tanpa animasi, LOD sebagai file terpisah. Tambahan: 14 file `SM_Jerangkong_*.fbx`.
- Validator memakai `validate_character.py` (generalisasi dari [19](19-rencana-model-aksa.md#65-validasi-otomatis)) dengan profil Jerangkong: setiap vertex **tepat 1 tulang dengan bobot 1,0** (potongan kaku), jumlah potongan = 17 (14 punya `SM_`), pivot `SM_` cocok dengan kepala tulang (toleransi 1 mm), tepat 4 slot material, batas tris per LOD.

## 7. Iterasi

> Estimasi jam **kasar**. Jadwal mengikuti roadmap: proxy untuk boss greybox **Fase 1 (Mar 2027)**, versi hero untuk **Fase 2** (pengadaan Apr–Mei 2027, boss final Agu–Sep 2027).

| Iter | Nama | Estimasi | Kapan (roadmap) |
|---|---|---|---|
| 0 | Design lock & model sheet | 3–4 jam | Fase 1, awal Mar 2027 |
| 1 | Proxy + rig + potongan | 6–8 jam | Fase 1, Mar 2027 |
| 2 | Hero modeling | 12–16 jam | Fase 2, Apr–Mei 2027 |
| 3 | Rig final & uji pose | 5–6 jam | Fase 2 |
| 4 | UV, tekstur & material | 8–10 jam | Fase 2 |
| 5 | LOD, export & integrasi UE | 5–6 jam | Fase 2 |

**Total ±40–50 jam**, kira-kira setengah dari Jayadwara/Aksa karena tidak ada skinning badan.

### Iterasi 0 — Design lock & model sheet
- **Claude:** normalisasi depan/samping/belakang dari `jerangkong_v01.webp` jadi reference plane (`make_reference_planes.py`, 1000 px = 2,2 m) dengan **postur bungkuk sedang** sebagai acuan (view samping konsep dikoreksi); isi bagian 9 (proporsi, palet hex, ukuran potongan); scene `Art/Blender/jerangkong_v00_setup.blend`.
- **Developer:** menyetujui model sheet & J1–J9.
- **Gate:** reference plane sejajar; model sheet disetujui.

**Status (12 Okt 2026): selesai dari sisi Claude, menunggu persetujuan developer.** Atas permintaan "siapkan untuk modeling jerangkong" (dibaca sebagai J9 = mulai sekarang, jalur art paralel). Artefak: `Art/Reference/jk_*.png` (`make_reference_planes_jerangkong.py`), scene `Art/Blender/jerangkong_v00_setup.blend` (`jerangkong_00_setup_scene.py`; plane dicek sejajar lewat render ortografis), model sheet [24](24-model-sheet-jerangkong.md). Temuan: tampak samping konsep bungkuk berlebihan (tengkorak 0,43 m di depan pergelangan kaki) → target bungkuk sedang ditandai `JK_TGT_*` di scene (S2), dan pose rest diusulkan sudah bungkuk agar retarget otomatis bungkuk (S3).

### Jalur B — basis model developer (Tripo AI), 12 Okt 2026

Developer membuat model awal dengan Tripo AI dari konsep: `Art/Source/jerangkong_tripo_v01.glb` (asli: `yahya_design/rKHD3GD0eELe7BHA74wR.glb`). Diimpor oleh `Art/Scripts/jerangkong_01_import_tripo.py` → `Art/Blender/jerangkong_v01_tripo.blend` (objek `JK_Source`, menghadap -Y, puncak tengkorak 2,19 m, vertex jahitan UV digabung).

| Temuan | Nilai | Akibat |
|---|---|---|
| Struktur | 1 mesh, 38,5k tris, 19k vertex, tanpa rig/animasi, 1 material (BC/N/ORM 2048²) | LOD0 sedikit di atas anggaran 35k → decimate ringan |
| Siluet depan vs konsep | IoU 0,86 | Proporsi sudah sesuai model sheet |
| Postur samping | Lebih tegak dari konsep, lengan menggantung lurus | Sudah mendekati bungkuk sedang (S2) |
| Geometri | Lunak/membulat; retak, gigi, rongga mata sebagian besar dari tekstur; jari sebagian menempel; 13k tepi non-manifold | Cukup untuk kamera raksasa; tengkorak perlu dipertegas untuk close-up |
| Tekstur | Warna mirip konsep, tapi ada noda merah di permukaan tulang bahu/selangka | Melanggar S11 → dibersihkan di tekstur |

**Keputusan (disetujui developer 12 Okt 2026):** Jalur B menggantikan modeling dari primitif. Lisensi Tripo akun developer mengizinkan pemakaian komersial (dikonfirmasi developer). **Catatan rilis:** Steam mewajibkan pengungkapan konten buatan AI di formulir rilis. Rencana semula: Iterasi 1 menjadi: rig dipasang ke mesh ini → mesh dipotong jadi 17 potongan (bobot kaku 1 tulang, ujung potongan ditutup) → 14 `SM_` → export & uji di UE. Iterasi 2 menyempit menjadi perbaikan: tengkorak (retak bergeometri, rongga mata & rahang dipertegas), pemisahan rahang, pembersihan merah S11. Material: 1 material dasar (tekstur Tripo) + mask emissive Kala, menggantikan 4 slot (6.4) kecuali developer memilih tetap 4 slot. **Syarat:** lisensi Tripo untuk akun yang dipakai mengizinkan pemakaian komersial (dicek developer).

#### Hasil jalur B (12 Okt 2026): Iterasi 1, 3, 4, 5 selesai dari sisi Claude; Iterasi 2 dipangkas

Pipeline (semua headless, bisa diulang; urutan & perintah di `Art/README.md`):

| Langkah | Skrip | Hasil |
|---|---|---|
| Impor & normalisasi | `jerangkong_01_import_tripo.py` | `jerangkong_v01_tripo.blend` (`JK_Source`) |
| Rig + potongan | `jk_skeleton.py` (sendi diukur dari mesh), `jk_segment.py`, `jerangkong_10_build.py` | `jerangkong_v02_rig.blend`: `JK_Armature` 70 tulang, 17 objek `JK_P_*`, 8 `SOCKET_*`; LOD0 33.984 tris |
| Tekstur | `make_textures_jerangkong.py` | `Art/Export/Textures_Jerangkong/T_Jerangkong_{BC,N,ORM,Emit}` |
| Material & uji pose | `jerangkong_12_materials.py`, `jerangkong_13_pose_tests.py` | `M_Jerangkong`; 7 pose → `Art/Export/_jerangkong_pose_tests.png` |
| Export | `jerangkong_14_export.py` | `SK_Jerangkong(_LOD1..3).fbx`, `SK_Kerangka(_LOD1..3).fbx`, `Jerangkong_Parts/SM_Jerangkong_*.fbx` (14), `SK_Jerangkong_parts.json`, `*_sockets.json` |
| Validasi | `validate_jerangkong.py` | Boss LOD0 **21/21** (termasuk pivot 14 SM, terburuk 2,3%); 7 FBX lain **18/18** |
| UE | `Tools/ue_import_jerangkong.py`, `Tools/ue_setup_jerangkong.py`, `Tools/ue_capture_jerangkong.py` | Daftar aset di bawah; bukti visual `Art/Export/_jerangkong_ue_cek.png` |

LOD (tris): 33.984 / 14.881 / 5.923 / 2.507 (anggaran J7 terpenuhi); tengkorak dilindungi (rasio ×1,6) di LOD1–3.

Keputusan teknis yang berubah dari rencana awal:

| Topik | Rencana | Jalur B | Alasan |
|---|---|---|---|
| Segmentasi | Model per potongan | Mesh Tripo dipotong otomatis: kapsul tulang terdekat + aturan wilayah (tengkorak/rahang, rusuk, kain) + bidang potong di sendi; lubang potongan ditutup (UV cap ke kotak tulang gelap 8 px di pojok atlas) | Mesh Tripo satu badan |
| Potongan multi-tulang | 1 tulang | `Ribs` = rusuk + selangka/belikat (S5), `Spine` = lumbar + leher, `Pelvis` = panggul + kain; batas antar-tulang di dalamnya berbobot campuran. Potongan yang bisa rontok tetap 1 tulang bobot 1,0 | Bahu & kain harus ikut animasi |
| Jari | 3 ruas ter-rig | Tulang jari ada (untuk retarget), tetapi geometri jari kaku ikut `hand_*` | Jari Tripo menempel; tidak terbaca di skala 31 m |
| Rahang | Model terpisah | Batang mandibula dipotong dari tengkorak (gigi atas ikut tengkorak) | |
| Material (6.4) | 4 slot | **1 slot** `M_Jerangkong_Master` + `T_Jerangkong_Emit`: R = energi Kala, G = retak titik lemah (`WeakPointPulse` + denyut), B = gelang (`OrnamentHide`, minion J8) | Atlas Tripo tunggal |
| Merah Kala (S11) | | Pendar hanya di zona konsep (isi rusuk, tulang belakang, leher, bahu, ±9 cm sendi, mata, retak); merah di kain/batang tulang dinetralkan ke warna tulang. `GlowIntensity` 2,5 (boss) / 2,0 (minion); nilai 8 terbukti membuat seluruh badan terbaca merah | Uji UE 12 Okt |
| Skala (J2) | 1 aset diskalakan di UE | **2 aset dari 1 model**: `SK_Jerangkong` (×14, 30,66 m) & `SK_Kerangka` (×0,85, 1,86 m, MinLOD 1), skeleton masing-masing | Skala harus di-bake (Anim Dynamics, docs/13 Iterasi 6b) |
| SM (6.2) | Orientasi = tulang | Pivot = kepala tulang pivot, orientasi **identitas** (sumbu komponen), skala boss. Saat rontok: SM = Translation(pivot), lalu inverse(BoneRef), lalu BoneNow (urutan komposisi UE); minion: skala aktor 0,85/14 | Sama persis dengan skinning kaku, jadi cocok di pose apa pun. Diuji di UE: pivot dunia = sendi (selisih 0,00 cm), lengan SM menggantikan tulang tersembunyi tanpa loncatan |
| Retarget | Auto-align semua | Hanya lengan (`clavicle..hand`) disejajarkan ke A-pose Manny; tulang belakang/leher/kaki memakai pose rest, jadi animasi Manny tetap bungkuk & kuda-kuda lebar. "Run IK Rig" dimatikan (FK murni, sama dengan Jayadwara) | S3 |

Aset UE (`/Game/Jayadwara/Characters/Jerangkong/`): `Textures/` 4 tekstur; `Materials/` master + `MI_Jerangkong`, `MI_Kerangka`; `Mesh/` `SK_`/`SKEL_`/`PA_` Jerangkong & Kerangka (4 LOD, 8 socket, PA 20 kapsul); `Parts/` 14 `SM_Jerangkong_*` (collision kapsul); `Rig/` `IK_` & `RTG_Mannequin_To_` tiap varian; `Anims_Jerangkong/`, `Anims_Kerangka/` (25 aset: `ABP_<varian>` dari ABP_Unarmed tanpa foot IK Control Rig; Anim Dynamics kain depan/belakang hanya di boss, BlendSpace boss ×√14, 3 serangan); `BP_Jerangkong` (AJDGiantCharacter: tinggi 3066 cm, kapsul 45×109,5 cm ×14) & `BP_Kerangka` (Character, kapsul 34×93). Level: `JK_Boss_01` di `Test_GiantScale` (±41 m depan-kiri PlayerStart, menghadap pemain), `JK_Minion_01..03` di `Test_Greybox`. **12 Okt 2026: aktor ini dihapus dari kedua level** (berat di laptop developer); `Tools/ue_setup_jerangkong.py` sekarang `PLACE_IN_LEVELS = False` dan hanya menaruhnya kalau diubah ke `True`. Minion/boss masuk level lagi di F1 Iterasi 5 & 8 ([23](23-rencana-fase-1.md)).

**Belum / sisa:**
- Retak tengkorak & rongga mata masih dari tekstur (Iterasi 2 "tengkorak bergeometri" belum dikerjakan); cukup untuk kamera raksasa, perlu dipertegas kalau ada close-up cutscene.
- Uji PIE (developer, 12 Okt 2026): boss & minion tampil benar (menapak, bungkuk, pendar sesuai zona). Kain minion melar & bergetar cepat (Anim Dynamics skala manusia, sama dengan selendang Aksa) → **kain minion dibuat kaku** (`cloth_dynamics` di `ue_setup_jerangkong.py`); kain boss tetap disimulasikan. Uji FPS 1 boss + 6 minion belum.
- SM `Ribs` membawa selangka/belikat dalam relasi rest terhadap `spine_04`; kalau bahu sedang terangkat saat rusuk rontok, bagian bahu bisa bergeser sedikit.
- Kode rontok/susun ulang (`AJDBoss_Jerangkong`, C++ Fase 1), animasi kustom (raungan dengan `jaw`, merayap, susun ulang), dan foot IK raksasa belum.
- Capture editor (`ue_capture_jerangkong.py`) kadang menangkap pose rest karena editor tidak men-tick animasi saat jendelanya tidak aktif.

### Iterasi 1 — Proxy + rig + potongan
**Tujuan:** proxy ringan yang langsung dipakai boss greybox Fase 1 dan untuk membuktikan mekanik rontok/susun ulang.
- **Claude:** 17 potongan dari primitif (silinder/kapsul/kotak berbevel), tengkorak dari bentuk dasar + retak sebagai inset; skeleton + parent kaku; 5 uji pose (idle bungkuk, sapuan, hantaman, lempar, roboh); export SK + 14 SM + `parts.json`; validator; import UE, retarget 3 animasi Mannequin, tampilkan di `Test_GiantScale` pada 31 m di samping Jayadwara dan di `Test_Greybox` pada skala minion.
- **Developer:** menilai siluet & skala di game.
- **Gate:** siluet cocok dengan konsep dari kamera raksasa; retarget tidak terpelintir; pivot `SM_` cocok (dibuktikan dengan satu uji: sembunyikan tulang lengan, munculkan `SM_` di tempat yang sama tanpa loncatan posisi).

### Iterasi 2 — Hero modeling
- **Claude:** per kelompok dengan review sebelum lanjut: **tengkorak** (rahang, rongga mata, alis tulang, retak berkedalaman, pecahan batu, akar) → pelat rusuk & tulang belakang → panggul & kain batik → lengan & tangan jari panjang (gelang perunggu) → kaki & gumpalan tanah → inti energi Kala. Render ortografis + close-up tengkorak 3/4 berdampingan dengan konsep (`render_compare.py`).
- **Developer:** review tiap kelompok.
- **Gate:** berdampingan dengan konsep terasa "Jerangkong yang sama"; tidak ada bagian yang terbaca sebagai daging.

### Iterasi 3 — Rig final & uji pose
- **Claude:** jari panjang, `jaw`, rantai kain; 10 uji pose (5 Iterasi 1 + raungan, lempar puing, merayap/susun ulang, terhuyung, roboh); cek tumpang-tindih antar-potongan (`06_deform_check.py` mode kaku).
- **Gate:** tidak ada potongan menembus potongan lain secara mencolok di 10 pose; retarget animasi Mannequin tetap rapi dengan postur bungkuk.

### Iterasi 4 — UV, tekstur & material
- **Claude:** UV terskrip; tekstur tulang tileable + mask tanah/lumut/retak; batik motif umum di kain (**hindari batik larangan**, [06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)); perunggu berpatina; material preview yang meniru parameter UE (`GlowIntensity`, `WeakPointPulse`).
- **Developer:** hand-paint opsional.
- **Gate:** dari kamera raksasa tulang terbaca tua & bertanah; energi merah jelas menyala, bukan basah.

### Iterasi 5 — LOD, export & integrasi UE
- **Claude:** LOD1–3 (lindungi tengkorak & inti energi); export final; skrip import (generalisasi `ue_import_jayadwara.py`) untuk SK, 14 SM + collision, 4 MI, socket, `parts.json`; `BP_Jerangkong` (boss) & `BP_Kerangka` (minion, ornamen disembunyikan); Physics Asset (fallback J3); Anim Dynamics kain.
- **Developer:** uji di level, cek FPS dengan 1 boss + 6 minion.
- **Gate:** boss & minion tampil benar di dua skala; potongan bisa dimunculkan di posisi tulangnya; 60 FPS.

## 8. Checklist Rating, Budaya & IP (dipakai di setiap gate)

- [ ] **Tanpa gore:** tidak ada daging, darah, organ, otot. Energi merah selalu emissive.
- [ ] Seram tapi terbaca (rating remaja, [09](09-product-brief.md#target-pemain)).
- [ ] Batik motif umum, bukan batik larangan; Jerangkong termasuk makhluk "aman" diadaptasi ([06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)).
- [ ] Energi Kala merah gelap (konsisten dengan sisi Kala), tanpa biru/silver.
- [ ] Tidak meniru desain monster kerangka dari IP lain secara spesifik.

## 9. Model Sheet

Diisi di Iterasi 0 sebagai dokumen terpisah: **[24-model-sheet-jerangkong.md](24-model-sheet-jerangkong.md)** (proporsi terukur, postur bungkuk sedang, palet, ukuran potongan, keputusan desain S1–S12).

## 10. Risiko

| Risiko | Mitigasi |
|---|---|
| Mekanik rontok/susun ulang rumit di C++ | Spesifikasi pivot & `parts.json` sejak Iterasi 1; uji satu lengan di Iterasi 1; fallback ragdoll + animasi bangkit (J3) |
| Animasi Mannequin terlihat terlalu tegak untuk postur bungkuk | Atur pose retarget di `RTG_` + lapisan aditif bungkuk di ABP; animasi khusus (raungan, merayap) dibuat kustom |
| Tulang tipis tidak terbaca di skala 31 m | Prinsip "tebal, bukan kurus"; cek dari kamera raksasa sejak proxy |
| Performa 6 minion + boss + potongan fisika | Minion mulai dari LOD1; batasi potongan aktif; puing tulang dihapus bertahap |
| Terbaca menjijikkan / terlalu seram | Gate visual tiap iterasi; energi emissive; warna tulang hangat, bukan kemerahan |

## 11. Keputusan untuk Developer

| # | Pertanyaan | Usulan Claude |
|---|---|---|
| **J1** | Skeleton sendiri + retargeter (bukan Manny asli)? | **Ya** |
| **J2** | Model 2,2 m, diskalakan di UE untuk boss & minion? | **Ya** |
| **J3** | Rontok = SK + static mesh per potongan? | **Ya**; fallback ragdoll |
| **J4–J8** | Energi mesh emissive, kain rantai tulang, tulang rahang, anggaran 35k, minion model sama tanpa gelang | **Ya** (default bagian 3) |
| **J9** | Jadwal: ikut roadmap (Iterasi 0–1 Mar 2027, sisanya Fase 2) atau lebih awal? | **Ikut roadmap**; boss greybox Fase 1 cukup dengan proxy |
