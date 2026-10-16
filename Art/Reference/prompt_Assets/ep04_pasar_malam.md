# Pasar malam: kios + lampu pasar

| | |
|---|---|
| **Episode** | 4 (pasar Kampung Kali dibuka malam hari); kios tutup juga dipakai di Ep 2 dan 10 |
| **Fungsi** | Hub wawancara warga (area B) dan arena boss; banyak warga = meter paling sensitif sebelum Ep 6 |
| **Prioritas** | Fase 4 |
| **Ukuran** | Kios tenda ±3 × 3 × 3 m; kios permanen ±4 × 4 × 3,5 m; tiang lampu ±4 m |
| **Rig** | Tidak. Static mesh; kios tenda = tukar puing saat diinjak |
| **Sumber** | [16 Ep 4](../../../docs/16-panduan-arc-1.md#ep-4--lilin-di-pasar-malam--babi-ngepet), [28 Ep 4](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Kit Kampung Kali dirangkai ulang + **prop kios dan lampu pasar malam** ([28](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1)).
- Gerobak dorong dari [ep02_properti_curian.md](ep02_properti_curian.md) dipakai ulang.
- Dagangan cukup kotak/karung sederhana; tanpa teks dan merek.
- Lampu = material emissive; gambar dalam keadaan mati.

## Prompt 1: kios tenda

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a simple Indonesian night market stall, about 3 meters wide, 3 meters deep and 3 meters tall. A steel pipe frame with a pitched roof covered by a taut blue-and-white striped tarpaulin, a long wooden display table across the front covered with a plain cloth, a few closed wooden crates and burlap sacks stacked tightly under the table, a single bare light bulb fixture hanging short from the roof center.

Important: no text, no products with labels, no people, no cables, no loose hanging items.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: kios permanen

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a small permanent market kiosk in an Indonesian traditional market, about 4 meters wide, 4 meters deep and 3.5 meters tall. Plastered brick walls painted faded yellow, a corrugated metal single-slope roof, a wide front opening with a metal rolling shutter rolled up, a tiled concrete counter in front, a blank signboard above the opening, plain blank side walls so kiosks can stand wall to wall.

Important: no text on the sign, no products, no people, no cables.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 3: tiang lampu pasar malam

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a temporary night market light pole about 4 meters tall, a thick bamboo pole set in a concrete-filled bucket base, with a short horizontal wooden crossbar at the top holding three simple round lamp shades facing down, and a thick short cable wrapped tightly along the pole.

Important: lights off, no glow, no long hanging wires, no text.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/pasar_<kios_tenda|kios|lampu>_v01.png`, potong per view. Target UE: `SM_Pasar_KiosTenda`, `SM_Pasar_Kios`, `SM_Pasar_Lampu`.
