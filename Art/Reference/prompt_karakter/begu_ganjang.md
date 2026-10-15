# Begu Ganjang ⚠️

| | |
|---|---|
| **Episode** | 19 |
| **Lokasi** | Toba |
| **Peran** | Makin tinggi kalau dilihat; dilawan lewat pantulan |
| **Fokus anggota** | Nadia |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- **Sensitif sosial** ([06](../../../docs/06-referensi-mitologi.md#catatan-per-boss-️)): tuduhan memelihara begu ganjang memicu kekerasan nyata. Jangan pakai **ulos** atau ornamen Batak nyata.
- Mekanik memanjang: badan dan leher di-rig dengan tulang yang bisa di-scale; segmen leher/torso panjang dan seragam supaya mudah diregang.

## Prompt

```
Monster character turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Begu Ganjang, a towering ghost from Batak folklore that grows taller when looked at, enlarged by dark red cursed energy. Extremely tall and thin humanoid, about 12 heads tall, with a long neck and very long thin limbs. Gray-black skin like dry ash, a small narrow head with a blank pale face and two glowing dark red eyes, mouth closed, thin wisps of long gray hair close to the scalp. Wrapped in plain dark gray tattered cloth bandages tightly around the torso and upper arms.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers spread, legs apart with a clear gap. Very long fingers spread.

Important: eerie, not gory. No traditional woven cloth patterns, no cultural ornaments. No blood. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/begu_ganjang_v01.png`, potong jadi `begu_ganjang_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
