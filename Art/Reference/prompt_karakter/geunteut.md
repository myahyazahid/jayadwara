# Geunteut

| | |
|---|---|
| **Episode** | 20 |
| **Lokasi** | Pesisir Aceh |
| **Peran** | **Finale Arc 2**: raksasa vs raksasa setara pertama; grup rig Buto |
| **Fokus anggota** | Kol. Bagas |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Rig grup **Buto / humanoid raksasa** (sama dengan Genderuwo); proporsi humanoid standar supaya bisa diretarget.
- Setara Jayadwara (1×): siluet harus terasa sebanding, bahu lebar, lengan panjang.
- Bedakan dari Genderuwo (Ep 9): Geunteut lebih tinggi-ramping, bulu abu-abu kehitaman panjang, kulit seperti batu karang pesisir.

## Prompt

```
Monster character turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Geunteut, a towering hairy giant from Acehnese folklore, enlarged by dark red cursed energy. Tall powerful humanoid about 8 heads tall, long arms, broad shoulders, strong legs. Long shaggy gray-black hair shaped as large chunky clumps covering the shoulders, back, forearms and shins, lying close to the body. Visible skin on the face, chest and hands is dark gray and rough like weathered coastal rock, with barnacle-like patches on the shoulders. Deep-set glowing dark red eyes, heavy brow, wide nose, mouth closed. Dark red glowing cracks across the chest.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers spread, legs apart with a clear gap.

Important: imposing and ancient, not gory. No clothing, no weapons, nothing held in the hands. No blood. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/geunteut_v01.png`, potong jadi `geunteut_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
