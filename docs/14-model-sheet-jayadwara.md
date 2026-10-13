# 14 — Model Sheet Jayadwara (Design Lock)

> **13 Okt 2026:** model aktif kini Jayadwara2 ([25](25-rencana-redesign-jayadwara.md)). Identitas desain (palet merah-hitam-emas, faceplate putih, tanduk emas, permata dada statis, kain sisi = selendang K5, batas IP) tetap berlaku; angka proporsi dan part list di sini milik model lama.

> Hasil **Iterasi 0** dari [13-rencana-model-jayadwara.md](13-rencana-model-jayadwara.md). Dokumen ini mengunci proporsi, palet, bagian, dan keputusan desain sebelum modeling.
> **Status:** draft — menunggu persetujuan developer pada bagian [8](#8-pertanyaan-untuk-developer). Angka diukur dari gambar AI beresolusi rendah (tinggi badan ±360 px) → akurasi ±3 cm, cukup untuk blockout, bukan untuk detail.

---

## 1. Sumber & referensi

Sumber tunggal: [`concept-art/jayadwara_final.webp`](concept-art/jayadwara_final.webp). Semua file turunan dibuat ulang oleh script `Art/Scripts/make_reference_planes.py`.

| File (`Art/Reference/`) | Isi | Pemakaian |
|---|---|---|
| `jd_ref_front.png`, `jd_ref_side.png`, `jd_ref_back.png`, `jd_ref_34.png` | Tampak depan / samping (hadap kiri) / belakang / 3/4. RGBA 760×1200, latar transparan | Reference plane di Blender. **1000 px = 1,90 m**, telapak kaki di baris y=1100, tengah badan di x=380 |
| `jd_head_detail.png` | Detail kepala | Bentuk helm, tanduk, faceplate |
| `jd_detail_chest.png`, `_shoulder`, `_belt`, `_leg` | Detail dada, bahu, sabuk & kain, kaki | Bentuk armor |
| `jd_hero_pose.png` | Pose aksi | Bahasa bentuk, arah kain saat bergerak |
| `jd_palette.png` | Swatch palet | Warna |

**Keterbatasan:** keempat view digambar pada skala sama dan sejajar (diverifikasi), tapi bukan proyeksi ortografis sejati dan antar-view ada ketidakkonsistenan (lihat bagian 5). Referensi pengganti yang lebih baik: bagian 7.

---

## 2. Proporsi (tinggi badan H = telapak kaki → puncak helm tanpa tanduk = **1,90 m**)

Tinggi kepala ±0,124 H → **±8 kepala** (ramping-atletis, cocok dengan aturan retarget Mannequin).

### Tinggi (dari lantai)
| Landmark | Fraksi H | Tinggi (m) | Catatan |
|---|---|---|---|
| Puncak tanduk | 1,045 | 1,99 | +0,09 m di atas helm (keputusan K4) |
| **Puncak helm** | 1,000 | 1,90 | |
| Ujung duri pauldron | 0,881 | 1,67 | Setinggi dagu |
| Dagu (bawah faceplate) | 0,876 | 1,66 | Leher hampir tak terlihat (kerah tinggi) |
| Garis bahu | 0,843 | 1,60 | |
| Pusat permata dada | 0,779 | 1,48 | Ornamen dada ±0,82 → 0,69 H |
| Ketiak | 0,724 | 1,38 | |
| Siku | 0,68 | 1,30 | |
| **Sabuk (pusat)** | 0,621 | 1,18 | Tebal ±0,06 H |
| Pergelangan tangan | 0,552 | 1,05 | |
| Ujung kepalan | 0,478 | 0,91 | Konsep; usulan K7: 0,44 H = 0,84 m |
| Sendi pinggul | ≈0,47 | ≈0,89 | Estimasi (tertutup kain) |
| Lutut (pusat) | 0,312 | 0,59 | Pelindung lutut berlian |
| Pergelangan kaki | 0,068 | 0,13 | |
| Tepi bawah kain (depan/samping/belakang) | 0,25–0,26 | 0,48–0,50 | Pertengahan betis |

### Lebar & kedalaman
| Ukuran | Fraksi H | Meter |
|---|---|---|
| Lebar helm (tanpa tanduk) | 0,116 | 0,22 |
| Rentang ujung tanduk | 0,138 | 0,26 |
| **Pauldron luar ke luar** | 0,332 | 0,63 |
| Dada (pelat armor) | ≈0,19 | ≈0,36 |
| **Pinggang / sabuk** | 0,158 | 0,30 |
| Rentang maks. kain sisi | 0,398 | 0,76 |
| Jarak luar ke luar kedua kaki (berdiri) | 0,38 | 0,72 |
| Kedalaman dada (samping, termasuk pauldron) | 0,175 | 0,33 |
| Panjang telapak kaki | 0,185 | 0,35 |
| Tinggi sepatu (sol → kerah pergelangan) | 0,12 | 0,22 |

Siluet: **V kuat** (bahu 0,63 m vs pinggang 0,30 m → rasio ±2,1), kain bersudut melebar di bawah.

---

## 3. Palet warna

Diukur dari swatch dan dari piksel figur (nada shadow / mid / highlight). Angka "Usulan" = nilai awal untuk material stylized (boleh di-tuning).

| Zona | Swatch sheet | Shadow | Mid | Highlight | Catatan |
|---|---|---|---|---|---|
| **Merah** | `#A92826` | `#581415` | `#852323` | `#B8362F` | Glossy, bidang besar |
| **Emas** | `#BD8F56` | `#78502A` | `#B28047` | `#E8B876` | Emas hangat/antik (bukan kuning murni, **bukan silver**) |
| **Hitam (undersuit)** | `#332E2E` | `#1B1110` | `#332E2E` | `#4A4040` | Ada pola kisi halus |
| **Putih (faceplate)** | `#DBD9DA` | `#B0ABA8` | `#DBD9DA` | `#F2EEEA` | Keramik bersih |
| **Marun** | `#422628` | — | `#422628` | — | Bagian dalam/lapis bawah kain, aksen |

**Emissive (konstan):** permata dada inti `#FFEFB9` / halo `#E3A66F`; mata inti putih hangat `#FFF4D6` / halo `#FADCA4`.

---

## 4. Bagian (part list)

Ukuran/tris mengikuti [13](13-rencana-model-jayadwara.md#daftar-bagian-part-list--anggaran-poligon-lod0). Berikut deskripsi bentuk dari konsep:

| Bagian | Bentuk & warna | Pembawa detail |
|---|---|---|
| **Helm** | Kubah merah bersudut dengan rusuk tengah; "sirip" merah menyapu ke belakang-bawah di pelipis; pelindung alis emas berbentuk V dari dahi turun ke mata | Garis alur di kubah |
| **Tanduk** (×2) | Emas, tumbuh dari sisi pelindung alis, melengkung ke atas-luar, meruncing | Alur emas halus |
| **Ornamen dahi** | Pelat emas bentuk tetesan, motif ukiran (relief) | Relief + normal map |
| **Faceplate** | Pelat putih bentuk V sempit di bawah mata, dagu merah runcing ("paruh"), pipi merah di sisinya | Garis ukiran tipis |
| **Mata** | Celah miring menyala | Emissive |
| **Pelat dada** | Merah, chevron V emas besar, permata berlian di tengah dikelilingi gulungan emas; chevron kedua di perut | Relief + normal |
| **Pauldron** (×2) | Emas berlapis, cangkang membulat dengan duri di atas, ukiran gulungan awan; merah di bawah | Relief + normal |
| **Bracer** (×2) | Pelat merah-emas di lengan bawah, melebar ke luar | |
| **Sarung tangan** (×2) | Hitam, jari ter-skin | |
| **Sabuk** | Ikat lebar merah dengan pita emas bermotif, gesper berlian emas di tengah | Motif tekstur |
| **Kain depan** | Panel merah panjang, tepi emas, motif ukiran di ujung bawah | Tekstur |
| **Kain sisi / selendang** (×2) | Helai panjang runcing bertepi emas, mengembang ke samping, melambai saat bergerak | Rantai tulang |
| **Kain belakang** | Panel tengah bermotif emas di ujung | Rantai tulang |
| **Pelindung paha/lutut** | Pelat merah di paha luar; pelindung lutut berlian emas | |
| **Greaves** | Merah ramping dengan sisi dalam hitam, trim emas | |
| **Sepatu** | Merah, ujung runcing sedikit, pelat berlian di punggung kaki, sol hitam tebal | |
| **Undersuit** | Hitam ramping, terlihat di sisi dada, bagian dalam lengan & paha | Pola kisi |

---

## 5. Keputusan desain (design lock)

Titik di mana sheet **tidak konsisten** atau **bertentangan dengan aturan IP**, beserta usulan. Semua berstatus **usulan — menunggu persetujuan**.

| # | Titik | Temuan di sheet | Usulan |
|---|---|---|---|
| **K1** | Ornamen dada | Konsep: chevron V + permata berlian + gulungan. Teks docs/08: "motif surya". Sheet "Armor Concept Sheet" (bukan final) memakai bintang surya berpendar | Pakai **chevron V + permata berlian + gulungan** (sesuai final). Tambahkan **ukiran sinar surya halus** di sekeliling permata (relief, tidak menyala) untuk memenuhi "motif surya". Bintang berpendar **ditolak** (mirip lampu dada) |
| **K2** | Faceplate | Pelat putih bentuk V di bawah mata, dagu merah runcing | Pelat putih tetap **sempit** (hanya tengah wajah); pipi **merah** bersudut; **tanpa celah/garis mulut**; punggungan tengah halus; dagu "paruh" merah. Bentuk ini yang membedakan dari wajah Ultra |
| **K3** | Dahi / Kala-Bhoma | Ornamen emas bentuk tetesan bergaya bunga/ukiran; docs/08 minta "motif Kala-Bhoma" | Bentuk pelat tetesan tetap; **relief** diukir bergaya Kala-Bhoma abstrak (simetris, alis-taring disederhanakan, gulungan). Matte, **tanpa permata/kristal, tanpa emissive** |
| **K4** | Tanduk | Turnaround: pendek (ujung ±0,36 tinggi kepala di atas puncak helm). Detail kepala & pose hero: besar, menyapu. Ukuran berbeda-beda | Ikuti keduanya di tengah: **ujung ±0,09 m di atas puncak helm (1,99 m)**, panjang sepanjang kurva ±0,30 m, tumbuh dari **sisi pelindung alis**, melengkung ke atas-luar, **penampang tebal runcing** (bukan bilah pipih). Rentang ujung ±0,26–0,28 m |
| **K5** | Struktur kain | Turnaround: panel depan + sayap sisi + panel belakang. Pose hero: dua helai panjang melambai. Sheet tidak menggambar selendang terpisah | **Tidak ada selendang terpisah.** Sayap sisi = selendang. Kain: 1 panel depan, 2 helai sisi panjang (selendang), 1 panel belakang, semua berujung runcing bertepi emas. Rantai tulang: `scarf_l/r_01…06`, `cloth_front_01…03`, `cloth_back_01…03` |
| **K6** | Mata & permata | Mata menyala miring; permata dada menyala | Mata **celah sempit miring** (lebar:tinggi ≥ 3:1), bukan oval besar. Permata ≤ 0,11 m, emissive **konstan**; tidak berkedip dan **tidak dikaitkan ke meter Sync** |
| **K7** | Panjang lengan | Ujung kepalan di 0,478 H (setinggi selangkangan) → lengan terlalu pendek untuk manusia & jangkauan pukulan | Panjang lengan **+10%** → ujung kepalan ≈ 0,44 H (0,84 m); siluet lain tetap |
| **K8** | Pose rest model | Sheet berpose lengan sedikit terbuka | **A-pose** — lengan ±30° dari tubuh, telapak ke paha. Kaki **melebar seperti di konsep** (diukur dari reference plane): sendi pinggul ±0,10 m, lutut ±0,18 m, pergelangan kaki ±0,24 m; sepatu menghadap keluar ±8°. Dicek lagi terhadap Mannequin saat UE ada. *(Revisi Iterasi 1: sebelumnya "±35°, kaki selebar bahu" — salah baca ukuran lebar kaki dan lengan 30° menjatuhkan pergelangan tepat di landmark 1,05 m.)* |

---

## 6. Checklist IP & budaya (status desain terkunci)

| Aturan | Status pada desain |
|---|---|
| Tanpa lampu/timer dada | ✅ Permata statis, tertanam di chevron (K1, K6). ⚠️ Pantau: jangan terlalu terang/bulat |
| Tanpa kristal dahi | ✅ Relief emas matte (K3) |
| Tanpa bilah kembar di atas kepala | ✅ Tanduk dari sisi alis, melengkung, penampang tebal (K4). ⚠️ Cek siluet dari belakang |
| Tanpa mata lensa besar | ✅ Celah sempit (K6) |
| Tanpa badan merah-silver | ✅ Merah/hitam/emas; tidak ada silver |
| Tanpa emblem garuda | ✅ Tidak ada |
| Faceplate putih ≠ Ultra | ⚠️ Titik paling dekat — K2 membedakan bentuk; **ulangi cek tiap gate** |
| Pose/jurus bukan Specium Ray | ➡️ Berlaku di fase animasi: hindari silang lengan bentuk L |
| Batik: motif umum | ➡️ Berlaku di Iterasi 4: kawung/ceplok; hindari batik larangan keraton (mis. parang rusak) |
| Kala-Bhoma dihormati | ➡️ Digambarkan sebagai kekuatan kosmik, bukan monster (docs/06) |

---

## 7. Referensi pengganti (disarankan)

Minta generator gambar membuat tiga view ortografis pose-A. Contoh prompt (lampirkan `jayadwara_final.webp` sebagai acuan desain):

```
Character model sheet of the armored tokusatsu hero "Jayadwara", exactly matching the attached
design (red angular helmet with two large curved golden horns, white V-shaped faceplate with
narrow slanted glowing eyes, red chevron chest armor with a gold diamond gem, gold carved
pauldrons, black undersuit, red belt with gold buckle, long pointed red sashes with gold trim).
Three views: front, side (facing left), back. Neutral A-pose: arms about 30 degrees from the
body, palms toward the thighs, legs slightly apart (ankles about 0.5 m from each other), feet pointing forward. Strict orthographic projection, no
perspective, no foreshortening, all views at the same scale with feet and head on the same
lines. Full body head to toe. Plain flat light-gray background, no text, no cast shadow.
Eight-heads-tall slim athletic proportions. High resolution, at least 2048 px tall per view.
```

---

## 8. Pertanyaan untuk developer

1. Setujui K1–K8, atau ubah yang perlu. (Tanpa jawaban, **K1–K8 dipakai sebagai default** saat Iterasi 1.)
2. Mau buat referensi pose-A baru (bagian 7)? Jika ya, kirim ke `Art/Reference/` dan script dijalankan ulang; jika tidak, Iterasi 1 memakai referensi yang ada.
3. Siapa yang mereview desain dari sisi budaya (Kala-Bhoma, batik)? Cukup dicatat; reviewnya sebelum rilis, bukan sekarang.
