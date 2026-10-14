# Tuyul

| | |
|---|---|
| **Episode** | 2 |
| **Peran** | Boss + minion tuyul kecil (satu model, pola Jerangkong) |
| **Prioritas** | Fase 4 |
| **Tripo** | ✅ |
| **Sumber** | [kartu episode](../../../docs/16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul), [05](../../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Bentuk = usulan Claude; kunci di model sheet sebelum modeling.
- Skala manusia dulu (seperti Jerangkong); ukuran raksasa diatur di UE ([16](../../../docs/16-panduan-arc-1.md#26-aturan-skala)).
- Harus terbaca sebagai goblin, bukan anak manusia.

## Prompt

```
Monster character turnaround sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Tuyul, a small mischievous goblin spirit from Javanese folklore, enlarged by dark red cursed energy. Short stocky body, about 3.5 heads tall, completely bald oversized head, large pointed ears, big round glowing dark red eyes, wide cheeky grin with closed mouth, small sharp nose. Grayish olive-green skin with a few darker blotches. Wears only a plain faded brown loincloth wrapped tightly at the waist. Thin dark red glowing veins on the back of the head.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso, hands open with long fingers spread, legs apart with a clear gap.

Important: playful and creepy, not a human child, clearly a goblin creature. No gore, no blood. No blue light. Nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic anatomy and materials, clear readable silhouette, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/tuyul_v01.png`, potong jadi `tuyul_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
