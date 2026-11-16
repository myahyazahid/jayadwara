# Ruko jalan raya

| | |
|---|---|
| **Episode** | 2 (dibangun), dipakai ulang di Ep 3 (pinggir) dan 10 |
| **Fungsi** | Deretan rumah-toko di jalan raya seberang kali (`LI_KampungKali_JalanRaya`); bisa hancur = penalti meter |
| **Prioritas** | Fase 4 |
| **Ukuran** | 1 unit ±5 × 15 × 11 m (3 lantai; usulan) |
| **Rig** | Tidak. Static mesh → blok Chaos (deret 3–4 unit) |
| **Sumber** | [31 bagian 8](../../../docs/31-desain-level-ep02.md#8-kit-dan-pakai-ulang) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Satu unit dirangkai berderet; papan nama toko = decal kosong/teks fiksi di UE.
- Rolling door tertutup supaya tanpa interior.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: one unit of a typical Indonesian three-story shophouse (ruko), about 5 meters wide, 15 meters deep and 11 meters tall. Ground floor with a closed gray metal rolling shutter door and a small canopy above it, a blank rectangular signboard panel above the canopy, upper floors with a row of glass windows with aluminum frames and a small balcony with a simple railing, plain painted concrete facade in light beige, flat concrete roof with a low parapet, plain blank side walls so units can stand wall to wall.

Shape: simple tall box, clean facade grid, thick walls.

Important: no text on the sign, no air conditioners, no cables, no plants, no vehicles, no people.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/ruko_v01.png`, potong per view. Target UE: `SM_Ruko`.
