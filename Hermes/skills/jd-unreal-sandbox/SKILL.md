---
name: jd-unreal-sandbox
description: Dipakai untuk apa pun di Unreal Editor proyek JAYADWARA (UE 5.6.1) — impor mesh/tekstur, membuat material, skeleton, level uji, menjalankan Python editor, screenshot. Semua hanya di /Game/Hermes/<Topik>/ lewat editor worktree Hermes; tidak pernah menyentuh SK_Mannequin atau aset /Game/Jayadwara/.
---

# Unreal Editor (sandbox)

## Editor yang benar
- Buka `C:\repository\unreal_engine\jayadwara_hermes\Jayadwara.uproject` (editor Hermes, terpisah dari editor developer).
- Jalankan skrip: `python Tools/ue_remote.py Hermes/Tools/<skrip>.py` **dari folder worktree**. Skrip ini hanya terhubung ke editor dari folder yang sama. Jangan pakai `--any-editor`.
- "Editor tidak ditemukan" → buka editor worktree dulu. Editor sedang Play (PIE) → hentikan dulu (skrip tidak melihat aset saat PIE).

## Aturan aset
- Setiap skrip diawali `DEST = "/Game/Hermes/<Topik>"`; semua path tujuan dibentuk dari `DEST`.
- Aset lama: hanya dibaca, atau **diduplikat** ke `DEST` lalu salinannya yang diubah. Tidak pernah Move/Rename/Delete aset lama, tidak pernah Fix Up Redirectors di luar sandbox.
- Simpan per aset: `unreal.EditorAssetLibrary.save_loaded_asset(aset)` hanya untuk aset di `/Game/Hermes/`. **Tidak pernah Save All.** Dialog "Save content" berisi aset luar sandbox → **Don't Save**.
- Tidak mengubah Project Settings, `Config/*.ini`, `.uproject`, plugin, World Settings level lama.
- Skrip proyek `Tools/ue_setup_*`, `ue_import_*`, `ue_test_*`, `ue_capture_*`, `ue_probe_*` **tidak dijalankan** (menulis ke level/aset proyek). Butuh logikanya: salin ke `Hermes/Tools/`, ganti tujuan ke `DEST`.

## Skeleton (jangan ulangi insiden 13–14 Okt, docs/25 R7)
- **Tidak pernah** mengimpor mesh ke `/Game/Characters/Mannequins/Meshes/SK_Mannequin`.
- Manusia: muat dulu `SKM_Manny_Simple` dan `SK_Aksa` (jangan disimpan), lalu `duplicate_asset(SK_Mannequin → DEST/Rig/SKEL_<Nama>)`, cetak jumlah tulang salinan (≥ 161), tambah `SK_Mannequin` ke **Compatible Skeletons** salinan, simpan hanya salinan. Impor mesh ke salinan itu.
- Monster dengan skeleton sendiri: skeleton dibuat saat impor di `DEST/Rig/`.
- Compatible Skeletons tidak membuat animasi jalan → **berhenti dan laporkan**, jangan mencari jalan pintas.

## Level uji & bukti
- Level: duplikat level proyek (mis. `Test_Combat`) → `DEST/Maps/Test_Hermes_<Topik>`. Model baru berdampingan dengan pembanding, animasi sama.
- Screenshot: `Tools/ue_check_aksa.py` boleh dijalankan **hanya** saat level Hermes terbuka (ia menaruh actor sementara di level aktif). Capture blur → `r.Streaming.FullyLoadUsedTextures 1`.
- Bukti tidak merusak, setelah setiap sesi editor:
  ```
  git status --porcelain
  python -I Tools/hermes_cek_sandbox.py
  ```
  Ada `.uasset/.umap` di luar `Content/Hermes/` → jangan disimpan/di-commit, `git restore` file itu, tulis di laporan.

## Urutan impor ulang (kalau mengikuti pola Jayadwara2)
Impor mesh → setup (material, PA, retarget) → komponen tambahan → combo. Langkah yang dilewati = hasil tampak rusak padahal file Blender benar (resep F8).
