# Ebu Gogo

| | |
|---|---|
| **Episode** | 11 |
| **Lokasi** | Flores (NTT) |
| **Peran** | Kawanan cerdik suka mencuri; boss = Ebu Gogo raksasa (satu model, pola Tuyul) |
| **Fokus anggota** | Prof. Yahyo |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Digambarkan sebagai **makhluk hutan**, bukan suku/manusia purba nyata.

## Prompt

```
Monster character turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Ebu Gogo, a small hairy forest creature from Flores folklore, clever and greedy, enlarged by dark red cursed energy. About 1 meter tall at human scale, stocky body with a round belly, long arms reaching the knees, short bowed legs, large flat feet. Covered in coarse reddish-brown hair shaped as large chunky clumps lying close to the body, bare dark leathery face, palms and soles. Wide flat nose, heavy brow, large curious glowing dark red eyes, wide mouth closed in a sly grin, small pointed ears. A few stolen trinkets (a bead necklace, a small woven pouch) tied tightly to the chest.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers spread, legs apart with a clear gap.

Important: mischievous forest creature, clearly not a human tribe or an ancient human species. No gore, no blood, no exposed organs. No blue light. Nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/ebu_gogo_v01.png`, potong jadi `ebu_gogo_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
