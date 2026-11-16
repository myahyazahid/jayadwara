# Candi induk Lawang Sapta

| | |
|---|---|
| **Episode** | 1 (latar adegan 3–9); Gerbang Induk muncul lagi di akhir cerita |
| **Fungsi** | Bangunan utama di plato candi; latar debrief; pembanding skala (sengaja lebih pendek dari Jerangkong) |
| **Prioritas** | **Ep 1, F2** |
| **Ukuran** | Alas 18 × 18 m, tinggi ±20 m ([30](../../../docs/30-desain-level-ep01.md#koordinat-greybox-meter-titik-nol--tengah-dasar-galian)) |
| **Rig** | Tidak. Static mesh, **tidak bisa hancur** |
| **Sumber** | [02](../../../docs/02-setting-dunia.md#candi-lawang-sapta--arca-kembar), [30](../../../docs/30-desain-level-ep01.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Gaya = usulan Claude: candi Jawa batu andesit (mirip gaya Jawa Tengah) agar sejalan dengan gerbang paduraksa dan arca Dwarapala. Bangunan **fiksi**, jangan menyalin candi nyata satu-satu.
- [18 C](../../../docs/18-kebutuhan-episode-1.md#c-lingkungan--level) merencanakan kit batu candi modular dari Fab + kustom; gambar ini jadi acuan siluet dan susunan, detail relief dari kit/material.
- Tangga satu sisi (menghadap gerbang, selatan). Pintu masuk gelap tanpa interior.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a fictional ancient Javanese Hindu-Buddhist temple (candi) made of weathered gray andesite stone, about 20 meters tall on an 18 by 18 meter square base. A tall stepped square platform base, a main square body with a single dark doorway at the top of one steep central staircase on the front side, a carved Kala face above the doorway, and a roof built of three diminishing stepped tiers decorated with small bell-shaped stone finials at the corners, topped by a larger bell-shaped finial. Simple bold relief panels on the walls.

Shape: symmetrical, solid stepped silhouette, staircase only on the front side.

Important: no moss, no cracks, no vegetation, no people, no statues in front, no glowing parts. Not a copy of any real temple.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/candi_induk_v01.png`, potong per view. Target UE: `SM_CandiInduk` (atau rakitan dari kit modular).
