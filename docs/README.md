# JAYADWARA: Guardian of the Seven Gates

> Game Design Docs — **draft v0.1** (10 Oktober 2026)

Action-adventure **linear semi-open-world** berbasis **Unreal Engine 5**, bergenre *kyodai hero* (manusia yang bisa berubah menjadi raksasa untuk melawan monster). Terinspirasi struktur serial seperti Ultraman Mebius, tapi dengan dunia, karakter, dan monster orisinal yang berakar pada **mitologi Nusantara**.

**Logline**
Aksa Jaya Mangkubumi, agen baru sebuah lembaga rahasia penanganan anomali, menyatu dengan roh Dwarapala — penjaga gerbang kuno yang dulu pernah dianggap monster. Ketika segel Tujuh Gerbang Nusantara retak dan makhluk-makhluk mitologi bangkit sebagai raksasa, Aksa harus melindungi negeri sambil menjaga agar kegelapan Kala di dalam dirinya tidak ikut terbangun.

---

## Daftar Dokumen

| # | Dokumen | Isi |
|---|---|---|
| 01 | [Konsep & Pilar](01-konsep-dan-pilar.md) | Konsep inti, batasan IP, tiga pilar desain, judul |
| 02 | [Setting Dunia](02-setting-dunia.md) | Kota Arunapura, peta regional, lore Sapta Dwara |
| 03 | [Karakter](03-karakter.md) | Aksa, organisasi DWARA, anggota pemberi misi, antagonis |
| 04 | [Skenario Cerita](04-skenario-cerita.md) | Prolog, sinopsis 5 arc, ending |
| 05 | [Daftar Episode & Boss](05-daftar-episode-boss.md) | Episode 1–50 lengkap dengan boss, lokasi, mekanik |
| 06 | [Referensi Mitologi](06-referensi-mitologi.md) | Katalog makhluk mitologi per daerah & panduan sensitivitas budaya |
| 07 | [Gameplay & Sistem](07-gameplay-sistem.md) | Mode manusia, mode raksasa, meter sinkronisasi, struktur episode |
| 08 | [Requirement & Produksi](08-requirement-produksi.md) | Art, audio, teknis UE5, legal, scope, milestone, keputusan terbuka |

### Dokumen Produksi

| # | Dokumen | Isi |
|---|---|---|
| 09 | [Product Brief](09-product-brief.md) | Pengganti PRD: target pemain, pembanding, USP, model bisnis, risiko |
| 10 | [Roadmap](10-roadmap.md) | Fase 0–5 dari setup sampai Early Access Season 1 |
| 11 | [Spesifikasi Vertical Slice](11-vertical-slice-spec.md) | Batas scope Episode 1 dan kriteria selesai |
| 12 | [Technical Design (TDD)](12-technical-design.md) | Arsitektur C++, plugin, struktur folder, konvensi, Git LFS |
| 13 | [Rencana Model Jayadwara](13-rencana-model-jayadwara.md) | Pipeline & iterasi membuat model raksasa di Blender 5.2 sampai siap dipakai di UE |
| 14 | [Model Sheet Jayadwara](14-model-sheet-jayadwara.md) | Design lock: proporsi, palet, part list, keputusan desain K1–K8 (hasil Iterasi 0) |
| 15 | [Spesifikasi Material Jayadwara](15-spesifikasi-material-jayadwara.md) | Slot, tekstur, parameter master material UE, alur hand-paint (hasil Iterasi 4) |
| 16 | [Panduan Arc 1](16-panduan-arc-1.md) | **Usulan.** Arahan desain Ep 1–10: aturan per episode, mekanik baru, benang merah, kartu episode |
| 17 | [Skenario Arc 1](17-skenario-arc-1.md) | **Usulan.** Skenario adegan per adegan Ep 1 (lengkap); Ep 2–10 menyusul |
| 18 | [Kebutuhan Episode 1](18-kebutuhan-episode-1.md) | **Usulan.** Daftar kerja Ep 1: sistem C++, karakter & animasi, level, VFX, audio, UI, data, urutan F0–F2 |
| 19 | [Rencana Model Aksa](19-rencana-model-aksa.md) | **Usulan.** Iterasi 0–7 membuat model Aksa di Blender (skeleton Mannequin, basis MPFB2) sampai menggantikan MetaHuman di UE |
| 20 | [Rencana Model Jerangkong](20-rencana-model-jerangkong.md) | **v0.2, terpasang di UE.** Boss Ep 1 + minion kerangka dari model Tripo developer (jalur B): satu model, potongan kaku untuk mekanik rontok/susun ulang |
| 21 | [Model Sheet Aksa](21-model-sheet-aksa.md) | **Draft.** Design lock Aksa: proporsi terukur (H = 1,75 m), palet, part list, keputusan desain D1–D10 (hasil Iterasi 0) |
| 22 | [Spesifikasi Material Aksa](22-spesifikasi-material-aksa.md) | **Draft.** Slot, tekstur dasar (BC/N/ORM/SSS/Mask), master & instance UE, pipeline UV (hasil Iterasi 5) |
| 23 | [Rencana Fase 1](23-rencana-fase-1.md) | **Usulan.** Prototype greybox: 9 iterasi (GAS → combat → minion → raksasa → gedung & meter → boss → playtest), gate, angka awal combat, pertanyaan Q1–Q14 |
| 24 | [Model Sheet Jerangkong](24-model-sheet-jerangkong.md) | **Dipakai.** Design lock Jerangkong: proporsi terukur (H = 2,2 m), postur bungkuk sedang, palet, potongan, keputusan S1–S12 (hasil Iterasi 0) |
| 25 | [Rencana Redesign Jayadwara](25-rencana-redesign-jayadwara.md) | **Persiapan.** Jayadwara2 dari model Tripo developer (lebih realistis): intake → spike → pemisahan → rig → tekstur → LOD → UE, keputusan R1–R10; model lama tetap utuh & bisa dikembalikan |
| 26 | [Rencana Jubah Jayadwara](26-rencana-jubah-jayadwara.md) | **J1 disetujui; J2 selesai (13 Okt 2026), menunggu developer**: jubah cap02 menempel tubuh sampai kerah, Mask zona + LOD0–2, simulasi rantai (J3 sebagian), tombol Y lepas (J4 sebagian). J5 belum. Jubah upacara (K9 docs/14): mesh terpisah ikut pose Jayadwara2, Chaos Cloth, pakai/lepas otomatis; basis Tripo `cap02`; J0–J3 ditarik sekarang sebagai jalur art paralel, J4–J5 tetap F2 |
| 27 | [Rencana Model Tuyul](27-rencana-model-tuyul.md) | **Usulan (backlog Fase 4).** Boss Ep 2 + kawanan: alur developer (konsep + GLB Tripo) → Hermes (K0–K7, [`Hermes/tuyul_hermes.md`](../Hermes/tuyul_hermes.md)) → Claude Code (review, perbaikan, integrasi, polish). Tiga ukuran ter-bake (1 m / 27 m / 45 m), keputusan T1–T9 |
| 28 | [Struktur Level per Episode](28-struktur-level-episode.md) | **Usulan.** Satu map per episode ala Resident Evil 4 (zona kedatangan → investigasi → konfrontasi → transformasi → arena raksasa), kit distrik Level Instance, rancangan map Ep 1–10 + hub, keputusan L1–L6. Konsep satu map Arunapura diarsipkan di sini |
| 29 | [Struktur Level Arc 2](29-struktur-level-arc-2.md) | **Usulan (backlog Season 2).** Map Ep 11–20 ala RE4 di 5 gerbang regional: kit inti + paket identitas, aturan budaya (rumah adat/ibadah tidak hancur), pos lapangan DWARA, sistem per episode, keputusan M1–M7 |


---

## Ringkasan Keputusan yang Sudah Final

| Aspek | Keputusan |
|---|---|
| Judul | **JAYADWARA: Guardian of the Seven Gates** |
| Engine | Unreal Engine **5.6.1**, C++ + Blueprint |
| Platform | PC (Steam) |
| Gaya visual | **Realistis** (game-realistis, bukan sinematik): proporsi dan anatomi nyata, material PBR fotorealistis, Lumen + Nanite (diputuskan developer 14 Okt 2026, menggantikan stylized semi-realistis 12 Okt). **Alasan:** stylized dipilih karena model yang dibangun Claude secara prosedural di Blender mentok di level itu; sekarang **geometri & tekstur dasar digenerate Tripo** (realismenya datang dari Tripo), Claude mengerjakan pembersihan, pemisahan, rig, dan pipeline ke UE. Risiko lain (volume 50 monster, animasi, performa) tetap ada; mitigasinya di [09](09-product-brief.md#risiko-utama). Jayadwara2 & Jerangkong sudah memakai jalur ini |
| Tim | Solo + Claude, sambilan ±10–15 jam/minggu |
| Struktur | Linear semi-open-world, **50 episode** dalam **5 arc** |
| Karakter utama | **Aksa Jaya Mangkubumi** ("Aksa"), codename **Lawang** |
| Wujud raksasa | **Jayadwara** (roh Dwarapala). **Model aktif sejak 13 Okt 2026: Jayadwara2** (basis Tripo AI developer, dirapikan Claude; [25](25-rencana-redesign-jayadwara.md)). Model lama ([13](13-rencana-model-jayadwara.md)) disimpan sebagai cadangan |
| Organisasi | **DWARA** — Divisi Warisan dan Riset Anomali |
| Kota utama | **Arunapura** (kota fiksi di Jawa) |
| Final boss | **Batara Kala** |
| Pilar desain | Mitologi Nusantara · penjaga yang ambigu · meter sinkronisasi |

## Status

Draft konsep. Lihat bagian **Keputusan Terbuka** di [08-requirement-produksi.md](08-requirement-produksi.md#keputusan-terbuka) untuk hal yang belum ditentukan.

*Semua nama karakter pendukung masih bisa diubah.*
