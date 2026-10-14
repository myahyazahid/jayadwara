# Parakang ⚠️

| | |
|---|---|
| **Episode** | 16 |
| **Lokasi** | Pesisir Bugis |
| **Peran** | Boss detektif: pelaku tersembunyi di antara warga; salah tuduh berkonsekuensi |
| **Fokus anggota** | Ratna |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- **Sensitif sosial** ([06](../../../docs/06-referensi-mitologi.md#catatan-per-boss-️)): tuduhan parakang memicu kekerasan nyata. Wujud monster harus **jelas makhluk Kala**, bukan wajah/etnis manusia tertentu; cerita menolak main hakim sendiri.
- Wujud: binatang bayangan gabungan (kucing hutan + anjing) yang "meminjam" bentuk manusia; tanpa ciri pakaian adat Bugis.

## Prompt

```
Monster creature turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, paws aligned on one ground line, wide empty space between views.

Creature: Parakang, a shapeshifting predator spirit from Bugis-Makassar folklore, enlarged by dark red cursed energy. A lean four-legged beast that mixes a wild cat and a wild dog: long narrow body, long legs with large clawed paws, a long tail, short coarse charcoal-black fur with faint darker rosette patterns. The head is beast-like with a long muzzle, mouth closed, and two glowing dark red eyes. Thin wisps of dark red cursed energy rise from the spine.

Pose: neutral standing pose, all four legs straight and vertical, front legs apart and hind legs apart with clear gaps between all legs, head straight forward, tail held away from the hind legs.

Important: clearly a supernatural beast, no human face, no human clothing, no traditional dress or cultural symbols. No blood, no gore. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/parakang_v01.png`, potong jadi `parakang_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
