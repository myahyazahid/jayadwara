# Banaspati

| | |
|---|---|
| **Episode** | 10 |
| **Peran** | Boss finale (3 fase) |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ kepala + lengan; api = VFX |
| **Sumber** | [kartu episode](../../../docs/16-panduan-arc-1.md#ep-10--prasasti-tujuh-gerbang--banaspati-finale), [05](../../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; kunci di model sheet sebelum modeling.
- Skala manusia dulu (seperti Jerangkong); ukuran raksasa diatur di UE ([16](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Berjalan dengan tangan, kepala di bawah. Badan batu & lava padat; api lepas ditambahkan sebagai VFX.

## Prompt

```
Monster creature turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, hands aligned on one ground line, wide empty space between views.

Creature: Banaspati, a fire demon from Javanese folklore that walks on its hands with its head down, enlarged by dark red cursed energy. A huge round demonic head made of cracked dark volcanic stone with glowing orange-red molten cracks, large glowing eyes, a wide mouth with big stone fangs, wild flame-shaped stone hair. Two massive long muscular arms grow from the top of the head and plant into the ground like legs, with big clawed stone hands flat on the ground. No torso, no legs.

Pose: standing upside down on its two hands, arms straight and spread wide apart with a clear gap between them, the head hanging between and above the arms.

Important: draw the body as solid stone and lava shapes only, no separate loose flames or smoke. No blood, no gore. No blue fire.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/banaspati_v01.png`, potong jadi `banaspati_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
