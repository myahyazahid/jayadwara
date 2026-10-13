# JAYADWARA: Guardian of the Seven Gates

Game action-adventure kyodai hero (ala Ultraman, tanpa IP Tsuburaya) berbasis mitologi Nusantara. Unreal Engine **5.6.1**, C++ + Blueprint, PC (Steam), stylized. Solo dev + Claude, sambilan ±10–15 jam/minggu.

## Sumber kebenaran desain
Semua keputusan ada di `docs/` — baca `docs/README.md` dulu sebelum mengusulkan perubahan desain.
- Cerita & dunia: `docs/01`–`docs/06`
- Gameplay: `docs/07`
- Produksi: `docs/09` (product brief), `docs/10` (roadmap), `docs/11` (vertical slice Ep 1)
- Teknis: `docs/12-technical-design.md` (arsitektur, prefix `JD`, struktur folder, penamaan aset)

## Aturan kerja
- Logic inti di **C++** (dikerjakan Claude); Blueprint/editor untuk merangkai, tuning, dan visual (dikerjakan developer). Claude tidak bisa membaca/mengedit `.uasset` / `.umap`.
- Kerjakan hanya yang masuk scope fase aktif di `docs/10-roadmap.md` dan `docs/11-vertical-slice-spec.md`; ide di luar scope dicatat ke backlog.
- Kalau keputusan desain berubah, perbarui dokumen di `docs/` yang relevan.
- Git + Git LFS; jangan commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`.
- **Claude tidak push langsung ke `development` atau `main`.** Kerjakan di branch sendiri `claude/<topik>` (dibuat dari `development`), push branch itu, lalu buat PR ke `development`. Developer yang merge.
- Commit & PR atas nama developer: author commit `Muhammad Yahya Zahid <myahyazahid11@gmail.com>`. Pesan commit dan deskripsi PR **hanya isi perubahan**, tanpa baris atribusi (`Co-Authored-By`, `Generated with/by Claude Code`, link sesi).
- Komunikasi dengan developer: bahasa Indonesia santai.
