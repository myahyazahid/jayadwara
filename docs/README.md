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

---

## Ringkasan Keputusan yang Sudah Final

| Aspek | Keputusan |
|---|---|
| Judul | **JAYADWARA: Guardian of the Seven Gates** |
| Engine | Unreal Engine **5.6.1**, C++ + Blueprint |
| Platform | PC (Steam) |
| Gaya visual | Stylized |
| Tim | Solo + Claude, sambilan ±10–15 jam/minggu |
| Struktur | Linear semi-open-world, **50 episode** dalam **5 arc** |
| Karakter utama | **Aksa Jaya Mangkubumi** ("Aksa"), codename **Lawang** |
| Wujud raksasa | **Jayadwara** (roh Dwarapala) |
| Organisasi | **DWARA** — Divisi Warisan dan Riset Anomali |
| Kota utama | **Arunapura** (kota fiksi di Jawa) |
| Final boss | **Batara Kala** |
| Pilar desain | Mitologi Nusantara · penjaga yang ambigu · meter sinkronisasi |

## Status

Draft konsep. Lihat bagian **Keputusan Terbuka** di [08-requirement-produksi.md](08-requirement-produksi.md#keputusan-terbuka) untuk hal yang belum ditentukan.

*Semua nama karakter pendukung masih bisa diubah.*
