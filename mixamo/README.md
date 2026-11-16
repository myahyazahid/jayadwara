# mixamo/ — tempat tukar file Mixamo (developer ↔ agent)

Folder ini supaya developer gampang generate animasi di [mixamo.com](https://www.mixamo.com) dan agent (Claude / Hermes) yang menyiapkan serta memindahkan filenya. **Bukan tempat file final.** Aturan ini berlaku untuk semua agent. File ini dikelola Claude, dan read-only untuk agent lain.

```
mixamo/
├── README.md     aturan ini
├── asset/        MENTAHAN: disiapkan agent, dipakai developer saat generate di Mixamo
│                 (DAFTAR_ANIMASI.md = daftar yang harus di-download + setting + nama file, gambar referensi pose,
│                  karakter untuk di-upload ke Mixamo kalau ada)
└── result/       HASIL: diisi developer (FBX hasil download Mixamo, sudah diganti nama sesuai daftar)
```

## Alur

1. **Agent → `asset/`.** Agent menulis `asset/DAFTAR_ANIMASI.md` berisi satu baris per animasi: peran, jurus (docs/07), kata kunci pencarian Mixamo, setting download, dan **nama file tujuan**. Gambar referensi pose ditaruh di `asset/ref/` (opsional).
2. **Developer → `result/`.** Developer generate dan download di Mixamo sesuai daftar, ganti nama file persis seperti kolom "nama file", lalu taruh di `result/`. Developer tidak perlu memindahkan apa pun ke tempat lain.
3. **Agent: cek, lalu pindahkan.** Agent memeriksa tiap file di `result/` (FBX valid, skeleton Mixamo `mixamorig:*`, durasi, fps, *In Place* atau tidak), mencatat hasilnya, lalu **memindahkan** file yang lulus ke folder yang dibutuhkan:

   | Siapa | Tujuan | Dibaca oleh |
   |---|---|---|
   | Claude (proyek utama) | `Art/Mixamo/<peran>.fbx` (Git LFS) | `Tools/ue_import_mixamo.py` |
   | Hermes (sandbox) | `Hermes/Art/<topik>/Mixamo/<peran>.fbx` | salinan skrip di `Hermes/Tools/` (lihat instruksi tugasnya) |

   File yang tidak lulus **tetap** di `result/`, dan alasannya ditulis di laporan supaya developer bisa download ulang.
4. Setelah dipindah, `result/` kosong lagi. Isi `result/` tidak di-commit (`.gitignore`), jadi hanya ada di folder kerja tempat developer menaruhnya.

## Setting download Mixamo (default)

| Untuk | Format | Skin | FPS | Lainnya |
|---|---|---|---|---|
| Karakter sumber, sekali saja: `ybot.fbx` | FBX Binary (.fbx) | **With Skin** | 30 | T-pose (karakter Y Bot bawaan Mixamo, tanpa animasi) |
| Tiap animasi | FBX Binary (.fbx) | **Without Skin** | 30 | Keyframe Reduction: none. Centang **In Place** kalau ada (gerak diatur kode). **Mirror** hanya kalau daftar bilang begitu |

Nama file: huruf kecil, sesuai kolom "nama file" di daftar (mis. `light_04.fbx`, `dodge_right.fbx`). Satu file = satu animasi.

## Lisensi

Animasi dan karakter Mixamo boleh dipakai di game komersial tanpa royalti. Yang tidak boleh adalah membagikan file mentahnya secara terpisah. Karena itu **repo harus tetap private**, dan FBX Mixamo hanya disimpan di `Art/Mixamo/` atau sandbox Hermes, tidak dirilis terpisah.
