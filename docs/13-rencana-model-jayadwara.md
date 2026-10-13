# 13 — Rencana Implementasi: Model Jayadwara (Wujud Raksasa)

> Draft v0.1 — 11 Oktober 2026. Rencana membuat model 3D Jayadwara di **Blender 5.2** (dibantu Claude lewat Blender MCP) supaya siap dipakai di Unreal Engine.
> **Keputusan arah**: model dibuat **dulu**, Unreal Engine dipasang **nanti**. Semua iterasi sebelum integrasi UE harus bisa divalidasi tanpa UE (lewat script di Blender).
> Acuan desain: [`concept-art/jayadwara_final.webp`](concept-art/jayadwara_final.webp) + [08-requirement-produksi.md](08-requirement-produksi.md#art-direction).
> **13 Okt 2026 (R6 docs/25): developer memilih Jayadwara2** (model Tripo) sebagai model aktif. Model di dokumen ini **tidak dipakai lagi di game tetapi disimpan utuh sebagai cadangan** (`Art/Blender/jayadwara_giant_v05_revisi.blend`, `Art/Export/SK_Jayadwara*.fbx`, `/Game/Jayadwara/Characters/Jayadwara/`). Kembali ke model ini: `ACTIVE_GIANT = "Jayadwara"` di `Tools/ue_setup_transform.py`.

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
| D4 | Skala authoring | 1 unit Blender = 1 m, tinggi tubuh **±1,9 m**. Skala raksasa **di-bake saat export** (`16_make_lods.py` `GIANT_HEIGHT_M`, placeholder **±45 m**, dikunci saat greybox): FBX & socket JSON sudah setinggi raksasa, diimpor ke UE di skala 1, komponen mesh `AJDGiantCharacter` berskala 1. *Revisi Iterasi 6: Import Uniform Scale masuk ke skala tulang root (UE 5.6.1); komponen mesh berskala membuat Anim Dynamics rusak* | Modeling di skala manusia tetap mudah; Anim Dynamics, Physics Asset, socket bekerja di satuan dunia. Ganti tinggi = jalankan ulang export + 3 skrip UE (otomatis) |
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

LOD1 ≈ 50k · LOD2 ≈ 20k · LOD3 ≈ 6k. *Angka perkiraan, diuji saat integrasi UE.* → **Realisasi (Iterasi 5):** LOD0 51,8k (hero jadi lebih ringan dari anggaran) · LOD1 26,0k · LOD2 11,8k · LOD3 5,4k, yaitu ±50/23/10% dari LOD0.

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
- **Status (11 Okt 2026): pekerjaan Claude selesai; Go/No-Go menunggu developer.** File: `Art/Blender/jayadwara_giant_v02_hero.blend` (dasar: v01), `Art/Export/SK_Jayadwara_Hero.fbx`.
  - [x] **Seluruh kelompok diganti versi hero**, nama objek sama dengan proxy sehingga rig tetap jalan: kepala (helm, rusuk, sirip, alis, tanduk kurva-S, pipi, mata celah, ornamen dahi, faceplate V, dagu, pelindung leher, kerah) → torso (pelat dada melengkung + chevron + gulungan + permata berbingkai + 12 sinar surya halus, punggung) → bahu (pauldron 3 lapis, duri, tutup merah, gulungan) → lengan (bracer, rim, inset merah, berlian, sarung tangan berjari) → sabuk (pita, cincin, gesper berbingkai) → kain (depan/belakang/selendang + garis emas) → kaki (pelindung paha, lutut berlian berlapis, greave, ankle, boots + toe cap + sol) → undersuit (Skin + subdiv 2).
  - [x] **77 objek, ±31,3k tris** (batas LOD0 100k) → masih ±68k tris cadangan untuk detail (Iterasi 7 / sesuai feedback). 4 slot material tetap.
  - [x] **Validator 22/22 PASS** dengan batas 100k. Dua cacat ditemukan dan diperbaiki: face luas nol di kutub elipsoid pauldron (96 face), dan validator sendiri O(n²) di cek vertex lepas.
  - [x] Zona deformasi bersih: undersuit 2.408 quad murni, 0 ngon, manifold tertutup; kain hanya quad + segitiga ujung runcing. Armor kaku: 105 ngon (tutup tabung) di 68 objek — tidak berdeformasi, UE akan men-triangulasi.
  - [x] 5 pose uji diulang pada mesh hero: tidak ada tembus parah (dilihat dari 3/4 dan samping; jongkok & kuda-kuda diperiksa lebih dekat).
  - [x] Siluet vs referensi: depan tanpa lengan **IoU 0,77**, samping **0,61** (setara/lebih baik dari proxy; pauldron dirapikan ke ±0,34 m).
  - [x] Checklist IP pada model: mata celah ±5:1 (≥3:1); permata 0,10 m, statis; dahi relief emas tanpa permata; tanduk dari ujung alis, penampang tebal; tanpa silver; tanpa emblem garuda.
  - [ ] **Developer memutuskan Go/No-Go.** Penilaian jujurku: bentuk, proporsi, dan ornamen utama sudah sesuai konsep, tapi **lebih "bersih/kaku" dari gambar AI** — tidak ada massa organik, ukiran masih berupa garis timbul, undersuit/lengan polos, kepalan kecil. Itu wajar karena ukiran/batik/gradien memang diserahkan ke tekstur (Iterasi 4) dan feedback-mu.
  - **Belum teruji:** FBX di Unreal (Iterasi 6); bobot undersuit masih auto-weight (Iterasi 3); armor kaku belum diuji pada gerakan ekstrem di luar 5 pose.

- **REVISI BESAR (11 Okt 2026, setelah feedback developer: "masih jelek, buat persis seperti konsep").** File: `Art/Blender/jayadwara_giant_v05_revisi.blend`, FBX `SK_Jayadwara_Hero.fbx` ditimpa versi revisi (validator **25/25**, 40.066 tris, 89 tulang). Perbandingan: `Art/Export/_compare_konsep_vs_model.png` (dibuat `render_compare.py` + `compare_sheet.py`, skala sama dengan reference plane).
  - Diubah mengikuti konsep: undersuit **berotot**; **cuirass besar** sampai perut + pelat sayap emas di dada + pita chevron pipih + gulungan merah + permata dengan bingkai sinar surya; **pelat perut bertingkat**; punggung merah penuh; **pauldron bersudut** dengan 4 bilah runcing ke atas; **lengan atas berpelat merah**, **bracer emas besar** + sirip siku, **tangan 1,3×**; sabuk lebih tebal; kain depan lebih panjang/lebar, **selendang ramping menghadap serong**; **kaki**: pelat paha merah, lutut berlian besar, greave melebar di lutut & meramping ke pergelangan (membungkus 330°), sepatu runcing; **helm** lebih besar, tanduk bulan sabit, ornamen dahi emas seperti mahkota, sirip pelipis; palet lebih hidup; kain: ornamen emas di bawah (kawung dihapus).
  - Bug yang ditemukan saat revisi: ornamen torso tenggelam di cangkang (offset dihitung dari tengah cangkang) dan tanda offset sayap yang terbalik di satu sisi — keduanya diperbaiki dan dicek secara numerik.
  - **Revisi kepala (atas feedback "kepala sama sekali tidak mirip"):** ditulis ulang dari nol (`11_hero_head.py`): helm bersudut berfaset (bukan kubah), bingkai emas V menyambung ke tanduk, pelindung pipi emas, ornamen dahi = plakat emas runcing + bingkai timbul + teratai emas padat di atas latar merah kecil (versi awal terbaca seperti "$", diperbaiki), mata lebar bersudut (rasio ≥3:1, K6), faceplate putih + **dagu merah di satu permukaan** dan **pipi merah tumbuh dari tepi faceplate** (tanpa celah), tanduk lengkung-S + tanduk kecil kedua, pecahan sirip merah ke belakang, pelat belakang berlapis. Proporsi kepala diukur ulang terhadap reference plane: lebar depan selisih ≤1,1 cm di semua ketinggian, puncak tanduk 1,985 vs 1,984 m. Perbandingan: `Art/Export/_compare_kepala.png`. Validator 25/25 (42.706 tris).
  - **Revisi perut, sabuk, lengan (atas feedback):** perut = satu pelat merah V bertingkat (2 chevron emas) menyambung dari bawah dada ke sabuk, oblique hitam tetap terlihat; sabuk = dua lilitan merah tebal miring berlapis + pita emas + 10 kancing emas + gesper berlian emas besar berpermata merah + pelat samping + dua ujung simpul; lengan atas = pelat merah hanya sisi luar, ujung runcing ke siku, tepi emas; lengan bawah = gauntlet emas bersudut yang meruncing seperti bilah melewati siku + panel merah + berlian + manset emas mengikuti tepi gauntlet. Validator 25/25 (47.424 tris). Konsekuensi: sabuk lebih tinggi menambah tumpang-tindih pada pose ekstrem (dada × sabuk +88 saat membungkuk 48°, paha × sabuk +218 saat tendangan setinggi kepala).
  - **Revisi sabuk, pauldron, sepatu (atas feedback "sabuk longgar & terlalu tinggi, pauldron & sepatu belum mirip"):** sabuk diukur dari undersuit lalu dibuat pas badan dan diturunkan ke pinggang (z 1,035–1,142, bukan perut); pauldron = tutup emas besar + dua lame emas melengkung yang ujung bawahnya meruncing + pita merah di bawah tiap lame + dua bilah ke atas + satu bilah kecil ke luar; sepatu = loft ramping berujung runcing, poros pergelangan menyatu ke greave, manset emas berbentuk V (pita, bukan kawat) + berlian di titik V, toe cap emas, strip emas di sisi, **berlian merah berbingkai emas di punggung kaki yang diproyeksikan ke permukaan sepatu** (BVH), sol hitam tebal 3,4 cm.
  - **Revisi "zirah melayang" (atas feedback "banyak gap antara zirah/pauldron dan badan; badan dibuat berisi/berotot"):** celah terukur sebelum revisi: median 8 cm di bawah tutup pauldron, 5,8 cm di bawah lame, hingga 11,8 cm di bibir atas cuirass. Perbaikan:
    1. Undersuit lebih berisi (`10_hero_body.py`: dada, punggung, trapezius, deltoid, bisep, lengan bawah).
    2. Skrip baru **`15_body_fit.py`**: badan di bawah zirah didorong keluar sampai ±8 mm dari permukaan dalam zirah, dengan transisi halus di tepi zirah. Aturan: lengan tidak didorong zirah dada; trapezius tidak didorong pauldron (hanya permukaan yang menghadap ke samping), karena itu sempat membuat bahu **berpunuk** (feedback berikutnya).
    3. Bobot ikut zirah: vertex yang didorong mewarisi bobot zirah di atasnya (`02_rig.py`, penuh pada dorongan ≥2 cm). Tanpa ini tutup pauldron tertelan deltoid saat lengan diangkat.
    4. Kerah hitam baru `JD_Torso_Collar`, berbentuk corong dari bibir cuirass ke kerah helm (konsep: leher tinggi hitam).
    5. Pauldron diturunkan 1,4 cm dan dibuat lebih pipih. Lame digeser turun dan lame bawah dipendekkan (tidak bentrok dengan gauntlet).
    6. Emblem pindah ke sisi luar tutup, berbentuk berlian vertikal. Versi bulat dengan titik di tengah terbaca seperti "mata", dan bersama dua bilah membuat pauldron mirip kepala makhluk.
  - Hasil revisi zirah melayang: validator 25/25 (51.808 tris). Render: `Art/Export/_compare_torso/render_torso.png`, `_compare_sabuk_pauldron_sepatu.png`.
  - **Biaya revisi zirah melayang (jujur):**
    - Pose lengan terangkat penuh (`tangan_atas`): peregangan maks 4,3 → 9,4 cm (15 tepi > 4 cm), 86 dari 352 vertex tutup pauldron masuk ke badan, tutup × kerah +98 segitiga. Pose lain bersih (tutup 0 vertex di dalam badan).
    - Tumpang-tindih pose ekstrem lain tetap: paha × sabuk +442 (tendangan setinggi kepala), gauntlet × pauldron kiri +262 (pukul).
    - Perlu diuji ulang di UE dengan animasi sungguhan. Kemungkinan perbaikan: tulang bantu bahu, atau tutup pauldron yang diangkat saat lengan naik (corrective).
  - **Masih berbeda dari konsep (jujur):** bentuk lebih kaku/tabung daripada lukisan; ukiran emas organik di dada/pauldron/kain disederhanakan jadi pita & bentuk geometris; helm belakang polos; badan sedikit lebih gempal; lengan A-pose 30° (konsep ±12°). Peregangan bahu saat lengan terangkat penuh naik ke 4,3 cm (undersuit lebih tebal).

### Iterasi 3 — Rig final & skinning
- **Claude:** armature lengkap (jari, twist, rantai selendang/kain, socket); undersuit auto-weight + script pembersih (batas 4 influence, normalisasi, smoothing); armor kaku di-weight ke satu tulang; uji pose diperluas (silat penuh, jangkauan tangan terbuka, tendang tinggi); daftar masalah deformasi + screenshot.
- **Developer:** perbaikan weight manual di titik rumit (bahu, pinggul, selendang).
- **Gate:** validasi skin lolos; pose uji tanpa penyok/tembus; pauldron tidak menembus dada/kepala di rentang gerak normal.
- **Status (11 Okt 2026): pekerjaan Claude selesai, menunggu review developer.** File: `Art/Blender/jayadwara_giant_v03_rig.blend` (dasar: v02), `Art/Export/SK_Jayadwara_Hero.fbx` (rig lengkap).
  - [x] **Armature 89 tulang:** 44 sebelumnya + 8 twist (`upperarm/lowerarm/thigh/calf_twist_01`) + 30 jari (`thumb/index/middle/ring/pinky_01..03` ×2, terkepal) + 7 IK (`ik_foot_root`, `ik_hand_root`, `ik_foot_l/r`, `ik_hand_gun/l/r`). IK tidak men-deform; export memakai opsi *semua tulang* (bukan hanya deform) agar IK ikut. Posisi sendi jari berasal dari satu sumber (`jd_skeleton.finger_joints`) yang juga membentuk mesh jari.
  - [x] **Jari ter-skin:** 10 objek jari (3 tulang per jari, bobot dari parameter panjang `JD_t`), telapak kaku ke `hand`. Armor tetap kaku; undersuit heat-map + 3× smoothing + batas 4 influence.
  - [x] **Validator 22/22 PASS** pada 89 tulang (30.990 tris).
  - [x] **13 pose uji** (6 awal + tangan terangkat, raih depan, tendang tinggi, tangkis, membungkuk, memutar badan, menoleh 55°) di Action `JD_PoseTest`. `06_deform_check.py` mengukur dua hal secara numerik:
    - **Peregangan undersuit:** perubahan panjang tepi maks **3,0 cm** (tendang tinggi/injak), 0 tepi di atas batas 4 cm. *Rasio* tepi sempat tampak parah (0,08–2,95×) tetapi hanya karena median tepi ±2,4 cm → metrik diganti ke perubahan absolut. *Batas 4 cm kutetapkan setelah melihat distribusi (maks 3,0 cm) — bukti lemah; yang lebih berarti adalah visual dan angka maks itu sendiri.* Smoothing tambahan tidak mengubah hasil (370 → 368 tepi), jadi bobot bukan penyebab.
    - **Penetrasi baru antar-armor** (segitiga berpotongan dikurangi rest, 33 pasangan): 20 pasangan nol. Dua perbaikan nyata: ujung V pelat dada vs sabuk saat membungkuk (V dipendekkan 2,5 cm) dan pelindung paha vs greave (dipendekkan/diberi celah, ditutup lutut berlian).
  - **Penetrasi tersisa (diterima, dengan alasan):** (a) pelindung paha × lutut berlian ±65 (L/R simetris) = tumpang-tindih berlapis yang disengaja; (b) kain/selendang × paha/greave/sabuk (21–128) = kain belum bersimulasi — selesai oleh Anim Dynamics di Unreal; (c) lengan × dada saat pukul (+36) = kontak wajar; (d) helm × pauldron kanan saat menoleh 55° (+18) = kecil; (e) **paha × sabuk saat tendang setinggi kepala (+128)** = batas desain pelat paha utuh — kandidat dipecah jadi 2 pelat di Iterasi 7 jika animasi butuh.
  - [ ] Developer mereview deformasi di viewport (putar frame 1–13).
  - **Belum diuji:** FBX di Unreal, retarget Mannequin (orientasi tulang), IK Retargeter; jari hanya terkepal (tidak diuji membuka); twist bone belum digerakkan (menunggu Control Rig/ABP).

### Iterasi 4 — UV, tekstur & material
- **Claude:** unwrap terskrip (seam dari sharp edge, island per bagian); layout **trim sheet** emas berukir; bake **mask map**; tile batik prosedural; material preview di Blender yang meniru parameter master material UE; tulis spek `M_Jayadwara_Master` (parameter: warna zona, emissive mata/permata, roughness).
- **Developer:** hand-paint (gradien, edge wear, AO); cek warna vs palet; review motif batik.
- **Catatan budaya:** pakai motif umum (mis. kawung, ceplok); **hindari batik larangan keraton** (mis. parang rusak). Review budayawan sebelum rilis (lihat [06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)).
- **Gate:** preview mendekati palet konsep; ukuran tekstur sesuai anggaran; tepat 4 slot material.
- **Status (11 Okt 2026): bagian Claude selesai; hand-paint & feedback menunggu developer.** File: `Art/Blender/jayadwara_giant_v04_tex.blend`, `Art/Export/Textures/` (17 PNG + `_bake/`), `Art/Export/SK_Jayadwara_Hero.fbx` (dengan UV), spesifikasi: [15-spesifikasi-material-jayadwara.md](15-spesifikasi-material-jayadwara.md).
  - [x] **UV terskrip** (`07_uv_unwrap.py`): smart_project (Body 45°, lainnya 89°), kain di-unwrap sudut dan **16 strip diputar searah panjang** (batik konsisten), lalu **packer sendiri** (packer bawaan Blender 5.2 tidak bisa disetel: cakupan tetap ±5% apa pun parameternya → density 238 px/m; packer sendiri → **611 px/m**). 0% tumpang-tindih di keempat slot; semua UV 0–1.
  - [x] **Tekstur** (`make_textures.py`): Mask zona RGBA, BC (pengali; batik kawung di kain), Normal (relief kawung di kain), ORM (AO bake Cycles 24 sample + roughness + metallic dari zona), Emit (mata + permata). 2048² Armor/Cloth, 1024² Body/Face.
  - [x] **Material Blender meniru master UE** (`08_materials.py`): nama parameter = label node; emissive konstan, tidak dikaitkan ke apa pun (aturan IP).
  - [x] **Validator 25/25 PASS** (ditambah cek UV: 1 layer, 0–1).
  - **Penyimpangan dari rencana:** Body 1024² (rencana: 2048²) karena didominasi hitam polos; tidak ada trim sheet emas terpisah — trim emas sudah geometri dan ukiran halus diserahkan ke hand-paint; AO bake bukan kualitas final.
  - **Dua kesalahan yang kutemukan di tengah jalan:** (1) UV Body sempat tumpang-tindih 1,8% karena smart_project 89° melipat tabung undersuit → sudut Body diturunkan; (2) bake awal 8 sample ber-noise → dinaikkan 24 sample.
  - [ ] **Developer: hand-paint dan feedback visual.** Aturan penting: jangan jalankan ulang `07`/`make_textures` ke folder yang sama setelah mulai mengecat (lihat docs/15 bagian 3).
  - **Belum diuji:** import tekstur/material di Unreal; tampilan emas metalik dengan refleksi UE.

### Iterasi 5 — LOD, export & paket UE-ready
- **Claude:** LOD1–3 (decimate terskrip + perbaikan), export final, jalankan `validate_jayadwara.py`; tulis `Art/Export/README_IMPORT_UE.md` (opsi import langkah demi langkah) dan `Tools/ue_import_jayadwara.py` (Unreal Python, **belum teruji sampai UE ada**); usulkan tambahan konvensi nama di [12](12-technical-design.md#konvensi-penamaan-aset): `SKEL_`, `PA_` (Physics Asset), `IK_`/`RTG_` (IK Rig/Retargeter).
- **Gate:** semua validasi hijau; paket lengkap (FBX, tekstur, README, script). **Model "selesai" sampai sini** untuk tujuan sekarang.
- **Status (11 Okt 2026): bagian Claude selesai; skrip & langkah UE belum diuji (menunggu UE, Iterasi 6).**
  - [x] **LOD** (`Art/Scripts/16_make_lods.py`):
    - Decimate COLLAPSE per bagian (rasio 0,50 / 0,22 / 0,09, dengan minimal tris per bagian), lalu bobot dibersihkan (≤4 influence, dinormalisasi) dan vertex/edge yatim dibuang.
    - Bagian dengan diagonal < 3,5 cm (LOD2) / < 8 cm (LOD3) dibuang; mata, permata, faceplate, undersuit dilindungi. Yang terbuang hanya berlian pergelangan di LOD3.
    - Berlian lutut & tanduk diberi batas decimate. Tanpa itu, facet-nya pecah jadi bidang abu-abu yang terbaca "silver" (aturan IP).
  - [x] **Export final:** `Art/Export/SK_Jayadwara.fbx` (LOD0) + `SK_Jayadwara_LOD1..3.fbx`, sesuai kontrak 6.5: LOD sebagai file terpisah, karena exporter FBX Blender tidak menulis LOD Group. `SK_Jayadwara_Hero.fbx` diganti oleh `SK_Jayadwara.fbx`.
    - Validator **25/25 di keempat file** (batas tris 100k / 30k / 14k / 6k).
    - Perbandingan visual: `Art/Export/_compare_lod.png`.
  - [x] **Bug export diperbaiki:** sejak revisi sebelumnya, `bake_anim=False` tidak sengaja masuk ke komentar di `05_export_fbx.py`, sehingga aksi pose test ikut terekspor. Sekarang FBX tanpa animasi (LOD0 2,8 → 2,4 MB).
  - [x] **Socket untuk UE:** `SK_Jayadwara_sockets.json` (tulang + posisi). UE tidak membuat socket skeletal mesh dari empty FBX.
  - [x] **Paket import:** `Art/Export/README_IMPORT_UE.md` (opsi skrip + manual + checklist verifikasi) dan `Tools/ue_import_jayadwara.py`. Skrip mengimpor:
    - tekstur dengan setelan docs/15, Flip Green untuk normal;
    - `M_Jayadwara_Master` + 4 MI;
    - mesh dengan Import Uniform Scale 45/1,90 ≈ 23,68 (placeholder D4; **diganti skala 1 di Iterasi 6**);
    - LOD1–3 + screen size, material per slot, rename `SKEL_`/`PA_`, dan socket.
  - [x] **Konvensi nama** `SKEL_`, `PA_`, `IK_`, `RTG_` ditambahkan ke [12](12-technical-design.md#konvensi-penamaan-aset).
  - **Asumsi yang belum diuji (risiko Iterasi 6):**
    - Interchange FBX di 5.6 dimatikan sementara lewat CVar `Interchange.FeatureFlags.Import.FBX`.
    - Nama API `SkeletalMeshEditorSubsystem.import_lod`, `SkeletalMesh.add_socket`, `AnimPoseExtensions`.
    - Konversi sumbu socket (x, −y, z) × 100.
    - Skala LOD ikut setelan import LOD0.
    - Setiap langkah yang gagal mencetak `[MANUAL]` dengan langkah pengganti.

### Iterasi 6 — Integrasi Unreal ✅
- **Prasyarat:** UE terpasang utuh, project C++ `Jayadwara` dibuat (Fase 0).
- **Developer (editor):** import FBX, atur Skeleton, Physics Asset kasar (kapsul per anggota badan), set Import Uniform Scale, material master, Anim Dynamics untuk rantai selendang/kain, IK Rig + Retargeter (Mixamo → Mannequin → Jayadwara).
- **Claude:** hubungkan `AJDGiantCharacter` (C++), nama socket di Anim Notify State hit detection, `UJDCombatProfile` skala raksasa, perbaiki script import.
- **Spike risiko:** impor mesh dengan tulang tambahan ke skeleton Mannequin → pastikan animasi Mannequin tetap jalan. Jika gagal: skeleton terpisah + IK Retargeter.
- **Gate:** pawn raksasa berjalan dengan animasi retarget; socket hit berfungsi; uji skala (±45 m) di level uji dengan gedung; target 60 FPS.
- **Hasil gate (12 Okt 2026): LULUS**, kecuali socket hit yang dipindah ke Fase 1 (butuh sistem combat; socket sudah ada).
- **Status (12 Okt 2026): sebagian besar dikerjakan Claude lewat Python Remote Execution** (`Tools/ue_remote.py`):
  - [x] **Bug export ditemukan & diperbaiki** (`05_export_fbx.py`), diuji dengan 7 varian FBX di UE 5.6.1. Penyebabnya:
    - objek armature `JD_Armature` jadi tulang root tambahan (skala 2368, roll 90°); UE hanya melewatinya kalau bernama `Armature`;
    - faktor unit FBX dan Import Uniform Scale masuk ke **skala tulang root**, bukan ke posisi tulang;
    - empty `SOCKET_*` ikut jadi tulang (99 tulang, bukan 89).
    - Perbaikan: salinan armature + mesh diskalakan ×100 dan di-apply (data dalam cm), salinan diberi nama `Armature`, `FBX_SCALE_ALL`, tanpa empty. Hasil: 89 tulang, root skala 1, 199 cm, menghadap +Y.
    - Validator 27/27 di keempat LOD (cek baru: nama `Armature`, tanpa empty; socket dibaca dari `_sockets.json`; satuan cm).
  - [x] **Import** (`Tools/ue_import_jayadwara.py`, skala import 1; sejak 6b FBX sudah 45 m): 17 tekstur, master + 4 MI (Cloth two-sided), LOD1–3 + screen size, `SKEL_`/`PA_`, 9 socket. Nama API & CVar Interchange dari Iterasi 5 terbukti ada. Perbaikan skrip:
    - socket: `socket_name`/`bone_name` read-only di Python → `set_socket_parent` lalu `rename_socket`;
    - elemen array struct (`materials`, `lod_info`) adalah salinan → dikumpulkan ke list baru lalu di-set.
  - [x] **Cek visual:** berdiri di z=0, emas tidak silver, permata & mata menyala, normal benar (`Saved/Screenshots/jd_*.png`).
  - [x] **Spike risiko diputuskan:** skeleton terpisah + IK Retargeter (orientasi tulang beda dari Mannequin; root roll 90° tidak masalah untuk retarget). `Tools/ue_setup_retarget.py` membuat `IK_Mannequin`, `IK_Jayadwara` (auto-characterize, 20 chain), `RTG_Mannequin_To_Jayadwara` (op stack default 5.6), `ABP_Jayadwara` + 24 animasi `_JD`. Pose hasil retarget selisih beberapa cm dari Manny.
  - [x] **`AJDGiantCharacter`** (C++): skala mesh, kapsul, kamera, step height dari `GiantHeightCm`; kecepatan/lompatan ×√skala dan animasi 1/√skala (skala Froude), BlendSpace raksasa ×√skala. `BP_Jayadwara`, `BP_JDGameMode_Giant`, level `Test_GiantScale` (`Tools/ue_setup_giant.py`). Uji PIE: jalan sampai 2.433 cm/s, tertahan gedung.
  - [x] Developer: main di `Test_GiantScale`, rasa gerak & kamera oke; 60 FPS oke; LOD tidak meloncat; tangan tidak menembus badan saat pukul (12 Okt 2026).
  - [x] **Physics Asset** dirapikan (`Tools/ue_setup_giant.py` + modul editor C++ `JayadwaraEditor`): 20 kapsul (pelvis, spine_01/03/05, neck, head, clavicle–upperarm–lowerarm–hand, thigh–calf–foot), 19 constraint Limited 30°, tanpa body selendang/kain/IK, tabrakan antar-body mati.
  - [x] **Foot IK Mannequin dilepas** dari `ABP_Jayadwara`: `CR_Mannequin_FootIK` (ikut dari ABP_Unarmed) membuat kaki mengangkang & telapak terpuntir karena orientasi tulang dan skala berbeda. Foot IK raksasa dibuat sendiri di Fase 1.
  - [x] **Skala raksasa di-bake ke mesh (Iterasi 6b, disetujui developer).** Upaya pertama (komponen mesh diskalakan 23,68) membuat Anim Dynamics rusak di semua mode: Component space meregang 3–5×, World space meregang saat bergerak, Actor space merusak skala tulang (panel kain hilang). Sekarang:
    - `16_make_lods.py` mem-bake `GIANT_HEIGHT_M / 1,90` lewat `BAKE_CM` di `05_export_fbx.py`; JSON socket berskala sama (`export_scale`); validator mengecek di skala authoring (28/28 di keempat LOD).
    - Di UE: mesh 47,1 m, root skala 1, 89 tulang; `AJDGiantCharacter::MeshHeightCm` = 4500 sehingga skala komponen 1.
    - Retarget: op **Run IK Rig dimatikan**. Di skala 45 m solver Full-Body IK menurunkan pinggul ±19 cm (setara skala manusia) dan menggeser badan; retarget FK murni cocok dengan Manny dalam beberapa cm.
  - [x] **Anim Dynamics selendang/kain** (4 rantai: `scarf_l/r` 6 tulang, `cloth_front/back` 3 tulang) di Component space, bola penolak di paha & betis, skala tulang tetap 1,0. Uji PIE: berayun saat berjalan, kembali tenang saat berhenti. Tuning di `Tools/ue_setup_giant.py`: `ACC_SCALE` 0,1 (0 = tenang, 0,15 = selendang terseret saat lari; ≥ 1 atau gravitasi Froude = terlempar ke atas karena waktu anim diperlambat 1/√skala).
  - [ ] Socket hit di Anim Notify State + `UJDCombatProfile`: menunggu sistem combat Fase 1.
  - Catatan teknis Iterasi 6:
    - Modul editor C++ `JayadwaraEditor` (`Source/JayadwaraEditor/`, `UJDEditorToolsLibrary`) dipakai skrip Python untuk hal yang tidak terjangkau API Python: `RebuildPhysicsAsset`, `AddAnimDynamicsChains`, `BypassAnimGraphNodes`, `RetargetAssetsToFolder`.
    - Batch retarget versi Python menaruh hasil di `/Game`; memindahkannya memutus rujukan ABP → animasi **di disk** (di memori tampak benar). `RetargetAssetsToFolder` menulis langsung ke `Anims/`; `ue_setup_retarget.py` mengecek isi file `.uasset` ABP.
    - Socket `hand_*`/`foot_*` bernama sama dengan tulangnya: `GetSocketLocation("foot_l")` mengembalikan socket (telapak), bukan sendi. Untuk posisi tulang pakai nama tulang tanpa socket atau `GetBoneLocation`.

### Iterasi 7 — Polish & varian *(opsional, Fase 2)*
Kepala hi-res untuk cutscene, polish/commission, recolor Dwarapala Kala & Kembar, slot sayap (Ep 38). **Peningkatan material** tanpa mengubah bentuk: ukiran emas organik (sculpt → normal map), keausan & kotoran di celah emas, tekstur kain/karet + jahitan di undersuit (arah stylized semi-realistis, 12 Okt 2026).

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
- Model Aksa (konsep: `concept-art/Aksa versi Final.png`, referensi: `concept-art/aksa_turnaround_v01.webp`; MetaHuman sebagai placeholder, lihat [12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)), Jerangkong, minion.
- Dwarapala Kala & Dwarapala Kembar (varian Jayadwara).
- Sayap (Ep 38), VFX kekuatan bumi (Ep 44).
- **Jubah upacara** — rencana iterasi di [26](26-rencana-jubah-jayadwara.md) (K9 [14](14-model-sheet-jayadwara.md), alur [07](07-gameplay-sistem.md#jubah-upacara)): mesh `SK_Jayadwara2_Cape` di skeleton Jayadwara2 (rantai `cloth_back_*` diperpanjang/dipecah), Chaos Cloth (hanya di luar combat), montage lepas ±2 s + versi cepat ±0,5 s + pakai kembali, Niagara buyar jadi cahaya; C++ `SetCapeEquipped` di karakter raksasa. Tombol manual (D-pad atas) opsional.
- Animasi silat final (Mixamo hanya untuk prototype).
