# Harimau Cindaku

| | |
|---|---|
| **Episode** | 18 |
| **Lokasi** | Hutan Kerinci |
| **Peran** | Predator sangat cepat; menang dengan timing counter |
| **Fokus anggota** | Bayu |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Dalam kepercayaan Kerinci, cindaku dekat dengan sosok **leluhur/penjaga**. Gambarkan sebagai harimau sumatra agung yang **dirasuki Kala** (retakan merah), bukan makhluk jahat; penyegelan = pemulihan, bukan pembunuhan.
- Berkaki empat: perlu rig baru (grup "Kucing besar") atau rig reptil berkaki empat yang disesuaikan.

## Prompt

```
Monster creature turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, paws aligned on one ground line, wide empty space between views.

Creature: Harimau Cindaku, a majestic Sumatran tiger spirit from Kerinci folklore, possessed and enlarged by dark red cursed energy. Powerful muscular four-legged tiger body, realistic Sumatran tiger proportions, deep orange fur with bold black stripes, white chest and muzzle, thick ruff of fur around the face. Glowing dark red eyes, mouth closed. Thin cracks of dark red glowing light run along the shoulders and spine like veins of corruption.

Pose: neutral standing pose, all four legs straight and vertical, front legs apart and hind legs apart with clear gaps between all legs, head straight forward, tail held straight back away from the hind legs.

Important: noble and dangerous, not monstrous or rabid. No blood, no gore. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/harimau_cindaku_v01.png`, potong jadi `harimau_cindaku_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
