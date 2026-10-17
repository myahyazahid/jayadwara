# Daftar Animasi Mixamo — Combo Iterasi 2

Ini daftar animasi yang perlu di-download dari [mixamo.com](https://www.mixamo.com) buat ganti placeholder Mannequin di combo Aksa (Iterasi 2, `docs/07` "Daftar jurus"). Satu baris = satu file. Nama file harus **persis** seperti kolom "Nama file" (huruf kecil semua) — dari nama itu aku (Hermes) tahu file itu buat jurus apa.

Ada 19 file: **10 wajib** (Prioritas 1) dan **9 opsional** (Prioritas 2). `finisher_03.fbx` ditambahkan 17 Okt 2026 (keputusan developer, `docs/07`). Kalau cuma mau yang wajib dulu, kerjakan tabel Prioritas 1 saja, sisanya nanti.

## Langkah download (baca sekali)

1. Buka **mixamo.com**, login pakai akun Adobe (gratis).
2. Di tab **Animations**, pilih karakter **Y Bot** (bawaan Mixamo) di panel kanan.
3. Cari pakai kata kunci di kolom "Kata kunci" — coba berurutan, ambil yang geraknya paling mirip jurusnya. Kalau tidak ada yang persis, ambil yang paling dekat (lihat bagian paling bawah).
4. Klik animasinya, atur setting di panel kanan sesuai kolom "Setting khusus" + tabel setting default di bawah, lalu **Download**.
5. Format **FBX Binary (.fbx)**. Animasi: **Without Skin**. Khusus `ybot.fbx`: **With Skin**.
6. Ganti nama file persis seperti kolom "Nama file" (contoh: `light_04.fbx`, bukan `mixamo.com.fbx` dan bukan `Light_04.FBX`).
7. Taruh semua file langsung di folder ini (tanpa subfolder, jangan di-zip):
   `C:\repository\unreal_engine\jayadwara_hermes_combo\mixamo\result\`
8. Centang kolom ☐ jadi ☑ di tabel biar kelihatan mana yang sudah. Kalau satu animasi di-skip, tulis alasannya di bawah tabel.

## Setting default (dari `mixamo/README.md`)

| Untuk | Format | Skin | FPS | Lainnya |
|---|---|---|---|---|
| Karakter sumber, sekali saja: `ybot.fbx` | FBX Binary (.fbx) | **With Skin** | 30 | T-pose (karakter Y Bot bawaan Mixamo, tanpa animasi) |
| Tiap animasi | FBX Binary (.fbx) | **Without Skin** | 30 | Keyframe Reduction: **none**. Centang **In Place** kalau ada (gerak diatur kode). **Mirror** hanya kalau daftar bilang begitu |

Nama file: huruf kecil, sesuai kolom "Nama file". Satu file = satu animasi.

## Prioritas 1 — wajib (jurus yang disetujui 16 Okt)

| ☐ | Nama file | Jurus (docs/07) | Kata kunci Mixamo (coba berurutan) | Setting khusus | Kena (tulang, jumlah) |
|---|---|---|---|---|---|
| ☑ | `ybot.fbx` | Karakter sumber retarget | Pilih karakter **Y Bot**, tanpa animasi (T-pose) | **With Skin** | — |
| ☑ | `light_04.fbx` | Tendangan putar belakang (*dwi huryeo chagi*), akhir combo | Spinning Back Kick, Spin Kick, Mma Kick | In Place | kaki, 1 |
| ☑ | `finisher_01.fbx` | Tendangan belakang (*dwi chagi*) | Back Kick, Mule Kick | In Place | kaki, 1 |
| ☑ | `finisher_02.fbx` | Tendangan ganda melompat (*narae chagi*) | Double Kick, Jumping Double Kick, Martelo 2 | In Place | kaki, **2** |
| ☑ | `finisher_03.fbx` | **Finisher 3**: ringan ×3 lalu berat (animasi dipilih developer di Mixamo) | Spinning Back Kick, Jump Spin Kick, Flying Knee | In Place | — (kena area dari kode) |
| ☑ | `air.fbx` | Tendangan terbang memutar | Tornado Kick, Butterfly Kick, Jump Spin Kick | In Place | kaki, 1 |
| ☐ | `dodge_back.fbx` | Salto belakang | Back Flip, Backflip | In Place | — |
| ☐ | `dodge_left.fbx` | Guling / cartwheel ke kiri | Dodge Roll Left, Cartwheel, Side Roll | In Place | — |
| ☐ | `dodge_right.fbx` | Guling / cartwheel ke kanan | sama dengan kiri | In Place + **Mirror** kalau hanya ada versi kiri | — |
| ☐ | `dodge_forward.fbx` | Langkah cepat menunduk | Quick Step, Dodge Forward, Evade | In Place | — |

## Prioritas 2 — opsional (kalau mau semua placeholder diganti)

| ☐ | Nama file | Jurus | Kata kunci | Kena |
|---|---|---|---|---|
| ☑ | `light_01.fbx` | Jab, tangan kiri depan | Jab, Lead Jab | tangan, 1 |
| ☑ | `light_02.fbx` | Cross, tangan kanan | Cross Punch, Punching | tangan, 1 |
| ☑ | `light_03.fbx` | Hook, tangan kiri | Hook Punch, Left Hook | tangan, 1 |
| ☑ | `lunge.fbx` | Terjang: lompat kecil, tangan kanan dari atas ke dada | Superman Punch, Jumping Punch | tangan, 1 |
| ☑ | `back.fbx` | Pukul mundur: langkah mundur lalu jab | Step Back Punch, Retreat Jab | tangan, 1 |
| ☐ | `heavy.fbx` | Pukulan putar: badan diputar menjauh, lalu pukulan lurus keras | Spinning Punch, Power Punch, Haymaker | tangan, 1 |
| ☑ | `air_slam.fbx` | Hantaman ke bawah, berlutut | Ground Punch, Ground Slam | — (kena area dari kode) |
| ☐ | `parry_01.fbx` | Tepis luar | Block / Parry, Outward Block | — |
| ☐ | `parry_02.fbx` | Tepis dalam | Inward Block, Parry | — |

Setting Prioritas 2 sama: **Without Skin**, 30 FPS, Keyframe Reduction **none**, **In Place**.

## Kalau animasi yang dicari tidak ada

- Ambil yang geraknya paling mirip, **tetap pakai nama file dari tabel**, dan tulis di catatan bawah siapa nama asli animasi Mixamo-nya.
- `dodge_right.fbx`: kalau Mixamo tidak punya versi kanan, download versi kiri dengan centang **Mirror** di panel download, simpan sebagai `dodge_right.fbx`.
- Jangan download animasi yang **tidak** In Place (kecuali memang tidak ada pilihannya) — nanti aku catat jarak geser pinggulnya di laporan dan kamu yang putuskan perlu download ulang atau tidak.
- Semua file harus dari karakter **Y Bot** yang sama, jangan campur karakter lain (nama tulangnya beda, retarget-nya jadi tidak bisa satu rig).

## Sesudah download

Aku yang cek tiap FBX (1 armature `mixamorig`, ada Hips/Spine/LeftHand/RightFoot, ada action ≥ 10 frame, 30 fps, geser pinggul < 30 cm), lalu aku pindahkan yang lulus ke sandbox. Yang gagal tetap di `result/` dan alasannya aku tulis di `Hermes/Laporan/2026-10-17-combo-iter2.md`, jadi kamu bisa download ulang.

## Catatan (isi kalau ada yang di-skip / diganti)

- 17 Okt 2026 — Hermes sudah cek 12 file di `result/`: **semua lulus** (1 armature, 65 tulang `mixamorig:` sama persis dengan `ybot.fbx`, 30 fps, action ≥ 10 frame, ybot 180,5 cm + berskin). Angka lengkap: `Hermes/Art/combo-iter2/Log/cek_fbx.json`.
- **Belum ada file (7):** `dodge_back.fbx`, `dodge_left.fbx`, `dodge_right.fbx`, `dodge_forward.fbx`, `heavy.fbx`, `parry_01.fbx`, `parry_02.fbx`. Selama belum ada, jurus itu tetap pakai animasi placeholder/gerak kode.
- **Tidak In Place** (bukan gagal, tapi bikin karakter bergeser saat montage): `air.fbx` 210,7 cm, `air_slam.fbx` 383,4 cm, `light_04.fbx` 51,3 cm. Kalau mau rapi, download ulang dengan centang **In Place**.
- `finisher_03.fbx` = animasi pilihan developer sendiri (81 frame, 2,67 s), masuk ke `heavy_finishers[2]`.
