# Menara air besi (D7)

| | |
|---|---|
| **Episode** | 1 (adegan 7) |
| **Fungsi** | Bangunan desa yang **bisa hancur**; tinggi sehingga terbaca dari kamera raksasa; roboh = air tumpah (VFX) |
| **Prioritas** | **Ep 1**: greybox F1 (Iterasi 7), final F2 |
| **Ukuran** | 4 × 4 × 15 m ([30 bagian 4](../../../docs/30-desain-level-ep01.md#4-daftar-bangunan-dan-prop-arena)) |
| **Rig** | Tidak. Static mesh → Geometry Collection |
| **Sumber** | [30](../../../docs/30-desain-level-ep01.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Rangka besi siku cukup balok persegi; batang silang diagonal dibuat sebagai balok, bukan kabel tipis.
- Tangga panjat boleh dihilangkan atau dibuat satu balok datar dengan tekstur anak tangga.
- Tangki dan rangka dipisah supaya saat roboh tangki jatuh utuh (spawn VFX air).

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a rural Indonesian village water tower about 15 meters tall. A square steel lattice frame 4 meters wide made of four thick vertical angle-steel legs with horizontal beams and X-shaped diagonal braces every 3 meters, painted faded gray with rust streaks. On top, a square platform with a simple railing and a large cylindrical water tank of blue-painted steel with a flat conical lid. A straight vertical ladder on one side.

Shape: thick readable beams, no thin wires or cables, simple cylinder tank.

Important: no text, no people, no plants, no pipes running to the ground.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/menara_air_v01.png`, potong per view. Target UE: `SM_MenaraAir` → versi fracture di Iterasi 7.
