# Genderuwo

| | |
|---|---|
| **Episode** | 9 |
| **Peran** | Boss tak terlihat; grup rig Buto |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ |
| **Sumber** | [kartu episode](../../../docs/16-panduan-arc-1.md#ep-9--yang-tak-kasatmata--genderuwo), [05](../../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; kunci di model sheet sebelum modeling.
- Skala manusia dulu (seperti Jerangkong); ukuran raksasa diatur di UE ([16](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Proporsi humanoid standar supaya rig bisa dipakai ulang untuk Buto Arc 3 dan diretarget ke Manny.
- Bulu digambar sebagai gumpalan besar yang menempel ke badan; bulu halus Tripo jelek.

## Prompt

```
Monster character turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Genderuwo, a huge hairy ape-like spirit from Javanese folklore that lives in old buildings and big trees and can turn invisible, enlarged by dark red cursed energy. Massive broad humanoid body about 7 heads tall, heavy shoulders and long powerful arms, thick legs. Covered in long coarse dark reddish-brown fur shaped as large chunky clumps, the fur lies close to the body. Heavy brow, flat wide nose, small tusks from the lower jaw, glowing dark red eyes, mouth closed. Dark gray skin visible on the face, chest, palms and soles. A few faint dark red glowing streaks in the fur.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers spread, feet shoulder-width apart with a clear gap between the legs.

Important: intimidating, not gory. No blood. No blue light. No clothing, no weapons, nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/genderuwo_v01.png`, potong jadi `genderuwo_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
