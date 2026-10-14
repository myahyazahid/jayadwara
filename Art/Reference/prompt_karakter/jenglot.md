# Jenglot

| | |
|---|---|
| **Episode** | 3 |
| **Peran** | Boss (membesar tiap fase) |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ |
| **Sumber** | [kartu episode](../../../docs/16-panduan-arc-1.md#ep-3--lapar-listrik--jenglot), [05](../../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; kunci di model sheet sebelum modeling.
- Skala manusia dulu (seperti Jerangkong); ukuran raksasa diatur di UE ([16](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Rambut panjang digambar sebagai satu massa padat di punggung supaya tidak menyatu ke lengan.
- Listrik kuning-putih, energi Kala merah gelap; tanpa biru.

## Prompt

```
Monster character turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Jenglot, a tiny dried mummified charm figure from Javanese folklore, grown huge by absorbing electricity and dark red cursed energy. Thin hunched humanoid body, dry dark brown leathery skin stretched over bones, extremely long straight black hair falling down the back to the knees as one thick solid mass, long thin fingers with long dark nails, small fangs visible, glowing dark red eyes. Thick black electrical cables wrapped tightly around the arms, legs, and torso like bandages, with broken plugs and small transformer parts stuck in the back. Cracks in the skin glow dark red with bright yellow-white electric sparks.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso, fingers spread, legs apart with a clear gap. Hair stays a solid mass behind the back, not touching the arms.

Important: eerie, not gory. No blood, no exposed organs. No blue light: electricity is yellow-white, cursed energy is dark red. No cables hanging loose.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/jenglot_v01.png`, potong jadi `jenglot_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
