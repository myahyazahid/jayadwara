# Pelabuhan Utara: gudang, derek, peti batu

| | |
|---|---|
| **Episode** | 9 (dibangun), dipakai ulang di Ep 10 (opsional) |
| **Fungsi** | Kompleks gudang = area penyusupan; **derek pelabuhan** = bentuk yang ditiru genderuwo saat menyamar (fase 2); peti batu = clue ○ (petunjuk arca kedua) |
| **Prioritas** | Fase 4 |
| **Ukuran** | Gudang ±40 × 25 × 12 m; derek kontainer ±30 × 25 × 50 m (usulan; genderuwo 0,8× ≈ 36 m); peti ±3 × 3 × 5 m |
| **Rig** | Tidak. Gudang & derek static mesh (Chaos/tukar puing); peti static |
| **Sumber** | [16 Ep 9](../../../docs/16-panduan-arc-1.md#ep-9--yang-tak-kasatmata--genderuwo), [28 Ep 9](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Kontainer, dermaga, bolder, dan kapal latar = **Fab** ([28 bagian 3](../../../docs/28-struktur-level-episode.md#3-kit-distrik-dibangun-sekali-dipakai-ulang)).
- Derek: siluet harus sebanding dengan genderuwo supaya samarannya masuk akal. Bentuk A-frame gantry yang jelas.
- **Peti batu berukuran arca**: kotak kayu peti kemas berisi **alas arca kosong** dengan bekas tali; samakan batunya dengan [ep01_gerbang_prasasti.md](ep01_gerbang_prasasti.md) (alas) supaya pemain mengenali. Logo Adikara di peti.

## Prompt 1: gudang pelabuhan

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: an old port warehouse in an Indonesian harbor, about 40 meters long, 25 meters wide and 12 meters tall. Lower walls of weathered concrete, upper walls of rusty corrugated metal sheets painted faded gray-blue, a shallow gable roof of corrugated metal with a row of translucent skylight panels, two very large sliding metal doors on the long side and one on the short end, a row of small high windows, a small external steel staircase to a side office door.

Shape: simple long box, large readable panels.

Important: no text, no numbers, no signs, no people, no vehicles, no cables.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: derek kontainer pelabuhan

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a ship-to-shore container gantry crane at a harbor, about 50 meters tall. Two huge A-frame steel legs on rail wheel bogies, connected by thick horizontal beams, a long horizontal boom extending forward over the water side and backward over the land side, a small operator cabin hanging under the boom, a machinery house on top, painted faded red and white.

Shape: strong A-frame silhouette, thick box-section beams, nothing thin.

Important: no thin cables drawn, no container hanging, no text, no numbers, no lights.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 3: peti batu berukuran arca

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a large heavy-duty open wooden shipping crate about 3 meters wide, 3 meters deep and 5 meters tall, made of thick rough pine planks with steel corner brackets, the front panel removed and leaning beside it. Inside, an empty ancient square stone statue pedestal of weathered gray andesite with a carved lotus band, with a few loose strap marks. A simple bold abstract sunrise logo stenciled on the side of the crate.

Shape: simple box with thick planks, readable pedestal inside.

Important: no statue on the pedestal, no text, no numbers, no people.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos other than the sunrise emblem. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/pelabuhan_<gudang|derek|peti>_v01.png`, potong per view. Target UE: `SM_Pelabuhan_Gudang`, `SM_Pelabuhan_Derek`, `SM_PetiArca` (alas di dalam peti memakai ulang `SM_AlasArca`).
