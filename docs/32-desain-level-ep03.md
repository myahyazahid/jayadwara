# 32 — Desain Level Ep 3: `Ep03_Adikara`

> **Status: v0.2, tata letak memanjang (17 Okt 2026), usulan.** Developer memilih map **memanjang barat → timur ala RE4** (alur terus maju, balik arah minim) menggantikan draf v01 plaza-tengah (1400 × 1050 m, gardu urutan bebas). Keputusan H1 sudah dijawab; H2–H8 menunggu developer (bagian 8).
> Rincian dari pola di [28](28-struktur-level-episode.md#ep-3--ep03_adikara--malam-lampu-kota-padam-bertahap), format sama dengan [30](30-desain-level-ep01.md) dan [31](31-desain-level-ep02.md).
> Sumber: [16 kartu Ep 3](16-panduan-arc-1.md#ep-3--lapar-listrik--jenglot) (isi episode), [16 bagian 4](16-panduan-arc-1.md#4-benang-merah-narasi) (benang merah), [02](02-setting-dunia.md) (Distrik Adikara). Skenario adegan Ep 3 belum ada di [17](17-skenario-arc-1.md), jadi urutan di sini juga jadi kerangka skenarionya.

**Visual:** [`visual/ep03-adikara.html`](visual/ep03-adikara.html) (buka di browser): denah berlapis, potongan memanjang dengan status lampu per tahap, potongan Menara Adikara, perbandingan tinggi, linimasa cahaya.

**Posisi di roadmap:** Ep 3 = Fase 4 ([10](10-roadmap.md#fase-4--produksi-season-1-ep-210-apr-2028--akhir-2029)). Dokumen ini **tidak memajukan jadwal**; tujuannya supaya kit Adikara (CBD) dan interior kantor dirancang sejak awal untuk dipakai ulang di Ep 10. Semua angka titik awal greybox; data generator (`Art/Level/ep03_*`) dan greybox belum dibuat.

---

## 1. Ringkasan

| | |
|---|---|
| Map | `Ep03_Adikara` · malam, lampu kota padam bertahap |
| Fokus episode | **Nadia** · benang utama: Teori energi Kala ● (Nadia menemukan pola energi), Entitas D ● (Ratna mulai menekan DWARA) |
| Medan | **2200 × 700 m** (x −1100 … +1100, y −350 … +350), alur barat → timur |
| Arena raksasa | **±1830 × 600 m** (x −750 … +1060, y −296 … +296); Jayadwara melintas memanjang ±26 detik |
| Boss | Jenglot 0,55× → 0,8× (**25 m → puncak 36 m**), tidak pernah setinggi Jayadwara 45 m |
| Minion | **Kabel hidup** (baru): cepat, rapuh, di lantai kantor |
| Mekanik baru | **Objektif lingkungan saat boss**: putus 3 gardu induk |
| Durasi | ±25–29 menit (tanpa wayang dan briefing di hub) |
| Kit baru | **Adikara (CBD)** + interior kantor |

**Prinsip v02:** satu jalur panjang seperti area RE4. Pemain selalu didorong maju: sebagai Aksa ke Menara Adikara, sebagai Jayadwara mengejar jenglot ke timur. Sektor di belakang pemain sudah gelap, sektor di depan masih menyala, jadi **cahaya sendiri yang menunjuk arah**. Kembali ke belakang tetap bisa (tidak ada dinding), tapi tidak ada yang perlu dicari di sana. Satu-satunya balik arah yang dirancang adalah lift pintas di dalam menara.

---

## 2. Tata letak v02 (17 Okt 2026)

```
   ░░░░░░░░░░░░░░░░░░░░░ MENARA KACA (latar, di luar batas) ░░░░░░░░░░░░░░░░░░░░░░░░
 ══╪══╪══╪══╪══╪══╪══ JALAN LAYANG TOL (batas utara, pilar tiap 60 m) ══╪══╪══╪══╪══╪══
 │ A · PINTU TOL │ PLAZA CBD  ▓MENARA│ SEKTOR KACA        │ SEKTOR APARTEMEN │ LAHAN    │≈│
 │ ruko 8–14 m   │ 300×300 m  ▓ADIKA-│ 60–180 m           │ 20–85 m          │ PROYEK   │K│
 │               │            ▓RA    │      [G1]▒kaca     │                  │ ADIKARA  │A│
 │ ● START ──── Jl. Adikara Raya ───▶▓══ boulevard = koridor aman ═════════════ [G3]   │N│
 │ ╲ pintu tol   │ ⊙ air mancur      │                    │  apt▒[G2]        │ fase 2 ◉ │A│
 │  ╲            │ ◎ Jayadwara muncul│                    │                  │          │L│
 ══════════════ REL LAYANG (batas selatan) ═══════════════════════════════════════════════
   ░░░░░░░░░░░░░░░░░░░░ KAMPUNG KALI (latar, Ep 2) ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
   ← barat                    alur pemain →                                     timur →
```

### Koordinat greybox v02 (meter, X timur, Y utara, titik nol = tengah jalur di Jl. Adikara Raya)

| Bagian | Pusat / rentang | Ukuran | Catatan |
|---|---|---|---|
| Latar menara kaca | y +320 … +350 | 60–200 m | Di luar batas |
| **Jalan layang tol** | y +300 … +320 | dek 15 m, pilar tiap 60 m | Batas utara; tidak hancur |
| **Rel layang** | y −300 … −312 | — | Batas selatan; Kampung Kali (Ep 2) di latar y < −312 |
| **Kanal Banjir Timur** | x +1060 … +1100 | lebar 40 | Batas timur; dangkal untuk raksasa, zona aman |
| Jl. Adikara Raya | y −12 … +12, x −1100 … +1060 | lebar 24 | Tulang punggung alur; di arena jadi **koridor aman** (boulevard) |
| Jalan sejajar | y +165 … +180 dan −165 … −180 | lebar 15 | Pembagi blok |
| Jalan melintang | x −110, +250, +695 | lebar 10–20 | Penanda batas sektor |
| **Pintu keluar tol** | lengkung dari (−1100, −255) ke (−1020, −12) | — | Kedatangan |
| START + mobil DWARA | (−1020, −20) | — | Barikade polisi di x −1050 |
| Zona A (ruko) | x −1100 … −750 | 8–14 m | Penalti tidak berlaku (di luar arena) |
| **Plaza CBD** | x −750 … −450, y −150 … +150 | 300 × 300 | Air mancur (−600, 0); zona aman |
| **Menara Adikara** | x −430 … −360, y −35 … +35 | 70 × 70, tinggi 220 m | **Tidak bisa hancur** (dipakai Ep 10/33); fasad retak scripted |
| Videotron | (−540, −120) | — | Berita Entitas D |
| **Sektor kaca** | x −300 … +250 | 60–180 m | Penalti tinggi (kaca mahal) |
| **G1** | (+100, +105) | 70 × 50, 30 m | Menara kaca 180 m di (+180, +105) |
| **Sektor apartemen** | x +250 … +690 | 20–85 m | Penalti tinggi (warga masih mengungsi) |
| **G2** | (+600, −100) | 70 × 50 | Apartemen 70 m di (+520, −100) |
| **Lahan proyek Adikara** | x +700 … +1060, y −280 … +280 | 360 × 560 | **Tanpa penalti**; 3 derek |
| **G3** (gardu induk utama) | (+900, +60) | 70 × 50 | Aman |

---

## 3. Zona dan alur pemain

| Zona | Lokasi | Waktu | Cahaya |
|---|---|---|---|
| Wayang + briefing | Hub Markas DWARA | 2–3 mnt | — |
| A. Pintu tol | x −1100 … −750 | ±2 mnt | 21.00, lampu jalan berkedip |
| B. Plaza + lobi + B1 | Plaza, menara L1/B1 | ±5–7 mnt | Menara redup |
| C. Lantai kantor | L20–22 | ±5–6 mnt | Gelap per lantai |
| C'. Ruang server | L50 | ±1 mnt | Gelap, percik listrik |
| D. Atap + transformasi | Atap menara | ±1 mnt | Kota masih menyala di timur |
| E. Arena (E1 → E2 → E3) | Plaza → kanal | ±7–9 mnt | Padam per sektor, lalu gelap total |
| Segel + debrief | Tepi kanal / hub | ±2 mnt | Lampu kembali dari timur ke barat |

### Wayang + briefing
- **Wayang (Ki Sastro):** jenglot sebagai sosok kecil kering yang disimpan sebagai jimat. Pemiliknya makin makmur, tapi jimat itu harus terus "diberi makan"; kalau lupa, ia mencari makan sendiri. Siluet wayang kecil menghisap cahaya pelita sampai padam.
- **Kol. Bagas:** Distrik Adikara mengalami pemadaman bergilir yang tidak tercatat PLN; petugas keamanan menara ditemukan lemas (H6).
- **Nadia (fokus):** konsumsi listrik menara melonjak lalu jatuh ke nol, berulang. "Seperti sesuatu yang sedang makan."
- **Ratna (pertama kali menekan):** Adikara Group keberatan DWARA masuk; rekaman Entitas D di Kampung Kali masih ramai. Akses diberikan dengan syarat tidak ada kerusakan.

### A. Pintu tol · ±2 menit
- Mobil DWARA berhenti di barikade polisi di pintu keluar tol. Aksa berjalan ±300 m ke timur di Jl. Adikara Raya (±1 menit pada 5 m/s, ditambah interaksi).
- **Landmark:** Menara Adikara berdiri tepat di ujung jalan, terlihat sejak START (kamera C1).
- **Scanner:** tiang lampu meredup berurutan ke arah menara. Nadia: "Ikuti arah tarikannya." Listrik di map ini adalah penunjuk arah.

### B. Plaza, lobi, B1 · ±5–7 menit
- Videotron di plaza memutar berita Entitas D lalu mati berkedip. Satpam Adikara yang tersisa menghalangi; Sekar mengirim surat akses Ratna.
- Lift penumpang mati; lift servis hanya sampai L20, sisanya dibuka per lantai (gerbang cerita ala keycard).

| # | Petunjuk | Lokasi | Isi |
|---|---|---|---|
| ★1 | Grafik konsumsi listrik (`Clue.Ep03.GrafikListrik`) | **B1 ruang kontrol listrik** | Lonjakan datang dari **3 gardu di timur**, bergiliran dan berirama seperti napas. Membuka lokasi gardu (objektif fase 1) dan awal "pola energi" Nadia |
| ★2 | Jimat pecah (`Clue.Ep03.JimatPecah`) | **L50 ruang server**, sesudah zona C (H4) | Inti tertinggal di jimat → menandai **inti di dada boss** (kelemahan fase 2) |
| ○ | Nota kolektor antik (`Clue.Ep03.NotaKolektor`) | **L38 lantai eksekutif**, cabang tangga darurat | Jenglot dibeli dari kolektor "untuk keberuntungan proyek", ditandatangani staf Adikara. Bestiary + catatan Sekar (benang uang Adikara ○) |

- **Kujang Aksa (H8):** di lemari koleksi L38 ada kujang yang bergetar saat didekati kalung Aksa. Menjawab "asal-usul kujang" yang belum diputuskan di [16 bagian Senjata](16-panduan-arc-1.md#senjata-usulan-developer-16-okt-2026-mulai-ep-3) dan memberi hadiah nyata untuk cabang opsional.

### C. Lantai kantor L20–22 · ±5–6 menit
- Gelap; cahaya dari monitor berkedip dan senter scanner. Kabel hidup keluar dari stop kontak dan plafon.
- Tiap lantai = satu gelombang. Setelah gelombang selesai, **Sekar membuka pintu tangga ke lantai berikutnya**.
- Di L22 Sekar menyalakan sebagian lift: **lift rusak jadi jalan pintas turun** (satu-satunya balik arah yang dirancang; dipakai untuk ke L38 atau saat mengulang).
- **Checkpoint:** awal L20, setelah L22.

### C'. Ruang server L50 · ±1 menit
- Aksa tiba saat jimat sudah pecah. Jenglot kecil menempel di trafo, menghisap, lalu **menjebol dinding kaca** dan melompat ke plaza. Fasad menara retak: **kerusakan pertama di gedung Adikara** (scripted; menara tetap tidak bisa hancur saat gameplay).

### D. Atap · ±1 menit
- Dari atap 220 m Aksa **menghadap timur**: jenglot membesar di plaza, sulur kabel merambat ke arah tiga gardu yang berderet menyala sepanjang jalur. Pemain melihat seluruh sisa level dari satu titik (garis pandang).
- **Transformasi di atap (H5):** gestur Lawang Terbuka, lalu Jayadwara muncul lewat gerbang cahaya di plaza (−650, −40).

### E. Arena raksasa · ±7–9 menit

| Bagian arena | Meter | Catatan |
|---|---|---|
| Plaza, boulevard (Jl. Adikara Raya), kanal | **Zona aman** | Boulevard = koridor aman untuk mengejar tanpa menginjak gedung |
| Lahan proyek Adikara | **Tanpa penalti** | Derek tumbang bebas |
| Sektor kaca | **Penalti tinggi** | Kaca mahal; G1 nempel menara 180 m |
| Sektor apartemen | **Penalti tinggi** | Warga mengungsi lewat boulevard (Ratna di koms) |
| Sisa blok di sekitar plaza | Penalti normal | — |
| Menara Adikara, jalan layang tol, rel layang | Tidak hancur | — |

- **Pembuka, jurus #1 gagal:** saat boss pertama kali stagger, sang penjaga mendorong Braja Lawang. Petirnya **diserap**, boss naik satu tahap. Nadia: "Jangan beri dia listrik! Putus sumbernya." Scripted sekali.
- **Fase 1, putus gardu berurutan (H3):** jenglot lari ke timur untuk "makan" gardu berikutnya; pemain mengejar.
  - **E1 · sektor kaca:** jenglot menghisap G1 dan mencapai puncak 36 m. Cabut G1 tanpa menjatuhkan menara kaca 180 m di sebelahnya. Sektor barat gelap, jenglot kabur.
  - **E2 · sektor apartemen:** warga masih mengungsi lewat boulevard; terburu-buru menurunkan meter. Cabut G2, jenglot menyusut ke 31 m dan lari ke lahan proyek.
  - **E3 · lahan proyek:** G3 di area tanpa penalti, jeda untuk bebas merusak.
  - Pertumbuhan boss dibatasi per tahap, **tanpa timer** (aturan IP, [16](16-panduan-arc-1.md#ep-3--lapar-listrik--jenglot)).
- **Fase 2, gelap total di tepi kanal:** jenglot 27 m mengamuk. **Satu-satunya cahaya adalah inti di dadanya** (★2). Tanpa ★2, inti hanya terlihat sekilas saat boss menyerang.
- **Keris Jayadwara (H7):** muncul di fase 2. Petir tidak berguna, jadi sang penjaga memanggil keris pusaka dari kalung; finisher = tusukan ke inti dada.
- **Checkpoint:** awal E1, setelah G2, awal fase 2.
- **Kalah sebagai Jayadwara:** Aksa muncul di tempat; lobi gedung dan kolong jalan layang jadi tempat berlindung skala manusia.

### Segel + debrief · ±2 menit
- Segel di tepi kanal. Lampu kembali menyala **dari timur ke barat**, dari tempat pemain berdiri sampai Menara Adikara.
- **Nadia (beat utama):** lonjakan di 3 gardu berirama sama dengan bacaan di Ep 1 dan Ep 2. "Energi Kala bukan acak. Ada polanya."
- **Ratna (beat utama):** berita malam menayangkan Entitas D di CBD dan fasad menara yang retak; Gunadi Adikara mengeluh di TV. Ratna menekan Kol. Bagas.
- **Unlock:** jurus spesial #2 (desain gerak di Fase 4) + senjata.

---

## 4. Interior Menara Adikara

Hanya lantai yang dimainkan yang dibangun; lantai lain dilewati tangga darurat atau lift (H2).

| Lantai | Ketinggian | Isi |
|---|---|---|
| Atap | 212–220 m | Zona D, garis pandang ke timur |
| L50 ruang server | 200–212 m | ★2, jenglot kabur |
| L38 lantai eksekutif | 150–158 m | ○ nota kolektor, kujang (H8); cabang tangga darurat |
| L20–22 lantai kantor | 80–92 m | Zona C, 3 gelombang kabel hidup |
| L1 lobi | 0–8 m | Masuk dari plaza |
| B1 ruang kontrol listrik | −8–0 m | ★1 |

---

## 5. Skala

| Objek | Tinggi | Catatan |
|---|---|---|
| Aksa | 1,75 m | |
| Kabel hidup | ±2,5 m | Panjang saat menjulur |
| Jalan layang tol | 15 m | |
| Jenglot fase 1 / puncak / fase 2 | 25 / 36 / 27 m | 0,55× → 0,8× |
| Gardu induk | 30 m | |
| Jayadwara | 45 m | |
| Apartemen | 20–85 m | |
| Perkantoran | 45–110 m | |
| Menara kaca | 60–180 m | |
| Menara Adikara | 220 m | |

Ep 3 adalah arena pertama yang sebagian besar gedungnya lebih tinggi dari Jayadwara: pertarungan terasa "sempit ke atas", dan boulevard jadi ruang gerak utama.

---

## 6. Kit dan pakai ulang

| Level Instance | Isi | Dipakai ulang |
|---|---|---|
| `LI_Adikara_Plaza` | Plaza, air mancur, videotron, Menara Adikara (eksterior) | Ep 10, Ep 33 |
| `LI_Adikara_BlokKaca` | Blok menara kaca modular | Ep 10 |
| `LI_Adikara_BlokApartemen` | Blok apartemen modular | Ep 10 |
| `LI_Adikara_Gardu` | Gardu induk (bisa dicabut) | Ep 10 |
| `LI_Adikara_InteriorKantor` | Lobi, B1, lantai kantor, eksekutif, server | Ep 33 |
| `LI_Adikara_JalanLayang` | Tol layang + pintu tol | Ep 2 (latar), Ep 10 |

**Sistem baru episode ini** ([16 bagian 2.2](16-panduan-arc-1.md#22-anggaran-produksi-per-episode-ep-210): maks 1): **objektif lingkungan saat boss** (gardu yang bisa dicabut + boss yang tumbuh/menyusut per tahap + sektor lampu). Dibuat generik karena dipakai ulang di Ep 4 (lilin ritual) dan Ep 17 (sumber kutukan, [29](29-struktur-level-arc-2.md)).

---

## 7. Arsip: draf v01 (17 Okt 2026)

Plaza CBD di tengah medan 1400 × 1050 m, Menara Adikara di utara plaza, tiga gardu di tiga sektor sekeliling plaza dengan urutan bebas, batas utara menara kaca dan selatan jalan layang. Diganti v02 karena developer ingin alur yang terus maju ala RE4.

---

## 8. Keputusan

| # | Pertanyaan | Status |
|---|---|---|
| **H1** | Map memanjang barat → timur ala RE4 (2200 × 700 m), menggantikan v01 plaza-tengah? | ✅ **Ya** (developer, 17 Okt 2026) |
| **H2** | Interior menara cukup 4 set lantai (B1+L1, L20–22, L38, L50+atap)? | Usulan: ya |
| **H3** | Gardu berurutan G1 → G2 → G3 (kartu [16](16-panduan-arc-1.md#ep-3--lapar-listrik--jenglot) belum menyebut urutan)? | Usulan: ya, konsekuensi H1 |
| **H4** | ★2 dipindah ke ruang server L50, sesudah zona C (di [28](28-struktur-level-episode.md#ep-3--ep03_adikara--malam-lampu-kota-padam-bertahap) ★2 ada di zona B)? | Usulan: ya |
| **H5** | Transformasi di atap, Jayadwara muncul di plaza? | Usulan: ya |
| **H6** | Korban di briefing: petugas lemas, bukan tewas? | Usulan: ya |
| **H7** | Keris Jayadwara muncul di fase 2 sebagai finisher, atau baru dibuka di debrief? | Usulan: fase 2 |
| **H8** | Kujang Aksa ditemukan di koleksi L38, atau dibuat Nadia? | Usulan: L38 |
