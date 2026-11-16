# Jembatan Kampung Kali (beton + bambu/gantung)

| | |
|---|---|
| **Episode** | 2 (dibangun), dipakai ulang di Ep 4 dan 10 |
| **Fungsi** | Jembatan beton = jalur warga mengungsi ke lapangan seberang; jembatan bambu/gantung = jalan pintas rute kejar-kejaran |
| **Prioritas** | Fase 4 |
| **Ukuran** | Beton ±24 × 6 m (lebar jalan 4 m); bambu ±12 × 1,5 m (usulan, lebar kali di level menyusul) |
| **Rig** | Tidak. Static mesh; jembatan beton **tidak** bisa hancur (jalur evakuasi) |
| **Sumber** | [28 Ep 2](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1), [31](../../../docs/31-desain-level-ep02.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Panjang final mengikuti lebar kali di greybox [31](../../../docs/31-desain-level-ep02.md#koordinat-greybox-meter-y-utara); buat modular (bentang + pilar) supaya bisa dipanjangkan.
- Jembatan bambu: tali/kabel gantung dibuat sebagai tube tebal di Blender; gambar menampilkan rangka yang kokoh.

## Prompt 1: jembatan beton

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a small old concrete road bridge over an urban river in an Indonesian kampung, about 24 meters long and 6 meters wide, a flat concrete deck with a 4 meter wide road and narrow raised walkways on both sides, low solid concrete parapet walls painted white with faded black-and-white striped ends, two thick square concrete piers in the middle, weathered gray concrete with water stains.

Shape: simple long box deck on thick piers, symmetrical.

Important: no vehicles, no people, no signs, no lamps, no cables, no water.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: jembatan bambu gantung

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a narrow pedestrian footbridge over a kampung river, about 12 meters long and 1.5 meters wide. A deck of thick split bamboo slats laid across two long wooden beams, simple handrails made of thick bamboo poles on both sides, supported at each end by a sturdy A-shaped wooden frame and two thick steel cables sagging gently between the frames, with thick vertical hangers down to the deck.

Shape: readable thick bamboo and wood parts, cables drawn thick and simple.

Important: no people, no signs, no plants, no water.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/kampung_jembatan_<beton|bambu>_v01.png`, potong per view. Target UE: `SM_KampungJembatan_Beton`, `SM_KampungJembatan_Bambu`.
