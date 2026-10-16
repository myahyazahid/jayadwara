# Prasasti Sapta Dwara

| | |
|---|---|
| **Episode** | 10 (finale): clue ★ di Situs Lawang Sapta, lokasi fase 3 (inti api), penutup cliffhanger ke Arc 2 |
| **Fungsi** | Prasasti besar yang menunjukkan **tujuh gerbang**; tempat Banaspati dikembalikan ke segelnya |
| **Prioritas** | Fase 4 |
| **Ukuran** | ±3 × 1 × 5 m di atas alas ±5 × 3 × 1 m (usulan; cukup besar untuk interaksi skala raksasa di fase 3) |
| **Rig** | Tidak. Static mesh, **tidak bisa hancur** |
| **Sumber** | [16 Ep 10](../../../docs/16-panduan-arc-1.md#ep-10--prasasti-tujuh-gerbang--banaspati-finale), [02](../../../docs/02-setting-dunia.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- **Usulan Claude:** docs/16 belum memastikan apakah ini prasasti Ep 1 yang dibaca ulang atau prasasti baru. Usulan: prasasti **baru**, tersingkap di bawah reruntuhan arca kiri setelah Ep 1, lebih besar, dengan **peta tujuh gerbang** berupa tujuh lingkaran berukir. Kalau dipilih memakai prasasti Ep 1, file ini tidak perlu.
- Aksara = teks fiksi (decal); di mesh hanya alur.
- Inti api fase 3 = VFX; gambar tanpa api.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a large ancient Javanese stone inscription monument of weathered gray andesite, a thick upright slab about 5 meters tall, 3 meters wide and 1 meter thick with a pointed arched top, standing on a wide low stepped stone platform. The front face is carved with a large relief of seven circles arranged like a map, one bigger circle in the center and six smaller circles around it, connected by carved lines, framed by a simple border and rows of shallow carved script grooves below. The back face is plain with a simple border.

Shape: solid monumental slab, bold readable relief.

Important: the script is abstract grooves, not readable letters. No moss, no cracks, no glow, no fire.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/prasasti_sapta_dwara_v01.png`, potong per view. Target UE: `SM_PrasastiSaptaDwara`.
