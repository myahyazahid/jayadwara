# Poppo

| | |
|---|---|
| **Episode** | 15 |
| **Lokasi** | Pesisir Bugis |
| **Peran** | Musuh udara cepat (dogfight) |
| **Fokus anggota** | Bayu |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Bedakan dari Kalong Wewe (Ep 7, kelelawar): Poppo = sayap **bulu** seperti burung malam.
- Sayap terbentang horizontal, tidak menumpuk ke badan/kaki.

## Prompt

```
Monster creature turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Poppo, a flying night predator spirit from Bugis folklore, enlarged by dark red cursed energy. Gaunt humanoid body with a hunched back, gray-brown skin, long bird-like legs ending in large talons. Huge feathered wings attached to the arms like a night bird, wingspan about 3 times its height, dark brown and black feathers in large clear layered shapes. A narrow face with a sharp hooked nose, wide glowing dark red eyes, mouth closed. Long black hair tied back tightly.

Pose: standing upright, wings fully spread horizontally to the sides, wings not overlapping the body or the legs, legs apart with a clear gap.

Important: menacing, not gory. Clearly feathered wings, not bat wings. No blood. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/poppo_v01.png`, potong jadi `poppo_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
