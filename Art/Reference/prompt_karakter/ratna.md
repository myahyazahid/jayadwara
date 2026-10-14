# Ratna Dewantari

| | |
|---|---|
| **Episode** | 2+ (hub markas DWARA); Ep 1 cukup potret 2D |
| **Peran** | Anggota DPR, penghubung pemerintah (opsional 3D) |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ badan + pakaian; wajah mungkin MetaHuman |
| **Sumber** | [03](../../../docs/03-karakter.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Penampilan = usulan Claude; docs/03 baru mengunci peran dan sifat.
- Bisa cukup potret/siaran TV; 3D hanya kalau muncul di level.

## Prompt

```
Character turnaround model sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: Ratna Dewantari, Indonesian member of parliament and government liaison, 45 years old. Slim upright build, light-brown skin, professional cold neutral expression, mouth closed. Black hair in a neat bun, a fitted dark maroon blazer closed with one button over a plain cream blouse, slim matching trousers, low black heels, a small gold lapel pin.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the waist, no scarf, no sash, no long coat tails, nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/ratna_v01.png`, potong jadi `ratna_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
