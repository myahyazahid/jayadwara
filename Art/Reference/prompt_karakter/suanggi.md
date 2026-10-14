# Suanggi ⚠️

| | |
|---|---|
| **Episode** | 17 |
| **Lokasi** | Maluku–Papua |
| **Peran** | Boss kutukan: membalik kontrol; hancurkan sumber kutukan |
| **Fokus anggota** | Ki Sastro |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- **Paling sensitif di Arc 2**: tuduhan suanggi masih memicu kekerasan nyata di Maluku, Papua, NTT. Jangan menggambarkan orang Papua/Maluku sebagai penyihir dan **jangan memakai topeng, ukiran, atau busana adat nyata**. Wujudnya roh kutukan abstrak.
- Tiga jimat melayang = sumber kutukan (titik lemah).
- Sangat disarankan review budayawan sebelum final ([06](../../../docs/06-referensi-mitologi.md#panduan-sensitivitas-budaya)).

## Prompt

```
Monster character turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, robe hem aligned on one ground line, wide empty space between views.

Creature: Suanggi, a cursed sorcery spirit from eastern Indonesian folklore, depicted as an abstract supernatural entity, enlarged by dark red cursed energy. A tall thin humanoid shape made of dense black smoke solidified into layered folds like a long robe, with long thin arms ending in long dark fingers. The face is a smooth featureless dark oval with two glowing dark red eye slits, no mouth. Three floating cursed charms made of twisted dark roots and cracked stone orbit close around its chest and glow dark red as clear weak points.

Pose: floating upright just above the ground, A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and the robe, fingers spread.

Important: an abstract spirit, not a human, no ethnic features, no real tribal masks, no carvings, no traditional costume or ornaments from any real culture. No gore. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/suanggi_v01.png`, potong jadi `suanggi_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
