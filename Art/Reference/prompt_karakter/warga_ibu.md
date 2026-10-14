# Warga desa: ibu

| | |
|---|---|
| **Episode** | 1 (+ semua) |
| **Peran** | NPC warga |
| **Prioritas** | **Ep 1, sekarang** |
| **Tripo** | ✅ |
| **Sumber** | [18](../../../docs/18-kebutuhan-episode-1.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Rok jarik panjang menyatukan kedua kaki. Terima saja (di-rig sebagai rok, bobot ke paha), atau ganti dengan `knee-length skirt over plain trousers`.
- Lengan pada hasil sebelumnya agak rapat (±25°); pastikan 45°.

## Prompt

```
Character turnaround model sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: an Indonesian village woman in her 40s, Central Java. Average build, warm brown skin, black hair in a low bun, calm neutral expression, mouth closed. Simple fitted long-sleeve blouse in a plain muted color, ankle-length fitted batik skirt with a large simple pattern, simple flat sandals.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the waist, no scarf, no sash, no bag, no tools in hand.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/warga_ibu_v01.png`, potong jadi `warga_ibu_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
