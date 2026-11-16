# Rumah Kampung Kali (kit rumah padat)

| | |
|---|---|
| **Episode** | 2 (dibangun), dipakai ulang di Ep 4 dan 10 |
| **Fungsi** | Rumah padat di gang dan bantaran kali; atapnya dipakai untuk rute kejar-kejaran tuyul; rusak = penalti meter |
| **Prioritas** | Fase 4 |
| **Ukuran** | 1 lantai ±5 × 8 × 4,5 m; 2 lantai ±5 × 8 × 7,5 m; rumah panggung ±5 × 6 × 5,5 m (usulan) |
| **Rig** | Tidak. Static mesh; sebagian dirangkai jadi **blok Chaos** (deret 3–4 rumah), sisanya **tukar puing** ([31 bagian 4](../../../docs/31-desain-level-ep02.md#4-bangunan-dan-kerusakan)) |
| **Sumber** | [16 Ep 2](../../../docs/16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul), [28](../../../docs/28-struktur-level-episode.md#3-kit-distrik-dibangun-sekali-dipakai-ulang), [31](../../../docs/31-desain-level-ep02.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Kit = **3 mesh dasar** (1 lantai, 2 lantai, rumah panggung bantaran) × variasi atap (seng, genteng) dan warna cat ([31](../../../docs/31-desain-level-ep02.md#4-bangunan-dan-kerusakan)). Variasi atap dan cat dibuat di Blender/material, bukan prompt baru.
- **Atap harus bisa dinaiki** (rute tuyul): kemiringan landai, tanpa antena/kabel di atasnya di mesh dasar. Toren air, antena, jemuran ditambahkan sebagai prop terpisah.
- Lebar depan sempit (±5 m) supaya bisa dirangkai rapat jadi gang. Sisi samping polos tanpa jendela (menempel ke tetangga).

## Prompt 1: rumah 1 lantai

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a narrow single-story Indonesian urban kampung row house, about 5 meters wide, 8 meters deep and 4.5 meters tall. Plastered brick walls painted faded mint green with patches of exposed gray plaster, a low-slope gable roof of corrugated metal sheets with some rust, a narrow front terrace under a small roof overhang, a wooden front door, one window with simple iron bars, plain blank side walls with no windows so houses can stand wall to wall.

Shape: simple narrow box, gentle roof slope that a person could walk on, thick walls.

Important: no antennas, no cables, no water tanks, no laundry, no plants, no motorbikes, no signs, no people.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: rumah 2 lantai

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a narrow two-story Indonesian urban kampung row house, about 5 meters wide, 8 meters deep and 7.5 meters tall. Ground floor of plastered brick painted pale yellow, upper floor partly finished with unpainted gray cement render, a small front balcony with a simple iron railing on the upper floor, a single-slope roof of orange clay tiles, a wooden front door and a barred window on the ground floor, a window and balcony door on the upper floor, plain blank side walls with no windows so houses can stand wall to wall.

Shape: simple narrow stacked boxes, thick walls, simple roof.

Important: no antennas, no cables, no water tanks, no laundry, no plants, no motorbikes, no signs, no people.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 3: rumah panggung bantaran

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a small Indonesian riverbank stilt house, about 5 meters wide, 6 meters deep and 5.5 meters tall, raised 1.5 meters above the ground on nine thick square concrete-and-wood posts. Walls of weathered horizontal wooden planks painted faded blue mixed with a few plywood patches, a corrugated metal gable roof with rust, a small wooden front porch with a short wooden staircase, a wooden door and two wooden shutter windows.

Shape: simple box on thick posts, large readable planks, nothing thin or dangling.

Important: no antennas, no cables, no laundry, no plants, no boats, no signs, no people, no water.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/kampung_rumah_<a|b|c>_v01.png`, potong per view. Target UE: `SM_KampungRumah_1Lt`, `SM_KampungRumah_2Lt`, `SM_KampungRumah_Panggung` (+ mesh puing untuk tukar puing).
