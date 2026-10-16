# Warung kayu/seng (D5–D6)

| | |
|---|---|
| **Episode** | 1 (adegan 7); dipakai ulang di desa/kota episode lain |
| **Fungsi** | Bangunan desa yang **bisa hancur**; paling mudah runtuh, banyak puing ringan |
| **Prioritas** | **Ep 1**: greybox F1 (Iterasi 7), final F2 |
| **Ukuran** | 6 × 5 × 4 m ([30 bagian 4](../../../docs/30-desain-level-ep01.md#4-daftar-bangunan-dan-prop-arena)) |
| **Rig** | Tidak. Static mesh → Geometry Collection |
| **Sumber** | [30](../../../docs/30-desain-level-ep01.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Papan kayu dan atap seng dipisah per lembar besar supaya runtuhnya "ringan" dan berhamburan.
- Tulisan papan nama warung = **decal kosong** atau teks fiksi di UE; gambar tanpa teks.
- Etalase/meja depan menyatu dengan dinding (padat). Barang dagangan tidak perlu dimodel.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a small Indonesian village roadside food stall (warung), about 6 meters wide, 5 meters deep and 4 meters tall. Walls of weathered horizontal wooden planks painted faded light blue, a single-slope roof of corrugated metal sheets with some rust patches, the front roof extending forward as an awning supported by two thin wooden poles. A wide front opening with a wooden counter, wooden shutter panels propped open above the counter, a blank wooden signboard above the opening, a long wooden bench in front attached to the wall.

Shape: simple box with a sloping roof, large readable planks and metal sheets.

Important: no text on the sign, no products, no people, no plants, no bottles, no hanging items.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/warung_v01.png`, potong per view. Target UE: `SM_Warung` → versi fracture di Iterasi 7.
