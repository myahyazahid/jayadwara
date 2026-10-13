# 25 — Rencana Redesign Jayadwara (Model Tripo Realistis)

> **Status: v1.0 — SELESAI, Jayadwara2 dipakai (13 Okt 2026, R6).** [Riwayat: v0.1 persiapan 12 Okt 2026.] Hasil tiap iterasi di bagian 9; keputusan bagian 3 dipakai sesuai default kecuali yang dicatat berubah di hasil iterasi (mis. R8 material 1 slot, sayap kinematik di R3d).
> Pola kerja mengikuti **jalur B Jerangkong** ([20](20-rencana-model-jerangkong.md#jalur-b--basis-model-developer-tripo-ai-12-okt-2026)): developer membuat bentuk di Tripo AI, Claude membereskan normalisasi, rig, skinning, tekstur, LOD, dan integrasi UE.
> Model lama (stylized, dibangun dari skrip) tetap ada dan **tidak boleh ditimpa** ([13](13-rencana-model-jayadwara.md)). Penggantian di game harus bisa dibalik dengan satu skrip.

---

## 1. Tujuan & syarat selesai

Jayadwara versi baru (**Jayadwara2**) dianggap siap menggantikan model lama kalau:

- [ ] `SK_Jayadwara2` (LOD0–LOD3) dengan **nama & hierarki tulang yang sama** dengan model lama (89 tulang: Mannequin + twist + jari + IK + `scarf_l/r_01…06` + `cloth_front/back_01…03`), sehingga skrip retarget, Physics Asset, Anim Dynamics, dan socket bisa dipakai ulang.
- [ ] Zirah tetap **kaku** saat bergerak (tidak melentur seperti karet), undersuit melentur rapi, tanpa celah & punuk di bahu, sabuk di pinggang (pelajaran revisi model lama, `15_body_fit.py`).
- [ ] Selendang & kain bisa berayun lewat rantai tulang (Anim Dynamics, D5 docs/13).
- [ ] 9 socket sama dengan model lama (`hand_l/r`, `foot_l/r`, `chest_sun`, `eye_l/r`, `head_top`, `back_center`).
- [ ] Mata & permata dada **emissive konstan** (aturan IP), emas tidak terbaca silver.
- [ ] Lulus validator, uji 13 pose, checklist IP & budaya (bagian 7).
- [ ] Terpasang di UE sebagai `BP_Jayadwara2`, bisa dipilih sebagai pawn transformasi lewat skrip (bisa dibalik ke `BP_Jayadwara`).
- [ ] Developer menyatakan "ganti" setelah uji di `Test_GiantScale` (gate R1 dan R6).

## 2. Titik awal (12 Okt 2026)

| Item | Kondisi |
|---|---|
| Model lama | `Art/Blender/jayadwara_giant_v05_revisi.blend`, `Art/Export/SK_Jayadwara*.fbx` (LOD0 51,8k tris, 89 tulang, 4 slot material), UE `/Game/Jayadwara/Characters/Jayadwara/` (`SK_`, `SKEL_`, `PA_`, `IK_`, `RTG_`, `ABP_`, `BP_Jayadwara`). Dipakai `BP_JDPlayerController.giant_pawn_class` (transformasi tombol T) |
| Model baru | Belum diterima. Di `yahya_design/` sudah ada `jayadwara.glb` (4,3 MB, 12 Okt 23:15) — **belum dibuka**, menunggu konfirmasi developer bahwa itu file yang dimaksud |
| Pipeline yang bisa dipakai ulang | Impor Tripo (`jerangkong_01_import_tripo.py`), skeleton (`jd_skeleton.py`, sendi diukur dari mesh seperti `jk_skeleton.py`), export kontrak cm + bake 45 m (`05_export_fbx.py`, `16_make_lods.py`), validator (`validate_jayadwara.py`), render pembanding (`render_compare.py` + `compare_sheet.py`), skrip UE (`ue_import_jayadwara.py`, `ue_setup_retarget.py`, `ue_setup_giant.py`, `ue_setup_transform.py`) |
| Pelajaran dari Jerangkong jalur B | Tripo = 1 mesh menyatu, geometri lunak, detail di tekstur, ±13k tepi non-manifold, atlas tunggal 2048² yang melukis warna di tempat yang salah; capture editor UE kadang tidak men-tick animasi |
| Beda besar dengan Jerangkong | Jerangkong = potongan **kaku** tanpa skinning. Jayadwara = undersuit **ter-skin** + zirah kaku + kain berantai. Ini bagian paling berisiko (lihat R1) |

## 3. Keputusan (default yang direkomendasikan, menunggu developer)

| # | Keputusan | Default | Alasan |
|---|---|---|---|
| **R1** | Arah gaya | **Semi-realistis**: bentuk & detail dari Tripo (lebih realistis dari model lama), tetap PBR stylized-friendly, tanpa mengejar fotorealisme | `docs/README` mencatat "realistis penuh ditolak" (volume monster, animasi, performa). Model Tripo Jerangkong sudah berada di level ini, jadi Jayadwara2 + Jerangkong akan seragam. **Kalau developer mau realistis penuh, keputusan di README & [08](08-requirement-produksi.md) harus dibuka ulang dulu** |
| **R2** | Desain | **Sama dengan konsep final** (`jayadwara_final.webp`: merah-hitam-emas, faceplate putih, tanduk emas, permata dada, selendang batik) | Yang berubah tingkat detail, bukan identitas. Kalau desainnya berubah, kirim juga gambar acuan yang dipakai di Tripo supaya cek IP dilakukan di R0 |
| **R3** | Nama & lokasi | `jayadwara2_*` (skrip & `.blend`), objek `JD2_*`, `SK_Jayadwara2`, UE `/Game/Jayadwara/Characters/Jayadwara2/`, `BP_Jayadwara2` | Model lama tetap utuh; tidak ada file/aset lama yang ditimpa |
| **R4** | Skeleton | **Hierarki & nama sama** dengan `jd_skeleton.py`, tapi posisi sendi **diukur dari mesh baru** (pola `jk_skeleton.py`); skeleton UE terpisah (`SKEL_Jayadwara2`) + `IK_Jayadwara2` + `RTG_Mannequin_To_Jayadwara2` | Pose rest & proporsi baru pasti beda; skeleton terpisah sudah terbukti (docs/13 Iterasi 6) |
| **R5** | Skala | Tinggi authoring **1,90 m** (telapak → puncak helm tanpa tanduk), bake 45 m saat export; `AJDGiantCharacter::MeshHeightCm` tetap 4500 | Gameplay, kamera, dan gedung uji sudah dituning di 45 m |
| **R6** | Skinning | **Transfer bobot dari model lama** sebagai awal, lalu zirah dikunci ke 1 tulang per pelat (bobot kaku) berdasarkan segmentasi zona | Cara tercepat dapat bobot yang sudah teruji di 13 pose |
| **R7** | Pemisahan bagian | Pisahkan dari mesh Tripo: zirah per pelat (dada, punggung, bahu, bracer, paha/lutut, greaves), helm+tanduk, selendang, kain depan/belakang, undersuit. Bagian yang menempel dan tidak bisa dipisah rapi (umumnya selendang & jari) **dibangun ulang** dari skrip lama lalu diberi tekstur dari atlas | Selendang yang menempel ke paha tidak bisa berayun |
| **R8** | Material | **2 slot**: `MI_Jayadwara2_Body` (atlas Tripo) + `MI_Jayadwara2_Cloth` (two-sided), ditambah tekstur `Emit` (mata, permata) dan `Mask` zona warna (R merah, G emas, B hitam, A putih) yang diturunkan dari atlas | Atlas Tripo tunggal; mask tetap disiapkan untuk recolor Dwarapala Kala & Kembar (D9 docs/13) |
| **R9** | Anggaran poligon | LOD0 ≤ **100k** · LOD1 ≤ 30k · LOD2 ≤ 14k · LOD3 ≤ 6k (sama dengan model lama) | Kalau Tripo jauh di atas 100k, decimate per bagian dengan helm/faceplate dilindungi |
| **R10** | Pergantian di game | `Tools/ue_setup_jayadwara2.py` dengan flag `USE_JAYADWARA2`: `True` = `giant_pawn_class` → `BP_Jayadwara2`, `False` = kembali ke `BP_Jayadwara` | Bisa dibalik kapan saja tanpa menghapus aset |

## 4. Pembagian kerja

| Claude | Developer |
|---|---|
| Impor & normalisasi GLB, laporan kondisi mesh, render pembanding vs konsep & vs model lama | Membuat model di Tripo; konfirmasi lisensi komersial akun yang dipakai |
| Rig, segmentasi, transfer bobot, pembersihan, uji pose | Review visual tiap gate; memutuskan ganti / tidak |
| Tekstur turunan (Mask, Emit, perbaikan warna), material, LOD, export, validator | (Opsional) hand-paint & sculpt koreksi; Claude tidak menimpa hasil manual |
| Impor & setup UE lewat `Tools/ue_remote.py`, update docs | Uji main di `Test_GiantScale` (rasa, FPS, transformasi T) |

## 5. Iterasi

> Estimasi kasar; banyak tergantung kondisi mesh Tripo. Setiap gate menunggu review developer.

### R0 — Intake & penilaian *(±1–2 jam)*
- **Claude:**
  - Salin GLB ke `Art/Source/jayadwara_tripo_v01.glb` (sumber asli di `yahya_design/` tidak diubah).
  - `jayadwara2_01_import_tripo.py` (headless): rotasi menghadap -Y, skala ke tinggi R5, telapak di z=0, vertex jahitan UV digabung, tekstur di-pack → `Art/Blender/jayadwara2_v01_tripo.blend` (objek `JD2_Source`). Laporan: tris, vertex, material, ukuran tekstur, pulau mesh terpisah, tepi non-manifold, simetri kiri-kanan, bbox.
  - Render ortografis depan/samping/belakang + close-up kepala 3/4, berdampingan dengan **konsep** dan **model lama** (`render_compare.py` + `compare_sheet.py`); IoU siluet depan.
  - Cek IP awal (bagian 7) dan cek warna emas vs silver di atlas.
- **Developer:** jawab R1–R10 yang belum cocok; konfirmasi lisensi.
- **Gate:** sepakat model ini layak dilanjutkan; daftar perbaikan wajib (IP, proporsi, bagian menyatu) disetujui.

### R1 — Uji coba cepat (spike) *(±4–6 jam)*
Tujuan: membuktikan model bisa bergerak dengan layak **sebelum** investasi besar. Ini alur yang sudah disepakati developer: impor → transfer bobot → pose ekstrem → cek di UE → baru putuskan ganti.
- **Claude:**
  - Pasang skeleton R4 (sendi diukur dari mesh; landmark bahu, siku, pergelangan, pinggul, lutut, pergelangan kaki, leher).
  - Transfer bobot dari `jayadwara_giant_v05_revisi.blend` (Data Transfer, nearest face interpolated) setelah model lama dipas ke proporsi baru; tanpa pemisahan bagian dulu.
  - 13 pose uji yang sama dengan model lama (`03_pose_tests.py`) + `06_deform_check.py`; catat titik yang melentur parah (bahu, pinggul, lutut, pelat dada).
  - Export kasar (LOD0 saja) + impor ke UE sebagai `SK_Jayadwara2_Spike` di folder `Jayadwara2/`, retarget ABP, taruh di `Test_GiantScale` di samping model lama.
- **Developer:** lihat pose & jalan di UE.
- **Gate (Go/No-Go):** siluet dan deformasi "bisa dibereskan". No-Go → model lama tetap dipakai; temuan dicatat di sini untuk percobaan Tripo berikutnya (mis. minta pose-A, bagian terpisah).

### R2 — Pemisahan & pembersihan geometri *(±6–10 jam)*
- **Claude:** segmentasi zona (pola `jk_segment.py`: kapsul tulang terdekat + aturan wilayah + bidang potong) jadi bagian R7; tutup lubang potongan; bangun ulang selendang/kain/jari kalau menyatu; perbaiki simetri; buang non-manifold yang mengganggu bobot; perbaiki fit zirah (tanpa celah, tanpa punuk bahu, sabuk di pinggang); pastikan mata & permata punya geometri sendiri untuk emissive; perbaikan IP dari R0.
- **Gate:** render pembanding terasa "Jayadwara yang sama" dengan konsep; bagian siap di-rig.

### R3 — Rig final & skinning *(±5–8 jam)*
- **Claude:** pelat zirah bobot kaku (bahu blend `clavicle`+`upperarm` seperti model lama), undersuit hasil transfer + perataan, rantai `scarf_*`/`cloth_*`, twist, jari; 13 pose + `06_deform_check.py`; cek pose lengan terangkat (zirah & otot bergerak bersama).
- **Gate:** tidak ada pelat melentur/menembus mencolok di 13 pose; peregangan maksimum sebanding dengan model lama (±3 cm).

### R4 — Tekstur & material *(±4–6 jam)*
- **Claude:** UV dari Tripo dipertahankan (potongan cap diberi kotak warna netral di pojok atlas); atlas dibersihkan (warna di zona yang salah, silver → emas); turunkan `Mask` zona warna & `Emit`; `ORM`/`N` dari Tripo kalau ada; material preview Blender yang meniru parameter UE.
- **Developer:** hand-paint opsional.
- **Gate:** emas terbaca emas di bawah cahaya level uji; mata & permata menyala konstan; tidak ada noda warna salah.

### R5 — LOD, export & validasi *(±2–3 jam)*
- **Claude:** `jayadwara2_16_make_lods.py` (decimate per bagian, helm/faceplate/mata dilindungi), export kontrak cm + bake 45 m (`Armature`, `FBX_SCALE_ALL`, tanpa empty, socket ke JSON), `validate_jayadwara.py --materials 2 --max-tris ...` di keempat LOD.
- **Gate:** validator hijau di 4 LOD.

### R6 — Integrasi UE & keputusan ganti *(±3–5 jam)*
- **Claude:** generalisasi `ue_import_jayadwara.py` / `ue_setup_retarget.py` / `ue_setup_giant.py` dengan parameter nama (supaya satu skrip melayani `Jayadwara` dan `Jayadwara2`, bukan salinan); impor tekstur, master/MI, LOD, socket, PA, Anim Dynamics, `IK_`/`RTG_`/`ABP_Jayadwara2`, `BP_Jayadwara2`; `ue_setup_jayadwara2.py` (R10).
- **Developer:** main di `Test_GiantScale`: jalan, lari, transformasi T, kamera, 60 FPS, LOD tidak meloncat.
- **Gate:** developer bilang **ganti** → flag `USE_JAYADWARA2 = True`, docs diperbarui (README ringkasan gaya, 08, 13, 14 merujuk ke dokumen ini). Kalau belum, tetap pakai model lama tanpa kehilangan apa pun.

## 6. Risiko

| Risiko | Mitigasi |
|---|---|
| Mesh Tripo menyatu (selendang ke paha, jari ke telapak, lengan ke badan) | Minta developer generate dalam **pose-A/T, lengan menjauh dari badan, kaki terbuka, selendang tidak menempel**; kalau tetap menyatu, bangun ulang bagian itu (R7) |
| Zirah melentur karena mesh satu badan | Segmentasi zona + bobot kaku (R3); spike R1 membuktikan lebih dulu |
| Detail realistis di atlas tidak cocok dengan Aksa & lingkungan stylized | Keputusan R1; samakan pencahayaan di level uji; Aksa bisa menyusul ke arah yang sama di Iterasi 7-nya |
| Logam emas Tripo terbaca silver (aturan IP) | Cek di R0, perbaiki di atlas/material R4 |
| Desain baru menyerempet Ultra/Bima Satria | Checklist bagian 7 di R0, sebelum kerja rig |
| Topologi Tripo (segitiga acak, non-manifold) jelek untuk deformasi | Remesh/retopo terbatas di zona sendi (bahu, siku, pinggul, lutut) kalau R1 menunjukkan masalah |
| Waktu ±25–40 jam menggeser Fase 1 | Jalur art paralel; Fase 1 tetap memakai model lama sampai gate R6 |
| Pengungkapan konten AI | Steam mewajibkan pengungkapan konten buatan AI di formulir rilis (sama dengan Jerangkong) |

## 7. Checklist IP & budaya (sama dengan [13](13-rencana-model-jayadwara.md#8-checklist-ip--budaya-dipakai-di-setiap-gate), dipakai di R0, R2, R6)

- [ ] Tidak ada lampu/timer dada; permata dada statis (emissive konstan, tidak dikaitkan ke meter Sync).
- [ ] Dahi = relief emas berukir, bukan kristal/permata menyala.
- [ ] Tanduk melengkung dari sisi helm, bukan bilah kembar paralel di atas kepala.
- [ ] Mata = celah miring menyala, bukan lensa besar bulat.
- [ ] Faceplate putih dengan bentuk mulut/pipi jelas berbeda dari Ultra.
- [ ] Tidak ada silver/perak; tidak ada badan merah-silver; tidak ada emblem garuda.
- [ ] Batik motif umum, bukan batik larangan.

## 8. Saran untuk generate di Tripo (sebelum/ulang)

Supaya R1–R3 jauh lebih ringan:
- Gambar acuan **tampak depan, pose-A** (lengan ±30–45° dari badan, kaki selebar bahu), latar polos.
- Selendang & kain **menggantung lepas**, tidak melilit kaki; jari agak terbuka.
- Pilih opsi **quad/topologi rapi** dan tekstur PBR (BaseColor + Normal + Roughness/Metallic) kalau tersedia; resolusi tekstur 2048² atau lebih.
- Kalau bisa, generate **helm/kepala terpisah** dengan resolusi lebih tinggi (kepala krusial untuk estetika).

## 9. Status

| Iter | Status | Tanggal | Catatan |
|---|---|---|---|
| Persiapan | ✅ | 12 Okt 2026 | Dokumen ini + `jayadwara2_01_import_tripo.py` |
| R0 Intake | ✅ | 13 Okt 2026 | GLB bersih 37,7k tris, IoU konsep 0,83, tanpa silver |
| R1 Spike | ✅ Go | 13 Okt 2026 | Rig 89 tulang, terpasang di UE (`Test_GiantScale2`) |
| Revisi visual | ✅ disetujui | 13 Okt 2026 | Mata pita miring menyala (berhenti di batas merah), permata dada, postur tegak (`POSTURE_DEG`) |
| R2 Pemisahan | ✅ (dilanjutkan R3c–R3d) | 13 Okt 2026 | Lembar kain via ketebalan, zirah kaku |
| R4 Tekstur & material | ✅ | 13 Okt 2026 | Mask zona + recolor, preview Blender |
| R3 Rig final | ✅ disetujui developer di Play | 13 Okt 2026 | + R3b leher/wajah, R3c–R3d kaki & sayap (tanpa lubang, kinematik); regangan pose ekstrem (tendang 180°) tetap > target lama |
| R5 LOD | ✅ | 13 Okt 2026 | 37,7k / 18,8k / 8,7k / 3,8k, validator 27/27 ×4 |
| R6 Keputusan ganti | ✅ **Jayadwara2 dipakai** | 13 Okt 2026 | Transformasi (T) & `BP_JDGameMode_Giant` -> `BP_Jayadwara2`; model lama cadangan |

### Hasil R0 (13 Okt 2026) — `yahya_design/jayadwara.glb`

Sumber disalin ke `Art/Source/jayadwara_tripo_v01.glb` (asli tidak diubah). `Art/Scripts/jayadwara2_01_import_tripo.py` → `Art/Blender/jayadwara2_v01_tripo.blend` (`JD2_Source`); render: `jayadwara2_02_render_views.py` → `Art/Export/_jd2/`; ukur: `jayadwara2_03_measure.py`. Perbandingan konsep | model lama | model baru: `Art/Export/_jd2/_banding_front.png`.

| Temuan | Nilai | Akibat |
|---|---|---|
| Struktur | 1 mesh, 37.690 tris, 18.835 vertex, 1 material (BC/N/ORM 2048²), tanpa rig; 1 pulau, 32 tepi non-manifold (sangat bersih dibanding Jerangkong 13k) | Anggaran R9 (≤100k) terpenuhi tanpa decimate; LOD0 bisa langsung dipakai |
| Tinggi | Puncak tanduk 1,99 m; helm tanpa tanduk ±1,90 m | **Sama persis dengan model lama** (1,90 / 1,99) → `--top-z 1.99` benar, R5 tidak perlu skala ulang |
| Simetri kiri-kanan | median 0,4 cm, p95 1,2 cm | Bobot bisa dicerminkan |
| Siluet depan vs konsep (IoU, dinormalisasi bbox) | **0,83** (model lama 0,63) | Jauh lebih setia ke konsep |
| Warna | Merah-hitam-emas sesuai konsep; piksel abu/silver 0,08% (tidak ada silver); faceplate putih; permata dada menyala-merah terang di tekstur | Cek IP: lolos awal. Permata dada **dilukis di tekstur** (bukan geometri) → emissive via mask di R4 |
| Pose rest | **Bukan A-pose**: lengan turun di samping badan (celah lengan-badan ±9–10 cm di dada/perut, tinggal ±2 cm di bisep, tangan mengepal menempel kain di z≈0,75), kaki selebar bahu, kain sisi menutup paha | Bobot tangan/kain berisiko bocor ke paha/pinggul; retarget lengan harus disejajarkan ke A-pose Manny (cara Jerangkong) |
| Bagian-bagian | Menyatu semua: **kain depan = lembaran tipis** (nyaris tanpa ketebalan dari samping), **sayap kain sisi (= selendang, K5 docs/14) menempel ke pinggul/paha**, kain belakang menyatu dengan sayap, jari = **kepalan menyatu** | Jari kaku ikut `hand_*` (pola Jerangkong); sayap sisi → `scarf_l/r_01…06`, depan/belakang → `cloth_*`, perlu dipisah dari paha di R2 |
| Detail | Ornamen dada, pauldron, ukiran: dari tekstur + relief ringan; wajah faceplate putih lunak (kepala kurang tajam di close-up) | Cukup untuk kamera raksasa; kepala bisa diganti hi-res di Iterasi 7 |
| Atlas | UV terpakai 61%, tanpa tumpang tindih | Ruang kosong cukup untuk kotak cap potongan (R2) |

**Rekomendasi:** lanjut ke R1. Pertanyaan R1–R10 di bagian 3 tetap memakai default sampai developer menjawab.

### Hasil R1 (13 Okt 2026) — spike rig, sisi Blender

Artefak: `Art/Blender/jayadwara2_v02_rig_spike.blend` (`JD2_Body` + `JD2_Armature` 89 tulang + 9 socket), `Art/Export/SK_Jayadwara2.fbx` (LOD0, 37.690 tris, ter-bake ukuran 45 m), `SK_Jayadwara2_sockets.json`, `Textures_Jayadwara2/T_Jayadwara2_{BC,N,ORM}.png`. Validator `validate_jayadwara.py --max-tris 100000 --materials 1 --no-zone`: **27/27 PASS**. Bukti visual: 13 pose di `Art/Export/_jd2/poses/_sheet_q.png`, peta pembagian bagian `Art/Export/_jd2/_macro.png`.

Skrip: `jd2_skeleton.py` (nama & hierarki = model lama, sendi diukur dari mesh) → `jayadwara2_10_rig_spike.py` → `jayadwara2_13_pose_tests.py` (13 pose yang sama dengan model lama) → `jayadwara2_14_export.py`; bantu: `jayadwara2_11_macro_render.py`, `jayadwara2_04_uv_islands.py`.

**Temuan utama**

| Temuan | Detail | Akibat |
|---|---|---|
| Heat-map (automatic weights) gagal untuk mesh ini | Mesh satu pulau; kepalan menyentuh/menyatu dengan sayap kain & paha, lengan dengan rusuk → saat pose, "jembatan" antar bagian terentang jadi balok panjang (tepi >4 cm: ±1.100 per pose) | **Wajib memisahkan jahitan sentuh** sebelum memberi bobot |
| Solusi yang berhasil | Tiap segitiga diberi makro (HEAD/TORSO/ARM/LEG/WING/CLOTH) dari kapsul tulang terdekat + aturan sayap/kain; tepi antar makro yang tidak sah dipisah (split edge, 496 dari 56.535 tepi; vertex 18.835 → 19.390); bobot kapsul bertetangga dibatasi ke makronya | Tepi >4 cm turun ke 0–179 per pose (13 pose); lengan, bahu, tendangan tinggi, jongkok terbaca wajar |
| Bug yang ditemukan lewat peta makro | `SKIN_BONES` model lama tidak memuat `head`, `foot`, `ball` (bagian kaku) → di mesh satu badan kepala terbaca sebagai torso | Diperbaiki; harus jadi bagian R2 (segmentasi pakai tulang lengkap) |
| Pose rest | Lengan turun (bukan A-pose), jadi 13 pose (berbasis arah tulang) tetap bisa dipakai; sendi diukur dari render ortografis (lutut, pergelangan, pinggul cocok pada overlay) | Retarget di UE: ratakan lengan ke A-pose Manny seperti Jerangkong |
| Pulau UV Tripo | 163 pulau, dipotong per ketinggian (bukan per bagian) | Tidak bisa dipakai untuk segmentasi |
| Kain depan | Lembar vertikal lurus di y≈-0,218 (tebal 1,5 cm) | Ter-skin ke `cloth_front_*` |
| Panel kain belakang | **Tidak ada** di mesh (yang tampak di antara kaki dari belakang adalah kain depan) | `cloth_back_*` tetap ada di skeleton (kompatibel model lama) tanpa mesh; sayap sisi = `scarf_*` |

**Metrik 13 pose** (perubahan panjang tepi absolut maksimum / jumlah tepi >4 cm; model lama menargetkan ±3 cm maks): kuda-kuda 8,9 cm/36 · pukul 15,5/76 · tendang 19,5/120 · injak 23,8/128 · jongkok 14,8/146 · tangan atas 24,5/179 · raih depan 17,1/171 · tendang tinggi 26,2/156 · tangkis 6,5/31 · bungkuk 3,8/0 · putar badan 6,9/96 · tengok 9,1/39. Nilai terburuk berada di **sayap kain** (disimulasikan, bukan deformasi badan).

**Masalah yang tersisa untuk R2/R3** (belum dibereskan, sengaja):
1. **Sayap kain sobek/berserakan** saat tendang & jongkok: sayap hanya mengikuti `pelvis` dan tidak bertabrakan dengan paha; serpihan sayap yang tertinggal di bawah kepalan ikut lengan. → pisahkan sayap jadi bagian sendiri, tutup tepi, Anim Dynamics di UE.
2. **Retakan di sambungan lengan–torso (z < 1,4 m) dan paha–torso** karena split. Tersembunyi di pose rest, terlihat sedikit di pose ekstrem.
3. **Zirah belum kaku**: pelat dada, pauldron, bracer, greaves masih ikut bobot kapsul (melentur sedikit). → R3: bobot kaku per pelat.
4. Twist, jari kaku (kepalan menyatu), IK: tulang ada tetapi belum diberi bobot (twist bobot 0).

**Rekomendasi gate R1: GO.** Bisa dibereskan dengan pemisahan bagian (R2) dan bobot kaku (R3); tidak ada penghalang struktural. Langkah R1 yang tersisa: impor `SK_Jayadwara2.fbx` ke UE (`/Game/Jayadwara/Characters/Jayadwara2/`, butuh editor terbuka), retarget animasi Mannequin, letakkan di samping model lama di `Test_GiantScale` untuk dinilai developer.

#### R1 di UE (13 Okt 2026)

Skrip (semua nama baru; aset Jayadwara lama tidak disentuh): `Tools/ue_import_jayadwara2.py` → `Tools/ue_setup_jayadwara2.py` → (bukti visual) `Tools/ue_capture_jayadwara2.py`. Hasil di `/Game/Jayadwara/Characters/Jayadwara2/`:

| Aset | Isi |
|---|---|
| `Textures/` | `T_Jayadwara2_BC`, `_N` (flip green), `_ORM` |
| `Materials/` | `M_Jayadwara2_Master` (two-sided; parameter `MetallicScale` 0,35, `RoughnessMin` 0,55, `NormalStrength` 0,5) + `MI_Jayadwara2` |
| `Mesh/` | `SK_Jayadwara2` (LOD0 saja), `SKEL_Jayadwara2` (89 tulang), `PA_Jayadwara2` (20 body), 9 socket |
| `Rig/`, `Anims/` | `IK_Jayadwara2` (20 chain, auto), `RTG_Mannequin_To_Jayadwara2` (Run IK Rig mati), 25 aset `*_JD2` termasuk `ABP_Jayadwara2` (Control Rig foot IK dilepas; Anim Dynamics 3 rantai: `scarf_l/r`, `cloth_front`) |
| `BP_Jayadwara2` | Salinan `BP_Jayadwara` (kamera/input sama), mesh & ABP diganti; `BP_JDGameMode_Giant2` |
| `Maps/Test_GiantScale2` | Salinan `Test_GiantScale`; Play = Jayadwara2, Jayadwara lama (`JD_Lama`) berdiri 30 m di sisi |

Temuan UE:
- **Material mentah terlihat "basah"**: Tripo memberi emas metalik berkekasaran rendah (ORM: metalik rata-rata 0,15 tetapi emas ±0,9; kekasaran 0,16–0,91). Di UE memantulkan langit dan memperlihatkan permukaan bergelombang; merah terbaca oranye. Dengan skala metalik 0,35, kekasaran minimum 0,55, dan normal 50%, warna dan ukiran sesuai konsep. Nilai ini bisa diubah di `MI_Jayadwara2`.
- Skala sama dengan model lama (kepala sejajar di 45 m). Close-up kepala lembek (geometri Tripo lunak); cukup untuk kamera raksasa, perlu kepala hi-res untuk cutscene (Iterasi 7 docs/13).
- PIE: pawn `BP_Jayadwara2` ter-spawn dengan `ABP_Jayadwara2` dan mesh yang benar; tampak belakang berdiri tegak, sayap kain terbawa. **Animasi gerak belum diuji**: animasi tidak ter-tick saat PIE dikendalikan dari jauh, jadi uji jalan/lari/serangan dilakukan developer (Play di `Test_GiantScale2`).
- Bukti visual: `Art/Export/_jd2/_ue_berdampingan.png` (lama | baru), `_ue_baru_depan.png`, `_ue_baru_kepala.png`, `_ue_pie_belakang.png`.

#### Revisi 1 (13 Okt 2026, umpan balik developer: "mata & diamond dada menyala, jangan terlalu bungkuk, kepala lebih tegas")

**Cahaya (Emit).** `make_textures_jayadwara2.py` (butuh `jayadwara2_15_dump_uv.py`) membuat `T_Jayadwara2_Emit`: tiap texel atlas diberi posisi 3D (rasterisasi segitiga di ruang UV), lalu hanya texel TERANG di zona yang menyala. R = berlian dada (|x|<3,5 cm, z 1,40–1,50 m; 625 texel), G = lobus krem di bawah alis emas yang menjadi "mata" (|x|<8,5 cm, z 1,715–1,775 m; 411 texel). Material: Emissive = (`Gem_Color` #FFC86B × R + `Eye_Color` #FFF1C8 × G) × `Emissive_Intensity` 3,0, nilai sama dengan Jayadwara lama. **Konstan**, tidak dikaitkan ke meter Sync (aturan IP). Catatan: mesh Tripo tidak punya celah mata bergeometri; yang menyala adalah lukisan lobus krem, bukan celah miring seperti model lama (K-IP: "mata = celah miring menyala"). Bila ingin celah miring sungguhan, perlu digambar ulang di tekstur (R4) atau mata dimodel terpisah.

**Postur.** Diukur di UE (`MM_Idle` hasil retarget, kepala − pinggul): auto-align chain-to-chain memutar `spine_01` −12,9° dan `neck_01` −23,2° (sumbu X lokal pada pose retarget target), sehingga idle Manny + badan Tripo yang sudah condong = kepala maju **29 cm (±10°)** dari pinggul. Model lama punya idle yang sama (sama-sama maju 29 cm) tetapi badannya lebih tegak; Tripo menambah condong sendiri. Perbaikan di `ue_setup_jayadwara2.py` (`POSTURE_DEG`): pose retarget `spine_01` −3,5° dan `neck_01` −12°. Hasil: kepala (6, 1, 1670) cm → **condong 0,0°**, dagu sedikit terangkat. Ubah `POSTURE_DEG` lalu jalankan ulang setup bila terlalu kaku/tegak (selisih: spine_01 24,5 cm per derajat pada tinggi 45 m). Pelajaran: `set_rotation_offset_for_retarget_pose_bone` tidak selalu bisa dikembalikan dengan kuaternion identitas (bone tetangga ikut berubah) → selalu bangun ulang RTG dari awal (setup melakukannya).

**Sisa:** bercak hitam di paha/lutut dan serpihan kain di pose bergerak (jahitan split R1) → R2.

Bukti: `Art/Export/_jd2/_ue_pie_depan_v2.png`, `_ue_pie_samping_v2.png`, `_emit_debug.png`.

#### Revisi 2 (13 Okt 2026, umpan balik: "mata masih jelek, ingin menyala seperti Jayadwara lama; dari samping badan bungkuk ke belakang, tidak proporsional")

**Mata.** Lobus krem yang menyala ternyata jelek. `make_textures_jayadwara2.py` kini MELUKIS celah miring pada atlas: dua celah meruncing (ujung dalam rendah → ujung luar naik, tatapan tegas; setengah tebal 6,5 mm → 1,8 mm), soket gelap 1,4 cm di sekelilingnya pada BC, dan inti celah di `T_Jayadwara2_Emit` G (542 texel). Atlas asli Tripo disimpan sebagai `T_Jayadwara2_BC_src.png` (sumber; skrip membaca darinya, `T_Jayadwara2_BC.png` = hasil lukis). Mata = celah miring (sesuai checklist IP), bukan lensa bulat.

**Postur (diagnosis ulang).** Mengukur posisi kepala saja (revisi 1) menyembunyikan kurva S: segmen [pinggul>dada, dada bawah>atas, dada>leher, leher>kepala] = [5,3°, −6,1°, −2,5°, 5,7°] (dada atas condong belakang). Idle Manny sendiri: [12,4°, 3,2°, 7,6°, 23,9°], lutut tertekuk (paha kiri 16° dari vertikal), satu kaki 3,5 m di depan; auto-align meniru semuanya. Pada proporsi Tripo (paha pendek, betis panjang) pinggul mundur + lutut tekuk membuat dada tampak melengkung ke belakang. Koreksi di `ue_setup_jayadwara2.py` (`POSTURE_DEG`, 11 tulang, **harus diset lengkap & berurutan** — `set_rotation_offset_for_retarget_pose_bone` tidak independen antar tetangga dan auto-align meninggalkan sisa offset di tulang lain), dicari dengan Gauss-Newton atas ukuran nyata (idle hasil retarget):
- tulang belakang → segmen [4°, 2°, 2°, 8°] (kepala maju ±95 cm pada 45 m, condong 3,2°);
- kaki → paha>betis L/R 4,1°/0,0°, betis>telapak 0,9°/1,1°, tinggi pergelangan 354/301 cm (target 332).
`ue_setup_jayadwara2.py` mencetak segmen ini sebagai laporan setiap dijalankan; ubah `POSTURE_DEG` lalu jalankan ulang bila ingin lebih membungkuk/lurus.

Bukti: `Art/Export/_jd2/_ue_pie_{depan,samping,belakang,kepala}_v3.png`. **Catatan:** animasi gerak (jalan/lari/serang) tetap belum diuji; kaki kiri-kanan tidak simetris karena idle Manny (kaki kiri di depan).

#### Revisi 3 (13 Okt 2026): mata lebih lebar
Celah revisi 2 (setengah tebal 6,5→1,8 mm) hanya mengisi sebagian kecil area mata; Jayadwara lama memakai pita putih lebar di bawah alis. Sekarang pita mata (`make_textures_jayadwara2.py`): ujung dalam (2,0 cm, z 1,733 m) → ujung luar (9,0 cm, z 1,757 m), setengah tebal 10,5 → 6,5 mm (±2,1 cm penuh), bingkai gelap 6 mm, tepi anti-alias per texel (≈3 mm) + blur 0,8 → 1.004 texel. `_face_proj.png` = proyeksi depan zona wajah (atlas asli | hasil) untuk menyetel bentuk. Bukti: `Art/Export/_jd2/_ue_kepala_v4.png`, `_ue_mata_v4.png`. Catatan: kerapatan texel di wajah rendah (±3 texel/cm), tepi bergerigi hanya tampak pada close-up ekstrem; untuk cutscene perlu kepala hi-res (Iterasi 7).

#### Revisi 4–5 (13 Okt 2026): bentuk & panjang mata
Umpan balik: mata harus memanjang sedikit ke belakang seperti Jayadwara lama, bukan melebar/blok; **panjang maksimum = batas area silver (krem/putih) dengan area merah**. Pita mata (`make_textures_jayadwara2.py`): (2,2 cm; z 1,727) → (10,2 cm; z 1,769), setengah tebal 11,5 mm meruncing ke ujung (eksponen 0,65), lalu **dipotong di area merah** menurut warna asli atlas Tripo (`redness = R − max(G,B)`, ambang 0,12–0,28; berlaku juga untuk bingkai gelap) → 1.432 texel. Warna: intensitas mata = `Emissive_Intensity` × `Eye_Scale` 0,45 (intensitas 3,0 membakar krem #FFF1C8 jadi putih; permata tetap 3,0). Bukti: `Art/Export/_jd2/_ue_kepala_v5.png`.

### Hasil R2 (13 Okt 2026) — pemisahan lembar kain, zirah kaku

Skrip baru `jayadwara2_21_rig_r2.py` (menggantikan `jayadwara2_10_rig_spike.py` yang tetap disimpan) → `Art/Blender/jayadwara2_v03_rig_r2.blend` (v02 spike tetap utuh). Pipeline: `21` → `13_pose_tests` → `14_export` → `15_dump_uv` → `make_textures_jayadwara2.py` → `ue_import_jayadwara2.py` → `ue_setup_jayadwara2.py`. FBX R1 diamankan sebagai `Art/Export/SK_Jayadwara2_R1spike.fbx`.

| Masalah R1 | Penyebab | Perbaikan R2 |
|---|---|---|
| Sayap kain sobek jadi serpihan saat kaki melebar; bercak hitam di paha | Lembar tipis sayap **menempel pada paha**; kapsul tulang membagi lembar itu ke kelas kaki dan sayap, jadi sebagian ikut kaki, sebagian tidak | **Ketebalan lokal**: ray cast ±normal (maks 15 cm) per vertex → lembar tipis (< 3 cm) = 5.358 vertex, jelas terpisah dari volume (peta `Art/Export/_jd2/_thick.png`). Segitiga dengan ≥ 2 vertex tipis di zona pinggul-paha menjadi makro WING/CLOTH utuh (sayap 2.6k segitiga per sisi, sebelumnya ~0,5k); jahitan ke paha/lengan dipisah (746 tepi) |
| Serpihan merah kecil melayang di dekat kepalan saat tangan terangkat | Sliver sisa split jahitan | Pulau mesh < 30 segitiga dibuang (55 pulau, 252 segitiga) |
| Zirah melentur | Bobot kapsul lunak di sendi | Vertex terang pada atlas (luminans > 0,17: emas/merah/putih = zirah, 65%) dipertajam: anggota badan w³ (dinormalisasi); pelat dada/punggung/sabuk kaku ke `pelvis`/`spine_04`/`spine_05` menurut ketinggian; helm kaku ke `head`. Bodysuit hitam tetap lunak |

Metrik 13 pose (maks perubahan panjang tepi cm / tepi > 4 cm): kuda-kuda 8,6/38 · pukul 14,4/90 · tendang 20,3/138 · injak 24,9/202 · jongkok 14,2/178 · tangan atas 22,8/180 · raih depan 16,3/163 · tendang tinggi 27,4/175 · tangkis 5,9/31 · bungkuk 8,1/86 · putar badan 10,0/151 · tengok 9,1/39. **Catatan:** jumlah tepi > 4 cm sedikit naik dibanding R1 (penajaman memusatkan regangan di zona sendi sempit) dan sebagian besar berada di lembar kain; pengukuran ini mencakup seluruh mesh. Penilaian akhir ada pada visual 13 pose (`Art/Export/_jd2/poses_r2/_sheet_q.png`) dan idle di UE (`_ue_r2_depan.png`, `_ue_r2_samping.png`): sayap utuh dengan tepi bersih, tidak ada serpihan melayang, bercak hitam di paha jauh berkurang.

Validator `SK_Jayadwara2.fbx` (37.438 tris): **27/27**. UE: impor ulang + setup (postur & mata dipertahankan), `Test_GiantScale2` diperbarui.

**Belum / sisa untuk R3:**
- Sayap hanya mengikuti `pelvis` + Anim Dynamics di UE; saat tendang/jongkok sayap menembus kaki (Anim Dynamics punya bola penolak di paha/betis; perlu dituning di PIE).
- Bobot twist (`*_twist_01`) dan jari masih 0 (kepalan menyatu ikut `hand_*`).
- Pelat dada dibuat kaku ke tulang tunggal; sambungan ke bodysuit abdomen (hitam, lunak) belum dihaluskan di pose bungkuk/putar ekstrem.
- Retakan kecil di sambungan lengan–torso (z < 1,4 m) dan paha–torso hasil split tetap ada (tersembunyi di pose rest).
- Tepi sayap tidak ditutup (lembar terbuka, material two-sided).

### Hasil R4 (13 Okt 2026) — tekstur & material (dikerjakan sebelum R3)

Modul/skrip: `jd2_atlas.py` (posisi 3D per texel + klasifikasi zona HSV), `analyze_atlas_jayadwara2.py`, `make_textures_jayadwara2.py` (BC, Emit, Mask), `jayadwara2_30_materials.py` (preview Blender), `Tools/ue_import_jayadwara2.py` (material). Hasil UV Tripo dipertahankan (tanpa UV baru; sehingga hand-paint developer tetap bisa di atlas yang sama).

**Analisis atlas (`_atlas_zones.png`).** 2048², 61% terpakai. Zona (HSV sRGB): merah 52,9%, hitam 30,9%, emas 15,5%, putih/krem 0,1% (faceplate), "lain" 0,5%. **Atlas bersih**: 0 texel hijau/biru/ungu; "lain" hanya texel peralihan emas↔merah di tepi (13.243, di-snap ke warna tetangga valid terdekat) dan 139 texel abu di sekitar wajah/leher (bukan silver permukaan zirah). Guratan hijau yang kulihat di close-up Blender awal ternyata artefak render, tidak ada di tekstur. Jadi "atlas dibersihkan" = snap peralihan; tidak ada silver/noda warna yang perlu diganti emas (gate IP terpenuhi sejak R0).

**Mask zona (`T_Jayadwara2_Mask`).** RGBA = merah, emas, hitam, putih/krem; diturunkan dari BC FINAL (termasuk soket & celah mata), tepi dilembutkan (blur 1,2 px) dan dinormalisasi (jumlah = 1). `T_Jayadwara2_Mask.json` menyimpan luminans linear referensi dan warna rata-rata per zona: merah 53% (0,056), emas 15,7% (0,223), hitam 31,2% (0,011), putih 0,2% (0,534).

**Material UE (`M_Jayadwara2_Master`).** Parameter per zona `Zone_<merah|emas|hitam|putih>_Color` dan `_Amount` (bawaan 0 = warna asli, tampilan baku tidak berubah). Rumus: `target = Zone_Color × luma(BC)/RefLuma` (mempertahankan ukiran/tekstur), `lerp(BC, target, Amount)`, dijumlah menurut Mask. Emissive (permata, mata) tidak ikut recolor. `MI_Jayadwara2_TesWarna` (uji, bukan untuk game): merah → ungu, hitam → biru-kelam, emas & putih tetap, mata & permata tetap menyala (`Art/Export/_jd2/_ue_r4_tes_warna.png`). Dipakai nanti untuk Dwarapala Kala/Kembar (D9 docs/13).

**Preview Blender (`jayadwara2_v04_tex.blend`, file kerja R4).** Material `M_Jayadwara2` meniru UE: BC×AO, metalik×0,35, kekasaran min 0,55, normal 50%, emissive konstan; render EEVEE `_bl_depan.png`, `_bl_kepala.png` cocok dengan UE.

**Gate R4:** emas terbaca emas, mata & permata menyala konstan, tidak ada noda warna salah ✅. **Catatan:** kerapatan texel wajah rendah (±3 texel/cm), close-up cutscene tetap butuh kepala hi-res (Iterasi 7 docs/13); developer boleh hand-paint BC (`T_Jayadwara2_BC_src.png` = sumber, jangan timpa BC hasil lukis tanpa menjalankan ulang `make_textures_jayadwara2.py`).

### Hasil R3 (13 Okt 2026) — rig final & skinning

Skrip `jayadwara2_22_rig_r3.py` (R2 + 3 perubahan) → `Art/Blender/jayadwara2_v05_rig_r3.blend`; FBX R2 diamankan `SK_Jayadwara2_R2.fbx`; terpasang di UE (validator 27/27, import + setup diulang, idle dan postur tetap sesuai target).

| Perubahan | Isi |
|---|---|
| Bobot twist | Vertex bodysuit (bukan zirah) di paruh distal segmen `upperarm/lowerarm/thigh/calf` mengalihkan hingga 60% bobotnya ke tulang `*_twist_01` (2.723 vertex) |
| Sayap/kain ikut paha | Sayap sisi ikut `thigh` hingga 55% di ujung (rantai `scarf` mengurangi), kain depan ikut kedua paha hingga 50% di ujung bawah (3.333 vertex). Pada tendangan/langkah lebar sayap & kain terbawa paha, tidak lagi menembus; sisa pergerakan bebas diserahkan ke Anim Dynamics di UE |
| Zona sendi dilunakkan | Penajaman zirah (R2) dimatikan di radius sendi: pinggul 17 cm, bahu 20 cm, lutut/siku 9 cm, pergelangan 8 cm (6.428 vertex; pelat torso kaku juga dilunakkan di pinggul/bahu 4.561). Menurunkan robekan pelat torso ↔ paha pada tendangan |
| Jari | Tetap kaku ikut `hand_*` (kepalan menyatu; 30 tulang jari ada untuk retarget) |
| Metrik | `jayadwara2_13_pose_tests.py` kini memisahkan regangan **badan** vs **kain** (tabel di bawah) |

Metrik 13 pose, R3 (badan: maks perubahan panjang tepi cm / tepi > 4 cm | kain: maks cm / tepi > 4 cm): kuda-kuda 8,9/35 | 2,8/0 · pukul 15,5/91 | 4,5/2 · tendang 19,7/133 | 7,0/15 · injak 24,1/203 | 9,2/25 · jongkok 14,8/179 | 3,6/0 · tangan atas 24,5/177 | 0/0 · raih depan 17,1/171 | 0/0 · tendang tinggi 26,5/183 | 10,5/39 · tangkis 6,4/31 | 0/0 · bungkuk 8,1/86 | 2,8/0 · putar badan 10,0/160 | 7,2/3 · tengok 9,1/38 | 0/0.

**Temuan.**
1. Regangan terbesar ada di **badan** (bukan kain), terpusat di sambungan pinggul ↔ paha (z 0,76–1,0 m; 27+17+11 dari 83 tepi > 8 cm pada tendang tinggi) dan sedikit di bahu ↔ torso. Di sana pelat torso (kaku ke pinggul) bertemu pelat paha: sambungan geometri asli Tripo tanpa celah gerak. Zona sendi yang dilunakkan hanya menurunkan tepi > 8 cm pada tendang tinggi 81 → 69; tidak menghilangkan.
2. **Tulang twist tidak digerakkan** animasi hasil retarget (rotasi lokal terhadap pose rest = 0,0° pada Attack_01/02 dan Idle). Twist bukan chain IK Rig dan twist Manny tidak ada di animasinya (di Manny asli dijalankan runtime oleh Control Rig). Bobot twist siap, tetapi baru berefek setelah ABP memuat koreksi twist (mis. node Transform Modify Bone: `lowerarm_twist_01` = 50% roll `hand`). Sampai itu, tulang twist ikut induknya (tak merugikan).
3. Efek Anim Dynamics pada sayap/kain dengan bobot paha baru **belum diverifikasi**: animasi tidak ter-tick saat PIE dikendalikan dari jauh; perlu dilihat developer saat Play (tinju, tendang, lompat).

**Gate R3** ("tidak ada pelat melentur/menembus mencolok di 13 pose; peregangan maksimum sebanding model lama ±3 cm"): **belum tercapai pada pose ekstrem** — maks 5,9–27 cm per tepi (tendang tinggi, injak, tangan atas terbesar). Pada pose gerak harian (kuda-kuda 9, tangkis 6, bungkuk 8, tengok 9 cm) mendekati batas. Perlu keputusan developer apakah pose ekstrem itu relevan: animasi Mannequin/Mixamo untuk Fase 1 umumnya tidak seekstrem 13 pose uji (tendang tinggi 180°, tangan di atas kepala). Jalan keluar bila tidak: retopo terbatas di zona pinggul/bahu (pisahkan pelat torso dari paha dengan celah gerak) — di luar R3.

### Hasil R5 (13 Okt 2026) — LOD, export & validasi

`Art/Scripts/jayadwara2_16_make_lods.py` (headless, dari `jayadwara2_v05_rig_r3.blend`; scene tidak disimpan). Per LOD: salinan `JD2_Body`, Armature dilepas, Decimate COLLAPSE dengan grup `LODPROTECT` (kepala depan z > 1,70 m & permata dada: 680 vertex) lalu bobot dibersihkan (≤ 4 influence, dinormalisasi), vertex lepas dibuang, Armature dipasang lagi, diekspor lewat `jayadwara2_14_export.py` (kontrak sama: `Armature`, cm, bake 45 m, tanpa empty).

| LOD | Rasio | Tris | Anggaran R9 | Vertex render di UE | Layar |
|---|---|---|---|---|---|
| 0 | 1,00 | 37.438 | ≤ 100k | 23.101 | 1,0 |
| 1 | 0,50 | 18.719 | ≤ 30k | 12.935 | 0,5 |
| 2 | 0,23 | 8.609 | ≤ 14k | 7.070 | 0,25 |
| 3 | 0,10 | 3.742 | ≤ 6k | 3.575 | 0,12 |

- **Validator** (`--materials 1 --no-zone --max-tris <anggaran>`): `SK_Jayadwara2.fbx`, `_LOD1`, `_LOD2`, `_LOD3` → **27/27 PASS** semuanya.
- **UE:** `ue_import_jayadwara2.py` kini mengimpor LOD1–3 (`SkeletalMeshEditorSubsystem.import_lod`) dan memasang ukuran layar; hasil 4 LOD terverifikasi (`get_num_verts`). Setup (`ue_setup_jayadwara2.py`) diulang setelah impor. Perbandingan Blender: `Art/Export/_jd2/_lod_depan.png`, `_lod_kepala.png`; UE (LOD dipaksa): `_ue_r5_lod.png`. Siluet, kepala, permata & mata terjaga di keempat LOD; LOD3 sedikit lebih bersudut (wajar untuk jarak jauh).
- **Pelajaran 1:** `Decimate` dengan `vertex_group` memakai bobot 1 = DIDECIMATE dan 0 = dilindungi (tak berbobot = terlindungi), sehingga tanpa `invert_vertex_group` hampir tak ada yang berkurang (36.110 tris di semua rasio).
- **Pelajaran 2:** capture editor tepat setelah impor menampilkan tekstur blur (mip rendah, tampak "basah" oranye) sampai streaming selesai; paksa dengan `r.Streaming.FullyLoadUsedTextures 1` + `Streaming.FlushResourceStreaming` dan beri jeda ±20 detik sebelum memotret.
- **Pelajaran 3:** skrip UE tidak dapat bekerja bila editor sedang Play ("The Editor is currently in a play mode": semua pencarian aset mengembalikan 0, tidak ada yang rusak); pastikan PIE berhenti sebelum impor.
- **Belum:** uji FPS (1 Jayadwara2 + banyak minion) dan tuning layar LOD di `Test_GiantScale2` oleh developer; LOD tidak mengubah Physics Asset atau Anim Dynamics.

#### Perbaikan R3b (13 Okt 2026): "wajah meleh saat melompat"

Laporan developer: saat melompat dll wajah tampak meleh (seharusnya kaku). Diagnosis (semua terukur, bukan tebakan):
- Animasi lompat/jatuh/mendarat hasil retarget normal: tanpa skala/translasi menyimpang, rotasi kepala maks 25° (`MM_Jump_JD2`), leher 12°.
- Bobot helm sudah kaku (z > 1,72 m: `head` ≈ 1,0) dan LOD tidak berpengaruh (close-up kepala LOD0–3 identik di UE).
- **Penyebab:** leher/kerah (z 1,50–1,64) berbobot 100% `spine_05` (makro TORSO; kapsul `spine_05` r = 0,24 mengalahkan `neck_*`; bobot tulang leher = 0,00 di seluruh mesh), dan dagu depan z 1,64–1,68 setengahnya ikut torso (rata-rata bobot `head` 0,58). Kepala berputar membawa helm, sementara dagu dan leher tertinggal di torso → wajah robek/meleh di sambungan itu. Tidak tertangkap di 13 pose uji karena hanya ada satu pose menoleh dan tidak ada kepala mendongak/menunduk besar.
- **Perbaikan** (`jayadwara2_22_rig_r3.py`): (a) leher (|x| < 12 cm, y > −10 cm, z 1,50–1,70 m; 581 vertex) diinterpolasi menurut tinggi `spine_05` → `neck_01` (1,56) → `neck_02` (1,61) → `head` (1,66); (b) wajah depan/dagu (y < −9 cm, z ≥ 1,62 m; 60 vertex) kaku 100% ke `head`. Uji: kepala dimiringkan 36° total (leher 8° + 6° + kepala 22°), perbandingan sebelum/sesudah `Art/Export/_jd2/_r3b_leher_banding.png`: sebelum, dagu merah menonjol terpisah dari leher; sesudah, kepala dan dagu satu kesatuan dengan leher menekuk mulus. LOD1–3 dan semua FBX dibuat ulang, validator 27/27 ×4, UE diimpor ulang dan setup diulang.
- **Pelajaran:** bobot kapsul dengan radius besar bisa membuat tulang kecil (leher) tak pernah menang; selalu periksa distribusi bobot per tulang (mis. total bobot tiap tulang), bukan hanya "tak ada vertex tanpa bobot". Tambahkan uji kepala miring besar ke daftar pose uji (R3).

#### Perbaikan R3c (13 Okt 2026): "kaki dan selendang berantakan dan keropos" saat berjalan

Laporan developer (tangkapan Play: sayap/kain pecah jadi serpihan merah yang menggantung, paha berlubang hitam). **Direproduksi di Blender** dengan pose langkah jalan (paha kiri maju 28°, kanan mundur 18°, lutut kanan 30°; `jayadwara2_17_walk_head_tests.py`) — persis tampilan UE. Tidak tertangkap oleh 13 pose uji (tidak ada langkah jalan biasa).
- **Penyebab:** lembar sayap menyelip dengan kulit paha pada mesh Tripo (satu cangkang). Aturan R2 "lembar tipis → bagian kain, sisanya → kaki" memecah sambungan sayap–paha (241+227 tepi dipisah) dan membuat label WING dan LEG berselang-seling di zona yang sama (peta makro `_macro_r3.png`: sayap magenta bercampur tungkai pada tampak samping). Saat paha berayun, potongan kaki dan potongan sayap bergerak berbeda → serpihan dan lubang yang memperlihatkan bodysuit hitam.
- **Perbaikan** (`jayadwara2_22_rig_r3.py`): (1) sayap–kaki **tidak dipisah** lagi (tepi dipisah 746 → 278); (2) bobot sayap **kontinu menurut jarak ke kaki**: pada kulit paha (jarak ≤ 0) ikut paha/betis/pinggul 100%, naik linear sampai 10 cm di luar kulit (`WING_BLEND_R`) tempat ia sepenuhnya ikut rantai `scarf_*` (Anim Dynamics di UE); pengikut-paha lama (55% per-ketinggian) dihapus untuk sayap; kain depan tetap memakai pengikut-paha 50%.
- **Hasil:** pose langkah (`_walk_r3c.png`): sayap & kain mengalir sebagai lembar utuh, paha tanpa lubang. LOD1–3 dan semua FBX dibuat ulang (validator 27/27 ×4), UE diimpor ulang + setup diulang.
- **Catatan:** ujung bawah sayap (jauh dari kaki, bobot penuh rantai) tinggal di posisi rest di Blender (rantai tidak disimulasikan di sana); di UE digerakkan Anim Dynamics, belum terverifikasi karena animasi tidak ter-tick saat PIE dikendalikan dari jauh (editor di latar belakang dibatasi ±3 fps; `EditorPerformanceSettings` tidak terbuka ke Python). Developer perlu melihatnya saat Play.

#### Perbaikan R3d (13 Okt 2026): kaki berlubang/keropos & sayap terlempar (laporan Play kedua)

Laporan: sayap terlempar keluar seperti ekor, kaki berlubang bergerigi (terlihat dari bawah), pinggir paha berserabut. Perbaikan R3c sebelumnya hanya diverifikasi pada satu pose jalan dari jauh; itu tidak cukup.
- **Audit baru** `jayadwara2_18_motion_audit.py`: rest, jalan (2 fase), lompat (lutut ditarik, badan terangkat), mendarat (jongkok dalam), langkah lebar; kamera samping, belakang 3/4, depan 3/4, dan **bawah**; mencetak jumlah tepi terbuka dan regangan badan vs kain.
- **Penyebab 1 (lubang/keropos):** rig menghasilkan **440 tepi terbuka** (sumber Tripo hanya 16) dari pemisahan jahitan antar-bagian dan penghapusan pulau kecil. Sambungan yang dipisah merenggang jadi lubang bergerigi saat bergerak.
- **Penyebab 2 (sayap terlempar):** rantai Anim Dynamics pada sayap (tulang `scarf_*`) di UE.
- **Perbaikan** (`jayadwara2_22_rig_r3.py`): (a) semua sambungan dipertahankan kecuali lengan ↔ selain torso-bahu dan kiri ↔ kanan (pemisahan 746 → 48 tepi, semuanya lengan–torso di bawah bahu); (b) pulau tidak lagi dihapus; (c) sebelum memisah, komponen label kecil (< 40 segitiga, mis. secuil sayap terlabel lengan) diberi label tetangga mayoritas (87 komponen) — menghilangkan serpihan melayang; (d) sayap & kain depan **kinematik**: dekat kulit paha ikut paha 100%, makin jauh/ke bawah campuran pinggul → paha (ujung sayap 55% paha, kain depan 50% dibagi kedua paha); (e) `ue_setup_jayadwara2.py`: tanpa node Anim Dynamics.
- **Hasil audit:** tepi terbuka 440 → 112 (16 sumber + 96 dari kontak lengan); regangan kain > 8 cm = 0 di semua pose audit; visual (`Art/Export/_jd2/audit_r3e/_sheet.png`): tidak ada lubang, serpihan, atau lembar pecah pada jalan, lompat, mendarat, langkah lebar, termasuk dari bawah; 13 pose uji lengan bersih (`poses_r3e/_arms.png`). Regangan badan > 8 cm naik pada lompat/mendarat (34/46 tepi, pinggul/selangkangan) karena tak lagi dipisah — tampil sebagai lipatan, bukan lubang.
- **Konsekuensi desain:** sayap tidak lagi berayun bebas (tanpa simulasi). Bila nanti ingin ayunan, tambahkan AD dengan batas kecil di atas bobot kinematik ini, bukan menggantikannya.

### Hasil R6 (13 Okt 2026) — keputusan: Jayadwara2 dipakai

Developer memilih Jayadwara2 setelah menilai di Play (jalan, lompat; kaki & sayap "sudah bagus, sudah OKE").
- `Tools/ue_setup_transform.py`: pilihan model lewat `ACTIVE_GIANT` (`"Jayadwara2"` aktif; `"Jayadwara"` = kembali ke model lama). Mengisi `BP_JDPlayerController.giant_pawn_class` (transformasi tombol T) dan `BP_JDGameMode_Giant.default_pawn_class` (level `Test_GiantScale`) dengan `BP_Jayadwara2`.
- **Diuji:** PIE di `Test_Greybox`, `ToggleTransformation` dipanggil seperti tombol T: pawn `BP_Aksa` → `BP_Jayadwara2` dengan mesh `SK_Jayadwara2` ✅.
- **Model lama tidak dihapus**: `.blend`, FBX, dan aset UE `/Game/Jayadwara/Characters/Jayadwara/` utuh; `Test_GiantScale2` tetap menampilkan keduanya berdampingan.
- Docs diperbarui: `README` (wujud raksasa & gaya visual), [13](13-rencana-model-jayadwara.md) (status cadangan + cara kembali), [14](14-model-sheet-jayadwara.md) (identitas desain tetap berlaku).

**Sisa untuk fase berikutnya (bukan penghalang):** combat raksasa (F1 Iterasi 6) belum bisa diuji; lipatan pinggul di pose sangat ekstrem; sayap tanpa ayunan bebas (bisa ditambah AD berbatas kecil); kepala hi-res untuk cutscene (Iterasi 7 docs/13); recolor Dwarapala Kala/Kembar lewat `Zone_*` (siap); tuning layar LOD & uji FPS di level nyata.
