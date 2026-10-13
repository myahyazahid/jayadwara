# Aksa2 — Instruksi Kerja untuk Hermes

> Dari Claude, untuk Hermes. **File ini read-only bagimu**; progres ditulis di `Hermes/Laporan/YYYY-MM-DD-aksa2.md`.
> Baca dulu `AGENTS.md` sampai habis (terutama §0 Cara kerja, §3 Unreal, §5 Blender). Semua aturan di sana berlaku di sini.
> Ini contoh terisi dari [`panduan_model_3d.md`](panduan_model_3d.md) untuk model **jenis A** (manusia ber-skeleton Manny); H0–H7 = K0–K7 di panduan.
> Versi: 14 Okt 2026. Menggantikan cara kerja Aksa2 sebelumnya (folder `C:\repository\unreal_engine\explorasi\aksa2`, impor ke `SK_Mannequin`, tulis ke `/Game/Jayadwara/Characters/Aksa2/`), yang merusak `SK_Mannequin` dan animasi proyek 13–14 Okt 2026 (docs/25 R7).

---

## 0. Ringkasan

**Aksa2** = model Aksa (wujud manusia) versi baru dari model **Tripo** buatan developer, menggantikan `SK_Aksa` (model skrip, docs/19) **kalau** developer setuju setelah mencoba. Pola kerjanya sama dengan Jayadwara2 (docs/25), dengan satu beda besar: Aksa2 memakai **skeleton Mannequin asli tanpa diubah** (keputusan A1 docs/19), jadi semua animasi Manny langsung jalan.

Model **lama** (`SK_Aksa`) adalah **pembanding wajib** di setiap langkah: Aksa2 hanya dianggap maju kalau tidak lebih buruk dari model lama di angka audit, dan lebih baik secara visual.

### Sumber kebenaran (baca, jangan ubah)
| Dokumen / file | Isi yang dipakai |
|---|---|
| `docs/21-model-sheet-aksa.md` | Proporsi (H = **1,806 m**), palet (§3), bagian (§4), keputusan D1–D10 (§5), checklist IP (§6) |
| `docs/19-rencana-model-aksa.md` | Skeleton (§6.1), socket (§6.2), kontrak export FBX (§6.4), anggaran LOD (A8), checklist IP (§8) |
| `docs/25-rencana-redesign-jayadwara.md` | Pola kerja model Tripo + pelajaran (ketiak bolong R8, insiden `SK_Mannequin` R7) |
| `Art/Reference/ak_ref_front/side/back.png` | Konsep (pembanding siluet) |
| `Art/Export/SK_Aksa.fbx`, `SK_Aksa_LOD1..3.fbx`, `SK_Aksa_sockets.json` | Model lama (pembanding) |
| `Art/Reference/manny/SKM_Manny_Simple.fbx` | Armature Manny asli (dasar rig) |

### Alat yang sudah disiapkan Claude (pakai, jangan diubah)
| Alat | Fungsi |
|---|---|
| `Art/Scripts/audit_karakter.py` | Dari FBX: cek orientasi/tinggi/bobot, **17 pose uji**, regangan per pose, tepi terbuka, render 3/4 + **ketiak dari bawah**, render ortografis untuk konsep → `audit.json` |
| `Art/Scripts/banding_karakter.py` | Dua hasil audit (lama vs baru) + konsep → `banding_ortho.png`, `banding_pose.png`, `banding.md` dengan **VONIS LULUS/GAGAL** |
| `Art/Scripts/validate_aksa.py` | Validator kontrak FBX: 88 tulang Manny persis (≤1 mm, ≤0,5°), root, influence, bobot, tinggi, UV, slot (`--slots`), socket |
| `Art/Scripts/aksa_spike_compare.py` | Bandingkan tulang dua FBX (Manny asli vs hasil ekspor dari UE) |
| `Tools/hermes_cek_sandbox.py` | Cek semua perubahan ada di sandbox (wajib LULUS sebelum commit) |
| `Tools/ue_remote.py` | Jalankan Python di editor UE **milik worktree-mu** saja |

---

## 1. Persiapan (sekali)

```
cd C:\repository\unreal_engine\jayadwara
git fetch origin development
git worktree add C:\repository\unreal_engine\jayadwara_hermes -b hermes/aksa2 origin/development
cd C:\repository\unreal_engine\jayadwara_hermes
git lfs pull
```
Semua perintah di bawah dijalankan **dari `C:\repository\unreal_engine\jayadwara_hermes`** (WORKTREE). Di bawah ini `blender` = path lengkap `blender.exe` Blender 5.2 di komputer developer (tanya developer kalau tidak ada di PATH).

### Nama & lokasi (pakai persis)
| Apa | Path |
|---|---|
| Sumber GLB | `Hermes/Art/aksa2/Source/aksa2_tripo_v01.glb` (salinan; asli developer tidak diubah) |
| File Blender | `Hermes/Art/aksa2/Blender/aksa2_v01_intake.blend`, `aksa2_v02_rig.blend`, ... (nomor naik, file lama tidak ditimpa) |
| Skrip | `Hermes/Tools/aksa2_<nomor>_<nama>.py` |
| Export | `Hermes/Art/aksa2/Export/SK_Aksa2.fbx`, `SK_Aksa2_LOD1..3.fbx`, `SK_Aksa2_sockets.json`, `Textures/T_Aksa2_*.png` |
| Hasil audit | `Hermes/Art/aksa2/Audit/<nama>/` |
| Hasil banding | `Hermes/Art/aksa2/Banding/<langkah>/` |
| Aset UE | `/Game/Hermes/Aksa2/{Rig,Mesh,Materials,Textures,Maps}/` |
| Laporan | `Hermes/Laporan/YYYY-MM-DD-aksa2.md` |
| Objek Blender | awalan `AK2_` (`AK2_Body`, `AK2_Armature`) |

### Pekerjaan Aksa2 lama
- Folder `C:\repository\unreal_engine\explorasi\aksa2\` boleh **dibaca**. File yang masih berguna (GLB sumber, tekstur, skrip) **disalin** ke path di atas, lalu dicatat di laporan (asal → tujuan).
- Aset `/Game/Jayadwara/Characters/Aksa2/` (`SK_Aksa2_Spike`, `M_Aksa2_Master`, `T_Aksa2_*`) dan skrip `Tools/ue_import_aksa2_spike.py`, `Tools/ue_test_aksa2_combat.py` **jangan disentuh dan jangan dijalankan** (menulis ke luar sandbox, mengimpor ke `SK_Mannequin`, menyunting `Test_Combat`). Claude yang akan membereskannya nanti.

### Pembanding model lama (sekali, di awal)
```
blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- Art/Export/SK_Aksa.fbx --out Hermes/Art/aksa2/Audit/lama
```
Harus selesai dengan `HASIL AUDIT: 8/8 lulus`. Kalau tidak: berhenti, tulis di laporan (artinya file LFS belum ter-pull atau Blender salah versi).

---

## 2. Cara membaca hasil audit & banding (wajib dipahami sebelum H0)

Setiap kali ada FBX baru:
```
blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- Hermes/Art/aksa2/Export/SK_Aksa2.fbx --out Hermes/Art/aksa2/Audit/<langkah>
python -I Art/Scripts/banding_karakter.py --lama Hermes/Art/aksa2/Audit/lama --baru Hermes/Art/aksa2/Audit/<langkah> --out Hermes/Art/aksa2/Banding/<langkah>
```
1. **Baca `banding.md` sampai habis**, tempel ke laporan. Baris `GAGAL` = harus diperbaiki. Baris `PERIKSA <tulang>` = lihat area tulang itu di gambar.
2. **Buka `banding_ortho.png`**: kolom 2 (lama) vs kolom 3 (baru) vs konsep. Di kolom 4, merah = ada di konsep tapi tidak di model, cyan = ada di model tapi tidak di konsep. Lengan selalu sedikit beda (pose rest Manny ≠ pose konsep, D2); yang penting **badan, kepala, kaki**.
3. **Buka `banding_pose.png`** baris demi baris (18 pose). Tiap baris: lama 3/4 | baru 3/4 | ketiak lama | ketiak baru. Untuk **setiap pose**, tulis satu baris di laporan:
   `<pose>: <apa yang beda dari lama>; masalah: <tidak ada / lubang di ... / kulit tembus di ... / melar di ... / bagian melayang ...>`
   Yang dicari:
   - **Lubang / tembus**: backface culling nyala, jadi lubang tampak sebagai warna latar (biru-abu) di tengah badan. Paling sering di **ketiak, selangkangan, leher, siku dalam, lutut belakang**.
   - **Melar / runcing**: vertex tertarik jadi paku/tenda, terutama bahu, pinggul, pantat saat jongkok/tendang.
   - **Ikut tulang yang salah**: bagian badan ikut lengan, kantong ikut betis, rambut ikut bahu, ujung jaket ikut paha. Bandingkan dengan kolom lama: kalau lama tidak begitu, itu salah bobot.
   - **Kaku seperti patung** di tempat yang harus melentur (siku, lutut) atau melentur di tempat yang harus kaku (gesper, sol boots, liontin).
   - **Kiri-kanan beda**: pose simetris (rest, jongkok, lompat, tangan_terangkat) harus terlihat simetris.
4. Kalau **tidak bisa melihat gambar** (model tidak mendukung gambar): tulis "TIDAK BISA MELIHAT GAMBAR — perlu dicek developer" di laporan, dan **jangan pernah** menulis deskripsi gambar yang tidak kamu lihat.
5. **Vonis GAGAL tidak boleh dilewati** dengan mengubah `--toleransi`, `--iou-turun`, `--max-strain`, atau isi skrip. Perbaiki modelnya.

---

## 3. Iterasi

Setiap iterasi: kerjakan langkahnya → jalankan cek → isi tabel progres di laporan → commit (`hermes_cek_sandbox.py` LULUS dulu) → push. Iterasi bertanda **GATE** = berhenti dan tunggu developer bilang "lanjut".

### H0 — Intake GLB & penilaian · **GATE**
1. Salin GLB dari developer ke `Hermes/Art/aksa2/Source/aksa2_tripo_v01.glb`.
2. Salin `Art/Scripts/jayadwara2_01_import_tripo.py` → `Hermes/Tools/aksa2_01_import_tripo.py`. Ubah **hanya**: path default `--src`/`--out` ke path Aksa2 di atas, nama objek `JD2_Source` → `AK2_Source`, collection `JD2_Jayadwara` → `AK2_Aksa`, `ROOT` → WORKTREE. Cek `findstr` dari AGENTS.md §5.
3. Jalankan dengan `--top-z 1.806` (tinggi Manny). Cek arah hadap di laporan skrip; kalau model menghadap salah, ulangi dengan `--rot-z` lain (0, 90, -90, 180) sampai ujung kaki menghadap -Y.
4. Render ortografis depan/samping/belakang dengan **kanvas yang sama** dengan konsep (760×1200, 1000 px = 1,806 m, telapak y=1100, tengah x=380): salin `Art/Scripts/aksa_12_render.py` → `Hermes/Tools/aksa2_02_render.py` (ganti collection `AK_Aksa` → `AK2_Aksa`, armature boleh tidak ada di H0). Lalu:
   `python -I Art/Scripts/aksa_12_compare_sheet.py Hermes/Art/aksa2/Render/h0 Hermes/Art/aksa2/Render/h0/compare.png`
5. Laporan H0 berisi: tris, jumlah objek/material, ukuran tekstur, tepi non-manifold, tinggi, IoU (penuh/inti/badan) **berdampingan dengan IoU model lama** (`Audit/lama` + `aksa_12_compare_sheet.py` pada folder itu), checklist IP docs/19 §8 satu per satu (✅/❌ + alasan), warna emas vs silver (lihat close-up kalung, gesper, ritsleting; palet docs/21 §3), bagian yang **menyatu** (jari, lengan ke badan, selendang ke paha, rambut ke kerah).
- **Lulus H0:** tinggi 1,806 ±0,01 m; menghadap -Y; IoU badan depan ≥ 0,80; tidak ada ❌ di checklist IP.
- **GATE:** developer membaca laporan H0 dan bilang lanjut / minta GLB baru.

### H1 — Fit ke pose rest Manny
Model Tripo hampir pasti tidak dalam pose rest Manny (lengan 35°/53° dari vertikal, pinggul ±0,100 m, lutut ±0,123 m, pergelangan kaki ±0,141 m — docs/21 D2). Skeleton **tidak boleh** diubah, jadi **mesh** yang dipaskan ke tulang.
1. Impor `Art/Reference/manny/SKM_Manny_Simple.fbx` ke file kerja (lihat cara di `Art/Scripts/aksa_10_armature.py`: empty skala 0,01 dibuang, skala di-apply, tulang `root` ditambahkan sebagai induk tulang akar Manny). Nama objek `AK2_Armature`. **Jangan memindah/memutar tulang apa pun.**
2. Pasang mesh ke pose Manny: armature sementara di pose Tripo → bobot otomatis → pose ke rest Manny → apply. Simpan sebagai `aksa2_v02_fit.blend`.
3. Ukur dan tulis: posisi bahu, siku, pergelangan, pinggul, lutut, pergelangan kaki mesh vs sendi Manny (`Art/Reference/manny/manny_rest.json`, `joints_m`).
- **Lulus H1:** tiap sendi mesh ≤ 2 cm dari sendi Manny (tabel per sendi di laporan); render depan/samping menunjukkan lengan dalam pose Manny tanpa kusut di bahu/siku.

### H2 — Pemisahan & pembersihan geometri
1. Pisahkan yang menyatu (dari laporan H0): jari, lengan dari badan, selendang dari paha. Bagian yang tidak bisa dipisah rapi: tulis, jangan dipaksa.
2. Tutup lubang hasil potongan; hapus kulit di bawah baju (D9); buang serpihan (pulau mesh < 50 vertex yang tidak terlihat).
3. Simpan `aksa2_v03_clean.blend`.
- **Lulus H2:** jumlah tepi terbuka (boundary) di zona ketiak, selangkangan, leher dicatat sebelum vs sesudah dan **turun**; render ortografis tidak berubah bentuk (IoU badan selisih ≤ 0,02 dari H1).

### H3 — Rig & skinning (spike) · **GATE**
Bagian paling sering salah. Kerjakan pelan.
1. Bobot: **transfer dari model lama** sebagai awal (Data Transfer, nearest face interpolated, sumber = mesh `SK_Aksa.fbx` yang diimpor), lalu perbaiki. Bagian kaku diberi **satu tulang** penuh: gesper & cincin sabuk → `pelvis`; liontin → `spine_05`; sol & trim boots → `foot_l/r` (+ `ball_l/r` di ujung); rambut → `head`.
2. Twist: bobot lengan bawah dibagi ke `lowerarm_twist_01/02`, lengan atas ke `upperarm_twist_01/02`, paha ke `thigh_twist_01/02`, seperti model lama (cek `Audit/lama`).
3. Selendang: rantai `sash_01..06` di bawah `pelvis` (docs/19 §6.1); kalau selendang belum dipisah, tulis dan lewati.
4. Bersihkan: maks 4 influence, normalisasi, 0 vertex tanpa bobot.
5. Export LOD0 dengan kontrak docs/19 §6.4: salin `Art/Scripts/aksa_14_export.py` → `Hermes/Tools/aksa2_14_export.py` (ubah `FBX_OUT`, `MESH_NAME = "SK_Aksa2"`, nama objek, `ROOT`). Socket: 7 socket dengan **nama & tulang sama** dengan `Art/Export/SK_Aksa_sockets.json` → `SK_Aksa2_sockets.json`.
6. Cek, berurutan, berhenti di yang pertama gagal:
   ```
   blender --background --factory-startup --python Art/Scripts/validate_aksa.py -- Hermes/Art/aksa2/Export/SK_Aksa2.fbx --max-tris 60000 --require-uv --slots <nama slot material, urut, dipisah koma>
   blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- Hermes/Art/aksa2/Export/SK_Aksa2.fbx --out Hermes/Art/aksa2/Audit/h3
   python -I Art/Scripts/banding_karakter.py --lama Hermes/Art/aksa2/Audit/lama --baru Hermes/Art/aksa2/Audit/h3 --out Hermes/Art/aksa2/Banding/h3
   ```
- **Lulus H3:** `validate_aksa.py` semua PASS (tempel output lengkap); `banding.md` **VONIS: LULUS**; deskripsi 18 pose di laporan (cara §2.3) tanpa lubang/tembus di ketiak & selangkangan.
- Gagal 3× → berhenti, laporkan (AGENTS.md §0.5).
- **GATE:** developer melihat `banding_pose.png` dan bilang lanjut.

### H4 — Tekstur & material
1. Atlas Tripo dipertahankan. Perbaiki: warna di zona salah, emas pucat/silver → emas `#D6A33A` matte (D8), biru menyala → hilang (IP). Turunkan `T_Aksa2_N`, `T_Aksa2_ORM` (R=AO, G=roughness, B=metallic; emas metallic rendah, D8) dan `T_Aksa2_Mask` bila perlu (docs/22 §2). Simpan ke `Hermes/Art/aksa2/Export/Textures/`.
2. Render 3/4 berwarna (Eevee/Workbench tekstur) depan & belakang, close-up kepala 3/4, close-up kalung/gesper/emblem punggung.
- **Lulus H4:** di laporan, untuk tiap zona palet docs/21 §3: warna sampel dari render (hex) vs usulan; emas tidak terbaca silver; tidak ada noda warna salah (sebut lokasi kalau ada); emblem punggung lolos D6.

### H5 — LOD & validasi akhir
1. LOD1–3 (salin pola `Art/Scripts/aksa_60_lods.py` ke `Hermes/Tools/aksa2_60_lods.py`, OUT_DIR ke Export sandbox). Anggaran: LOD0 ≤ 60k, LOD1 ≤ 25k, LOD2 ≤ 10k, LOD3 ≤ 4k tris (A8). Kepala, mata, tangan, liontin dilindungi.
2. Tiap LOD: `validate_aksa.py` (dengan `--max-tris` sesuai LOD) + `audit_karakter.py` + `banding_karakter.py` **melawan LOD lama yang sama** (`Art/Export/SK_Aksa_LOD<n>.fbx` diaudit ke `Audit/lama_lod<n>`).
- **Lulus H5:** 4 LOD × validator PASS, 4 × VONIS LULUS; tabel tris per LOD di laporan.

### H6 — Uji di Unreal (sandbox) · **GATE**
Buka editor dari `WORKTREE\Jayadwara.uproject`. Semua skrip lewat `python Tools/ue_remote.py Hermes/Tools/<skrip>.py`.
1. **Salinan skeleton** (tidak pernah impor ke `SK_Mannequin`):
   - muat dulu `/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple` dan `/Game/Jayadwara/Characters/Aksa/Mesh/SK_Aksa` (supaya skeleton lengkap di memori — docs/25 R7; **jangan disimpan**);
   - `EditorAssetLibrary.duplicate_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin", "/Game/Hermes/Aksa2/Rig/SKEL_Aksa2")`;
   - cetak jumlah tulang salinan (`AnimPoseExtensions.get_bone_names(get_reference_pose(skel))`), harus ≥ 161;
   - di `SKEL_Aksa2`, tambahkan `SK_Mannequin` ke **Compatible Skeletons** (supaya animasi Manny bisa diputar). Simpan **hanya** `SKEL_Aksa2`.
2. Impor `SK_Aksa2.fbx` + LOD ke `/Game/Hermes/Aksa2/Mesh/` dengan skeleton `SKEL_Aksa2` (pola impor `Tools/ue_import_aksa.py`, semua tujuan diganti ke `/Game/Hermes/Aksa2/`). Tekstur & `M_Aksa2_Master` + `MI_Aksa2_*` ke folder sandbox. Socket dari JSON.
3. **Bukti tidak merusak**: setelah impor, jalankan cek ini dan tempel hasilnya:
   - `git status --porcelain` → tidak ada `.uasset` di luar `Content/Hermes/`;
   - `python -I Tools/hermes_cek_sandbox.py` → LULUS.
   Kalau ada aset lama yang berubah: **jangan disimpan**, tutup editor tanpa save, `git restore` file itu, tulis di laporan.
4. Level uji: duplikat `/Game/Jayadwara/Maps/Test_Combat` → `/Game/Hermes/Aksa2/Maps/Test_Hermes_Aksa2`. Di level itu: `SK_Aksa` (kiri) dan `SK_Aksa2` (kanan) sebagai SkeletalMeshActor berdampingan, masing-masing memutar `MM_Idle`, `MF_Unarmed_Walk_Fwd`, `MM_Attack_01..03` (path di `Tools/ue_test_aksa2_combat.py`; logika boleh disalin, level & tujuan diganti).
5. Screenshot berdampingan per animasi (pakai `Tools/ue_check_aksa.py` saat `Test_Hermes_Aksa2` terbuka, atau salinannya). Deskripsikan tiap screenshot seperti §2.3.
- **Lulus H6:** animasi jalan di `SK_Aksa2` (screenshot 2 frame berbeda tidak identik); tinggi bounds ±180,6 cm (cetak dari `get_bounds`); 7 socket ada; cek sandbox LULUS.
- Compatible Skeletons tidak membuat animasi jalan → **berhenti dan laporkan**. Jangan mencari jalan pintas dengan mengimpor ke `SK_Mannequin`.
- **GATE:** developer membuka `Test_Hermes_Aksa2` dan menilai.

### H7 — Laporan akhir & serah terima
1. Laporan lengkap (template AGENTS.md §8) + tabel progres H0–H6 + semua `banding.md` + daftar gambar.
2. "Usulan perubahan di luar sandbox" minimal berisi: impor `SK_Aksa2` ke skeleton proyek, mengganti mesh di `BP_Aksa`, Physics Asset, Anim Dynamics jaket/selendang, dan cara membalik ke `SK_Aksa`. **Tidak dikerjakan sendiri.**
3. `hermes_cek_sandbox.py` LULUS → commit → push `hermes/aksa2`. Selesai; Claude yang me-review dan memindahkan.

---

## 4. Kesalahan yang sudah pernah terjadi (jangan diulang)

| Kesalahan | Akibat | Pencegahan |
|---|---|---|
| Mengimpor mesh ke `SK_Mannequin` lalu menyimpan | `SK_Mannequin` tersimpan 92 tulang, retarget crash, `Jayadwara2/Anims` terhapus (13–14 Okt) | Salinan `SKEL_Aksa2` di sandbox (H6.1); cek sandbox sebelum commit |
| Bekerja di folder di luar repo (`explorasi`) dengan skrip yang menulis ke repo | Perubahan tidak terlacak, tercampur ke commit developer | Worktree + branch `hermes/aksa2` |
| Ketiak bolong tidak terlihat di render depan | Baru ketahuan saat Play (Jayadwara2 R8) | Render ketiak dari bawah dengan backface culling (`audit_karakter.py`) |
| Menyatakan "rig sudah bagus" tanpa angka | Developer menemukan masalah sendiri | Vonis `banding_karakter.py` + deskripsi 18 pose |
| Skrip salinan masih menunjuk `C:\repository\unreal_engine\jayadwara` | Menimpa file developer | Ganti `ROOT`, cek `findstr` (AGENTS.md §5) |
| Mengubah tulang Manny supaya cocok dengan mesh | Animasi Manny rusak di model | Tulang tidak pernah diubah; mesh yang dipaskan (H1); `validate_aksa.py` ≤ 1 mm / 0,5° |
