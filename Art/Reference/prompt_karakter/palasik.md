# Palasik

| | |
|---|---|
| **Episode** | 12 |
| **Lokasi** | Ranah Minang |
| **Peran** | Kepala-kepala terbang (kawanan); grup rig **kepala terbang** |
| **Fokus anggota** | Ratna |
| **Prioritas** | Di luar Season 1 (Arc 2, setelah Fase 4) |
| **Tripo** | ✅ |
| **Sumber** | [05](../../../docs/05-daftar-episode-boss.md#arc-2--gelombang-nusantara-ep-1120), [04](../../../docs/04-skenario-cerita.md#arc-2--gelombang-nusantara-ep-1120), [06](../../../docs/06-referensi-mitologi.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; belum ada panduan Arc 2 seperti [16](../../../docs/16-panduan-arc-1.md). Kunci di model sheet sebelum modeling.
- Skala manusia dulu; ukuran raksasa diatur di UE. Arc 2 boss **mendekati 1×** tinggi Jayadwara, Ep 20 = setara ([16 bagian 2.6](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Grup rig kepala terbang dipakai bersama Kuyang (Ep 13) dan Kala Rahu ([05 pengelompokan rig](../../../docs/05-daftar-episode-boss.md#pengelompokan-rig--skeleton-hemat-produksi)); bedakan siluetnya dari Kuyang: Palasik = rambut + bara, Kuyang = sulur.
- Legenda mengincar bayi: di game cukup lewat misi melindungi rumah sakit bersalin, tanpa adegan bayi diserang.
- Tanpa leher/organ menggantung; ujung bawah kepala = asap & bara merah gelap (jadi VFX).

## Prompt

```
Monster creature turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, base aligned on one ground line, wide empty space between views.

Creature: Palasik, a floating detached head spirit from Minangkabau folklore, enlarged by dark red cursed energy. A large gaunt human-like head with sunken cheeks, pale gray skin with fine cracks, glowing dark red eyes, mouth closed with thin lips. Very long black hair flowing backward as one thick solid mass. No neck and no body: the underside of the head ends in a smooth rounded base of dark cracked stone with dark red glowing embers.

Pose: floating upright, facing straight ahead, hair flowing straight back and down behind the head, not covering the face.

Important: eerie and sorrowful. No gore, no blood, no exposed organs. No blue light. No spine, no neck, no organs hanging below the head.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/palasik_v01.png`, potong jadi `palasik_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
