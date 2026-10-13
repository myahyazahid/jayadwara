# 21 — Model Sheet Aksa (Design Lock)

> Hasil **Iterasi 0** dari [19-rencana-model-aksa.md](19-rencana-model-aksa.md). Mengunci proporsi, palet, bagian, dan keputusan desain sebelum modeling.
> **Status:** draft (12 Okt 2026) — menunggu persetujuan developer pada bagian [7](#7-pertanyaan-untuk-developer). **Revisi setelah spike (12 Okt 2026):** model dibuat pada **H = 1,806 m** (tinggi Manny), semua ukuran konsep di bawah dikali **K = 1,032**; pose rest dan stance kaki mengikuti Manny (D1, D2). Angka diukur dari gambar AI beresolusi rendah (tinggi badan ±780 px di sheet → 1 px ≈ 2,2 mm) → akurasi ±2 cm, cukup untuk blockout, bukan untuk detail.
> Pola dokumen sama dengan [14-model-sheet-jayadwara.md](14-model-sheet-jayadwara.md).

---

## 1. Sumber & referensi

Sumber tunggal modeling: [`concept-art/aksa_turnaround_v01.webp`](concept-art/aksa_turnaround_v01.webp) (1774×887: depan, samping hadap kiri, belakang, kepala depan, kepala samping). `Aksa Final v2.png` adalah turnaround yang sama (isi identik secara visual, file beda). [`Aksa versi Final.png`](concept-art/Aksa%20versi%20Final.png) hanya acuan gaya, pose, dan ekspresi (serius / senyum / marah): gauntlet di sheet itu **dibuang**.

Semua file turunan dibuat ulang oleh `python -I Art/Scripts/make_reference_planes_aksa.py`.

| File (`Art/Reference/`) | Isi | Pemakaian |
|---|---|---|
| `ak_ref_front.png`, `ak_ref_side.png`, `ak_ref_back.png` | Tampak depan / samping (hadap kiri) / belakang. RGBA 760×1200, latar transparan | Reference plane di Blender. **1000 px = 1,75 m**, telapak sepatu di baris y=1100, garis tengah di x=380 |
| `ak_head_front.png`, `ak_head_side.png` | Kepala depan & samping (apa adanya) | Wajah, rambut, kerah |
| `ak_detail_collar.png` | Kerah berbatik, kaos, kalung, liontin | Kerah, kalung |
| `ak_detail_sash.png`, `ak_detail_sash_side.png` | Sabuk, simpul & selendang, kantong paha | Selendang, sabuk |
| `ak_detail_leg.png` | Kantong kargo + strap paha | Celana |
| `ak_detail_glove.png`, `ak_detail_boot_front.png`, `ak_detail_boot_side.png` | Sarung tangan, boots | Aksesori, sepatu |
| `ak_detail_emblem.png` | Emblem punggung + jahitan bahu | Jaket |
| `ak_palette.png` | Swatch palet hasil ukur | Warna |

**Cara normalisasi:** ketiga view digambar pada skala dan garis tanah yang sama (garis tanah y=823–824; sol boots menjorok ±4 px). Tinggi = telapak sepatu (y=827) → ujung rambut tertinggi (y=47). Garis tengah depan/belakang = rata-rata titik tengah kepala dan bahu; samping = titik tengah pinggul–betis. Landmark di bagian 2 sudah ditimpa ke ketiga view dan dicek (±1–2 cm).

**Keterbatasan:** bukan proyeksi ortografis sejati; figur sedikit bergeser ke kiri-gambar di depan (pusat sepatu ≈2 cm di kiri pusat kepala); beberapa detail tidak konsisten antar-view (bagian 5).

---

## 2. Proporsi (tinggi badan H = telapak sepatu → ujung rambut = **1,75 m** di konsep; **1,806 m** di model, ×1,032)

Tinggi kepala (ujung rambut → dagu) ≈ 0,225 m → **±7,8 kepala**: tungkai dan bahu mengikuti sheet, tidak dikoreksi ke 7,5.

### Tinggi (dari lantai)
| Landmark | Fraksi H | Tinggi (m) | Catatan |
|---|---|---|---|
| **Ujung rambut** (jambul tertinggi) | 1,000 | 1,75 | Kubah rambut tanpa jambul ±1,73 |
| Garis mata | 0,923 | 1,62 | |
| Dagu | 0,871 | 1,525 | Ujung kerah berdiri setinggi dagu |
| Garis bahu (jahitan bahu jaket) | 0,806 | 1,41 | |
| Pusat liontin | 0,743 | 1,30 | Rantai membentuk V dari leher |
| Ketiak | 0,709 | 1,24 | |
| Siku | 0,634 | 1,11 | Gulungan lengan jaket ±1,09 |
| **Sabuk (pusat)** | 0,603 | 1,055 | Tebal ±0,035 m |
| Ujung bawah jaket | 0,577 | 1,01 | Jaket pendek, di bawah sabuk |
| Pergelangan tangan (manset sarung tangan) | 0,543 | 0,95 | |
| Sendi pinggul | 0,514 | 0,90 | Estimasi |
| Selangkangan | 0,486 | 0,85 | Titik kaki berpisah di tampak depan |
| Ujung jari | 0,426 | 0,745 | A-pose |
| Ujung selendang | 0,30–0,31 | 0,52–0,54 | Depan ±0,54, samping/belakang ±0,52 |
| Lutut | 0,297 | 0,52 | |
| Bibir atas boots | 0,149 | 0,26 | Strap + gesper di sini |
| Pergelangan kaki | 0,063 | 0,11 | |

### Lebar & kedalaman
| Ukuran | Meter | Catatan |
|---|---|---|
| Lebar kepala (termasuk rambut) | 0,20 | |
| Kedalaman kepala (samping, termasuk rambut) | 0,23 | |
| **Bahu luar ke luar (jaket)** | 0,49–0,51 | Siluet V jelas |
| Dada (badan jaket, tanpa lengan) | 0,35 | |
| Pinggang / sabuk | 0,31–0,36 | |
| Kedalaman badan (dada, tanpa lengan) | ±0,24 | Dengan lengan di samping: 0,26–0,29 |
| Jarak pergelangan ke pergelangan (A-pose) | 0,68 | ±0,34 dari garis tengah |
| Rentang ujung jari kiri–kanan | 0,84 | |
| Pusat paha (di 0,69 m) | ±0,13 | |
| Lutut | ±0,15 | |
| Pergelangan kaki / pusat boots | ±0,215 / ±0,24 | Kaki mengangkang, boots menghadap keluar |
| Panjang telapak (boots) | 0,30 | Sol tebal ±0,04 |
| Lebar kaki celana di bawah (di atas boots) | 0,14–0,16 | Celana menumpuk di bibir boots |

**A-pose sheet:** lengan ±22° dari vertikal (bahu → pergelangan; lengan atas ±17°, lengan bawah ±26°), telapak ke paha. Beda dari prompt turnaround (35°) dan dari pose rest Mannequin; **sudut yang dipakai ditentukan di spike** ([19 §Temuan](19-rencana-model-aksa.md#temuan-iterasi-0-12-okt-2026)).

---

## 3. Palet warna

Median piksel pada area terfilter (`ak_palette.png`). "Usulan" = nilai awal untuk material stylized; sheet AI cenderung kusam, jadi usulan sedikit lebih jenuh. Final dituning di Iterasi 5 (docs spesifikasi material Aksa).

| Zona | Ukur (shadow / mid / highlight) | Usulan | Catatan |
|---|---|---|---|
| **Jaket navy** | `#23242B` / `#32323A` / `#3D3E46` | `#2B2E45` | Terbaca slate gelap, bukan biru terang. Jangan jenuh |
| **Kaos hitam** | `#181616` / `#2A2829` / `#302E2E` | `#1F1D1E` | |
| **Celana charcoal** | `#1E1A1B` / `#312E30` / `#413D3D` | `#2F2C2E` | Sedikit lebih terang dari kaos |
| **Kulit** (sawo matang) | `#A36D50` / `#C68965` / `#D39772` | `#C68965` | Wajah dan lengan sama |
| **Rambut** | `#111010` / `#232123` / `#393839` | `#1C1A1B` | Kilau tepi halus |
| **Batik** (kerah, selendang) | `#503221` / `#76543E` / `#B79071` | latar `#5A3B2B` + motif emas | Motif kawung/ceplok (bagian 6) |
| **Emas** | sheet `#C7986B` – `#DCB17E` | **`#D6A33A`** (`jd_common.HEX["gold"]`) | Emas sheet lebih pucat/peach. Pakai emas yang sama dengan Jayadwara, tapi **matte** (metalik rendah) |
| **Boots / sarung tangan** | `#110E0D` / `#23201F` / `#3D3837` | `#1A1817` | Trim emas |
| **Liontin** | abu batu, bingkai emas | `#6B6B6E` + emas | Tidak menyala di luar adegan transformasi |
| **Mata** | coklat | `#4A3426` | |

**Tanpa** silver/chrome dan **tanpa** biru menyala (palet "teknologi" di sheet lama dibuang).

---

## 4. Bagian (part list)

Anggaran tris mengikuti [19 §4](19-rencana-model-aksa.md#daftar-bagian--anggaran-poligon-lod0).

| Bagian | Bentuk & warna (dari sheet) | Pembawa detail |
|---|---|---|
| **Kepala** | Rahang tegas, hidung lurus, alis tebal lurus, mata coklat, ekspresi netral (mulut tertutup) | Morph target ekspresi |
| **Rambut** | Hitam pendek berantakan, helai berlapis seperti bulu, jambul mencuat ke atas, poni jatuh di dahi (sisi kanan karakter) | Gumpalan mesh; kilau tepi di tekstur |
| **Leher & lengan bawah** | Kulit terlihat dari leher, dan lengan bawah dari manset gulungan jaket sampai sarung tangan | Satu mesh ter-skin |
| **Kaos** | Hitam, leher bulat, terlihat di dada-perut karena jaket terbuka | |
| **Jaket** | Navy, pendek (sampai 1,01 m), **terbuka**: ritsleting emas di kedua tepi. Kerah berdiri melebar, lapisan dalam batik. Dua kantong dada bertutup + 2 kancing emas. Lengan digulung sampai bawah siku (manset dengan batang jahit emas). Pita jahit emas di yoke bahu. Motif emas (kuncup teratai/anak panah) di lengan atas kiri-kanan. Pita pinggang di ujung bawah. **Emblem emas di punggung** | Emblem & jahitan = relief tipis + tekstur |
| **Celana kargo** | Charcoal, kantong kargo bertutup di paha luar kiri-kanan, strap paha, kantong belakang, ujung menumpuk di bibir boots | Kantong = geometri; strap = geometri tipis |
| **Sabuk** | Kulit hitam, gesper persegi emas (motif silang), simpul selendang di pinggul kiri-depan dengan cincin emas | |
| **Selendang** | Batik coklat-emas, lebar ±0,10 m, simpul di pinggul kiri-depan, menjuntai di sisi kiri paha sampai ±0,52–0,54 m, ujung runcing | **Rantai tulang** `sash_01..06` |
| **Kalung** | Rantai emas tipis berbentuk V; liontin = pecahan batu abu bingkai emas (±4×2 cm) | Menempel ke leher/dada (`neck_01`/`spine_05`) |
| **Sarung tangan** (×2) | Hitam, **tanpa jari** (ujung jari & ibu jari terbuka), manset ber-strap | Ter-skin |
| **Boots** (×2) | Hitam, tinggi ±0,26 m, tali + kait cincin emas, strap + gesper emas di bibir, sol tebal bergerigi, trim emas di sol dan ujung | Sol + strap kaku; bibir ter-skin |

---

## 5. Keputusan desain (design lock)

Titik di mana sheet **tidak konsisten**, **bertentangan dengan aturan IP**, atau perlu diputuskan. Semua berstatus **usulan — menunggu persetujuan**; tanpa jawaban, D1–D10 dipakai sebagai default di Iterasi 1.

| # | Titik | Temuan di sheet | Usulan |
|---|---|---|---|
| **D1** | Tinggi & proporsi | Sheet ±7,8 kepala; prompt turnaround minta 7,5; konsep 175 cm | **180,6 cm = tinggi Manny (A3 revisi, spike 12 Okt 2026), proporsi mengikuti sheet** (bukan prompt), seluruh ukuran ×1,032. Tinggi tidak bisa diubah lewat skala impor di UE 5.6.1 |
| **D2** | Sudut A-pose | Sheet ±22°, prompt 35°, Mannequin berbeda lagi | Model mengikuti **pose rest Manny** (terukur di spike): lengan atas 35° dan lengan bawah 53° dari vertikal (tangan 16 cm di depan badan), pinggul ±0,100 m, lutut ±0,123 m, pergelangan kaki ±0,141 m. Reference plane hanya acuan volume, bukan sudut atau stance; konsekuensinya IoU siluet penuh 0,61–0,79 tapi IoU badan 0,80–0,88 ([19](19-rencana-model-aksa.md) Iterasi 1) |
| **D3** | Posisi selendang | Depan: simpul di pinggul kiri-depan, menjuntai di depan paha kiri. Samping (hadap kiri): membentang dari depan ke belakang pinggul. Belakang: di sisi kiri pinggul | **Satu pita**: simpul di kiri-depan sabuk (`x=+0,09`, `y=-0,10`), jatuh di sisi **lateral** paha kiri, ujung runcing ±0,53 m. Tanpa ekor kedua. Rantai `sash_01..06` |
| **D4** | Kantong & strap | Kantong kargo di kedua paha luar; strap melintang jelas di paha kanan-karakter, tertutup selendang di kiri; belakang: kedua sisi | **Kedua paha**: satu kantong kargo bertutup + satu strap tiap sisi. Kantong belakang = tekstur saja |
| **D5** | Ekspresi | Wajah depan sedikit tersenyum miring; sheet final punya serius/senyum/marah | Model = **netral**. Senyum/marah lewat morph target (A4) dan potret dialog |
| **D6** | Emblem punggung | Ornamen emas simetris (bunga/mahkota kecil) | Tetap simetris, **kuncup teratai + sinar** (selaras dengan motif surya Jayadwara). **Tanpa sayap, tanpa paruh/kepala burung** (bukan Garuda); bukan logo tim serial Ultra. Relief tipis, matte |
| **D7** | Kalung | Rantai V + liontin batu abu bingkai emas | Statis, matte, ±4×2 cm. Cahaya hanya lewat VFX transformasi di socket `pendant`; **tidak berkedip, bukan timer** |
| **D8** | Warna emas | Emas sheet pucat/peach (`#C7986B`–`#DCB17E`) | Pakai emas Jayadwara `#D6A33A`, matte, supaya satu bahasa warna kedua wujud |
| **D9** | Kulit & baju | Kaos tertutup jaket, lengan bawah terbuka | Sesuai A6: kulit di bawah kaos/jaket/celana **dihapus**. Kulit hanya kepala, leher, lengan bawah, tangan |
| **D10** | Jaket | Terbuka, tanpa tudung, kerah melebar, lengan digulung | Jaket = **cangkang terpisah** setebal ±5 mm dengan lipatan di bahu/siku (geometri sedang). Hindari lipatan dalam yang menembus kaos |

---

## 6. Checklist IP & budaya (status desain terkunci)

| Aturan ([19 §8](19-rencana-model-aksa.md#8-checklist-ip--budaya-dipakai-di-setiap-gate)) | Status pada desain |
|---|---|
| Tanpa alat transformasi di lengan | ✅ Turnaround tanpa gauntlet/gelang; sarung tangan polos. ⚠️ Manset sarung tangan jangan diberi plat/ornamen yang terbaca sebagai brace |
| Kalung tidak menyala di luar adegan transformasi, bukan timer | ✅ D7 |
| Tanpa silver/chrome atau cahaya biru | ✅ Palet navy/hitam/emas/coklat. ⚠️ Pantau kilau sol boots (jangan terbaca silver) |
| Emblem punggung bukan Garuda, bukan logo tim serial Ultra | ✅ D6. ⚠️ Ornamen di sheet berbentuk mahkota melebar; jaga agar tidak membentuk sayap |
| Batik umum, bukan batik larangan | ➡️ Berlaku di Iterasi 5: kawung/ceplok/truntum; hindari parang rusak dan motif keraton terlarang ([06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)) |
| Pose uji & animasi tanpa silang lengan bentuk L | ➡️ Berlaku di uji pose Iterasi 1/4 |

---

## 7. Pertanyaan untuk developer

1. Setujui **D1–D10**, atau ubah yang perlu. (Tanpa jawaban, dipakai sebagai default.)
2. Setujui keputusan teknis **A1–A8** di [19](19-rencana-model-aksa.md) (khususnya **A1/A3**, lihat temuan di sana) dan jawab **A9**. Catatan Claude: permintaan "persiapan modeling Aksa" 12 Okt 2026 dibaca sebagai **A9 = mulai sekarang (jalur art paralel)**; roadmap belum diubah.
3. Perlu referensi tambahan? Yang belum ada: **belakang kepala/rambut** dan **3/4 wajah**. Prompt tambahan bisa ditambahkan ke `Art/Reference/prompt_aksa_turnaround.md`. Setelah spike, mungkin perlu turnaround ulang dengan sudut A-pose yang cocok dengan skeleton.
4. Izin memasang **MPFB2** (A2). Sumber unduhan dan lisensi aset (CC0) diverifikasi dulu sebelum dipasang; kalau ditolak, badan dibuat dengan skrip seperti Jayadwara.
