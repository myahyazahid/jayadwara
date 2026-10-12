# 25 — Rencana Redesign Jayadwara (Model Tripo Realistis)

> **Status: v0.1 — persiapan (12 Okt 2026).** Model `.glb` dari developer belum diterima; rencana ini disiapkan supaya begitu file masuk, Iterasi R0 bisa langsung jalan. Semua keputusan di bagian 3 masih **usulan** sampai dijawab developer.
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
| Persiapan | ✅ | 12 Okt 2026 | Dokumen ini + `Art/Scripts/jayadwara2_01_import_tripo.py` (diuji kering ke GLB Jerangkong, keluaran di luar repo) |
| R0 | ⬜ | | Menunggu GLB dari developer |
| R1–R6 | ⬜ | | |
