# Babi Ngepet

| | |
|---|---|
| **Episode** | 4 |
| **Peran** | Boss berkaki empat (badan panjang, 0,5×) |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ |
| **Sumber** | [kartu episode](../../../docs/16-panduan-arc-1.md#ep-4--lilin-di-pasar-malam--babi-ngepet), [05](../../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; kunci di model sheet sebelum modeling.
- Skala manusia dulu (seperti Jerangkong); ukuran raksasa diatur di UE ([16](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Pose berdiri netral dengan celah di antara keempat kaki; ekor menjauh dari kaki belakang.

## Prompt

```
Monster creature turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, hooves aligned on one ground line, wide empty space between views.

Creature: Babi Ngepet, a cursed black wild boar from Javanese black-magic folklore, created by a greedy wealth ritual and enlarged by dark red cursed energy. Long low muscular body (body length about 2.5 times its shoulder height), thick black bristly hide shaped as large chunky clumps, short curved yellowish tusks, small glowing dark red eyes, a ridge of stiff black bristles along the spine. Faint dark red glowing cracks on the flanks shaped like dripping candle wax. A short tail.

Pose: neutral standing pose, all four legs straight and vertical, front legs apart and hind legs apart with clear gaps between all legs, head straight forward, mouth closed, tail held away from the hind legs.

Important: menacing but not gory. No blood. No blue light. No saddle, no ropes, no candles on the body.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/babi_ngepet_v01.png`, potong jadi `babi_ngepet_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
