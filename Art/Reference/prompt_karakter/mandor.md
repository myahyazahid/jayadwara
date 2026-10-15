# Mandor Adikara

| | |
|---|---|
| **Episode** | 1 |
| **Peran** | NPC (Adikara) |
| **Prioritas** | **Ep 1, sekarang** |
| **Tripo** | ✅ input v01 sudah dipotong (siap Multiview) |
| **Sumber** | [18](../../../docs/18-kebutuhan-episode-1.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Walkie-talkie dan tepi lubang lengan rompi menyatu dengan badan; aman karena kaku.
- Logo matahari terbit abstrak, bukan merek nyata.

## Prompt

```
Character turnaround model sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: an Indonesian construction site foreman in his 40s working for a big mining and infrastructure company. Stocky build, warm brown skin, short black hair with a thin mustache, stern neutral expression, mouth closed. White hard hat, orange high-visibility safety vest over a dark gray work shirt, the vest has a simple bold geometric company logo (an abstract stylized sunrise shape, not any real brand), dark cargo work pants, black steel-toe boots. A walkie-talkie clipped tightly on the vest chest.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the belt, no lanyard, no tools in hand.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos other than the vest emblem. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/mandor_v01.png`, potong jadi `mandor_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
