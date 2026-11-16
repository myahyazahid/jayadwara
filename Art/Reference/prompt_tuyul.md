# Prompt konsep Tuyul (satu model: boss + kawanan kecil)

Brief: [docs/05](../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) (kawanan tuyul lalu bergabung jadi satu raksasa), [docs/16](../../docs/16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul) (mencuri properti warga), [docs/27](../../docs/27-rencana-model-tuyul.md) (arahan desain bagian 2).
Gaya: **realistis** (docs/README, 14 Okt 2026), sama dengan Jayadwara2, Aksa2, dan Jerangkong. **Tanpa gore**, **bukan anak manusia**, bukan goblin/Gollum.

**Satu model saja** (keputusan developer 15 Okt 2026): desain boss yang besar dan seram dipakai juga untuk kawanan kecil; bedanya hanya ukuran (1 m / 27 m / 45 m, di-bake saat export). Jadi **hanya satu gambar konsep dan satu GLB Tripo**. Jangan menambah detail yang hanya masuk akal di satu ukuran (banyak kepala/tangan tambahan).

## 1. Prompt (turnaround + detail, rasio 2:1)

Kalau memakai gambar tuyul yang sudah ada sebagai referensi identitas, lampirkan dan tulis di awal prompt: *"Use the attached small creature as the base identity (same bald cracked skull with glowing red crack network, pointed ears, glowing red eyes, loincloth), but redesign it as its giant, terrifying evolved form."*

```
Monster character concept sheet for a realistic 3D action game. Left side: three orthographic views of the same creature side by side, FRONT view, SIDE view (left profile), BACK view, same scale, feet aligned on one ground line, neutral A-pose with arms angled away from the body, jaw open wide, eyes open. Right side: a large close-up of the head from a 3/4 angle, and a small scale chart showing the creature next to a red-and-gold armored giant hero silhouette: the creature is slightly TALLER than the hero and much bulkier. Plain flat light-gray background, flat even lighting, no cast shadows, no text, no labels, no logos.

Creature: the giant evolved form of Tuyul, a money-stealing spirit from Javanese folklore, swollen to monstrous size by dark red cursed energy. It is a huge, hunched, predatory brute, intimidating and hungry, NOT cute and NOT human. Enormous bald skull covered by a glowing network of dark red cracks, as if the cursed energy is bursting through the bone. Long pointed ears, deep-set glowing red eyes under a heavy brow, a huge gaping mouth with rows of small sharp teeth and a clear gap between the lips. Pale grey-green leathery skin stretched tight over thick bone and corded muscle, with glowing dark red veins running along the chest, shoulders and arms. Broad hunched shoulders, extremely long thick arms that reach below the knees, huge hands with long hooked claws and separated fingers, a massive distended pot belly with glowing cracks, thick short powerful legs, wide clawed feet. Pesugihan details: a giant tattered loincloth made of old sacks, strings of huge rusty old coins hanging across the chest like a bandolier, a few large faded banknotes plastered on the body, a big heavy sack slung on the back.

Mood: menacing and mischievous-cruel, a greedy thief grown into a monster. Eerie and powerful, suitable for a teen-rated game.

Important: no flesh wounds, no blood, no gore, no organs, no exposed muscle meat. Dark red only as glowing energy, never wet. No blue light, no silver. Not a goblin, not Gollum, not any existing movie or game creature.

Style: realistic game creature concept art with believable skin, bone and muscle anatomy, bold readable silhouette, consistent design across all views, suitable as a 3D modeling reference.
```

## 2. Tips Tripo (pelajaran Aksa2, Jerangkong, Jayadwara2)

- **A-pose**, tangan terpisah dari badan, **jari terpisah** (jari menempel di Jerangkong), kaki sedikit terbuka dan menapak.
- **Mata terbuka, bibir punya celah** (mata dan mulut hanya dilukis di Aksa2 menghentikan rig wajah). Rahang terbuka lebar memberi celah yang jelas.
- Cawat, kantong, dan untaian koin sebagai bagian terpisah dari badan bila bisa (kalau menyatu, Hermes mencatatnya di K0).
- Hindari bayangan terpanggang di tekstur (minta flat-lit bila Tripo menyediakan); merah hanya sebagai retak/urat menyala, bukan basah.
- Simpan GLB asli; salin ke `Hermes/Art/tuyul/Source/tuyul_tripo_v01.glb` (tugas Hermes).

## Cek setelah gambar jadi
- Siluet bungkuk-bulky terbaca dari jauh; tempurung retak menyala; jelas seram tetapi bukan horor.
- Tidak terbaca anak manusia, goblin, atau Gollum; atribut pesugihan ada.
- Masih masuk akal kalau diperkecil jadi 1 m untuk kawanan (tidak ada detail yang hanya cocok untuk raksasa).
- Boss tidak lebih pendek dari Jayadwara di scale chart.
- Merah gelap hanya sebagai pendar; tanpa gore; tanpa biru/silver.
- Simpan hasil di `docs/concept-art/` (mis. `tuyul_v01.webp`).
