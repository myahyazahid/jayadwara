# Kuyang

| | |
|---|---|
| **Episode** | 13 |
| **Lokasi** | Kota sungai, Kalimantan |
| **Peran** | Kepala terbang malam; harus menemukan tubuh yang ditinggalkannya |
| **Fokus anggota** | Nadia |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ kepala; tubuh = prop terpisah |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- **Organ menggantung dari legenda diganti** sulur akar & energi Kala bercahaya (rating remaja, [16 aturan konten](../../../docs/16-panduan-arc-1.md#27-aturan-konten)).
- "Tubuh yang ditinggalkan": usul jadi **cangkang batu/kayu tanpa kepala** yang diselimuti kain, bukan tubuh manusia. Perlu keputusan developer.
- Grup rig kepala terbang (sama dengan Palasik).

## Prompt

```
Monster creature turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, root tips aligned on one ground line, wide empty space between views.

Creature: Kuyang, a flying head spirit from Kalimantan folklore, enlarged by dark red cursed energy. A large female-like head with sharp gaunt features, dark brown skin with fine bark-like cracks, glowing dark red eyes, mouth closed, long black hair tied back tightly in a thick bun. Instead of a neck, a dense cluster of thick twisted dark roots and vines hangs below the head down to about twice the head height, the roots glowing with dark red light inside the cracks.

Pose: floating upright facing straight ahead, the roots hanging straight down and grouped tightly together.

Important: eerie, not gory. Clearly roots and vines, not intestines or organs. No blood, no flesh. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/kuyang_v01.png`, potong jadi `kuyang_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
