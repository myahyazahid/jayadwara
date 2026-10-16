# Musala desa

| | |
|---|---|
| **Episode** | 1 (adegan 7, di sebelah lapangan desa tempat warga berlindung) |
| **Fungsi** | Bangunan desa yang **tidak bisa hancur** (aturan budaya) |
| **Prioritas** | **Ep 1, F2** |
| **Ukuran** | ±9 × 9 × 8 m (usulan; ukuran belum ada di docs/30) |
| **Rig** | Tidak. Static mesh, tanpa fracture |
| **Sumber** | [17 cek IP & budaya](../../../docs/17-skenario-arc-1.md#cek-ip--budaya-ep-1), [30 bagian 4](../../../docs/30-desain-level-ep01.md#tidak-bisa-hancur) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- **Tidak bisa hancur dan tidak boleh rusak** (aturan budaya). Collision padat supaya puing memantul.
- Bentuk = usulan Claude: atap **tajug** bertumpuk khas musala/masjid desa Jawa, bukan kubah besar, supaya terbaca sebagai desa Jawa dan beda siluet dari rumah.
- **Tanpa kaligrafi atau teks** di mesh/tekstur. Interior tidak perlu.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a small rural Javanese village prayer house (musala), about 9 meters square and 8 meters tall. Plastered walls painted clean white with a light green base band, a traditional two-tiered Javanese tajug pyramid roof covered with dark gray clay tiles with a small simple pointed finial at the top. A front veranda under the lower roof tier with four square white columns, a wide double wooden door, tall arched wooden windows on each side wall, a raised tiled floor two steps above the ground, a small separate covered water tap area attached to one side wall.

Shape: symmetrical, clean simple volumes.

Important: no text, no calligraphy, no signs, no loudspeakers, no people, no plants.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/musala_v01.png`, potong per view. Target UE: `SM_Musala`.
