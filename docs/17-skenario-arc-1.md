# 17 — Skenario Arc 1 "Kebangkitan"

> **Status: USULAN v0.1 (12 Okt 2026)**, menunggu review developer.
> Isi: skenario per episode Arc 1. Ep 1 ditulis lengkap (vertical slice); Ep 2–10 menyusul sebagai outline.
> Aturan desain (struktur episode, skala, penyegelan, mekanik) ada di [16-panduan-arc-1.md](16-panduan-arc-1.md). Batas scope Ep 1 tetap [11-vertical-slice-spec.md](11-vertical-slice-spec.md): adegan di sini tidak menambah sistem di luar daftar "Masuk Scope", kecuali yang ditandai **[opsional]**.

---

# Episode 1 — "Gerbang yang Retak"

## Ringkasan

| | |
|---|---|
| **Logline** | Di misi lapangan pertamanya, Aksa dikirim ke candi tempat kakeknya dulu menjadi juru kunci. Ia hampir mati melawan Jerangkong, lalu roh Dwarapala memilihnya. |
| **Boss** | Jerangkong, kerangka raksasa yang terus menyusun ulang dirinya (±0,7× tinggi Jayadwara) |
| **Lokasi** | Situs Lawang Sapta: area penggalian Adikara, gerbang candi, dan desa kecil di tepi jalan akses |
| **Waktu** | Sore menjelang senja (investigasi) → senja merah (kebangkitan) → awal malam (boss & debrief) |
| **Durasi** | ±22–28 menit |
| **Tema episode** | *Pulang.* Aksa kembali ke tempat yang ingin ia lupakan dan menerima warisan yang tidak pernah ia minta |
| **Pemeran** | Aksa · Ki Sastro (narasi wayang) · Kol. Bagas · Sekar (operator) · Dr. Nadia · Prof. Yahyo · suara Sang Penjaga · Gunadi Adikara (stinger, opsional) |

## Busur emosi Aksa

| Awal | Titik balik | Akhir |
|---|---|---|
| Menganggap DWARA sekadar pekerjaan baru setelah keluar dari timnas silat. Tidak mau membahas kakeknya. "Kerja yang tenang aja." | Tergeletak di kaki arca, Sang Penjaga bertanya: *"Kau masih mau menjaga?"* Aksa menjawab iya, dan untuk pertama kalinya menerima peran keluarganya. | Menang, tapi merahasiakan semuanya dari tim. Ada sesuatu di dalam dirinya yang "menghitung". Ia tidak tahu itu apa. |

## Sang Penjaga (suara roh Dwarapala)

Karakter baru yang hanya berupa **suara** di Ep 1. Usulan arahan:
- Suara berat dan tua, kalimatnya pendek, sesekali kata Jawa. **Tidak memakai mantra nyata.**
- Netral, bukan malaikat penolong. Ia peduli pada gerbang, belum tentu pada Aksa. Ini menjaga pilar "penjaga yang ambigu".
- Di Ep 1 ia menjelaskan meter sinkronisasi secara naratif ("ikatan kita"), sehingga meter tidak perlu menunggu penjelasan Nadia (lore alat ukurnya baru di Ep 6).

---

## Alur Adegan

Kolom **Jenis**: `WAYANG` = 2D parallax · `DIALOG` = teks + potret (UI) · `MAIN` = gameplay · `KOMS` = suara di telinga selama gameplay (teks subtitle + potret kecil) · `SEQ` = cutscene Sequencer.

| # | Adegan | Jenis | Durasi |
|---|---|---|---|
| 1 | Pembuka wayang: Dua Penjaga | WAYANG | 1,5 mnt |
| 2 | Briefing di jalan | DIALOG | 1,5 mnt |
| 3 | Tiba di galian | MAIN + KOMS | 2 mnt |
| 4 | Tiga petunjuk | MAIN + KOMS | 5–6 mnt |
| 5 | Tulang yang bangun | MAIN (combat tutorial) | 4–6 mnt |
| 6 | Kebangkitan | SEQ | 1,5–2 mnt |
| 7 | Jayadwara vs Jerangkong | MAIN | 6–8 mnt |
| 8 | Penyegelan | SEQ | 30 dtk |
| 9 | Debrief | DIALOG | 1–1,5 mnt |
| 10 | Stinger: arca kedua **[opsional]** | SEQ / gambar diam | 30 dtk |
| 11 | Kartu "Episode berikutnya" | UI | 10 dtk |

---

### Adegan 1 — Pembuka wayang: "Dua Penjaga" · WAYANG

Kelir wayang, blencong menyala. Ki Sastro sebagai dalang. Gamelan pelan.

> **KI SASTRO:** Dahulu kala, sebelum kota-kota berdiri, Batara Kala menebar makhluk-makhluknya ke seluruh Nusantara.
>
> **KI SASTRO:** Para leluhur membangun tujuh gerbang. Di setiap gerbang, berdiri dua penjaga. Dwarapala namanya.
>
> *(Dua wayang Dwarapala berhadapan, gada di tangan. Wayang makhluk Kala menyerbu, lalu tersedot masuk ke balik gerbang.)*
>
> **KI SASTRO:** Mereka mengunci makhluk Kala di balik gerbang. Ratusan tahun gerbang itu tertutup.
>
> **KI SASTRO:** Tapi tak ada yang pernah bertanya, apa harga yang dibayar para penjaga itu.
>
> *(Gunungan ditancapkan. Layar gelap.)*

**Catatan:**
- Kalimat terakhir adalah *foreshadowing* rahasia Ep 30 (Dwarapala menyegel dengan cara memakan). **Jangan** diucapkan lebih jelas dari ini.
- "Dua penjaga" menyiapkan payoff arca kedua (Ep 40).

---

### Adegan 2 — Briefing di jalan · DIALOG

Latar: kabin mobil DWARA di jalan desa menuju candi, sore. Panggilan video di tablet.

> **SEKAR:** Lawang, tes. Suaraku masuk? Oke. Selamat datang di misi pertamamu!
>
> **KOL. BAGAS:** Langsung saja. Tiga malam terakhir, empat pekerja proyek tol Adikara ditemukan meninggal di area galian. Polisi bilang kecelakaan kerja. Saya tidak percaya.
>
> **KOL. BAGAS:** Statusmu di sana petugas cagar budaya. Lihat, catat, laporkan. Jangan sok jadi pahlawan.
>
> **DR. NADIA:** Itu Netra, prototipe. Scan apa pun yang aneh. Dan tolong, jangan dijatuhin.
>
> **SEKAR:** Lokasinya... Candi Lawang Sapta.
>
> *(Jeda. Potret Aksa berubah.)*
>
> **AKSA:** ...Saya tahu tempatnya, Pak.
>
> **KOL. BAGAS:** Saya tahu kamu tahu. Makanya kamu yang saya kirim.

**Catatan:** Bagas tahu latar keluarga Aksa (ia yang merekrut Aksa). Ini membuka pertanyaan kecil tanpa menjawabnya.

---

### Adegan 3 — Tiba di galian · MAIN + KOMS

Aksa turun dari mobil di batas garis polisi. Truk dan alat berat Adikara sedang pergi; seorang mandor menyuruh semua orang pulang sebelum gelap. Desa kecil terlihat di bawah bukit.

**Gameplay:** tutorial gerak (jalan, lari, lompat, dodge) di jalur galian yang berundak menuju candi. Penanda tujuan: gerbang candi.

> **MANDOR (lewat):** Mas cagar budaya? Jangan lama-lama. Habis magrib, nggak ada yang mau di sini.
>
> **SEKAR (KOMS):** Ramah banget orangnya.
>
> **AKSA (sendiri, melihat gerbang candi dari kejauhan):** Masih sama aja.

**Interaksi opsional:** batu datar di pinggir jalur, tempat Aksa kecil dulu berlatih kuda-kuda dengan kakeknya.
> **AKSA:** Di sini dulu disuruh kuda-kuda sampai magrib. Kalau kakiku goyang, Kakek ketuk pakai tongkat.
>
> **SEKAR (KOMS):** Kakekmu tinggal di sini?
>
> **AKSA:** ...Dulu.

**Catatan:** interaksi ini mengenalkan Ki Zahid tanpa menyebut nama dan tanpa flashback visual (hemat aset).

---

### Adegan 4 — Tiga petunjuk · MAIN + KOMS

**Gameplay:** tutorial scanner Netra (mode scan, penanda di HUD). Di Ep 1 **ketiga petunjuk ada di jalur utama** karena episode ini tutorial yang linear. Ini pengecualian dari aturan 2.1 di [16](16-panduan-arc-1.md#21-struktur-dari-07), yang menjadikan petunjuk ke-3 opsional.

**Petunjuk 1 — Jejak energi** (`Clue.Ep01.JejakEnergi`)
Aliran energi Kala merah gelap mengalir dari lubang galian menuju gerbang candi, hanya terlihat di mode scan.
> **DR. NADIA (KOMS):** Pembacaan energinya... ini bukan listrik, bukan radiasi. Aku belum pernah lihat yang begini.
>
> **SEKAR (KOMS):** Ikutin aja alirannya. Kayak sungai.

**Petunjuk 2 — Tulang yang bergeser** (`Clue.Ep01.Tulang`)
Di dasar lubang galian, tempat para pekerja ditemukan, berserakan fragmen tulang tua, jauh lebih tua dari umur para pekerja. Saat di-scan kedua kalinya, posisinya sudah bergeser.
> **DR. NADIA (KOMS):** Tunggu. Scan pertama sama scan kedua beda. Tulangnya pindah tiga senti.
>
> **AKSA:** Angin?
>
> **DR. NADIA (KOMS):** Tulang nggak ketiup angin, Aksa.

**Petunjuk 3 — Prasasti retak** (`Clue.Ep01.Prasasti`)
Di gerbang candi ada dua alas arca Dwarapala. Arca kiri berdiri retak; **arca kanan masih ada, tapi sudah dililit tali derek dengan stiker inventaris Adikara**. Prasasti di antara keduanya retak oleh getaran alat berat. Prof. Yahyo membacanya dari jarak jauh lewat Netra.
> **PROF. YAHYO (KOMS):** Aksara Kawi. Sebagian hilang... "yang tersusun dari tulang, kembali menjadi tulang... kecuali kepalanya dipecah."
>
> **PROF. YAHYO (KOMS):** Dan di bawahnya... "penjaga kedua berdiri agar penjaga pertama tak sendirian."
>
> **AKSA (melihat tali derek di arca kanan):** Kenapa arca ini diiket?
>
> **SEKAR (KOMS):** Di dokumen Adikara tertulis "relokasi benda cagar budaya". Izinnya... nggak ada.

**Hasil:** tag kelemahan `Clue.Ep01.Prasasti` aktif → tengkorak Jerangkong ditandai di HUD saat boss fight (sesuai [11](11-vertical-slice-spec.md#boss-jerangkong-2-fase)).

**Catatan:**
- [11](11-vertical-slice-spec.md#alur-episode-2030-menit) menyebut petunjuk "tulang pekerja". Di sini ditafsirkan sebagai **tulang kuno di lokasi pekerja meninggal**, bukan jasad pekerja, untuk menjaga rating remaja tanpa gore. Jasad pekerja tidak pernah ditampilkan.
- Arca kanan yang dililit tali derek adalah setup visual untuk truk di adegan 6.

---

### Adegan 5 — Tulang yang bangun · MAIN (combat tutorial)

Saat Prof. Yahyo selesai membaca, tanah bergetar. Fragmen tulang di galian merayap dan menyusun diri menjadi **kerangka kecil** (minion, skala manusia).

> **SEKAR (KOMS):** Eh. Eh, eh, eh. Itu tulangnya berdiri!
>
> **KOL. BAGAS (KOMS):** Aksa, mundur ke mobil. Itu perintah.
>
> **AKSA:** Mobilnya di belakang mereka, Pak.

**Gameplay — tutorial bertahap dalam 3 gelombang, makin dekat ke gerbang candi:**

| Gelombang | Musuh | Yang diajarkan |
|---|---|---|
| 1 | 3 kerangka | Pukulan ringan (combo 3), pukulan berat |
| 2 | 5 kerangka | Dodge, tangkis + parry |
| 3 | 6 kerangka yang **bangkit lagi** kalau tidak dihabisi | Finisher memecah tengkorak supaya kerangka tidak bangkit lagi |

> **AKSA (setelah combo pertama):** Badannya masih inget.
>
> **AKSA (saat kerangka bangkit lagi):** Kepalanya. Kata prasasti: kepalanya.

**Catatan desain:** gelombang 3 sengaja mengajarkan "pecahkan kepala" di skala manusia. Pemain memakai pelajaran yang sama di boss raksasa (satu sistem, dua skala).

**Checkpoint:** awal gelombang 3.

---

### Adegan 6 — Kebangkitan · SEQ

Senja merah. Semua sisa tulang di galian tersedot ke tengah lubang. Tanah merekah. **Jerangkong** bangkit, kerangka raksasa ±31 m dengan energi Kala merah di sela tulang rusuknya.

1. Aksa terpental oleh satu sapuan lengan Jerangkong, menghantam **arca Dwarapala kiri**, lalu jatuh di kakinya. Arca retak lebih besar.
2. *(Wide shot)* Di jalan akses, di belakang Jerangkong, **truk Adikara melaju pergi membawa arca kanan** yang tertutup terpal. Tidak ada yang melihatnya, kecuali pemain.
3. Aksa tergeletak. Suara sekitar tenggelam, dan napasnya berat.

> **SANG PENJAGA:** Keturunan juru kunci.
>
> **AKSA (lirih):** ...Siapa?
>
> **SANG PENJAGA:** Gerbang ini retak. Yang dulu menjaganya sudah tak ada.
>
> **SANG PENJAGA:** Kau masih mau menjaga?
>
> *(Jerangkong mengangkat kaki di atas Aksa. Tangan kanan Aksa menekan tanah di kaki arca.)*
>
> **AKSA:** ...Iya.

4. **Transformasi:** arca pecah. Pecahan batunya melayang dan berputar mengelilingi Aksa, lalu retakan cahaya emas merambat dari telapak tangannya yang menempel di tanah. Pecahan batu menjadi zirah. **Jayadwara** berdiri dan menahan kaki Jerangkong dengan satu tangan.
5. Pose kuda-kuda silat. Judul muncul: **JAYADWARA**.

**Catatan:**
- **Gestur transformasi = telapak tangan menekan bumi**, terkait nama *Mangkubumi* ("yang memangku bumi"). Usulan ini menggantikan "item transformasi" dan jauh dari gestur Ultra (mengangkat alat ke langit). Perlu persetujuan (keputusan S1).
- Tidak ada gelang atau alat. Tidak ada cahaya dari langit. Kekuatan datang dari **tanah dan batu arca**.
- Truk di latar (poin 2) sesuai [11](11-vertical-slice-spec.md#alur-episode-2030-menit).

---

### Adegan 7 — Jayadwara vs Jerangkong · MAIN

Arena: halaman candi + galian + desa kecil di bawah bukit (6–10 bangunan yang bisa hancur: rumah, warung, menara air, gardu ronda; musala desa **tidak** bisa hancur). Beberapa warga berlarian.

**Pengenalan kontrol raksasa** (prompt di layar) dan **meter sinkronisasi**, dijelaskan oleh Sang Penjaga:
> **SANG PENJAGA:** Lihat ke belakangmu. Rumah. Orang.
>
> **SANG PENJAGA:** Setiap yang runtuh karena kita, ikatan kita melemah. Kalau ikatan putus, kau kembali jadi manusia, di depan makhluk itu.

> **SEKAR (KOMS, panik):** Pak... ada dua raksasa di layar. Yang satu merah.
>
> **KOL. BAGAS (KOMS):** Semua unit, jangan menembak yang merah. Belum.

**Fase 1 — Kerangka yang menyusun ulang**
- Jerangkong menyerang jarak dekat dengan lengan tulang (sapuan, hantaman, lemparan tulang).
- Lengan atau kaki yang dihancurkan rontok, lalu merayap kembali dan menyusun ulang. Pemain sadar memukul badan tidak cukup.
- Setelah tubuhnya dihancurkan dan menyusun ulang 2×, masuk fase 2.

> **AKSA (setelah susun ulang pertama):** Sama kayak yang kecil.

**Fase 2 — Tengkorak**
- Tengkorak terekspos (energi Kala menyala di rongga mata). **Tengkorak ditandai HUD** karena petunjuk prasasti.
- Jerangkong lebih agresif dan melempar puing ke arah desa. Pemain bisa **menangkis** puing untuk melindungi warga.
- Boss hanya bisa dikalahkan dengan menghancurkan tengkorak (jurus spesial #1 atau finisher).

**Meter:** turun kalau bangunan hancur atau warga terkena (versi dasar, [16 D2](16-panduan-arc-1.md#9-keputusan-yang-perlu-dijawab-developer)). Health Jayadwara habis = kembali jadi Aksa di tempat, menghindar sampai energi transformasi penuh, lalu berubah lagi; Aksa mati = ulang checkpoint awal fase (keputusan 12 Okt 2026, [23](23-rencana-fase-1.md#45-kalah-sebagai-jayadwara--energi-transformasi-q15)). Meter habis: usulan sama (Q17 di 23).

**Checkpoint:** awal fase 1, awal fase 2.

---

### Adegan 8 — Penyegelan · SEQ

Tengkorak retak. Jayadwara menempelkan telapak tangan ke pecahan tengkorak. Energi Kala tersedot ke telapak tangannya, dan tulang-tulang raksasa runtuh menjadi debu.

Sepersekian detik, **mata Jayadwara berkedip merah gelap**, lalu kembali normal.

> **SANG PENJAGA:** ...Satu.

Jayadwara memudar menjadi cahaya dan pecahan batu yang jatuh ke alas arca kosong.

**Catatan:**
- "Satu" = menghitung yang sudah "dimakan". Ambigu; pemain baru memahaminya di Ep 30.
- Kedipan merah hanya di **mata**, bukan permata dada (aturan IP, [16 bagian 2.3](16-panduan-arc-1.md#23-penyegelan-ritual-penutup-tiap-boss)).

---

### Adegan 9 — Debrief · DIALOG

Malam, lampu sorot tim DWARA. Aksa duduk di alas arca yang kosong, berselimut, dan lecet-lecet.

> **KOL. BAGAS:** Kamu di mana waktu makhluk merah itu muncul?
>
> **AKSA:** Ketimpa reruntuhan, Pak. Pas sadar, semuanya udah selesai.
>
> **SEKAR:** Kamu beruntung banget, sumpah.
>
> **DR. NADIA:** Satu hal aneh. Data Netra-mu putus empat menit, persis selama raksasa merah itu ada.
>
> **AKSA:** Rusak kebentur, mungkin.
>
> **DR. NADIA:** ...Mungkin.
>
> **KOL. BAGAS:** Pusat sudah memberi kode untuk makhluk itu: **Entitas D**. Statusnya belum jelas, kawan atau ancaman. Sampai jelas, kita perlakukan sebagai ancaman.
>
> **PROF. YAHYO:** Kolonel, satu lagi. Di foto drone, kedua alas arca kosong. Yang satu hancur, saya mengerti. Yang satu lagi... ke mana?
>
> *(Kamera ke alas arca kanan: bekas tali derek dan jejak ban truk di tanah.)*

**Catatan:**
- Aksa berbohong. Ini awal rahasia identitas sampai Ep 30.
- Nadia mulai curiga lewat data ([03](03-karakter.md#peta-hubungan)).
- Bestiary terisi: **Jerangkong**. Unlock: **jurus spesial #1** (sudah dipakai di boss, resmi tercatat di debrief). *Vertical slice: cukup baris teks; UI bestiary & sistem unlock di luar scope [11](11-vertical-slice-spec.md) (lihat [18 K5](18-kebutuhan-episode-1.md#6-keputusan-yang-perlu-diambil)).*

---

### Adegan 10 — Stinger: arca kedua · SEQ / gambar diam **[opsional]**

Gudang gelap milik Adikara. Terpal ditarik dari arca Dwarapala kanan. **Gunadi Adikara** menatapnya, lalu menatap tablet yang menampilkan rekaman Jayadwara.

> **GUNADI ADIKARA:** Satu sudah bangun.
>
> **GUNADI ADIKARA:** Yang ini... punya kita.

**Catatan:** stinger **tidak ada** di daftar scope [11](11-vertical-slice-spec.md). Kalau disetujui, pakai versi paling murah (1 shot statis atau gambar ilustrasi). Kalau tidak, informasi arca kedua sudah cukup dari adegan 6 dan 9.

---

### Adegan 11 — Kartu "Episode berikutnya" · UI

Gaya serial tokusatsu: potongan gambar + judul.

> **Episode berikutnya: "Tangan-Tangan Kecil"**

---

## Daftar Produksi Ep 1

### Cutscene & presentasi

| ID | Adegan | Jenis | Aset utama |
|---|---|---|---|
| `WAY_Ep01_Pembuka` | 1 | Wayang 2D | Wayang Dwarapala ×2, makhluk Kala, gunungan, kelir |
| `DT_Dialogue_Ep01` | 2, 3, 4, 5, 7, 9 | DataTable dialog | Potret: Aksa, Bagas, Sekar, Nadia, Yahyo, mandor; ikon suara Sang Penjaga |
| `LS_Ep01_Kebangkitan` | 6 | Sequencer | Jerangkong bangkit, Aksa terpental, truk + arca berterpal, transformasi |
| `LS_Ep01_Penyegelan` | 8 | Sequencer | Template penyegelan (dipakai ulang Ep 2–10) |
| `LS_Ep01_Stinger` | 10 | Sequencer / gambar | **[opsional]** gudang, Gunadi, arca kanan |

### Tag & data

| Tag / data | Kegunaan |
|---|---|
| `Clue.Ep01.JejakEnergi`, `Clue.Ep01.Tulang`, `Clue.Ep01.Prasasti` | 3 petunjuk; `Prasasti` = kelemahan boss |
| `DA_Ep01_LawangSapta` | `UJDEpisodeData` Ep 1 |
| `Unlock.Jurus.Spesial01` | Unlock debrief |

### Karakter yang perlu potret / suara

Aksa, Kol. Bagas, Sekar, Dr. Nadia, Prof. Yahyo, Ki Sastro, mandor (NPC), Sang Penjaga (suara saja), Gunadi Adikara (opsional).

---

## Cek IP & Budaya Ep 1

- [x] Tanpa item transformasi berbentuk gelang; gestur = telapak ke tanah, bukan mengangkat alat ke langit.
- [x] Tanpa timer; meter dijelaskan sebagai "ikatan", habis = kembali jadi manusia.
- [x] Penyegelan: kedipan merah hanya di mata, permata dada statis.
- [x] Tanpa gore: jasad pekerja tidak ditampilkan; tulang = tulang kuno.
- [x] Sang Penjaga tidak memakai mantra nyata; aksara Kawi di prasasti = teks fiksi.
- [x] Masjid/musala di desa tidak dijadikan bangunan yang bisa dihancurkan.
- [ ] Review budayawan untuk penggambaran Dwarapala & candi (sebelum rilis).

---

## Keputusan untuk Developer (Ep 1)

| # | Pertanyaan | Usulan Claude |
|---|---|---|
| **S1** | Gestur transformasi: telapak tangan menekan bumi? | **Ya**, terkait nama Mangkubumi dan jauh dari gestur Ultra. Di episode lain Aksa memakai gestur yang sama. Kalung pecahan arca Aksa ([03](03-karakter.md#aksa-jaya-mangkubumi-aksa)) menyala samar saat gestur, bukan alat yang diangkat |
| **S2** | Sang Penjaga berbicara langsung ke Aksa? | **Ya**, suara saja, kalimat pendek, netral/ambigu. Memberi alasan naratif untuk meter di Ep 1 |
| **S3** | Kol. Bagas sudah tahu latar keluarga Aksa? | **Ya**, sedikit ("Makanya kamu yang saya kirim"), tanpa dijelaskan. Bisa dibayar di arc berikutnya |
| **S4** | Stinger Gunadi + arca kedua masuk vertical slice? | **Opsional**, versi gambar diam. Di luar scope [11](11-vertical-slice-spec.md) sampai disetujui |
| **S5** | "Tulang pekerja" (docs/11) → tulang kuno? | **Ya**, demi rating remaja; docs/11 diperbarui kalau disetujui |
| **S6** | Ketiga petunjuk di jalur utama (pengecualian aturan 2.1 docs/16)? | **Ya**, khusus Ep 1 sebagai tutorial |

---

# Episode 2–10

*Menyusul sebagai outline (±1 halaman per episode) setelah skenario Ep 1 disetujui.*
