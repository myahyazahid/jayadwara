# 22 — Spesifikasi Material & Tekstur Aksa

> Hasil **Iterasi 5** dari [19-rencana-model-aksa.md](19-rencana-model-aksa.md). Tekstur **dasar** (dibuat skrip) supaya model sudah berwarna & berpermukaan; developer menimpa/mengecat di atasnya (kulit, lipatan, keausan). Pola kerja sama dengan Jayadwara ([15](15-spesifikasi-material-jayadwara.md)).

## 1. Slot, ukuran, texel density

| Slot | Isi | Ukuran | Density* | Tekstur |
|---|---|---|---|---|
| `Skin` | Kepala, leher, tangan, jari | 2048² | ±1280 px/m (kepala ±2,2×) | BC, N, ORM, SSS |
| `Eyes` | Sklera, iris, pupil (proyeksi planar, mata kiri/kanan berdampingan) | 512² | ±5900 px/m | BC, N (datar), ORM |
| `Hair` | Rambut, alis | 1024² | ±1350 px/m | BC, N, ORM |
| `Cloth` | Jaket, kaus, celana, kerah dalam & selendang batik | 2048² | ±720 px/m | Mask, BC, N, ORM |
| `Gear` | Boots, sarung tangan, sabuk, emas, kalung, batu | 1024² | ±590 px/m | BC, N, ORM |

\*Dari `make_textures_aksa.py` (rata-rata); bobot per bagian di `aksa_50_uv.py` (`DENS`). Padding 4–8 px.

Nama file: `T_Aksa_<Slot>_<BC|N|ORM|SSS|Mask>.png` (`Art/Export/Textures_Aksa/`). Di UE: `/Game/Jayadwara/Characters/Aksa/Textures/`.

## 2. Isi tekstur

- **BC** (sRGB): warna zona dari vertex color `AK_Zone` (palet [21](21-model-sheet-aksa.md)), diinterpolasi per piksel (bibir, bulu mata, iris, pupil ikut) + variasi halus. Iris: serat radial + cincin limbal; sklera: sedikit kemerahan di tepi. **Batik**: kawung gaya (lingkaran berpotongan + titik) cokelat-emas redup di atas `#5A3B2B` pada kerah dalam & selendang; skala motif 4,5 cm.
- **N** (OpenGL +Y): pori halus (kulit), anyaman benang (kain; kawung timbul), butiran kulit (boots/sarung tangan/sabuk), datar (mata, emas).
- **ORM**: R = AO (putih; dibaca dari `_bake/AO_<Slot>.png` bila ada), G = roughness per zona (kulit 0,55; kain 0,80–0,90; emas 0,30; kulit boots 0,55; mata 0,10), B = metallic (emas 1,0).
- **SSS** (Skin): 1 di kulit & bibir; dipakai Blender (Subsurface Weight). **Belum** dipakai di UE (butuh Subsurface Profile; Iterasi 6/polish).
- **Mask** (Cloth, RGBA): R jaket, G kaus, B celana, A batik. Untuk recolor/varian (Iterasi 7).

## 3. Material di Unreal

`M_Aksa_Master` (dibuat `Tools/ue_import_aksa.py`): `BC × AO` → Base Color, `N` → Normal, `ORM.G` → Roughness, `ORM.B` → Metallic; two-sided, skeletal mesh. Parameter tekstur: **BC, N, ORM**. Lima instance `MI_Aksa_<Slot>` mengisi tiga parameter itu dengan tekstur slotnya. Tekstur diimpor dengan pengaturan benar (BC sRGB; N Normalmap, non-sRGB; ORM/SSS/Mask non-sRGB).

- **Kornea mata:** di Blender memakai Coat (Principled). Di UE belum ada (master Default Lit); opsi: material Eyes terpisah dengan Clear Coat (Iterasi 6) — tetap 5 slot.
- Impor ulang **tidak menimpa tekstur yang sudah ada** (aman bagi hasil cat developer); untuk menimpa: `AKSA_RETEX=1`.
- `M_Aksa_Proxy` (warna dari vertex color, Iterasi 1) tidak lagi dipakai; asetnya boleh dihapus manual.

## 4. Pipeline

`aksa_22` → `aksa_30` → `aksa_40` → **`aksa_50_uv.py`** → `python -I Art/Scripts/make_textures_aksa.py` → **`aksa_51_materials.py`** (material Blender bertekstur, `aksa_v05_tex.blend`) → `aksa_13` → `aksa_14` → `validate_aksa.py --require-uv --require-morph 8` → `Tools/ue_import_aksa.py`.

Jangan jalankan ulang `aksa_50` / `make_textures_aksa` **setelah developer mulai mengecat** (UV/tata letak berubah → cat tidak cocok lagi).

## 5. Batas & catatan

- **UV kepala belum rapi untuk hand-paint**: `smart_project` memecah kepala jadi banyak island kecil (basis MPFB tidak membawa UV asli ke model). Cukup untuk warna dasar; untuk mengecat wajah sebaiknya unwrap ulang kepala manual (seam di belakang telinga/leher) di Blender sebelum mengecat. Kandidat perbaikan Claude: bawa UV asli basemesh MPFB (Iterasi 6).
- Cakupan atlas masih 35–55% (packer shelf sederhana); cukup untuk ukuran sekarang. Dinding tipis trim/tali (≈1% poligon) punya area UV nol (tekstur melar, tak terlihat).
- Tekstur belum di-bake AO; AO = putih (ambient occlusion hanya dari engine). Skrip `make_textures_aksa.py` sudah membaca `_bake/AO_<Slot>.png` bila disediakan.
- Motif batik: kawung (umum), **bukan** motif larangan keraton; tetap perlu review budayawan ([06](06-referensi-mitologi.md)).
- Morph target tidak boleh bernilai ≠ 0 saat export (nilai di-nol-kan otomatis oleh `aksa_14_export.py`).
