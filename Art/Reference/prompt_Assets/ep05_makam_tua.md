# Makam tua Kota Lama ⚠️

| | |
|---|---|
| **Episode** | 5 |
| **Fungsi** | Kawasan makam (investigasi, gerbang makam terkunci = gerbang cerita); **zona larangan rusak** di arena (penalti besar) |
| **Prioritas** | Fase 4 |
| **Ukuran** | Gerbang ±4 × 1 × 4 m; pagar modul ±3 × 0,3 × 2 m; nisan ±0,5–1,5 m; rumah juru kunci ±6 × 8 × 5 m |
| **Rig** | Tidak. Static mesh, **tidak bisa hancur** |
| **Sumber** | [16 Ep 5](../../../docs/16-panduan-arc-1.md#ep-5--tali-yang-belum-dilepas--pocong-️), [06](../../../docs/06-referensi-mitologi.md#catatan-per-boss-️), [28 Ep 5](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- **Sensitif.** Ditampilkan dengan hormat dan tenang: makam rapi, terawat, tanpa kesan horor murahan. Tanpa tulisan/nama di nisan, tanpa simbol agama yang spesifik di mesh (nisan bentuk umum makam tua Jawa).
- Makam yang "terganggu survei lahan" = nisan miring + patok survei (prop proyek Adikara dari [ep01_prop_proyek_adikara.md](ep01_prop_proyek_adikara.md)), bukan makam rusak/terbongkar.
- Pohon kamboja dan beringin = Fab/vegetasi.

## Prompt 1: gerbang + pagar makam

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: the entrance gate of an old quiet Javanese town cemetery, about 4 meters wide and 4 meters tall. Two thick square plastered brick pillars painted white with weathering, each topped with a simple stepped cap, a small curved tiled roof bridging the two pillars, and a pair of old dark green iron gates with simple vertical bars, closed. On each side, one short section of low white plastered wall with an iron railing on top.

Shape: symmetrical, thick pillars, simple readable bars.

Important: no text, no names, no religious symbols, no plants, no people, no padlock detail.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: set nisan

```
Orthographic model reference sheet for a realistic 3D action game, a set of three separate grave markers, each shown in FRONT, SIDE and TOP orthographic views, arranged in three rows with wide empty space between them, same scale.

Objects: (1) a simple old Javanese grave with a low rectangular white plastered base about 2 meters long and two small rounded stone headstones at both ends; (2) an older weathered grave of dark gray stone with a slightly raised stepped base and two small plain carved headstones; (3) a very old simple grave marker, a single upright rounded stone about 50 centimeters tall set in the ground.

Important: respectful and tidy, no text, no names, no religious symbols, no flowers, no damage, no bones, no spooky elements.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 3: rumah juru kunci

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a small old caretaker's house next to a town cemetery, about 6 meters wide, 8 meters deep and 5 meters tall. Lower walls of plastered brick painted white, upper walls of dark wooden planks, a traditional Javanese kampung-style gable roof of dark clay tiles, a small front veranda with two wooden posts and a wooden bench attached to the wall, a wooden door and two wooden windows with shutters.

Important: no text, no signs, no plants, no people.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/makam_<gerbang|nisan|rumah_juru_kunci>_v01.png`, potong per view. Target UE: `SM_Makam_Gerbang`, `SM_Makam_Pagar`, `SM_Makam_Nisan_A/B/C`, `SM_Makam_RumahJuruKunci`.
