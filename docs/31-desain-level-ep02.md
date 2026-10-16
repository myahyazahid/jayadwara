# 31 — Desain Level Ep 2: `Ep02_KampungKali`

> **Status: v0.3, tata letak v02 (16 Okt 2026)**: developer menilai map v01 (600 × 500 m) terlalu kecil untuk Jayadwara yang gesit (±70 m/s, PR #29) dan memilih **opsi B: perluas + area baru** (bagian 2a). Angka di bagian 2 adalah **v01 (arsip)**. F1–F7 tetap berlaku (bagian 9).
> v0.2 (15 Okt 2026): F1–F7 dijawab developer sesuai usulan. Rincian dari pola di [28](28-struktur-level-episode.md#ep-2--ep02_kampungkali--siang--sore), format sama dengan [30](30-desain-level-ep01.md) (Ep 1).
> Sumber: [16 kartu Ep 2](16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul) (isi episode), [27](27-rencana-model-tuyul.md) (ukuran Tuyul), [02](02-setting-dunia.md) (Kampung Kali). Skenario adegan Ep 2 belum ada ([17](17-skenario-arc-1.md#episode-210)), jadi urutan di sini juga jadi kerangka skenarionya.

**Visual:** [`visual/ep02-kampung-kali.html`](visual/ep02-kampung-kali.html) (buka di browser).

**Posisi di roadmap:** Ep 2 = Fase 4 (mulai Apr 2028, [10](10-roadmap.md#fase-4--produksi-season-1-ep-210-apr-2028--akhir-2029)). Dokumen ini **tidak memajukan jadwal**; tujuannya supaya kit Kampung Kali dan sistem kejar-kejaran dirancang sejak awal untuk dipakai ulang di Ep 4 dan Ep 10. Semua angka titik awal greybox.

---

## 1. Ringkasan

| | |
|---|---|
| **Konsep tempat** | **Kampung kota padat di tepi kali**: gang sempit, atap seng bertumpuk, jemuran, kabel semrawut, bantaran sungai, jembatan gantung kuning. Diapit jalan raya (utara) dan kali (selatan) |
| **Nada** | Ringan dan jahil, siang terang (kontras dengan Ep 1 yang senja dan seram) |
| **Durasi main** | ±23–28 menit (v01: ±20–25) |
| **Area total** | **±1400 × 1000 m** (v02; v01: 600 × 500 m), arena raksasa ±1340 × 930 m |
| **Skala acuan** | Aksa 1,75 m · tuyul kecil 1 m · rumah 1 lantai 3,5 m / 2 lantai 6,5 m · gang 1,2–2,5 m · kali lebar ±40 m · tuyul besar 27 m · tuyul raksasa 45 m ([27](27-rencana-model-tuyul.md#1-satu-model-tiga-ukuran)) · Jayadwara 45 m |
| **Ide utama level** | **Atap adalah jalan kedua.** Bagian manusia bergerak di dua lapis (gang dan atap). Di mode raksasa, seluruh kampung itu setinggi mata kaki, jadi pemain harus bertarung di kali, gudang Adikara, dan lapangan selatan supaya tidak menginjak rumah. **Kampung inti tetap padat; ruang Jayadwara ada di cincin luar** (v02) |
| **Kit baru** | **Kampung Kali** ([28 bagian 3](28-struktur-level-episode.md#3-kit-distrik-dibangun-sekali-dipakai-ulang)), dipakai ulang di Ep 4 (pasar) dan Ep 10 |

---

## 2. Denah v01 (arsip, 15 Okt 2026)

> Diganti tata letak v02 di bagian 2a. Disimpan untuk riwayat.

Utara = jalan raya. Titik nol = tengah kampung (dekat pos RT).

```
   ░░ gedung tinggi Distrik Adikara (latar jauh, foreshadow Ep 3) ░░
 ┌─────────────────────────── RUKO + toko ───────────────────────────────┐
 │═══════════════════ JALAN RAYA (mobil, gerobak, angkot) ═══════════════│
 R      ● START mobil DWARA ─► mulut gang                                 │
 E  ┌──────────────── KAMPUNG PADAT (rumah 1–2 lantai) ───────┐┌─────────┐│
 L  │ ★1 rumah kemalingan     ┊ gang utama                     ││ PASAR   ││
    │   T1 (atap)             ┊   ⌂ pos RT                ★2   ││ (tutup, ││
 K  │          T2 atap seng   ┊        ☪ musala   warung CCTV  ││  Ep 4)  ││
 E  │ ○ sesajen (gang buntu)  ┊                  T3 (atap)     │└─────────┘│
 R  └──────────── bantaran / tanggul ── LAPANGAN TEPI KALI (T5) ┘           │
 E  ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈ K A L I  (±40 m, arus ke timur) ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈│
 T     ╪ jembatan gantung kuning (T4)              ║ jembatan beton      │
 A  ┌────────────── KAMPUNG SEBERANG (lebih jarang) + jalan inspeksi ──────┐│
    └──────────────────────────────────────────────────────────────────────┘│
 └────────────── sawah kota / gudang → batas selatan ─────────────────────────┘
```

### Koordinat greybox (meter, Y utara)

| Bagian | Pusat / rentang | Ukuran | Catatan |
|---|---|---|---|
| Jalan raya | y +110 … +125, x −260 … +260 | lebar 15 | Mobil parkir, gerobak, angkot (properti yang dicuri boss) |
| Deret ruko | y +125 … +145 | 2–3 lantai (7–10 m) | Batas utara arena manusia |
| START + mobil DWARA | (−30, +117) | — | Mulut gang utama di (−20, +105) |
| Kampung padat | x −200 … +150, y −40 … +105 | ±350 × 145 | Turun pelan ±4 m ke arah kali |
| Gang utama | x −20, y −40 … +105 | lebar 2,5 | Bisa dilewati motor; tulang punggung navigasi |
| Gang samping | y +70, +30, −10 (timur–barat) | lebar 1,2–2 | Ditambah gang buntu dan tangga |
| Pos RT | (−20, +70) | — | Titik kumpul warga, checkpoint |
| Musala | (+60, +50) | 12 × 12 | **Tidak bisa hancur** |
| Rumah kemalingan (★1) | (−130, +60) | 2 lantai | Cabang barat |
| Warung + CCTV (★2) | (+110, +85) | — | Cabang timur, dekat gerbang pasar |
| Gang buntu + beringin (○) | (−170, −20) | — | Cabang tersembunyi barat daya |
| Pasar (tutup) | x +150 … +260, y −20 … +110 | ±110 × 130 | Gerbang ditutup; dipakai Ep 4 |
| Bantaran + tanggul | y −45 … −75 | tanggul 3 m | Jalan setapak, perahu, jemuran |
| Lapangan tepi kali | (+20, −60) | 50 × 30 | Titik gabung kawanan + transformasi |
| Kali | y −80 … −120 | lebar ±40, dalam ±1,5 m | Arus ke timur; dangkal untuk raksasa |
| Jembatan gantung | x −80 | lebar 1,5 | Kuning, landmark dari mulut gang |
| Jembatan beton | x +120 | lebar 8 | Mobil |
| Kampung seberang | y −125 … −230 | lebih jarang | Jalan inspeksi di y −125 |
| Rel kereta | x −235, utara–selatan, tanggul 6 m | — | Batas barat + jembatan rel di atas kali |

## 2a. Tata letak v02 (16 Okt 2026, yang berlaku)

**Alasan:** dari mata Jayadwara yang lari ±70 m/s, arena v01 (500 × 380 m) habis dilintasi dalam ±7 detik, sementara Ep 1 sudah naik ke 1400 × 1220 m ([30 bagian 2a](30-desain-level-ep01.md#2a-tata-letak-v02-16-okt-2026-yang-berlaku)). Dari tiga opsi (A tarik jarak ×1,7 · **B perluas + area baru** · C dua kampung), developer memilih **B**. Prinsipnya sama dengan Ep 1 v02: **ukuran objek tetap asli** (gang 1,2–2,5 m, rumah 3,5–6,5 m, kali ±40 m). **Kampung inti hanya dibesarkan ±1,3×** supaya kejar-kejaran di gang tetap rapat; luas baru ditaruh di **cincin luar** tempat Jayadwara bergerak, dan tiap area baru punya fungsi untuk boss.

| | v01 (arsip, bagian 2) | **v02** |
|---|---|---|
| Medan | 600 × 500 m | **1400 × 1000 m** (x −700 … +700, y −600 … +400) |
| Arena raksasa | ±500 × 380 m | **±1340 × 930 m** (x −650 … +690, y −600 … +330) |
| Jayadwara melintas arena | ±7 detik | **±19 detik** (Ep 1 v02: ±17) |
| Kampung inti | 350 × 145 m | **455 × 190 m**, tetap padat |
| Rute kejar Aksa | ±650 m | **±1270 m** pos RT → T5 (atap → gang → jembatan gantung → bantaran → pintu air), ±3,5 mnt lari |
| Tempat bertarung tanpa penalti | kali | **kali, bantaran, gudang Adikara, lapangan + sawah selatan** |

```
   ░░░░░ gedung tinggi Distrik Adikara (latar, di luar batas, foreshadow Ep 3) ░░░░░
 ┌──────────────── BLOK KOTA (ruko belakang, perumahan; penalti normal) ─────────────────┐
 │ R ┌────────────── RUKO + toko ───────────────────────────────────────────────────────┐│
 │ E │═╪══╪══╪══╪ JALAN LAYANG (pilar 15 m) di atas JALAN RAYA ══╪══╪══╪══╪══╪══╪══╪══╪═││
 │ L │   ● START → mulut gang                                                            ││
 │   │ ┌─────── KAMPUNG PADAT (inti, ±1,3×) ─────────┐┌─ PASAR ─┐┌── GUDANG & PABRIK ───┐││
 │ ▓ │ │ ★1  T1        ┊ gang utama          ★2      ││ (tutup, ││  ADIKARA             │││
 │ STASIUN │   T2 seng ┊ ⌂ pos RT  ☪ musala   T3     ││  Ep 4)  ││  (tanpa penalti)     │││
 │   │ │ ○ sesajen     ┊                             │└─────────┘└────── dermaga ───────┘││
 │   │ └──────────────── bantaran / tanggul ─────────┘                                   ││
 │ ⊟ pintu air  LAPANGAN TEPI KALI (gabung)                                              ││
 │≈≈≈≈╪≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈ K A L I (±40 m, arus ke timur) ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈││
 │ ║ jbt rel  ╪ jembatan gantung kuning (T4)       ║ jembatan beton                       ││
 │ ║ anak  ┌──────────── KAMPUNG SEBERANG + jalan inspeksi ─────────────┐  ⊙ menara air   ││
 │ ║ kali  └────────────────────────────────────────────────────────────┘  lahan kosong   ││
 │ ║     LAPANGAN BOLA + SAWAH KOTA (aman) ── tiang SUTET ── tiang SUTET ── tiang SUTET   ││
 └───────────────────────────────────────────────────────────────────────────────────────┘
```

**Pratinjau tampak atas:** `python -I Art/Level/pratinjau_ep02_v02.py` menulis `docs/visual/ep02_layout_v02_atas.png` (butuh Pillow; PNG tidak di-commit dari sesi cloud karena unggahan Git LFS ditolak, developer boleh meng-commit-nya).

**Data (sumber kebenaran, dipakai Hermes dan nanti `Tools/ue_greybox_ep02.py`):** [`Art/Level/ep02_medan_v02.py`](../Art/Level/ep02_medan_v02.py) (medan, 8 slot material, 14 titik uji; z = 0 muka air kali) dan [`Art/Level/ep02_layout_v02.json`](../Art/Level/ep02_layout_v02.json) (145 objek, 8 kelompok instanced berisi 1.817 rumah/ruko/blok/pilar/kontainer, pohon, tiang, 23 penanda, 5 zona, 8 kamera), yang **dibuat** oleh [`Art/Level/buat_layout_ep02_v02.py`](../Art/Level/buat_layout_ep02_v02.py). Pratinjau: [`Art/Level/pratinjau_ep02_v02.py`](../Art/Level/pratinjau_ep02_v02.py). Tata letak diubah di generator, bukan di JSON. Instruksi Hermes: [`Hermes/maps_ep2_hermes.md`](../Hermes/maps_ep2_hermes.md) (branch `hermes/maps_ep2`; greybox dimajukan atas permintaan developer 16 Okt 2026, jalur paralel Level/Map).

### Koordinat greybox v02 (meter, Y utara, titik nol dekat pos RT)

| Bagian | Pusat / rentang | Ukuran | Catatan |
|---|---|---|---|
| Blok kota utara | y +200 … +365, x −700 … +700 | blok 20–40 m, tinggi 10–20 m | Penalti normal; latar gedung Adikara di luar batas (y > +400) |
| Deret ruko | y +168 … +195 | 2–3 lantai (7–10 m) | Batas utara area manusia |
| Jalan raya | y +145 … +165 | lebar 20 | Mobil parkir, gerobak, angkot (properti yang dicuri boss) |
| **Jalan layang** *(baru)* | di atas jalan raya, y +150 … +160 | dek 15 m, pilar tiap 60 m | Penghalang dan pembanding skala (setinggi paha Jayadwara), mirip pilar tol Ep 1 |
| START + mobil DWARA | (−40, +155) | — | Mulut gang utama di (−26, +140) |
| Kampung padat | x −260 … +195, y −50 … +140 | ±455 × 190 | Turun pelan ±4 m ke arah kali |
| Gang utama | x −26, y −50 … +140 | lebar 2,5 | Tulang punggung navigasi |
| Gang samping | y +91, +39, −13 (timur–barat) | lebar 1,2–2 | Ditambah gang buntu dan tangga |
| Pos RT | (−26, +91) | — | Titik kumpul warga, checkpoint |
| Musala | (+78, +65) | 14 × 14 | **Tidak bisa hancur** |
| Rumah kemalingan (★1) | (−170, +78) | 2 lantai | Cabang barat |
| Warung + CCTV (★2) | (+143, +110) | — | Cabang timur, dekat gerbang pasar |
| Gang buntu + beringin (○) | (−220, −26) | — | Cabang tersembunyi barat daya |
| Pasar (tutup) | x +205 … +340, y −30 … +140 | ±135 × 170 | Gerbang dikunci; dipakai Ep 4 |
| **Gudang & pabrik Adikara** *(baru)* | x +360 … +690, y −45 … +140 | ±330 × 185 | **Tanpa penalti** (milik Adikara, sama dengan base camp Ep 1). 3 gudang besar, deret kontainer, truk, dermaga bongkar ke kali di x +450 … +520 |
| Bantaran + tanggul | y −50 … −85, x −560 … +700 | tanggul 3 m | Jalan setapak, perahu, jemuran |
| **Lapangan tepi kali** | (−420, −68) | 60 × 30 | Dipindah ke barat (v01: +20, −60): titik gabung kawanan + transformasi, dekat pintu air |
| Kali | y −85 … −125, x −700 … +700 | lebar ±40, dalam ±1,5 m | Arus ke timur; dangkal untuk raksasa; **jalur cepat aman** untuk memotong jalan boss |
| Jembatan gantung | x −105 | lebar 1,5 | Kuning, landmark dari mulut gang |
| Jembatan beton | x +156 | lebar 8 | Mobil; jalur evakuasi warga ke selatan |
| **Pintu air** *(baru)* | (−505, −105) | 50 × 50, menara 12 m | Landmark kedua; T5; aman untuk Jayadwara |
| **Anak kali** *(baru)* | dari pintu air ke selatan, x −520 … −490, y −125 … −600 | lebar ±20 | Zona aman; membelah selatan-barat |
| **Kampung pinggir barat** *(baru)* | x −530 … −265, y −50 … +140 | jarang | Penalti normal; pengisi antara rel dan kampung inti |
| Rel kereta | x −560 … −540, utara–selatan, puncak tanggul +12 m (±3–8 m di atas tanah) | — | Batas barat; **jembatan rel** di atas jalan raya, kali, dan jalan inspeksi (tidak hancur) |
| **Stasiun kecil** *(baru)* | x −650 … −570, y −10 … +130 | peron 140 m sejajar puncak rel | Penalti normal; kereta lewat sesekali sebagai bahaya ringan |
| Kampung seberang | x −470 … +450, y −130 … −330 | lebih jarang | Jalan inspeksi di y −130 |
| **Menara air** *(baru)* | (+260, −230) | tinggi 30 m | Pembanding skala |
| **Lapangan bola + sawah kota** *(baru)* | x −480 … +700, y −340 … −600 | lapangan 105 × 68 di (−200, −414) | **Zona aman** kedua; 4 tiang SUTET 48 m di y −520 sebagai pembanding skala |
| Lahan kosong timur | x +450 … +700, y −130 … −330 | — | Penalti rendah; puing dan semak |

---

## 3. Zona dan alur pemain

| Zona | Adegan (kerangka) | Waktu | Cahaya |
|---|---|---|---|
| Briefing di hub | Markas DWARA pertama kali ([16 D4](16-panduan-arc-1.md#9-keputusan-yang-perlu-dijawab-developer)) | 1–2 mnt | — |
| A. Kedatangan | Turun di jalan raya, masuk mulut gang | ±2 mnt | Siang terik 12.30 |
| B. Investigasi | 3 petunjuk di kampung | ±5–7 mnt | Siang |
| C. Kejar-kejaran | 5 tuyul di gang, atap, dan bantaran | ±5–6 mnt | Sore 15.30 |
| D. Gabung + transformasi | Lapangan tepi kali | ±1 mnt | Sore keemasan |
| E. Arena raksasa | Kali, kampung, jalan raya, gudang Adikara, selatan | ±7–9 mnt | Keemasan → senja |
| Segel + debrief | Bantaran, uang warga kembali | ±1–2 mnt | Senja |

### A. Kedatangan · ±2 menit
- Mobil DWARA berhenti di jalan raya karena gang terlalu sempit. Ketua RT menyambut di mulut gang.
- **Landmark:** dari mulut gang, gang utama menurun lurus ke selatan dan **jembatan gantung kuning** terlihat di ujungnya, di atas kali. Pemain langsung tahu "kampung ini berujung di sungai".
- Tutorial ulang singkat (kontrol, scanner) untuk pemain yang lupa setelah Ep 1.
- **Batas:** jalan raya dibatasi garis polisi dan mobil pemadam di ujung timur dan barat.

### B. Investigasi · ±5–7 menit
Area semi-terbuka; urutan petunjuk bebas. Gang utama adalah "koridor" yang selalu bisa ditemukan lagi.

| # | Petunjuk | Lokasi | Catatan |
|---|---|---|---|
| ★1 | Jejak kaki kecil berenergi Kala (`Clue.Ep02.JejakKaki`) | Rumah kemalingan, barat (−170, +78) | Scan menunjukkan jejak naik dinding ke **atap**: mengenalkan lapis atap |
| ★2 | CCTV warung yang diretas Sekar (`Clue.Ep02.CCTV`) | Warung, timur (+143, +110) | Memperlihatkan **pola rute kawanan** (dipakai di fase 2 boss). Pemilik warung menjual mainan → **umpan mainan** |
| ○ | Sesajen pesugihan (`Clue.Ep02.Sesajen`) | Gang buntu di bawah beringin, barat daya | Bestiary + petunjuk benang merah "rekening penampung" (Sekar) |

- **Pintu kecil ala RE4:** gang buntu ○ hanya terbuka lewat atap rumah sebelah (tangga bambu di belakang rumah kemalingan), jadi hadiah untuk pemain yang menjelajah.
- Warga di teras (ibu-ibu, anak-anak, tukang ojek) memberi celetukan; tanpa sistem wawancara (itu Ep 4).

### C. Kejar-kejaran · ±5–6 menit · mekanik baru episode
Setelah ★1 dan ★2 ditemukan, kawanan mencuri **kotak uang kas RT** di pos RT dan kabur. Kejar 5 tuyul lewat **rute melingkar** (±1270 m di v02, ±3,5 menit lari tanpa berhenti) dengan 5 titik:

| Titik | Lokasi | Lapis | Isi |
|---|---|---|---|
| T1 | Atap rumah kemalingan (−170, +98) | Atap | Tuyul pertama; tangga bambu naik atap |
| T2 | Deret atap seng (−78, +39) | Atap | Lari di atap yang berbunyi; lompat celah gang |
| T3 | Atap belakang warung (+117, +26) | Atap → gang | Turun lewat tumpukan galon; **umpan mainan** dari warung |
| T4 | Jembatan gantung (−105, −105) | Jembatan | Jembatan bergoyang; tuyul kabur ke barat lewat bantaran; **umpan yuyu** dari bantaran (−250, −70) |
| T5 | Pintu air (−505, −105) | Tanah → menara | *(v02)* Tuyul memanjat menara pintu air; turun ke lapangan tepi kali (−420, −68) → zona D |

- **Aturan:** tuyul yang lolos kabur ke titik berikutnya; **tidak ada game over** ([16 Ep 2](16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul)). Tuyul ditangkap dengan pukulan atau sapuan.
- **Umpan:** mainan (warung) dan yuyu (bantaran) bisa diambil dan dilempar; tuyul berhenti sejenak.
- **Jalan pintas:** tangga bambu, papan antar-atap, dan pintu belakang rumah yang dibuka warga **tetap terbuka** setelah dilewati, jadi rute kedua lebih cepat kalau tuyul kabur.
- **Checkpoint:** awal kejar-kejaran (pos RT) dan setelah tuyul ke-3.
- **Atap:** hanya atap tertentu yang bisa dinaiki (ditandai jemuran, tangga, atau antena), supaya pemain tidak tersesat dan level tetap murah.

### D. Gabung + transformasi · ±1 menit (sequence)
- Kawanan (yang tertangkap maupun yang lolos) tersedot energi Kala dan **bergabung** di lapangan tepi kali menjadi **tuyul raksasa**, lalu mengangkat sebuah mobil dari jalan raya.
- Aksa transformasi di lapangan (gestur **Lawang Terbuka** versi pendek, [17 S1](17-skenario-arc-1.md#keputusan-untuk-developer-ep-1)). Jayadwara berdiri **di dalam kali**: sengaja, supaya langkah pertamanya tidak menginjak rumah.

### E. Arena raksasa · ±6–8 menit
Arena = blok kota + jalan raya + kampung + gudang Adikara + kali + kampung seberang + lapangan dan sawah selatan, **±1340 × 930 m** (v02).

| Bagian arena | Meter sinkronisasi | Catatan |
|---|---|---|
| **Kali + bantaran + lapangan + pintu air + anak kali** | **Zona aman** (tanpa penalti) | Air setinggi mata kaki Jayadwara; percikan besar (VFX) |
| **Lapangan bola + sawah kota** *(v02)* | **Zona aman** | Tiang SUTET hancur tanpa penalti |
| **Gudang & pabrik Adikara** *(v02)* | **Tanpa penalti** | Milik Adikara, sama dengan base camp Ep 1; boleh dihancurkan bebas |
| Kampung padat | **Penalti tinggi** | Rumah rapat: satu langkah salah = beberapa rumah |
| Jalan raya + ruko + blok kota | Penalti normal | Mobil yang dicuri boss tidak dihitung |
| Jalan layang + stasiun *(v02)* | Penalti normal | Pilar dan gelagar runtuh per bentang |
| Kampung seberang | Penalti normal | Lebih jarang; ruang fase 2 |
| Musala, jembatan rel, menara pintu air | Tidak hancur | — |
| Pasar (tutup) | Penalti normal | Hanya pinggirnya yang terjangkau |

- **Fase 1, tuyul raksasa (45 m) lari dan mencuri:** boss mengangkat mobil di jalan raya lalu berlari ke timur menuju **gudang Adikara** (±950 m, *v02*). Pemain **memotong jalannya** lewat kali yang sejajar dan aman (tidak mengejar dari belakang) dan menjatuhkannya dengan pukulan. Saat jatuh, ia menjatuhkan barang curian (mobil, gerobak). Pelajaran meter Ep 2: **mengejar membabi buta lewat kampung itu mahal** ([16](16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul)).
- **Fase 2, tiga tuyul besar (27 m):** tubuhnya pecah jadi tiga dan menyebar ke **gudang Adikara, stasiun, dan lapangan bola selatan** (*v02*; v01: kali, jalan raya, kampung seberang). **Kelemahan:** dengan petunjuk CCTV, tuyul yang asli bergerak mengikuti **pola rute yang sama dengan rekaman CCTV** dan ubun-ubunnya berdenyut (`RealPulse`, [27](27-rencana-model-tuyul.md#2-arahan-desain-usulan)). Tanpa petunjuk, pemain harus menebak; memukul yang palsu membuatnya pecah jadi asap dan muncul lagi.
- **Checkpoint:** awal fase 1, awal fase 2.
- **Kalah sebagai Jayadwara:** Aksa muncul di tempat; gang dan bawah jembatan jadi tempat bersembunyi skala manusia.

### Segel + debrief · ±1–2 menit
- Penyegelan di tepi kali. Uang curian berhamburan dan dikembalikan warga ke pos RT (adegan ringan).
- Debrief: Sekar menemukan uang curian mengalir ke **rekening penampung yang sama** ([16 bagian 4](16-panduan-arc-1.md#4-benang-merah-narasi)). Unlock: scanner jangkauan +50%.

---

## 4. Bangunan dan kerusakan

Kampung padat punya ratusan rumah, jauh lebih banyak dari anggaran 8–10 gedung hancur Chaos ([30 E7](30-desain-level-ep01.md#9-keputusan-dijawab-developer-15-okt-2026)). Usulan **dua kelas kerusakan** (keputusan F2):

| Kelas | Jumlah | Cara | Di mana |
|---|---|---|---|
| **Blok Chaos** | 8 (maks 10) | Satu Geometry Collection = **satu deret 3–4 rumah**, runtuh bersama | Pinggir kali dan jalan raya (tempat pertarungan paling sering) |
| **Rumah tukar puing** | Sisanya | Tanpa fisika: saat diinjak, mesh rumah diganti mesh puing + debu (VFX) + penalti meter | Bagian dalam kampung |

- Kit rumah: 3 mesh dasar (1 lantai, 2 lantai, rumah panggung bantaran) × variasi atap (seng, genteng) dan warna cat.
- Detail pembanding skala: jemuran, antena TV, toren air di atap, kabel listrik, motor di gang, pot bunga.
- **Properti curian** (fase 1): 3–4 mobil dan 2 gerobak di jalan raya, sebagai aktor fisika biasa.

### Warga
- 10–14 warga ([30](30-desain-level-ep01.md#4-daftar-bangunan-dan-prop-arena) memakai 8–12); berlari ke **lapangan bola selatan** lewat jembatan beton saat fase 1.

---

## 5. Suasana dan pencahayaan

| Bagian | Waktu | Cahaya | Catatan |
|---|---|---|---|
| A–B | 12.30 | Matahari tinggi, bayangan pendek, gang teduh vs atap silau | Terang dan hidup; radio, ayam, motor |
| C | 15.30 | Matahari condong ke barat; atap seng memantul | Kejar-kejaran terasa cepat |
| D–E | 17.00 | **Keemasan**, matahari di barat ujung kali | Siluet raksasa di atas kali berkilau |
| Debrief | 17.45 | Senja ungu, lampu rumah menyala | Hangat |

Transisi lewat Data Layer pencahayaan ([28](28-struktur-level-episode.md#teknis-per-map)).

---

## 6. Latar jauh dan batas

| Arah | Batas | Fungsi |
|---|---|---|
| Utara | Blok kota + jalan layang; gedung tinggi **Distrik Adikara** di kejauhan | Foreshadow Ep 3 |
| Barat | **Rel kereta** di tanggul (puncak +12 m) + stasiun kecil; kereta lewat sesekali | Batas alami + pembanding skala |
| Timur | Pasar (tutup) → gudang Adikara → kali berbelok | Pasar disimpan untuk Ep 4 |
| Selatan | Kampung seberang → lapangan bola + sawah kota + tiang SUTET | Arena fase 2, zona aman kedua |

---

## 7. Anggaran performa (titik awal)

| Item | Batas awal |
|---|---|
| Blok Chaos aktif | 8 (maks 10) |
| Rumah tukar puing | tanpa batas fisika (mesh swap) |
| Warga | ≤ 14 |
| Tuyul kecil bersamaan | 5 |
| Mobil/gerobak fisika | ≤ 6 |
| Gudang Adikara *(v02)* | rumah tukar puing (mesh swap) + kontainer fisika ≤ 10 |
| Jalan layang *(v02)* | tukar puing per bentang (tanpa Chaos) |
| Pembanding skala *(v02)* | pohon, tiang listrik, SUTET: instancing |
| Kampung | Nanite + HLOD per blok; atap dan kabel memakai instancing |
| Air kali | Satu permukaan air sederhana + VFX percikan (tanpa simulasi fluida) |

---

## 8. Kit dan pakai ulang

| Level Instance | Isi | Dipakai ulang di |
|---|---|---|
| `LI_KampungKali_Gang` | Blok rumah + gang + atap yang bisa dinaiki | Ep 4, Ep 10 |
| `LI_KampungKali_Bantaran` | Tanggul, rumah panggung, lapangan, jembatan gantung | Ep 4, Ep 10 |
| `LI_KampungKali_JalanRaya` | Jalan, ruko, kendaraan | Ep 3 (pinggir), Ep 10 |
| `LI_KampungKali_Pasar` | Pasar (tutup di Ep 2) | **Ep 4** (pasar malam, dibuka) |

Area baru v02 **tidak menambah kit**: gudang Adikara memakai ulang prop base camp Adikara Ep 1 (kontainer, truk, pagar seng) + gudang blok kasar; jalan layang, stasiun, pintu air, dan menara air cukup mesh blok sederhana. Anggaran 1 kit baru per episode ([28](28-struktur-level-episode.md)) tetap.

**Sistem baru episode ini** ([16 bagian 2.2](16-panduan-arc-1.md#22-anggaran-produksi-per-episode-ep-210): maks 1): **kejar-kejaran + kawanan**, mis. `AJDFleeRoute` (titik T1–T5 + jalur gang/atap) dan perilaku kabur di StateTree. Dibuat generik karena dipakai ulang di Ep 11 (Ebu Gogo).

---

## 9. Keputusan (dijawab developer 15 Okt 2026)

| # | Pertanyaan | Keputusan ✅ |
|---|---|---|
| **F1** | Ukuran boss: tuyul raksasa **45 m (1,0×)** sesuai arahan developer di [27](27-rencana-model-tuyul.md#1-satu-model-tiga-ukuran), atau **0,5–0,8×** sesuai aturan skala [16 bagian 2.6](16-panduan-arc-1.md#26-aturan-skala)? | **45 m.** Aturan skala [16 bagian 2.6](16-panduan-arc-1.md#26-aturan-skala) diperbarui: boss Arc 1 boleh 0,5–1,0×; Ep 20 jadi lawan setara pertama dalam tenaga dan teknik |
| **F2** | Kerusakan kampung: 8 blok Chaos + rumah tukar puing? | **Ya**. Satu-satunya cara kampung padat terasa rapuh tanpa melewati anggaran FPS |
| **F3** | Kali + bantaran + lapangan sebagai zona aman? | **Ya**, sama dengan sawah di Ep 1 |
| **F4** | Pasar ditutup di Ep 2, dibuka di Ep 4? | **Ya** (kit sama, cerita berbeda) |
| **F5** | Atap yang bisa dinaiki hanya yang ditandai (jemuran/tangga/antena)? | **Ya**, supaya rute jelas dan aset atap lainnya bisa murah |
| **F6** | Kejar-kejaran dimulai setelah ★1 + ★2 (○ opsional)? | **Ya**, sesuai aturan 2 petunjuk wajib ([16 bagian 2.1](16-panduan-arc-1.md#21-struktur-dari-07)) |
| **F7** | Ep 2 dibuka dari briefing di Markas DWARA (hub pertama)? | **Ya** ([16 D4](16-panduan-arc-1.md#9-keputusan-yang-perlu-dijawab-developer)); map Ep 2 dimuat setelah briefing |
