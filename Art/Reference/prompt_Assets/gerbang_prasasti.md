# Gerbang candi + alas arca + prasasti retak

| | |
|---|---|
| **Episode** | 1 (adegan 4, 6, 9); Situs Lawang Sapta muncul lagi di episode lain |
| **Fungsi** | Gerbang masuk plato candi; prasasti = **clue 3** (`Clue.Ep01.Prasasti`, kelemahan boss); alas kiri = tempat transformasi & debrief |
| **Prioritas** | **Ep 1, F2** |
| **Ukuran** | Gerbang lebar bukaan 8 m (usulan tinggi ±10 m); alas arca ±2,5 × 2,5 × 1 m; prasasti ±1,2 × 0,4 × 1,8 m ([30](../../../docs/30-desain-level-ep01.md#koordinat-greybox-meter-titik-nol--tengah-dasar-galian)) |
| **Rig** | Tidak. Static mesh, **tidak bisa hancur** ([30 bagian 4](../../../docs/30-desain-level-ep01.md#tidak-bisa-hancur)) |
| **Sumber** | [17 adegan 4](../../../docs/17-skenario-arc-1.md#adegan-4--tiga-petunjuk--main--koms), [30](../../../docs/30-desain-level-ep01.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- **Bentuk gerbang = usulan Claude.** Gerbang paduraksa (beratap, bukan candi bentar terbelah) dipilih supaya nyambung dengan gerbang cahaya paduraksa di transformasi "Lawang Terbuka" ([17 adegan 6](../../../docs/17-skenario-arc-1.md#adegan-6--kebangkitan--seq)). Bukaan 8 m lebih besar dari gerbang candi nyata karena dipakai di sekitar dua raksasa.
- Gerbang, alas, dan prasasti dibuat **3 prompt terpisah** supaya tiap gambar cukup besar untuk modeling.
- Retak prasasti di mesh cukup satu retakan besar diagonal; retak halus dan aksara Kawi dibuat di tekstur/decal. Aksara = **teks fiksi**, bukan prasasti nyata.
- Alas kanan di adegan 9: tambah decal bekas tali derek + jejak ban (di level, bukan di mesh).

## Prompt 1: gerbang paduraksa

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a massive ancient Javanese paduraksa temple gate made of weathered gray andesite stone blocks, about 10 meters tall with a wide rectangular doorway 8 meters wide and 6 meters high. Two thick stepped stone pillars on each side, a solid stone lintel above the doorway, and a tiered stepped stone roof above that, rising in four diminishing layers to a small square finial on top. A large carved Kala face above the center of the doorway, simple and bold. Three low stone steps in front of and behind the doorway.

Shape: thick solid blocky stone masses, clean stepped silhouette, symmetrical left to right.

Important: no doors, no statues, no moss, no cracks, no vegetation, no glowing parts.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: alas arca

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: an empty ancient Javanese statue pedestal made of weathered gray andesite stone, a square stepped plinth about 2.5 meters wide and 1 meter tall. A wide bottom step, a slightly recessed middle band with a simple carved lotus petal row, and a flat square top surface. Completely empty on top.

Important: no statue, no moss, no cracks, no vegetation.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 3: prasasti retak

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: an ancient Javanese stone inscription stele (prasasti) made of weathered gray andesite, about 1.8 meters tall, 1.2 meters wide and 0.4 meters thick, with a rounded pointed top like a leaf shape, standing on a low rectangular stone base. The front face is flat and covered with rows of shallow carved ancient script shown as simple horizontal grooves. One large diagonal crack runs across the front from the upper left to the lower right, with a small chunk missing at the right edge.

Important: the script is abstract grooves, not readable letters. No moss, no vegetation, no glowing parts.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/gerbang_candi_v01.png`, `alas_arca_v01.png`, `prasasti_v01.png`, lalu potong per view. Target UE: `SM_GerbangCandi`, `SM_AlasArca`, `SM_Prasasti`.
