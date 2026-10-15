# 28 — Struktur Level per Episode (pola ala Resident Evil 4)

> **Status: USULAN v0.1 (15 Okt 2026)**, menunggu persetujuan developer. Developer memilih arah "disusun seperti Resident Evil 4, tapi lebih luas" (15 Okt 2026). Konsep lama "satu map Arunapura" **diarsipkan**, tidak dibuang (bagian 9).
> Sumber: [02](02-setting-dunia.md) (distrik), [16](16-panduan-arc-1.md) (kartu episode Arc 1), [17](17-skenario-arc-1.md) (adegan Ep 1), [18](18-kebutuhan-episode-1.md#c-lingkungan--level) (zona Ep 1), [12](12-technical-design.md) (teknis). Kalau bertentangan, dokumen sumber yang berlaku sampai keputusannya diperbarui.

**Posisi di roadmap:** tidak memajukan jadwal. Ep 1 tetap Fase 2 (greybox level di akhir Fase 1), Ep 2–10 tetap Fase 4. Dokumen ini hanya menetapkan **bentuk** map supaya level Ep 1 dibangun dengan cara yang bisa dipakai ulang.

---

## 1. Keputusan inti

| | |
|---|---|
| **Pola** | **Satu map per episode** (`EpNN_<Lokasi>`), seperti chapter RE4: rangkaian area yang tersambung dan terarah, bukan kota yang dijelajah bebas |
| **"Lebih luas" dari RE4** | Bagian manusia **semi-terbuka**: area investigasi dengan beberapa cabang ke 3 petunjuk. Bagian raksasa = **satu arena terbuka besar** |
| **Pakai ulang** | Distrik dibangun sebagai **kit Level Instance** (`LI_<Distrik>_<Potongan>`) sekali, lalu dirangkai ulang di episode lain |
| **Hub** | **Markas DWARA** = map sendiri (`Hub_MarkasDWARA`), mulai Ep 2 ([16 D4](16-panduan-arc-1.md#9-keputusan-yang-perlu-dijawab-developer)). Pilih episode/misi dari sini, bukan dengan berjalan melintasi kota |
| **Alasan** | Gaya realistis membuat tiap meter persegi mahal; cukup bangun yang dilewati pemain. Performa (Lumen + Nanite + Chaos + raksasa 45 m) lebih mudah dijaga per map. Cocok dengan alur episode yang memang linear |

### Yang diambil dari RE4 dan yang tidak

| Diambil | Tidak diambil (di Arc 1) |
|---|---|
| Area berurutan dengan **gerbang cerita** (pintu/jalan baru terbuka setelah petunjuk atau gelombang selesai) | Ekonomi merchant, inventori koper, amunisi |
| **Cabang opsional** yang memberi hadiah (petunjuk ○, lore, bestiary) | Backtracking panjang lintas map |
| **Jalan pintas** yang terbuka balik ke checkpoint (pintu dibuka dari sisi lain, tangga diturunkan) | Puzzle kunci yang rumit |
| **Arena tertutup** dengan batas alami untuk pertarungan besar | Kamera over-the-shoulder menembak |
| **Set-piece** (kejar-kejaran, on-rails) sebagai selingan | |
| Suasana berganti dalam satu map (sore → senja → malam) | |

---

## 2. Anatomi satu map episode

Setiap map mengikuti urutan zona yang sama dengan struktur episode ([16 bagian 2.1](16-panduan-arc-1.md#21-struktur-dari-07)). Pembuka wayang, briefing, dan debrief tidak butuh map (UI/sequence, atau di hub).

```
[A] Kedatangan ──► [B] Area investigasi ──► [C] Jalur konfrontasi ──► [D] Titik transformasi ──► [E] Arena raksasa
     (linear)        (semi-terbuka, 3 cabang)   (linear, gelombang,       (cutscene,                  (terbuka, 2 fase,
                      ★ ★ ○                      gerbang cerita)           checkpoint)                 meter sinkronisasi)
                         ▲                            │
                         └──── jalan pintas ──────────┘
```

| Zona | Fungsi | Ukuran kasar | Aturan |
|---|---|---|---|
| **A. Kedatangan** | Tutorial gerak/ingat kontrol, perkenalan suasana, tujuan terlihat dari jauh (*landmark*) | jalur ±50–100 m | Linear. Landmark zona E terlihat dari sini (pembanding skala) |
| **B. Area investigasi** | 3 petunjuk (★ ★ ○). Inilah bagian "lebih luas" dari RE4 | ±80×80 – 150×150 m | Semi-terbuka; urutan petunjuk bebas. Petunjuk ○ di cabang yang paling jauh/tersembunyi. Satu atau dua NPC/warga untuk dialog |
| **C. Jalur konfrontasi** | Gelombang minion, set-piece episode | jalur ±100–200 m | Linear dengan **gerbang cerita**: maju setelah gelombang selesai. Checkpoint di awal gelombang terakhir. Jalan pintas balik ke B setelah dilalui |
| **D. Titik transformasi** | Boss bangkit, cutscene transformasi | satu titik | Tanpa loading: pawn diganti di map yang sama |
| **E. Arena raksasa** | Boss 2 fase (Ep 10: 3 fase), gedung hancur, warga | **±300×300 – 500×500 m** | Batas alami (bukit, sungai, laut, gedung tinggi, jalan layang), bukan dinding tak terlihat. 6–10 gedung hancur aktif di satu waktu ([11](11-vertical-slice-spec.md#mode-raksasa)). Zona larangan rusak ditandai jelas |
| **Latar jauh** | Pembanding skala, langit, kota di kejauhan | — | Mesh murah / HLOD / matte; tidak bisa didatangi |

**Kenapa arena E jauh lebih besar dari RE4:** Jayadwara ±45 m. Satu langkahnya ±15–20 m, dodge ±55 m ([23](23-rencana-fase-1.md#11-status--hasil)). Arena 300 m hanya ±7 tinggi badan. Angka pasti diuji di greybox (keputusan L2).

**Zona A–C dan E boleh tumpang tindih.** Contoh Ep 1: zona B/C (galian) adalah bagian dari arena E. Saat transformasi, pemain melihat tempat yang tadi ia jalani dari ketinggian 45 m. Ini momen skala yang diinginkan, jadi diusahakan di setiap episode.

### Teknis per map

- **Satu map, tanpa loading** dari kedatangan sampai penyegelan. Perubahan suasana dan kerusakan memakai **Data Layer di dalam map itu** (`DL_Pra`, `DL_Boss`, `DL_Pasca`), bukan Data Layer lintas episode.
- **Kit distrik = Level Instance** (`LI_KampungKali_Gang01`, `LI_Adikara_Plaza`, ...) yang dirangkai di map episode. Gedung hancur tetap aktor `AJDDestructibleBuilding` terpisah supaya jumlahnya bisa dibatasi per arena.
- **World Partition tidak wajib**. Map Arc 1 cukup kecil untuk dimuat utuh, kecuali Ep 10 (keputusan L4).
- Batas pemain: `BlockingVolume` di balik batas alami; jatuh ke luar → respawn di titik terdekat.
- `UJDEpisodeData` ([16 bagian 8](16-panduan-arc-1.md#8-panduan-teknis-untuk-claude)) menyimpan nama map episode.

---

## 3. Kit distrik (dibangun sekali, dipakai ulang)

| Kit | Isi | Dibangun di | Dipakai ulang di |
|---|---|---|---|
| **Situs & candi** | Batu candi, gerbang, arca, galian berundak, alat berat | Ep 1 | Ep 10 (Arc 5: Ep 44, 48, 50) |
| **Desa bukit** | Rumah desa, warung, menara air, gardu ronda, musala, sawah/kebun | Ep 1 | Ep 6, Ep 8 |
| **Kampung Kali** | Rumah padat, gang, atap seng, jembatan, sungai, pasar | Ep 2 | Ep 4, Ep 10 |
| **Adikara (CBD)** | Gedung tinggi, plaza, jalan layang, gardu listrik, interior kantor | Ep 3 | Ep 10 |
| **Kota Lama** | Bangunan kolonial, alun-alun, museum, makam tua, stadion/menara lampu | Ep 5 | Ep 7, Ep 10, Hub |
| **Lereng Gunung** | Hutan, sungai berbatu, jalan desa menanjak | Ep 6 | Ep 8 |
| **Pelabuhan Utara** | Gudang, kontainer, derek, dermaga, laut | Ep 9 | Ep 10 (opsional) |

Sumber aset sesuai gaya **realistis** ([README](README.md#ringkasan-keputusan-yang-sudah-final)): Fab/Megascans untuk yang generik (batu, tanah, vegetasi, kontainer), Tripo + Blender untuk yang khas Indonesia (warung, rumah kampung, gardu ronda, candi). Ketujuh kit ini kira-kira sama dengan distrik Arunapura, jadi jalan kembali ke konsep satu kota tetap terbuka (bagian 9).

---

## 4. Rancangan map per episode (Arc 1)

Format: **Map** · **Suasana** · alur zona A → E · elemen RE4 · arena raksasa · pakai ulang. Isi episode mengikuti kartu di [16 bagian 6](16-panduan-arc-1.md#6-kartu-episode).

### Ep 1 — `Ep01_LawangSapta` · sore → senja merah → awal malam
- **A. Jalan akses:** mobil DWARA, garis polisi, truk Adikara, mandor. Batu latihan kuda-kuda (interaksi opsional). Gerbang candi terlihat di puncak bukit.
- **B. Galian berundak:** di Ep 1 ketiga petunjuk ada di jalur utama (pengecualian tutorial, [17](17-skenario-arc-1.md#adegan-4--tiga-petunjuk--main--koms)): jejak energi → tulang di dasar galian → prasasti di gerbang candi.
- **C. Galian → gerbang candi:** 3 gelombang kerangka, makin dekat ke gerbang. Checkpoint awal gelombang 3.
- **D. Gerbang candi:** Jerangkong bangkit dari tengah galian; arca kiri pecah → transformasi.
- **E. Arena:** halaman candi + galian + **desa di bawah bukit** (6–10 gedung hancur, musala tidak bisa hancur). Batas: punggung bukit, hutan, jurang. Truk Adikara pergi lewat jalan akses (latar).
- **Elemen RE4:** gerbang cerita (prasasti dibaca → tanah bergetar); dari puncak candi, desa yang nanti jadi arena terlihat sejak zona A.
- **Pakai ulang:** membangun kit **Situs & candi** + **Desa bukit**.
- **Rincian (denah, koordinat greybox, gelombang, arena, cahaya, anggaran):** [30](30-desain-level-ep01.md).

### Ep 2 — `Ep02_KampungKali` · siang → sore
- **A. Ujung jalan kampung:** mobil DWARA berhenti di mulut gang (jalan terlalu sempit). Sungai dan jembatan terlihat.
- **B. Kampung (semi-terbuka):** tiga cabang: ★ rumah warga (jejak kaki kecil), ★ warung dengan CCTV (Sekar meretas), ○ gang belakang dengan sesajen.
- **C. Set-piece kejar-kejaran:** 5 tuyul kabur lewat **gang dan atap berlapis** (dua ketinggian). Rute berbentuk lingkaran besar yang melewati 5 titik; tuyul yang lolos lari ke titik berikutnya (tanpa game over). Umpan mainan/yuyu di titik tertentu. Tangga dan jembatan bambu jadi jalan pintas.
- **D. Lapangan kampung tepi sungai:** kawanan bergabung jadi tuyul raksasa.
- **E. Arena:** tepi sungai + kampung padat + jalan raya di seberang (mobil, gerobak untuk dicuri boss). Batas: sungai lebar, rel kereta, gedung tinggi di kejauhan. Rumah sangat rapat = meter mudah turun.
- **Elemen RE4:** rute atap yang terbuka bertahap; jalan pintas jembatan bambu.
- **Pakai ulang:** membangun kit **Kampung Kali**.

### Ep 3 — `Ep03_Adikara` · malam (lampu kota padam bertahap)
- **A. Plaza depan gedung Adikara:** keamanan sudah dievakuasi; lampu berkedip.
- **B. Interior gedung (vertikal):** lobi → ruang kontrol listrik (★ grafik konsumsi, data Nadia) → ruang server (★ jimat pecah). ○ kolektor antik di lantai eksekutif (cabang opsional lewat tangga darurat).
- **C. Lantai kantor:** minion **kabel hidup**. **Gerbang cerita ala keycard**: Sekar membuka pintu per lantai setelah gelombang selesai. Lift rusak jadi jalan pintas turun.
- **D. Atap gedung:** jenglot pecah keluar dari ruang server dan membesar di plaza.
- **E. Arena:** plaza CBD dengan **3 gardu listrik** di tiga sudut, gedung tinggi di antaranya. Batas: jalan layang, menara kaca. Gedung kaca = kerusakan mahal.
- **Elemen RE4:** progres vertikal yang terkunci per lantai, lift sebagai jalan pintas.
- **Pakai ulang:** membangun kit **Adikara (CBD)** + interior kantor.

### Ep 4 — `Ep04_PasarKali` · pasar malam
- **A. Parkiran pasar:** tukang parkir (salah satu saksi).
- **B. Pasar malam (semi-terbuka, hub wawancara):** 3 warga di 3 sudut pasar; kesaksian dicocokkan dengan bukti scan. Ini area B paling "RE4 desa": ramai, banyak lorong kios.
- **C. Gudang di belakang pasar:** pengawal pelaku (preman). Pelaku ditangkap; lilin ritual menyala → boss bangkit.
- **E. Arena:** pasar + **atap 3 gedung tempat lilin raksasa**. Batas: sungai Kampung Kali (dari Ep 2, sisi lain), jalan raya. Warga paling banyak di Arc 1.
- **Elemen RE4:** pasar sebagai "desa" yang dijelajah dulu sebelum ada pertempuran.
- **Pakai ulang:** kit **Kampung Kali** (Ep 2) dirangkai ulang jadi pasar; tambah prop kios dan lampu pasar malam.

### Ep 5 — `Ep05_MakamKotaLama` · malam, sunyi
- **A. Jalan kolonial Kota Lama:** lampu jalan kuning, gedung tua.
- **B. Kawasan makam tua (luar pagar):** ★ makam terganggu oleh patok survei, ★ rumah juru kunci (catatan), ○ bunga dan doa keluarga.
- **C. Gang menuju gerbang makam:** minion **bayang-bayang**. **Gerbang makam terkunci**; kuncinya dari juru kunci (gerbang cerita). Nada tenang, tanpa humor ([16 Ep 5](16-panduan-arc-1.md#6-kartu-episode)).
- **E. Arena:** **alun-alun Kota Lama** di sebelah makam. Makam = **zona larangan rusak** (penalti besar), jadi pertarungan sengaja digiring ke alun-alun. Batas: deretan gedung kolonial, kanal.
- **Pakai ulang:** membangun kit **Kota Lama** (dipakai juga untuk eksterior museum di hub).

### Ep 6 — `Ep06_LerengDesa` · sore cerah → asap dan api
- **A. Jalan desa menanjak:** warga mulai mengungsi.
- **B. Desa + tepi hutan (area B terbesar Arc 1):** ★ titik api yang tidak membakar kayu, ★ pola api mengikuti sungai (data Nadia), ○ cerita warga. Sambil mengarahkan warga ke titik kumpul.
- **C. Jalan setapak hutan:** minion **api kecil**; evakuasi warga sebagai syarat maju.
- **E. Arena:** **lembah sungai** dengan desa di kedua sisi dan hutan di lereng. Sungai dipakai untuk mendorong inti kemamang (kelemahan). Api menyebar ke hutan dan desa (tutorial meter penuh). Batas: punggung gunung, air terjun.
- **Pakai ulang:** kit **Desa bukit** (Ep 1) + membangun kit **Lereng Gunung**.

### Ep 7 — `Ep07_KotaLamaMalam` · malam, listrik padam
- **A–B. Observatorium / jalan Kota Lama:** ★ kawanan kelelawar lari dari lampu jalan, ★ pola pemadaman, ○ catatan observatorium.
- **C. Set-piece on-rails:** Bayu menyetir di **jalur spline** lewat jalan-jalan Kota Lama; Aksa menyorot kelelawar dengan lampu sorot ([16 D3](16-panduan-arc-1.md#9-keputusan-yang-perlu-dijawab-developer)). Ini pengganti zona C linear yang biasa.
- **E. Arena:** Kota Lama + **stadion dengan menara lampu**. Ruang udara harus lapang (boss terbang). Batas: gedung kolonial tinggi, rel layang.
- **Pakai ulang:** kit **Kota Lama** (Ep 5) dari sudut kota yang berbeda; tambah stadion.

### Ep 8 — `Ep08_BukitKentongan` · tengah malam
- **A. Kaki bukit:** warga desa berkumpul, kentongan dibagikan.
- **B. Desa lereng:** ★ jejak anak-anak hilang ke arah bukit, ★ Ki Sastro (cara memanggil anak), ○ orang tua yang menyesal.
- **C. Jalan setapak ke puncak bukit:** minion **akar hidup**; mengumpulkan warga yang ikut menabuh kentongan (mereka mengikuti Aksa ke atas).
- **E. Arena:** lereng bertingkat (terasering) dengan **lapangan desa sebagai titik aman** untuk menaruh anak-anak (cengkeram/lepas). Batas: hutan lebat, tebing.
- **Pakai ulang:** kit **Lereng Gunung** + **Desa bukit**.

### Ep 9 — `Ep09_PelabuhanUtara` · malam berkabut
- **A. Gerbang pelabuhan:** Bayu dan Aksa menyusup lewat pagar.
- **B–C. Kompleks gudang (paling mirip RE4):** gudang berlapis, kontainer jadi lorong. Bayu mengalihkan penjaga; minion **bayang-bayang** hanya terlihat lewat scanner. ★ jejak panas raksasa, ★ catatan pengiriman (Sekar), ○ alas peti batu berukuran arca (gudang terkunci, cabang opsional). Pintu gudang dibuka dari dalam jadi jalan pintas.
- **E. Arena:** dermaga + tumpukan kontainer + **derek** (genderuwo menyamar sebagai derek/gedung). Batas: laut (alami, terbuka luas), tembok pabrik.
- **Pakai ulang:** membangun kit **Pelabuhan Utara**.

### Ep 10 — `Ep10_Arunapura` · senja → kota terbakar (finale)
- Map paling besar: **irisan Arunapura** yang dirangkai dari kit Ep 1–9, bukan kota utuh.
- **A–B. Investigasi lintas distrik:** ★ prasasti di Situs Lawang Sapta, ★ titik api di tiap distrik (pola gerbang), ○ arsip Ki Zahid di museum. Perpindahan antardistrik lewat **perjalanan mobil DWARA** (cutscene pendek / loading tersembunyi), seperti perpindahan area di RE4.
- **C. Evakuasi:** gabungan minion Arc 1 (kerangka, api kecil, bayang-bayang) di jalan Kampung Kali yang terbakar.
- **E. Arena 3 fase yang berpindah:** fase 1 di **Kampung Kali + sungai** (api menyebar) → fase 2 bergeser ke **Distrik Adikara** (kepala terbang, serangan bertelegraf) → fase 3 di **Situs Lawang Sapta** (prasasti gerbang). Perpindahan fase = boss mundur, pemain mengejar (cutscene pendek).
- **Pakai ulang:** semua kit. Kandidat satu-satunya map Arc 1 yang memakai World Partition (keputusan L4).

### Hub — `Hub_MarkasDWARA` (mulai Ep 2)
- Ruang bawah tanah di bawah museum Kota Lama: ruang briefing, lab Nadia (bestiary, upgrade scanner), meja Sekar, ruang latihan (bisa jadi tempat uji combat).
- Versi Ep 2: satu ruangan ([16 D4](16-panduan-arc-1.md#9-keputusan-yang-perlu-dijawab-developer)); bertambah bertahap. Dari sini pemain memilih "berangkat" ke episode berikutnya atau mengulang episode lama (keputusan L5).

---

## 5. Ringkasan per episode

| Ep | Map | Area B (investigasi) | Set-piece C | Arena E | Batas alami | Kit baru |
|---|---|---|---|---|---|---|
| 1 | `Ep01_LawangSapta` | Galian (linear) | 3 gelombang kerangka | Candi + desa bukit | Bukit, jurang | Situs, Desa bukit |
| 2 | `Ep02_KampungKali` | Kampung, 3 cabang | Kejar tuyul di atap | Tepi sungai + kampung | Sungai, rel | Kampung Kali |
| 3 | `Ep03_Adikara` | Interior gedung vertikal | Lantai terkunci | Plaza CBD + 3 gardu | Jalan layang | Adikara |
| 4 | `Ep04_PasarKali` | Pasar malam (wawancara) | Gudang preman | Pasar + atap lilin | Sungai, jalan raya | — |
| 5 | `Ep05_MakamKotaLama` | Luar makam | Gang + gerbang terkunci | Alun-alun (makam dilarang rusak) | Gedung kolonial, kanal | Kota Lama |
| 6 | `Ep06_LerengDesa` | Desa + hutan (terbesar) | Evakuasi + api kecil | Lembah sungai | Gunung, air terjun | Lereng Gunung |
| 7 | `Ep07_KotaLamaMalam` | Jalan + observatorium | On-rails mobil Bayu | Kota Lama + stadion | Gedung tinggi | (stadion) |
| 8 | `Ep08_BukitKentongan` | Desa lereng | Naik bukit bersama warga | Terasering + lapangan aman | Hutan, tebing | — |
| 9 | `Ep09_PelabuhanUtara` | Kompleks gudang (menyusup) | Gudang berlapis | Dermaga + derek | Laut | Pelabuhan |
| 10 | `Ep10_Arunapura` | Lintas distrik | Evakuasi kota terbakar | 3 arena berpindah | Semua | — |

Kit baru per episode: Ep 1 (2), Ep 2, 3, 5, 6, 9 (1 masing-masing), sisanya 0. Episode tanpa kit baru (4, 7, 8, 10) adalah peluang mengejar jadwal ±2 bulan per episode ([16 bagian 2.2](16-panduan-arc-1.md#22-anggaran-produksi-per-episode-ep-210)).

---

## 6. Arc 2–5 (garis besar)

Pola yang sama dipakai untuk peta regional ([02](02-setting-dunia.md#peta-misi-regional)): **satu map per episode, kit per wilayah** (Sumatra, Kalimantan, Sulawesi, Nusa Tenggara, Maluku–Papua, Jawa Timur, Bali). Episode yang kembali ke Arunapura (mis. Ep 21–25, 31, 33, 36) memakai kit Arc 1. Rincian Arc 2 (Ep 11–20) sudah disiapkan di [29](29-struktur-level-arc-2.md); Arc 3–5 dibuat saat arc tersebut mendekati produksi.

---

## 7. Urutan kerja

| Kapan | Apa | Oleh |
|---|---|---|
| Akhir Fase 1 (Iterasi 7–9) | Uji ukuran arena raksasa di `Test_Destruction` / `Test_Boss` / `Test_Loop`: berapa meter terasa pas untuk raksasa 45 m, berapa gedung hancur sebelum < 60 FPS | Claude (skrip) + developer |
| Akhir Fase 1 | **Greybox `Ep01_LawangSapta`** dengan zona A–E dari bagian 4 | Claude (skrip kotak) + developer (rangkai, uji alur) |
| Fase 2 (Jun–Jul 2027) | Kit Situs & candi + Desa bukit (realistis), level art Ep 1 | Developer + Claude |
| Awal Fase 4 | Konfirmasi pola ini setelah Ep 1 selesai; mulai Ep 2 | Developer |

---

## 8. Keputusan yang perlu dijawab developer

| # | Pertanyaan | Usulan Claude |
|---|---|---|
| **L1** | Setuju pola satu map per episode (ala RE4) untuk Season 1? | **Ya.** Konsep satu map Arunapura diarsipkan (bagian 9) |
| **L2** | Ukuran arena raksasa | Mulai **±400×400 m**, disesuaikan setelah uji Iterasi 7–8 |
| **L3** | Area B (investigasi): seberapa "luas"? | ±80–150 m per sisi, 3 cabang. Lebih besar dari ini menambah biaya aset realistis tanpa menambah petunjuk |
| **L4** | Ep 10 memakai World Partition? | Diputuskan saat Ep 10 dibuat. Default: map biasa + perpindahan distrik lewat cutscene mobil |
| **L5** | Episode bisa diulang dari hub? | **Ya** (pilih episode dari Markas DWARA); murah karena tiap episode sudah satu map |
| **L6** | Transisi zona C → E tanpa loading? | **Ya**, satu map utuh; loading hanya di perpindahan hub ↔ episode |

---

## 9. Arsip: Konsep "Satu Map Arunapura"

> **Status: DIARSIPKAN (15 Okt 2026)**, bukan dibatalkan. Konsepnya dinilai bagus oleh developer; disimpan untuk Season 2+ atau kalau tim dan dana bertambah.

**Isi konsep (usulan lama di [16 bagian 8](16-panduan-arc-1.md#8-panduan-teknis-untuk-claude) dan [02](02-setting-dunia.md#kota-utama-arunapura)):**
- Arunapura = **hub semi-open-world**: satu map besar `Arunapura` memakai **World Partition**, keenam distrik (Kota Lama, Kampung Kali, Distrik Adikara, Pelabuhan Utara, Situs Lawang Sapta, Lereng Gunung) tersambung dalam satu dunia.
- Tiap episode = **Data Layer** (`DL_Ep02`, `DL_Ep03`, ...) yang menyalakan prop, petunjuk, spawn, gedung hancur, NPC, dan suasana waktu khusus episode itu.
- Ep 1 tetap map sendiri (`Ep01_LawangSapta`) sebagai vertical slice.
- Investigasi dilakukan dengan berjalan di distrik; Markas DWARA di bawah museum Kota Lama bisa didatangi langsung di kota.
- Potensi jangka panjang: jelajah bebas, misi sampingan, kerusakan kota yang terasa berlanjut antarepisode.

**Kenapa diarsipkan:**
- Gaya realistis membuat seluruh kota harus layak dilihat dari segala arah, termasuk dari ketinggian 45 m. Biaya awalnya terlalu besar untuk dev solo sambilan.
- Streaming World Partition + Lumen + Chaos + raksasa dengan jarak pandang jauh lebih sulit dijaga di 60 FPS.
- Kerusakan antarepisode di satu kota perlu dikelola (reset/persisten) dan menambah kerumitan.

**Jalan kembali:** kit distrik di bagian 3 dibangun sebagai Level Instance dengan skala dan orientasi yang konsisten. Kalau konsep ini dihidupkan lagi, kit yang sama dirangkai jadi satu map `Arunapura` (World Partition) dan konten episode dipindah ke Data Layer. Syarat menghidupkan: Season 1 laku, ada tambahan artis lingkungan, dan uji performa kota utuh lulus.
