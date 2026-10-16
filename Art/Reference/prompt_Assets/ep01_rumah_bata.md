# Rumah bata genteng (D1–D4)

| | |
|---|---|
| **Episode** | 1 (adegan 7, arena boss); dipakai ulang di desa episode lain |
| **Fungsi** | Bangunan desa yang **bisa hancur**; runtuh = penalti meter sinkronisasi |
| **Prioritas** | **Ep 1**: greybox F1 (Iterasi 7), final F2 |
| **Ukuran** | 10 × 8 × 6 m ([30 bagian 4](../../../docs/30-desain-level-ep01.md#4-daftar-bangunan-dan-prop-arena)) |
| **Rig** | Tidak. Static mesh → Geometry Collection (pre-fractured) |
| **Sumber** | [18 C](../../../docs/18-kebutuhan-episode-1.md#c-lingkungan--level), [30](../../../docs/30-desain-level-ep01.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- **1 mesh dasar + 2 variasi atap** (D1–D4). Prompt 1 = atap pelana, Prompt 2 = atap limasan. Cat dinding divariasikan di material.
- Untuk fracture: dinding tebal (±20 cm) tertutup, atap, kusen, dan teras dipisah per bagian. **Interior tidak perlu**; jendela/pintu cukup gelap.
- Dilihat terutama dari kamera raksasa (±45 m), jadi siluet atap dan warna genteng lebih penting dari detail.

## Prompt 1: atap pelana

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a simple single-story rural Javanese village house, about 10 meters wide, 8 meters deep and 6 meters tall to the roof ridge. Plastered brick walls painted pale cream with a darker gray band along the bottom, a gable roof covered with orange-brown clay roof tiles, a small front porch under the roof overhang supported by two square wooden posts, a wooden front door painted green, two wooden windows with simple frames on the front, one window on each side wall, a low tiled floor platform one step above the ground.

Shape: clean rectangular volumes, thick walls, simple roof shape.

Important: no people, no vehicles, no plants, no laundry, no satellite dishes, no signs.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: atap limasan

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a simple single-story rural Javanese village house, about 10 meters wide, 8 meters deep and 6 meters tall to the roof ridge. Plastered brick walls painted pale blue-white with a darker gray band along the bottom, a traditional Javanese limasan hip roof with a short ridge, covered with dark red clay roof tiles, a front veranda with four thin square wooden posts, a double wooden front door, two wooden windows with simple frames on the front, one window on each side wall, a low tiled floor platform one step above the ground.

Shape: clean rectangular volumes, thick walls, simple roof shape.

Important: no people, no vehicles, no plants, no laundry, no satellite dishes, no signs.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/rumah_bata_a_v01.png` dan `rumah_bata_b_v01.png`, potong per view. Target UE: `SM_RumahBata_A`, `SM_RumahBata_B` → versi fracture di Iterasi 7.
