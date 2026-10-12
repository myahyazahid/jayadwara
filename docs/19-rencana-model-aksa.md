# 19 — Rencana Implementasi: Model Aksa (Wujud Manusia)

> **Status: USULAN v0.4 (12 Okt 2026)**, menunggu persetujuan developer. **Iterasi 6 putaran 1 selesai** (LOD0–3, `BP_Aksa` memakai `SK_Aksa`, Anim Dynamics jaket, potret dialog). **Iterasi 5 putaran 1 selesai** (UV, tekstur dasar, material). **Iterasi 4 putaran 1 selesai** (rig final + 8 morph target). **Iterasi 3 putaran 1 selesai** (pakaian hero + tangan). **Iterasi 2 putaran 3 selesai** (kepala MPFB; rambut, alis, mata mengikuti referensi gaya dari developer; menunggu feedback). **Iterasi 0 selesai dari sisi Claude** (spike lulus → jalur (a), skeleton Manny asli) dan **Iterasi 1 selesai dari sisi Claude** (proxy ter-skin, FBX lolos validator 17/17, terimpor ke `SK_Mannequin`, animasi Mannequin jalan); lihat bagian 7. Menunggu review developer: model sheet ([21](21-model-sheet-aksa.md)), A1–A9, proporsi proxy. Permintaan "persiapan modeling Aksa" (12 Okt 2026) dibaca sebagai **A9 = mulai sekarang** sebagai jalur art paralel; roadmap ([10](10-roadmap.md)) belum diubah.
> Mengikuti pola [13-rencana-model-jayadwara.md](13-rencana-model-jayadwara.md) dan memakai ulang pipeline-nya (`Art/Scripts/`, validator, skrip import UE). Bagian yang berbeda dari Jayadwara ditulis eksplisit.
> Keputusan dasar (12 Okt 2026): model Aksa **dibuat sendiri** di Blender (Claude + developer); **MetaHuman** dipakai sebagai placeholder visual sampai model ini jadi ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)).

## 1. Tujuan & definisi "siap dipakai di UE"

`SK_Aksa` menggantikan komponen MetaHuman di `BP_Aksa` **tanpa mengubah logika, animasi, atau kode** ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)).

- [ ] Skeletal mesh `SK_Aksa` (LOD0–LOD3) yang memakai **skeleton Mannequin UE5** (lihat keputusan A1) dan bisa memutar animasi Mannequin/Mixamo yang sama dengan Manny.
- [ ] Wajah, rambut, dan pakaian sesuai [`aksa_turnaround_v01.webp`](concept-art/aksa_turnaround_v01.webp) dan [`Aksa versi Final.png`](concept-art/Aksa%20versi%20Final.png), **tanpa** alat transformasi di lengan ([03](03-karakter.md#aksa-jaya-mangkubumi-aksa)).
- [ ] Material & tekstur (5 slot, bagian 6.3).
- [ ] Rantai tulang tambahan untuk selendang & ujung jaket (Anim Dynamics).
- [ ] Morph target ekspresi dasar (kedip, senyum, marah, mulut terbuka).
- [ ] Lulus validasi otomatis + uji pose silat + checklist IP & budaya (bagian 8).
- [ ] Terpasang di `BP_Aksa` menggantikan MetaHuman; animasi gameplay tetap jalan.

## 2. Titik awal (12 Okt 2026)

| Item | Status |
|---|---|
| Konsep | `Aksa versi Final.png` (pose dinamis, ada gauntlet yang dibuang) + `aksa_turnaround_v01.webp` (A-pose depan/samping/belakang + kepala depan/samping, tanpa gauntlet, dengan kalung) |
| Blender | 5.2.2 LTS + MCP; pipeline Jayadwara (`jd_common.py`, `jd_skeleton.py`, validator, render pembanding). MPFB2 **belum terpasang** (add-on aktif hanya bawaan: cycles, io_*) |
| Persiapan Iterasi 0 (12 Okt 2026) | `Art/Reference/ak_*.png` (3 reference plane + kepala + 8 detail + palet), `Art/Blender/aksa_v00_setup.blend` (19 landmark, penggaris 1,75 m), [21-model-sheet-aksa.md](21-model-sheet-aksa.md) |
| UE | Project jalan; `BP_Aksa` = `SKM_Manny_Simple` + `ABP_Unarmed`; `IK_Mannequin` sudah dibuat (`Tools/ue_setup_retarget.py`) |
| MetaHuman placeholder | Belum dibuat (developer) |

**Pelajaran dari Jayadwara yang langsung dipakai:**
1. **Ukur dari reference plane** sebelum menerjemahkan angka (kesalahan lebar kaki di Iterasi 1).
2. **Bandingkan render ortografis vs konsep** berdampingan, bukan hanya angka IoU (revisi besar Iterasi 2). Kepala dirender close-up 3/4.
3. **Kontrak export UE** yang sudah teruji di Iterasi 6: objek armature bernama `Armature`, data dalam cm dan skala di-apply, `FBX_SCALE_ALL`, tanpa empty `SOCKET_*` (socket lewat JSON).
4. **Lapisan luar harus pas di badan**, tanpa celah atau tonjolan ([armor fit](13-rencana-model-jayadwara.md#iterasi-2--hero-modeling-mid-poly)). Untuk Aksa: jaket, celana, dan sepatu terhadap badan.
5. **Metrik deformasi absolut** (perubahan panjang tepi dalam cm), bukan rasio.

## 3. Keputusan Teknis (dengan default yang direkomendasikan)

| # | Keputusan | Default yang direkomendasikan | Alasan |
|---|---|---|---|
| **A1** | Skeleton | **Terpilih: skeleton Mannequin UE5 asli** (spike lulus 12 Okt 2026, [Temuan](#temuan-iterasi-0-12-okt-2026)): `SKM_Manny` diekspor dari UE → dipakai sebagai armature di Blender → `SK_Aksa` diimpor ke `SKEL_Mannequin` yang sama | Semua animasi Manny/Mixamo-retarget langsung jalan tanpa retargeter. Aksa akan punya animasi terbanyak di game. Jayadwara memakai skeleton sendiri + IK Retargeter karena orientasi tulangnya beda; risiko itu diuji di **spike Iterasi 0**. Fallback: skeleton sendiri + retargeter seperti Jayadwara |
| **A2** | Basis badan & wajah | **MPFB2** (MakeHuman untuk Blender): mesh manusia dengan topologi bersih, lalu di-stylize lewat skrip agar mirip konsep | Wajah manusia dari primitif skrip cenderung kaku. **Hanya aset CC0** dari MPFB2 yang dipakai. Perlu developer menyetujui pemasangan ekstensinya |
| **A3** | Tinggi Aksa | **180,6 cm = tinggi Manny** (revisi dari 175 cm; konsep dikali 1,032) | Spike mengukur Manny 180,6 cm dan skala impor tidak bisa menyesuaikan tinggi di UE 5.6.1. Kapsul & kamera mengikuti Manny, jadi tidak ada selisih dengan mesh logika ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)) |
| **A4** | Ekspresi wajah | **Morph target saja** (±8: kedip L/R, senyum, marah, mulut terbuka, alis naik, meringis, mata lirik) | Skeleton Mannequin tidak punya tulang wajah; dialog vertical slice = teks + potret. Rig wajah penuh → Iterasi 7 |
| **A5** | Rambut | **Mesh gumpalan stylized** (seperti konsep), kaku ke `head` | Lebih ringan dan lebih cocok gaya game daripada groom/cards |
| **A6** | Kulit tertutup baju | **Dihapus** (hanya kepala, leher, lengan bawah, tangan yang tersisa) | Mencegah kulit tembus baju saat pose silat lebar; hemat poligon |
| **A7** | Kain | **Rantai tulang + Anim Dynamics** untuk selendang (±6 tulang) dan dua ujung depan jaket (±2 tulang); celana & badan jaket ter-skin biasa | Sama dengan selendang Jayadwara; tanpa simulasi kain Chaos (berat) |
| **A8** | Anggaran poligon | LOD0 ≤ **60k** · LOD1 ≤ 25k · LOD2 ≤ 10k · LOD3 ≤ 4k tris | Mode manusia sering dilihat dekat; tetap di bawah Jayadwara (≤100k) |

### Temuan Iterasi 0 (12 Okt 2026)

Dari membaca hasil Iterasi 6 Jayadwara ([13](13-rencana-model-jayadwara.md#iterasi-6--integrasi-unreal)) dan mengukur turnaround Aksa ([21](21-model-sheet-aksa.md)). Bagian ini **mengubah cara A1 dan A3 dibaca**; keputusan akhirnya dari spike.

1. **A1 dan A3 saling bertabrakan.** Skeleton Mannequin yang tidak diubah berarti tinggi Aksa = tinggi tulang Manny. **Tinggi Manny belum diukur** (spike langkah S1). Di UE 5.6.1, *Import Uniform Scale* masuk ke **skala tulang root**, bukan posisi tulang, dan animasi retarget yang mengunci skala root = 1 membatalkannya lagi (ditemukan di Iterasi 6 Jayadwara). Jadi 175 cm **tidak bisa dicapai lewat skala impor** kalau skeleton Manny dipertahankan.
2. **Dua jalur, spike memilih:**
   - **(a) Skeleton Manny asli.** Tinggi Aksa mengikuti Manny; animasi Manny/Mixamo langsung jalan; tanpa retargeter. Syarat: tinggi dan sudut A-pose Manny bisa diterima, dan round-trip Blender↔UE terbukti.
   - **(b) Skeleton sendiri bernama Mannequin pada 1,75 m + IK Retargeter** (jalur Jayadwara yang sudah jalan: `Tools/ue_setup_retarget.py` bisa dipakai ulang untuk `IK_Aksa` + `RTG_Mannequin_To_Aksa`). Cocok dengan arsitektur mesh logika vs visual ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)) yang memang menyalin pose dari Manny tersembunyi, jadi tidak ada animasi yang perlu di-retarget satu per satu.
   - **Rekomendasi Claude:** (a) kalau tinggi Manny dalam ±3% dari 175 cm, atau developer mau Aksa setinggi Manny; selain itu **(b)**. Kalau (b), langkah Iterasi 1 membuat `ak_skeleton.py` (analog `jd_skeleton.py`) dan `05_export_fbx.py` serta `validate_jayadwara.py` digeneralisasi.
3. **Spike Jayadwara tidak otomatis berlaku.** Di sana skeleton buatan sendiri gagal dipakai di Mannequin (orientasi tulang beda, root roll 90°). Untuk Aksa armature berasal dari ekspor Manny asli, jadi orientasi terjaga, tapi importer FBX Blender tidak selalu menjaga roll tulang. Karena itu spike menguji **round-trip penuh** (UE → Blender → UE), bukan hanya impor.
4. **Sudut A-pose.** Sheet ±22°, prompt 35°, Manny punya sudut sendiri ([21](21-model-sheet-aksa.md) D2). Mesh harus mengikuti pose rest skeleton; `aksa_spike_analyze_manny.py` mengukurnya.
5. **MPFB2.** Sumber unduhan dan lisensi aset (CC0) harus diverifikasi sebelum dipasang; belum ada di Blender. Kalau ditolak/gagal, badan dibuat dengan skrip seperti Jayadwara (lebih lama di Iterasi 2).
6. **Skrip yang masih khusus Jayadwara:** `05_export_fbx.py` (awalan `JD_`, `JD_Armature`) dan `validate_jayadwara.py`. Digeneralisasi di Iterasi 1 (`validate_character.py`), kontrak export (6.4) tidak berubah.

#### Hasil spike (12 Okt 2026) — jalur (a) dipilih

| Langkah | Hasil |
|---|---|
| S1 `Tools/ue_export_manny.py` | `SKM_Manny_Simple` setinggi **180,6 cm** (kotak batas, kaki di z=0). Skeleton aset = `/Game/Characters/Mannequins/Meshes/SK_Mannequin` (bukan `SKEL_Mannequin`; dipakai bersama Manny/Quinn, 161 tulang, mesh Manny Simple memakai 88) |
| S2 `aksa_spike_analyze_manny.py` | 88 tulang. Importer Blender menjadikan node `root` sebagai **objek** (data dalam cm di bawah empty berskala 0,01), 5 tulang akar: `pelvis`, `ik_foot_root`, `ik_hand_root`, `interaction`, `center_of_mass`. **Pose rest Manny:** lengan atas 35° dan lengan bawah 53° dari vertikal (tangan 16 cm di depan badan), pinggul ±0,100 m, lutut ±0,123 m, pergelangan ±0,141 m (stance sempit), panjang kaki 0,853 m, kiri = +X, menghadap -Y |
| S3 `aksa_spike_roundtrip.py` | Kontrak export dibuktikan: tulang `root` dibuat sungguhan (induk 5 tulang akar), objek armature bernama `Armature`, data x100 di-apply, `FBX_SCALE_ALL`. Tanpa data x100 yang benar, skala meledak 100x atau masuk ke tulang |
| S4 `ue_spike_aksa_import.py` + `aksa_spike_compare.py` | Impor ke `SK_Mannequin` **tidak membuat skeleton baru**. Mesh diekspor lagi dari UE: 88 tulang Manny identik (selisih ≤0,005 mm, 0,000°) |
| S5 | Animasi Mannequin (`MM_Attack_01`, `Walk_Fwd`, `MM_Idle`) dibekukan pada mesh Aksa dan Manny di editor: pose identik (`Tools/ue_check_aksa.py`) |

Konsekuensi: **tinggi 180,6 cm** (A3 revisi); **pose rest dan stance kaki mengikuti Manny**, bukan konsep ([21](21-model-sheet-aksa.md) D1/D2, koreksi di model, bukan di tulang); tulang tambahan (`sash_*`) ikut digabung ke `SK_Mannequin` (aset itu berubah di git; Manny/Quinn tidak terpengaruh).

## 4. Prinsip Desain Model

- **Stylized semi-realistis** seperti konsep: bentuk tegas, siluet terbaca dari jauh, detail kecil (jahitan, motif batik) di tekstur, bukan geometri.
- **Siluet kunci**: rambut berantakan ke atas, kerah tinggi berbatik, jaket pendek terbuka, selendang menjuntai di pinggang kiri, boots tebal.
- **Silat dulu**: setiap keputusan bentuk diuji di pose kuda-kuda lebar dan tendangan tinggi; celana dan jaket tidak boleh menghambat atau robek visual.
- **Ketidakkonsistenan referensi** diputuskan di model sheet (Iterasi 0), bukan ditebak saat modeling. Yang sudah diketahui: posisi selendang di view samping, senyum di wajah depan (model = netral), jumlah kantong celana antar-view.

### Daftar bagian & anggaran poligon LOD0

| Kelompok | Bagian | Deformasi | Tulang utama | Anggaran |
|---|---|---|---|---|
| Kepala | Kepala, telinga, mata (+ kornea), alis, gigi/lidah sederhana | Ter-skin + morph | `head`, `neck_*` | 12k |
| Rambut | Gumpalan rambut | Kaku | `head` | 6k |
| Badan terlihat | Leher, lengan bawah, tangan + jari | Ter-skin | lengan, tangan, jari | 6k |
| Atasan | Kaos hitam, jaket (kerah berbatik, lengan digulung, kantong, emblem punggung) | Ter-skin + rantai ujung jaket | tulang belakang, bahu, lengan | 14k |
| Bawahan | Celana kargo (kantong, strap paha), sabuk + gesper | Ter-skin | pinggul, paha, betis | 9k |
| Aksesori | Selendang batik, kalung + liontin, sarung tangan tanpa jari | Selendang: rantai; kalung: `spine_05`/`neck_01`; sarung tangan: ter-skin | — | 5k |
| Sepatu | Boots bertali, sol, trim emas | Ter-skin (pergelangan) + kaku | `foot`, `ball` | 6k |
| **Total** | | | | **±58k** |

## 5. Pembagian Kerja

| Claude (skrip Blender & UE, lewat MCP / `ue_remote.py`) | Developer |
|---|---|
| Reference plane, model sheet, ukuran proporsi | Menyetujui model sheet & keputusan A1–A8 |
| Spike skeleton Manny (export UE → Blender → UE) | Memasang ekstensi MPFB2 (setuju unduhan) |
| Membangun & men-stylize badan, kepala, rambut, pakaian lewat skrip | Review tiap kelompok; **wajah**: feedback paling banyak di sini |
| Rig, skinning, morph target, uji pose, validator | Perbaikan weight manual di titik rumit (bahu, pinggul) |
| UV, tekstur dasar, material preview, LOD, export | Hand-paint (kulit, lipatan, batik), cek warna |
| Import UE, ganti MetaHuman → `SK_Aksa`, Anim Dynamics, potret dialog | Main dan menilai di game |

## 6. Spesifikasi Teknis Aset

### 6.1 Skeleton
- **A1 (default):** armature = `SKM_Manny` hasil ekspor UE, **tidak diubah** posisi/orientasi tulangnya. Mesh Aksa di-fit ke armature itu (proporsi dikoreksi lewat mesh, bukan tulang). Tulang tambahan hanya **daun baru** di bawah tulang yang ada: `sash_01..06` (di bawah `pelvis`), `jacket_l/r_01..02` (di bawah `spine_03`). UE menggabungkan tulang daun baru ke `SKEL_Mannequin` saat import tanpa mengganggu animasi.
- Kalau spike gagal (fallback): skeleton sendiri bernama Mannequin + `IK_Aksa` + `RTG_Mannequin_To_Aksa`, persis seperti Jayadwara.

### 6.2 Socket (lewat `SK_Aksa_sockets.json`, bukan empty)
`hand_r_hit`, `hand_l_hit`, `foot_r_hit`, `foot_l_hit` (hit detection), `pendant` (VFX kalung saat transformasi), `head_fx`, `back_fx`.

### 6.3 Material (5 slot)
| Slot | Isi | Tekstur |
|---|---|---|
| `MI_Aksa_Skin` | Kulit kepala, leher, lengan, tangan | BC, N, ORM, (SSS mask) 2048² |
| `MI_Aksa_Eyes` | Iris, sklera, kornea | BC 512² |
| `MI_Aksa_Hair` | Rambut, alis | BC, N, ORM 1024² |
| `MI_Aksa_Cloth` | Jaket, kaos, celana, selendang, kerah batik | Mask zona, BC, N, ORM 2048² |
| `MI_Aksa_Gear` | Boots, sarung tangan, sabuk, gesper, kalung, emblem | BC, N, ORM 1024² |

Palet diambil dari konsep (hex di model sheet): navy jaket, hitam/charcoal kaos & celana, emas aksen (**sama dengan emas Jayadwara**, `jd_common.HEX`), coklat batik, kulit sawo matang. **Tanpa silver/chrome, tanpa biru menyala.**

### 6.4 Kontrak export FBX
Sama dengan kontrak Jayadwara yang sudah diperbaiki di Iterasi 6 ([13](13-rencana-model-jayadwara.md#iterasi-6--integrasi-unreal)): objek armature bernama `Armature`, data dalam cm dan skala di-apply, `FBX_SCALE_ALL`, tanpa empty, tanpa animasi, LOD sebagai file terpisah (`SK_Aksa.fbx`, `SK_Aksa_LOD1..3.fbx`), morph target ikut (`use_shape_keys`).

### 6.5 Validasi otomatis
`validate_jayadwara.py` digeneralisasi jadi `validate_character.py` (profil per karakter) + cek baru:
- nama, jumlah, dan hierarki tulang **sama persis dengan `SKM_Manny`** (kecuali tulang daun tambahan);
- morph target ada dan tidak menggeser vertex di luar kepala;
- tidak ada kulit di bawah baju (A6);
- batas tris per LOD (A8), ≤4 influence, bobot ternormalisasi, UV 0–1, tepat 5 slot material.

## 7. Iterasi

> Estimasi jam **kasar** (kapasitas ±10–15 jam/minggu). Direvisi di akhir Iterasi 1.

| Iter | Nama | Estimasi | Butuh UE? | Status |
|---|---|---|---|---|
| 0 | Design lock, fondasi & **spike skeleton** | 8–10 jam | Ya (spike) | **Selesai sisi Claude** (12 Okt 2026); gate: persetujuan developer |
| 1 | Badan dasar + proxy pakaian + rig | 10–12 jam | Ya (uji ganti MetaHuman) | **Selesai sisi Claude** (12 Okt 2026); gate: review proporsi developer |
| 2 | **Kepala & wajah** + rambut | 15–20 jam | Tidak | **Putaran 3 selesai** (MPFB + rambut/alis/mata gaya referensi, 12 Okt 2026); gate Go/No-Go: feedback developer |
| 3 | Pakaian hero | 20–25 jam | Tidak | **Putaran 1 selesai** (12 Okt 2026); feedback developer |
| 4 | Skinning final, rantai kain, morph target | 12–15 jam | Tidak | **Putaran 1 selesai** (12 Okt 2026); feedback developer |
| 5 | UV, tekstur & material | 15–20 jam | Tidak | Belum |
| 6 | LOD, export & integrasi UE | 10–12 jam | Ya | Belum |
| 7 | Polish & varian (opsional) | — | Ya | Opsional |

**Total Iter 0–6: ±90–115 jam ≈ 7–9 minggu** pada kapasitas penuh. Di roadmap, model Aksa dijadwalkan di pengadaan aset Fase 2 (Apr–Mei 2027, [10](10-roadmap.md#fase-2--vertical-slice-episode-1-gerbang-yang-retak-apr--des-2027)); kalau dikerjakan lebih awal sebagai jalur art paralel (seperti Jayadwara), tanggal Fase 0–1 ikut bergeser (keputusan A9).

### Iterasi 0 — Design lock, fondasi & spike skeleton
**Tujuan:** menghilangkan ambiguitas desain dan risiko teknis terbesar sebelum modeling.
- **Claude:**
  - [x] Normalisasi `aksa_turnaround_v01.webp` jadi reference plane depan/samping/belakang + kepala + 8 crop detail + palet (`Art/Scripts/make_reference_planes_aksa.py` → `Art/Reference/ak_*.png`; 1000 px = 1,75 m; landmark ditimpa ke tiga view dan dicek ±1–2 cm).
  - [x] **Model sheet Aksa** [21-model-sheet-aksa.md](21-model-sheet-aksa.md): proporsi terukur, palet hex, part list, keputusan desain D1–D10, checklist IP.
  - [x] Scene `Art/Blender/aksa_v00_setup.blend` (`Art/Scripts/aksa_00_setup_scene.py`: collection per kelompok, reference plane, penggaris 1,75 m, 19 landmark `AK_LM_*`). Catatan: reference plane hanya tampil di viewport ortografis (numpad 1/3/7), bukan di `look` perspektif.
  - [x] **Spike skeleton (A1/A3)** lulus (hasil di [Temuan](#hasil-spike-12-okt-2026--jalur-a-dipilih)): S1 ekspor Manny, S2 analisis, S3 export sesuai kontrak, S4 impor ke `SK_Mannequin` + banding pose referensi (selisih ≤0,005 mm, 0,000°), S5 animasi Mannequin identik. Jalur (a) dipilih; tinggi Aksa = 180,6 cm (A3 revisi).
- **Developer:** menyetujui model sheet & A1–A9 (+ D1–D10); memasang ekstensi MPFB2 (A2) setelah sumber/lisensinya dicek.
- **Gate:** model sheet disetujui (⏳ developer); spike lulus, jalur (a) dipilih (✅); reference plane sejajar (✅).

### Iterasi 1 — Badan dasar + proxy pakaian + rig (Manny asli, jalur (a))
**Tujuan:** proporsi benar, ter-rig, dan **jalur SK_Aksa menggantikan placeholder terbukti** sejak awal.
- **Claude (selesai 12 Okt 2026):**
  - [x] Armature = Manny asli + tulang `root` + rantai `sash_01..06` (`Art/Scripts/aksa_10_armature.py` → `Art/Blender/aksa_v01_proxy.blend`; 95 tulang, 31 tulang deform; LOD2 Manny jadi hantu referensi `AK_REF_MannyGhost`, tidak ikut export). Referensi diskala 1,032.
  - [x] Proxy dari primitif (`aksa_11_proxy.py`, `ak_common.py`): 30 bagian, **3.094 tris**, 5 slot (Skin, Eyes, Hair, Cloth, Gear), warna zona lewat vertex color `AK_Zone`. Kepala/rambut/mata kaku ke `head`; kaos, jaket (depan terbuka), kerah, lengan jaket, celana + kantong kargo, sabuk, boots ter-skin dengan bobot jarak ke segmen tulang + haluskan; selendang berbobot sepanjang rantai `sash_*`; kalung/liontin ke `spine_05`. Badan di bawah leher digeser 2,2 cm ke belakang (sumbu konsep, `BODY_SHIFT_Y`).
  - [x] **Siluet vs konsep** (`aksa_12_render.py` + `aksa_12_compare_sheet.py`, kanvas 1000 px): IoU badan (tanpa lengan dan kaki bawah) depan **0,88**, samping **0,80**, belakang **0,86**. IoU seluruh siluet lebih rendah (0,61/0,79/0,64) karena pose rest Manny beda dari konsep: lengan 35°/53° (konsep 22°) dan kaki lebih rapat (±0,14 vs ±0,22 m di pergelangan).
  - [x] **6 uji pose** (`aksa_13_pose_tests.py`, action `AK_PoseTest`): kuda-kuda, pukul, tendang tinggi, dodge, jongkok, tangan terangkat. Peregangan tepi maks **7,7 cm** (jongkok dalam, `AK_PantsLeg`; tepi proxy panjang), 7,3 cm (lengan terangkat, `AK_Sleeve`), 6,0 cm (tendang tinggi); pose lain ≤4 cm. Tidak ada robekan atau tembus parah secara visual.
  - [x] Export (`aksa_14_export.py`) → `Art/Export/SK_Aksa_Proxy.fbx` + `SK_Aksa_Proxy_sockets.json` (7 socket: `hand_*_hit`, `foot_*_hit`, `pendant`, `head_fx`, `back_fx`). **Validator** `validate_aksa.py`: **17/17 lulus** (88 tulang Manny identik ≤0,003 mm dan 0,000°, `root` satu-satunya akar, tulang tambahan hanya `sash_*`, 1 mesh, 5 slot berurutan, ≤4 influence, bobot ternormalisasi, tinggi 1,804 m, 7 socket).
  - [x] Impor UE (`Tools/ue_import_aksa.py`): `SK_Aksa` di `/Game/Jayadwara/Characters/Aksa/Mesh/` memakai `SK_Mannequin` (tulang `sash_01..06` tergabung; skeleton jadi 167 tulang), `M_Aksa_Proxy` + 5 MI, 7 socket, `PA_Mannequin` sementara. **Animasi Mannequin jalan di SK_Aksa** (`Tools/ue_check_aksa.py`: attack/walk/idle identik dengan Manny).
  - [ ] **Belum:** `BP_Aksa` belum diganti ke `SK_Aksa` (hanya diuji lewat actor sementara); keputusan penggantian komponen visual menunggu review developer.
  - [ ] **Belum terverifikasi visual:** warna proxy di UE setelah material terakhir (`M_Aksa_Proxy`: vertex color → Power 2,2 → Base Color). Warna zona terbukti sampai ke UE (uji dengan jalur emissive: jaket, celana, kulit, selendang terbaca), tapi screenshot akhir gagal karena viewport editor tidak merender saat jendela tidak terlihat (`HighResShot` butuh editor aktif). Buka editor lalu `python Tools/ue_remote.py Tools/ue_check_aksa.py` untuk mengecek, hapus actor uji dengan perintah CLEAN di header skrip.
- **Developer:** review proporsi di Blender (`aksa_v01_proxy.blend`) dan di game ("bahu lebih lebar", "kaki kurang panjang").
- **Gate:** siluet depan/samping cocok dengan konsep (✅ dalam batas pose Manny: badan 0,80–0,88); animasi Manny jalan di `SK_Aksa` proxy (✅); tidak ada tembus parah di 6 pose (✅ visual; metrik peregangan di atas). **Menunggu review developer.**
- **Catatan:** badan dibuat dari primitif (bukan MPFB2); MPFB2 baru relevan untuk kepala di Iterasi 2 dan tetap menunggu keputusan A2.

### Iterasi 2 — Kepala & wajah + rambut
**Tujuan:** wajah yang terbaca sebagai Aksa. **Bagian paling berisiko**, jadi dikerjakan sebelum pakaian hero.
- **Claude (putaran 1 selesai 12 Okt 2026):**
  - [x] **Kepala dari skrip, bukan MPFB2** (MPFB2 belum disetujui/dipasang; unduhan butuh izin): `Art/Scripts/ak_head.py` membangun kulit sebagai loft cincin (104 level, rapat di zona mata/hidung/mulut; 88 titik per cincin, rapat di muka ±76°) dari profil terukur `ak_head_front/side.png` (KEYS: lebar, y depan/belakang per tinggi, interpolasi Hermite mulus), lalu fitur wajah analitik sepanjang normal: soket + bukaan mata almond, kelopak, alis menonjol, hidung (jembatan, ujung, sayap, lubang), filtrum, bibir atas/bawah, garis mulut, dagu, tulang pipi. **Semua angka wajah ada di `KEYS` dan `feature()`**, jadi iterasi feedback = ubah angka lalu jalankan ulang `aksa_20_head.py`.
  - [x] Telinga (`AK_Ear_L/R`, dengan cekungan + tepi heliks), mata (`AK_EyeSclera/Iris/Pupil` terpisah, slot Eyes; **kornea ditunda ke Iterasi 5** karena butuh material translucent), alis mesh (`AK_Brows`, menempel ke permukaan lewat ray cast), leher baru (lebih ramping, di belakang rahang).
  - [x] Rambut (`ak_hair.py`, seed tetap): tudung kulit kepala (tepi dihaluskan) + **343 gumpalan** pipih runcing: 2 lapis poni (menyapu ke +X), volume puncak, tuft keliling, 6 jambul pendek, sisi + cambang, belakang berlapis; ±12% gumpalan berwarna highlight coklat (`AK_HairHi`). Tinggi rambut maks 1,809 m (dalam batas Manny ±2 cm), lebar maks ±0,117 m.
  - [x] Render pembanding berbingkai sama dengan referensi (`aksa_21_render_head.py` + `aksa_21_head_sheet.py`, Eevee): `Art/Export/_compare_aksa_kepala.png` (depan + samping, konsep vs model) dan `_aksa_kepala_q34.png` (3/4).
  - [x] Export `Art/Export/SK_Aksa_WIP.fbx` (32.315 tris total) → **validator 17/17**; terimpor ke UE (`Tools/ue_import_aksa.py` memilih FBX terbaru otomatis), `SK_Aksa` terperbarui.
  - **Anggaran tris:** kepala kulit 18,3k (anggaran 12k), rambut 9,2k + 0,9k (6k), mata 1,5k. Total model 32k < 60k, jadi aman, tapi LOD1+ harus memangkas kepala dan rambut (Iterasi 6).
  - **Penilaian jujur putaran 1:** siluet kepala, proporsi, mata, hidung, dan massa rambut sudah dalam bahasa konsep, tapi **wajah belum "terasa Aksa"**: area mulut-dagu bergelombang dan terlalu datar, hidung terlalu runcing, tulang pipi/rahang belum tegas, rambut masih terlalu runcing seperti duri dan kurang menyapu seperti helai di konsep, belum ada ekspresi/kehidupan di mata (tanpa kornea/refleksi). Ini batas wajar bentuk dari fungsi; bagian ini memang paling butuh mata manusia.
- **Claude (putaran 2, 12 Okt 2026, setelah developer: "wajah masih jauh berbeda", izin MPFB, "rambut tidak harus sama dengan konsep, yang penting bagus dan cocok"):**
  - [x] **MPFB 2.0.18 terpasang** (A2 disetujui): dari extensions.blender.org (ekstensi resmi), `add-on-mpfb-v2.0.18.zip` 43,8 MB, SHA-256 dicocokkan (`c075b3e9…2dad`). Lisensi: kode GPLv3, **aset inti (base mesh, target) CC0**; aset sistem tambahan (mata/alis/rambut MPFB) tidak dipakai.
  - [x] **Kepala MPFB** (`Art/Scripts/aksa_22_mpfb_head.py`): `create_human` laki-laki 25 th, atletis, campuran Asia/Kaukasia/Afrika (`MACRO`) + ±45 target wajah (`TARGETS`: rahang bentuk V bersudut, pipi tirus, alis rendah ujung dalam turun, mata berjarak lebar dan lebih terbuka, hidung lurus lebih pendek, bibir tidak maju, leher atletis). Kepala + telinga + leher diambil (bahu MPFB dibuang, tepi leher dirapikan, masuk ke dalam kaos), dipetakan ke ukuran konsep (skala 0,757; x 0,787; mata z 1,668; hidung y -0,111). 8.860 tris (sebelumnya 18,3k).
  - [x] Bola mata di pusat helper mata MPFB (r 12,4 mm), garis bulu mata gelap lewat vertex color, warna bibir, alis mesh lebih tebal-panjang. Bobot: kaku ke `head` di atas garis rahang, campuran `neck_02/neck_01/spine_05` di bawahnya.
  - [x] **Rambut gaya baru** (`ak_hair2.py`, menggantikan gumpalan duri `ak_hair.py`): textured crop rapi: cangkang bervolume (tebal di atas/depan, tipis di sisi/tengkuk, tepi berdinding) + 170 gumpalan berpenampang lensa yang **menempel mengikuti medan aliran** (menyapu ke depan dan ke kiri karakter, sisi turun), poni pendek berhenti di atas alis, highlight coklat halus 6%. Rambut 7,1k tris (sebelumnya 10k).
  - [x] `Art/Blender/aksa_v03_mpfb.blend`; export `SK_Aksa_WIP.fbx` **19.751 tris total**, **validator 17/17**; `SK_Aksa` di UE terperbarui. Perbandingan: `Art/Export/_compare_aksa_kepala.png`, `_aksa_kepala_q34.png`.
  - **Penilaian:** wajah sekarang wajah manusia yang meyakinkan dengan rahang tegas dan alis serius; rambut rapi dan cocok untuk game. Masih beda dari konsep: mata belum sebesar ilustrasi, bibir sedikit tebal, warna kulit masih datar (tekstur & pipi di Iterasi 5), belum ada kornea.
- **Claude (putaran 3, 12 Okt 2026, developer memberi gambar referensi gaya stylized: "rambutnya kayak gini", "alisnya juga, matanya juga"):**
  - [x] **Rambut gaya 3** (`ak_hair3.py`): disisir ke belakang dengan belahan samping (kanan karakter), jambul depan rendah, sisi disisir ke belakang; cangkang menipis halus ke garis rambut yang **ditempel tepat ke kurva garis rambut** (tidak bergerigi); 53 helai teratur sejajar berpenampang lensa (2 baris atas berselang, sisi, belakang) dengan normal dihaluskan. Warna tetap hitam Aksa (referensi coklat; tinggal ganti `HEX["hair"]`). Rambut 5,1k tris.
  - [x] **Mata stylized lebih besar**: daerah mata (kelopak + bola mata) diperbesar 1,20x dengan falloff halus, iris r 7,4 mm, pupil 3 mm, garis bulu mata atas lebih tipis. Warna iris tetap coklat.
  - [x] **Alis seperti referensi**: tebal, terpisah di tengah, lengkung dengan puncak di 2/3 lalu meruncing ke luar.
  - [x] Bibir dikecilkan (volume/lebar turun, mundur). Export `SK_Aksa_WIP.fbx` **17.801 tris**, validator **17/17**, `SK_Aksa` di UE terperbarui; gambar `Art/Export/_compare_aksa_kepala.png`, `_aksa_kepala_q34.png` (depan, 3/4, samping).
- **Claude (putaran 4, 12 Okt 2026, developer memberi referensi wajah stylized-game #2: "wajahnya masih kurang"):** target MPFB disetel ulang (`TARGETS` di `aksa_22_mpfb_head.py`): rahang lebar bersudut + dagu kotak (`head-square` 0,55, `chin-bones` 0,8, `chin-width` +0,4), pipi penuh, **alis tebal rendah miring turun ke hidung** (`eyebrows-angle-down` 0,5), mata sedang dengan kelopak atas berat (skala 1,08x), **hidung lebar** (width1-3 +0,35–0,45, sayap jelas), mulut lebar dengan bibir tipis dan sudut sedikit turun, leher tebal; macro otot 0,78. Leher MPFB dipotong lebih rendah (masuk ke kaos); rambut tetap sisir-belakang (+volume atas supaya tinggi tetap lolos). Karena leher berubah, pakaian dibangun ulang (`aksa_30_outfit.py`). Export 48.260 tris, validator 17/17, `SK_Aksa` di UE terperbarui. Ekspresi dibuat netral-serius; kalau mau lebih marah seperti referensi, naikkan `eyebrows-angle-down` dan `mouth-angles-down`.
- **Developer:** feedback wajah (bagian yang paling butuh mata manusia). Opsi cepat: sculpt langsung di `aksa_v02_head.blend` (objek `AK_Head`, mode Sculpt; skrip tidak boleh dijalankan ulang di atas hasil sculpt), atau beri catatan per bagian untuk putaran 2.
- **Gate (Go/No-Go):** wajah "terasa Aksa" menurut developer. Kalau belum setelah 2 putaran revisi: pilih perbaiki lagi, atau **commission sculpt kepala saja** dengan model ini sebagai basis (jauh lebih murah daripada commission karakter utuh); MPFB2 (A2) tetap opsi untuk basis wajah yang lebih alami.

### Iterasi 3 — Pakaian hero
- **Claude:** jaket (terbuka, kerah tinggi berlapis batik, lengan digulung, kantong dada, aksen emas bahu, emblem emas di punggung), kaos, celana kargo (kantong samping, strap paha), sabuk + gesper emas, selendang batik, sarung tangan tanpa jari, boots bertali + trim emas, kalung + liontin pecahan batu. Hapus kulit tertutup (A6). Skrip fit ala `15_body_fit.py`: pakaian pas di badan tanpa celah dan tanpa tembus.
- **Claude (putaran 1 selesai 12 Okt 2026):** `Art/Scripts/aksa_30_outfit.py` + `ak_cloth.py` → `Art/Blender/aksa_v04_outfit.blend` (48 objek pakaian/tangan, 32,7k tris; total model **48,3k tris**).
  - [x] **Tangan + lengan bawah**: metaball mengikuti tulang jari Manny (tiap jari terpisah agar tidak menyatu), bobot ke tulang jari (tulang jari Manny kini `use_deform`). **Sarung tangan tanpa jari** metaball + strap pergelangan, tanpa kulit tembus.
  - [x] **Kaos** dengan leher bulat mengikuti leher MPFB + rib; **jaket** terbuka setebal 4,5 mm dengan pita pinggang, 2 kantong dada bertutup + 4 kancing emas, ritsleting emas di kedua tepi, pita emas bahu, emblem punggung teratai + sinar (D6, bukan garuda); **kerah berdiri** (luar navy, lapisan dalam batik); **lengan jaket** + manset gulung berlapis + batang jahit emas + emblem lengan atas.
  - [x] **Celana kargo** (lutut sedikit longgar, kerutan di atas boots) + **kantong kargo** bertutup kedua paha + **strap paha** bergesper emas; **sabuk** + gesper berbingkai + 5 tali sabuk; **selendang** batik (simpul + pita menempel paha, rantai `sash_*`); **kalung** (rantai mengikuti dada/leher + pecahan batu berbingkai emas); **boots** bertali (badan + batang, sol tebal bergerigi, trim emas, 12 kait emas, tali silang, strap atas + gesper).
  - [x] Anti-tembus antar lapisan (`push_outside`): kaos↔leher, jaket↔kaos, kerah↔leher, sarung tangan↔tangan, celana↔boots.
  - [x] Siluet vs konsep (`aksa_12_*`): IoU badan depan **0,86**, samping **0,77**, belakang **0,85** (`Art/Export/_compare_aksa_outfit_front/side.png`); render Eevee `_aksa_outfit_q34.png`.
  - [x] Uji pose (6): peregangan maks **8,0 cm** (lengan jaket saat tangan terangkat), pose lain ≤6,5 cm; badan jaket mengikuti clavicle, bukan lengan atas (sebelumnya 13,5 cm). Visual: `_compare_aksa_outfit_poses.png`, tanpa robekan atau tembus parah.
  - [x] Export `SK_Aksa_WIP.fbx` **validator 17/17**; terimpor ke UE (`SK_Aksa`), dicek di editor: warna zona tampil (material vertex color + koreksi sRGB terverifikasi), animasi `MM_Attack_01`/`Walk_Fwd`/`MM_Idle` jalan identik dengan Manny (`Art/Export/_aksa_ue_check.png`).
  - **Catatan:** warna/motif (batik, jahitan) masih warna datar → Iterasi 5. Lipatan kain masih sederhana. Boots masih agak membulat di ujung.
- **Developer:** review per kelompok (atasan → bawahan → aksesori → sepatu).
- **Gate:** render ortografis berdampingan dengan konsep; tidak ada celah/tembus di pose netral dan kuda-kuda.

### Iterasi 4 — Skinning final, rantai kain, morph target
- **Claude:** bobot final (bahu, pinggul, lutut untuk pose silat lebar), tulang twist & jari dari skeleton Manny, rantai `sash_*` dan `jacket_*`, 8 morph target (A4), uji pose diperluas (13 pose seperti Jayadwara) + `06_deform_check.py`.
- **Claude (putaran 1 selesai 12 Okt 2026):**
  - [x] **8 morph target wajah** (`ak_blink_L`, `ak_blink_R`, `ak_smile`, `ak_angry`, `ak_mouth_open`, `ak_brow_up`, `ak_wince`, `ak_sad`) dari unit ekspresi FACS bawaan MPFB (ras asian; resep di `RECIPES`, `aksa_22_mpfb_head.py`), delta dipetakan ke ukuran konsep dan ditulis sebagai shape key `AK_Head`; alis (`AK_Brows`) ikut lewat transfer delta dari vertex kepala terdekat. Basis kepala MPFB punya rongga mulut, jadi `ak_mouth_open` menampakkan bagian dalam mulut. Render: `Art/Export/_aksa_morphs.png` (`aksa_41_render_morphs.py`). **Mata lirik** ditunda: butuh tulang mata (rig wajah, Iterasi 7); diganti `ak_sad`.
  - [x] **Rig final** (`Art/Scripts/aksa_40_rig.py`): tulang twist Manny (`upperarm/lowerarm/thigh/calf_twist_01/02`) kini deform dan ikut bobot lengan jaket, tangan, celana, kantong kargo (segmen bobot dipecah sepanjang anggota badan); rantai **`jacket_l_01..02` / `jacket_r_01..02`** (induk `spine_03`) untuk dua ujung depan jaket, dicampur ke badan jaket, pita pinggang, dan ritsleting emas menurut tinggi dan kedekatan ke tepi depan. Rantai `sash_01..06` sudah ada (Iterasi 1). Total 99 tulang, 89 deform.
  - [x] **13 pose + rest** (`aksa_13_pose_tests.py`): kuda-kuda, pukul, tendang tinggi, dodge, jongkok, lari, lompat, tendang samping, tangkis, putar badan, lunge, bungkuk, tangan terangkat. Peregangan tepi maks **7,8 cm** (lengan jaket saat tangan terangkat), pose lain ≤6,5 cm (`AK_Trousers_pelvis` pada tendang tinggi). Visual `Art/Export/_compare_aksa_13pose.png`: tanpa robekan atau tembus parah; ada sudut runcing kecil di pangkal lengan jaket saat lengan diangkat tinggi (tendang tinggi/samping), kandidat perbaikan manual bobot.
  - [x] Export `SK_Aksa_WIP.fbx` (48.260 tris, shape key ikut: kepala dijadikan objek aktif saat join) dan **validator 20/20** (tambahan: `--require-morph 8` memeriksa jumlah morph, tidak ada vertex di bawah leher yang bergeser, tiap morph menggeser vertex).
  - [x] Impor UE (`import_morph_targets` aktif): `SK_Aksa` dengan **8 morph target** dan skeleton 171 tulang (jacket_* tergabung ke `SK_Mannequin`). Cek editor: animasi serang/jalan/diam jalan identik Manny (`Art/Export/_aksa_ue_check.png`).
  - **Belum:** Anim Dynamics untuk `sash_*` dan `jacket_*` (di ABP, Iterasi 6); bobot jari (tangan statis diuji di pose rest saja); perbaikan manual bobot bahu/pinggul oleh developer.
  - **Urutan pipeline** (penting): `aksa_22` → `aksa_30` → `aksa_40` → `aksa_13` → `aksa_14` → `validate_aksa --require-morph 8` → UE import. Menjalankan ulang `aksa_30` menghapus tulang jari/twist deform dan bobot ulang, jadi `aksa_40` wajib diulang.
- **Developer:** perbaikan weight manual di titik rumit.
- **Gate:** peregangan maks terukur dan dijelaskan; tidak ada tembus kain × kaki di kuda-kuda dan tendangan; morph target tidak merusak mesh.

### Iterasi 5 — UV, tekstur & material
- **Claude:** UV terskrip (`07_uv_unwrap.py` dengan packer sendiri), tekstur dasar (mask zona, BC, N, ORM), motif batik pada kerah & selendang, material preview di Blender yang meniru parameter UE, spesifikasi material Aksa (dokumen baru di `docs/`).
- **Developer:** hand-paint kulit (gradasi, pipi), lipatan kain, keausan sepatu; review motif.
- **Catatan budaya:** motif batik umum (kawung, ceplok, truntum); **hindari batik larangan keraton** (parang rusak, dll., [06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)).
- **Claude (putaran 1 selesai 12 Okt 2026):** spesifikasi lengkap di [22-spesifikasi-material-aksa.md](22-spesifikasi-material-aksa.md).
  - [x] **UV terskrip** (`aksa_50_uv.py`): per slot, `smart_project` 85° + packer sendiri (shelf + pencarian biner; density berbobot: kepala 2,2×, tangan 1,5×); mata = proyeksi planar kiri/kanan. NPZ per-segitiga `Art/Export/_uv_faces_aksa.npz`. Validator: UV 0–1 + segitiga degenerate <2%.
  - [x] **Tekstur dasar** (`make_textures_aksa.py` → `Art/Export/Textures_Aksa/`, 17 PNG): BC dari vertex color + variasi, N, ORM, SSS (kulit), Mask zona (kain), kawung pada kerah dalam & selendang.
  - [x] **Material Blender** (`aksa_51_materials.py`, `aksa_v05_tex.blend`) meniru master UE; render cek `Art/Export/_aksa_tex_full.png`, `_aksa_tex_head.png`.
  - [x] **UE**: `ue_import_aksa.py` mengimpor tekstur (tidak menimpa yang sudah ada), membuat `M_Aksa_Master` + 5 `MI_Aksa_*` bertekstur; `SK_Aksa` terimpor ulang, validator **22/22**.
  - [x] **Rambut gaya 4 — helai** (permintaan developer: gaya 3 terlalu kasar/bergumpal): `ak_hair4.py` + `aksa_23_hair4.py` (ganti rambut di file kerja tanpa mengulang kepala/pakaian/rig). Cangkang gaya 3 tetap sebagai dasar; ditutup 520 helai pita datar 1,6–3 mm (revisi 2: lebih tipis & jarang, rambut hitam pekat `#0D0C0E`) yang meruncing ke ujung, mengikuti medan aliran + arah gerombol (disisir ke belakang, menjauhi belahan), 5% helai highlight. Model 51,6k tris (batas 60k), validator 22/22. Render: `Art/Export/_aksa_tex_head.png`, `_aksa_tex_back.png`, `_aksa_tex_side.png`. Catatan: UV rambut = ±1800 island kecil (cat rambut sebaiknya lewat warna dasar/vertex, bukan hand-paint per helai).
  - [x] **Revisi wajah** (`aksa_24_face.py`, tanpa mengulang kepala/pakaian/rig; permintaan developer + gambar garis putih): alis dibangun ulang sebagai busur tipis (puncak di atas pertengahan mata, ujung dalam lebih rendah, ujung luar lebih pendek); **senyum tipis permanen** (50% delta `ak_smile` dipanggang ke Basis, `ak_smile`=1,0 tetap senyum penuh); **mata lebih terbuka** (kelopak atas naik maks ±3,2 mm, bawah turun 0,8 mm, dipanggang ke Basis dan semua key kecuali kedipan, jadi blink tetap menutup penuh) karena mata terkesan mengantuk. Idempoten (`ak_face_rev`).
  - [x] **Revisi wajah 5** (developer: "wajah sangat tidak mirip" konsep; rambut sudah oke): dibandingkan dengan `ak_head_front/side.png` lewat `aksa_21_render_head` + lembar crop, lalu `aksa_22` disetel ulang: skala dari mata→ubun-ubun (`EYE_TO_CROWN`, tengkorak tetap) supaya wajah bisa memanjang; target MPFB wajah oval-V, tulang pipi tinggi + pipi tirus, dagu lebih panjang & maju, hidung ramping lurus, mulut lebih sempit, alis rendah; wajah lebih lebar (`SX_EXTRA` 1,10) tetapi leher bawah dikecilkan ke ukuran lama (`NECK_KX/KY`, kaos & kerah tidak tembus); wajah bawah sedikit dipanjangkan (`LOWER_K`). Putaran 5b (developer: makin jelek, kepala tidak proporsional dengan badan, rambut terlalu tinggi, bibir pucat): **kepala diperbesar 16%** dari pangkal leher (`HEAD_K`; rambut dibangun di kepala skala 1 lalu diskalakan), dagu/hidung dipendekkan lagi, **rambut dipipihkan** (`ak_hair3.thick`), **bibir `#A4584A`** + bibir dikecualikan dari SSS, senyum 0,15. Validator tinggi kini −6/+2 cm (rambut boleh lebih rendah dari Manny). Bug: `aksa_22` ikut menghapus `AK_Necklace` (awalan `AK_Neck`) — diperbaiki, kalung dipulihkan dari v04.
  - [x] **Revisi tampak samping 5c** (developer: dari samping jelek): peregangan dagu depan (`LOWER_K`) dihapus karena membuat garis bawah rahang miring ke leher; dagu dipanjangkan lewat target + `chin-prognathism` 0,6 (dagu maju), `neck-double-decr` (rahang tegas), dahi lebih miring ke belakang, ujung hidung sedikit naik, pivot pembesaran kepala diturunkan ke 1,535 (seluruh rahang ikut terskala rata); alis kini 25 titik ray cast (mengikuti lengkung kepala, tidak mencuat lurus dari samping); **cambang** di depan telinga (`ak_hair3.hairline_at`) supaya pelipis tidak botak; senyum 0,08.
  - [x] **Rambut gaya 5 — low fade + atas bertekstur** (`ak_hair5.py`, dipakai `aksa_22`; referensi foto dari developer): samping & belakang = rambut cukur lewat warna vertex kulit kepala (`paint_fade`, gelap → kulit, masuk ke BC; SSS dimatikan di area itu), garis bobot `top_line` membulat di belakang (tidak lancip); atas = lapisan tipis (maks ±1,2 cm) + 950 helai halus 1,2–2,6 mm dari pusaran ubun-ubun ke depan, poni pendek miring, ujung terangkat acak, garis potong/ujung poni acak. Bibir atas & bawah disamakan (`mouth-upperlip-volume-incr` / `mouth-lowerlip-volume-decr`).
  - **Temuan:** nilai shape key `AK_Head`/`AK_Brows` tersimpan 1,0 di file kerja (wajah terbuka/terpejam saat dirender) → `aksa_14_export.py` kini me-nol-kan nilai pada salinan sebelum export.
  - **Belum / catatan:** cek visual di editor UE tertunda (HighResShot butuh editor terlihat); kornea/SSS di UE; **UV kepala belum rapi untuk hand-paint** (lihat 22 bagian 5).
- **Gate:** preview mendekati palet konsep; tepat 5 slot; ukuran tekstur sesuai 6.3.

### Iterasi 6 — LOD, export & integrasi UE
- **Claude:** LOD1–3 (`16_make_lods.py`, lindungi mata/wajah/liontin), export final, validator di semua LOD; skrip import (generalisasi `ue_import_jayadwara.py` → `ue_import_character.py`) ke `SKEL_Mannequin`; material master `M_JD_Character` + 5 MI; **ganti MetaHuman → `SK_Aksa` di `BP_Aksa`** sesuai [12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa); Physics Asset; Anim Dynamics selendang & ujung jaket; render **potret dialog** (netral, senyum, marah) dari model untuk UI ([18](18-kebutuhan-episode-1.md#f-ui--narasi)).
- **Claude (putaran 1 selesai 12 Okt 2026):**
  - [x] **LOD** (`Art/Scripts/aksa_60_lods.py`): `SK_Aksa.fbx` (LOD0 52,2k tris, 8 morph) + `SK_Aksa_LOD1..3.fbx` = **23,0k / 8,2k / 3,1k** (anggaran A8: 25k / 10k / 4k). Decimate per bagian (kepala/mata dijaga), helai rambut dipangkas di LOD1 dan dibuang mulai LOD2 (lapisan rambut tetap), tali sepatu & tali sabuk dibuang di LOD2, jari & pupil di LOD3; muka luas nol dibuang. Validator: LOD0 22/22, LOD1–3 19/19 (socket memakai JSON LOD0; cek UV degenerate mengabaikan muka luas nol).
  - [x] **UE** (`Tools/ue_import_aksa.py`): LOD1–3 diimpor ke `SK_Aksa` (screen size 1,0 / 0,45 / 0,22 / 0,10); mesh kini **ditimpa, bukan dihapus** supaya rujukan `BP_Aksa` utuh; `AKSA_RETEX` dibuang setelah dibaca (proses editor persisten).
  - [x] **`Tools/ue_setup_aksa.py`**: `PA_Aksa` (20 kapsul, dibangun ulang dari mesh lewat `JDEditorToolsLibrary`), `ABP_Aksa` = salinan `ABP_Unarmed` + **Anim Dynamics ujung jaket** (`jacket_l/r_01..02`, ditolak paha), **`BP_Aksa`: mesh = `SK_Aksa`, anim = `ABP_Aksa`** (tanpa perubahan C++). Uji PIE di `Test_Greybox`: pawn jalan dengan `SK_Aksa`, rantai jaket stabil.
  - [x] **Keputusan:** karena `SK_Aksa` memakai skeleton Mannequin asli (jalur (a)), ia **langsung menjadi mesh logika**; lapisan "mesh visual" + MetaHuman di [12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa) tidak dipakai (MetaHuman placeholder tidak pernah dibuat).
  - [x] **Selendang dilepas sementara** (developer: desain belum pas). Objek `AK_SashNew*` disembunyikan di `aksa_v05_tex.blend` (properti `ak_kind` → `ak_kind_off`, kembalikan untuk memasang lagi); tulang `sash_*` tetap di skeleton. Temuan PIE: rantai 6 body berskala manusia **melar ke bawah** dengan iterasi solver bawaan Anim Dynamics (gravitasi menang atas batas linear; dengan gravitasi 0 stabil) — saat selendang kembali, naikkan `NumSolverIterationsPre/PostUpdate` di `JDEditorToolsLibrary` atau pakai `GravityScale` kecil.
  - [x] **Potret dialog** (`Art/Scripts/aksa_61_portraits.py`): netral / senyum / marah dari morph target model, 1024² latar transparan → `Art/Export/Portraits/` dan `/Game/Jayadwara/UI/Portraits/` (tekstur UI). Lembar: `Art/Export/_aksa_portraits.png`.
  - **Belum:** uji 60 FPS & penilaian visual di bawah lighting Ep 1 (developer); Physics Asset masih kapsul generik (cukup untuk ragdoll/hit dasar); kornea/SSS di UE; screenshot editor otomatis belum berhasil (HighResShot butuh editor terlihat).
- **Developer:** main di game, nilai di bawah lighting Ep 1.
- **Gate:** semua animasi gameplay jalan di `SK_Aksa`; tidak ada perubahan kode/ABP yang dibutuhkan untuk mengganti MetaHuman; 60 FPS di `Test_Greybox`.

### Iterasi 7 — Polish & varian *(opsional, Fase 2+)*
Rig wajah penuh untuk cutscene, kepala hi-res, varian pakaian (seragam DWARA, kasual, versi terluka setelah boss Ep 1), model Dimas sebagai turunan Aksa (sepupu, rig sama).

---

## 8. Checklist IP & budaya (dipakai di setiap gate)

- [ ] **Tidak ada alat transformasi di lengan** (gauntlet, gelang, bracer, jam): terlalu mirip Mebius Brace ([01](01-konsep-dan-pilar.md#wajib-dihindari)).
- [ ] Kalung/liontin **tidak menyala** di luar adegan transformasi dan **tidak berfungsi sebagai timer**.
- [ ] Tidak ada silver/chrome atau cahaya biru (palet "teknologi" di konsep lama dibuang).
- [ ] Emblem punggung jaket bukan Garuda dan tidak mirip logo tim di serial Ultra.
- [ ] Motif batik umum, bukan batik larangan.
- [ ] Pose uji & animasi: hindari silang lengan bentuk L.

---

## 9. Risiko

| Risiko | Mitigasi |
|---|---|
| Wajah terlihat kaku / tidak mirip | Basis MPFB2 (A2), Iterasi 2 dikerjakan sebelum pakaian, render pembanding close-up, gate Go/No-Go, fallback commission sculpt kepala |
| Skeleton Manny rusak setelah bolak-balik Blender ↔ UE | Spike di Iterasi 0 sebelum modeling apa pun; fallback skeleton sendiri + retargeter (sudah terbukti di Jayadwara) |
| Kain tembus kaki di pose silat lebar | Uji kuda-kuda & tendangan sejak proxy (Iterasi 1); celana sedikit longgar di selangkangan; rantai tulang selendang |
| Lisensi aset basis | Hanya aset CC0 dari MPFB2; catat asal setiap aset di `Art/README.md` |
| Waktu bersaing dengan Fase 0–1 | Keputusan A9: kerjakan paralel atau tunggu Fase 2; MetaHuman menutup kebutuhan visual sementara |
| Referensi AI tidak konsisten antar-view | Diputuskan di model sheet (Iterasi 0) |

---

## 10. Keputusan untuk Developer (sebelum Iterasi 0)

| # | Pertanyaan | Usulan Claude |
|---|---|---|
| **A1** | Pakai skeleton Mannequin asli? | **Ya, kalau spike lulus** (jalur (a)); kalau tidak, skeleton sendiri + retargeter (jalur (b)). Lihat [Temuan Iterasi 0](#temuan-iterasi-0-12-okt-2026) |
| **A2** | Pasang ekstensi MPFB2 di Blender (unduh dari extensions.blender.org)? | **Ya**, hanya aset CC0 |
| **A3** | Tinggi Aksa 175 cm? | **Ya**, tapi hanya terjamin di jalur (b); di jalur (a) tingginya = tinggi Manny (diukur di spike S1) |
| **A4** | Ekspresi lewat morph target saja (tanpa rig wajah) untuk sekarang? | **Ya**; rig wajah di Iterasi 7 |
| **A5–A8** | Rambut gumpalan, hapus kulit tertutup, rantai kain, anggaran 60k | **Ya** (default di bagian 3) |
| **A9** | Mulai kapan: sekarang sebagai jalur art paralel, atau menunggu Fase 2 (Apr 2027)? | **Dibaca "sekarang"** (permintaan 12 Okt 2026; Iterasi 0 sudah berjalan). Konfirmasi dan dampaknya ke Fase 0–1 di [10](10-roadmap.md) tetap keputusan developer. Sisa Iterasi 6 Jayadwara (uji main di `Test_GiantScale`) jangan sampai terbengkalai |

---

## 11. Backlog (di luar scope rencana ini)

- Rig wajah penuh & lip-sync (voice acting di luar scope vertical slice).
- Varian pakaian Aksa, model Dimas (turunan rig Aksa).
- Anggota DWARA lain sebagai karakter 3D (vertical slice cukup potret).
