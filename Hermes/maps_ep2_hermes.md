# Maps Ep 2 (greybox Kampung Kali v02) — Instruksi Kerja untuk Hermes

> Dari Claude, untuk Hermes. **File ini read-only bagimu**; progres ditulis di `Hermes/Laporan/YYYY-MM-DD-maps_ep2.md`.
> Baca dulu `AGENTS.md` sampai habis (terutama §0 Cara kerja, §1 Git, §2 Sandbox, §3 Unreal, §5 Blender), lalu skill `Hermes/skills/jd-mulai-tugas`, `jd-blender-skrip`, `jd-unreal-sandbox`, `jd-selesai-tugas`. Kalau ada beda, `AGENTS.md` menang atas file ini.
> Desain yang dibangun: [`docs/31-desain-level-ep02.md`](../docs/31-desain-level-ep02.md) **bagian 2a (tata letak v02)**. Visual: `docs/visual/ep02-kampung-kali.html` (buka di browser) dan pratinjau tampak atas yang kamu buat sendiri di MK0 (`Hermes/Art/maps_ep2/Render/MK0_pratinjau.png`).
> Pola kerja sama dengan Maps Ep 1 ([`maps_ep1_hermes.md`](maps_ep1_hermes.md) + [`maps_ep1_v02_hermes.md`](maps_ep1_v02_hermes.md)). Kalau kamu sudah mengerjakan Ep 1, skripnya boleh disalin dan disesuaikan; **semua angka dan aturan di file ini yang berlaku untuk Ep 2**.
> Versi: 16 Okt 2026. **Jalur paralel Level/Map** (keputusan developer 16 Okt 2026); greybox Ep 2 dimajukan atas permintaan developer (Ep 2 sendiri tetap Fase 4). Tulis kalimat itu di laporan.

---

## 0. Ringkasan

Bangun **greybox** map Episode 2 `Ep02_KampungKali` di Unreal: medan landai dari jalan raya turun ke kali, kampung padat dengan gang sempit dan **atap yang bisa dinaiki**, kali + anak kali + pintu air, jembatan gantung kuning, jalan layang, stasiun + rel, gudang Adikara, kampung seberang, lapangan bola + sawah selatan, penanda gameplay, zona meter, batas arena, dan 8 kamera dengan render PNG. Semua **kotak dan warna datar**. Tujuannya supaya developer bisa **memainkan** map ini sebagai Aksa (1,75 m; kejar-kejaran di gang dan atap) dan Jayadwara2 (45 m; arena ±1340 × 930 m) untuk menilai skala.

Bedanya dengan Ep 1: **rumahnya ribuan**. Hampir semua rumah dibangun sebagai **Instanced Static Mesh (ISM) per kelompok**, bukan actor per rumah. Hanya rumah yang punya peran (blok Chaos, atap bertanda, rumah petunjuk) yang jadi actor sendiri.

**Semua angka sudah ditentukan.** Kamu tidak mengarang posisi, ukuran, atau tinggi. Sumbernya file read-only:

| File (read-only) | Isi |
|---|---|
| `Art/Level/ep02_medan_v02.py` | `elev(x, y)` (tinggi medan, meter), `zona_material(x, y)` (slot medan), konstanta area, `TITIK_UJI` (14 titik). Uji: `python -I Art/Level/ep02_medan_v02.py` → `SEMUA LULUS` |
| `Art/Level/ep02_layout_v02.json` | 145 objek, 8 kelompok ISM (1.817 item), 258 pohon (5 kelompok), 55 tiang, 23 penanda, 5 zona, batas arena, 8 kamera, 3 cahaya, `mi_warna`, `rute_investigasi`, `rute_kejar`. **Dibuat** oleh `Art/Level/buat_layout_ep02_v02.py` |
| `Art/Level/pratinjau_ep02_v02.py` | Menggambar pratinjau tampak atas dari JSON (butuh Pillow). **Acuan** render MK2 dan C5, dibuat di MK0 |

Ada yang terasa salah di data (objek melayang, menembus, gang tertutup, atap tidak tersambung)? **Jangan ubah file di `Art/Level/`.** Tulis di laporan bagian "Usulan perubahan di luar sandbox" dengan angka dan screenshot. Claude yang memperbaiki lewat generator.

### Tidak dikerjakan di tugas ini
- **Landscape UE**: medan adalah static mesh dari Blender.
- **Chaos / Geometry Collection** dan sistem tukar puing: bangunan cukup kotak/ISM bertag (`blok_chaos`, `tukar_puing`). Diganti nanti.
- **C++ apa pun**, AI tuyul, rute kabur (`AJDFleeRoute`), umpan, meter sinkronisasi.
- Simulasi air, kereta yang bergerak, mobil fisika, foliage art, material realistis, NPC warga.
- Menjalankan `Tools/ue_setup_*`, `ue_import_*`, `ue_test_*`, `ue_capture_*`, `ue_probe_*` (AGENTS.md §3).

---

## 1. Persiapan (sekali)

```
cd C:\repository\unreal_engine\jayadwara
git fetch origin development
git worktree add C:\repository\unreal_engine\jayadwara_hermes_maps_ep2 -b hermes/maps_ep2 origin/development
cd C:\repository\unreal_engine\jayadwara_hermes_maps_ep2
git lfs pull
```
- **WORKTREE** = `C:\repository\unreal_engine\jayadwara_hermes_maps_ep2`. Semua perintah dijalankan dari sini.
- **Branch** = `hermes/maps_ep2` (dari `development`, **bukan** dari branch Ep 1-mu).
- Editor: buka `WORKTREE\Jayadwara.uproject` (editor terpisah dari developer dan worktree Hermes lain). Pertama kali minta compile C++ → Yes.
- `ue_remote.py` hanya terhubung ke editor dari folder yang sama. "Editor tidak ditemukan" → buka editor WORKTREE ini dulu; **jangan** `--any-editor`.
- `blender` = path lengkap `blender.exe` Blender 5.2, **headless** (AGENTS.md §5). Jangan pakai MCP Blender.
- `Art/Level/ep02_medan_v02.py` dan `Art/Level/ep02_layout_v02.json` harus ada. Tidak ada → PR data Ep 2 belum masuk `development`: **berhenti dan lapor**.

### Nama & lokasi (pakai persis)
| Apa | Path |
|---|---|
| Folder aset UE (`DEST`) | `/Game/Hermes/MapsEp2` (= `Content/Hermes/MapsEp2/`) |
| Level greybox | `/Game/Hermes/MapsEp2/Maps/Test_Hermes_MapsEp2` |
| Mesh medan | `/Game/Hermes/MapsEp2/Meshes/SM_Ep02_Medan` |
| Material | `/Game/Hermes/MapsEp2/Materials/M_Hermes_Greybox` + `MI_Ep02_<Nama>` (master **dibuat baru di folder ini**; jangan merujuk aset `MapsEp1`, karena branch Ep 1 tidak ada di worktree ini) |
| Skrip | `Hermes/Tools/maps_ep2_<NN>_<nama>.py` |
| Blender, ekspor, render | `Hermes/Art/maps_ep2/` (`maps_ep2_medan_v02.blend`, `Export/`, `Render/`) |
| Laporan | `Hermes/Laporan/YYYY-MM-DD-maps_ep2.md` (format AGENTS.md §8) |
| Commit | `[hermes] maps_ep2 MK<n> <ringkas>` |

---

## 2. Konvensi data (wajib dipahami sebelum menulis skrip)

### Koordinat
- Meter: `x` = timur, `y` = utara, `z` = atas. **`z = 0` = muka air kali** (dasar kali −1,5; jalan raya +9). Titik nol dekat pos RT.
- **Ke UE (cm):** `UE_X = x * 100`, `UE_Y = -y * 100`, `UE_Z = z * 100`. Tampak atas UE = utara di atas, sama dengan denah `docs/31`.
- `"yaw"` (derajat, berlawanan jarum jam dari atas, 0 = timur) → yaw UE = `-yaw`.
- `"hadap_ke"` / `"lihat_ke"`: hitung di koordinat UE: `yaw = degrees(atan2(UE_Y_t - UE_Y, UE_X_t - UE_X))`, pitch dari selisih Z dan jarak datar.

### Ketinggian
- Objek/item **tanpa `"z"`**: alas = `elev` **terendah** di tapak (sampel 5 × 5 titik di dalam persegi tapak setelah rotasi, sama dengan fungsi `alas()` di generator). Terbenam sedikit di sisi miring itu wajar.
- **`"z"` = tinggi alas absolut** (papan antar-atap, jembatan, dermaga, menara pintu air, permukaan air, latar).
- `"z_dasar_relatif"`: ditambahkan ke alas otomatis (tangki menara air di atas tiangnya, tajuk beringin).
- `"ukuran": [P, L, T]` = panjang (sumbu x sebelum rotasi), lebar (y), tinggi (z), meter.

### Jenis objek (`objek`)
| `jenis` | Cara membangun |
|---|---|
| `kotak` | `/Engine/BasicShapes/Cube` diskala `P, L, T`; lokasi Z = alas + T/2 |
| `rumah` | Dinding `P × L × (T − 0,5)` + atap pelat `(P + 0,4) × (L + 0,4) × 0,5` di atasnya. Dinding pakai `mi`, atap pakai `mi_atap`. Satu actor induk + 2 komponen (label `<id>`) |
| `bidang` | `/Engine/BasicShapes/Plane` diskala `P × L`; dengan `"z"` di tinggi itu (air), tanpa `"z"` 5 cm di atas tanah |
| `dinding` | Kotak tipis dari `dari` ke `ke`, tinggi `tinggi`, tebal `tebal` |
| `kerucut` | `/Engine/BasicShapes/Cone` diskala `[diameter, diameter, tinggi]` (tajuk beringin) |

### Kelompok instanced (`kelompok`, 8 kelompok, 1.817 item)
- **Satu actor per kelompok** (label = `id`, folder = awalan id), berisi ISM. `item` = `[x, y, P, L, T, yaw]`.
- `bentuk: "rumah"` → **dua ISM**: `Dinding` (Cube, `P × L × (T − 0,5)`, `mi`) dan `Atap` (Cube, `(P + 0,4) × (L + 0,4) × 0,5`, `mi_atap`). Jumlah instance kedua ISM sama.
- `bentuk: "kotak"` → satu ISM Cube `P × L × T`, `mi`.
- `"z"` di kelompok = alas absolut semua item (`LAYANG_Pilar` z 9, `LAYANG_Dek` z 22,5). Tanpa `"z"` → alas otomatis per item.
- Collision ISM **BlockAll** (atap harus bisa dipijak Aksa dan Jayadwara).
- Tag actor dari field kelompok (lihat bawah). Instance ISM tidak punya tag sendiri; itu benar.

### Tag actor
| Field di data | Tag UE |
|---|---|
| `"hancur": true` | `hancur` |
| `"penalti": "tinggi" / "normal" / "tanpa"` | `penalti_tinggi` / `penalti_normal` / `tanpa_penalti` |
| `"blok_chaos": "BLOK3"` | `blok_chaos` + `BLOK3` (8 deret × 4 rumah = satu Geometry Collection nanti, F2) |
| `"tukar_puing": true` (kelompok) | `tukar_puing` |
| `"atap_naik": true` | `atap_naik` (atap bertanda yang bisa dinaiki, F5) |
| `"milik": "Adikara"` | `adikara` |
| `"curian": true` | `curian` (mobil/gerobak yang dicuri boss, tidak dihitung meter) |
| `"tanpa_tabrakan": true` | (bukan tag) collision **NoCollision** |
| `hancur` tidak ada / false | tanpa tag `hancur` (musala, jembatan rel, menara pintu air, pos RT) |

- **Label actor** = `id` persis. **Folder Outliner** = awalan id sebelum `_` (`KAMPUNG`, `BLOK1`…`BLOK8`, `ATAP`, `JALAN`, `PASAR`, `GUDANG`, `REL`, `STASIUN`, `BANTARAN`, `AIR`, `PINTUAIR`, `JEMBATAN`, `SELATAN`, `LATAR`, `SEBERANG`, `BARAT`, `KOTA`, `LAYANG`, `POHON`, `TIANG`, `PENANDA`, `ZONA`, `BATAS`, `KAMERA`).

### Pohon dan tiang
- `pohon_kelompok` (5 kelompok): satu actor `POHON_<Kelompok>` dengan dua ISM: `Batang` (Cylinder Ø0,5 × 7 m, `MI_Ep02_Kayu`, BlockAll) dan `Tajuk` (Cone Ø7 × 8 m, alas 5 m di atas tanah, `MI_Ep02_Pohon`, NoCollision). Titik `[x, y, s]`: ukuran × `s`, alas = `elev(x, y)`.
- `tiang_listrik.titik`: satu actor `TIANG_Listrik`, ISM Cylinder Ø0,3 × 9 m, `MI_Ep02_Kendaraan`, BlockAll.

### Material greybox
`M_Hermes_Greybox`: parameter vektor `Warna` → Base Color, Roughness 0,9 (sama dengan Ep 1, dibuat ulang di `DEST/Materials`). **23 MI** dari `mi_warna` di JSON (sRGB 0–255 → linear saat diisi ke parameter): `MI_Ep02_<Nama>`.
- **8 slot medan** (nama slot mesh = nama MI tanpa awalan): `Air`, `Rel`, `Jalan`, `Gudang`, `Paving`, `Kampung`, `Bantaran`, `Sawah`.
- **15 untuk objek**: `Rumah`, `Atap`, `AtapNaik` (oranye, atap yang bisa dinaiki harus langsung terbaca), `Kota`, `Layang`, `Adikara`, `Alat`, `Kayu`, `Kendaraan`, `Mobil`, `Musala`, `JembatanKuning`, `Lapangan`, `Pohon`, `Penanda`.

---

## 3. Langkah MK0–MK7

Satu langkah → cek → catat di laporan → commit. Gagal 3× → berhenti dan tulis (AGENTS.md §0.5).

### MK0 — Persiapan
- Worktree, branch, editor (bagian 1). Buat laporan dari templat AGENTS.md §8.
- Jalankan:
  ```
  python -I Art/Level/ep02_medan_v02.py
  python -I Art/Level/buat_layout_ep02_v02.py
  git status
  ```
  Generator menulis ulang JSON yang sama; `git status` **harus tetap bersih**. Tidak bersih → lapor (data di repo beda dengan generator), jangan commit JSON-nya.
- Pratinjau acuan: `python -I Art/Level/pratinjau_ep02_v02.py Hermes/Art/maps_ep2/Render/MK0_pratinjau.png`. **Selalu beri path keluaran di sandbox**; tanpa argumen skrip menulis ke `docs/visual/` (di luar sandbox). Pillow belum terpasang (`ModuleNotFoundError: PIL`) → berhenti dan minta developer memasangnya; jangan memasang paket sendiri.
- **Lulus:** medan mencetak 15 baris `OK` lalu `SEMUA LULUS`; generator mencetak
  `objek 145 (hancur 90, tanpa penalti 19, blok Chaos 8 x 4 rumah, atap naik 27, papan 7)`,
  `kelompok KAMPUNG_RumahInti 810, BARAT_Rumah 181, SEBERANG_Rumah 581, JALAN_Ruko 62, KOTA_Blok 93, LAYANG_Pilar 23, LAYANG_Dek 22, GUDANG_Kontainer 45`,
  `pohon 258, tiang 55, penanda 23, zona 5, kamera 8`,
  `rute investigasi … 560 m`, `rute kejar … 1266 m`, dan `SEMUA LULUS`; `MK0_pratinjau.png` (1400 × 1000 px) ada. Tempel keluarannya dan gambarnya di laporan.

### MK1 — Cek data layout
- `Hermes/Tools/maps_ep2_11_cek_layout.py` (Python biasa, `-I`): baca JSON, impor `ep02_medan_v02` (tambahkan `Art/Level` ke `sys.path`), cetak tabel objek: id, jenis, pos, alas (m), selisih tanah di tapak; dan ringkasan per kelompok (jumlah item, alas min/maks).
- **Lulus:**
  - jumlah sama dengan MK0; penanda per jenis: 1 `PlayerStart`, 15 `titik`, 7 `area`
  - tag per penalti di objek: `tinggi` 61, `normal` 10, `tanpa` 19; `milik Adikara` 11; `curian` 6
  - alas: `KAMPUNG_PosRT` 7,85; `KAMPUNG_Musala` 7,22; `GUDANG_Gudang1` 6,00; `BANTARAN_Gubuk1` 3,50; `SELATAN_SUTET1` 3,00 (± 0,02)
  - **puncak atap bertanda** (`ATAP_Naik*`: alas + 3,5) ada di 9,97 … 11,45 m, dan tiap `ATAP_Papan*` (z + 0,15) selisih ≤ 0,6 m dari puncak atap `ATAP_Naik*` terdekat (papan harus bisa dilewati)
  - temuan selisih tanah > 2 m dicatat; yang sudah diketahui: `STASIUN_Peron` ±2,9 m (berdiri di kaki tanggul rel), boleh

### MK2 — Medan di Blender (headless)
- `Hermes/Tools/maps_ep2_20_medan_blender.py`, jalankan:
  `blender --background --factory-startup --python Hermes/Tools/maps_ep2_20_medan_blender.py -- --out Hermes/Art/maps_ep2`
- Isi:
  1. Grid `x` −700…700, `y` −600…400, sel **2,5 m** → **561 × 401 = 224.961 vertex**; tinggi = `elev(x, y)`.
  2. Slot per muka = `zona_material` di titik tengah muka (8 slot, bagian 2).
  3. Simpan `maps_ep2_medan_v02.blend`; ekspor `Export/SM_Ep02_Medan.fbx` (meter → cm di UE, lihat MK3).
  4. Render `Render/MK2_atas.png` (ortografis dari atas, utara di atas, warna slot dari `mi_warna`) dan `Render/MK2_miring.png` (dari barat daya, ±35° ke bawah, menghadap kampung).
- **Lulus:** jumlah vertex 224.961; tinggi mesh di **14 titik uji** = `elev` ± 0,05 m (cetak tabel); `MK2_atas.png` cocok dengan `MK0_pratinjau.png`. Uraikan per bagian: jalan raya lurus di utara; blok kota di atasnya; tanggul rel di barat dengan **3 celah** (jalan raya, kali, jalan inspeksi); kampung inti di tengah dan kampung pinggir barat; tanggul + bantaran; kali timur–barat; anak kali ke selatan di x −505; kampung seberang; lahan kosong timur; lapangan + sawah selatan; lot gudang diratakan di timur.

### MK3 — Level UE + medan
- `Hermes/Tools/maps_ep2_30_level.py` (diawali `DEST = "/Game/Hermes/MapsEp2"`), jalankan `python Tools/ue_remote.py Hermes/Tools/maps_ep2_30_level.py`:
  1. Level baru dari `/Engine/Maps/Templates/Template_Default` → `DEST/Maps/Test_Hermes_MapsEp2`. Hapus lantai bawaan.
  2. Impor `SM_Ep02_Medan.fbx` ke `DEST/Meshes` (tanpa Nanite, tanpa LOD otomatis), collision **Use Complex as Simple**.
  3. Buat `M_Hermes_Greybox` + 23 MI (bagian 2), pasang ke 8 slot medan.
  4. Medan di (0, 0, 0). World Settings: **GameMode Override = `/Game/Jayadwara/Core/BP_JDGameMode`** (hanya dirujuk, tidak diubah; tombol **T** = berubah ke Jayadwara2).
  5. DirectionalLight = cahaya `siang`.
  6. Simpan level dan aset `DEST` satu per satu. **Tidak pernah Save All.**
- **Lulus:** bounds medan 140.000 × 100.000 cm, Z −150 … 1.200 cm; line trace vertikal di 14 titik uji = `elev × 100` ± 5 cm (tabel); `python -I Tools/hermes_cek_sandbox.py` LULUS. Screenshot perspektif.

### MK4 — Objek, kelompok, pohon, tiang
- `Hermes/Tools/maps_ep2_40_objek.py` (objek tunggal) dan `maps_ep2_41_kelompok.py` (ISM, pohon, tiang). Pisahkan supaya bisa dijalankan ulang sendiri-sendiri; tiap skrip **menghapus actor buatannya dulu** (cari per folder) sebelum membangun ulang.
- **Lulus:**
  - 145 objek ada (rumah = satu actor); **alas actor = alas hitungan ± 5 cm** (dengan `"z"`: = `z` ± 5 cm)
  - tag: `hancur` 90; `penalti_tinggi` 61, `penalti_normal` 10, `tanpa_penalti` 19; `blok_chaos` 32 (BLOK1…BLOK8 masing-masing 4); `atap_naik` 27; `adikara` 11 objek + 1 kelompok; `curian` 6
  - `KAMPUNG_Musala`, `KAMPUNG_PosRT`, `REL_Jembatan*`, `PINTUAIR_*`, `JEMBATAN_*` **tanpa** `hancur`
  - 8 actor kelompok; jumlah instance = jumlah item (rumah: `Dinding` = `Atap`); total **1.817**
  - 5 actor pohon (258 batang = 258 tajuk), 1 actor tiang (55)
  - **gang utama terbuka**: line trace mendatar 1,0 m di atas tanah sepanjang x −26 dari y +138 ke y −48 **tidak mengenai apa pun**
  - Waktu skrip dan jumlah draw call (`stat RHI` di viewport, tampak C5) dicatat
- Screenshot (setinggi mata Aksa kecuali disebut): gang utama dari mulut gang; deret atap oranye T1 → T3 dari atas atap; jembatan gantung kuning dari bantaran; gudang Adikara dari dermaga; jalan layang dari jalan raya; **tampak 45 m** dari `JAYADWARA_Mulai` ke kampung.

### MK5 — Penanda, zona, batas
- `Hermes/Tools/maps_ep2_50_penanda.py`:
  1. `START` → **PlayerStart** di atas tanah, menghadap `hadap_ke` (jembatan gantung). Hapus PlayerStart bawaan.
  2. `titik` → **TargetPoint** + **TextRenderActor** (teks = `label`, huruf 150 cm, 3 m di atasnya). Dengan `"z"`: di tinggi itu (T4 di dek jembatan, T5 di puncak menara pintu air). Dengan `"di_atap": true`: line trace turun dari z 60 m, letakkan di titik kena pertama (puncak atap).
  3. `area` → silinder 0,2 m, radius `radius`, `MI_Ep02_Penanda`, **NoCollision**, + TextRender.
  4. `zona` → **TriggerBox** seukuran persegi, tinggi 60 m, label = id, TextRender 500 cm di tengah.
  5. `batas_arena` → 4 dinding tak terlihat tinggi 120 m (x −650…690, y −600…330), **Hidden in Game**, **BlockAll**; + 4 dinding sama di tepi medan (−700/700, −600/400).
- **Lulus:** 1 PlayerStart, 15 titik, 7 area, 5 zona, 8 dinding; PlayerStart Z = `elev(−40, 155) × 100` + setengah kapsul ± 10 cm (= 900 cm + kapsul); T1–T3 berada di atas atap oranye (Z ≥ 990 cm). Screenshot tampak atas semua penanda.

### MK6 — Kamera dan render C1–C8
- `Hermes/Tools/maps_ep2_60_kamera.py`: CameraActor per kamera (posisi = `pos` + `tinggi_di_atas_tanah` di atas permukaan **pertama yang kena line trace dari atas**, supaya C2 berdiri di atap), arah `lihat_ke`, FOV dari JSON. `C5_TampakAtas` ortografis, lebar 1.450 m, lurus ke bawah. DirectionalLight diset ke `cahaya` kamera (`siang`, `sore`, `keemasan`) sebelum render. SceneCapture2D 1920 × 1080 → `Hermes/Art/maps_ep2/Render/<id>_<cahaya>.png`.
- **Lulus:** 8 PNG, 1920 × 1080, rata-rata kecerahan > 20/255. Buka tiap PNG dan isi tabel (ya/tidak + apa yang terlihat):

| Kamera | Harus terlihat |
|---|---|
| C1 START mulut gang | Gang utama menurun lurus; **jembatan gantung kuning** di ujungnya sebagai landmark; mobil DWARA di dekat kamera |
| C2 Atap menuju T3 | Deret atap oranye bersambung dengan papan di atas gang; rumah biasa (abu) di kiri-kanan lebih rendah/terpisah |
| C3 Jembatan gantung ke pintu air | Bantaran memanjang ke barat; menara pintu air + tanggul rel di ujung |
| C4 Mata Jayadwara (45 m, keemasan) | Kampung padat setinggi mata kaki; gudang Adikara di timur jauh; kali sebagai jalur |
| C5 Tampak atas | Sama dengan `MK0_pratinjau.png` |
| C6 Dari lapangan bola | Kampung seberang di depan, kampung inti dan jalan layang di belakangnya; SUTET di samping |
| C7 Gudang Adikara | Gudang besar, pabrik + cerobong, kontainer; kali di kanan |
| C8 Jalan layang (45 m) | Dek jalan layang setinggi paha; ruko dan blok kota di utara; kampung di selatan |

### MK7 — Rute, daftar uji, laporan akhir
- `Hermes/Tools/maps_ep2_70_rute.py`: panjang `rute_investigasi` dan `rute_kejar` (sampel tiap 1 m; tinggi = permukaan pertama dari line trace, jadi bagian atap ikut terhitung). Target ±560 m dan ±1.266 m (± 3 %). Waktu pada 500 cm/s. Cetak per ruas.
- Daftar uji developer (jangan diisi sendiri):
  1. Play di `Test_Hermes_MapsEp2`: muncul di jalan raya menghadap gang; jembatan kuning terlihat dari mulut gang?
  2. Jalan ke ★1 lalu ★2 lewat gang: gang terasa sempit dan padat, tapi tidak tersesat? Catat waktu.
  3. Naik tangga bambu di rumah kemalingan, lari di atap oranye T1 → T3: lompatan antar-atap dan papan enak? Turun ke gang, ke jembatan gantung (T4), menyusur bantaran ke menara pintu air (T5). Catat waktu.
  4. Tekan **T** di lapangan tepi kali (`TRANSFORMASI`): Jayadwara2 muncul tanpa tersangkut? Berdiri di kali, lalu lari ke gudang Adikara: arena terasa cukup luas? Kampung terasa setinggi mata kaki? Jalan layang dan SUTET membantu rasa skala?
  5. Bandingkan render C1–C8 dengan `docs/visual/ep02-kampung-kali.html`: mana yang sesuai, mana yang perlu digeser.
  6. FPS di tampak C4 dan C5 (`stat fps`).
- Cek sandbox LULUS → commit → `git push -u origin hermes/maps_ep2`. **Selesai, jangan merge.**
- **Gate developer:** hasil uji 1–6 diisi developer di laporan. Koreksi angka dikerjakan Claude di `Art/Level/` (bukan olehmu).

---

## 4. Bukti wajib di laporan

| Langkah | Bukti |
|---|---|
| MK0 | Keluaran 3 perintah + `MK0_pratinjau.png` |
| MK1 | Tabel 145 objek, ringkasan 8 kelompok, cek alas, atap + papan, temuan |
| MK2 | 224.961 vertex, tabel 14 titik, `MK2_atas.png`, `MK2_miring.png` + uraian per bagian |
| MK3 | Bounds, tabel line trace 14 titik, cek sandbox, screenshot |
| MK4 | Tabel alas, jumlah tag, jumlah instance per kelompok (total 1.817), hasil trace gang utama, draw call, 6 screenshot |
| MK5 | Jumlah actor per jenis, tinggi PlayerStart dan T1–T5, screenshot tampak atas |
| MK6 | 8 PNG + tabel cocok/tidak |
| MK7 | Rute per ruas, daftar uji kosong, cek sandbox terakhir |

## 5. Setelah selesai (untuk developer dan Claude)

1. Developer mengisi uji MK7 di editor WORKTREE (atau checkout `hermes/maps_ep2`).
2. Kalau dipakai, Claude me-review (CLAUDE.md "Hasil kerja Hermes"), memindahkan logika skrip ke `Tools/ue_greybox_ep02.py` (membaca `Art/Level/ep02_layout_v02.json` yang sama), dan level greybox dibangun ulang di `/Game/Jayadwara/Maps/` lewat PR. Aset sandbox tidak dipindah mentah.
3. Koreksi tata letak dari hasil uji → Claude memperbarui `Art/Level/buat_layout_ep02_v02.py` + `docs/31` → skrip MK2–MK6 dijalankan ulang.
