# Dr. Nadia Prameswari

| | |
|---|---|
| **Episode** | 2+ (hub markas DWARA); Ep 1 cukup potret 2D |
| **Peran** | Ilmuwan, pencipta scanner Netra |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ badan + pakaian; wajah mungkin MetaHuman |
| **Sumber** | [03](../../../docs/03-karakter.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Penampilan = usulan Claude; docs/03 baru mengunci peran dan sifat.
- Opsional: ganti rambut dengan `a plain dark hijab neatly tucked into the collar`.

## Prompt

```
Character turnaround model sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: Dr. Nadia Prameswari, Indonesian energy physicist, 32 years old. Slim build, light-brown skin, shoulder-length straight black hair tied in a low ponytail, thin rectangular glasses, sharp skeptical neutral expression, mouth closed. Short fitted white lab jacket worn closed over a dark turtleneck, a small handheld scanner device clipped flat on the hip, slim dark trousers, simple flat shoes.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the waist, no scarf, no sash, no long coat tails, nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/nadia_v01.png`, potong jadi `nadia_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
