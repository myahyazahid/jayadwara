# Lilin ritual (raksasa di atap + lilin merah kecil)

| | |
|---|---|
| **Episode** | 4 |
| **Fungsi** | **3 lilin raksasa** di atap gedung: selama menyala boss kebal (dipadamkan Jayadwara dengan tangan/tiupan). Lilin merah kecil = petunjuk tukang parkir dan prop ritual di gudang |
| **Prioritas** | Fase 4 |
| **Ukuran** | Raksasa ±2,5 m diameter × 8 m (usulan; boss 0,5× ≈ 22 m); kecil ±4 × 25 cm |
| **Rig** | Tidak. Static mesh; api = VFX, lelehan = mesh |
| **Sumber** | [16 Ep 4](../../../docs/16-panduan-arc-1.md#ep-4--lilin-di-pasar-malam--babi-ngepet) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Satu model dipakai untuk dua ukuran: lilin raksasa = lilin kecil diskala, ditambah **dudukan tanah liat** yang mencengkeram atap supaya terbaca "ditaruh di atap", bukan tumbuh dari atap.
- Lilin raksasa terbuat dari energi Kala yang memadat (usulan): lilin merah gelap dengan retak bercahaya (emissive). Gambar tanpa api dan tanpa glow.
- Harus bisa dipadamkan **tanpa meruntuhkan atap**: dudukan lebar dan rendah.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a thick dark red ritual candle standing in a heavy round clay holder. The candle is a tall cylinder about three times taller than its width, slightly uneven, with large thick drips of red wax running down the sides and pooling over the rim of the holder, a short black wick at the top. The holder is a wide low rough terracotta dish with three thick stubby feet.

Shape: simple solid cylinder with big chunky wax drips, wide stable base.

Important: unlit, no flame, no smoke, no glow, no text, no symbols.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/lilin_ritual_v01.png`, potong per view. Target UE: `SM_LilinRitual` (skala kecil dan raksasa dari aset yang sama, material raksasa dengan retak emissive).
