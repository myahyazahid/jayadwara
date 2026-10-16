# Jimat jenglot pecah

| | |
|---|---|
| **Episode** | 3 (clue ★ di ruang server gedung Adikara) |
| **Fungsi** | Petunjuk wajib: menunjukkan inti boss di dada jenglot |
| **Prioritas** | Fase 4 |
| **Ukuran** | Kotak ±25 × 15 × 30 cm |
| **Rig** | Tidak. Static mesh (versi utuh untuk flashback/kolektor + versi pecah) |
| **Sumber** | [16 Ep 3](../../../docs/16-panduan-arc-1.md#ep-3--lapar-listrik--jenglot) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Jenglot disimpan sebagai jimat dalam kotak kaca kecil. Di clue, **kotaknya pecah dan kosong** (makhluknya sudah keluar), jadi tidak perlu model jenglot kecil.
- Ukiran kayu generik, bukan simbol ritual nyata.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, wide empty space between views, shown large and centered.

Object: a small antique display case for a mystical talisman, about 30 centimeters tall. A dark carved teak wood base with a simple floral relief, a tall glass box on top with thin dark wood corner frames, and a small dark wood lid. The glass front is shattered with a large jagged hole, a few big glass shards lying on the base, and the inside is empty except for a small faded red cloth cushion.

Important: no creature inside, no blood, no glow, no text, no symbols.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/jimat_jenglot_v01.png`, potong per view. Target UE: `SM_JimatJenglot`, `SM_JimatJenglot_Pecah`.
