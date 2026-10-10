# 08 — Requirement & Produksi

## Art Direction

- **Gaya visual**: *keputusan terbuka* — realistis (Lumen/Nanite) atau stylized (lebih ringan untuk tim kecil).
- **Desain Jayadwara**: berbasis arca Dwarapala; motif ukiran, batik, wayang, candi; topeng/helm bermotif Kala-Bhoma. **Tidak** merah-perak, **tidak** ada lampu timer di dada.
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

## Keputusan Terbuka

| # | Pertanyaan | Dampak |
|---|---|---|
| 1 | **Ukuran tim** — solo atau ada anggota lain? | Scope, jadwal, pembagian peran |
| 2 | **Gaya visual** — realistis atau stylized? | Pipeline aset, performa |
| 3 | **Platform target** — PC saja atau juga konsol? | Batas destruction & Lumen, spesifikasi minimum |
| 4 | **Blueprint saja, atau C++ + Blueprint?** | GAS butuh C++ minimal untuk setup |
| 5 | **Isi rilis pertama** — Arc 1 saja, atau lebih? | Target milestone |
| 6 | **Syarat transformasi** — bebas / momen tertentu / setelah syarat? | Desain loop episode |
| 7 | **Durasi target total game** | Ukuran tiap episode |
