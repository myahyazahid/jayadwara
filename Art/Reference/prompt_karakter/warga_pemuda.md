# Warga desa: pemuda (juga preman Ep 4)

| | |
|---|---|
| **Episode** | 1 (+ semua); preman Ep 4 |
| **Peran** | NPC warga; minion preman dengan tekstur lain |
| **Prioritas** | **Ep 1, sekarang** |
| **Tripo** | ✅ |
| **Sumber** | [18](../../../docs/18-kebutuhan-episode-1.md), [16](../../../docs/16-panduan-arc-1.md#7-aset--pemakaian-ulang) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Kemeja flanel terbuka = lapisan tipis (mirip jaket Aksa), masih wajar.
- Preman Ep 4 memakai mesh ini dengan tekstur jaket kulit/kaos gelap; tidak perlu generate terpisah.

## Prompt

```
Character turnaround model sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: an Indonesian village young man around 20, slim build, warm brown skin, short messy black hair, calm neutral expression, mouth closed. Plain t-shirt, open short-sleeve flannel shirt, dark jeans, sneakers.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the waist, no scarf, no sash, no bag, no tools in hand.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/warga_pemuda_v01.png`, potong jadi `warga_pemuda_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
