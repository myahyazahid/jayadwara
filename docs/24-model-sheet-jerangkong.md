# 24 — Model Sheet Jerangkong (Design Lock)

> Hasil **Iterasi 0** dari [20-rencana-model-jerangkong.md](20-rencana-model-jerangkong.md). Mengunci proporsi, postur, palet, potongan, dan keputusan desain sebelum modeling.
> **Status:** dipakai (12 Okt 2026). Developer menyukai desain Tripo tanpa revisi; S1–S12 dipakai sebagai default (status implementasi di akhir bagian 5). Angka diukur dari gambar AI beresolusi rendah (tinggi figur ±770 px di sheet → 1 px ≈ 2,9 mm) → akurasi ±2–3 cm, cukup untuk blockout, bukan untuk detail.
> Pola dokumen sama dengan [14](14-model-sheet-jayadwara.md) dan [21](21-model-sheet-aksa.md).

---

## 1. Sumber & referensi

Sumber tunggal modeling: [`concept-art/jerangkong_v01.webp`](concept-art/jerangkong_v01.webp) (1774×887: depan, samping hadap kiri, belakang, tengkorak 3/4, chart skala). Prompt: [`Art/Reference/prompt_jerangkong.md`](../Art/Reference/prompt_jerangkong.md).

Semua file turunan dibuat ulang oleh `python -I Art/Scripts/make_reference_planes_jerangkong.py`. Scene: `Art/Blender/jerangkong/jerangkong_v00_setup.blend` (`Art/Scripts/jerangkong_00_setup_scene.py`).

| File (`Art/Reference/`) | Isi | Pemakaian |
|---|---|---|
| `jk_ref_front.png`, `jk_ref_side.png`, `jk_ref_back.png` | Tampak depan / samping (hadap kiri) / belakang. RGBA 900×1200, latar transparan | Reference plane di Blender. **1000 px = 2,2 m**, telapak di baris y=1100, garis tengah di x=450 |
| `jk_head_34.png` | Tengkorak 3/4 close-up | Bintang model: retak, rongga mata, alis tulang, pecahan batu, akar |
| `jk_scale_chart.png` | Jerangkong vs Jayadwara | Hanya rasa skala; rasio di chart (±0,85×) **tidak dipakai** (lihat S1) |
| `jk_detail_skull_front.png`, `jk_detail_skull_side.png` | Tengkorak depan & samping | Bentuk tengkorak, rahang |
| `jk_detail_ribcage.png`, `jk_detail_spine_back.png` | Rusuk + tulang dada + energi; ruas belakang + belikat | Pelat rusuk, tulang belakang |
| `jk_detail_pelvis_cloth.png`, `jk_detail_cloth_back.png`, `jk_detail_cloth_side.png` | Panggul, simpul & kain batik | Kain |
| `jk_detail_arm_bracelet.png`, `jk_detail_wrist_bracelet.png` | Gelang perunggu lengan atas & pergelangan | Ornamen |
| `jk_detail_hand.png`, `jk_detail_hand_side.png` | Tangan jari panjang | Tangan |
| `jk_detail_knee.png`, `jk_detail_foot_front.png`, `jk_detail_foot_side.png` | Lutut + inti energi; kaki menggumpal tanah | Kaki |
| `jk_palette.png` | Swatch palet hasil ukur | Warna |

**Cara normalisasi:** ketiga view digambar pada skala dan garis tanah yang sama (garis tanah y=827–829, puncak tengkorak y=55–57 di ketiga view). Tinggi = telapak (y=827) → puncak tengkorak tampak depan (y=57). Garis tengah depan/belakang = rata-rata titik tengah tengkorak dan kedua telapak (figur sedikit asimetris); samping = titik tengah pergelangan kaki. Hanya lubang kecil (sela rusuk) yang diisi; celah lengan–badan tetap transparan. Plane dicek lewat render ortografis headless: telapak di z=0, puncak tengkorak & garis mata cocok dengan landmark.

**Keterbatasan:** bukan proyeksi ortografis sejati. Tampak samping memperlihatkan **bungkuk berlebihan** (tengkorak ±0,43 m di depan pergelangan kaki) padahal tinggi tengkorak sama dengan tampak depan; model memakai bungkuk sedang (S2), jadi plane samping hanya acuan volume tulang, bukan posisi kepala.

---

## 2. Proporsi (H = telapak → puncak tengkorak tampak depan konsep = **2,2 m**)

Tinggi tengkorak + rahang (puncak → dagu) ≈ 0,35 m → **±6,3 kepala** (tengkorak sengaja besar). Lengan lebih panjang dari tungkai: bahu → ujung jari 1,49 m, pinggul → telapak 1,27 m.

### Tinggi (dari lantai, tampak depan)
| Landmark | Fraksi H | Tinggi (m) | Catatan |
|---|---|---|---|
| **Puncak tengkorak** | 0,995 | 2,19 | Dengan bungkuk sedang turun ke ±2,15 (S2) |
| Garis mata (pusat rongga) | 0,905 | 1,99 | |
| Dagu (gigi bawah) | 0,836 | 1,84 | Rahang menempel ke dada (leher pendek terlihat dari depan) |
| Sendi bahu (kepala humerus) | 0,841 | 1,85 | Bahu terangkat setinggi dagu; puncak belikat ±1,90 |
| Gelang lengan atas | 0,736 | 1,60–1,64 | |
| Ujung bawah rusuk | 0,686 | 1,51 | Tulang dada berakhir ±1,55 |
| Puncak panggul (krista + simpul kain) | 0,632 | 1,39 | Ruas lumbar terlihat 1,39–1,51 |
| **Siku** | 0,605 | 1,33 | Kiri-gambar ±1,30, kanan ±1,36 (asimetri sheet) |
| **Sendi pinggul** | 0,577 | 1,27 | Inti energi merah |
| Gelang pergelangan | 0,377 | 0,81–0,85 | |
| **Lutut** | 0,348 | 0,765 | Inti energi merah |
| Pergelangan tangan | 0,341 | 0,75 | |
| Ujung kain depan (rata-rata) | 0,26 | 0,57 | Juntaian terpanjang ±0,52 |
| **Ujung jari** | 0,164 | 0,36 | Melewati lutut ±0,40 m |
| Pergelangan kaki | 0,091 | 0,20 | Gumpalan tanah mulai di sini |

### Lebar & kedalaman
| Ukuran | Meter | Catatan |
|---|---|---|
| Tengkorak: lebar / dalam / tinggi (dengan rahang) | 0,23 / 0,30 / 0,35 | Alis tulang menonjol; rongga mata besar |
| **Bahu luar ke luar** | 0,82 | Siluet lebar-atas |
| Rusuk (lebar / dalam) | 0,53 / ±0,40 | Dalam dengan belikat ±0,45 |
| Panggul (lebar krista) | 0,46 | |
| Sendi pinggul / lutut / pergelangan kaki dari garis tengah | ±0,25 / ±0,27 / ±0,30 | Kuda-kuda lebar (S3) |
| Siku / pergelangan dari garis tengah | ±0,48 / ±0,53 | Lengan menggantung sedikit terbuka |
| Rentang tangan kiri–kanan | 1,17 | |
| Panjang segmen | lengan atas 0,52 · lengan bawah 0,58 · tangan 0,39 · paha 0,50 · betis 0,57 | |
| Kaki (tanah ikut): panjang / lebar / tinggi | 0,57 / 0,36 / ±0,20 | Sangat besar: membuat raksasa "menapak" |
| Diameter batang tulang (dibuat tebal, docs/20 §4) | lengan atas ±0,08 · lengan bawah (radius+ulna) ±0,10 · paha ±0,09 · betis ±0,10 | Ujung sendi (epifisis) ±1,5× batang |

---

## 3. Palet warna

Median piksel pada area terfilter (`jk_palette.png`), ditulis shadow (p20) / mid / highlight (p80). "Usulan" = nilai awal material stylized; sheet AI cenderung kusam. Final dituning di Iterasi 4.

| Zona | Ukur (shadow / mid / highlight) | Usulan | Catatan |
|---|---|---|---|
| **Tulang terang** | `#A9876C` / `#AF8F73` / `#BB9B80` | `#BFA07C` | Hangat (gading–coklat), **bukan kemerahan** |
| **Tulang gelap** (celah, retak, rongga) | `#694E3A` / `#785A47` / `#866B57` | `#6E5240` | Lewat AO + mask retak |
| **Tanah** | `#39260D` / `#4C3923` / `#624C3A` | `#4A3622` | Kaki, sela sendi, rongga |
| **Lumut** | `#525639` / `#5F644C` / `#6F765D` | `#5E6B3E` | Tipis, di puncak tengkorak, bahu, sendi |
| **Kain dasar** | `#201716` / `#32241D` / `#3C362F` | `#3A2A20` | Lusuh, pudar |
| **Motif batik** | `#936A4D` / `#9F7658` / `#B5825C` | `#A8804F` | Coklat-emas pudar, **bukan emas metalik** |
| **Perunggu** (gelang) | `#505342` / `#5E5D4E` / `#707160` | patina `#4F6B5C` + rim `#8A6A3E` | Sheet: pita patina hijau-teal dengan tepi perunggu |
| **Merah Kala** (emissive) | glow `#B6352E` / `#C7433B` / `#DC554E` | dasar `#B0201A`, intensitas di UE | Merah gelap menyala; tidak ada biru/silver |

---

## 4. Potongan (part list)

Daftar & anggaran tris mengikuti [20 §4](20-rencana-model-jerangkong.md#daftar-potongan--anggaran-poligon-lod0). **Satu potongan boleh berisi beberapa tulang** (mis. tangan + jari), tetapi setiap vertex tetap tepat 1 tulang berbobot 1,0.

| # | Potongan | Bentuk (dari sheet) | Ukuran kunci |
|---|---|---|---|
| 1 | **Tengkorak** | Kubah besar sedikit lonjong ke belakang, alis tulang tebal, rongga mata dalam menyala, retak menyala dari ubun-ubun ke alis kanan-karakter (S10), 2 pecahan batu ukir tertanam di sisi kiri-karakter, akar tipis & lumut di puncak, tulang pipi lebar, hidung segitiga | 0,23 × 0,30 × 0,27 (tanpa rahang) |
| 2 | **Rahang** | Lebar, gigi besar rapat (deret blok, bukan gigi satu-satu), tertutup di pose rest | lebar ±0,17 |
| 3 | **Pelat rusuk** | 3 lapis per sisi + tulang dada panjang; **selangka & belikat** menumpuk berat di bahu (punuk di samping) | 0,53 × 0,40 × 0,35 |
| 4 | **Tulang belakang + leher** | Ruas tebal, ±5 ruas lumbar terlihat di depan, deretan prosesus besar di belakang; inti energi di sela ruas | ruas Ø ±0,09 |
| 5 | **Panggul + kain** | Krista lebar; kain dililit + disimpul di depan; panel depan & belakang berujung compang-camping; tali/strip di sisi | lebar 0,46 |
| 6–9 | **Lengan atas / bawah** | Batang tebal, epifisis membulat; radius+ulna = satu bentuk pipih dengan celah dangkal | 0,52 / 0,58 |
| 10–11 | **Tangan** | Besar, jari panjang 3 ruas, ujung tumpul (bukan cakar), ibu jari besar | 0,39 (pergelangan → ujung jari) |
| 12–15 | **Paha / betis** | Seperti lengan; tempurung lutut menonjol + inti energi | 0,50 / 0,57 |
| 16–17 | **Kaki** | Tulang telapak terkubur gumpalan tanah + akar; jari kaki pendek tebal mencuat; alas rata | 0,57 × 0,36 |
| — | **Gelang perunggu** (×4) | Lengan atas kiri-kanan (dengan ornamen tegak kecil) + pergelangan kiri-kanan; ikut potongan lengannya | Slot `Ornament` |
| — | **Inti energi Kala** | Bola/cakram menyala di sendi bahu, siku, pinggul, lutut, pergelangan; deret di sela ruas; isi rusuk; rongga mata; retak | Slot `KalaGlow`, ikut tulangnya |

---

## 5. Keputusan desain (design lock)

Semua berstatus **usulan — menunggu persetujuan**; tanpa jawaban, S1–S12 dipakai sebagai default di Iterasi 1.

| # | Titik | Temuan di sheet | Usulan |
|---|---|---|---|
| **S1** | Tinggi & skala | Chart ±0,85× hero; prompt ±0,7× | **H konsep 2,2 m** (J2). Boss ×14 ≈ 30 m tampak (bungkuk); minion ×0,85 ≈ 1,8 m. Rasio chart diabaikan |
| **S2** | Postur | Samping: tengkorak 0,43 m di depan pergelangan kaki tapi setinggi tampak depan | **Bungkuk sedang**: pusat tengkorak 0,22 m di depan, mata ±1,97 m (penanda `JK_TGT_*` di scene). Lumbar tegak, toraks condong ±20°, leher ±35°. Tengkorak tetap terjangkau pukulan Jayadwara |
| **S3** | Pose rest | Lengan menggantung sedikit terbuka; kuda-kuda lebar | **Pose rest = postur S2** (bungkuk sudah di rest, jadi animasi Manny hasil retarget otomatis tetap bungkuk). Lengan menggantung seperti sheet (siku ±0,48, pergelangan ±0,53), telapak menghadap paha. Pinggul ±0,25, lutut ±0,27, pergelangan kaki ±0,30. Retarget pose Manny diatur di `RTG_` (Iterasi 1 membuktikan) |
| **S4** | Tengkorak | ±6,3 kepala | Ukuran sheet dipertahankan; detail tertinggi di model. Retak & mata harus terbaca dari kamera raksasa |
| **S5** | Selangka & belikat | Menumpuk berat di bahu | Masuk potongan pelat rusuk secara visual, tapi bobotnya ke tulang `clavicle_l/r` (supaya bahu tetap bergerak dengan animasi). Saat rusuk rontok, bagian selangka ikut disembunyikan |
| **S6** | Rusuk | Satu per satu, banyak | **3 pelat per sisi** ([20 §4](20-rencana-model-jerangkong.md#daftar-potongan--anggaran-poligon-lod0)), celah antar-pelat cukup lebar agar inti energi di dalam terlihat |
| **S7** | Tangan | Jari panjang ramping, sedikit mencakar | Jari lebih tebal dari sheet (skala 31 m), ujung tumpul, bukan cakar; 5 jari × 3 ruas |
| **S8** | Kaki | Gumpalan tanah + akar besar | Tanah = geometri yang menyatu dengan tulang telapak; alas rata untuk kontak tanah; akar = tekstur + beberapa geometri |
| **S9** | Kain batik | Panel depan & belakang compang-camping, simpul depan, strip samping | Ujung compang-camping sebagai **geometri** (bukan masked/opacity) supaya murah di skala 31 m dan tetap 4 slot material. Panel depan & belakang = rantai `cloth_front/back_01..03` (J5) |
| **S10** | Retak titik lemah | Garis merah dari ubun-ubun turun ke alis kanan-karakter | Retak bergeometri (inset dalam) + emissive; socket `skull_weakpoint` di pusat retak; parameter `WeakPointPulse` |
| **S11** | Merah di permukaan tulang | Sheet mewarnai sebagian tulang bahu/sendi kemerahan (bisa terbaca darah) | **Merah hanya emissive** (inti, urat tipis, retak). Albedo tulang tidak boleh kemerahan; pendar merah ke tulang lewat cahaya/bloom, bukan tekstur |
| **S12** | Pecahan batu & akar | Batu ukir di tengkorak, paha, betis; akar menjuntai dari tengkorak | 2 batu di tengkorak + 1 di paha kiri; motif ukir **umum** (sulur/geometris), bukan relief candi tertentu. Akar: beberapa strip tipis di tengkorak & kaki |

---

### Status implementasi (jalur B, 12 Okt 2026)
Model memakai mesh Tripo developer ([20 Jalur B](20-rencana-model-jerangkong.md#jalur-b--basis-model-developer-tripo-ai-12-okt-2026)). S1 ✅ (×14 / ×0,85, dua aset). S2/S3 ✅ (pose rest = postur Tripo yang sudah bungkuk sedang; retarget hanya menyejajarkan lengan). S4 ✅ ukuran sheet. S5 ✅. S6: rusuk Tripo satu per satu (bukan pelat), tetap satu potongan. S7 ✅ jari kaku. S8/S9/S12 ✅ dari geometri Tripo (kain compang-camping bergeometri, gumpalan tanah, batu). S10 ⚠️ retak hanya tekstur + emissive (`Emit.G`, socket `skull_weakpoint`), belum bergeometri. S11 ✅ pendar dibatasi ke zona Kala, merah lain dinetralkan.

## 6. Checklist IP & budaya (status desain terkunci)

| Aturan ([20 §8](20-rencana-model-jerangkong.md#8-checklist-rating-budaya--ip-dipakai-di-setiap-gate)) | Status pada desain |
|---|---|
| Tanpa gore (daging, darah, organ, otot) | ✅ Sheet tanpa daging. ⚠️ S11: tulang kemerahan di sheet harus dibuang |
| Energi Kala merah gelap, tanpa biru/silver | ✅ Sheet hanya merah. ⚠️ Patina gelang hijau-teal: jaga agar tidak terbaca biru menyala (tidak emissive) |
| Batik umum, bukan batik larangan | ➡️ Iterasi 4: motif sulur/ceplok/kawung; hindari parang rusak & motif keraton terlarang ([06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)) |
| Tidak meniru monster kerangka IP lain | ✅ Pembeda: bungkuk + lengan panjang, kaki bergumpal tanah, kain batik, gelang perunggu, batu candi tertanam, retak menyala di dahi |
| Seram tapi terbaca (remaja) | ✅ Ekspresi dari rongga mata menyala + rahang; tanpa luka berdarah |

---

## 7. Pertanyaan untuk developer

1. Setujui **S1–S12**, atau ubah yang perlu. (Tanpa jawaban, dipakai sebagai default.)
2. Setujui keputusan teknis **J1–J8** di [20](20-rencana-model-jerangkong.md) dan jawab **J9**. Catatan Claude: permintaan "siapkan untuk modeling jerangkong" 12 Okt 2026 dibaca sebagai **J9 = mulai sekarang (jalur art paralel)**, sama seperti Aksa; roadmap belum diubah.
3. Perlu referensi tambahan? Yang belum ada: **tengkorak tampak atas/belakang**, **telapak tangan terbuka**, dan **versi minion** (prompt opsional di `prompt_jerangkong.md` §2).
