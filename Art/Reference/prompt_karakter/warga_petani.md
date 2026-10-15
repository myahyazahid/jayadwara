# Warga desa: bapak petani

| | |
|---|---|
| **Episode** | 1 (dipakai ulang di semua episode) |
| **Peran** | NPC warga |
| **Prioritas** | **Ep 1, sekarang** |
| **Tripo** | ✅ |
| **Sumber** | [18](../../../docs/18-kebutuhan-episode-1.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Satu karakter per gambar. Sheet 9 view (3 warga) membuat tiap figur cuma ±300 px, terlalu kecil untuk Tripo.
- Caping lebar aman; kalau menyatu ke kepala, pisahkan di Blender.

## Prompt

```
Character turnaround model sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: an Indonesian village farmer in his 50s, Central Java. Average build, warm brown sun-tanned skin, short gray-black hair, calm neutral expression, mouth closed. Wide conical woven bamboo hat (caping), faded loose button-up work shirt with rolled sleeves, plain dark knee-length shorts, simple rubber sandals.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the waist, no scarf, no sash, no bag, no tools in hand.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/warga_petani_v01.png`, potong jadi `warga_petani_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
