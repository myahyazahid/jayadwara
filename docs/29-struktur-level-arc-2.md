# 29 — Struktur Level Arc 2 "Gelombang Nusantara" (Ep 11–20)

> **Status: USULAN v0.1 (15 Okt 2026), backlog Season 2.** Disiapkan atas permintaan developer. **Tidak memajukan jadwal**: Arc 2 dikerjakan setelah Early Access Season 1 ([10](10-roadmap.md#fase-5--early-access-season-1-akhir-2029)).
> Memakai pola **satu map per episode ala Resident Evil 4** dari [28](28-struktur-level-episode.md) (zona A–E, kit Level Instance, hub). Sumber: [02](02-setting-dunia.md#peta-misi-regional) (peta regional, Sapta Dwara), [04](04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120) (cerita Arc 2), [05](05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120) (boss & mekanik), [06](06-referensi-mitologi.md) (mitologi & sensitivitas). Kalau bertentangan, dokumen sumber yang berlaku.

---

## 1. Identitas Arc 2 untuk level

| | |
|---|---|
| **Cerita** | DWARA membuka operasi regional. Di tiap titik gerbang **selalu ada proyek Adikara**; Sekar mulai menemukan polanya ([04](04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120)) |
| **Wilayah** | Lima gerbang dari Sapta Dwara ([02](02-setting-dunia.md#lore-inti-sapta-dwara-tujuh-gerbang)): Tenggara (Flores), Barat (Sumatra), Utara (Kalimantan), Timur Laut (Sulawesi), Timur (Maluku–Papua) |
| **Perbedaan dari Arc 1** | Keluar dari Arunapura. Setiap wilayah butuh kit baru, jadi **pembagian kit** (bagian 3) adalah kunci anggaran |
| **Ukuran boss** | Mendekati Jayadwara: **0,8–1×**. Ep 20 Geunteut = **raksasa setara pertama** ([16 bagian 2.6](16-panduan-arc-1.md#26-aturan-skala)) |
| **Ukuran arena** | Lebih besar dari Arc 1 karena boss makin besar: **±450×450 m**, Ep 20 ±600×600 m (angka akhir mengikuti hasil uji L2 di [28](28-struktur-level-episode.md#8-keputusan-yang-perlu-dijawab-developer)) |
| **Penanda berulang** | **Lokasi proyek Adikara** di tiap map (pagar seng, alat berat, kantor kontainer, papan proyek). Kit-nya dipakai ulang dari Ep 1. Pemain akan mengenali polanya sebelum Sekar menyebutkannya |

---

## 2. Aturan tempat dan budaya (wajib di setiap map Arc 2)

- **Kota/desa fiktif di wilayah nyata.** Wilayah boleh disebut (Flores, Toba, Kerinci, Aceh), tapi desa, kota, dan situs yang dibangun **fiktif**, seperti Arunapura. Tidak meniru kampung adat, situs megalitik, atau rumah ibadah nyata.
- **Rumah adat dan rumah ibadah = zona larangan rusak.** Rumah gadang, rumah bolon, rumah panggung adat, masjid, gereja, pura, dan makam keramat **tidak** bisa hancur. Mengenainya memberi penalti meter besar. Gedung hancur diambil dari bangunan biasa (ruko, gudang, rumah modern, kios).
- **Ikuti [06 panduan sensitivitas](06-referensi-mitologi.md#panduan-sensitivitas-budaya).** Ep 16 Parakang, Ep 17 Suanggi, dan Ep 19 Begu Ganjang bertanda ⚠️ (sosial): tuduhan terhadap warga harus berkonsekuensi, dan level tidak boleh mengarahkan pemain untuk "menangkap warga yang dicurigai" tanpa bukti.
- **Pakaian dan arsitektur adat** diambil dari referensi yang benar, lalu dikonsultasikan dengan budayawan sebelum rilis (rekomendasi di [06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)).
- **Ep 20 (Aceh):** hindari citra gelombang besar yang menghancurkan pesisir. Ingatan tsunami 2004 masih sangat hidup (keputusan M4).

---

## 3. Kit regional (hemat produksi)

Arc 2 punya 8 lokasi untuk 10 episode. Membangun 8 kit lengkap terlalu mahal, jadi kit dibagi dua lapis:

- **Kit inti**: medan, vegetasi, bangunan biasa, dan jalan yang sama untuk beberapa wilayah.
- **Paket identitas**: sedikit bangunan dan prop khas yang membuat wilayah langsung dikenali (rumah adat, perahu, pasar khas). Hampir semuanya berstatus zona larangan rusak (bagian 2), jadi cukup satu versi utuh tanpa fracture.

| Kit inti | Isi | Dipakai di | Paket identitas |
|---|---|---|---|
| **Proyek Adikara** *(dari Ep 1)* | Pagar seng, alat berat, kantor kontainer, papan proyek, galian | Semua Ep 11–20 | — |
| **Dataran tinggi Sumatra** | Bukit, sawah bertingkat, hutan hujan, kebun teh, kota kecil (ruko), jalan berkelok | Ep 12, 18, 19 | Minang (rumah gadang, surau) · Kerinci (kebun teh, danau) · Batak (rumah bolon, tepi danau) |
| **Kota sungai Kalimantan** | Sungai lebar, rumah panggung dan rumah lanting, titian kayu, pasar terapung, gudang kayu | Ep 13, 14 | Kota tua tepi sungai (Ep 14) |
| **Pesisir timur** | Pantai, desa nelayan, dermaga kayu, perahu, tebing karang | Ep 15, 16, 17, 20 | Bugis (rumah panggung, pinisi) · Maluku–Papua (rumah pesisir, hutan sagu) · Aceh (meunasah, pelabuhan) |
| **Savana Nusa Tenggara** | Padang savana, bukit kering, tebing, desa di punggung bukit, hutan kecil | Ep 11 | Desa adat fiktif (rumah beratap tinggi) |
| **Pelabuhan** *(dari Ep 9)* | Gudang, kontainer, derek | Ep 14, 20 | — |
| **Vegetasi Lereng Gunung** *(dari Ep 6)* | Hutan tropis | Ep 12, 17, 18 | — |

**Kit baru di Arc 2: 4 kit inti** (Dataran tinggi Sumatra, Kota sungai Kalimantan, Pesisir timur, Savana NT) **+ 7 paket identitas**. Kit inti ini juga dipakai Arc 3–4 (Soppeng Ep 26, Hutan Sumatra Ep 34, Pesisir Sumatra Ep 35, Pesisir Kalimantan Ep 37, Ora di Flores Ep 32).

---

## 4. Hub dan perjalanan

- **Markas DWARA** (`Hub_MarkasDWARA`, [28](28-struktur-level-episode.md#hub--hub_markasdwara-mulai-ep-2)) tetap jadi hub utama: briefing, bestiary, upgrade, pilih episode.
- **Pos lapangan DWARA** di zona A tiap map: tenda komando atau kontainer berlogo DWARA dengan meja Sekar portabel. Fungsinya seperti *typewriter* RE4: checkpoint, simpan, dan dialog singkat dengan anggota fokus episode. Satu set prop, dipakai di semua map Arc 2 (keputusan M5).
- **Perpindahan wilayah** = cutscene singkat (pesawat/kapal DWARA + peta Nusantara yang menandai gerbang). Peta ini juga UI pilih episode di hub.

---

## 5. Rancangan map per episode

Format sama seperti [28 bagian 4](28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1): zona **A** kedatangan → **B** investigasi → **C** konfrontasi → **D** transformasi → **E** arena raksasa. Ukuran boss adalah usulan (keputusan M6).

### Ep 11 — `Ep11_SavanaFlores` · Ebu Gogo · fokus Prof. Yahyo · gerbang Tenggara
- **Suasana:** siang terik → sore keemasan di savana.
- **A.** Jalan tanah menuju desa di punggung bukit; pos lapangan DWARA. Situs Adikara (pengeboran) terlihat di lembah.
- **B. Desa + bukit batu:** ★ gudang hasil panen yang dijarah (jejak kaki kecil, pola Ep 2), ★ **batu bertulis segel kuno** di bukit (Prof. Yahyo; momen kunci arc, [04](04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120)), ○ cerita tetua tentang "orang kecil yang suka mencuri".
- **C. Set-piece:** kawanan Ebu Gogo mencuri peralatan DWARA dan kabur ke **gua di tebing**. Kejar-kejaran (pakai ulang sistem Ep 2) di jalur tebing dan lorong gua; gua punya cabang ○ berisi relief segel.
- **E. Arena:** savana terbuka + desa di bukit + situs pengeboran Adikara. Boss: pemimpin Ebu Gogo yang membesar **0,8×** dan memanggil kawanan. Batas: tebing, laut di kejauhan.
- **Catatan:** savana sangat terbuka, sehingga gedung hancur sedikit. Meter dijaga lewat desa dan ladang.

### Ep 12 — `Ep12_RanahMinang` · Palasik · fokus Ratna · gerbang Barat
- **Suasana:** malam, kabut di lembah.
- **A.** Kota kecil di lembah; Ratna mengoordinasi pengamanan rumah sakit.
- **B. Kota kecil (ruko, pasar, surau):** ★ catatan bidan tentang bayi yang sakit mendadak, ★ jejak energi dari proyek Adikara di bukit (bendungan/terowongan), ○ cerita orang tua tentang palasik.
- **C. Pertahanan rumah sakit bersalin:** **mode bertahan** pertama: kepala-kepala terbang kecil menyerang dari banyak jendela; Aksa menjaga 3 bangsal. Pintu antarbangsal dibuka bertahap (gerbang cerita).
- **E. Arena:** lembah dengan sawah bertingkat, kota kecil, dan bukit. **Rumah sakit dan rumah gadang = zona larangan rusak**; boss (kepala raksasa **0,8×**, rambut dan selendang energi panjang) terus berusaha mendekati rumah sakit. Batas: bukit dan tebing lembah.
- **Catatan:** Ratna mengatur evakuasi lewat komunikasi. Ini fondasi peran evakuasinya di Ep 29.

### Ep 13 — `Ep13_KotaSungai` · Kuyang · fokus Nadia · gerbang Utara
- **Suasana:** malam, sungai berkabut, lampu rumah lanting.
- **A.** Dermaga kota; DWARA datang naik perahu.
- **B. Kota sungai (area investigasi paling luas di Arc 2):** tujuannya **menemukan tubuh yang ditinggalkan kuyang**. ★ jejak darah energi (scanner) di titian kayu, ★ data sensor panas Nadia yang memetakan rumah kosong, ○ dukun beranak yang memberi tahu ciri kuyang. Titian kayu dan perahu menghubungkan cabang-cabang.
- **C.** Kuyang kecil (minion kepala terbang) mengganggu saat pemain menyisir rumah-rumah; tubuh ditemukan di gudang kayu dekat proyek Adikara.
- **E. Arena:** sungai lebar dengan kota di dua tepi dan pasar terapung. **Kelemahan:** tubuh yang ditemukan diamankan supaya kuyang raksasa (**0,85×**) tidak bisa kembali, dan Jayadwara memaksanya turun saat fajar. Batas: sungai yang makin lebar, hutan rawa.
- **Catatan:** horor malam tanpa gore; organ menggantung digambarkan sebagai **energi Kala berbentuk sulur**, bukan organ realistis (rating remaja).

### Ep 14 — `Ep14_KotaTuaSungai` · Kuntilanak · fokus Ki Sastro · gerbang Utara
- **Suasana:** malam berhujan.
- **A.** Kota tua tepi sungai (beda sisi dari Ep 13); menara air dan gudang pelabuhan sungai.
- **B. Kota tua:** ★ rekaman suara tangisan di radio warga (Sekar menganalisis frekuensi), ★ Ki Sastro menjelaskan legenda "paku di tengkuk", ○ pohon tua yang ditebang proyek Adikara.
- **C.** Gang dan gudang; **efek sonik pertama di skala manusia**: HUD bergetar dan suara kacau ketika jeritan terdengar. Pemain belajar berlindung di balik dinding.
- **E. Arena:** pelabuhan sungai + kota tua + menara air. **Gedung menghalangi jeritan sonik**: berlindung di balik gedung memulihkan HUD, tapi gedung jadi rusak. Ini konflik meter yang disengaja. Boss **0,85×**. Batas: sungai, rawa.
- **Pakai ulang:** kit Kota sungai (Ep 13) + Pelabuhan (Ep 9).

### Ep 15 — `Ep15_TebingBugis` · Poppo · fokus Bayu · gerbang Timur Laut
- **Suasana:** siang berangin, langit terbuka.
- **A.** Pelabuhan pinisi; Bayu menyiapkan perahu cepat.
- **B. Desa nelayan:** ★ jala dan perahu yang tercabik dari atas, ★ pola terbang poppo direkam radar nelayan, ○ cerita pembuat pinisi.
- **C. Set-piece:** **kejar-kejaran perahu on-rails** (Bayu menyetir, pakai ulang sistem Ep 7) di antara tebing karang sambil menembak suar ke kawanan poppo kecil.
- **E. Arena:** tebing karang tinggi + teluk + desa. Poppo raksasa (**0,9×**) sangat cepat. Jayadwara tidak terbang (sayap baru di Ep 38), jadi "dogfight"-nya berupa **memakai tebing sebagai panggung**: memanjat/melompat ke puncak tebing, melempar batu karang, dan counter saat poppo menukik (keputusan M1). Batas: laut, tebing.
- **Catatan:** pengembangan dari Ep 7 (musuh udara) dengan kecepatan lebih tinggi dan medan vertikal.

### Ep 16 — `Ep16_DesaPesisirBugis` · Parakang ⚠️ · fokus Ratna · gerbang Timur Laut
- **Suasana:** sore → malam; desa tegang.
- **A.** Desa pesisir; warga berkumpul dan saling tuduh.
- **B. Investigasi warga (inti episode):** pakai ulang sistem wawancara Ep 4, diperluas. 4–5 warga dengan kesaksian yang bertentangan; bukti scanner harus dicocokkan sebelum menyebut pelaku. **Salah tuduh punya konsekuensi** ([06](06-referensi-mitologi.md#catatan-per-boss-️)): warga yang salah dituduh diserang massa dan Ratna harus menenangkan, ada adegan dan dialog berbeda di debrief. Pelaku sebenarnya ternyata **pekerja proyek Adikara yang terpapar energi Kala**, bukan warga desa.
- **C.** Melindungi warga yang dituduh dari amukan massa (tanpa melukai warga: dorong, halangi, Ratna bicara), lalu menghadapi wujud kecil parakang di dermaga.
- **E. Arena:** desa rumah panggung + pantai + dermaga. **Rumah panggung adat = zona larangan rusak**, jadi pertarungan didorong ke pantai dan area proyek Adikara. Boss **0,85×**.
- **Catatan:** episode ini adalah pelajaran keadilan untuk Ratna. Level dan dialog **tidak boleh** memberi hadiah untuk main hakim sendiri.

### Ep 17 — `Ep17_TelukTimur` · Suanggi ⚠️ · fokus Ki Sastro · gerbang Timur
- **Suasana:** malam bulan purnama, hutan sagu.
- **A.** Pantai dan dermaga kayu; pos lapangan di gereja/rumah warga yang dipinjam (bangunan tidak bisa hancur).
- **B. Desa pesisir + hutan sagu:** ★ benda-benda kutukan yang tertanam di sekitar proyek Adikara (scanner), ★ Ki Sastro bertemu tetua adat yang menjelaskan cara menangkal, ○ warga yang dulu pernah dituduh suanggi (sisi sosial, bestiary).
- **C.** Jalan hutan dengan **kutukan pembalik kontrol** di skala manusia (zona tertentu membalik arah gerak); pemain belajar membaca tanda sebelum masuk zona.
- **E. Arena:** teluk + desa + hutan + tanjung. **3 sumber kutukan** di tanjung dan bukit (pola objektif Ep 3): selama masih ada, kontrol Jayadwara terbalik secara berkala. Boss **0,9×**.
- **Catatan ⚠️:** suanggi digambarkan sebagai **kekuatan kutukan yang berasal dari energi Kala**, bukan seseorang dari warga. Tidak ada adegan warga dituduh menjadi suanggi tanpa konsekuensi.

### Ep 18 — `Ep18_HutanKerinci` · Harimau Cindaku · fokus Bayu · gerbang Barat
- **Suasana:** pagi berkabut di kebun teh → hutan gelap.
- **A.** Jalan di antara kebun teh; danau di kejauhan.
- **B. Desa kebun teh:** ★ jejak cakar besar di perkebunan, ★ cerita pemburu yang melihat "manusia berubah", ○ makam leluhur desa (zona larangan, sisi lore cindaku sebagai penjaga).
- **C. Set-piece Bayu (misi pribadinya):** **diburu di hutan**. Harimau kecil menyerang dari semak; pemain bertahan dengan timing parry dan bergerak dari satu tempat terang ke tempat terang lain. Bayu bicara soal keluarganya yang tewas karena serangan monster.
- **E. Arena:** hutan lebat + kebun teh berbukit + tepi danau. Sedikit bangunan, sehingga **kebun dan desa** jadi sumber penalti meter. Boss **0,85×**, sangat cepat. Mekanik counter timing, sedangkan pohon besar menghalangi pandangan.
- **Pakai ulang:** kit Dataran tinggi Sumatra (Ep 12) + vegetasi Lereng Gunung.

### Ep 19 — `Ep19_TepiDanau` · Begu Ganjang ⚠️ · fokus Nadia · gerbang Barat
- **Suasana:** senja → malam, danau tenang seperti cermin.
- **A.** Pelabuhan kecil di tepi danau besar (fiktif, terinspirasi Toba).
- **B. Desa tepi danau:** ★ warga yang "melihat sesuatu makin tinggi" (tanda mekanik), ★ Nadia menguji pantulan di cermin dan permukaan air (momen kunci, [04](04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120)), ○ cerita sosial tentang tuduhan memelihara begu ganjang.
- **C.** Jalan desa malam: begu ganjang kecil hanya bisa dilawan lewat **kaca spion/cermin** (melihat langsung = ia makin tinggi). Ini tutorial mekanik pantulan di skala manusia.
- **E. Arena:** tepi danau + desa + bukit. **Danau adalah alat utama**: Jayadwara bertarung dengan **melihat pantulan boss di air**. Kamera atau mode khusus memperlihatkan pantulan; menatap langsung membuat boss tumbuh dan lebih kuat. Boss mulai **0,8×**, bisa tumbuh sampai 1,2× kalau ditatap langsung.
- **Catatan ⚠️:** sisi sosial wajib ada (orang yang dituduh memelihara begu ganjang). Rumah bolon = zona larangan rusak.

### Ep 20 — `Ep20_PesisirAceh` · Geunteut (finale Arc 2) · fokus Kol. Bagas · gerbang Barat
- **Suasana:** pagi mendung → badai di laut tanpa ombak besar (keputusan M4).
- **A.** Pelabuhan dan kota pesisir; **operasi gabungan militer** (Kol. Bagas memimpin). Pos lapangan DWARA terbesar di Arc 2.
- **B. Kota pesisir + hutan:** ★ jejak kaki raksasa di hutan (ukuran setara Jayadwara), ★ catatan proyek Adikara terbesar di Arc 2 (Sekar menyatukan pola 5 gerbang), ○ hikayat geunteut dari tetua.
- **C.** Evakuasi kota bersama tentara; minion gabungan Arc 2. Bagas memilih antara perintah atasan dan melindungi "Entitas D".
- **E. Arena terbesar Arc 2 (±600×600 m):** kota pesisir + pelabuhan + hutan + bukit. **Geunteut 1×**: raksasa setara pertama; pertarungan grapple dan dorong-dorongan (fokus duel, bukan monster yang lebih kecil). Meunasah dan masjid = zona larangan rusak. 2 fase berpindah: kota → hutan/bukit (agar kota tidak hancur total).
- **Penutup:** setelah menang, tubuh Aksa menyerap terlalu banyak energi Kala ([04](04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120)), sebagai set-up Arc 3 dan Ep 30.

---

## 6. Ringkasan

| Ep | Map | Wilayah / gerbang | Boss (ukuran) | Investigasi (B) | Set-piece (C) | Arena (E) | Mekanik level baru |
|---|---|---|---|---|---|---|---|
| 11 | `Ep11_SavanaFlores` | Flores · Tenggara | Ebu Gogo (0,8×) | Desa + batu segel | Kejar ke gua tebing | Savana + desa bukit | Kawanan di medan terbuka |
| 12 | `Ep12_RanahMinang` | Minang · Barat | Palasik (0,8×) | Kota kecil lembah | Bertahan di rumah sakit | Lembah sawah, RS dilindungi | Mode bertahan, bangunan yang dilindungi |
| 13 | `Ep13_KotaSungai` | Kalimantan · Utara | Kuyang (0,85×) | Kota sungai (terluas) | Menyisir rumah | Sungai + dua tepi | Cari objek di area besar |
| 14 | `Ep14_KotaTuaSungai` | Kalimantan · Utara | Kuntilanak (0,85×) | Kota tua | Efek sonik di gang | Pelabuhan sungai | Gedung sebagai pelindung sonik |
| 15 | `Ep15_TebingBugis` | Bugis · Timur Laut | Poppo (0,9×) | Desa nelayan | Perahu on-rails | Tebing karang + teluk | Medan vertikal anti-udara |
| 16 | `Ep16_DesaPesisirBugis` | Bugis · Timur Laut | Parakang ⚠️ (0,85×) | Wawancara warga (inti) | Lindungi yang dituduh | Pantai + dermaga | Konsekuensi salah tuduh |
| 17 | `Ep17_TelukTimur` | Maluku–Papua · Timur | Suanggi ⚠️ (0,9×) | Desa + hutan sagu | Zona pembalik kontrol | Teluk + 3 sumber kutukan | Kontrol terbalik |
| 18 | `Ep18_HutanKerinci` | Kerinci · Barat | Harimau Cindaku (0,85×) | Desa kebun teh | Diburu di hutan | Hutan + kebun + danau | Pandangan terhalang pohon |
| 19 | `Ep19_TepiDanau` | Toba · Barat | Begu Ganjang ⚠️ (0,8→1,2×) | Desa tepi danau | Lawan lewat cermin | Danau sebagai cermin | Pantulan |
| 20 | `Ep20_PesisirAceh` | Aceh · Barat | Geunteut (1×) | Kota pesisir + hutan | Evakuasi bersama militer | Arena terbesar, 2 zona | Raksasa setara |

**Pakai ulang antarepisode di Arc 2:** 13↔14 (kota sungai), 15↔16 (pesisir Bugis), 12↔18↔19 (dataran tinggi Sumatra). Episode tanpa kit inti baru: 14, 16, 18, 19, 20, jadi lebih ringan.

---

## 7. Sistem yang dibutuhkan level Arc 2

Mengikuti aturan "maksimal 1 sistem C++ baru per episode" ([16 bagian 2.2](16-panduan-arc-1.md#22-anggaran-produksi-per-episode-ep-210)):

| Ep | Sistem | Pakai ulang dari |
|---|---|---|
| 11 | — | Kejar kawanan (Ep 2) |
| 12 | **Objektif lindungi bangunan** (HP bangunan, boss mengincar) | Zona larangan rusak (Ep 5) |
| 13 | — | Scanner + objektif (Ep 3) |
| 14 | **Gangguan HUD/audio + penghalang garis pandang** | — |
| 15 | — | On-rails (Ep 7), musuh udara (Ep 7) |
| 16 | **Wawancara v2: tuduhan + konsekuensi bercabang** | Wawancara (Ep 4) |
| 17 | **Efek pembalik kontrol** (GameplayEffect + zona) | Objektif lingkungan (Ep 3) |
| 18 | — | Combat, timing parry |
| 19 | **Pantulan** (render target permukaan air + aturan "jangan menatap") | — |
| 20 | **Grapple raksasa vs raksasa** | Cengkeram/lepas (Ep 8) |

Sistem paling berisiko untuk level: **pantulan Ep 19** (render target + Lumen di permukaan air). Prototipe-kan paling awal saat Arc 2 dimulai.

---

## 8. Keputusan yang perlu dijawab developer

| # | Pertanyaan | Usulan Claude |
|---|---|---|
| **M1** | Ep 15 "dogfight" padahal Jayadwara belum bisa terbang (sayap Ep 38)? | **Medan vertikal**: tebing sebagai panggung, lempar karang, counter saat menukik. Dogfight sebenarnya disimpan untuk setelah Ep 38 |
| **M2** | Rumah adat dan rumah ibadah tidak bisa hancur? | **Ya**, sebagai zona larangan rusak (penalti meter besar). Lebih aman secara budaya dan lebih murah (tanpa fracture) |
| **M3** | Nama tempat nyata atau fiktif? | **Wilayah nyata, desa/kota fiktif** (seperti Arunapura) |
| **M4** | Ep 20 di Aceh: hindari citra gelombang besar? | **Ya**. Badai tanpa ombak besar, arena bergeser ke hutan/bukit di fase 2 |
| **M5** | Pos lapangan DWARA di tiap map sebagai checkpoint/save ala *typewriter* RE4? | **Ya**, satu set prop untuk semua map Arc 2 |
| **M6** | Ukuran boss Arc 2 (0,8–1×) seperti tabel bagian 6? | Ya, sebagai titik awal; Ep 20 tetap satu-satunya yang 1× |
| **M7** | Urutan episode tetap melompat-lompat wilayah (Flores → Sumatra → Kalimantan → ...)? | Ikuti [05](05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120) untuk cerita. Untuk produksi, map boleh dikerjakan **per kit** (13+14, 15+16, 12+18+19) supaya kit dibangun sekali |
