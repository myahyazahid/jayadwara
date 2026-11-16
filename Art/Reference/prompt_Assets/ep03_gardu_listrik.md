# Gardu listrik (objektif boss Ep 3)

| | |
|---|---|
| **Episode** | 3 (3 gardu di sudut arena); sistem objektif lingkungan dipakai ulang |
| **Fungsi** | **Objektif saat boss**: tiap gardu yang diputus membuat jenglot mengecil. Harus bisa diputus **tanpa meruntuhkan gedung di sampingnya** |
| **Prioritas** | Fase 4 |
| **Ukuran** | ±20 × 15 × 12 m (usulan; cukup besar untuk dicabut/dihancurkan tangan Jayadwara) |
| **Rig** | Tidak. Static mesh; 2 kondisi: utuh dan putus (mesh tukar + VFX percikan) |
| **Sumber** | [16 Ep 3](../../../docs/16-panduan-arc-1.md#ep-3--lapar-listrik--jenglot), [28 Ep 3](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Gardu induk kota versi ringkas dengan **titik interaksi jelas**: satu blok trafo besar di tengah yang bisa diangkat/dicabut, dikelilingi pagar. Bentuk = usulan Claude.
- Kabel tegangan tinggi antar-gardu = prop terpisah tanpa fisika.
- Energi Kala yang mengalir = VFX merah gelap, bukan di mesh.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a compact urban electrical substation in a city business district, about 20 meters long, 15 meters wide and 12 meters tall, on a concrete pad. In the center, one very large gray power transformer block with radiator fins on the sides and three tall white ceramic insulator bushings on top. Around it, two steel lattice gantry frames holding thick insulator strings, a few smaller gray switchgear cabinets, and a low concrete wall with a steel mesh fence around the perimeter with one gate.

Shape: big readable blocky transformer in the middle, thick lattice beams, cables drawn thick and short.

Important: no long overhead power lines leaving the frame, no text, no warning signs, no people, no glow.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/gardu_listrik_v01.png`, potong per view. Target UE: `SM_GarduListrik`, `SM_GarduListrik_Putus`.
