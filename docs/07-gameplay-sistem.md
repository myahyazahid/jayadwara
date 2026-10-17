# 07 — Gameplay & Sistem

## Mode Manusia (porsi waktu terbesar)

| Sistem | Deskripsi |
|---|---|
| **Traversal** | Lari, panjat ringan, kendaraan sederhana (bersama Bayu) |
| **Scanner Netra** | Alat investigasi ciptaan Nadia: scan jejak energi Kala, sampel, makhluk tak terlihat |
| **Investigasi** | Cari petunjuk, wawancara warga, baca prasasti (bersama Prof. Yahyo). Hasilnya **membuka kelemahan boss** |
| **Combat silat** | Melee melawan minion / bentuk awal monster. Sistem yang sama dipakai di mode raksasa |
| **Dialog & pilihan** | Sederhana, mendukung tema "apa benar dia pahlawan?" dan konsekuensi (mis. salah tuduh di Ep 16) |

### Satu sistem, dua skala

Keputusan developer 16 Okt 2026. Aksa dan Jayadwara memakai **sistem combo inti yang sama**: input, ability, dan aturan combo (bagian di bawah). Yang beda per skala:
- **Rasa**: animasi, hit-stop, guncangan kamera, debu/puing (`DA_CombatProfile_Human` vs `DA_CombatProfile_Giant`).
- **Jurus khas**: 2–3 jurus per skala, mulai **Fase 2** (beam Jayadwara dibahas terpisah).

Di Fase 1 combo kedua skala identik.

### Combo & arah

Keputusan developer 16 Okt 2026. Berlaku sama untuk Aksa dan Jayadwara (satu ability, beda `DA_CombatProfile`).

| Input | Hasil |
|---|---|
| Pukulan ringan berulang | Combo **4 pukulan**; pukulan ke-4 = finisher |
| **Maju** + pukul, musuh agak jauh | Pembuka **terjang** (gap closer): lompat kecil ke dekat musuh, pukulan dari atas ke dada; lalu combo lanjut dari pukulan 2 |
| **Mundur** + pukul | Pembuka **sapuan / pukulan sambil mundur**, lalu combo lanjut dari pukulan 2 |
| Netral, atau maju saat musuh sudah dekat | Combo biasa |
| **Kiri/kanan** + pukul | Untuk **memilih target** (soft target ala Arkham, [23](23-rencana-fase-1.md) Iterasi 4), bukan jurus |
| Pukulan berat di tengah combo | **Cabang finisher**: setelah pukulan 1, 2 dan 3 masing-masing punya pukulan berat sendiri; dari diam / setelah pukulan 4 = pukulan berat biasa |

Arah dihitung **relatif ke musuh yang dituju**, bukan ke kamera, supaya "maju" selalu berarti mendekati musuh. Combo sengaja tidak lebih dari 4 pukulan: referensinya Arkham + Sekiro ringan, dan combo yang lebih panjang membuat pemain terkunci animasi sehingga telat menangkis. Variasi datang dari pembuka arah dan cabang finisher, bukan dari panjang combo.

#### Daftar jurus (konsep pose)

Disetujui developer 16 Okt 2026 dari konsep pose ("Usulan Jurus Aksa"). Patokan bentuk gerak untuk memilih animasi placeholder F1 dan brief mocap F2; tendangan memakai bentuk taekwondo. Gaya combat tidak harus silat murni; yang dikejar combat yang seru (keputusan developer 16 Okt 2026). Sama untuk Aksa dan Jayadwara.

| Input | Jurus | Gerak |
|---|---|---|
| Ringan ×1 | Jab | Pukulan lurus cepat tangan kiri (depan) |
| Ringan ×2 | Cross | Pukulan lurus tangan kanan dengan putaran pinggul |
| Ringan ×3 | Hook | Pukulan melengkung tangan kiri, siku setinggi bahu |
| Ringan ×4 | Tendangan putar belakang (*dwi huryeo chagi*) | Badan berputar membelakangi musuh, tumit kanan disabetkan melengkung; akhir combo |
| Maju + ringan | Terjang | Lompat kecil ke dekat musuh, tangan kanan dari atas dihantamkan ke dada |
| Mundur + ringan | Pukul mundur | Langkah mundur ±1,5 m lalu jab balasan |
| Berat (diam, atau setelah pukulan 4) | Pukulan putar | Satu tangan: badan diputar menjauh sambil menarik tangan, lalu melangkah maju dan memutar balik melepas pukulan lurus keras |
| Ringan ×1 → berat | Finisher 1: tendangan belakang (*dwi chagi*) | Berputar membelakangi musuh, telapak kaki didorong lurus ke belakang |
| Ringan ×2 → berat | Finisher 2: tendangan ganda melompat (*narae chagi*) | Lompat kecil, dua tendangan melingkar beruntun (kanan lalu kiri), dua kali kena |
| Ringan ×3 → berat | Finisher 3 | Animasi dipilih developer langsung di Mixamo (`finisher_03.fbx`, keputusan 17 Okt 2026); selama belum ada, slot ini = pukulan putar |
| Udara + ringan | Tendangan terbang memutar | Satu putaran penuh di udara, lalu kaki kanan menendang lurus, kaki kiri terlipat |
| Udara + berat | Hantaman ke bawah | Menukik, tinju kanan ke tanah sampai berlutut, gelombang kejut |

### Dodge per arah

Keputusan developer 16 Okt 2026. Sama untuk Aksa dan Jayadwara; `UJDGA_Dodge` sudah memilih montage per arah.

| Input | Gerak |
|---|---|
| Mundur + dodge | **Salto belakang** |
| Kiri/kanan + dodge | Guling ke samping atau *cartwheel* |
| Maju + dodge | Langkah cepat menunduk (bukan salto, supaya tidak menabrak musuh) |

Gerak dibedakan per arah, bukan per jarak ke musuh, supaya pemain selalu tahu hasil tombolnya.

### Parry (tepis)

Usulan 17 Okt 2026, dinilai lewat gate parry Iterasi 3 ([23](23-rencana-fase-1.md)). Sama untuk Aksa dan Jayadwara. Tekan tangkis tepat sebelum pukulan kena (jendela 0,2 s manusia / 0,25 s raksasa):

| Urutan | Rasa |
|---|---|
| 1. Kena | Hit-stop khusus parry (±0,12 s, hampir beku) + percikan di titik kena + suara parry + shake kamera |
| 2. Tepis | Tepisan cepat menghadap penyerang, **2 varian bergantian** (tepis luar / tepis dalam), bukan pose tangkis ditahan |
| 3. Lambat | Slow-mo singkat seluruh dunia (±0,35 s di laju 0,35×), hanya kalau pemain terlibat |
| 4. Balas | Penyerang stagger 1 s; **pukulan ringan dalam 0,8 s = serangan balik** ke penyerang itu (selalu ke dia, apa pun arah input), lalu combo lanjut dari pukulan 2 |

Semua angka di `DA_CombatProfile_*` bagian Block|Parry (milik yang bertahan).

### Serangan udara

Keputusan developer 16 Okt 2026. Sama untuk Aksa dan Jayadwara.

| Input di udara | Hasil |
|---|---|
| Pukulan ringan | Tendangan terbang memutar; badan "ngambang" sebentar (gravitasi dikurangi ±0,3 s). Maks. **2 per lompatan**, reset saat mendarat |
| Pukulan berat | **Hantaman ke bawah**: menukik lurus ke tanah, saat mendarat gelombang kejut dengan radius (hit-stop, shake). Untuk Jayadwara nanti ikut merusak gedung sekitar ([23](23-rencana-fase-1.md) Iterasi 7) |
| Dodge, tangkis | Tidak bisa di udara (F1) |

Bentuknya tendangan terbang memutar dan hantaman tinju ke bawah (lihat daftar jurus di atas), bukan pose tendangan terbang khas Ultraman.

### Reaksi kena pukul

Keputusan 17 Okt 2026 (Fase 1 Iterasi 4). Sama untuk Aksa, Jayadwara, dummy, dan musuh; angka di [23](23-rencana-fase-1.md) bagian 5.

| Reaksi | Kapan | Hasil |
|---|---|---|
| Ringan | Kena pukul, poise belum pecah | Tersentak ±0,3 s, serangan musuh terpotong. Pemain yang sedang menyerang tidak tersentak (combo tidak putus), damage tetap masuk |
| Stagger | Poise pecah (0) | Terhuyung 1,2 s, terdorong ±3 m menjauhi penyerang, semua aksi terkunci. Poise kembali penuh setelahnya |
| Jatuh | Poise pecah oleh serangan bertanda **Jatuh** (finisher berat, hantaman ke bawah), atau serangan Jatuh mengenai yang sedang stagger | Terlempar ±6 m, rebah, lalu bangun dengan i-frame (tidak bisa dipukuli terus di tanah) |

Poise beregenerasi setelah jeda tanpa kena pukul. Raksasa memakai aturan yang sama; beratnya dari hit-stop, shake, debu, dan gedung, bukan dari reaksi yang lebih lambat (ala Mebius).

### Soft target

Pukulan "menempel" ke musuh searah input (Q3, gaya Arkham): musuh dalam kerucut ±30° dari arah stik/WASD (tanpa input: arah hadap) dan dalam radius cari target, dipilih yang paling dekat dan paling lurus. Saat pukulan dimulai badan berputar ke target, dan kalau celahnya dekat (≤ 2,2 m) badan meluncur sampai jarak pukul (maks. 2 m, 0,1 s). Lebih jauh dari itu tidak disedot: pakai terjang (Combo & arah). Penanda kecil di atas kepala target di HUD. Lock-on kamera hanya untuk boss raksasa ([23](23-rencana-fase-1.md) Iterasi 6). Raksasa: jarak × skala.

## Mode Raksasa (Jayadwara)

| Sistem | Deskripsi |
|---|---|
| **Combat raksasa gesit, impact berat** | Gerak "ala Mebius" (keputusan developer 16 Okt 2026): serangan secepat mode manusia, berbalik badan cepat, lompatan tinggi. Rasa raksasa datang dari momen kena (hit-stop, guncangan kamera, debu, suara langkah, gedung runtuh pelan), bukan dari animasi yang diperlambat. Gerakan dan nama jurus tetap silat/Dwarapala, tidak meniru jurus Ultraman ([01](01-konsep-dan-pilar.md#wajib-dihindari)) |
| **Meter sinkronisasi** | Lihat di bawah |
| **Kelemahan boss** | Terbuka dari hasil investigasi mode manusia |
| **Destruction** | Gedung bisa hancur; kerusakan memengaruhi meter sinkronisasi |
| **Kamera skala** | Rig kamera khusus + elemen pembanding (kendaraan, warga, fog) agar terasa raksasa |

### Tameng Inten (perisai energi)

Usulan 17 Okt 2026 (permintaan developer), **Fase 2**. Hanya Jayadwara; Aksa tidak punya walau kalungnya sama. Visual konsep: artifact "Tameng Inten".

Serangan **kekuatan** (bola api, sinar, semburan; ditandai `Attack.Type.Energy`) tidak bisa ditangkis lengan. Saat tombol tangkis ditahan dan yang datang serangan energi, permata dada menyala dan melepas **16 keping berlian** bercahaya yang menyatu jadi perisai belah ketupat di depan badan, lalu kembali ke permata dan padam saat dilepas. Pukulan fisik tetap ditangkis lengan seperti biasa. Tombolnya tetap satu (tangkis).

| Kasus | Hasil (angka usulan) |
|---|---|
| Ditahan sebelum energi tiba | **Serap**: keping menyatu dalam 0,25 s, tanpa damage; bola api −2 keping |
| Ditekan dalam 0,25 s terakhir | **Pantul**: keping langsung menyatu, proyektil berbalik ke pengirimnya, tanpa kehilangan keping; anti spam 0,5 s (sama parry) |
| Sinar ditahan | Tidak bisa dipantul; −1 keping tiap 0,15 s, Jayadwara terdorong mundur |
| Keping habis | **Pecah**: keping berhamburan, stagger 1,2 s, sisa serangan kena badan; keping penuh lagi 8 s |
| Tanpa perisai / telat | Energi kena penuh (±15 HP) |
| Menghindar | Jayadwara aman, tapi energi yang lolos mengenai gedung di belakangnya → kerusakan + penalti Sync. Perisai = cara melindungi kota |

- Pulih 1 keping / 1,5 s, mulai 1 s setelah tombol dilepas. Arah sama dengan tangkis (depan 140°). **Tidak memakai stamina**: sumber dayanya keping, terlihat dari jumlah berlian di perisai dan di HUD.
- **Bentuk:** belah ketupat besar dari belah ketupat kecil (bentuk kalung pecahan arca Ki Zahid), emas hangat, celah tipis antar keping. Pose: tangan kiri terbuka ke depan, tangan kanan di sisi dada.
- **Batas IP** ([01](01-konsep-dan-pilar.md#wajib-dihindari)): bukan dinding bulat/heksagon transparan, tidak keluar dari lengan, tanpa silang lengan atau pose L. Permata dada menyala **hanya selama perisai keluar** lalu padam, tidak berkedip, dan tidak menunjukkan sisa keping (K1, K6 di [14](14-model-sheet-jayadwara.md)).
- **Kode (perkiraan):** hasil baru di `UJDCombatComponent::ResolveIncomingHit` (`ShieldAbsorbed`, `Reflected`, `ShieldBroken`), komponen keping, cabang di `UJDGA_Block` (`bEnergyShield` di profil raksasa), `AJDEnergyProjectile` (bisa dipantul), `AJDEnergyBeam` (berhenti di perisai atau gedung). Developer: Niagara keping dari socket permata, material emissive, SFX.
- **Kapan:** bukan Fase 1 (kerangka & Jerangkong tidak punya serangan energi; puing Jerangkong fisik). Dibuat bersama musuh energi pertama, kandidat Kemamang Ep 6 (bola api, cocok untuk pantul); sinar untuk Banaspati Ep 10.

## Meter Sinkronisasi

Pengganti timer transformasi.

| Kejadian | Efek |
|---|---|
| Gedung / properti warga hancur | Meter turun |
| Warga terluka | Meter turun drastis |
| Melindungi warga / menyelamatkan sandera | Meter naik |
| Bertarung sesuai kelemahan boss | Meter stabil |
| Meter habis | Transformasi berakhir paksa → Aksa di tempat, bisa berubah lagi setelah energi transformasi penuh |

- Diperkenalkan sebagai tutorial di **Ep 6 (Kemamang)**.
- Payoff naratif di **Ep 50**: harapan warga memulihkan sinkronisasi.
- Secara lore: teknologi pengukurnya dikembangkan Nadia.

## Transisi & Progression

- **Syarat transformasi**: **energi transformasi** penuh (bar di HUD manusia; keputusan 12 Okt 2026). Transformasi pertama tiap episode boleh dipicu cerita.
- **Kalah sebagai Jayadwara** (Health habis atau meter sinkronisasi habis): kembali jadi Aksa **di tempat**, pertarungan berlanjut; Aksa menghindar sampai energi penuh lagi lalu berubah lagi. Aksa mati = ulang checkpoint. Detail: [23](23-rencana-fase-1.md#45-kalah-sebagai-jayadwara--energi-transformasi-q15).
- **Jubah upacara** — lihat bagian [Jubah upacara](#jubah-upacara) di bawah.
- **Upgrade**:
  - Skill tree silat (berlaku di dua skala).
  - Upgrade scanner Netra.
  - "Ingatan" sang penjaga → membuka jurus baru Jayadwara.
  - Kekuatan dari ujian: **sayap** (Lembuswana, Ep 38), **kekuatan bumi** (Antaboga, Ep 44).
- **Kondisi kalah & checkpoint** untuk kedua mode.

### Jubah upacara

Keputusan 13 Okt 2026. Desain: K9 di [14](14-model-sheet-jayadwara.md); rencana iterasi: [26](26-rencana-jubah-jayadwara.md). Jayadwara memakai jubah panjang **hanya di luar combat**; saat bertarung tanpa jubah (kaki & siluet tetap terbaca dari kamera belakang, tanpa simulasi kain di combat).

| Kejadian | Jubah | Pemicu |
|---|---|---|
| Transformasi | Muncul **berjubah** (animasi kedatangan) | Tombol transformasi (T / L1+R1) |
| Lock-on ke boss pertama kali | Animasi **lepas jubah** ±2 s; jubah buyar jadi cahaya/serpihan emas ("kembali ke kalung"), tidak jatuh ke tanah. Boss sedang animasi intro supaya pemain tidak dipukul | Otomatis dari lock-on (Q / R3) |
| Menyerang/dodge sebelum lock-on | Lepas **versi cepat** (dikibas ±0,5 s), input serangan tidak hilang | Otomatis |
| Boss kalah | Jubah **kembali** di pose menang/kepergian | Otomatis / cutscene |
| Cutscene | Diatur per adegan | Sequencer |

- Animasi lepas pendek dan bisa di-skip (terlihat tiap episode).
- Tanpa tombol khusus. Tombol manual (pamer/foto, usulan D-pad atas) → backlog.

---

## Struktur Satu Episode

1. **Pembuka wayang** — Ki Sastro menceritakan legenda monster episode itu dalam cutscene wayang kulit.
2. **Briefing di markas DWARA** — misi utama dari Kol. Bagas, misi sampingan dari anggota lain.
3. **Investigasi di hub** — scan (Nadia), telusuri situs (Prof. Yahyo), tangani warga (Ratna), menyusup (Bayu), hacking (Sekar). Membuka kelemahan boss.
4. **Konfrontasi skala manusia** — combat silat melawan minion / bentuk awal monster.
5. **Transformasi → boss fight raksasa** dengan meter sinkronisasi.
6. **Debrief** — dampak cerita, hubungan dengan anggota tim, upgrade.

## Markas DWARA (Hub Antar-Episode)

Mirip konsep markas di Mass Effect:
- Ngobrol dengan anggota tim → memperdalam hubungan.
- Membuka misi sampingan per anggota.
- Upgrade alat & skill.
- Melihat arsip monster (bestiary) yang terisi dari hasil investigasi.

## Jenis Misi per Anggota

| Anggota | Jenis Misi |
|---|---|
| Kol. Bagas Suryo | Misi utama, operasi taktis |
| Dr. Nadia Prameswari | Scan, sampel, uji alat |
| Prof. Yahyo Sasmito | Artefak, situs kuno, prasasti |
| Ratna Dewantari | Evakuasi, media, VIP, opini publik |
| Ki Sastro | Ritual, penyegelan, warga adat |
| Bayu Saputra | Stealth, kejar-kejaran, kendaraan |
| Sekar | Hacking, intel digital |
