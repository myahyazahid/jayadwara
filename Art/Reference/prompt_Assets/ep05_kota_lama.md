# Kota Lama: gedung kolonial, museum, lampu jalan

| | |
|---|---|
| **Episode** | 5 (dibangun), dipakai ulang di Ep 7, 10, dan hub (museum di atas markas DWARA) |
| **Fungsi** | Deretan gedung kolonial di sekitar alun-alun (arena Ep 5, Ep 7); museum = eksterior hub |
| **Prioritas** | Fase 4 |
| **Ukuran** | Gedung kolonial ±20 × 15 × 14 m; museum ±40 × 25 × 18 m; lampu jalan ±4,5 m (usulan) |
| **Rig** | Tidak. Gedung kolonial → Chaos/tukar puing; museum **tidak** bisa hancur (hub) |
| **Sumber** | [16 Ep 5, 7](../../../docs/16-panduan-arc-1.md#ep-5--tali-yang-belum-dilepas--pocong-️), [28 Ep 5, 7, Hub](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Gaya Indische/kolonial Belanda khas kota tua Jawa (mirip Kota Lama Semarang, Kota Tua Jakarta), tapi **bangunan fiksi**.
- 2 varian gedung (Prompt 1 dan 2) + variasi cat di material cukup untuk deretan.
- Museum = bangunan khas dengan portiko kolom; markas DWARA ada di bawah tanah, jadi eksterior saja.

## Prompt 1: gedung kolonial A (kantor dagang)

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a two-story Dutch colonial era trading office building in an old Indonesian city, about 20 meters wide, 15 meters deep and 14 meters tall. Thick white plastered walls with faded patches, tall narrow wooden windows with dark green louvered shutters in a regular row on both floors, a central entrance with a semicircular arched top, a simple stepped decorative gable in the middle of the facade, a steep red clay tile hip roof behind it, a covered front arcade on the ground floor with thick square columns.

Shape: symmetrical, thick walls, clean repeating windows.

Important: no text, no signs, no plants, no vehicles, no people, no lamps.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: gedung kolonial B (ruko tua)

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a narrow two-story colonial era shophouse in an old Indonesian city, about 8 meters wide, 15 meters deep and 12 meters tall. Pale ochre plastered walls, a ground floor with three tall wooden folding doors painted dark brown, an upper floor with three tall windows with wooden shutters and a narrow cast-iron balcony, a decorative molded cornice, a red clay tile gable roof, plain blank side walls so units can stand wall to wall.

Shape: narrow tall box, thick walls, simple roof.

Important: no text, no signs, no plants, no vehicles, no people, no lamps.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 3: museum Kota Lama (eksterior hub)

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a grand neoclassical colonial era museum building in an old Indonesian city, about 40 meters wide, 25 meters deep and 18 meters tall. White plastered walls, a raised base with a wide flight of front stairs, a central portico with six tall white Doric columns holding a triangular pediment, two symmetrical wings with tall arched windows, a low hipped dark gray roof, a small square cupola in the center of the roof.

Shape: symmetrical, strong columns, clean classical proportions.

Important: no text on the pediment, no flags, no signs, no plants, no people.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 4: lampu jalan kolonial

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: an old cast-iron colonial style street lamp about 4.5 meters tall, painted dark green, with a thick fluted base, a slender pole, and a single four-sided glass lantern at the top with a small pointed cap.

Important: light off, no glow, no cables, no signs.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/kotalama_<gedung_a|gedung_b|museum|lampu>_v01.png`, potong per view. Target UE: `SM_KotaLama_GedungA`, `SM_KotaLama_GedungB`, `SM_KotaLama_Museum`, `SM_KotaLama_LampuJalan`.
