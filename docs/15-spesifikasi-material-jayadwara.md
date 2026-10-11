# 15 — Spesifikasi Material & Tekstur Jayadwara

> Hasil **Iterasi 4** dari [13-rencana-model-jayadwara.md](13-rencana-model-jayadwara.md). Dipakai saat membuat `M_Jayadwara_Master` di Unreal (Iterasi 6). Di Blender, `Art/Scripts/08_materials.py` sudah membangun material yang **meniru** desain ini, jadi tampilannya bisa dicek sebelum UE terpasang.

## 1. Slot material & tekstur

| Slot | Isi | Ukuran | Texel density* |
|---|---|---|---|
| `M_Jayadwara_Armor` | Semua pelat merah + trim emas | 2048² | 508 px/m |
| `M_Jayadwara_Cloth` | Kain depan/belakang/selendang + garis tepi emas | 2048² | 1492 px/m |
| `M_Jayadwara_Body` | Undersuit, sarung tangan & jari, sol, kerah | 1024² | 340 px/m |
| `M_Jayadwara_Face` | Faceplate putih, mata & permata dada (emissive) | 1024² | 3608 px/m |

\* Pada skala model 1,9 m. UV: 1 layer `UVMap`, semua di 0–1, **0% tumpang-tindih** di keempat slot (diukur), padding 8 px.

Tiap slot punya set (`Art/Export/Textures/`):

| File | Isi | Import UE |
|---|---|---|
| `T_Jayadwara_<Slot>_Mask` | RGBA zona warna: **R** merah, **G** emas, **B** hitam, **A** putih | sRGB **off**, compression *Masks* |
| `T_Jayadwara_<Slot>_BC` | **Pengali** warna zona (putih = tidak berubah); kain: garis batik kawung | sRGB **on** |
| `T_Jayadwara_<Slot>_N` | Normal (OpenGL, +Y); kain: relief ornamen halus, lainnya datar | *Normalmap* + **Flip Green Channel** (UE memakai DirectX) |
| `T_Jayadwara_<Slot>_ORM` | **R** AO (bake Cycles), **G** roughness, **B** metallic | sRGB **off**, compression *Masks* |
| `T_Jayadwara_Face_Emit` | **R** emissive (mata + permata dada) | sRGB **off**, compression *Masks* |

## 2. Master material (`M_Jayadwara_Master`)

Warna = campuran zona oleh Mask → × BC → × AO. Parameter (nama sama dengan label node di material Blender):

| Parameter | Default | Catatan |
|---|---|---|
| `Color_Red` | `#A8262B` | Revisi: lebih hidup dari nilai mid docs/14 (yang tampak kusam di render) |
| `Color_Gold` | `#D6A33A` | Emas kuning-jenuh seperti konsep, **bukan silver** (revisi: lebih terang dari `#C8962E`) |
| `Color_Black` | `#2A2626` | Undersuit |
| `Color_White` | `#E2E0DE` | Faceplate |
| `Emissive_Color` | `#FFC86B` | Permata kuning-oranye bercahaya seperti konsep (mata `#FFF1C8`) |
| `Emissive_Intensity` | 3,0 | **KONSTAN** |

- Roughness = `ORM.G`, Metallic = `ORM.B` (emas 0,20 — gaya cat stylized; merah 0,36 rough; kain 0,80 rough).
- Cloth: **Two Sided**. Face: tambahkan `Emissive_Color × Emit.R × Emissive_Intensity` ke Emissive.
- Implementasi UE (Iterasi 5, `Tools/ue_import_jayadwara.py`): satu master untuk keempat slot; emissive dikalikan parameter `Emissive_Enable` (0 di Body/Armor/Cloth, 1 di MI Face). Two Sided kain lewat *Material Property Overrides* di `MI_Jayadwara_Cloth`. Normal map diimpor dengan **Flip Green** (sumber OpenGL).
- **Material Instance** per varian: `Color_*` berbeda (Dwarapala Kala/Kembar, recolor) tanpa mengubah model.

> **Aturan IP:** `Emissive_Intensity` untuk permata dada **tidak boleh dikaitkan ke meter Sync**, berkedip, atau dianimasikan sebagai timer ([08](08-requirement-produksi.md#art-direction)). Mata boleh konstan saja.

## 3. Alur hand-paint (kerjaan developer)

1. Cat di **BC** (pengali: gradien, edge wear, kotoran) dan, bila perlu, tambah detail ke **N** dan **ORM**. **Jangan ubah Mask** (zona warna dibaca dari sana); kalau butuh zona baru, koordinasikan dulu.
2. UV = sumber kebenaran. Kalau geometri berubah, jalankan ulang `07_uv_unwrap.py` — **ini mengubah tata letak UV dan membuat cat lama tidak cocok**. Selesaikan perubahan geometri sebelum mengecat.
3. `make_textures.py` **menimpa** semua tekstur di folder keluarannya. Setelah mulai mengecat, jalankan dengan folder lain: `python -I Art/Scripts/make_textures.py <npz> <folder_baru>`.

## 4. Catatan & keterbatasan

- **Kain** (revisi): merah polos + **ornamen emas di bagian bawah** (pita ganda, berlian bertingkat + titik, chevron) seperti konsep; panel depan/belakang crimson lebih gelap (BC 0,8). Motif kawung dihapus. Ornamen = geometris umum; tetap perlu review budayawan ([06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)).
- **AO**: bake Cycles 24 sample (jarak 6 cm), dihaluskan σ=1 px, dilunakkan (0,55 + 0,45·AO) karena AO penuh membuat merah kusam & berbintik.
- **Emas**: metalik 0,75 membuat emas cokelat gelap di render tanpa lingkungan → diturunkan ke 0,35, lalu 0,20 bersama warna yang lebih terang (gaya cat). Tuning ulang di UE dengan refleksi.
- **Marun** (`#422628`) belum dipakai pada geometri; disiapkan sebagai warna lapisan dalam kain bila diinginkan.
- Ukiran halus (ornamen dahi, bahu, gulungan) masih berupa geometri/garis timbul; detail ukir sebenarnya = tugas hand-paint (N + BC).
