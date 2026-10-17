# AGENTS.md — Aturan untuk Hermes (dan agent lain selain Claude)

Repo ini adalah game **JAYADWARA: Guardian of the Seven Gates** (Unreal Engine **5.6.1**, C++ + Blueprint). Pemeliharanya satu developer + Claude. Kamu (Hermes) di sini sebagai **pembantu eksperimen**: hasil kerjamu **selalu terisolasi**. Developer yang memutuskan apakah dipakai, lalu Claude yang me-review dan memindahkannya ke proyek utama.

> **Prinsip utama: jangan pernah mengubah, memindahkan, mengganti nama, atau menghapus apa pun yang sudah ada. Buat yang baru di area sandbox kamu sendiri.**

Kalau ragu sebuah tindakan melanggar aturan ini, **jangan lakukan**. Tulis di laporan sebagai usulan.

**Skill Hermes** ada di [`Hermes/skills/`](Hermes/skills/README.md) (format `SKILL.md`): `jd-mulai-tugas` (awal SETIAP tugas), `jd-perbaiki-model`, `jd-audit-model`, `jd-blender-skrip`, `jd-unreal-sandbox`, `jd-selesai-tugas` (sebelum commit/lapor). Kalau skill tidak terpasang otomatis, baca file `SKILL.md`-nya langsung sesuai situasi.

**Cara kerja & perbaikan model** ("lengan robek", "ketiak bolong", dll.): baca dan ikuti [`Hermes/panduan_kerja_claude.md`](Hermes/panduan_kerja_claude.md) **sebelum** menyentuh file. Perbaikan model **wajib** lewat `Art/Scripts/diagnosa_mesh.py` → `Art/Scripts/perbaiki_mesh.py` → diagnosa ulang `--sebelum`, bukan edit manual.

**Tugas model 3D apa pun** (NPC, monster, boss, varian): ikuti [`Hermes/panduan_model_3d.md`](Hermes/panduan_model_3d.md). Kalau ada instruksi khusus model `Hermes/<model>_hermes.md` (mis. [`aksa_hermes.md`](Hermes/aksa_hermes.md) untuk Aksa2), ikuti itu langkah demi langkah. Aturan di file ini menang atas keduanya.

---

## 0. Cara kerja (wajib, baca ini dulu)

Kamu sering salah di model 3D dan rigging, dan salahnya baru ketahuan saat developer membuka hasilnya. Aturan ini ada supaya kesalahan ketahuan **olehmu sendiri** dulu:

1. **Satu langkah, lalu cek.** Jangan menjalankan lima skrip lalu baru melihat hasil. Setelah tiap langkah: baca output/log sampai habis, buka gambar hasilnya, cocokkan dengan kriteria lulus langkah itu.
2. **Tidak ada klaim tanpa bukti.** "Sudah benar", "sudah rapi", "rig bagus" tidak berarti apa-apa. Yang dihitung: **angka** (output validator, IoU, jumlah tulang, tris, cm peregangan) dan **gambar** (path PNG). Setiap klaim di laporan harus menunjuk ke salah satunya.
3. **Lihat gambarnya sungguh-sungguh.** Setelah membuat render, buka file PNG-nya dan jelaskan apa yang terlihat per bagian (kepala, bahu, ketiak, siku, tangan, pinggang, selangkangan, lutut, kaki). Cari: lubang, kulit tembus baju, mesh melar/runcing, bagian melayang, warna di tempat salah, kiri-kanan tidak simetris. Kalau tidak bisa melihat gambar, **tulis itu** di laporan; jangan menebak isinya.
4. **Bandingkan, jangan menilai sendirian.** Model baru selalu dinilai **berdampingan** dengan pembanding: konsep (`Art/Reference/ak_ref_*.png`) dan model lama yang sudah dipakai (`SK_Aksa`). Kalau model baru lebih jelek dari model lama di satu aspek, tulis.
5. **Gagal = berhenti dan tulis.** Kalau kriteria lulus tidak tercapai setelah **3 percobaan**, berhenti, tulis di laporan apa yang dicoba, angka tiap percobaan, dan dugaan penyebabnya. Jangan melonggarkan kriteria, jangan mengubah validator supaya lulus, jangan menyembunyikan bagian yang rusak.
6. **Jangan improvisasi di luar instruksi.** Kalau langkah di instruksi tidak jelas atau tidak cocok dengan kondisi file, tanya developer atau tulis di laporan. Jangan mengarang nama tulang, nama aset, path, atau angka.
7. **Pakai path persis** seperti di instruksi. Salah satu huruf (mis. `aksa2` vs `Aksa2`) = file baru di tempat lain.
8. **Catat semuanya di laporan saat itu juga** (§8), bukan dari ingatan di akhir.
9. **Diminta memperbaiki sesuatu yang rusak?** Jangan langsung mengedit. Ikuti `Hermes/panduan_kerja_claude.md` §3: reproduksi → diagnosa dengan pembanding sehat → satu resep → diagnosa ulang `--sebelum` → regresi.

## 1. Git: worktree & branch sendiri

### 1a. Worktree (sekali per tugas)
Kamu bekerja di **folder salinan repo sendiri** (git worktree), bukan di folder developer. Jadi editor Unreal, Blender, dan file kamu tidak pernah menyentuh punya developer, bahkan kalau ada yang salah.

```
cd C:\repository\unreal_engine\jayadwara
git fetch origin development
git worktree add C:\repository\unreal_engine\jayadwara_hermes -b hermes/<topik-singkat> origin/development
cd C:\repository\unreal_engine\jayadwara_hermes
git lfs pull
```
- Semua kerjamu di `C:\repository\unreal_engine\jayadwara_hermes` (selanjutnya: **WORKTREE**). Jangan pernah `cd` ke folder developer untuk menulis apa pun.
- Buka Unreal dengan `WORKTREE\Jayadwara.uproject` (editor kamu sendiri). Pertama kali akan minta compile C++, jawab Yes.
- Tugas baru: worktree baru dengan branch baru, atau `git switch -c hermes/<topik-baru> origin/development` di WORKTREE setelah tugas lama sudah di-push.
- Nama branch: `hermes/<topik>`, contoh `hermes/aksa2`, `hermes/vfx-retak-tanah`. Satu tugas = satu branch.

### 1b. Aturan git
1. Commit & push **hanya** ke branch `hermes/*` milikmu: `git push -u origin hermes/<topik>`.
2. **Sebelum setiap commit**, jalankan cek sandbox dan pastikan **LULUS**:
   ```
   python -I Tools/hermes_cek_sandbox.py
   ```
   GAGAL → kembalikan file yang disebut (perintahnya dicetak skrip), jangan commit.
3. **Dilarang:**
   - commit/push ke `development`, `main`, atau branch yang bukan `hermes/*`;
   - `merge` ke branch lain, membuat/menggabung pull request, `rebase` branch orang lain;
   - `push --force`, `reset --hard` di branch selain milikmu, menghapus branch apa pun;
   - mengubah `.gitignore`, `.gitattributes`, konfigurasi Git LFS, atau hook.
4. Jangan commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `.vs/`, `*.sln`. File biner (`.uasset`, `.umap`, `.fbx`, `.png`, `.blend`, `.glb`, `.wav`, dll.) harus lewat **Git LFS** (sudah diatur di `.gitattributes`; cek `git lfs status` sebelum commit).
5. Pesan commit diawali `[hermes]`, contoh: `[hermes] aksa2 H3 rig + uji pose`.

## 2. Area sandbox (satu-satunya tempat kamu boleh menulis)

| Jenis | Lokasi sandbox | Catatan |
|---|---|---|
| Aset Unreal (`.uasset`, BP, material, mesh, skeleton, dll.) | `Content/Hermes/<Topik>/` (= `/Game/Hermes/<Topik>/`) | Di Content Browser tampil sebagai folder **Hermes** |
| Level/map Unreal | `Content/Hermes/<Topik>/Maps/Test_Hermes_<Topik>.umap` | Level baru, bukan menyunting level lama |
| C++ | `Source/Jayadwara/Hermes/<Topik>/` | File baru saja, lihat §4 |
| Skrip Python editor / Blender / tool | `Hermes/Tools/` | Bukan di `Tools/` atau `Art/Scripts/` |
| File Blender, sumber GLB, gambar, ekspor | `Hermes/Art/<topik>/` | Bukan di `Art/` |
| Catatan, usulan desain, laporan | `Hermes/Laporan/` | Bukan di `docs/` |
| Daftar & mentahan Mixamo untuk developer | `mixamo/asset/` | Aturan di [`mixamo/README.md`](mixamo/README.md) (read-only). FBX hasil download developer di `mixamo/result/` **dipindah** ke `Hermes/Art/<topik>/Mixamo/` (hanya di WORKTREE-mu; di folder developer cukup disalin) |

Di luar tabel di atas: **read-only**. Kamu boleh membaca semua file untuk memahami proyek. `Hermes/panduan_model_3d.md` dan semua `Hermes/<model>_hermes.md` juga read-only (instruksi dari Claude); progresmu ditulis di `Hermes/Laporan/`.

## 3. Unreal Engine

- **Jangan sunting aset yang sudah ada** (apa pun di `Content/` di luar `Content/Hermes/`), termasuk `Content/Characters/Mannequins/**` (`SK_Mannequin`, `SKM_Manny*`, animasi `MM_*`/`MF_*`), `Content/Jayadwara/**` (level, `BP_Aksa`, `BP_Jayadwara*`, GameMode, Input, Data Asset), dan `LevelPrototyping/`.
- **Jangan impor mesh ke skeleton yang sudah ada** (terutama `SK_Mannequin`). Impor skeletal mesh ke `SK_Mannequin` menambah/mengubah tulang di aset itu dan ikut tersimpan; ini yang merusak proyek 13–14 Okt 2026 (`SK_Mannequin` tersimpan 92 tulang, retarget crash, animasi Jayadwara2 terhapus; lihat docs/25 R7). Pakai **salinan skeleton** di sandbox (cara di `Hermes/aksa_hermes.md` H5).
- Butuh memodifikasi aset lama? **Duplikat** dulu ke `Content/Hermes/<Topik>/`, lalu ubah salinannya. Contoh: duplikat `Test_Combat` → `Content/Hermes/<Topik>/Maps/Test_Hermes_<Topik>`.
- **Dilarang Move / Rename / Delete** aset lama (membuat redirector & mematahkan referensi). Jangan "Fix Up Redirectors" di folder lain.
- Jangan pakai **Save All**. Simpan aset satu per satu (`EditorAssetLibrary.save_loaded_asset` untuk aset di `/Game/Hermes/` saja). Sebelum menutup editor, kalau muncul dialog "Save content" berisi aset di luar `/Game/Hermes/`, pilih **Don't Save**.
- Jangan ubah **Project Settings**, **World Settings level lama**, `Config/*.ini`, `Jayadwara.uproject`, atau mengaktifkan/mematikan plugin. Kalau perlu GameMode lain, pakai GameMode Override di World Settings **level milikmu sendiri**.
- Skrip Python editor dijalankan lewat **`python Tools/ue_remote.py <skrip>` dari WORKTREE**. Skrip itu hanya terhubung ke editor yang membuka proyek di folder repo yang sama, jadi tidak bisa mengenai editor developer. **Jangan pakai `--any-editor`.** Kalau keluar "Editor tidak ditemukan" dan di daftar hanya ada editor developer: buka editor WORKTREE dulu, jangan cari jalan lain.
- Skrip Python editor buatanmu **hanya boleh menulis ke `/Game/Hermes/`**. Di awal tiap skrip tulis konstanta `DEST = "/Game/Hermes/<Topik>"` dan semua path tujuan dibentuk dari `DEST`.
- Skrip proyek di `Tools/` yang boleh dijalankan langsung hanya `ue_remote.py` dan `hermes_cek_sandbox.py`. `Tools/ue_check_aksa.py` boleh **hanya saat level yang terbuka adalah level milikmu** (`Test_Hermes_*`), karena ia menaruh actor sementara di level yang sedang terbuka. Sisanya (`ue_setup_*`, `ue_import_*`, `ue_test_*`, `ue_capture_*`, `ue_probe_*`): **jangan** dijalankan; mereka membuka/menyimpan level lama dan menulis ke `/Game/Jayadwara/`. Butuh logikanya? Salin ke `Hermes/Tools/`, ubah semua tujuan ke `/Game/Hermes/<Topik>/` dan level ke level milikmu.
- Penamaan aset ikut prefix proyek (`BP_`, `SM_`, `SK_`, `SKEL_`, `PA_`, `IK_`, `RTG_`, `M_`/`MI_`, `T_`, `ABP_`, `AM_`, `NS_`, `WBP_`, `DA_`/`DT_`, `GA_`/`GE_`, `IA_`/`IMC_`) — lihat `docs/12-technical-design.md`.

## 4. C++

- Hanya **file baru** di `Source/Jayadwara/Hermes/<Topik>/`. Nama class pakai prefix `JDH` (mis. `AJDHCameraTestActor`, file `JDHCameraTestActor.h/.cpp`) supaya tidak bentrok dengan class proyek (`JD`).
- **Jangan ubah** file C++ yang sudah ada (`Source/Jayadwara/**`, `Source/JayadwaraEditor/**`, `Source/JayadwaraAnimNodes/**`), `*.Build.cs`, `*.Target.cs`. Butuh modul baru / ubah class lama? Tulis di laporan (bagian "Usulan perubahan di luar sandbox") lengkap dengan potongan kode yang diusulkan.
- Kode harus tetap **compile** bersama proyek (jangan mengandalkan modul yang belum ada di `Jayadwara.Build.cs`). Kalau tidak bisa memastikan compile, tulis jelas di laporan.

## 5. Blender

- **Pakai Blender headless** (`blender --background ... --python <skrip> -- <argumen>`) dengan file di WORKTREE. Jangan pakai MCP Blender: MCP mengendalikan Blender developer yang sedang terbuka. Kalau developer sendiri yang menyuruh lewat MCP: sebelum menyimpan, cek `bpy.data.filepath` berada di dalam `WORKTREE\Hermes\Art\` dan tulis hasil cek itu di log.
- Jangan menimpa file di `Art/Blender/`. Mulai dari file lama: buka, lalu langsung **Save As** ke `Hermes/Art/<topik>/<nama>_hermes_v01.blend` **sebelum** mengubah apa pun.
- Ekspor (`.fbx`/`.glb`) ke `Hermes/Art/<topik>/Export/`, render & gambar uji ke `Hermes/Art/<topik>/Render/`.
- **Skrip di `Art/Scripts/` banyak yang menulis path tetap** `C:\repository\unreal_engine\jayadwara\...` (folder developer!). Aturannya:
  - skrip yang menerima path input/output lewat argumen dan hanya **membaca** file proyek (mis. `aksa_spike_compare.py`, `aksa_12_compare_sheet.py`) boleh dipanggil langsung dari WORKTREE dengan argumen yang menunjuk ke sandbox;
  - selain itu: **salin** ke `Hermes/Tools/`, ganti setiap `C:\repository\unreal_engine\jayadwara` dengan path WORKTREE, dan arahkan output ke `Hermes/Art/<topik>/`. Setelah menyalin, cari lagi: `findstr /s /i "unreal_engine\\jayadwara" Hermes\Tools\*.py` harus hanya menemukan `jayadwara_hermes`.

## 6. Dokumen desain

- `docs/` adalah sumber kebenaran desain — **read-only** untukmu. Baca `docs/README.md` dulu, lalu dokumen yang relevan (`docs/10-roadmap.md`, `docs/11-vertical-slice-spec.md`, `docs/23-rencana-fase-1.md` untuk scope aktif).
- Jangan ubah `CLAUDE.md`, `AGENTS.md`, `Hermes/panduan_model_3d.md`, `Hermes/*_hermes.md`, `Art/Scripts/pose_profil/*`, `README` mana pun di luar `Hermes/Laporan/`.
- Ide desain baru / perubahan desain → tulis di laporan sebagai **usulan**, jangan langsung diterapkan.

## 7. Hal yang selalu dilarang

- Menghapus/memindahkan file atau folder di luar sandbox.
- Memasukkan API key, token, password, atau path pribadi ke repo.
- Menambah dependensi/plugin/marketplace asset tanpa dicatat di laporan (sertakan lisensinya). Aset pihak ketiga hanya yang lisensinya aman untuk game komersial di Steam.
- Memakai IP milik pihak lain (mis. nama/desain Ultraman, Tsuburaya) — lihat `docs/01-konsep-dan-pilar.md` dan checklist IP di `docs/19-rencana-model-aksa.md` §8.
- Melonggarkan validator / kriteria lulus supaya lulus.

## 8. Laporan wajib

Buat `Hermes/Laporan/YYYY-MM-DD-<topik>.md` di branch yang sama, **diperbarui setiap langkah selesai** (bukan hanya di akhir):

```markdown
# <Judul tugas>
- Branch: hermes/<topik>
- Worktree: C:\repository\unreal_engine\jayadwara_hermes
- Tanggal:
- Tugas dari developer: (ringkas permintaannya)

## Progres per langkah
| Langkah | Status (LULUS / GAGAL / BELUM) | Angka | Bukti (path log/PNG) |
|---|---|---|---|

## Yang dibuat
- (daftar file/aset baru + path lengkap, mis. /Game/Hermes/<Topik>/Maps/Test_Hermes_X)

## Cara mencoba
- (langkah: buka level apa, tekan apa, apa yang seharusnya terlihat)

## Hasil pembanding (wajib untuk model/rig/tekstur)
- (gambar lembar perbandingan + apa yang terlihat per bagian, termasuk yang JELEK)

## Status
- Compile C++: sudah dicek / belum dicek
- Cek sandbox: LULUS (tempel 1 baris output terakhir hermes_cek_sandbox.py)
- Yang sudah jalan / yang belum / bug yang diketahui

## Ketergantungan
- (aset/class proyek yang dipakai/direferensikan, plugin, aset pihak ketiga + lisensi)

## Usulan perubahan di luar sandbox
- (apa yang perlu diubah di file/aset lama supaya hasil ini bisa dipakai — JANGAN dikerjakan sendiri)
```

## 9. Alur setelah kamu selesai

1. Kamu: `hermes_cek_sandbox.py` LULUS → push branch `hermes/<topik>` + laporan. Selesai — **jangan merge**.
2. Developer mencoba hasilnya di editor (buka WORKTREE atau checkout branch-mu).
3. Kalau dipakai, developer meminta **Claude** me-review dan mengimplementasikan ke `development` (memindahkan dari sandbox ke struktur proyek, menyesuaikan nama/prefix, memperbarui `docs/`).
4. Kalau tidak dipakai, branch dibiarkan atau dihapus oleh developer.
