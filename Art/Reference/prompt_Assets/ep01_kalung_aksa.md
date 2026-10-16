# Kalung pecahan arca (Aksa)

| | |
|---|---|
| **Episode** | Semua (inti kekuatan); close-up di adegan 6 Ep 1 |
| **Fungsi** | Inti kekuatan transformasi "Lawang Terbuka": digenggam di dada, menyala di sela jari |
| **Prioritas** | **Ep 1, F2** |
| **Ukuran** | Liontin belah ketupat ±5 × 3,5 × 1 cm; rantai ±60 cm |
| **Rig** | Tidak. Static mesh dipasang ke socket dada Aksa |
| **Sumber** | [03](../../../docs/03-karakter.md#aksa-jaya-mangkubumi-aksa), [17 adegan 6](../../../docs/17-skenario-arc-1.md#adegan-6--kebangkitan--seq) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Bentuk dikunci di docs/03: **pecahan batu arca berbentuk belah ketupat (diamond), berbingkai emas**, peninggalan Ki Zahid. Warna batu = batu [arca Dwarapala](ep01_arca_dwarapala.md).
- Mesh dibuat **terpisah dari Aksa** ([prompt Aksa](../prompt_karakter/aksa.md#catatan)) supaya bisa menyala (material emissive) dan muncul jelas di close-up.
- Rantai cukup tube sederhana atau dibuat dari array mata rantai di Blender; gambar hanya untuk liontin.
- Glow saat transformasi = material/VFX, jadi gambar **tanpa cahaya**.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, wide empty space between views, shown large and centered.

Object: a pendant made from a small rough fragment of ancient carved gray andesite stone, cut into a vertical diamond (rhombus) shape about 5 centimeters tall, set in a simple sturdy gold frame that wraps the edges. A faint carved line pattern from the original temple statue is visible on the stone face. A small gold loop at the top, connected to a plain gold chain shown only as a short piece.

Important: no glow, no gemstones, no engraved letters, no extra charms.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/kalung_aksa_v01.png`, potong per view. Target UE: `SM_KalungAksa`, dipasang ke socket dada `SK_Aksa2`.
