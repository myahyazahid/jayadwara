# Pocong ⚠️

| | |
|---|---|
| **Episode** | 5 |
| **Peran** | Boss |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ |
| **Sumber** | [kartu episode](../../../docs/16-panduan-arc-1.md#ep-5--tali-yang-belum-dilepas--pocong-️), [05](../../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; kunci di model sheet sebelum modeling.
- Skala manusia dulu (seperti Jerangkong); ukuran raksasa diatur di UE ([16](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Pedoman sensitivitas ([06](../../../docs/06-referensi-mitologi.md#catatan-per-boss-️)): tanpa olok-olok kafan/pemakaman, tanpa wajah busuk, nada khidmat.
- Tiga simpul bercahaya = titik lemah (mekanik bidik bagian tubuh).

## Prompt

```
Spirit creature turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same figure, same scale, base aligned on one ground line, wide empty space between views.

Creature: a restless wrapped spirit from Javanese folklore whose shroud ties were never untied, enlarged by dark red cursed energy. A tall upright body fully wrapped in old off-white cloth, slightly weathered and dusty, smooth simplified fabric folds, no arms or legs visible. Three large thick knotted ties: one above the head, one around the neck, one around the ankles, each knot glowing softly dark red as a clear weak point. The face area is a deep calm shadow with two faint glowing dark red eyes, no visible rotting flesh.

Pose: standing perfectly straight and still, feet together inside the wrapping.

Important: solemn, sorrowful and eerie, not comedic and not grotesque. No blood, no decay, no gore, no exposed skin. No blue light. No grave or tombstone in the image.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Simple bold shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/pocong_v01.png`, potong jadi `pocong_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
