# Prompt konsep Tuyul (kawanan kecil + boss Ep 2)

Brief: [docs/05](../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110) (kawanan tuyul lalu bergabung jadi satu raksasa), [docs/16](../../docs/16-panduan-arc-1.md#ep-2--tangan-tangan-kecil--tuyul) (jahil, lincah, mencuri properti warga), [docs/27](../../docs/27-rencana-model-tuyul.md) (arahan desain bagian 2).
Gaya: **realistis** (docs/README, 14 Okt 2026), sama dengan Jayadwara2, Aksa2, dan Jerangkong. **Tanpa gore**, **bukan anak manusia**, bukan goblin/Gollum.

**Dua desain, satu identitas** (revisi 15 Okt 2026): tuyul **kecil** (kawanan, lucu-jahil) dan **boss** (besar, seram) adalah dua model dengan bahasa desain yang sama. Boss = kawanan yang sudah digembungkan energi Kala. Pegangan identitas (harus muncul di keduanya): kepala botak besar dengan **jaring retak merah menyala** di tempurung, telinga runcing panjang, mata merah menyala, kulit abu-abu hijau pucat, cawat kain lusuh, atribut pesugihan (kantong, uang kertas, koin).

## 1. Boss: turnaround + detail (rasio 2:1) — pakai ini untuk boss

Kalau memakai gambar tuyul kecil sebagai referensi, lampirkan dan tulis di awal prompt: *"Use the attached small creature as the base identity (same bald cracked skull with glowing red crack network, pointed ears, glowing red eyes, loincloth), but redesign it as its giant, terrifying evolved form."*

```
Monster character concept sheet for a realistic 3D action game. Left side: three orthographic views of the same creature side by side, FRONT view, SIDE view (left profile), BACK view, same scale, feet aligned on one ground line, neutral A-pose with arms angled away from the body, jaw open wide, eyes open. Right side: a large close-up of the head from a 3/4 angle, and a small scale chart showing the creature next to a red-and-gold armored giant hero silhouette: the creature is slightly TALLER than the hero and much bulkier. Plain flat light-gray background, flat even lighting, no cast shadows, no text, no labels, no logos.

Creature: the giant evolved form of Tuyul, a money-stealing spirit from Javanese folklore, swollen to monstrous size by dark red cursed energy. It is a huge, hunched, predatory brute, intimidating and hungry, NOT cute and NOT human. Enormous bald skull covered by a glowing network of dark red cracks, as if the cursed energy is bursting through the bone. Long pointed ears, deep-set glowing red eyes under a heavy brow, a huge gaping mouth with rows of small sharp teeth and a clear gap between the lips. Pale grey-green leathery skin stretched tight over thick bone and corded muscle, with glowing dark red veins running along the chest, shoulders and arms. Broad hunched shoulders, extremely long thick arms that reach below the knees, huge hands with long hooked claws, a massive distended pot belly with glowing cracks, thick short powerful legs, wide clawed feet. Pesugihan details: a giant tattered loincloth made of old sacks, strings of huge rusty old coins hanging across the chest like a bandolier, a few large faded banknotes plastered on the body, a big heavy sack slung on the back.

Mood: menacing and mischievous-cruel, a greedy thief grown into a monster. Eerie and powerful, suitable for a teen-rated game.

Important: no flesh wounds, no blood, no gore, no organs, no exposed muscle meat. Dark red only as glowing energy, never wet. No blue light, no silver. Not a goblin, not Gollum, not any existing movie or game creature.

Style: realistic game creature concept art with believable skin, bone and muscle anatomy, bold readable silhouette, consistent design across all views, suitable as a 3D modeling reference.
```

### Varian B: boss kawanan menyatu ("Tangan-Tangan Kecil")
Tempel paragraf ini **menggantikan** kalimat "Pesugihan details..." di atas, kalau mau boss yang terlihat tersusun dari banyak tuyul:

```
Fusion detail: the creature looks like a whole swarm of small mischievous spirits fused into one giant body. Dozens of small grey-green arms and hands with tiny clawed fingers reach out from its shoulders, back, belly and sides, clutching coins, banknotes and stolen objects. Two or three small bald heads with glowing red eyes are fused on its shoulders and belly, smaller than the main head. Hands and heads are clearly part of the body, no gore, no flesh wounds, no blood. Strings of rusty coins and old banknotes hang across the chest, a tattered loincloth made of old sacks, a big sack on the back.
```
Catatan: varian B menambah mesh dan tangan kecil yang perlu di-skin; kalau dipilih, anggaran poligon dan rig di docs/27 ikut dihitung ulang.

## 2. Tuyul kecil (kawanan)

Gambar yang sudah dibuat developer (15 Okt 2026) dipakai sebagai dasar kawanan. Kalau mau digenerate ulang dengan perbaikan (bibir punya celah, kulit lebih pucat abu-hijau agar tidak terbaca goblin, atribut pesugihan):

```
Concept art of a small mischievous spirit creature for a realistic 3D action game: about 1 meter tall, pale grey-green waxy skin (not olive, not wrinkled like a goblin), very large bald head with a glowing dark red crack network across the skull, long pointed ears, big glowing red eyes, a cheeky grin with small pointed teeth and a visible gap between the lips, round pot belly, thin nimble limbs with separated clawed fingers, tattered loincloth made of old sack cloth, a small worn sack at the side, a few banknotes and old coins stuck to the body. Front view, side view and back view in neutral A-pose with mouth slightly open and eyes open, plain light-gray background, flat even lighting, no cast shadows, no text. Playful and a little eerie, not horrifying. No gore, no blood, no blue light, clearly not a human child, not a goblin, not Gollum.
```

## 3. Tips Tripo (pelajaran Aksa2, Jerangkong, Jayadwara2)

- **A-pose**, tangan terpisah dari badan, **jari terpisah** (jari menempel di Jerangkong), kaki sedikit terbuka dan menapak.
- **Mata terbuka, bibir punya celah** (mata dan mulut hanya dilukis di Aksa2 menghentikan rig wajah). Untuk boss: rahang terbuka lebar memberi celah yang jelas.
- Cawat, kantong, dan rantai koin sebagai bagian terpisah dari badan bila bisa (kalau menyatu, Hermes mencatatnya di K0).
- Hindari bayangan terpanggang di tekstur (minta flat-lit bila Tripo menyediakan); merah hanya sebagai retak/urat menyala, bukan basah.
- Generate **boss dan kecil sebagai dua GLB terpisah**. Simpan GLB asli; salin ke `Hermes/Art/tuyul/Source/` (tugas Hermes).

## Cek setelah gambar jadi
- Kecil: kawanan terbaca lucu-jahil dan bukan anak manusia/goblin; atribut pesugihan ada.
- Boss: siluet bungkuk-bulky terbaca dari jauh; kepala retak menyala; jelas lebih besar dan seram, tetapi masih "tuyul yang sama".
- Boss tidak lebih pendek dari Jayadwara di scale chart.
- Merah gelap hanya sebagai pendar; tanpa gore; tanpa biru/silver.
- Simpan hasil di `docs/concept-art/` (mis. `tuyul_kecil_v01.webp`, `tuyul_boss_v01.webp`).
