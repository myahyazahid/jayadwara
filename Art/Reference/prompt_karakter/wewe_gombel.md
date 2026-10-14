# Wewe Gombel

| | |
|---|---|
| **Episode** | 8 |
| **Peran** | Boss dengan zona larangan pukul |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ |
| **Sumber** | [kartu episode](../../../docs/16-panduan-arc-1.md#ep-8--kentongan-tengah-malam--wewe-gombel), [05](../../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; kunci di model sheet sebelum modeling.
- Skala manusia dulu (seperti Jerangkong); ukuran raksasa diatur di UE ([16](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Versi legenda (payudara menjuntai) tidak dipakai (rating remaja). Tiga rongga bercahaya = zona tempat anak disembunyikan.

## Prompt

```
Monster character turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Wewe Gombel, a tall gaunt forest spirit from Central Javanese folklore who hides neglected children, enlarged by dark red cursed energy. Very tall thin hunched figure with long arms, gray-brown bark-like skin, a sad tired old face with deep-set glowing dark red eyes, mouth closed. Very long gray-black hair falling down the back as one thick solid mass merging into a long cloak of tangled roots, vines and dry leaves that covers the body like a fitted robe. Three clearly visible woven nest-like hollows on the body (on the chest, the belly, and the back), each lined with soft warm yellow light, where children are hidden safely inside.

Pose: A-pose, long arms straight and angled 45 degrees away from the body, clear empty space between arms and torso, long fingers spread, legs apart with a clear gap under the robe.

Important: sorrowful and eerie, sympathetic, not grotesque and not sexualized. No exposed breasts, no gore, no blood. No children visible in the image, only the glowing hollows. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/wewe_gombel_v01.png`, potong jadi `wewe_gombel_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
