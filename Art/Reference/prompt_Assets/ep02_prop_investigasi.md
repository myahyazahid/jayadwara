# Prop investigasi Ep 2: sesajen pesugihan + umpan tuyul

| | |
|---|---|
| **Episode** | 2 |
| **Fungsi** | Sesajen di gang belakang (clue ○, bestiary); umpan mainan dan yuyu (kepiting sawah) yang membuat tuyul berhenti sejenak |
| **Prioritas** | Fase 4 |
| **Ukuran** | Sesajen ±40 × 40 × 30 cm; mainan ±20–30 cm; yuyu ±10 cm |
| **Rig** | Tidak. Static mesh (yuyu cukup diam; kalau mau bergerak, animasi transform sederhana) |
| **Sumber** | [16 Ep 2](../../../docs/16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- **Sensitivitas budaya** ([06](../../../docs/06-referensi-mitologi.md#panduan-sensitivitas-budaya)): sesajen ditampilkan netral sebagai petunjuk, bukan diolok. Bentuk generik (nampan anyaman, bunga, dupa), bukan menyalin ritual tertentu.
- Mainan umpan = mainan tradisional murah (kincir, mobil-mobilan kayu); satu prompt berisi beberapa benda kecil.

## Prompt 1: sesajen

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, wide empty space between views, shown large and centered.

Object: a small traditional offering arrangement placed on the ground in a narrow alley, about 40 centimeters wide. A round woven bamboo tray holding a few banana-leaf folded containers, scattered red and white flower petals, a small clay cup, and two short incense sticks standing in a small clay holder. Simple and tidy.

Important: no smoke, no fire, no blood, no animals, no money, no text.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: umpan mainan + yuyu

```
Orthographic model reference sheet for a realistic 3D action game, a set of three separate small objects, each shown in FRONT, SIDE and TOP orthographic views, arranged in three rows with wide empty space between them, same scale.

Objects: (1) a simple handmade wooden toy car about 25 centimeters long painted red and yellow, with four round wooden wheels; (2) a traditional colorful paper-and-bamboo pinwheel toy about 30 centimeters tall on a thick bamboo stick; (3) a small brown freshwater rice-field crab (yuyu) about 10 centimeters wide, legs tucked close to the body, claws folded in front.

Important: no text, no brand, no hands holding them.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/sesajen_v01.png`, `umpan_tuyul_v01.png`, potong per view. Target UE: `SM_Sesajen`, `SM_UmpanMobilKayu`, `SM_UmpanKincir`, `SM_Yuyu`.
