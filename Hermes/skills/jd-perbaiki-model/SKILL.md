---
name: jd-perbaiki-model
description: Dipakai saat developer melaporkan model 3D rusak di JAYADWARA — "lengan robek", "ketiak bolong", "paha keropos", "wajah meleh", "kain tembus", "bolong saat pukul", "melar saat jongkok" — atau saat audit/banding GAGAL. Alur diagnosa_mesh.py → perbaiki_mesh.py (resep F1–F8) → diagnosa ulang --sebelum → regresi. Jangan pernah langsung mengedit mesh.
---

# Memperbaiki model yang rusak

Panduan lengkap + katalog resep + contoh teruji: `Hermes/panduan_kerja_claude.md` §3–§7. Skill ini ringkasannya. **Jangan langsung mengedit**: model yang langsung mengedit hampir selalu gagal, karena "robek" punya 4 penyebab berbeda dengan resep berbeda.

## 0. Keluhan persis
Tulis: bagian (kiri/kanan), pose/animasi, sudut lihat, terlihat di Blender atau hanya di UE. Tidak jelas → **tanya developer**.

## 1. Dua FBX
- Model yang dikeluhkan: export file kerja terbaru (skrip export proyek, kontrak FBX) → `Hermes/Art/<topik>/Export/SK_<Nama>_vNN.fbx`
- Pembanding sehat: versi sebelum rusak > model lama yang digantikan (`Art/Export/SK_Aksa.fbx` untuk manusia) > model sejenis yang disetujui. LOD sama dengan LOD sama.
- File 130 byte / "ASCII FBX not supported" = pointer Git LFS → `git lfs pull --include="<file>"`.

## 2. Tulang wilayah
Lengan atas/bahu/ketiak `upperarm_r,clavicle_r` · siku/lengan bawah `lowerarm_r,hand_r` · leher/wajah `neck_01,neck_02,head` · pinggul `pelvis,thigh_l,thigh_r` · paha/lutut `thigh_l,calf_l` · kaki `calf_l,foot_l`. Kiri: `_l`.

## 3. Diagnosa (pembanding dulu, lalu model)
```
blender --background --factory-startup --python Art/Scripts/diagnosa_mesh.py -- <FBX sehat> --tulang <t> --out Hermes/Art/<topik>/Diagnosa/sehat_<wilayah> --tanpa-render
blender --background --factory-startup --python Art/Scripts/diagnosa_mesh.py -- <FBX model> --tulang <t> --out Hermes/Art/<topik>/Diagnosa/vNN_<wilayah> --pembanding-hasil Hermes/Art/<topik>/Diagnosa/sehat_<wilayah>
```
Raksasa/monster: tambah `--height <m>` (dan `--profil <json>`), nilai sama dengan audit.
- Baca `diagnosa.md`: dugaan #1 dikerjakan dulu. Keterangan "akibatnya" = hilang sendiri setelah penyebab diperbaiki.
- Buka `diagnosa_sheet.png`. Warna (merah lubang, magenta bobot jauh, kuning jahitan, oranye bobot tajam, biru tembus) **harus ada di tempat keluhan**. Kalau tidak: tulang/wilayah salah, kembali ke langkah 2.
- "Tidak ada temuan": coba `--pose <pose keluhan>`; masalah hanya di UE → F8; tulis kesimpulanmu.

## 4. Satu resep, file baru
```
blender --background <file kerja vNN.blend> --python Art/Scripts/perbaiki_mesh.py -- <F#> --objek <mesh> --tulang <t> --out <file vNN+1_F#.blend> [opsi]
```
| Dugaan | Resep | Opsi wajib/umum |
|---|---|---|
| JAHITAN TERBELAH | `F2` | `--gabung` (model potongan kaku seperti Jerangkong: JANGAN, itu desain) |
| BOBOT KE TULANG SALAH | `F3` | `--sumber <FBX sehat>` (terbaik) atau `--mode jarak`; **naikkan `--radius` (0.12 → 0.2 → 0.3) sampai PERINGATAN "di luar wilayah" hilang** |
| LUBANG / LUBANG BARU | `F1` lalu `F4` | `--pusat "x,y,z;..."` HANYA loop yang kolom "ada di model sehat?" = **tidak** dan merah di tempat keluhan. Jangan menutup kerah/lengan baju/kantong |
| BOBOT TAJAM | `F4` | `--iterasi 3`, `--kunci <tulang bagian kaku>` |
| NORMAL TERBALIK | `F7` | periksa gambar sesudahnya |
| TEMBUS / MELAR / hanya di UE | F6 / F5 / F8 | ikuti tabel `panduan_kerja_claude.md` §4 (butuh skrip khusus; tulis rencana dulu) |

Baca output skrip: `sebelum` / `sesudah` / **`PERINGATAN` = belum selesai**.

## 5. Ukur ulang
Export versi baru → diagnosa yang sama + `--sebelum <dir diagnosa versi lama>`. Lulus hanya kalau:
- dugaan yang diperbaiki hilang;
- regangan p99 tiap pose ≤ pembanding + 5 poin (bandingkan dengan `diagnosa.json` pembanding);
- tidak ada MEMBURUK besar;
- warna penanda hilang dari tempat keluhan di gambar.
**"Angka penyebab turun" saja tidak cukup** (contoh teruji: bobot jauh 135 → 1 tapi regangan jongkok naik 504 → 651 %, penyebabnya radius terlalu kecil).
Masih ada dugaan → langkah 4 lagi. Gagal 3× pada dugaan yang sama → berhenti, laporkan angka tiap percobaan.

## 6. Regresi, lalu UE
Skill `jd-audit-model` (seluruh badan, VONIS LULUS) → LOD dibuat ulang + validator → skill `jd-unreal-sandbox` (animasi keluhan + screenshot dari sudut keluhan dan dari bawah).

## Larangan
Menghapus muka untuk menyembunyikan; mengubah tulang; menghaluskan bobot seluruh badan; memperbaiki di opsi impor UE; >1 dugaan per langkah; mengubah radius/pembanding/profil **diagnosa** supaya dugaan hilang; menyatakan selesai tanpa `--sebelum` + regresi + melihat gambar.
