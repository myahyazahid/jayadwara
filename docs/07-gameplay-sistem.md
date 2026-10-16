# 07 — Gameplay & Sistem

## Mode Manusia (porsi waktu terbesar)

| Sistem | Deskripsi |
|---|---|
| **Traversal** | Lari, panjat ringan, kendaraan sederhana (bersama Bayu) |
| **Scanner Netra** | Alat investigasi ciptaan Nadia: scan jejak energi Kala, sampel, makhluk tak terlihat |
| **Investigasi** | Cari petunjuk, wawancara warga, baca prasasti (bersama Prof. Yahyo). Hasilnya **membuka kelemahan boss** |
| **Combat silat** | Melee melawan minion / bentuk awal monster. Sistem yang sama dipakai di mode raksasa |
| **Dialog & pilihan** | Sederhana, mendukung tema "apa benar dia pahlawan?" dan konsekuensi (mis. salah tuduh di Ep 16) |

### Combo & arah

Keputusan developer 16 Okt 2026. Berlaku sama untuk Aksa dan Jayadwara (satu ability, beda `DA_CombatProfile`).

| Input | Hasil |
|---|---|
| Pukulan ringan berulang | Combo **4 pukulan**; pukulan ke-4 = finisher |
| **Maju** + pukul, musuh agak jauh | Pembuka **terjang** (gap closer) ke musuh, lalu combo lanjut dari pukulan 2 |
| **Mundur** + pukul | Pembuka **sapuan / pukulan sambil mundur**, lalu combo lanjut dari pukulan 2 |
| Netral, atau maju saat musuh sudah dekat | Combo biasa |
| **Kiri/kanan** + pukul | Untuk **memilih target** (soft target ala Arkham, [23](23-rencana-fase-1.md) Iterasi 4), bukan jurus |
| Pukulan berat di tengah combo | **Cabang finisher**: setelah pukulan 1 dan setelah pukulan 2 masing-masing punya pukulan berat sendiri; dari diam / langkah lain = pukulan berat biasa |

Arah dihitung **relatif ke musuh yang dituju**, bukan ke kamera, supaya "maju" selalu berarti mendekati musuh. Combo sengaja tidak lebih dari 4 pukulan: referensinya Arkham + Sekiro ringan, dan combo yang lebih panjang membuat pemain terkunci animasi sehingga telat menangkis. Variasi datang dari pembuka arah dan cabang finisher, bukan dari panjang combo.

## Mode Raksasa (Jayadwara)

| Sistem | Deskripsi |
|---|---|
| **Combat raksasa gesit, impact berat** | Gerak "ala Mebius" (keputusan developer 16 Okt 2026): serangan secepat mode manusia, berbalik badan cepat, lompatan tinggi. Rasa raksasa datang dari momen kena (hit-stop, guncangan kamera, debu, suara langkah, gedung runtuh pelan), bukan dari animasi yang diperlambat. Gerakan dan nama jurus tetap silat/Dwarapala, tidak meniru jurus Ultraman ([01](01-konsep-dan-pilar.md#wajib-dihindari)) |
| **Meter sinkronisasi** | Lihat di bawah |
| **Kelemahan boss** | Terbuka dari hasil investigasi mode manusia |
| **Destruction** | Gedung bisa hancur; kerusakan memengaruhi meter sinkronisasi |
| **Kamera skala** | Rig kamera khusus + elemen pembanding (kendaraan, warga, fog) agar terasa raksasa |

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
