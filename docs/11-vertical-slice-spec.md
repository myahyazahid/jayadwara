# 11 — Spesifikasi Vertical Slice: Episode 1 "Gerbang yang Retak"

> Vertical slice = satu episode lengkap dengan kualitas mendekati final. Dipakai untuk trailer, halaman Steam, demo, dan pitching.
> Dokumen ini adalah **batas scope**: yang tidak tercantum di bagian "Masuk Scope" **tidak dikerjakan** di fase ini.

## Tujuan

1. Membuktikan loop utama: **investigasi → konfrontasi manusia → transformasi → boss raksasa**.
2. Menetapkan standar kualitas visual realistis, combat, dan rasa skala.
3. Menghasilkan materi trailer dan demo Steam.

## Alur Episode (±20–30 menit)

| # | Bagian | Isi | Durasi |
|---|---|---|---|
| 1 | **Pembuka wayang** | Ki Sastro menarasikan legenda Dwarapala & Kala (wayang kulit, gambar 2D dengan parallax) | 1–2 mnt |
| 2 | **Briefing** | Kol. Bagas memberi misi lewat panggilan video; Sekar sebagai operator | 1–2 mnt |
| 3 | **Investigasi** | Aksa tiba di area penggalian Adikara dekat Candi Lawang Sapta. Scan 3 petunjuk dengan Netra (jejak energi, tulang kuno di lokasi pekerja meninggal, prasasti retak) | 5–8 mnt |
| 4 | **Konfrontasi manusia** | Kerangka-kerangka kecil (minion) menyerang; tutorial combat silat | 4–6 mnt |
| 5 | **Kebangkitan** | Jerangkong bangkit dan membesar; Aksa hampir mati; arca Dwarapala hancur dan menyatu dengannya (cutscene). Arca kedua terlihat diangkut truk Adikara di latar | 1–2 mnt |
| 6 | **Boss raksasa** | Jayadwara vs Jerangkong di area candi + blok kota kecil, dengan meter sinkronisasi | 6–8 mnt |
| 7 | **Debrief** | Laporan ke DWARA: kode "Entitas D" diumumkan; Aksa menyembunyikan identitasnya | 1 mnt |

## Masuk Scope

### Mode Manusia
- [ ] Gerak: jalan, lari, lompat, dodge
- [ ] Combat silat: pukulan ringan (combo 3), pukulan berat, tangkis + parry, dodge
- [ ] Hit reaction, stagger, finisher sederhana
- [ ] Scanner Netra: mode scan, 3 petunjuk yang bisa ditemukan, penanda di HUD
- [ ] 1 jenis minion (kerangka kecil) dengan AI dasar

### Transformasi
- [ ] Cutscene transformasi pertama (Sequencer)
- [ ] Ganti pawn manusia → raksasa, ganti input & kamera

### Mode Raksasa
- [ ] Combat yang sama dengan data skala raksasa (gesit "ala Mebius", impact besar, hit-stop, camera shake; [07](07-gameplay-sistem.md#mode-raksasa-jayadwara))
- [ ] 1 jurus spesial Jayadwara
- [ ] **Meter sinkronisasi**: turun saat gedung hancur / NPC terkena; habis = gagal
- [ ] 6–10 gedung yang bisa hancur (Chaos Geometry Collection, pre-fractured)
- [ ] Sejumlah kecil NPC warga yang bisa diselamatkan (tanpa Mass AI)

### Boss: Jerangkong (2 fase)
- [ ] **Fase 1**: serangan tulang jarak dekat; ketika dihancurkan, tubuhnya menyusun ulang
- [ ] **Fase 2**: tengkorak (titik lemah) terbuka — hanya bisa dikalahkan dengan menghancurkan tengkorak
- [ ] Kelemahan yang terbuka dari investigasi: petunjuk prasasti → tengkorak ditandai di HUD

### Narasi & Presentasi
- [ ] Pembuka wayang (2D)
- [ ] Stinger arca kedua + Gunadi Adikara: **gambar diam** (keputusan S4 [17](17-skenario-arc-1.md#keputusan-untuk-developer-ep-1), 15 Okt 2026)
- [ ] Briefing & debrief (dialog teks + potret karakter)
- [ ] HUD: health, stamina, meter sinkronisasi, penanda petunjuk
- [ ] Menu utama sederhana, pause, pengaturan grafis dasar
- [ ] Musik: 1 tema eksplorasi, 1 tema combat manusia, 1 tema boss (gamelan + orkestra/rock)
- [ ] SFX inti: pukulan, langkah raksasa, gedung runtuh

### Aset
| Aset | Sumber yang Disarankan |
|---|---|
| Aksa (manusia) | **Dibuat sendiri** (Blender, bersama Claude). Sementara memakai **MetaHuman** sebagai placeholder visual, lihat [12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa) (keputusan 12 Okt 2026) |
| Jayadwara | Blender, dibuat bersama Claude ([rencana](13-rencana-model-jayadwara.md)); commission opsional untuk polish final (aset paling penting secara visual) |
| Jerangkong + minion kerangka | Commission / Fab + modifikasi |
| Candi Lawang Sapta + area penggalian | Kit modular realistis (Fab / Megascans) + kustom |
| Blok kota kecil | Kit kota realistis (Fab / Megascans) |
| Animasi | Mixamo (prototype) → video-mocap / commission untuk silat final |

## Di Luar Scope (jangan dikerjakan di fase ini)

- Markas DWARA sebagai hub yang bisa dijelajahi
- Sistem upgrade & skill tree
- Dialog bercabang & pilihan
- Save/load lengkap (cukup checkpoint)
- Voice acting final (boleh placeholder / tanpa suara)
- Kerumunan Mass AI
- Distrik Arunapura lain & peta regional
- Pertarungan udara, kendaraan
- Lokalisasi selain ID + EN

## Target Teknis

| Item | Target |
|---|---|
| Resolusi / FPS | 1080p, 60 FPS di PC kelas menengah (spesifikasi pasti ditetapkan saat prototype) |
| Waktu loading | Di bawah ±20 detik |
| Stabilitas | Tidak ada crash dalam satu playthrough penuh |

## Kriteria Selesai

- [ ] Bisa dimainkan dari menu utama sampai debrief tanpa bantuan developer.
- [ ] Minimal **5 playtester** menyelesaikan episode; mayoritas menilai combat dan rasa skala "seru".
- [ ] Memenuhi target teknis di atas.
- [ ] Ada footage yang cukup untuk trailer 60–90 detik.
