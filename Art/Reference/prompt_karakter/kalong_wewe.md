# Kalong Wewe

| | |
|---|---|
| **Episode** | 7 |
| **Peran** | Boss udara |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ |
| **Sumber** | [kartu episode](../../../docs/16-panduan-arc-1.md#ep-7--bayang-di-atas-atap--kalong-wewe), [05](../../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; kunci di model sheet sebelum modeling.
- Skala manusia dulu (seperti Jerangkong); ukuran raksasa diatur di UE ([16](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Sayap terbentang horizontal, tidak menumpuk ke badan/kaki.

## Prompt

```
Monster creature turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Kalong Wewe, a giant cursed bat spirit from Sundanese folklore, enlarged by dark red cursed energy. Hunched humanoid bat body with digitigrade legs and clawed feet, large pointed ears, flat bat nose, glowing dark red eyes, mouth closed. Short thick dark brown fur shaped as large chunky clumps on the body. Huge leathery wings attached to the arms, wingspan about 3 times its height, thin dark gray-brown membrane with clear finger bones, tattered edges at the tips only. Faint dark red glowing veins in the wing membranes.

Pose: standing upright, wings fully spread horizontally to the sides, wings not overlapping the body or legs, legs apart with a clear gap.

Important: menacing, not gory. No blood. No blue light. The creature is sensitive to light: its eyes are small and squinting.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/kalong_wewe_v01.png`, potong jadi `kalong_wewe_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
