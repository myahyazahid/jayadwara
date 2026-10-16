# Properti curian: mobil warga + gerobak dorong

| | |
|---|---|
| **Episode** | 2 (fase 1 boss: tuyul raksasa mencuri properti), dipakai ulang sebagai kendaraan jalanan di episode kota |
| **Fungsi** | Aktor fisika biasa yang diangkat/dibawa lari boss; pembanding skala |
| **Prioritas** | Fase 4; mobil kandidat kuat **Fab** |
| **Ukuran** | Mobil ±4,2 × 1,7 × 1,7 m; gerobak ±1,8 × 0,8 × 1,8 m |
| **Rig** | Tidak. Static mesh (roda boleh terpisah) |
| **Sumber** | [16 Ep 2](../../../docs/16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul), [31 bagian 4](../../../docs/31-desain-level-ep02.md#4-bangunan-dan-kerusakan) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- 3–4 mobil + 2 gerobak di jalan raya. Variasi warna mobil di material.
- **Tanpa merek nyata.**

## Prompt 1: mobil warga

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a generic compact seven-seat family MPV common on Indonesian streets, about 4.2 meters long, silver-gray paint, dark tinted windows, simple black plastic bumpers, plain grille with no emblem, ordinary steel wheels with black tires, slight dust on the lower body.

Important: no real car brand, no badges, no license plate text, no people inside.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: gerobak dorong pedagang

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: an Indonesian street food push cart (gerobak), about 1.8 meters long, 0.8 meters wide and 1.8 meters tall. A wooden box body painted bright red and white with a glass display case on top, a small flat roof on four thin wooden posts, two large bicycle-style wheels at the back, one small support leg at the front, two long wooden push handles.

Important: no text on the glass, no food, no people, no gas tank, no hanging items.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/mobil_warga_v01.png`, `gerobak_v01.png`, potong per view. Target UE: `SM_MobilWarga`, `SM_Gerobak` (gerobak dipakai ulang di pasar Ep 4).
