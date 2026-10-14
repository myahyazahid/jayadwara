# Gunadi Adikara

| | |
|---|---|
| **Episode** | 2+ (hub markas DWARA); Ep 1 cukup potret 2D |
| **Peran** | CEO Adikara Group (opsional 3D) |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ badan + pakaian; wajah mungkin MetaHuman |
| **Sumber** | [03](../../../docs/03-karakter.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Penampilan = usulan Claude; docs/03 baru mengunci peran dan sifat.
- Bisa cukup potret.

## Prompt

```
Character turnaround model sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: Gunadi Adikara, CEO of a large Indonesian mining and infrastructure group, 58 years old. Tall build with a slight belly, warm brown skin, slicked-back gray-black hair, confident calm neutral expression, mouth closed. Tailored charcoal suit, closed jacket, plain white shirt, dark tie, a small abstract sunrise-shaped gold lapel pin, polished black shoes.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the waist, no scarf, no sash, no long coat tails, nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/gunadi_v01.png`, potong jadi `gunadi_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
