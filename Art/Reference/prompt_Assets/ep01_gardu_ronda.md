# Gardu ronda + kentongan (D8)

| | |
|---|---|
| **Episode** | 1 (adegan 7); dipakai ulang di desa episode lain |
| **Fungsi** | Bangunan desa kecil yang **bisa hancur**, untuk "kecelakaan" tak sengaja |
| **Prioritas** | **Ep 1**: greybox F1 (Iterasi 7), final F2 |
| **Ukuran** | 3 × 3 × 4 m ([30 bagian 4](../../../docs/30-desain-level-ep01.md#4-daftar-bangunan-dan-prop-arena)) |
| **Rig** | Tidak. Static mesh → Geometry Collection |
| **Sumber** | [30](../../../docs/30-desain-level-ep01.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Kentongan menggantung pendek di tiang depan; buat menempel ke tiang (tanpa tali panjang) supaya padat.
- Lantai panggung kayu (bale-bale) menyatu dengan rangka.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a small Indonesian village night-watch hut (gardu ronda), about 3 meters wide, 3 meters deep and 4 meters tall. Four thick square wooden posts, a raised wooden plank floor platform half a meter above the ground, a low wooden half-wall around three sides, open on the front, a simple gable roof of orange clay tiles. A traditional hollow wooden slit drum (kentongan) about 60 centimeters long fixed tight against the front right post.

Shape: thick posts and planks, simple roof, nothing thin or dangling.

Important: no text, no people, no lamps, no posters, no plants.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/gardu_ronda_v01.png`, potong per view. Target UE: `SM_GarduRonda` → versi fracture di Iterasi 7.
