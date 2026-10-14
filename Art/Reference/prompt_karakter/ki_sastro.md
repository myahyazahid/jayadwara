# Ki Sastro

| | |
|---|---|
| **Episode** | 2+ (hub markas DWARA); Ep 1 cukup potret 2D |
| **Peran** | Budayawan & dalang (ritual Ep 5, 8) |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ badan + pakaian; wajah mungkin MetaHuman |
| **Sumber** | [03](../../../docs/03-karakter.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Penampilan = usulan Claude; docs/03 baru mengunci peran dan sifat.
- Kain jarik panjang akan menyatukan kaki. Prompt memakai jarik selutut di atas celana hitam; alternatif: jarik penuh lalu di-rig sebagai rok.

## Prompt

```
Character turnaround model sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: Ki Sastro, Javanese cultural elder and wayang shadow puppet master (dalang), 70 years old. Small slim build, warm brown skin, wrinkled kind face, thin white mustache, gentle neutral expression, mouth closed. Dark batik blangkon headcloth, closed dark beskap jacket with a high collar and simple buttons, a knee-length brown batik jarik cloth wrapped tightly around the waist over plain black trousers, simple dark sandals. No keris, no weapon.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the waist, no scarf, no sash, no long coat tails, nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/ki_sastro_v01.png`, potong jadi `ki_sastro_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
