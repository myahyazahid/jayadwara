---
name: jd-mulai-tugas
description: Wajib dipakai di AWAL setiap tugas di repo JAYADWARA (game Unreal Engine 5.6, model 3D Blender), apa pun tugasnya — membuat/memperbaiki model, skrip, aset UE, C++. Menyiapkan worktree & branch hermes/<topik>, membaca aturan dan riwayat, menulis rencana berangka sebelum mengerjakan apa pun.
---

# Mulai tugas JAYADWARA

Jangan menyentuh file apa pun sebelum 5 langkah ini selesai.

## 1. Pastikan berada di worktree Hermes dan branch yang benar
```
cd C:\repository\unreal_engine\jayadwara_hermes
git status -sb
```
- Baris pertama harus `## hermes/<topik>`. Kalau `development`/`main`/lainnya: **berhenti**.
- Belum ada worktree: lihat `AGENTS.md` §1a.
- Tugas baru: `git fetch origin development` lalu `git switch -c hermes/<topik-baru> origin/development` (tugas lama sudah di-push).
- Ambil aturan terbaru: `git fetch origin development` lalu `git merge origin/development`.

## 2. Baca aturan (urutan menang: atas > bawah)
1. `AGENTS.md` (seluruhnya, terutama §0 cara kerja)
2. Instruksi khusus `Hermes/<model>_hermes.md` kalau ada (mis. `aksa_hermes.md`)
3. `Hermes/panduan_model_3d.md` (tugas model) dan `Hermes/panduan_kerja_claude.md` (semua tugas, wajib untuk perbaikan)

## 3. Cari riwayat masalah serupa
Hampir semua masalah pernah terjadi dan sudah ada penyebab + perbaikannya:
```
findstr /s /i /n "<kata kunci>" docs\*.md
```
Kata kunci contoh: `robek`, `bolong`, `ketiak`, `melar`, `tembus`, `meleh`, `keropos`, `retarget`, `LOD`, `tekstur`. Tulis di laporan: dokumen + bagian yang relevan (mis. "docs/25 R8 ketiak bolong").

## 4. Tulis rencana di laporan SEBELUM mengerjakan
File `Hermes/Laporan/YYYY-MM-DD-<topik>.md` (template `AGENTS.md` §8). Rencana berisi:
- Tugas persis dari developer (salin kalimatnya). Kalau ada yang tidak jelas (bagian mana, pose apa, kiri/kanan), **tanya dulu**.
- Langkah-langkah, satu langkah = satu file baru (`_v05` → `_v06`).
- **Kriteria lulus berangka** per langkah (mis. "regangan tangkis ≤ pembanding + 5 poin", "validator semua PASS", "VONIS LULUS").
- Pembanding sehat yang dipakai (model lama / versi sebelum rusak).
- Alat ukur yang dipakai (skill `jd-audit-model`, `jd-perbaiki-model`).

## 5. Pilih skill berikutnya
| Tugas | Skill |
|---|---|
| Ada yang rusak / developer mengeluh | `jd-perbaiki-model` |
| Mengecek model hasil kerja | `jd-audit-model` |
| Menjalankan/menulis skrip Blender | `jd-blender-skrip` |
| Apa pun di Unreal Editor | `jd-unreal-sandbox` |
| Mau commit/push/lapor selesai | `jd-selesai-tugas` |

## Larangan dasar (detail di AGENTS.md)
Menulis di luar `Content/Hermes/`, `Source/Jayadwara/Hermes/`, `Hermes/`; menimpa file lama; push ke branch selain `hermes/*`; merge; mengubah file instruksi Claude; mengklaim sesuatu tanpa angka/gambar.
