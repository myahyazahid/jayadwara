# Gedung Adikara + gedung tinggi CBD

| | |
|---|---|
| **Episode** | 3 (dibangun), dipakai ulang di Ep 10 dan Arc berikutnya (kantor pusat Adikara) |
| **Fungsi** | Gedung Adikara = lokasi investigasi vertikal (lobi, ruang kontrol, server, atap); gedung kaca lain = pengisi CBD, **kerusakan mahal** |
| **Prioritas** | Fase 4 |
| **Ukuran** | Menara Adikara ±40 × 40 × 120 m; gedung pengisi ±30 × 30 × 60–90 m (usulan, sebanding dengan Jayadwara 45 m) |
| **Rig** | Tidak. Static mesh; kaca pecah + fasad runtuh sebagian lewat Chaos/tukar puing |
| **Sumber** | [16 Ep 3](../../../docs/16-panduan-arc-1.md#ep-3--lapar-listrik--jenglot), [28 Ep 3](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1), [02](../../../docs/02-setting-dunia.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Gedung tinggi generik (plaza, jalan layang, menara kaca latar) kandidat **Fab**; prompt di sini untuk **menara Adikara** yang khas (logo matahari terbit, puncak menyerupai matahari terbit = "Proyek Fajar"; usulan).
- Interior (lobi, ruang kontrol, server, lantai kantor) dirangkai dari kit/Fab; gambar ini hanya eksterior.
- Kaca dibuat modul panel supaya mudah dipecah per panel.

## Prompt 1: menara Adikara

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: the corporate headquarters tower of a powerful Indonesian mining and infrastructure conglomerate, about 120 meters tall on a 40 by 40 meter square footprint. A sleek modern skyscraper with a dark blue-gray glass curtain wall in a clean grid, white vertical stone fins running the full height on the corners, a wide three-story glass lobby podium with a large flat canopy over the entrance, and a crown at the top shaped like an abstract half sunrise with radiating white fins. A large simple abstract sunrise logo on the podium facade.

Shape: strong simple silhouette, clean repeating facade grid, symmetrical.

Important: no readable text, no real company logo, no people, no vehicles, no trees, no lights on.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos other than the sunrise emblem. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: gedung kantor pengisi

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a generic modern office building in a Southeast Asian business district, about 75 meters tall on a 30 by 30 meter footprint. Green-tinted glass curtain wall with horizontal light gray concrete spandrel bands every floor, a recessed ground floor with square columns, a flat roof with a simple rooftop mechanical box and a low parapet.

Shape: simple rectangular tower, clean repeating grid.

Important: no readable text, no logos, no people, no vehicles, no trees, no lights on.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/menara_adikara_v01.png`, `gedung_kantor_v01.png`, potong per view. Target UE: `SM_MenaraAdikara`, `SM_GedungKantor_A`.
