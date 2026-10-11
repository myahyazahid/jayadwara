# 08 — Requirement & Produksi

## Art Direction

- **Gaya visual**: *keputusan terbuka* — realistis (Lumen/Nanite) atau stylized (lebih ringan untuk tim kecil).
- **Desain Jayadwara**: hero bergaya **tokusatsu**, berbasis arca Dwarapala; motif ukiran, batik, wayang, candi; helm bermotif Kala-Bhoma.
  - **Concept final**: [`jayadwara_final.webp`](concept-art/jayadwara_final.webp) (turnaround 4 sisi, detail kepala, detail armor, siluet, palet). Gambar AI = brief untuk commission/modeling, bukan aset final. Varian lain di `concept-art/` (v01–v06 dan dua sheet "Jayadwara_ Nusantara ...") hanya arsip eksplorasi, bukan final.
  - **Palet**: merah (utama), hitam, emas, putih (faceplate), merah marun gelap. Tidak ada armor silver.
  - **Helm**: merah bersudut, dua tanduk emas besar menyapu ke atas, ornamen emas berukir di dahi, faceplate putih dengan mata menyala.
  - **Armor**: pelat merah bersudut dengan trim emas berukir — ornamen dada bermotif surya dengan permata emas di tengah, bahu berukir tradisional, sabuk + selendang panjang bermotif batik, pelindung kaki ramping.
  - **Badan**: ramping-atletis (aman di-retarget ke skeleton Mannequin), undersuit hitam, pose khas kuda-kuda silat.
  - **Inspirasi**: relief candi, gunungan wayang, surya, gunung.
  - **Batas IP (hindari kemiripan Ultraman)**: tidak ada lampu/timer di dada, tidak ada kristal di dahi, tidak ada bilah kembar di atas kepala, tidak ada mata lensa besar, tidak ada kombinasi badan merah-silver, permata dada tidak berkedip/berfungsi sebagai timer, tidak ada emblem garuda (Bima Satria Garuda). Faceplate putih = titik paling dekat ke Ultra — saat commission, minta bentuk mulut/pipi dibedakan.
- **Desain monster**: siluet jelas dan kelemahan yang terlihat secara visual.
- **Rasa skala**: kamera, fog, kendaraan, dan pejalan kaki sebagai pembanding ukuran.
- **Cutscene pembuka**: gaya wayang kulit (narasi Ki Sastro).

## Audio

- Musik: gamelan + orkestra / rock tokusatsu.
- SFX berbobot berlapis: langkah raksasa, gedung runtuh, gema kota.
- Voice acting: bahasa Indonesia + subtitle Inggris.

---

## Teknis Unreal Engine 5

| Kebutuhan | Fitur UE |
|---|---|
| Hub semi-open-world | **World Partition** + Level Streaming |
| Gedung hancur | **Chaos Destruction** (Geometry Collection) — rencanakan dari awal, berat |
| Skill, cooldown, meter | **Gameplay Ability System (GAS)** — satu sistem untuk dua mode |
| Animasi combat | Motion Matching (locomotion) + Montage (serangan) |
| Kerumunan warga | **Mass Entity / Mass AI** |
| VFX jurus & aura | Niagara |
| Karakter manusia | MetaHuman (opsional) |
| Input | Enhanced Input — dua mapping context: manusia & raksasa |
| Kamera | Dua rig kamera + transisi sinematik saat transformasi |

### Version Control
- Project UE wajib memakai **Git LFS** (`.uasset`, `.umap` adalah file binary).
- Alternatif: **Perforce** kalau tim membesar.

---

## Legal & Budaya

- Hindari semua elemen khas IP Tsuburaya (lihat [01-konsep-dan-pilar.md](01-konsep-dan-pilar.md#wajib-dihindari)).
- Cek judul & nama karakter terhadap merek dagang: Steam, **PDKI**, **WIPO Global Brand Database**; domain & username media sosial.
- Aset Fab / Marketplace: pastikan lisensi mengizinkan rilis komersial.
- Ikuti [panduan sensitivitas budaya](06-referensi-mitologi.md#panduan-sensitivitas-budaya); libatkan budayawan untuk review.

---

## Scope & Strategi Produksi

- **50 episode** = sangat besar untuk UE. Strategi:
  - Durasi per episode **20–40 menit**.
  - **Pakai ulang rig/skeleton** (lihat [pengelompokan rig](05-daftar-episode-boss.md#pengelompokan-rig--skeleton-hemat-produksi)).
  - Peta regional kecil dari **modular kit**.
  - **Rilis per season**: misalnya Season 1 = Arc 1 (Ep 1–10) sebagai rilis pertama / Early Access, arc berikutnya menyusul.

## Milestone

| # | Milestone | Isi |
|---|---|---|
| 1 | **Prototype (greybox)** | Karakter manusia bergerak & memukul, transformasi, raksasa bertarung di satu arena |
| 2 | **Vertical slice** | Satu episode lengkap (investigasi → transformasi → boss) dengan kualitas mendekati final. Dipakai untuk pitching / publisher / crowdfunding |
| 3 | **Produksi penuh** | Episode-episode berikutnya per arc |

---

## Keputusan yang Sudah Diambil

| Pertanyaan | Keputusan |
|---|---|
| Ukuran tim | **Solo** + Claude |
| Kapasitas kerja | Sambilan, **±10–15 jam/minggu** |
| Gaya visual | **Stylized** |
| Platform | **PC (Steam)** |
| Engine & bahasa | **UE 5.6.1, C++ + Blueprint** (Claude tidak bisa mengedit `.uasset`) |
| Isi rilis pertama | **Season 1 = Arc 1 (Ep 1–10)** sebagai Early Access (lihat [roadmap](10-roadmap.md)) |
| Sumber aset 3D Jayadwara | **Modeling sendiri di Blender 5.2 bersama Claude** (via Blender MCP); commission hanya opsional untuk polish. Model dibuat **sebelum** UE terpasang (lihat [rencana model](13-rencana-model-jayadwara.md)) |

## Keputusan Terbuka

| # | Pertanyaan | Dampak |
|---|---|---|
| 1 | **Syarat transformasi** — bebas / momen tertentu / setelah syarat? | Desain loop episode |
| 2 | **Sumber aset 3D selain Jayadwara** (Aksa, monster, lingkungan) — modeling sendiri (Blender), commission, Fab, atau campuran? | Bottleneck terbesar, budget |
| 3 | **Harga & model season berikutnya** — update gratis atau DLC? | Model bisnis |
| 4 | **Durasi target total game** | Ukuran tiap episode |
| 5 | **Pengalaman developer** dengan Unreal / C++ / Blender | Lama Fase 0 dan kebutuhan belajar |
