# AGENTS.md — Aturan untuk Hermes (dan agent lain selain Claude)

Repo ini adalah game **JAYADWARA: Guardian of the Seven Gates** (Unreal Engine **5.6.1**, C++ + Blueprint). Pemeliharanya satu developer + Claude. Kamu (Hermes) di sini sebagai **pembantu eksperimen**: hasil kerjamu **selalu terisolasi**. Developer yang memutuskan apakah dipakai, lalu Claude yang me-review dan memindahkannya ke proyek utama.

> **Prinsip utama: jangan pernah mengubah, memindahkan, mengganti nama, atau menghapus apa pun yang sudah ada. Buat yang baru di area sandbox kamu sendiri.**

Kalau ragu sebuah tindakan melanggar aturan ini, **jangan lakukan**. Tulis di laporan sebagai usulan.

---

## 1. Git: selalu di branch sendiri

1. Mulai dari `development` terbaru:
   ```
   git fetch origin development
   git checkout -b hermes/<topik-singkat> origin/development
   ```
   Contoh nama: `hermes/test-kamera-raksasa`, `hermes/vfx-retak-tanah`. Satu tugas = satu branch.
2. Commit & push **hanya** ke branch `hermes/*` milikmu: `git push -u origin hermes/<topik>`.
3. **Dilarang:**
   - commit/push ke `development`, `main`, atau branch yang bukan `hermes/*`;
   - `merge` ke branch lain, membuat/menggabung pull request, `rebase` branch orang lain;
   - `push --force`, `reset --hard` di branch selain milikmu, menghapus branch apa pun;
   - mengubah `.gitignore`, `.gitattributes`, konfigurasi Git LFS, atau hook.
4. Jangan commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `.vs/`, `*.sln`. File biner (`.uasset`, `.umap`, `.fbx`, `.png`, `.blend`, `.wav`, dll.) harus lewat **Git LFS** (sudah diatur di `.gitattributes`; cek `git lfs status` sebelum commit).
5. Pesan commit diawali `[hermes]`, contoh: `[hermes] level uji kamera raksasa`.

## 2. Area sandbox (satu-satunya tempat kamu boleh menulis)

| Jenis | Lokasi sandbox | Catatan |
|---|---|---|
| Aset Unreal (`.uasset`, BP, material, mesh, dll.) | `Content/Hermes/<topik>/` | Di Content Browser tampil sebagai folder **Hermes** |
| Level/map Unreal | `Content/Hermes/<topik>/Maps/Test_Hermes_<Topik>.umap` | Level baru, bukan menyunting level lama |
| C++ | `Source/Jayadwara/Hermes/<Topik>/` | File baru saja, lihat §4 |
| Skrip Python editor / Blender / tool | `Hermes/Tools/` | Bukan di `Tools/` |
| File Blender, gambar referensi, ekspor | `Hermes/Art/<topik>/` | Bukan di `Art/` |
| Catatan, usulan desain, laporan | `Hermes/Laporan/` | Bukan di `docs/` |

Di luar tabel di atas: **read-only**. Kamu boleh membaca semua file untuk memahami proyek.

## 3. Unreal Engine

- **Jangan sunting aset yang sudah ada** (apa pun di `Content/` di luar `Content/Hermes/`), termasuk `Content/Jayadwara/Maps/*`, `BP_Aksa`, `BP_Jayadwara`, GameMode, Input, Data Asset, Mannequin, dan `LevelPrototyping/`.
- Butuh memodifikasi aset lama? **Duplikat** dulu ke `Content/Hermes/<topik>/`, lalu ubah salinannya. Contoh: duplikat `Test_Combat` → `Content/Hermes/<topik>/Maps/Test_Hermes_<Topik>`.
- **Dilarang Move / Rename / Delete** aset lama (ini membuat redirector & mematahkan referensi). Jangan "Fix Up Redirectors" di folder lain.
- Jangan pakai **Save All** kalau ada aset di luar `Content/Hermes/` yang ikut berubah (bertanda `*`). Simpan hanya aset sandbox milikmu.
- Jangan ubah **Project Settings**, **World Settings level lama**, `Config/*.ini`, `Jayadwara.uproject`, atau mengaktifkan/mematikan plugin. Kalau perlu, buat level baru dengan GameMode Override di World Settings **level milikmu sendiri**, atau tulis usulannya di laporan.
- Skrip Python editor (termasuk lewat `Tools/ue_remote.py`) **hanya boleh menulis ke `/Game/Hermes/`**. Jalankan skrip di `Tools/` milik proyek hanya kalau skrip itu jelas read-only (mis. `ue_check_*`, `ue_capture_*`); skrip `ue_setup_*` / `ue_import_*` **jangan** dijalankan.
- Penamaan aset ikut prefix proyek (`BP_`, `SM_`, `SK_`, `M_`/`MI_`, `T_`, `ABP_`, `AM_`, `NS_`, `WBP_`, `DA_`/`DT_`, `GA_`/`GE_`, `IA_`/`IMC_`) — lihat `docs/12-technical-design.md`.

## 4. C++

- Hanya **file baru** di `Source/Jayadwara/Hermes/<Topik>/`. Nama class pakai prefix `JDH` (mis. `AJDHCameraTestActor`, file `JDHCameraTestActor.h/.cpp`) supaya tidak bentrok dengan class proyek (`JD`).
- **Jangan ubah** file C++ yang sudah ada (`Source/Jayadwara/**`, `Source/JayadwaraEditor/**`), `*.Build.cs`, `*.Target.cs`. Butuh modul baru / ubah class lama? Tulis di laporan (bagian "Usulan perubahan di luar sandbox") lengkap dengan potongan kode yang diusulkan.
- Kode harus tetap **compile** bersama proyek (pakai `JAYADWARA_API` atau tidak sama sekali; jangan mengandalkan modul yang belum ada di `Jayadwara.Build.cs`). Kalau tidak bisa memastikan compile, tulis jelas di laporan.

## 5. Blender (termasuk lewat MCP Blender)

- Jangan menimpa file di `Art/Blender/`. Kalau perlu mulai dari file lama: **Save As** ke `Hermes/Art/<topik>/<nama>_hermes_v01.blend` **sebelum** mengubah apa pun.
- Kalau Blender developer sedang terbuka dengan file proyek, jangan simpan ke file itu.
- Ekspor (`.fbx`/`.glb`) ke `Hermes/Art/<topik>/Export/`, bukan `Art/Export/`.

## 6. Dokumen desain

- `docs/` adalah sumber kebenaran desain — **read-only** untukmu. Baca `docs/README.md` dulu, lalu dokumen yang relevan (`docs/10-roadmap.md`, `docs/11-vertical-slice-spec.md`, `docs/23-rencana-fase-1.md` untuk scope aktif).
- Jangan ubah `CLAUDE.md`, `AGENTS.md`, `README` mana pun di luar `Hermes/`.
- Ide desain baru / perubahan desain → tulis di laporan sebagai **usulan**, jangan langsung diterapkan.

## 7. Hal yang selalu dilarang

- Menghapus/memindahkan file atau folder di luar sandbox.
- Memasukkan API key, token, password, atau path pribadi ke repo.
- Menambah dependensi/plugin/marketplace asset tanpa dicatat di laporan (sertakan lisensinya). Aset pihak ketiga hanya yang lisensinya aman untuk game komersial di Steam.
- Memakai IP milik pihak lain (mis. nama/desain Ultraman, Tsuburaya) — lihat `docs/01-konsep-dan-pilar.md`.

## 8. Laporan wajib (setiap selesai tugas)

Buat `Hermes/Laporan/YYYY-MM-DD-<topik>.md` di branch yang sama, isi:

```markdown
# <Judul tugas>
- Branch: hermes/<topik>
- Tanggal:
- Tugas dari developer: (ringkas permintaannya)

## Yang dibuat
- (daftar file/aset baru + path lengkap, mis. /Game/Hermes/<topik>/Maps/Test_Hermes_X)

## Cara mencoba
- (langkah: buka level apa, tekan apa, apa yang seharusnya terlihat)

## Status
- Compile C++: sudah dicek / belum dicek
- Yang sudah jalan / yang belum / bug yang diketahui

## Ketergantungan
- (aset/class proyek yang dipakai/direferensikan, plugin, aset pihak ketiga + lisensi)

## Usulan perubahan di luar sandbox
- (apa yang perlu diubah di file/aset lama supaya hasil ini bisa dipakai — JANGAN dikerjakan sendiri)
```

## 9. Alur setelah kamu selesai

1. Kamu: push branch `hermes/<topik>` + laporan. Selesai — **jangan merge**.
2. Developer mencoba hasilnya di editor.
3. Kalau dipakai, developer meminta **Claude** me-review dan mengimplementasikan ke `development` (memindahkan dari sandbox ke struktur proyek, menyesuaikan nama/prefix, memperbarui `docs/`).
4. Kalau tidak dipakai, branch dibiarkan atau dihapus oleh developer.
