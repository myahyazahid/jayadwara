# 13 — Rencana Implementasi: Model Jayadwara (Wujud Raksasa)

> Draft v0.1 — 11 Oktober 2026. Rencana membuat model 3D Jayadwara di **Blender 5.2** (dibantu Claude lewat Blender MCP) supaya siap dipakai di Unreal Engine.
> **Keputusan arah**: model dibuat **dulu**, Unreal Engine dipasang **nanti**. Semua iterasi sebelum integrasi UE harus bisa divalidasi tanpa UE (lewat script di Blender).
> Acuan desain: [`concept-art/jayadwara_final.webp`](concept-art/jayadwara_final.webp) + [08-requirement-produksi.md](08-requirement-produksi.md#art-direction).

---

## 1. Tujuan & definisi "siap dipakai di UE"

Model dianggap **selesai** kalau paket ini lengkap dan lulus validasi:

- [ ] **Skeletal mesh** `SK_Jayadwara` (1 FBX, LOD0–LOD3) dengan skeleton kompatibel UE5 Mannequin (nama + hierarki tulang).
- [ ] **Set material & tekstur** (4 slot material, mask map untuk recolor).
- [ ] **Socket** untuk hit detection, VFX jurus, dan cadangan sayap.
- [ ] **Rantai tulang** untuk selendang & kain (siap Anim Dynamics).
- [ ] **Lulus validasi otomatis** (bagian 6.6) dan uji pose.
- [ ] **Lulus checklist IP & budaya** (bagian 8).
- [ ] **README import** + script import UE (Python) siap dipakai begitu UE terpasang.

---

## 2. Titik awal (pengecekan 11 Okt 2026)

| Item | Kondisi |
|---|---|
| Blender | **5.2.2 LTS**, add-on MCP v1.8 aktif (port 9876). Scene masih default (Cube, Light, Camera). |
| Exporter | FBX dan glTF aktif. **Rigify tidak aktif** → rig dibuat lewat script sendiri. |
| Unreal Engine | Folder `UE_5.6` hanya berisi cache `.egstore` (±4.9 GB), tanpa `Engine/` → instalasi tampaknya belum selesai. Project UE belum dibuat. Visual Studio baru **Build Tools 2022** (workload C++ ada). Tidak menghalangi tahap model. |
| Repo | Belum ada `.gitattributes` / `.gitignore` → buat sebelum commit `.blend` pertama (Fase 0). |
| Referensi | Satu sheet gambar AI. Tampak depan/samping/belakang **tidak persis konsisten** dan resolusi detailnya kecil → butuh langkah *design lock* (Iterasi 0). |
| Docs | Jayadwara satu grup rig dengan **Dwarapala Kala & Dwarapala Kembar** ([05](05-daftar-episode-boss.md#pengelompokan-rig--skeleton-hemat-produksi)); satu sistem combat dipakai dua skala ([12](12-technical-design.md#combat-satu-sistem-dua-skala)). |

---

## 3. Keputusan teknis (dengan default yang direkomendasikan)

| # | Keputusan | Default | Alasan |
|---|---|---|---|
| D1 | Sumber aset | **Blender 5.2 + Claude (MCP)** untuk semua tahap; commission hanya opsional untuk polish (Iterasi 7) | Arahan developer; memangkas bottleneck aset |
| D2 | Urutan | **Model dulu, UE belakangan**; validasi di UE = Iterasi 6 | UE belum terpasang |
| D3 | Skeleton | **Kompatibel UE5 Mannequin** (nama + hierarki) + tulang tambahan (selendang, kain) | Satu skeleton dibagi dengan Aksa → ABP/montage/GAS ability dipakai ulang; Kala & Kembar ikut |
| D4 | Skala authoring | 1 unit Blender = 1 m, tinggi tubuh **±1,9 m**; skala raksasa lewat *Import Uniform Scale* di UE. Tinggi raksasa di game (placeholder **±45 m**) dikunci saat greybox | Modeling & retarget di skala manusia lebih mudah; angka tinggi bisa diubah tanpa membongkar model |
| D5 | Selendang & kain | **Rantai tulang + Anim Dynamics**, bukan Chaos Cloth | Murah, stabil, mudah di-tuning untuk solo dev |
| D6 | LOD | **4 LOD manual**; tidak mengandalkan Nanite skeletal mesh | Fitur itu belum tentu stabil di 5.6.1 — cek saat UE terpasang |
| D7 | Detail ukiran & batik | **Texture** (trim sheet + tile batik + mask), bukan geometri | Hemat poligon; cocok gaya stylized |
| D8 | Lokasi file | `Art/Blender/`, `Art/Reference/`, `Art/Scripts/`, `Art/Export/` (di luar `Content/`) | UE hanya membaca `Content/`; `.blend`/`.fbx`/`.png` lewat Git LFS |
| D9 | Variasi Kala/Kembar | Material berbasis **mask zona warna** (merah/emas/hitam/putih) | Recolor tanpa model baru (implementasinya nanti) |

> Jika ada default yang tidak cocok, ubah di tabel ini sebelum Iterasi 1 dimulai.

---

## 4. Prinsip desain model

1. **Armor modular & kaku, undersuit lentur.** Undersuit hitam = satu mesh ter-skin. Pelat armor, helm, tanduk = potongan kaku yang di-parent/di-weight ke satu tulang (tanpa deformasi aneh). Selendang & kain = strip ter-skin ke rantai tulang.
2. **Siluet dulu.** Tanduk, bahu, dan selendang adalah identitas — cek siluet dari depan, samping, 3/4 bawah (sudut kamera raksasa) sebelum menambah detail.
3. **Bentuk bersudut = cocok di-script.** Desain faceted/angular bisa dibangun dengan bmesh + modifier (bevel, solidify, mirror). Bentuk lengkung (tanduk, selendang) lewat curve → mesh.
4. **Detail di tekstur.** Ukiran, batik, dan ornamen dada berupa relief ringan + normal map.
5. **Wajib reversible.** Tiap iterasi disimpan sebagai versi `.blend` (`v01`, `v02`, ...) supaya bisa kembali.
6. **Tidak ada wajah.** Faceplate + mata menyala → tidak butuh facial rig.

### Daftar bagian (part list) & anggaran poligon LOD0

| Kelompok | Bagian | Tipe | Tulang induk | Tris (±) |
|---|---|---|---|---|
| Kepala | Helm, faceplate, ornamen dahi, pelindung leher | Kaku | `head` / `neck_02` | 9k |
| | Tanduk emas kiri-kanan | Kaku | `head` | 3k |
| Torso | Pelat dada (motif surya), pelat punggung, perut | Kaku | `spine_03` / `spine_02` | 12k |
| Bahu | Pauldron kiri-kanan | Kaku (blend `clavicle` + `upperarm`) | `clavicle_*` | 8k |
| Lengan | Bracer, sarung tangan (jari) | Bracer kaku, sarung tangan ter-skin | `lowerarm_*` / `hand_*` | 14k |
| Pinggang | Sabuk, kain depan, kain belakang | Sabuk kaku, kain ter-skin | `pelvis` + rantai | 10k |
| Selendang | Selendang panjang | Ter-skin | rantai `scarf_*` | 5k |
| Kaki | Pelindung paha/lutut (berlian), greaves, sepatu | Kaku | `thigh_*` / `calf_*` / `foot_*` | 16k |
| Undersuit | Badan hitam ramping-atletis | Ter-skin | seluruh tubuh | 18k |
| **Total LOD0** | | | | **≈ 95k (batas ≤ 100k)** |

LOD1 ≈ 50k · LOD2 ≈ 20k · LOD3 ≈ 6k. *Angka perkiraan, diuji saat integrasi UE.*

---

## 5. Pembagian kerja

| Claude (lewat Blender MCP, script, file teks) | Developer |
|---|---|
| Ekstrak & siapkan referensi, model sheet, proportion chart | Menyetujui model sheet; menyelesaikan keputusan desain yang ambigu |
| Script modeling (blockout → hard surface), armature, skinning otomatis + pembersihan | Review visual di viewport Blender, memberi koreksi proporsi |
| Script UV, bake mask, material preview | Hand-paint (gradien, edge wear), perbaikan weight manual di titik rumit |
| Script validasi, export FBX, LOD | Sculpt/koreksi detail organik bila hasil script kurang |
| README import UE + script Python import UE | Instal UE; menjalankan import; menyusun Skeleton/Physics Asset/ABP di editor |
| Update docs & checklist IP | Review budaya (batik, Kala-Bhoma) oleh budayawan sebelum rilis |

**Aturan kerja Blender**
- Script menyimpan di `Art/Scripts/` (bisa dijalankan ulang untuk membuat basis). Setelah iterasi disetujui, **`.blend` jadi sumber kebenaran** — edit manual developer tidak ditimpa script.
- Save versi `.blend` di akhir setiap langkah besar; MCP bisa terputus jika Blender crash.
- Nama objek: `JD_<Kelompok>_<Bagian>_<L|R>` (contoh `JD_Armor_Pauldron_L`).

---

## 6. Spesifikasi teknis aset

### 6.1 Skeleton (kompatibel UE5 Mannequin)
`root` → `pelvis` → `spine_01…05` → `neck_01…02` → `head`; `clavicle_l/r` → `upperarm` → `lowerarm` → `hand` → jari (`thumb/index/middle/ring/pinky_01…03`); `thigh` → `calf` → `foot` → `ball`. Tulang twist (`*_twist_01`) ikut. Tulang IK helper (`ik_foot_*`, `ik_hand_*`) mengikuti Mannequin.
**Tulang tambahan:** `scarf_l_01…06`, `scarf_r_01…06` (selendang = helai kain sisi, lihat K5 di [14](14-model-sheet-jayadwara.md)), `cloth_front_01…03`, `cloth_back_01…03`, (opsional) `pauldron_l/r`.
> Nama persis dicocokkan dengan template ThirdPerson UE 5.6 saat UE terpasang. Simpan **tabel mapping nama** (`Art/Scripts/bone_map.json`) supaya rename massal gampang.

### 6.2 Socket (empty `SOCKET_<nama>` di-parent ke tulang)
`SOCKET_hand_r`, `SOCKET_hand_l`, `SOCKET_foot_r`, `SOCKET_foot_l` (trace hit-detection), `SOCKET_chest_sun` (VFX jurus spesial), `SOCKET_eye_l/r`, `SOCKET_head_top`, `SOCKET_back_center` (cadangan sayap Ep 38).

### 6.3 Material (4 slot)
| Slot | Isi |
|---|---|
| `M_Jayadwara_Body` | Undersuit hitam + sarung tangan |
| `M_Jayadwara_Armor` | Pelat merah + trim emas (trim sheet) |
| `M_Jayadwara_Cloth` | Selendang & kain (batik, two-sided) |
| `M_Jayadwara_Face` | Faceplate putih; mata & permata dada emissive **konstan** |

Mask map RGBA per zona warna (R = merah, G = emas, B = hitam, A = putih/aksen) → untuk Kala/Kembar.

### 6.4 Tekstur
Default 2048² per slot (1024² untuk Face); naik ke 4096² hanya untuk kepala/dada kalau perlu close-up. Packing: BaseColor, Normal, ORM, Mask.

### 6.5 Kontrak export FBX
- Z-up, skala 1, tanpa leaf bone, hanya tulang deform + socket, modifier di-apply.
- **Jangan hardcode enum** — baca nilai valid dari Blender 5.2 (`bl_rna.properties[...].enum_items`).
- Nama file: `SK_Jayadwara.fbx` (LOD di dalam file atau `SK_Jayadwara_LOD1.fbx` dst.).

### 6.6 Validasi otomatis (jalan tanpa UE)
Script `Art/Scripts/validate_jayadwara.py`: re-import FBX ke scene kosong lalu cek —
- jumlah & nama tulang sesuai `bone_map.json`; hanya satu root; tidak ada nama ganda;
- tinggi bounding box ≈ 1,9 m; skala objek 1; tidak ada scale negatif;
- tris per LOD sesuai anggaran; jumlah material = 4;
- skin weight: tiap vertex ≤ 4 influence (maks. 8), ternormalisasi, **0 vertex tanpa weight**;
- ngon di zona deformasi = 0; non-manifold di mesh armor = 0.

---

## 7. Iterasi

> Estimasi jam **kasar** (kapasitas ±10–15 jam/minggu). Direvisi di akhir Iterasi 1.

| Iter | Nama | Estimasi | Butuh UE? |
|---|---|---|---|
| 0 | Design lock & fondasi | 6–8 jam | Tidak |
| 1 | Proxy blockout + rig dasar | 12–15 jam | Tidak |
| 2 | Hero modeling (mid-poly) | 25–30 jam | Tidak |
| 3 | Rig final & skinning | 15–20 jam | Tidak |
| 4 | UV, tekstur & material | 20–25 jam | Tidak |
| 5 | LOD, export & paket UE-ready | 10–12 jam | Tidak |
| 6 | Integrasi Unreal | 15–20 jam | **Ya** (setelah UE + project siap) |
| 7 | Polish & varian (opsional, Fase 2) | — | Ya |

**Total sebelum UE (Iter 0–5): ±88–110 jam ≈ 7–9 minggu** pada kapasitas penuh.

### Iterasi 0 — Design lock & fondasi
**Tujuan:** menghilangkan ambiguitas desain sebelum modeling.
- **Claude:** crop front/side/back/kepala dari sheet ke `Art/Reference/`; ukur proporsi (jumlah kepala, lebar bahu, panjang kaki) → *proportion chart*; ambil palet warna (hex) dari sheet; tulis **model sheet** (part list + keputusan di titik tidak konsisten); siapkan struktur folder `Art/`, scene Blender (unit metrik, collection per kelompok, penamaan), draft `.gitattributes` & `.gitignore` (termasuk `*.blend1`).
- **Developer:** menyetujui model sheet; menjawab keputusan desain (lihat di bawah); **sangat disarankan** meminta referensi baru dari generator gambar: *Jayadwara pose A netral, tampak depan/samping/belakang ortografis, latar polos* (referensi turnaround AI sekarang berpose dinamis).
- **Keputusan desain yang harus dikunci:** (1) ornamen dada — chevron V + permata berlian (final.webp) atau bintang surya; (2) bentuk mulut/pipi faceplate yang dibedakan dari Ultra; (3) cara menampilkan motif Kala-Bhoma di dahi (relief emas, bukan kristal); (4) bentuk tanduk (melengkung dari sisi helm, bukan bilah paralel di atas kepala).
- **Gate:** model sheet disetujui; referensi ortografis siap; checklist IP (bagian 8) terisi.
- **Status (11 Okt 2026): pekerjaan Claude selesai, menunggu persetujuan developer.**
  - [x] Referensi ortografis ternormalisasi (`Art/Reference/`, script `make_reference_planes.py`; 1000 px = 1,90 m, keempat view sejajar).
  - [x] Proportion chart, palet (swatch + shadow/mid/highlight + emissive), part list → [14-model-sheet-jayadwara.md](14-model-sheet-jayadwara.md).
  - [x] Keputusan desain K1–K8 diusulkan; checklist IP terisi.
  - [x] Scene Blender: `Art/Blender/jayadwara_giant_v00_setup.blend` (satuan metrik, collection per kelompok, reference plane depan/samping/belakang, penggaris 1,9 m, 17 penanda landmark; keselarasan diverifikasi di view ortografis).
  - [x] `.gitattributes` (LFS), `.gitignore`, `Art/README.md`.
  - [ ] Developer menyetujui K1–K8 (bagian 8 di dokumen 14) dan memutuskan referensi pose-A baru.
  - **Catatan hasil:** konsep memiliki lengan pendek (kepalan setinggi selangkangan) dan tanduk yang ukurannya berbeda antar-view → diputuskan lewat K7 dan K4. Tidak ada cara memverifikasi "sendi pinggul" karena tertutup kain (estimasi).

### Iterasi 1 — Proxy blockout + rig dasar
**Tujuan:** proxy raksasa < 12k tris, proporsi benar, ter-rig, bisa di-export. Dipakai nanti sebagai **pawn raksasa di prototype Fase 1** (Feb 2027), menggantikan kotak.
- **Claude:** script blockout per part list (primitif + bevel), 4 material warna datar; armature Manny-style + socket; parent/auto-weight; 5 uji pose (kuda-kuda silat, pukul, tendang, injak, jongkok); export FBX; jalankan validasi; render `look` 4 sudut vs turnaround.
- **Developer:** review di viewport Blender; koreksi proporsi dengan bahasa biasa ("bahu lebih lebar", "kaki kurang panjang").
- **Gate:** siluet depan/samping/belakang cocok dengan konsep; lolos validasi; 5 pose tanpa tembus parah.
- **Status (11 Okt 2026): pekerjaan Claude selesai, menunggu review developer di viewport.** File: `Art/Blender/jayadwara_giant_v01_proxy.blend`, `Art/Export/SK_Jayadwara_Proxy.fbx`.
  - [x] Proxy 43 bagian, **2.154 tris** (batas 12k), 4 slot material (warna dari atribut `JD_Zone`; permata & mata emissive konstan), K1–K8 diterapkan sebagai default.
  - [x] Rig 44 tulang bergaya Mannequin (rantai `scarf_l/r` ×6, `cloth_front/back` ×3), 9 socket, undersuit ter-skin (heat-map), armor kaku, kain berbobot sepanjang rantai.
  - [x] Validasi FBX di Blender headless terpisah: **22/22 PASS** (nama & jumlah tulang, 1 root, tinggi 1,99 m, skala 1, ≤4 influence, 0 vertex tanpa weight, ternormalisasi, socket ter-parent, tanpa vertex lepas). Validator menemukan 3 vertex lepas (artefak Skin modifier) → diperbaiki di `finish_part`.
  - [x] 5 pose uji (kuda-kuda, pukul, tendang, injak, jongkok) tersimpan sebagai Action `JD_PoseTest`; diperiksa visual dari depan dan samping, tidak ada tembus parah. *Penetrasi tidak diukur secara numerik.*
  - [x] Siluet vs referensi (`silhouette_compare.py`): depan tanpa area lengan **IoU 0,76**, samping **0,59** (dada samping 0,79; sisanya terseret garis kaki referensi yang bergeser ±5 cm dan helai kain tipis). Pengukuran ini menangkap satu kesalahanku (lebar kaki; IoU depan 0,59 → 0,76 setelah dikoreksi). *Ambang lulus (≥0,75 / ≥0,55) kutetapkan setelah melihat hasil, jadi bukti lemah — penilaian akhir tetap review visual developer.*
  - [ ] Developer mereview proporsi di Blender dan memberi koreksi.
  - **Deviasi dari konsep (disengaja):** lengan 30° dari tubuh (konsep ±12°) dan +10% lebih panjang (K7), sehingga area lengan dikecualikan dari IoU depan.
  - **Belum teruji:** FBX di Unreal (pilihan sumbu `-Y`/`Z`, orientasi tulang) → Iterasi 6. Bobot undersuit hasil auto-weight belum dirapikan manual → Iterasi 3.
  - Urutan membangun ulang: lihat [Art/README.md](../Art/README.md).

### Iterasi 2 — Hero modeling (mid-poly)
**Tujuan:** bentuk final LOD0 ≤ 100k tris, topologi bersih di zona deformasi.
- **Claude:** bangun per kelompok, **review tiap kelompok sebelum lanjut**: kepala (helm, faceplate, tanduk, ornamen) → torso → bahu → lengan & sarung tangan → sabuk & kain → kaki & sepatu. Pakai bmesh, bevel/solidify/mirror, curve→mesh untuk tanduk dan selendang.
- **Developer:** review tiap kelompok; sculpt/model manual bagian yang gagal dari script.
- **Deliverable:** `jayadwara_hero_v01.blend`.
- **Gate (Go/No-Go):** bandingkan berdampingan dengan konsep. Cukup layak → lanjut. Belum → pilih: perbaiki, atau commission polish (Iterasi 7) dengan model ini sebagai basis.

### Iterasi 3 — Rig final & skinning
- **Claude:** armature lengkap (jari, twist, rantai selendang/kain, socket); undersuit auto-weight + script pembersih (batas 4 influence, normalisasi, smoothing); armor kaku di-weight ke satu tulang; uji pose diperluas (silat penuh, jangkauan tangan terbuka, tendang tinggi); daftar masalah deformasi + screenshot.
- **Developer:** perbaikan weight manual di titik rumit (bahu, pinggul, selendang).
- **Gate:** validasi skin lolos; pose uji tanpa penyok/tembus; pauldron tidak menembus dada/kepala di rentang gerak normal.

### Iterasi 4 — UV, tekstur & material
- **Claude:** unwrap terskrip (seam dari sharp edge, island per bagian); layout **trim sheet** emas berukir; bake **mask map**; tile batik prosedural; material preview di Blender yang meniru parameter master material UE; tulis spek `M_Jayadwara_Master` (parameter: warna zona, emissive mata/permata, roughness).
- **Developer:** hand-paint (gradien, edge wear, AO); cek warna vs palet; review motif batik.
- **Catatan budaya:** pakai motif umum (mis. kawung, ceplok); **hindari batik larangan keraton** (mis. parang rusak). Review budayawan sebelum rilis (lihat [06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)).
- **Gate:** preview mendekati palet konsep; ukuran tekstur sesuai anggaran; tepat 4 slot material.

### Iterasi 5 — LOD, export & paket UE-ready
- **Claude:** LOD1–3 (decimate terskrip + perbaikan), export final, jalankan `validate_jayadwara.py`; tulis `Art/Export/README_IMPORT_UE.md` (opsi import langkah demi langkah) dan `Tools/ue_import_jayadwara.py` (Unreal Python, **belum teruji sampai UE ada**); usulkan tambahan konvensi nama di [12](12-technical-design.md#konvensi-penamaan-aset): `SKEL_`, `PA_` (Physics Asset), `IK_`/`RTG_` (IK Rig/Retargeter).
- **Gate:** semua validasi hijau; paket lengkap (FBX, tekstur, README, script). **Model "selesai" sampai sini** untuk tujuan sekarang.

### Iterasi 6 — Integrasi Unreal *(ditunda sampai UE 5.6.1 + project siap)*
- **Prasyarat:** UE terpasang utuh, project C++ `Jayadwara` dibuat (Fase 0).
- **Developer (editor):** import FBX, atur Skeleton, Physics Asset kasar (kapsul per anggota badan), set Import Uniform Scale, material master, Anim Dynamics untuk rantai selendang/kain, IK Rig + Retargeter (Mixamo → Mannequin → Jayadwara).
- **Claude:** hubungkan `AJDGiantCharacter` (C++), nama socket di Anim Notify State hit detection, `UJDCombatProfile` skala raksasa, perbaiki script import.
- **Spike risiko:** impor mesh dengan tulang tambahan ke skeleton Mannequin → pastikan animasi Mannequin tetap jalan. Jika gagal: skeleton terpisah + IK Retargeter.
- **Gate:** pawn raksasa berjalan dengan animasi retarget; socket hit berfungsi; uji skala (±45 m) di level uji dengan gedung; target 60 FPS.

### Iterasi 7 — Polish & varian *(opsional, Fase 2)*
Kepala hi-res untuk cutscene, polish/commission, recolor Dwarapala Kala & Kembar, slot sayap (Ep 38).

---

## 8. Checklist IP & budaya (dipakai di setiap gate)

Berdasarkan [01](01-konsep-dan-pilar.md#wajib-dihindari), [08](08-requirement-produksi.md#art-direction), [06](06-referensi-mitologi.md#panduan-sensitivitas-budaya):

- [ ] Tidak ada lampu/timer di dada; **permata dada statis** (emissive konstan, **tidak dihubungkan ke meter Sync** atau berkedip).
- [ ] Dahi = relief emas berukir, **bukan kristal/permata menyala**.
- [ ] Tanduk melengkung dari sisi helm — **bukan bilah kembar paralel di atas kepala**.
- [ ] Mata = celah miring menyala, **bukan lensa besar bulat**.
- [ ] Faceplate putih dengan bentuk mulut/pipi yang jelas berbeda dari Ultra (titik paling dekat ke Ultra).
- [ ] **Tidak ada warna silver/perak**; trim memakai emas; tidak ada kombinasi badan merah-silver.
- [ ] Tidak ada emblem garuda.
- [ ] Pose & jurus: hindari silang lengan bentuk L (Specium Ray).
- [ ] Motif batik umum, bukan batik larangan; Kala-Bhoma digambarkan hormat.

---

## 9. Risiko

| Risiko | Mitigasi |
|---|---|
| Referensi AI tidak konsisten antar sudut | Iterasi 0 (design lock) + referensi A-pose ortografis |
| Hasil script kurang "hero" untuk bentuk organik/ukiran | Review per kelompok; gate Go/No-Go di Iterasi 2; fallback commission polish |
| Kompatibilitas skeleton Mannequin belum teruji | Tabel mapping nama; spike Iterasi 6; fallback IK Retargeter |
| Selendang/kain di skala raksasa terlihat "terlalu cepat" | Rantai tulang yang bisa di-tuning; fallback sway animasi statis |
| Anggaran poligon belum teruji | LOD 4 level; uji performa di Iterasi 6 |
| Sesi Blender MCP terputus / Blender crash | Simpan versi tiap langkah; script di `Art/Scripts/` |
| Waktu: ±90–110 jam menggeser Fase 0–1 | Revisi tanggal di akhir Iterasi 1; proxy Iterasi 1 sudah bisa dipakai prototype |
| Faceplate putih terlalu mirip Ultra | Keputusan desain #2 di Iterasi 0; cek ulang di tiap gate |

---

## 10. Backlog (di luar scope rencana ini)

- Arca Dwarapala + fragmen untuk cutscene transformasi Ep 1 (aset terpisah).
- Model Aksa (konsep: `concept-art/aksa_v01.png`), Jerangkong, minion.
- Dwarapala Kala & Dwarapala Kembar (varian Jayadwara).
- Sayap (Ep 38), VFX kekuatan bumi (Ep 44).
- Animasi silat final (Mixamo hanya untuk prototype).
