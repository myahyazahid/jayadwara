# Maps Ep 1 (greybox) — Instruksi Kerja untuk Hermes

> Dari Claude, untuk Hermes. **File ini read-only bagimu**; progres ditulis di `Hermes/Laporan/YYYY-MM-DD-maps_ep1.md`.
> Baca dulu `AGENTS.md` sampai habis (terutama §0 Cara kerja, §1 Git, §2 Sandbox, §3 Unreal, §5 Blender), lalu skill `Hermes/skills/jd-mulai-tugas`, `jd-blender-skrip`, `jd-unreal-sandbox`, `jd-selesai-tugas`. Kalau ada beda, `AGENTS.md` menang atas file ini.
> Desain yang dibangun: [`docs/30-desain-level-ep01.md`](../docs/30-desain-level-ep01.md) (+ gambar `docs/concept-art/ep01_lawangsapta_konsep_v01.webp`, `docs/visual/ep01_denah_skala_v01.jpg`).
> Versi: 16 Okt 2026.
> **Jalur paralel Level/Map** (keputusan developer 16 Okt 2026): boleh dikerjakan sekarang, terpisah dari iterasi Fase 1. Tulis kalimat itu di laporan.

---

## 0. Ringkasan

Bangun **greybox** map Episode 1 `Ep01_LawangSapta` di Unreal: medan bukit, galian berundak, candi, desa, sawah, prop proyek, penanda gameplay, batas arena, dan 6 kamera dengan render PNG. Semua masih **kotak dan warna datar**. Tujuannya supaya developer bisa **memainkan** map ini sebagai Aksa (1,75 m) dan Jayadwara2 (45 m) untuk menilai skala.

**Semua angka sudah ditentukan.** Kamu tidak mengarang posisi, ukuran, atau tinggi. Sumbernya dua file read-only:

| File (read-only) | Isi |
|---|---|
| `Art/Level/ep01_medan.py` | Fungsi `elev(x, y)`: tinggi medan di setiap titik (meter). Ada uji mandiri |
| `Art/Level/ep01_layout_v01.json` | 43 objek, 11 penanda gameplay, 2 zona, batas arena, 6 kamera, 2 setelan cahaya |

Ada yang terasa salah di data itu (objek melayang, menembus, posisi aneh)? **Jangan ubah filenya.** Tulis di laporan bagian "Usulan perubahan di luar sandbox" dengan angka dan screenshot. Claude yang memperbaiki.

### Tidak dikerjakan di tugas ini
- **Landscape UE** (sculpt/paint): medan adalah static mesh dari Blender. Konversi ke Landscape nanti di Fase 2.
- **Gedung hancur Chaos / Geometry Collection**: bangunan cukup kotak biasa bertag `hancur`.
- **C++ apa pun**: tidak dibutuhkan.
- Foliage, pencahayaan art, material realistis, NPC, minion, boss yang bergerak.
- Menjalankan `Tools/ue_setup_*`, `ue_import_*`, `ue_test_*`, `ue_capture_*`, `ue_probe_*` (AGENTS.md §3).

---

## 1. Persiapan (sekali)

```
cd C:\repository\unreal_engine\jayadwara
git fetch origin development
git worktree add C:\repository\unreal_engine\jayadwara_hermes_maps_ep1 -b hermes/maps_ep1 origin/development
cd C:\repository\unreal_engine\jayadwara_hermes_maps_ep1
git lfs pull
```
- **WORKTREE** = `C:\repository\unreal_engine\jayadwara_hermes_maps_ep1`. Semua perintah di bawah dijalankan dari sini.
- **Branch** = `hermes/maps_ep1`.
- Editor: buka `WORKTREE\Jayadwara.uproject` (editor terpisah dari developer dan dari worktree Hermes lain). Pertama kali minta compile C++ → Yes.
- `ue_remote.py` hanya terhubung ke editor dari folder yang sama. Kalau muncul "Editor tidak ditemukan", buka editor WORKTREE ini dulu; **jangan** `--any-editor`.
- `blender` = path lengkap `blender.exe` Blender 5.2, dijalankan **headless** (AGENTS.md §5). Jangan pakai MCP Blender.
- Pastikan `Art/Level/ep01_medan.py` dan `Art/Level/ep01_layout_v01.json` ada di WORKTREE. Kalau tidak ada, branch `development` belum berisi PR desain Ep 1: **berhenti dan lapor**.

### Nama & lokasi (pakai persis)
| Apa | Path |
|---|---|
| Folder aset UE (`DEST`) | `/Game/Hermes/MapsEp1` (= `Content/Hermes/MapsEp1/`) |
| Level greybox | `/Game/Hermes/MapsEp1/Maps/Test_Hermes_MapsEp1` |
| Mesh medan + tangga | `/Game/Hermes/MapsEp1/Meshes/SM_Ep01_Medan`, `SM_Ep01_Tangga` |
| Material | `/Game/Hermes/MapsEp1/Materials/M_Hermes_Greybox` + `MI_Ep01_<Nama>` |
| Skrip | `Hermes/Tools/maps_ep1_<NN>_<nama>.py` |
| File Blender, ekspor, render | `Hermes/Art/maps_ep1/` (`maps_ep1_medan_v01.blend`, `Export/`, `Render/`) |
| Laporan | `Hermes/Laporan/YYYY-MM-DD-maps_ep1.md` (format AGENTS.md §8) |
| Commit | `[hermes] maps_ep1 M<n> <ringkas>` |

---

## 2. Konvensi data (wajib dipahami sebelum menulis skrip)

### Koordinat
- Data dalam **meter**: `x` = timur, `y` = utara, `z` = atas, `z = 0` = muka tanah desa. Titik nol = tengah dasar galian.
- **Ke UE (cm):** `UE_X = x * 100`, `UE_Y = -y * 100`, `UE_Z = z * 100`. Dengan ini tampak atas UE (X kanan, Y ke bawah) = utara di atas, sama dengan denah `docs/30`.
- **Yaw** objek di JSON (`"yaw"`, derajat, berlawanan jarum jam dilihat dari atas, 0 = menghadap timur) → yaw UE = `-yaw`.
- **Hadap ke titik** (`"hadap_ke"`, `"lihat_ke"`): hitung di koordinat UE: `yaw = degrees(atan2(UE_Y_target - UE_Y, UE_X_target - UE_X))`, pitch dari selisih Z dan jarak datar.

### Ketinggian objek
- Objek tanpa `"z"`: **alas objek = nilai `elev` terendah di bawah tapaknya** (sampel tiap 1 m di dalam persegi tapak, setelah rotasi), supaya tidak ada yang melayang. Alas lebih rendah dari tanah di sisi miring itu wajar (terbenam sedikit).
- `"z_dasar_relatif"`: ditambahkan ke alas tadi (mis. ambang gerbang mulai 6 m di atas tanah, arca di atas alasnya).
- `"ukuran": [P, L, T]` = panjang (sumbu x sebelum rotasi), lebar (y), tinggi (z), dalam meter.

### Jenis objek
| `jenis` | Cara membangun |
|---|---|
| `kotak` | `/Engine/BasicShapes/Cube` (100 cm, pivot di tengah) diskala `P, L, T`; lokasi Z = alas + T/2 |
| `rumah` | Kotak dinding `P × L × (T − 2)` + kotak atap `(P + 0,6) × (L + 0,6) × 2` di atasnya (satu actor induk + anak, atau dua actor dengan label `_Dinding`/`_Atap`) |
| `candi_bertingkat` | Kotak bertumpuk sesuai daftar `tingkat` (dari bawah), masing-masing di atas yang sebelumnya |
| `tangga` | Mesh `SM_Ep01_Tangga` dari Blender (M2): `anak_tangga` balok dari `dari` ke `ke`, lebar `lebar` |
| `dinding` | Kotak tipis dari titik `dari` ke `ke`, tinggi `tinggi`, tebal `tebal`. `tanpa_tabrakan: true` → collision NoCollision |
| `bidang` | `/Engine/BasicShapes/Plane` diskala `P × L`, 5 cm di atas tanah |

- **Tag actor:** `hancur` untuk `"hancur": true`, tambah `cadangan` untuk `"cadangan": true`. Ini dipakai nanti saat diganti Geometry Collection.
- **Label actor** = `id` persis. **Folder Outliner** = awalan id (`CANDI`, `PROYEK`, `DESA`, `SAWAH`, `LATAR`, `PENANDA`, `ZONA`, `BATAS`, `KAMERA`).

### Material greybox (`M_Hermes_Greybox`)
Satu material dengan parameter vektor `Warna` → Base Color, Roughness 0,9. Instance:

| MI | Warna (sRGB) | Dipakai |
|---|---|---|
| `MI_Ep01_Andesit` | 108, 120, 113 | candi, tangga, pilar tol, batu |
| `MI_Ep01_Arca` | 150, 140, 110 | arca kiri/kanan (beda dari andesit supaya terbaca) |
| `MI_Ep01_Galian` | 181, 88, 47 | slot medan Galian |
| `MI_Ep01_Plato` | 128, 132, 118 | slot medan Plato |
| `MI_Ep01_Sawah` | 126, 162, 89 | slot medan Sawah, lapangan desa |
| `MI_Ep01_Desa` | 199, 166, 121 | slot medan Desa, rumah |
| `MI_Ep01_Hutan` | 79, 107, 74 | slot medan Hutan |
| `MI_Ep01_Air` | 91, 143, 176 | slot medan Air |
| `MI_Ep01_Jalan` | 150, 120, 90 | slot medan Jalan |
| `MI_Ep01_Kayu` | 140, 100, 60 | warung, gardu, gubuk |
| `MI_Ep01_Alat` | 230, 180, 40 | alat berat, truk, pos mandor, menara air, pagar |
| `MI_Ep01_Terpal` | 60, 110, 200 | tenda |
| `MI_Ep01_Kendaraan` | 40, 40, 45 | mobil DWARA |
| `MI_Ep01_Musala` | 240, 240, 235 | musala |
| `MI_Ep01_Penanda` | 225, 50, 50 | garis polisi, lapangan bola, area penanda |

---

## 3. Langkah M0–M7

Satu langkah → cek → catat di laporan → commit. Gagal 3× → berhenti dan tulis (AGENTS.md §0.5).

### M0 — Persiapan
- Worktree, branch, editor terbuka (bagian 1). Buat laporan dari templat AGENTS.md §8.
- Jalankan `python -I Art/Level/ep01_medan.py`.
- **Lulus jika:** keluaran berakhir `SEMUA LULUS` (12 titik uji + jarak galian→desa ≥ 150 m). Tempel keluarannya di laporan.

### M1 — Cek data layout
- Tulis `Hermes/Tools/maps_ep1_11_cek_layout.py` (Python biasa, `-I`): baca JSON, impor `elev` dari `Art/Level/ep01_medan.py` (tambahkan `Art/Level` ke `sys.path`), lalu cetak tabel: id, jenis, pos, alas (m), selisih tanah di tapak (maks − min).
- **Lulus jika:** 43 objek, 11 penanda, 2 zona, 6 kamera terbaca; semua `pos` di dalam batas medan; objek `DESA_*` alasnya 0,0 m; objek `CANDI_*` (kecuali tangga) alasnya 35,0 m. Selisih tanah > 2 m dicatat di laporan sebagai temuan (bukan diperbaiki).

### M2 — Medan + tangga di Blender (headless)
- Tulis `Hermes/Tools/maps_ep1_20_medan_blender.py`, jalankan:
  `blender --background --factory-startup --python Hermes/Tools/maps_ep1_20_medan_blender.py -- --out Hermes/Art/maps_ep1`
- Isi skrip:
  1. Grid dari `medan` di JSON (`x` −340…460, `y` −420…280, sel 2 m → **401 × 351 = 140.751 vertex**), tinggi = `elev(x, y)`.
  2. Tiap muka diberi slot material menurut `material_zona` di JSON (dievaluasi di titik tengah muka, urutan aturan dari atas; yang pertama cocok menang). Nama slot = `Air`, `Galian`, `Jalan`, `Plato`, `Sawah`, `Desa`, `Hutan`.
  3. Objek kedua `SM_Ep01_Tangga`: 28 balok dari (0; 87,5; 28) ke (0; 112,5; 35), lebar 10 m, origin di (0, 0, 0) dunia yang sama dengan medan.
  4. Simpan `Hermes/Art/maps_ep1/maps_ep1_medan_v01.blend`; ekspor `Export/SM_Ep01_Medan.fbx` dan `Export/SM_Ep01_Tangga.fbx` (satuan meter; pastikan di UE jadi cm, lihat M3).
  5. Render dua PNG (Eevee, warna slot sesuai tabel MI): `Render/M2_atas.png` (ortografis dari atas, utara di atas) dan `Render/M2_miring.png` (dari selatan-barat daya, sudut ±35° ke bawah, seperti gambar konsep).
- **Lulus jika:** jumlah vertex medan 140.751; skrip mencetak tinggi mesh di 12 titik uji (`TITIK_UJI` di `ep01_medan.py`) dan semuanya sama dengan `elev` ± 0,05 m; kedua PNG ada. **Buka kedua PNG** dan bandingkan dengan `docs/visual/ep01_denah_skala_v01.jpg` dan denah `docs/30`: galian tapal kuda terbuka ke selatan, 4 undakan, ram timur dan utara, plato, jalan akses di punggung bukit timur, jalan proyek, kali di barat, sawah selatan-tenggara, desa barat daya. Tulis apa yang terlihat per bagian.

### M3 — Level UE + medan
- Tulis `Hermes/Tools/maps_ep1_30_level.py` (diawali `DEST = "/Game/Hermes/MapsEp1"`), jalankan `python Tools/ue_remote.py Hermes/Tools/maps_ep1_30_level.py`:
  1. Level baru dari `/Engine/Maps/Templates/Template_Default` → `DEST/Maps/Test_Hermes_MapsEp1`. Hapus lantai bawaan template.
  2. Impor kedua FBX ke `DEST/Meshes` sebagai Static Mesh (tanpa Nanite, tanpa LOD otomatis). Collision: **Use Complex as Simple**.
  3. Buat `M_Hermes_Greybox` + 15 MI (bagian 2), pasang ke slot medan menurut nama slot.
  4. Taruh medan dan tangga di (0, 0, 0).
  5. World Settings level ini: **GameMode Override = `/Game/Jayadwara/Core/BP_JDGameMode`** (hanya direferensikan, tidak diubah). GameMode ini memakai `BP_Aksa` dan `BP_JDPlayerController`, yang sudah bisa berubah ke Jayadwara2 dengan tombol **T**.
  6. Simpan level dan aset `DEST` satu per satu. **Tidak pernah Save All.**
- **Lulus jika:** bounds medan ±80.000 × 70.000 cm, Z −1.400 … ±8.000 cm; line trace vertikal di 12 titik uji mengenai medan di `elev × 100` ± 5 cm (cetak tabelnya); `python -I Tools/hermes_cek_sandbox.py` LULUS. Screenshot viewport perspektif di laporan.

### M4 — Objek (candi, proyek, desa, sawah, latar)
- `Hermes/Tools/maps_ep1_40_objek.py`: bangun 43 objek dari JSON sesuai bagian 2 (jenis, alas, rotasi, MI, tag, label, folder).
- **Lulus jika:** 43 objek ada (rumah dihitung satu objek walau dua actor); skrip memeriksa ulang setiap objek: **alas actor = alas yang dihitung ± 5 cm** dan tidak ada objek yang alasnya di bawah tanah lebih dari 1 m di titik tengahnya; 10 objek bertag `hancur` (2 di antaranya `cadangan`); `DESA_Musala` dan semua `CANDI_*` **tanpa** tag `hancur`. Cetak tabelnya. Screenshot tiga sudut: candi dari tangga, desa dari sawah, galian dari START.

### M5 — Penanda gameplay, zona, batas arena
- `Hermes/Tools/maps_ep1_50_penanda.py`:
  1. `START` → **PlayerStart** di atas tanah, yaw menghadap `hadap_ke` (gerbang). Hapus PlayerStart bawaan template.
  2. Penanda `titik` → **TargetPoint** + **TextRenderActor** (teks = `label`, tinggi huruf 150 cm, 3 m di atas tanah, selalu menghadap kamera tidak perlu).
  3. Penanda `area` → silinder `/Engine/BasicShapes/Cylinder` setinggi 0,2 m dengan radius `radius`, `MI_Ep01_Penanda`, **NoCollision**, + TextRender.
  4. `zona` → **TriggerBox** seukuran persegi `x`, `y`, tinggi 60 m (terlihat sebagai garis di editor), label = id, + TextRender besar (500 cm) di tengahnya.
  5. `batas_arena` → 4 dinding kotak tak terlihat di tepi persegi, tinggi 100 m, **Hidden in Game**, collision **BlockAll**. Tambah 4 dinding yang sama di tepi medan (−340/460, −420/280) sebagai pengaman jatuh.
- **Lulus jika:** jumlah actor per jenis sesuai JSON (1 PlayerStart, 6 titik, 4 area, 2 zona, 8 dinding); PlayerStart berdiri di Z = `elev(140, −20) × 100` + setengah tinggi kapsul ± 10 cm. Screenshot tampak atas dengan semua penanda terlihat.

### M6 — Kamera dan render C1–C6
- `Hermes/Tools/maps_ep1_60_kamera.py`:
  1. **CameraActor** untuk tiap kamera JSON (label = id, folder `KAMERA`): posisi = `pos` + `tinggi_di_atas_tanah` di atas `elev`, arah ke `lihat_ke`, FOV dari JSON. `C5_TampakAtas` = ortografis, lebar `lebar_ortho` m, menghadap lurus ke bawah.
  2. Setel **DirectionalLight** bawaan template sesuai `cahaya` kamera (`sore` / `senja`: pitch, yaw, warna, intensitas) sebelum merender kamera itu.
  3. Render dengan **SceneCapture2D** (ikut transform/FOV/ortho kamera) ke Render Target 1920 × 1080, ekspor PNG ke `Hermes/Art/maps_ep1/Render/<id>_<cahaya>.png`. Capture buram → `r.Streaming.FullyLoadUsedTextures 1`.
- **Lulus jika:** 6 PNG ada, 1920 × 1080, tidak hitam (rata-rata kecerahan > 20/255). **Buka tiap PNG** dan cocokkan dengan daftar ini (tulis ya/tidak + apa yang terlihat):

| Kamera | Harus terlihat |
|---|---|
| C1 START | Gerbang candi di tengah atas bingkai sebagai landmark; galian di depan; garis polisi dan mobil di dekat kamera |
| C2 Bibir galian | Undakan turun ke dasar galian; ram timur; dasar galian (titik bangkit Jerangkong) |
| C3 Gerbang ke timur | Jalan proyek dan truk derek di kanan; galian di bawah; jalan akses di kejauhan |
| C4 Mata Jayadwara | Galian kecil di bawah; **desa di kiri, sawah di kanan**; kesan "rumah seperti mainan" |
| C5 Tampak atas | Tata letak sama dengan denah `docs/30` (utara di atas) |
| C6 Dari sawah | Bukit dan candi di atas, siluet di langit senja |

### M7 — Uji skala oleh developer + laporan akhir
- `Hermes/Tools/maps_ep1_70_rute.py`: hitung panjang rute Aksa di permukaan medan (START → CLUE_1 → turun ram timur → CLUE_2 → ram utara → kaki tangga → tangga → CLUE_3, sampel tiap 1 m dengan tinggi `elev`) dan perkiraan waktu jalan pada `MaxWalkSpeed` Aksa 500 cm/s. Cetak per ruas dan total.
- Tulis di laporan **daftar uji untuk developer** (jangan diisi sendiri):
  1. Play (PIE) di `Test_Hermes_MapsEp1`: muncul di START menghadap gerbang?
  2. Jalan sebagai Aksa ke ★1 → ★2 → ★3: catat waktu; undakan bisa dilewati lewat ram; tangga bisa dinaiki.
  3. Tekan **T** di halaman candi (dekat `JAYADWARA_Mulai`): Jayadwara2 45 m muncul tanpa tersangkut. Jalan ke mulut galian lalu ke sawah dan ke desa: apakah arena terasa cukup luas? Desa terasa jauh dari galian?
  4. Bandingkan render C1–C6 dengan gambar konsep: mana yang sesuai, mana yang perlu digeser.
- `python -I Tools/hermes_cek_sandbox.py` LULUS → commit → `git push -u origin hermes/maps_ep1`. **Selesai, jangan merge.**
- **Gate developer:** hasil uji 1–4 diisi developer di laporan. Koreksi angka dikerjakan Claude di `Art/Level/` (bukan olehmu).

---

## 4. Ringkasan bukti yang wajib ada di laporan

| Langkah | Bukti |
|---|---|
| M0 | Keluaran `ep01_medan.py` (`SEMUA LULUS`) |
| M1 | Tabel 43 objek + temuan selisih tanah |
| M2 | Jumlah vertex, tabel 12 titik uji (mesh vs `elev`), `Render/M2_atas.png`, `Render/M2_miring.png` + uraian per bagian |
| M3 | Bounds medan, tabel line trace 12 titik, output cek sandbox, screenshot |
| M4 | Tabel alas actor vs hitungan, jumlah tag `hancur`, 3 screenshot |
| M5 | Jumlah actor per jenis, tinggi PlayerStart, screenshot tampak atas |
| M6 | 6 PNG + tabel cocok/tidak per kamera |
| M7 | Panjang dan waktu rute per ruas, daftar uji developer (kosong), output cek sandbox terakhir |

## 5. Setelah selesai (untuk developer dan Claude)

1. Developer mengisi uji M7 di editor WORKTREE (atau checkout `hermes/maps_ep1`).
2. Kalau dipakai, Claude me-review (CLAUDE.md "Hasil kerja Hermes"), memindahkan logika skrip ke `Tools/ue_greybox_ep01.py` (membaca `Art/Level/ep01_layout_v01.json` yang sama), dan level greybox dibangun ulang di `/Game/Jayadwara/Maps/` lewat PR. Aset `.uasset`/`.umap` sandbox tidak dipindah mentah.
3. Koreksi tata letak dari hasil uji → Claude memperbarui `Art/Level/` + `docs/30` → Hermes atau Claude menjalankan ulang skrip M2–M6.
