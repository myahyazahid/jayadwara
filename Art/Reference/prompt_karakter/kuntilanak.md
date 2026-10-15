# Kuntilanak

| | |
|---|---|
| **Episode** | 14 |
| **Lokasi** | Kota sungai, Kalimantan (Pontianak) |
| **Peran** | Boss sonik: jeritan mengacaukan HUD & kontrol; titik lemah di tengkuk |
| **Fokus anggota** | Ki Sastro |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Gaun panjang menyatukan kedua kaki: wajar karena ia melayang; rig sebagai rok + rantai kain.
- Titik lemah di **tengkuk** (tempat "paku"): beri tanda bercahaya yang jelas.
- Tanpa seksualisasi.

## Prompt

```
Monster character turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, dress hems aligned on one ground line, wide empty space between views.

Creature: Kuntilanak, a female ghost from Malay and Kalimantan folklore, enlarged by dark red cursed energy. Tall slender figure, pale gray skin, a sorrowful gaunt face partly framed by very long straight black hair that falls behind the shoulders and down the back to the knees as one thick solid mass. Long loose off-white dress with long sleeves, weathered and dusty, reaching below the feet. A glowing dark red mark at the nape of the neck as a clear weak point. Glowing dark red eyes, mouth closed.

Pose: floating upright just above the ground, A-pose, arms straight and angled 45 degrees away from the body, long sleeves not touching the dress, long thin fingers spread. Hair stays behind the shoulders, not covering the arms.

Important: eerie and sorrowful, not sexualized, not gory. No blood. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/kuntilanak_v01.png`, potong jadi `kuntilanak_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
