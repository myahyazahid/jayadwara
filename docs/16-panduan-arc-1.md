# 16 — Panduan Arc 1 "Kebangkitan" (Ep 1–10)

> **Status: DISETUJUI v0.2 (15 Okt 2026)**: keputusan D1–D6 dijawab developer (bagian 9), aturan skala diperbarui (bagian 2.6, keputusan F1 di [31](31-desain-level-ep02.md#9-keputusan-dijawab-developer-15-okt-2026)). Dokumen ini menjadi acuan Claude saat membangun episode Arc 1.
> Sumber: [04](04-skenario-cerita.md#arc-1--kebangkitan-ep-110) (cerita), [05](05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) (boss), [07](07-gameplay-sistem.md) (sistem), [11](11-vertical-slice-spec.md) (Ep 1), [12](12-technical-design.md) (arsitektur). Kalau dokumen ini bertentangan dengan dokumen sumber, dokumen sumber yang berlaku sampai keputusannya diperbarui.

**Posisi di roadmap:** Ep 1 = vertical slice (Fase 2, Apr–Des 2027). Ep 2–10 = produksi Season 1 (Fase 4, mulai Apr 2028). Dokumen ini **tidak memajukan jadwal**. Tujuannya supaya sistem yang dibuat untuk Ep 1 sudah disiapkan untuk dipakai ulang di Ep 2–10, dan supaya setiap episode punya arahan yang konsisten.

---

## 1. Identitas Arc

| | |
|---|---|
| **Tema** | Belajar mengendalikan kekuatan. "Apa yang sebenarnya merasukiku?" |
| **Tier musuh** | E: hantu lokal Jawa & Sunda yang kecil, jelek, dan dekat dengan keseharian, membesar karena energi Kala |
| **Fungsi desain** | **Arc tutorial.** Setiap episode mengajarkan **satu** mekanik baru. Di Ep 10 semuanya diuji bersama |
| **Lokasi** | Hanya Arunapura: Situs Lawang Sapta, Kampung Kali, Distrik Adikara, Kota Lama, Lereng Gunung, Pelabuhan Utara |
| **Nada** | Horor kampung yang ringan, hangat, dan kadang lucu, lalu berubah jadi tokusatsu megah saat transformasi. Seram boleh, gore tidak (target rating remaja, [09](09-product-brief.md#target-pemain)) |
| **Perasaan pemain di akhir arc** | "Aku udah jago silat dan bisa jaga kota. Tapi ada yang aneh dengan Jayadwara, dan ternyata gerbangnya ada tujuh." |

---

## 2. Aturan Tetap untuk Setiap Episode

Claude memakai aturan ini sebagai *template* setiap kali membangun episode Arc 1.

### 2.1 Struktur (dari [07](07-gameplay-sistem.md#struktur-satu-episode))

| # | Bagian | Durasi target | Catatan |
|---|---|---|---|
| 1 | Pembuka wayang | 1–2 mnt | Ki Sastro menceritakan legenda **asli** makhluknya (versi rakyat, bukan versi game). 2D parallax, bisa di-skip |
| 2 | Briefing | 1–2 mnt | Kol. Bagas menjelaskan misi utama; anggota **fokus** episode memberi konteks. Dialog teks + potret |
| 3 | Investigasi | 5–8 mnt | **3 petunjuk**. Minimal 2 petunjuk wajib untuk membuka kelemahan boss; petunjuk ke-3 opsional (bonus info / bestiary) |
| 4 | Konfrontasi manusia | 4–6 mnt | Combat silat melawan minion atau bentuk kecil makhluknya |
| 5 | Transformasi | ±30 dtk | Sequence pendek (versi panjang hanya di Ep 1) |
| 6 | Boss raksasa | 6–8 mnt | **2 fase** (Ep 10: 3 fase). Meter sinkronisasi aktif |
| 7 | Penyegelan + Debrief | 1–2 mnt | Lihat 2.3 |

**Total target 20–30 menit per episode** (batas bawah dari target 20–40 menit di [05](05-daftar-episode-boss.md#ringkasan-scope), karena ini arc tutorial).

### 2.2 Anggaran produksi per episode (Ep 2–10)

Roadmap memberi ±2 bulan per episode ([10](10-roadmap.md#fase-4--produksi-season-1-ep-210-apr-2028--akhir-2029)). Supaya muat:

- **Maksimal 1 sistem C++ baru** per episode (kolom "Mekanik baru" di tabel 3). Sisanya data/konten.
- **1 boss baru** (class turunan `AJDBossBase` + StateTree + DataAsset).
- **Maksimal 1 tipe minion baru**; minion lama boleh dipakai ulang.
- **Distrik dipakai ulang.** Kit distrik (Level Instance) dirangkai ulang di map episode baru, tidak membangun distrik baru dari nol (kecuali distrik itu muncul pertama kali). Lihat [28 bagian 3](28-struktur-level-episode.md#3-kit-distrik-dibangun-sekali-dipakai-ulang).
- Kalau satu episode butuh lebih dari itu, potong fiturnya atau pindahkan ke backlog.

### 2.3 Penyegelan (ritual penutup tiap boss)

Dwarapala menyegel monster dengan cara **memakannya** ([02](02-setting-dunia.md#dwarapala--sifat-kala)). Faktanya baru dibongkar di Ep 30, jadi di Arc 1 cukup diberi *foreshadowing*:

- Saat boss kalah, energinya tersedot ke telapak tangan Jayadwara. Animasi dan VFX-nya sama di setiap episode, hanya warna energinya yang berganti.
- **Jejak Kala bertambah** tiap episode secara halus: kilatan merah gelap di **mata** atau aura Jayadwara, makin lama dari Ep 1 ke Ep 10. Di Ep 10 Aksa sempat terhuyung setelah menyegel.
- ⚠️ **Permata dada tidak boleh ikut berubah** (aturan IP, [13 bagian 8](13-rencana-model-jayadwara.md#8-checklist-ip--budaya-dipakai-di-setiap-gate)). Jejak Kala hanya lewat mata/aura/VFX.

### 2.4 Debrief

- Kol. Bagas menutup misi. Media atau Ratna membahas "Entitas D" (lihat benang merah di bagian 4).
- **Entri bestiary** terisi (legenda asli dari pembuka wayang + kelemahan yang ditemukan + petunjuk opsional).
- **Satu unlock** (lihat bagian 5).

### 2.5 Kelemahan boss = hasil investigasi

Aturan dari [12](12-technical-design.md#investigasi--kelemahan-boss): boss menyimpan daftar tag clue yang dibutuhkan, misalnya `Clue.Ep02.Mainan`.
- **Kelemahan ditemukan:** titik lemah ditandai di HUD **dan** damage multiplier aktif.
- **Tidak ditemukan:** boss tetap bisa dikalahkan, tapi lebih lama, dan meter sinkronisasi lebih susah dijaga. Pemain tidak pernah terkunci (*soft lock*) karena melewatkan petunjuk.

### 2.6 Aturan skala

Lore: makhluk yang menyerap energi Kala membesar menjadi raksasa ([02](02-setting-dunia.md#energi-kala)). Karena itu setiap episode punya **dua skala musuh**:

| Mode | Musuh | Ukuran |
|---|---|---|
| Manusia (Aksa) | Minion + **wujud awal** makhluknya sebelum membesar | Skala manusia (±1–3 m) |
| Raksasa (Jayadwara ±45 m) | Boss setelah membesar | Raksasa, **0,5–1,0× Jayadwara** (lihat di bawah) |

- **Boss Arc 1 = 0,5–1,0× tinggi Jayadwara** (±22–45 m), ditentukan per boss sesuai cerita. Diperbarui 15 Okt 2026 (keputusan F1): developer ingin boss bisa sama besar dengan Jayadwara, seperti kaiju di serial Ultraman; contoh pertama tuyul raksasa Ep 2 (45 m). Ukuran per boss ada di tabel 3.
- **Batas bawah 0,5×**: di bawah itu Jayadwara terus memukul ke bawah (kamera sulit, butuh animasi khusus, gedung lebih mudah kena). Boss yang rendah tapi panjang (mis. Babi Ngepet) butuh serangan bawah sebagai pengecualian.
- **Progresi antar-arc** (diperbarui 15 Okt 2026): yang naik bertahap adalah **kekuatan dan teknik**, bukan hanya tinggi. Boss Arc 1 boleh setinggi Jayadwara tapi bertarung liar/tanpa teknik; **Ep 20 Geunteut = lawan setara pertama**: raksasa humanoid yang menyamai Jayadwara dalam tenaga dan teknik, duel grapple dan dorong-dorongan ([05](05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120)). Arc 5 lebih besar dari Jayadwara (Bedawang Nala, Batara Kala).
- Ukuran ditulis relatif ke Jayadwara karena skala final Jayadwara masih placeholder (D4 di [13](13-rencana-model-jayadwara.md), 45 m).

### 2.7 Aturan konten

- Checklist IP ([01](01-konsep-dan-pilar.md#wajib-dihindari), [13 bagian 8](13-rencana-model-jayadwara.md#8-checklist-ip--budaya-dipakai-di-setiap-gate)) dicek di setiap episode: tidak ada timer 3 menit, tidak ada pose L, permata dada statis.
- Makhluk digambarkan sesuai **pedoman sensitivitas** ([06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)). Di Arc 1 hanya Pocong (Ep 5) yang bertanda ⚠️.
- Legenda di pembuka wayang = versi rakyat. Adaptasi game (mis. Jenglot menyerap listrik) **disebut sebagai efek energi Kala**, bukan diklaim sebagai legenda aslinya.

---

## 3. Peta Episode

| Ep | Judul (usulan) | Boss | Ukuran boss | Lokasi | Fokus | **Mekanik baru** | Unlock debrief |
|---|---|---|---|---|---|---|---|
| 1 | Gerbang yang Retak | Jerangkong | 0,7× | Situs Lawang Sapta | Aksa | Semua dasar: gerak, silat, scanner, transformasi, combat raksasa, meter (versi dasar) | Jurus spesial #1 |
| 2 | Tangan-Tangan Kecil | Tuyul | 1,0× (fase 1), 0,6× ×3 (fase 2) | Kampung Kali | Sekar | **Kejar-kejaran + kawanan musuh** | Scanner: jangkauan +50% |
| 3 | Lapar Listrik | Jenglot | 0,55× → 0,8× | Distrik Adikara | Nadia | **Objektif lingkungan saat boss** (putus sumber energi) + boss yang makin kuat | Jurus spesial #2 |
| 4 | Lilin di Pasar Malam | Babi Ngepet | 0,5× (badan panjang) | Kampung Kali (pasar) | Sekar | **Investigasi warga / dialog** (wawancara sebagai petunjuk) | Silat manusia: finisher baru |
| 5 | Tali yang Belum Dilepas | Pocong ⚠️ | 0,75× | Kota Lama (makam tua) | Ki Sastro | **Serangan area bertelegraf + bidik bagian tubuh** | Scanner: tandai titik lemah dari jauh |
| 6 | Api di Lereng | Kemamang | inti 0,6× + anak api | Lereng Gunung | Nadia | **Meter penuh**: api menyebar, memadamkan & menyelamatkan menaikkan meter | Kapasitas meter +15% |
| 7 | Bayang di Atas Atap | Kalong Wewe | badan 0,5×, sayap 1,5× | Kota Lama (malam) | Bayu | **Musuh udara** (Jayadwara tetap di darat; jatuhkan pakai cahaya) | Jurus spesial #3 (anti-udara) |
| 8 | Kentongan Tengah Malam | Wewe Gombel | 0,8× | Lereng Gunung (bukit) | Ki Sastro | **Zona larangan pukul** (anak-anak di tubuh boss) | Silat raksasa: cengkeram/lepas |
| 9 | Yang Tak Kasatmata | Genderuwo | 0,8× | Pelabuhan Utara (gudang) | Bayu | **Musuh tak terlihat + tanda scanner terbawa ke mode raksasa** | Scanner: tanda bertahan lebih lama |
| 10 | Prasasti Tujuh Gerbang | Banaspati | 0,9× | Seluruh Arunapura | Prof. Yahyo | **Kota terbakar skala besar**: ujian gabungan, 3 fase | Jurus spesial #4 (penutup arc) |

Kolom "Mekanik baru" sejalan dengan tabel sistem Fase 4 di [10](10-roadmap.md#fase-4--produksi-season-1-ep-210-apr-2028--akhir-2029).

**Urutan pengenalan lokasi:** Situs (1) → Kampung Kali (2) → Distrik Adikara (3) → Kota Lama (5) → Lereng Gunung (6) → Pelabuhan Utara (9) → semua (10). Markas DWARA di Kota Lama dibuka sebagai hub mulai Ep 2 (lihat keputusan D4).

---

## 4. Benang Merah Narasi

Setiap episode wajib memajukan **minimal satu** benang. Tanda ● = beat utama, ○ = sebutan kecil.

| Benang | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| **Aksa belajar kendali** & jejak Kala (2.3) | ● | ○ | ○ | ○ | ○ | ● | ○ | ○ | ○ | ● |
| **Entitas D**: Ratna & publik curiga | ● | ○ | ● | ○ | ○ | ○ | ● | ○ | ○ | ● |
| **Teori energi Kala** (Nadia) | ○ | ○ | ● | ○ | ○ | ● | ○ | ○ | ○ | ● |
| **Uang Adikara & pesugihan** (Sekar) | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ | ● | ○ |
| **Ki Sastro & Prof. Yahyo curiga** pada Aksa | ○ | ○ | ○ | ○ | ● | ○ | ○ | ● | ○ | ● |
| **Arca kedua yang hilang** | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ● | ○ |
| **Bayu & bayangan Dimas** | – | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ |

Beat utama per episode:
- **Ep 1**: Jayadwara lahir; arca kedua terlihat diangkut truk Adikara; kode "Entitas D".
- **Ep 2**: Sekar menemukan bahwa uang curian tuyul mengalir ke rekening penampung yang sama.
- **Ep 3**: Nadia menemukan **pola energi** ([04](04-skenario-cerita.md#arc-1--kebangkitan-ep-110)). Jenglot mengamuk di Distrik Adikara, jadi kerusakan pertama di gedung Adikara dan Ratna mulai menekan DWARA.
- **Ep 4**: Pelaku pesugihan babi ngepet ternyata menerima "modal" dari perantara yang terhubung ke Adikara (**benih konspirasi**).
- **Ep 5**: Ki Sastro melihat Aksa memberi salam yang hanya dipakai keluarga juru kunci candi. Ia mulai curiga.
- **Ep 6**: Nadia memperkenalkan alat ukur sinkronisasi (lore asal meter). Data menunjukkan lonjakan energi selalu terjadi saat Aksa "menghilang".
- **Ep 7**: Bayu nyaris tewas dan diselamatkan Entitas D, lalu siaran publik menyorotnya. Bayu menyebut nama Dimas pertama kali ("teman latihanku dulu").
- **Ep 8**: Ki Sastro memimpin ritual ([04](04-skenario-cerita.md#arc-1--kebangkitan-ep-110)). Ia diam-diam bilang ke Aksa, "Kakekmu dulu juga begini."
- **Ep 9**: Kerja sama pertama Aksa & Bayu ([04](04-skenario-cerita.md#arc-1--kebangkitan-ep-110)). Di gudang pelabuhan ditemukan **jejak alas peti batu berukuran arca**, petunjuk arca kedua.
- **Ep 10**: Prof. Yahyo menemukan prasasti **Sapta Dwara**: ada enam gerbang lain (hook ke Arc 2). Ratna menuntut Entitas D diburu, sementara Aksa terhuyung oleh jejak Kala.

---

## 5. Progresi Pemain di Arc 1

Sistem upgrade baru dibangun di Fase 4 ([10](10-roadmap.md#fase-4--produksi-season-1-ep-210-apr-2028--akhir-2029)). Usulan untuk Arc 1 dibuat **kecil dan linear**: satu unlock tetap per episode tanpa skill tree, sehingga mudah dibangun dan diseimbangkan.

| Jalur | Unlock (Ep) | Sumber lore |
|---|---|---|
| **Jurus spesial Jayadwara** | #1 (Ep 1), #2 (Ep 3), #3 (Ep 7), #4 (Ep 10) | "Ingatan sang penjaga" yang muncul setelah penyegelan |
| **Scanner Netra** | jangkauan (Ep 2), tandai dari jauh (Ep 5), tanda bertahan (Ep 9) | Upgrade dari Nadia |
| **Silat** (berlaku di dua skala) | finisher (Ep 4), cengkeram/lepas (Ep 8) | Ingatan latihan Ki Zahid |
| **Meter** | kapasitas +15% (Ep 6) | Alat penstabil Nadia |

- Nama dan gerak jurus spesial: berbasis pencak silat + motif Dwarapala (mis. gada, injakan bumi). **Hindari pose dan nama yang mirip Specium Ray** ([01](01-konsep-dan-pilar.md#wajib-dihindari)). Desain jurus #2–#4 ditentukan di Fase 4.
- Kurva kesulitan: Ep 1–3 pemaaf (checkpoint rapat, meter turun pelan), Ep 4–7 normal, Ep 8–10 menuntut pemain memakai semua mekanik.

---

## 6. Kartu Episode

Format tetap: **Investigasi** (3 petunjuk; ★ = wajib untuk kelemahan) → **Konfrontasi manusia** → **Boss** → **Meter** → **Catatan**.

### Ep 1 — Gerbang yang Retak · Jerangkong
Batas scope ada di [11-vertical-slice-spec.md](11-vertical-slice-spec.md); skenario adegan per adegan ada di [17-skenario-arc-1.md](17-skenario-arc-1.md#episode-1--gerbang-yang-retak). Yang ditambahkan dokumen ini hanyalah aturan untuk dipakai ulang:
- Semua sistem dasar dibangun **generik** (clue, boss fase, meter, penyegelan, debrief, `UJDEpisodeData`) karena Ep 2–10 hanya mengganti data.
- Penyegelan (2.3) pertama kali tampil di sini, dengan jejak Kala paling tipis.
- Meter sinkronisasi versi dasar: turun saat gedung atau warga terkena, habis = gagal (sesuai [11](11-vertical-slice-spec.md#mode-raksasa)). Mekanik meter naik baru diajarkan di Ep 6 (keputusan D2).

### Ep 2 — Tangan-Tangan Kecil · Tuyul
- **Pembuka wayang:** tuyul sebagai makhluk pesugihan yang mencuri uang untuk tuannya.
- **Investigasi:** ★ jejak kaki kecil berenergi Kala di rumah warga; ★ CCTV warung yang di-retas Sekar (pola rute kawanan); ○ sesajen pesugihan di gang (bestiary).
- **Konfrontasi manusia:** kejar 5 tuyul kecil di gang sempit dan atap Kampung Kali, tangkap dengan pukulan atau sapuan. **Mekanik baru: kejar-kejaran + kawanan.** Kalau gagal tidak game over, tuyul kabur ke titik berikutnya. Umpan mainan dan yuyu (adaptasi dari kepercayaan rakyat) membuat tuyul berhenti sejenak.
- **Boss:** kawanan bergabung jadi satu tuyul raksasa yang lincah.
  - Fase 1: lari dan mencuri properti warga (mobil, gerobak). Kejar dan pukul untuk menjatuhkan.
  - Fase 2: tubuhnya pecah lagi jadi 3 tuyul besar, hanya satu yang asli. **Kelemahan:** pola rute dari CCTV menandai yang asli.
- **Meter:** gang sempit = mudah merusak rumah. Mengajarkan pemain bahwa mengejar membabi buta itu mahal.
- **Catatan:** tuyul boleh lucu dan jahil, cocok untuk episode kedua yang ringan.

### Ep 3 — Lapar Listrik · Jenglot
- **Pembuka wayang:** jenglot sebagai sosok kecil yang "haus" dan disimpan sebagai jimat.
- **Investigasi:** ★ jimat jenglot pecah di ruang server gedung Adikara; ★ grafik konsumsi listrik yang melonjak (data Nadia); ○ kolektor barang antik yang menjualnya.
- **Konfrontasi manusia:** minion **kabel hidup** (tipe minion baru, cepat dan rapuh) di gedung perkantoran.
- **Boss:** jenglot raksasa menyerap listrik kota dan **membesar tiap fase**.
  - Fase 1: putuskan 3 gardu listrik di sekitar arena. **Mekanik baru: objektif lingkungan saat boss.** Setiap gardu yang putus membuat boss mengecil.
  - Fase 2: boss yang sudah lemah mengamuk; selesaikan dengan combat. **Kelemahan:** jimat menunjukkan intinya di dada boss.
- **Meter:** gardu harus diputus tanpa meruntuhkan gedung di sampingnya.
- **Catatan:** pertumbuhan boss dibatasi per fase, **bukan timer menit**, supaya tidak terasa seperti batas waktu transformasi (aturan IP).

### Ep 4 — Lilin di Pasar Malam · Babi Ngepet
- **Pembuka wayang:** babi ngepet yang mencuri sementara rekannya menjaga lilin. Lilin yang bergoyang tanda bahaya.
- **Investigasi:** **Mekanik baru: wawancara warga.** 3 warga pasar memberi kesaksian, dan pemain mencocokkannya dengan bukti scan. ★ pedagang yang kios-nya selalu kehilangan uang; ★ tukang parkir yang melihat seseorang membeli lilin merah tiap malam; ○ penjaga warung yang menyebut "investor" baru.
- **Konfrontasi manusia:** pengawal pelaku (preman, minion manusia biasa; pukul untuk menjatuhkan, bukan membunuh).
- **Boss:** babi raksasa menyeruduk di pasar.
  - Fase 1: boss kebal selama **3 lilin ritual raksasa** di atap gedung masih menyala. Padamkan dengan tangan atau tiupan (interaksi raksasa, jangan meruntuhkan atap).
  - Fase 2: boss rentan; selesaikan. **Kelemahan:** kesaksian tukang parkir menandai lilin di HUD.
- **Meter:** pasar ramai warga sehingga paling sensitif di Arc 1 sebelum Ep 6.
- **Catatan:** pelaku pesugihan ditangkap, bukan dihakimi warga. Tunjukkan konsekuensi hukum, bukan main hakim sendiri ([06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)).

### Ep 5 — Tali yang Belum Dilepas · Pocong ⚠️
- **Pembuka wayang:** kepercayaan bahwa arwah tidak tenang kalau tali kafannya belum dilepas.
- **Investigasi (makam tua Kota Lama, malam):** ★ makam yang terganggu oleh survei lahan; ★ catatan juru kunci makam; ○ bunga dan doa dari keluarga (bestiary, penghormatan).
- **Konfrontasi manusia:** minion **bayang-bayang** (siluet gelap, bukan pocong-pocong kecil) di gang menuju makam.
- **Boss:** pocong raksasa.
  - Fase 1: setiap lompatannya memicu **gelombang kejut bertelegraf**. Pemain belajar membaca tanda dan menghindar. **Mekanik baru: serangan area bertelegraf + bidik bagian tubuh.**
  - Fase 2: bidik **tali ikatan** (3 simpul) dengan lock-on bagian tubuh. **Kelemahan:** catatan juru kunci menandai simpulnya.
- **Penutup:** simpul terakhir dilepas lewat ritual Ki Sastro, lalu arwah tenang dan disegel dengan hormat. Ini **pelepasan, bukan penghancuran**.
- **Meter:** area makam = zona yang tidak boleh rusak (penalti besar).
- **Catatan budaya:** jangan mengolok-olok pemakaman atau kain kafan ([06](06-referensi-mitologi.md#catatan-per-boss-️)). Tanpa humor di episode ini, tanpa adegan merusak makam, tanpa *jumpscare* murahan dengan kafan.

### Ep 6 — Api di Lereng · Kemamang
- **Pembuka wayang:** api-api kecil yang melayang di hutan dan sungai.
- **Investigasi:** ★ titik api yang tidak membakar kayu (scan suhu); ★ pola sebaran api mengikuti aliran sungai (data Nadia); ○ cerita warga desa tentang "obor tanpa pembawa".
- **Konfrontasi manusia:** minion **api kecil** yang hanya bisa dipadamkan dengan serangan tertentu, sambil membantu warga desa mengungsi.
- **Boss:** kemamang raksasa (bola api besar dengan anak-anak api).
  - Fase 1: anak api menyebar ke desa dan hutan. **Mekanik baru: meter penuh.** Memadamkan api dan menyelamatkan warga **menaikkan** meter; api yang dibiarkan menurunkannya.
  - Fase 2: inti kemamang terekspos. **Kelemahan:** pola aliran sungai memberi tahu cara mendorongnya ke air.
- **Meter:** episode ini adalah tutorial meter ([05](05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110)). Nadia menjelaskan lore alatnya di briefing.
- **Catatan:** sistem api menyebar dibuat generik karena dipakai ulang di Ep 10.

### Ep 7 — Bayang di Atas Atap · Kalong Wewe
- **Pembuka wayang:** Kalong Wewe, makhluk kelelawar gaib dari tanah Sunda.
- **Investigasi (malam):** ★ kawanan kelelawar yang lari dari lampu jalan; ★ pemadaman listrik selalu mendahului serangan; ○ catatan observatorium kota.
- **Konfrontasi manusia:** Bayu menyetir, Aksa mengarahkan **lampu sorot** ke kelelawar minion. Bagian ini *on-rails* tanpa sistem kendaraan bebas (keputusan D3).
- **Boss:** kalong raksasa terbang mengelilingi Kota Lama. **Mekanik baru: musuh udara.**
  - Fase 1: boss menukik dan menyambar. Tangkis dan counter saat menukik.
  - Fase 2: nyalakan **menara lampu stadion** atau lampu sorot (objek di arena) supaya boss silau dan jatuh, lalu hajar di darat. **Kelemahan:** pola pemadaman menandai menara lampu yang bisa dinyalakan.
- **Meter:** boss menabrak atap saat jatuh. Pemain memilih di mana menjatuhkannya.
- **Catatan:** Jayadwara **tidak terbang**; sayap baru didapat di Ep 38. Jurus spesial #3 (anti-udara) diberikan di debrief.

### Ep 8 — Kentongan Tengah Malam · Wewe Gombel
- **Pembuka wayang:** Wewe Gombel menyembunyikan anak-anak yang ditelantarkan, dan warga menabuh kentongan dan tampah untuk memanggil mereka pulang.
- **Investigasi:** ★ jejak anak-anak hilang mengarah ke bukit; ★ Ki Sastro menjelaskan cara memanggil anak dengan bunyi-bunyian; ○ cerita orang tua yang menyesal karena sering memarahi anaknya (bestiary, sisi simpatik Wewe Gombel).
- **Konfrontasi manusia:** minion **akar dan ranting hidup** di bukit, sambil mengumpulkan warga yang ikut menabuh kentongan.
- **Boss:** Wewe Gombel raksasa dengan anak-anak tersembunyi di tubuhnya. **Mekanik baru: zona larangan pukul.**
  - Fase 1: memukul zona tubuh tempat anak disembunyikan membuat meter **turun drastis**. Pemain harus memilih target.
  - Fase 2: warga menabuh kentongan dan boss melemah. Anak-anak keluar satu per satu; Jayadwara **cengkeram dan lepas** (unlock di episode ini) untuk menangkap dan menaruh mereka di tempat aman. **Kelemahan:** penjelasan Ki Sastro memicu fase 2 lebih cepat.
- **Catatan:** Wewe Gombel tidak sepenuhnya jahat. Penyegelannya lembut, sesuai sisi simpatik dari legendanya.

### Ep 9 — Yang Tak Kasatmata · Genderuwo
- **Pembuka wayang:** genderuwo, makhluk besar berbulu yang suka menyamar dan menghuni pohon besar atau bangunan tua.
- **Investigasi (gudang pelabuhan, menyusup bersama Bayu):** ★ jejak panas raksasa yang tak terlihat; ★ catatan pengiriman gudang (Sekar); ○ alas peti batu berukuran arca (petunjuk arca kedua, bagian 4).
- **Konfrontasi manusia:** penyusupan ringan. Bayu mengalihkan penjaga, Aksa melawan minion **bayang-bayang** (pakai ulang dari Ep 5) yang hanya terlihat lewat scanner.
- **Boss:** genderuwo raksasa yang **tak terlihat**. **Mekanik baru: tanda scanner terbawa ke mode raksasa.**
  - Fase 1: sebelum transformasi, pemain menandai genderuwo dengan scanner. Tanda itu tetap tampil di mode raksasa selama durasi tertentu, lalu tanda ulang lewat serangan Bayu (suar dari darat).
  - Fase 2: genderuwo menyamar sebagai gedung atau derek pelabuhan. **Kelemahan:** jejak panas membuat samarannya bergetar.
- **Catatan:** pakai grup rig "Buto / humanoid raksasa" ([05](05-daftar-episode-boss.md#pengelompokan-rig--skeleton-hemat-produksi)), jadi rig-nya bisa dipakai ulang di Arc 3.

### Ep 10 — Prasasti Tujuh Gerbang · Banaspati (finale)
- **Pembuka wayang:** Banaspati, roh api yang berjalan dengan tangan dan kepala di bawah.
- **Investigasi (seluruh Arunapura, terbatas waktu cerita, bukan timer):** ★ Prof. Yahyo membaca prasasti di Situs Lawang Sapta; ★ titik-titik api di tiap distrik membentuk pola gerbang; ○ arsip Ki Zahid di museum (petunjuk untuk Arc 4–5).
- **Konfrontasi manusia:** gabungan minion Arc 1 (kerangka, api kecil, bayang-bayang) di tengah evakuasi.
- **Boss (3 fase), ujian gabungan:**
  - Fase 1: Banaspati membakar distrik. Sistem api dari Ep 6 dipakai skala besar sambil menyelamatkan warga.
  - Fase 2: kepalanya terbang menyerang sementara tangannya menghantam. Pakai cara dari Ep 7 (musuh udara) dan Ep 5 (telegraf).
  - Fase 3: inti api di prasasti gerbang. **Kelemahan:** prasasti menunjukkan cara mengembalikan Banaspati ke segelnya.
- **Penutup:** penyegelan dengan jejak Kala paling kuat; Aksa terhuyung. Prof. Yahyo membaca prasasti **Sapta Dwara**, ternyata ada enam gerbang lain. Cliffhanger ke Arc 2.

---

## 7. Aset & Pemakaian Ulang

| Kategori | Arc 1 butuh | Pakai ulang |
|---|---|---|
| **Boss** | 10 boss (Jerangkong, Tuyul, Jenglot, Babi Ngepet, Pocong, Kemamang, Kalong Wewe, Wewe Gombel, Genderuwo, Banaspati) | Genderuwo → rig buto (Arc 3); Banaspati & Kemamang berbagi sistem api |
| **Minion** | 7 tipe: kerangka (1), tuyul kecil (2), kabel hidup (3), preman (4), bayang-bayang (5, 9), api kecil (6, 10), akar hidup (8) | Ep 10 hanya memakai minion lama |
| **Distrik** | 6 distrik Arunapura + markas DWARA | Kampung Kali (2, 4), Kota Lama (5, 7), Lereng Gunung (6, 8) |
| **Sistem generik** | Clue, boss fase, meter, penyegelan, debrief, bestiary, api menyebar, objektif lingkungan, zona tubuh, tanda scanner | Semua dipakai lagi di Arc 2+ |

*Catatan: "preman" memakai mannequin/karakter manusia yang sama dengan warga.*

---

## 8. Panduan Teknis untuk Claude

Mengikuti arsitektur [12](12-technical-design.md):

- **Satu episode = satu `UJDEpisodeData`** (`DA_Ep02_Tuyul`, dst.): ID, judul, boss class, daftar clue (`Clue.Ep02.*`), DataTable dialog (`DT_Dialogue_Ep02`), sequence, unlock.
- **Boss:** `AJDBoss_<Nama>` turunan `AJDBossBase` + StateTree `ST_Boss_<Nama>`. Fase dan transisi didefinisikan di data, bukan hardcode.
- **Mekanik baru per episode** = komponen atau subsystem generik yang bisa dipakai episode lain (mis. `UJDFireSpreadSubsystem`, `UJDBodyZoneComponent`, `UJDEnvironmentObjective`), **bukan** logic khusus satu boss.
- **Map:** satu map per episode (`Ep01_LawangSapta`, `Ep02_KampungKali`, ...) ala Resident Evil 4, distrik dipakai ulang sebagai kit Level Instance; rincian per episode di [28](28-struktur-level-episode.md) (usulan 15 Okt 2026). Usulan lama satu map `Arunapura` (World Partition + Data Layer per episode) **diarsipkan** di [28 bagian 9](28-struktur-level-episode.md#9-arsip-konsep-satu-map-arunapura).
- **Tag & penamaan:** `Clue.EpNN.<Nama>`, `Boss.EpNN`, `Unlock.<Jalur>.<Nama>`.
- **Definisi selesai per episode:** bisa dimainkan dari briefing sampai debrief; semua petunjuk ★ bisa ditemukan; boss bisa dikalahkan dengan **dan** tanpa kelemahan; checklist IP & budaya dicek; tidak ada crash dalam satu playthrough.

---

## 9. Keputusan (dijawab developer 15 Okt 2026)

Semua dijawab developer 15 Okt 2026 sesuai usulan.

| # | Pertanyaan | Keputusan ✅ |
|---|---|---|
| **D1** | Syarat transformasi ([08 keputusan terbuka #1](08-requirement-produksi.md#keputusan-terbuka)) untuk Arc 1? | **Terjadi di momen cerita** (setelah konfrontasi manusia). Paling mudah diatur untuk arc tutorial; transformasi bebas dipertimbangkan di Arc 2 |
| **D2** | Meter di Ep 1 versus tutorial meter di Ep 6? | Ep 1 = versi dasar (**hanya turun**, sesuai [11](11-vertical-slice-spec.md)); Ep 6 = mekanik naik + api menyebar |
| **D3** | Ep 7 butuh kendaraan Bayu? | **On-rails** (Bayu menyetir otomatis), tanpa sistem kendaraan bebas. Kendaraan bebas → backlog |
| **D4** | Markas DWARA sebagai hub mulai kapan? | Mulai Ep 2, versi kecil: satu ruangan, ngobrol dengan anggota, bestiary, unlock. Misi sampingan → setelah Ep 10 jalan |
| **D5** | Judul episode di tabel 3? | Usulan saja, silakan diganti |
| **D6** | Season 1 dipersingkat jadi Ep 1–5 ([10 opsi mempercepat](10-roadmap.md#opsi-mempercepat))? | Belum perlu diputuskan sekarang. Dokumen ini sudah menempatkan cukup mekanik dasar di Ep 1–5 kalau opsi itu dipilih, **kecuali** tutorial meter penuh (Ep 6). Kalau dipersingkat, pindahkan Kemamang ke Ep 5 |
